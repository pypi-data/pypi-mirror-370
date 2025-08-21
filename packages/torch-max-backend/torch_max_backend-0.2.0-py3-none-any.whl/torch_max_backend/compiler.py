import torch
from max.dtype import DType
from collections.abc import Callable
from max.graph import Graph
from max.torch.torch import max_device_ref
import max.graph.value
from max import engine
from max.driver import Accelerator, accelerator_count, CPU
from .aten_functions import MAPPING_TORCH_ATEN_TO_MAX
import warnings
from torch._dynamo.backends.common import aot_autograd
from max.driver import Device
from functorch.compile import make_boxed_func
from torch_max_backend.aten_functions import DECOMPOSITION_TABLE
from torch_max_backend.flags import profiling_enabled, verbose_enabled
import time
import traceback
from typing import Any


class MaxCompilerError(Exception):
    pass


import datetime as dt


def gather_stats_on_graph(gm: torch.fx.GraphModule):
    # count the number of times we see each function.
    # print and sort alphabetically.
    function_counts = {}
    for node in gm.graph.nodes:
        if node.op == "call_function" or node.op == "call_method":
            name = get_fully_qualified_name(node.target)
            function_counts.setdefault(name, 0)
            function_counts[name] += 1
    sorted_counts = sorted(function_counts.items(), key=lambda x: x[1], reverse=True)
    print("Function call counts:")
    for name, count in sorted_counts:
        print(f"{name}: {count}")


def get_fully_qualified_name(func: Callable | str) -> str:
    if isinstance(func, str):
        return f"torch.Tensor.{func}"
    result = ""
    if hasattr(func, "__module__"):
        result += func.__module__ + "."

    if hasattr(func, "__qualname__"):
        result += func.__qualname__

    result += " of type " + str(type(func)) + " "
    return result


def keep_only_tensors(
    inputs: list[int | float | torch.Tensor] | tuple[int | float | torch.Tensor, ...],
    detach: bool = False,
) -> list[torch.Tensor]:
    result = []
    for x in inputs:
        if isinstance(x, torch.Tensor):
            if detach:
                x = x.detach()
            result.append(x)
    return result


class TensorsBook:
    def __init__(self):
        self.tensors: dict[str, Any] = {}

    def __setitem__(self, name: str, tensor):
        self.tensors[name] = tensor

    def convert_to_max(self, something):
        if isinstance(something, torch.fx.Node):
            return self.tensors[something.name]
        elif isinstance(something, str):
            return something
        elif isinstance(something, int):
            return something
        elif isinstance(something, float):
            return something
        elif isinstance(something, slice):
            return slice(
                self.convert_to_max(something.start),
                self.convert_to_max(something.stop),
                self.convert_to_max(something.step),
            )
        elif isinstance(something, torch.fx.immutable_collections.immutable_list):
            return [self.convert_to_max(x) for x in something]
        elif isinstance(something, tuple):
            return tuple(self.convert_to_max(x) for x in something)
        elif isinstance(something, torch.device):
            return something
        elif isinstance(something, torch.dtype):
            return something
        elif isinstance(something, torch.layout):
            return something
        elif isinstance(something, torch.memory_format):
            return something
        elif something is None:
            return None
        elif something == ...:
            return ...
        elif isinstance(something, torch.nn.Module):
            return something
        raise ValueError(f"Unsupported type when reading the graph: {type(something)}")


def fetch_attr(gm: torch.fx.GraphModule, target: str):
    """Fetch an attribute from the Module hierarchy of self.gm.
    Args:
        target (str): The fully-qualified name of the attribute to fetch
    """
    target_atoms = target.split(".")
    attr_itr = gm
    for i, atom in enumerate(target_atoms):
        if not hasattr(attr_itr, atom):
            raise RuntimeError(
                f"Node referenced nonexistent target {'.'.join(target_atoms[: i + 1])}"
            )
        attr_itr = getattr(attr_itr, atom)
    return attr_itr


def get_error_message(
    node: torch.fx.Node, node_idx: int, func_args: list, func_kwargs: dict
) -> str:
    if node.stack_trace is None:
        stack_trace = "No stack trace available, likely because this node is the result of a decomposition."
    else:
        stack_trace = node.stack_trace
    return (
        f"Failing at node {node_idx} when executing function {get_fully_qualified_name(node.target)}. "
        f"inputs of node were: args={func_args}, kwargs={func_kwargs}. "
        f"You can open an issue at https://github.com/gabrieldemarmiesse/torch-max-backend/issues . "
        f"It comes from there in your code: \n"
        f"{stack_trace}\n"
    )


class _GraphFactory:
    def __init__(self):
        self.names_to_input_idx: dict[str, int] = {}
        self.shape_names_to_input_dim: dict[str, tuple[str, int]] = {}
        self.graph_inputs: list[max.graph.value.TensorType] = []
        self.graph: Graph | None = None
        self.tensor_book = TensorsBook()
        # Link the shape expressions (names) to the node names
        self.expression_to_node_name: dict[str, str] = {}

    def initialize_graph(self):
        if self.graph is not None:
            raise RuntimeError("Graph has already been initialized.")
        self.graph = Graph(
            "torch_max_backend", input_types=self.graph_inputs
        ).__enter__()
        # Let's fill the tensor book
        for tensor_name, idx in self.names_to_input_idx.items():
            self.tensor_book[tensor_name] = self.graph.inputs[idx]
        for shape_name, (tensor_name, dim_idx) in self.shape_names_to_input_dim.items():
            self.tensor_book[shape_name] = self.tensor_book.tensors[tensor_name].shape[
                dim_idx
            ]

    def handle_placeholder(self, node: torch.fx.Node):
        if "example_value" in node.meta:
            example_value = node.meta["example_value"]
        elif "val" in node.meta:
            example_value = node.meta["val"]
        if isinstance(example_value, torch.SymInt):
            self.expression_to_node_name[example_value.node.expr.name] = node.name
        if isinstance(example_value, torch.Tensor | torch.nn.Parameter):
            shape = []
            for dim_idx, dim in enumerate(example_value.shape):
                if isinstance(dim, torch.SymInt):
                    shape.append(str(dim))
                    self.shape_names_to_input_dim[
                        self.expression_to_node_name[str(dim)]
                    ] = (node.name, dim_idx)
                elif isinstance(dim, int):
                    shape.append(dim)
                else:
                    raise TypeError(
                        f"Unsupported dimension type {type(dim)} for input {node.name} at index {dim_idx}"
                    )
            self.graph_inputs.append(
                max.graph.value.TensorType(
                    dtype=DType.from_torch(example_value.dtype),
                    shape=shape,
                    device=max_device_ref(example_value.device),
                )
            )
            self.names_to_input_idx[node.name] = len(self.graph_inputs) - 1

    def handle_call_function(self, node_idx: int, node: torch.fx.Node):
        func_args = [self.tensor_book.convert_to_max(x) for x in node.args]
        func_kwargs = {
            k: self.tensor_book.convert_to_max(v) for k, v in node.kwargs.items()
        }
        key = node.target

        # TODO: refactor this
        if (
            key not in MAPPING_TORCH_ATEN_TO_MAX
            and key.overloadpacket in MAPPING_TORCH_ATEN_TO_MAX
        ):
            key = key.overloadpacket

        if key not in MAPPING_TORCH_ATEN_TO_MAX:
            raise MaxCompilerError(
                "The aten function is not supported by the Max backend yet. "
                + get_error_message(node, node_idx, func_args, func_kwargs)
                + "You can try to write it yourself and insert it in the MAPPING_TORCH_ATEN_TO_MAX dictionary."
            )
        try:
            mapping_func = MAPPING_TORCH_ATEN_TO_MAX[key]
            func_output = mapping_func(*func_args, **func_kwargs)
        except Exception as e:
            raise MaxCompilerError(
                get_error_message(node, node_idx, func_args, func_kwargs)
                + "There was an error when executing the function. See the original error below. \n"
                f"{e}\n"
                f"{traceback.format_exc()}"
            )
        self.tensor_book[node.name] = func_output

    def handle_get_attr(self, node: torch.fx.Node):
        attr_value = fetch_attr(self.graph, node.target)
        self.tensor_book[node.name] = attr_value

    def handle_output(self, node: torch.fx.Node):
        output_tensors = []

        # None outputs can be required. So we remember here if
        # we want an output tensor (and we reccord the tensor position)
        # or if we want None.
        output_blueprint: list[int | None] = []

        for x in node.args[0]:
            converted = self.tensor_book.convert_to_max(x)
            if converted is None:
                output_blueprint.append(None)
            else:
                # position of the output tensor
                output_blueprint.append(len(output_tensors))
                output_tensors.append(converted)

        # Store the none indices for runtime handling
        self.graph.output(*output_tensors)
        self.graph.__exit__(None, None, None)
        return output_blueprint

    def create_graph(self, gm: torch.fx.GraphModule) -> tuple[Graph, list[int | None]]:
        output_blueprint = None
        for node_idx, node in enumerate(gm.graph.nodes):
            if node.op == "placeholder":
                self.handle_placeholder(node)
                continue

            if not self.graph:
                self.initialize_graph()

            if node.op in ("call_function", "call_method"):
                self.handle_call_function(node_idx, node)
            elif node.op == "get_attr":
                self.handle_get_attr(node)
            elif node.op == "output":
                output_blueprint = self.handle_output(node)
            else:
                raise ValueError(f"Unsupported node type: {node.op}")
        if output_blueprint is None:
            raise ValueError(
                "No output node found in the graph, this should never happen."
            )
        return self.graph, output_blueprint


def get_accelerators() -> list[Device]:
    result = [CPU()]
    if accelerator_count() > 0:
        for i in range(accelerator_count()):
            try:
                result.append(Accelerator(i))
            except ValueError as e:
                warnings.warn(f"Failed to create accelerator {i}. {e}")
    return result


class BaseMaxCompiler:
    def __init__(self, gm: torch.fx.GraphModule, example_inputs: list, mode=None):
        if profiling_enabled():
            compiler_start = time.time_ns()
        if verbose_enabled():
            print(f"Graph has {len(gm.graph.nodes)} nodes.")
            gather_stats_on_graph(gm)

        graph, self.output_blueprint = _GraphFactory().create_graph(gm)
        if profiling_enabled():
            graph_defined_time = time.time_ns()
        session = engine.InferenceSession(devices=list(get_accelerators()))
        self.model = session.load(graph)
        if profiling_enabled():
            compiling_done_time = time.time_ns()
            defining = dt.timedelta(
                microseconds=(graph_defined_time - compiler_start) / 1000
            )
            print(f"Defining the Max graph in {defining}")
            compiling = dt.timedelta(
                microseconds=(compiling_done_time - graph_defined_time) / 1000
            )
            print(f"Compiling the Max graph in {compiling}")

    def __call__(self, *args) -> list[torch.Tensor | None]:
        # Detach tensors to avoid gradient tracking issues with DLpack
        if profiling_enabled():
            start_inference_time = time.time_ns()
        outputs = self.model.execute(*keep_only_tensors(args, detach=True))
        tensor_outputs = [torch.from_dlpack(x) for x in outputs]

        # Reconstruct the original output structure with None values
        result = []
        for i in self.output_blueprint:
            if i is None:
                result.append(None)
            else:
                result.append(tensor_outputs[i])
        if profiling_enabled():
            end_inference_time = time.time_ns()
            inference_duration = dt.timedelta(
                microseconds=(end_inference_time - start_inference_time) / 1000
            )
            print(f"Running the Max graph in {inference_duration}")
        return result


def _MaxCompilerBackpropCompatible(
    gm: torch.fx.GraphModule, example_inputs: list, mode=None
):
    _max_compiler = BaseMaxCompiler(gm, example_inputs)
    return make_boxed_func(_max_compiler.__call__)


max_backend = aot_autograd(
    fw_compiler=_MaxCompilerBackpropCompatible, decompositions=DECOMPOSITION_TABLE
)
