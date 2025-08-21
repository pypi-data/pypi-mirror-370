import torch
import torch.nn.functional as F
import pytest
import math
from torch_max_backend.testing import check_functions_are_equivalent
from torch.ops import aten


def test_basic_addition(device: str):
    def fn(x, y):
        return x + y

    a = torch.randn(3)
    b = torch.randn(3)

    check_functions_are_equivalent(fn, device, [a, b])


def test_iadd(device: str):
    def fn(x, y):
        x += y
        return x

    a = torch.randn(3)
    b = torch.randn(3)

    check_functions_are_equivalent(fn, device, [a, b])


def test_t_method(device: str):
    def fn(x):
        return x.t()

    a = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [a])


def test_t_function(device: str):
    def fn(x):
        return torch.t(x)

    a = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [a])


def test_new_ones(device: str):
    def fn(x):
        return x.new_ones((3, 3))

    a = torch.randn(3)

    check_functions_are_equivalent(fn, device, [a])


def test_new_ones_device(device: str):
    def fn(x):
        return x.new_ones((3, 3), device=torch.device(device))

    a = torch.randn(3)

    check_functions_are_equivalent(fn, "cpu", [a])


def test_new_ones_dtype(device: str):
    def fn(x):
        return x.new_ones((3, 3), dtype=torch.uint8)

    a = torch.randn(3)

    check_functions_are_equivalent(fn, device, [a])


def test_operator_add(device: str, tensor_shapes: tuple):
    def fn(x, y):
        return x + y

    a = torch.randn(tensor_shapes)
    b = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a, b])


def test_subtraction(device: str, tensor_shapes: tuple):
    def fn(x, y):
        return x - y

    a = torch.randn(tensor_shapes)
    b = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a, b])


def test_subtraction_different_dtypes(device: str, tensor_shapes: tuple):
    def fn(x, y):
        return x - y

    a = torch.randn(tensor_shapes, dtype=torch.float32)
    b = torch.randint(0, 10, tensor_shapes, dtype=torch.int64)

    check_functions_are_equivalent(fn, device, [a, b])


def test_multiplication(device: str, tensor_shapes: tuple):
    def fn(x, y):
        return x * y

    a = torch.randn(tensor_shapes)
    b = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a, b])


def test_multiplication_int32(device: str, tensor_shapes: tuple):
    def fn(x, y):
        return x * y

    a = torch.randint(0, 10, size=tensor_shapes, dtype=torch.int32)
    b = torch.randint(0, 10, size=tensor_shapes, dtype=torch.int32)

    check_functions_are_equivalent(fn, device, [a, b])


def test_division(device: str, tensor_shapes: tuple):
    def fn(x, y):
        return x / y

    a = torch.randn(tensor_shapes)
    b = torch.randn(tensor_shapes) + 1.0  # Avoid division by zero

    check_functions_are_equivalent(fn, device, [a, b])


def test_floor_division(device: str, tensor_shapes: tuple):
    def fn(x, y):
        return x // y

    a = torch.randn(tensor_shapes) * 10
    b = torch.randn(tensor_shapes).abs() + 1.0  # Avoid division by zero

    check_functions_are_equivalent(fn, device, [a, b])


def test_power(device: str, tensor_shapes: tuple):
    def fn(x, y):
        return x**y

    a = torch.randn(tensor_shapes).abs() + 0.1  # Avoid negative base
    b = torch.randn(tensor_shapes) * 2  # Keep exponent reasonable

    check_functions_are_equivalent(fn, device, [a, b])


def test_modulo(device: str, tensor_shapes: tuple):
    def fn(x, y):
        return x % y

    a = torch.randn(tensor_shapes) * 10
    b = torch.randn(tensor_shapes).abs() + 1.0  # Avoid division by zero

    check_functions_are_equivalent(fn, device, [a, b])


def test_abs(device: str, tensor_shapes: tuple):
    def fn(x):
        return torch.abs(x)

    a = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a])


def test_floor(device: str, tensor_shapes: tuple):
    def fn(x):
        return torch.floor(x)

    # Use a mix of positive and negative values to test floor properly
    a = torch.randn(tensor_shapes) * 10  # Scale to get larger values

    check_functions_are_equivalent(fn, device, [a])


def test_floor_edge_cases(device: str):
    """Test floor with specific edge cases"""

    def fn(x):
        return torch.floor(x)

    # Test with specific values to ensure floor behavior is correct
    test_cases = [
        torch.tensor([2.7, -2.7, 3.0, -3.0, 0.5, -0.5, 0.0]),  # Mixed cases
        torch.tensor([1.9999, -1.9999, 10.1, -10.1]),  # Near integers
        torch.tensor([100.9, -100.9, 0.1, -0.1]),  # Large and small values
    ]

    for test_tensor in test_cases:
        check_functions_are_equivalent(fn, device, [test_tensor])


def test_tensor_floor_method(device: str):
    """Test tensor.floor() method"""

    def fn(x):
        return x.floor()

    x = torch.randn(3, 4) * 5  # Scale values for better floor testing
    check_functions_are_equivalent(fn, device, [x])


def test_cos(device: str, tensor_shapes: tuple):
    def fn(x):
        return torch.cos(x)

    a = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a])


def test_sin(device: str, tensor_shapes: tuple):
    def fn(x):
        return torch.sin(x)

    a = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a])


def test_tanh(device: str, tensor_shapes: tuple):
    def fn(x):
        return torch.tanh(x)

    a = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a])


def test_sign(device: str, tensor_shapes: tuple):
    def fn(x):
        return torch.sign(x)

    # Test with mixed positive, negative, and zero values
    a = torch.randn(tensor_shapes)
    # Ensure we have a mix of positive, negative, and zero
    if a.numel() >= 3:
        a.view(-1)[:3] = torch.tensor([-1.0, 0.0, 1.0])

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("dtype", [torch.float32, torch.float64])
def test_sign_different_dtypes(device: str, dtype):
    def fn(x):
        return torch.sign(x)

    a = torch.tensor([-2.5, -1.0, 0.0, 1.0, 2.5], dtype=dtype)

    check_functions_are_equivalent(fn, device, [a])


def test_atanh(device: str, tensor_shapes: tuple):
    def fn(x):
        return torch.atanh(x)

    # atanh is defined for |x| < 1, so we need to ensure our test values are in this range
    a = torch.rand(tensor_shapes) * 1.8 - 0.9  # Values in range (-0.9, 0.9)

    check_functions_are_equivalent(fn, device, [a])


def test_outer(device: str):
    def fn(x, y):
        return torch.outer(x, y)

    # torch.outer requires 1D tensors
    a = torch.randn(5)
    b = torch.randn(3)

    check_functions_are_equivalent(fn, device, [a, b])


def test_log1p_basic(device: str):
    """Test basic log1p functionality"""

    def fn(x):
        return torch.log1p(x)

    # log1p domain is x > -1, use values in range (-0.5, 2.0) for safety
    a = torch.rand(3, 4) * 2.5 - 0.5  # Range (-0.5, 2.0)
    check_functions_are_equivalent(fn, device, [a])


def test_log1p_small_values(device: str):
    """Test log1p with small values where it's most beneficial"""

    def fn(x):
        return torch.log1p(x)

    # Test with very small values where log1p is numerically superior to log(1+x)
    test_cases = [
        torch.tensor([0.0, 0.1, 0.01, 0.001]),  # Small positive values
        torch.tensor([-0.1, -0.01, -0.001, -0.0001]),  # Small negative values
        torch.tensor([1e-6, -1e-6, 1e-10, -1e-10]),  # Very small values
        torch.rand(2, 3) * 0.2 - 0.1,  # Random small values in (-0.1, 0.1)
    ]
    for test_tensor in test_cases:
        check_functions_are_equivalent(fn, device, [test_tensor])


def test_log_basic(device: str):
    """Test basic log functionality"""

    def fn(x):
        return torch.log(x)

    # Use positive values only since log is only defined for positive numbers
    a = torch.rand(3, 4) + 0.1  # Range (0.1, 1.1) to avoid values too close to zero
    check_functions_are_equivalent(fn, device, [a])


def test_log_various_ranges(device: str):
    """Test log with various value ranges"""

    def fn(x):
        return torch.log(x)

    test_cases = [
        torch.tensor([1.0, 2.0, 10.0, 100.0]),  # Simple positive values
        torch.tensor([0.1, 0.5, 1.5, 5.0]),  # Mixed small and medium values
        torch.tensor(
            [math.e, 1.0, math.e**2, math.e**0.5]
        ),  # Values with known log results
        torch.rand(2, 3) * 10 + 0.1,  # Random positive values in range (0.1, 10.1)
    ]

    for test_tensor in test_cases:
        check_functions_are_equivalent(fn, device, [test_tensor])


def test_log1p_various_ranges(device: str):
    """Test log1p with various value ranges"""

    def fn(x):
        return torch.log1p(x)

    test_cases = [
        torch.tensor([0.0, 1.0, 2.0, 10.0]),  # Simple values
        torch.tensor([math.e - 1, 0.0, math.e**2 - 1]),  # Values with known results
        torch.tensor([-0.5, -0.9, -0.99, -0.999]),  # Negative values approaching -1
        torch.rand(2, 3) * 5 - 0.5,  # Random values in (-0.5, 4.5)
    ]
    for test_tensor in test_cases:
        check_functions_are_equivalent(fn, device, [test_tensor])


def test_log_edge_cases(device: str):
    """Test log with edge cases"""

    def fn(x):
        return torch.log(x)

    # Test with edge values (avoiding zero and negative values)
    test_cases = [
        torch.tensor([1.0]),  # log(1) = 0
        torch.tensor([math.e]),  # log(e) = 1
        torch.tensor([1e-5, 1e5]),  # Very small and very large positive values
        torch.tensor([0.001, 1000.0]),  # Range of magnitudes
    ]

    for test_tensor in test_cases:
        check_functions_are_equivalent(fn, device, [test_tensor])


def test_log1p_edge_cases(device: str):
    """Test log1p with edge cases"""

    def fn(x):
        return torch.log1p(x)

    # Test with edge values (avoiding -1 which gives -inf)
    test_cases = [
        torch.tensor([0.0]),  # log1p(0) = 0
        torch.tensor([math.e - 1]),  # log1p(e-1) = 1
        torch.tensor([-0.9999, 0.9999]),  # Close to domain boundary and symmetric
        torch.tensor([100.0, 1000.0]),  # Large positive values
    ]
    for test_tensor in test_cases:
        check_functions_are_equivalent(fn, device, [test_tensor])


def test_isnan_basic(device: str):
    """Test basic isnan functionality"""

    def fn(x):
        return torch.isnan(x)

    # Create tensor with mix of normal values and NaNs
    a = torch.tensor([1.0, float("nan"), 3.0, float("nan"), 5.0])
    check_functions_are_equivalent(fn, device, [a])


def test_isnan_no_nan(device: str):
    """Test isnan with tensor containing no NaNs"""

    def fn(x):
        return torch.isnan(x)

    # Regular tensor with no NaNs
    a = torch.randn(3, 4)
    check_functions_are_equivalent(fn, device, [a])


def test_isnan_all_nan(device: str):
    """Test isnan with tensor containing all NaNs"""

    def fn(x):
        return torch.isnan(x)

    # Tensor with all NaNs
    a = torch.full((2, 3), float("nan"))
    check_functions_are_equivalent(fn, device, [a])


def test_isnan_edge_cases(device: str):
    """Test isnan with various edge cases"""

    def fn(x):
        return torch.isnan(x)

    # Test with inf, -inf, 0, negative numbers, and NaN
    test_cases = [
        torch.tensor([0.0, -0.0, float("inf"), float("-inf"), float("nan")]),
        torch.tensor([[1.0, float("nan")], [float("inf"), -2.5]]),
        torch.tensor(
            [1e10, -1e10, 1e-10, float("nan")]
        ),  # Very large and small numbers
    ]

    for test_tensor in test_cases:
        check_functions_are_equivalent(fn, device, [test_tensor])


def test_tensor_log1p_method(device: str):
    """Test tensor.log1p() method"""

    def fn(x):
        return x.log1p()

    # Use range where log1p is well-defined (x > -1)
    x = torch.rand(3, 4) * 3 - 0.5  # Range (-0.5, 2.5)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_log_method(device: str):
    """Test tensor.log() method"""

    def fn(x):
        return x.log()

    # Positive values for log domain
    x = torch.rand(3, 4) * 5 + 0.5  # Range (0.5, 5.5)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_isnan_method(device: str):
    """Test tensor.isnan() method"""

    def fn(x):
        return x.isnan()

    # Mix of NaN and regular values
    x = torch.tensor([1.0, float("nan"), -3.5, float("nan"), 0.0])
    check_functions_are_equivalent(fn, device, [x])


def test_stack_1d(device: str):
    # Test 1D tensors
    def fn_1d(a, b):
        return torch.stack([a, b], dim=0)

    a1d = torch.randn(2)
    b1d = torch.randn(2)
    check_functions_are_equivalent(fn_1d, device, [a1d, b1d])


@pytest.mark.parametrize("dim", [0, 1, -1])
def test_stack_2d(device: str, dim: int):
    def fn(a, b, c):
        return torch.stack([a, b, c], dim=dim)

    # Create tensors with same shape for stacking
    a = torch.randn(3, 4)
    b = torch.randn(3, 4)
    c = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [a, b, c])


def test_stack_3d(device: str):
    # Test 3D tensors
    def fn_3d(a, b):
        return torch.stack([a, b], dim=0)

    a3d = torch.randn(2, 3, 4)
    b3d = torch.randn(2, 3, 4)
    check_functions_are_equivalent(fn_3d, device, [a3d, b3d])


@pytest.mark.parametrize("func", [min, max])
def test_builtin_min_max(device: str, func):
    """Only works with a single dimension."""

    def fn(x):
        return func(x)

    a = torch.randn((9,))

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("keepdim", [True, False])
@pytest.mark.parametrize("func", [torch.amin, torch.amax])
@pytest.mark.parametrize(
    "shapes,dims",
    [
        ((3, 4), (0,)),
        ((5, 6, 2), (0, 2)),
        ((8,), (0,)),
        ((2, 3, 4), (-1,)),
        ((2, 3, 4), -1),
        ((2, 3, 4), None),
    ],
)
def test_torch_amin_amax_single_element_options(
    device: str, shapes, dims, keepdim, func
):
    """Only works with a single element."""

    def fn(x):
        return func(x, dims, keepdim=keepdim)

    a = torch.randn(shapes)

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("keepdim", [True, False])
@pytest.mark.parametrize("shapes,dims", [((8,), 0), ((2, 3, 4), -1), ((2, 3, 4), None)])
def test_torch_argmax(device: str, shapes, dims, keepdim):
    """Test argmax with various dimensions and keepdim options."""

    def fn(x):
        return torch.argmax(x, dim=dims, keepdim=keepdim)

    a = torch.randn(shapes)

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("shapes", [(8,), (3, 4), (2, 3, 4), (5, 6, 2, 3)])
def test_torch_argmax_no_dim(device: str, shapes):
    """Test argmax with only tensor argument (no dim parameter)."""

    def fn(x):
        return torch.argmax(x)

    a = torch.randn(shapes)

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("keepdim", [True, False])
@pytest.mark.parametrize("shapes,dims", [((8,), 0), ((2, 3, 4), -1), ((2, 3, 4), None)])
def test_torch_argmin(device: str, shapes, dims, keepdim):
    """Test argmin with various dimensions and keepdim options."""

    def fn(x):
        return torch.argmin(x, dim=dims, keepdim=keepdim)

    a = torch.randn(shapes)

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("shapes", [(8,), (3, 4), (2, 3, 4), (5, 6, 2, 3)])
def test_torch_argmin_no_dim(device: str, shapes):
    """Test argmin with only tensor argument (no dim parameter)."""

    def fn(x):
        return torch.argmin(x)

    a = torch.randn(shapes)

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("func", [torch.min, torch.max])
@pytest.mark.parametrize("shapes", [(8,), (3, 4), (2, 3, 4), (5, 6, 2, 3)])
def test_torch_max_single_value(device: str, shapes, func):
    def fn(x):
        return func(x)

    a = torch.randn(shapes)

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("func", [torch.min, torch.max])
@pytest.mark.parametrize("keepdim", [True, False])
@pytest.mark.parametrize("shapes,dims", [((8,), 0), ((2, 3, 4), -1)])
def test_torch_max_with_dim(device: str, shapes, dims, keepdim, func):
    def fn(x):
        return func(x, dim=dims, keepdim=keepdim)

    a = torch.randn(shapes)

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("func", [torch.min, torch.max])
@pytest.mark.parametrize("shapes,dims", [((8,), 0), ((2, 3, 4), -1)])
def test_torch_max_with_dim_positional(device: str, shapes, dims, func):
    def fn(x):
        return func(x, dims)

    a = torch.randn(shapes)

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("func", [torch.min, torch.max])
def test_torch_max_elementwise(device: str, tensor_shapes: tuple, func):
    def fn(x, y):
        return func(x, y)

    a = torch.randn(tensor_shapes)
    b = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a, b])


@pytest.mark.parametrize("func", [torch.minimum, torch.maximum])
def test_minimum_maximum(device: str, tensor_shapes: tuple, func):
    """Only works with elementwise min/max of two tensors."""

    def fn(x, y):
        return func(x, y)

    a = torch.randn(tensor_shapes)
    b = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a, b])


def test_relu(device: str, tensor_shapes: tuple):
    def fn(x):
        return F.relu(x)

    a = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a])


def test_cat(device: str, tensor_shapes: tuple):
    def fn(x, y):
        return torch.cat([x, y], dim=0)

    a = torch.randn(tensor_shapes)
    b = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a, b])


def test_combination_add_mul(device: str, tensor_shapes: tuple):
    def fn(x, y, z):
        return (x + y) * z

    a = torch.randn(tensor_shapes)
    b = torch.randn(tensor_shapes)
    c = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a, b, c])


def test_combination_sub_div(device: str, tensor_shapes: tuple):
    def fn(x, y, z):
        return (x - y) / z

    a = torch.randn(tensor_shapes)
    b = torch.randn(tensor_shapes)
    c = torch.randn(tensor_shapes) + 1.0  # Avoid division by zero

    check_functions_are_equivalent(fn, device, [a, b, c])


def test_combination_trig_arithmetic(device: str, tensor_shapes: tuple):
    def fn(x, y):
        return torch.sin(x) + torch.cos(y)

    a = torch.randn(tensor_shapes)
    b = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a, b])


def test_combination_abs_mul_add(device: str, tensor_shapes: tuple):
    def fn(x, y, z):
        return torch.abs(x) * y + z

    a = torch.randn(tensor_shapes)
    b = torch.randn(tensor_shapes)
    c = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a, b, c])


def test_combination_pow_mod(device: str, tensor_shapes: tuple):
    def fn(x, y):
        return (x**2) % y

    a = torch.randn(tensor_shapes).abs() + 0.1
    b = torch.randn(tensor_shapes).abs() + 1.0

    check_functions_are_equivalent(fn, device, [a, b])


def test_complex_combination(device: str, tensor_shapes: tuple):
    def fn(x, y, z):
        return torch.abs(torch.sin(x) * y + torch.cos(z))

    a = torch.randn(tensor_shapes)
    b = torch.randn(tensor_shapes)
    c = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a, b, c])


def test_scalar_shapes(device: str):
    def fn(x, y):
        return x + y * 2

    a = torch.randn(())  # Scalar tensor
    b = torch.randn(())

    check_functions_are_equivalent(fn, device, [a, b])


def test_broadcasting_compatible(device: str):
    def fn(x, y):
        return x + y

    a = torch.randn(5, 1)
    b = torch.randn(1, 5)

    check_functions_are_equivalent(fn, device, [a, b])


def test_conv2d_basic(device: str):
    """Test basic conv2d with default parameters"""

    def fn(x, w):
        return F.conv2d(x, w)

    batch_size, in_channels, height, width = 2, 3, 8, 8
    out_channels, kernel_size = 4, 3

    x = torch.randn(batch_size, in_channels, height, width)
    w = torch.randn(out_channels, in_channels, kernel_size, kernel_size)

    check_functions_are_equivalent(fn, device, [x, w])


def test_conv2d_with_bias(device: str):
    """Test conv2d with bias"""

    def fn(x, w, b):
        return F.conv2d(x, w, b)

    batch_size, in_channels, height, width = 2, 3, 8, 8
    out_channels, kernel_size = 4, 3

    x = torch.randn(batch_size, in_channels, height, width)
    w = torch.randn(out_channels, in_channels, kernel_size, kernel_size)
    b = torch.randn(out_channels)

    check_functions_are_equivalent(fn, device, [x, w, b])


def test_conv2d_stride_int(device: str):
    """Test conv2d with integer stride"""

    def fn(x, w):
        return F.conv2d(x, w, stride=2)

    batch_size, in_channels, height, width = 2, 3, 16, 16
    out_channels, kernel_size = 4, 3

    x = torch.randn(batch_size, in_channels, height, width)
    w = torch.randn(out_channels, in_channels, kernel_size, kernel_size)

    check_functions_are_equivalent(fn, device, [x, w])


def test_conv2d_stride_tuple(device: str):
    """Test conv2d with tuple stride"""

    def fn(x, w):
        return F.conv2d(x, w, stride=(2, 3))

    batch_size, in_channels, height, width = 2, 3, 16, 16
    out_channels, kernel_size = 4, 3

    x = torch.randn(batch_size, in_channels, height, width)
    w = torch.randn(out_channels, in_channels, kernel_size, kernel_size)

    check_functions_are_equivalent(fn, device, [x, w])


def test_conv2d_padding_int(device: str):
    """Test conv2d with integer padding"""

    def fn(x, w):
        return F.conv2d(x, w, padding=1)

    batch_size, in_channels, height, width = 2, 3, 8, 8
    out_channels, kernel_size = 4, 3

    x = torch.randn(batch_size, in_channels, height, width)
    w = torch.randn(out_channels, in_channels, kernel_size, kernel_size)

    check_functions_are_equivalent(fn, device, [x, w])


def test_conv2d_padding_tuple(device: str):
    """Test conv2d with tuple padding"""

    def fn(x, w):
        return F.conv2d(x, w, padding=(1, 2))

    batch_size, in_channels, height, width = 2, 3, 8, 8
    out_channels, kernel_size = 4, 3

    x = torch.randn(batch_size, in_channels, height, width)
    w = torch.randn(out_channels, in_channels, kernel_size, kernel_size)

    check_functions_are_equivalent(fn, device, [x, w])


@pytest.mark.xfail(reason="Dilation not implemented yet on max")
def test_conv2d_dilation_int(device: str):
    def fn(x, w):
        return F.conv2d(x, w, dilation=2)

    batch_size, in_channels, height, width = 2, 3, 16, 16
    out_channels, kernel_size = 4, 3

    x = torch.randn(batch_size, in_channels, height, width)
    w = torch.randn(out_channels, in_channels, kernel_size, kernel_size)

    check_functions_are_equivalent(fn, device, [x, w])


@pytest.mark.xfail(reason="Dilation not implemented yet on max")
def test_conv2d_dilation_tuple(device: str):
    """Test conv2d with tuple dilation"""

    def fn(x, w):
        return F.conv2d(x, w, dilation=(2, 3))

    batch_size, in_channels, height, width = 2, 3, 16, 16
    out_channels, kernel_size = 4, 3

    x = torch.randn(batch_size, in_channels, height, width)
    w = torch.randn(out_channels, in_channels, kernel_size, kernel_size)

    check_functions_are_equivalent(fn, device, [x, w])


def test_conv2d_all_params(device: str):
    """Test conv2d with all parameters specified"""

    def fn(x, w, b):
        return F.conv2d(x, w, b, stride=2, padding=1, dilation=1)

    batch_size, in_channels, height, width = 2, 3, 16, 16
    out_channels, kernel_size = 4, 3

    x = torch.randn(batch_size, in_channels, height, width)
    w = torch.randn(out_channels, in_channels, kernel_size, kernel_size)
    b = torch.randn(out_channels)

    check_functions_are_equivalent(fn, device, [x, w, b])


def test_conv2d_1x1_kernel(device: str):
    """Test conv2d with 1x1 kernel (pointwise convolution)"""

    def fn(x, w):
        return F.conv2d(x, w)

    batch_size, in_channels, height, width = 2, 3, 8, 8
    out_channels = 4

    x = torch.randn(batch_size, in_channels, height, width)
    w = torch.randn(out_channels, in_channels, 1, 1)

    check_functions_are_equivalent(fn, device, [x, w])


def test_conv2d_large_kernel(device: str):
    """Test conv2d with larger kernel"""

    def fn(x, w):
        return F.conv2d(x, w, padding=2)

    batch_size, in_channels, height, width = 2, 3, 16, 16
    out_channels, kernel_size = 4, 5

    x = torch.randn(batch_size, in_channels, height, width)
    w = torch.randn(out_channels, in_channels, kernel_size, kernel_size)

    check_functions_are_equivalent(fn, device, [x, w])


def test_conv2d_asymmetric_kernel(device: str):
    """Test conv2d with asymmetric kernel"""

    def fn(x, w):
        return F.conv2d(x, w, padding=(1, 2))

    batch_size, in_channels, height, width = 2, 3, 8, 8
    out_channels = 4

    x = torch.randn(batch_size, in_channels, height, width)
    w = torch.randn(out_channels, in_channels, 3, 5)  # 3x5 kernel

    check_functions_are_equivalent(fn, device, [x, w])


def test_conv2d_different_input_sizes(device: str):
    """Test conv2d with different input tensor sizes"""

    def fn(x, w):
        return F.conv2d(x, w, padding=1)

    # Test various input sizes
    sizes = [(1, 1, 4, 4), (3, 8, 32, 32), (2, 16, 64, 64)]

    for batch_size, in_channels, height, width in sizes:
        out_channels, kernel_size = 4, 3

        x = torch.randn(batch_size, in_channels, height, width)
        w = torch.randn(out_channels, in_channels, kernel_size, kernel_size)

        check_functions_are_equivalent(fn, device, [x, w])


def test_conv2d_edge_cases(device: str):
    """Test conv2d edge cases"""

    # Single pixel output
    def fn1(x, w):
        return F.conv2d(x, w)

    batch_size, in_channels = 1, 2
    out_channels, kernel_size = 3, 3

    x = torch.randn(batch_size, in_channels, 3, 3)  # Exactly kernel size
    w = torch.randn(out_channels, in_channels, kernel_size, kernel_size)

    check_functions_are_equivalent(fn1, device, [x, w])


def test_conv2d_combined_with_other_ops(device: str):
    """Test conv2d combined with other operations"""

    def fn(x, w, b, y):
        conv_out = F.conv2d(x, w, b, padding=1)
        return conv_out + y

    batch_size, in_channels, height, width = 2, 3, 8, 8
    out_channels, kernel_size = 4, 3

    x = torch.randn(batch_size, in_channels, height, width)
    w = torch.randn(out_channels, in_channels, kernel_size, kernel_size)
    b = torch.randn(out_channels)
    # y should have same shape as conv output: (2, 4, 8, 8)
    y = torch.randn(batch_size, out_channels, height, width)

    check_functions_are_equivalent(fn, device, [x, w, b, y])


def test_embedding_basic(device: str):
    """Test basic embedding lookup"""

    def fn(indices, weight):
        return F.embedding(indices, weight)

    vocab_size, embedding_dim = 10, 5
    seq_length = 4

    # Create indices tensor (LongTensor)
    indices = torch.randint(0, vocab_size, (seq_length,))
    weight = torch.randn(vocab_size, embedding_dim)

    check_functions_are_equivalent(fn, device, [indices, weight])


def test_embedding_2d_indices(device: str):
    """Test embedding with 2D indices (batch processing)"""

    def fn(indices, weight):
        return F.embedding(indices, weight)

    vocab_size, embedding_dim = 20, 8
    batch_size, seq_length = 3, 6

    indices = torch.randint(0, vocab_size, (batch_size, seq_length))
    weight = torch.randn(vocab_size, embedding_dim)

    check_functions_are_equivalent(fn, device, [indices, weight])


def test_embedding_3d_indices(device: str):
    """Test embedding with 3D indices"""

    def fn(indices, weight):
        return F.embedding(indices, weight)

    vocab_size, embedding_dim = 15, 4
    batch_size, seq_length, depth = 2, 3, 4

    indices = torch.randint(0, vocab_size, (batch_size, seq_length, depth))
    weight = torch.randn(vocab_size, embedding_dim)

    check_functions_are_equivalent(fn, device, [indices, weight])


def test_embedding_single_index(device: str):
    """Test embedding with single index (scalar)"""

    def fn(indices, weight):
        return F.embedding(indices, weight)

    vocab_size, embedding_dim = 10, 3

    indices = torch.tensor(5)  # Scalar tensor
    weight = torch.randn(vocab_size, embedding_dim)

    check_functions_are_equivalent(fn, device, [indices, weight])


def test_embedding_combined_with_other_ops(device: str):
    """Test embedding combined with other operations"""

    def fn(indices, weight, bias):
        embedded = F.embedding(indices, weight)
        return embedded + bias

    vocab_size, embedding_dim = 10, 5
    seq_length = 4

    indices = torch.randint(0, vocab_size, (seq_length,))
    weight = torch.randn(vocab_size, embedding_dim)
    bias = torch.randn(embedding_dim)

    check_functions_are_equivalent(fn, device, [indices, weight, bias])


def test_embedding_with_padding_idx(device: str):
    """Test embedding with padding_idx parameter"""

    def fn(indices, weight):
        return F.embedding(indices, weight, padding_idx=0)

    vocab_size, embedding_dim = 8, 4

    # Include padding index (0) in the indices
    indices = torch.tensor([[0, 1, 2, 0, 3], [4, 0, 5, 6, 0]])
    weight = torch.randn(vocab_size, embedding_dim)

    check_functions_are_equivalent(fn, device, [indices, weight])


def test_embedding_padding_idx_different_values(device: str):
    """Test embedding with different padding_idx values"""

    def fn_pad_0(indices, weight):
        return F.embedding(indices, weight, padding_idx=0)

    def fn_pad_2(indices, weight):
        return F.embedding(indices, weight, padding_idx=2)

    vocab_size, embedding_dim = 6, 3

    indices_0 = torch.tensor([0, 1, 3, 0])  # Using 0 as padding
    indices_2 = torch.tensor([1, 2, 4, 2])  # Using 2 as padding
    weight = torch.randn(vocab_size, embedding_dim)

    check_functions_are_equivalent(fn_pad_0, device, [indices_0, weight])
    check_functions_are_equivalent(fn_pad_2, device, [indices_2, weight])


def test_embedding_padding_idx_scalar(device: str):
    """Test embedding with padding_idx on scalar indices"""

    def fn(indices, weight):
        return F.embedding(indices, weight, padding_idx=0)

    vocab_size, embedding_dim = 5, 3

    indices = torch.tensor(0)  # Scalar padding index
    weight = torch.randn(vocab_size, embedding_dim)

    check_functions_are_equivalent(fn, device, [indices, weight])


def test_tensor_slice_basic(device: str):
    def fn(x):
        return x[1:3]  # Basic slice along first dimension

    x = torch.randn(5, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_slice_2d(device: str):
    def fn(x):
        return x[1:3, 0:2]  # Slice along both dimensions

    x = torch.randn(5, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_slice_negative_index(device: str):
    def fn(x):
        return x[-2:]  # Negative slice

    x = torch.randn(5, 3)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_slice_with_step(device: str):
    def fn(x):
        return x[1:10:2]  # Negative slice

    x = torch.randn(20, 20)

    check_functions_are_equivalent(fn, device, [x])


def test_to_float(device: str):
    def fn(x):
        return x.float()

    x = torch.randint(0, 10, (5,))

    check_functions_are_equivalent(fn, device, [x])


def test_expand_basic(device: str):
    """Test basic expand operation"""

    def fn(x):
        return x.expand(3, 4)

    x = torch.randn(1, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_expand_with_negative_one(device: str):
    """Test expand with -1 (keep dimension unchanged)"""

    def fn(x):
        return x.expand(-1, 5)

    x = torch.randn(3, 1)

    check_functions_are_equivalent(fn, device, [x])


def test_expand_multiple_dims(device: str):
    """Test expand on tensor with multiple dimensions"""

    def fn(x):
        return x.expand(2, 3, 4)

    x = torch.randn(1, 1, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_expand_same_size(device: str):
    """Test expand to same size (should be no-op)"""

    def fn(x):
        return x.expand(2, 3)

    x = torch.randn(2, 3)

    check_functions_are_equivalent(fn, device, [x])


def test_expand_add_dimensions(device: str):
    """Test expand adding new leading dimensions"""

    def fn(x):
        return x.expand(2, 3, 4)

    x = torch.randn(4)  # 1D tensor

    check_functions_are_equivalent(fn, device, [x])


def test_expand_mixed_operations(device: str):
    """Test expand combined with arithmetic operations"""

    def fn(x, y):
        expanded_x = x.expand(2, 3)
        return expanded_x + y

    x = torch.randn(1, 3)
    y = torch.randn(2, 3)

    check_functions_are_equivalent(fn, device, [x, y])


def test_expand_with_scalar_broadcast(device: str):
    """Test expand from scalar dimension"""

    def fn(x):
        return x.expand(5, 5)

    x = torch.randn(1, 1)

    check_functions_are_equivalent(fn, device, [x])


def test_expand_complex_pattern(device: str):
    """Test expand with complex dimension pattern"""

    def fn(x):
        return x.expand(2, -1, 4, -1)

    x = torch.randn(1, 3, 1, 5)

    check_functions_are_equivalent(fn, device, [x])


def test_transpose_2d(device: str):
    """Test basic transpose on 2D tensor"""

    def fn(x):
        return x.transpose(0, 1)

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_transpose_3d_first_last(device: str):
    """Test transpose swapping first and last dimensions on 3D tensor"""

    def fn(x):
        return x.transpose(0, 2)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_transpose_3d_middle_dims(device: str):
    """Test transpose swapping middle dimensions on 3D tensor"""

    def fn(x):
        return x.transpose(1, 2)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_transpose_negative_dims(device: str):
    """Test transpose with negative dimension indices"""

    def fn(x):
        return x.transpose(-2, -1)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_transpose_same_dim(device: str):
    """Test transpose with same dimension (should be no-op)"""

    def fn(x):
        return x.transpose(1, 1)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_transpose_4d(device: str):
    """Test transpose on 4D tensor"""

    def fn(x):
        return x.transpose(1, 3)

    x = torch.randn(2, 3, 4, 5)

    check_functions_are_equivalent(fn, device, [x])


def test_transpose_batch_dimension(device: str):
    """Test transpose involving batch dimension"""

    def fn(x):
        return x.transpose(0, 1)

    x = torch.randn(8, 16, 32)

    check_functions_are_equivalent(fn, device, [x])


def test_transpose_with_arithmetic(device: str):
    """Test transpose combined with arithmetic operations"""

    def fn(x, y):
        x_t = x.transpose(0, 1)
        return x_t + y

    x = torch.randn(3, 4)
    y = torch.randn(4, 3)

    check_functions_are_equivalent(fn, device, [x, y])


def test_transpose_multiple_ops(device: str):
    """Test multiple transpose operations"""

    def fn(x):
        # First transpose: (2, 3, 4) -> (2, 4, 3)
        x1 = x.transpose(1, 2)
        # Second transpose: (2, 4, 3) -> (4, 2, 3)
        x2 = x1.transpose(0, 1)
        return x2

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_transpose_with_other_methods(device: str):
    """Test transpose combined with other tensor methods"""

    def fn(x):
        x_t = x.transpose(0, 1)
        return x_t.expand(-1, 5, -1)

    x = torch.randn(1, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_transpose_scalar_like(device: str):
    """Test transpose on tensor with singleton dimensions"""

    def fn(x):
        return x.transpose(0, 2)

    x = torch.randn(1, 3, 1)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_cos_method(device: str):
    """Test tensor.cos() method"""

    def fn(x):
        return x.cos()

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_sin_method(device: str):
    """Test tensor.sin() method"""

    def fn(x):
        return x.sin()

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_atanh_method(device: str):
    """Test tensor.atanh() method"""

    def fn(x):
        return x.atanh()

    # atanh is defined for |x| < 1, so we need values in this range
    x = torch.rand(3, 4) * 1.8 - 0.9  # Values in range (-0.9, 0.9)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_cos_sin_combined(device: str):
    """Test combining tensor.cos() and tensor.sin() methods"""

    def fn(x):
        return x.cos() + x.sin()

    x = torch.randn(2, 3)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_cos_with_arithmetic(device: str):
    """Test tensor.cos() combined with arithmetic operations"""

    def fn(x, y):
        return x.cos() * y

    x = torch.randn(3, 4)
    y = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x, y])


def test_tensor_sin_with_arithmetic(device: str):
    """Test tensor.sin() combined with arithmetic operations"""

    def fn(x, y):
        return x.sin() - y

    x = torch.randn(3, 4)
    y = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x, y])


def test_tensor_cos_sin_chained(device: str):
    """Test chained tensor.cos().sin() operations"""

    def fn(x):
        return x.cos().sin()

    x = torch.randn(2, 3)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_trig_with_transpose(device: str):
    """Test tensor trigonometric methods with transpose"""

    def fn(x):
        return x.transpose(0, 1).cos()

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_cos_sin_different_shapes(device: str, tensor_shapes: tuple):
    """Test tensor.cos() and tensor.sin() with different tensor shapes"""

    def fn_cos(x):
        return x.cos()

    def fn_sin(x):
        return x.sin()

    x = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn_cos, device, [x])
    check_functions_are_equivalent(fn_sin, device, [x])


def test_tensor_pow_method(device: str):
    """Test tensor.pow() method"""

    def fn(x, y):
        return x.pow(y)

    x = torch.randn(3, 4).abs() + 0.1  # Avoid negative base
    y = torch.randn(3, 4) * 2  # Keep exponent reasonable

    check_functions_are_equivalent(fn, device, [x, y])


def test_tensor_pow_scalar_exponent(device: str):
    """Test tensor.pow() with scalar exponent"""

    def fn(x):
        return x.pow(2)

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_pow_negative_exponent(device: str):
    """Test tensor.pow() with negative exponent"""

    def fn(x):
        return x.pow(-2)

    x = torch.randn(3, 4).abs() + 1.0  # Avoid division by zero

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_pow_fractional_exponent(device: str):
    """Test tensor.pow() with fractional exponent"""

    def fn(x):
        return x.pow(0.5)  # Square root

    x = torch.randn(3, 4).abs() + 0.1  # Ensure positive for square root

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_pow_with_arithmetic(device: str):
    """Test tensor.pow() combined with arithmetic operations"""

    def fn(x, y, z):
        return x.pow(y) + z

    x = torch.randn(3, 4).abs() + 0.1
    y = torch.randn(3, 4) * 2
    z = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x, y, z])


def test_tensor_pow_chained(device: str):
    """Test chained tensor.pow() operations"""

    def fn(x):
        return x.pow(2).pow(0.5)  # Should be approximately x

    x = torch.randn(3, 4).abs() + 0.1

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_pow_broadcast(device: str):
    """Test tensor.pow() with broadcasting"""

    def fn(x, y):
        return x.pow(y)

    x = torch.randn(3, 4).abs() + 0.1
    y = torch.randn(1, 4) * 2

    check_functions_are_equivalent(fn, device, [x, y])


def test_tensor_pow_different_shapes(device: str, tensor_shapes: tuple):
    """Test tensor.pow() with different tensor shapes"""

    def fn(x):
        return x.pow(2)

    x = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_pow_with_other_methods(device: str):
    """Test tensor.pow() combined with other tensor methods"""

    def fn(x):
        return x.transpose(0, 1).pow(2).cos()

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_change_device_to_cpu(device: str):
    """Test changing device to CPU"""

    def fn(x):
        return x.to("cpu")

    x = torch.randn(1, 3)

    check_functions_are_equivalent(fn, device, [x])


def test_change_device_to_cpu_by_device(device: str):
    """Test changing device to CPU"""

    def fn(x):
        return x.to(torch.device("cpu"))

    x = torch.randn(1, 3)

    check_functions_are_equivalent(fn, device, [x])


def test_change_device_to_cuda(device: str, gpu_available: bool):
    """Test changing device to CUDA"""
    if not gpu_available:
        pytest.skip("CUDA not available")

    def fn(x):
        return x.to("cuda")

    x = torch.randn(1, 3)

    check_functions_are_equivalent(fn, device, [x])


def test_change_device_to_cuda_by_device(device: str, gpu_available: bool):
    """Test changing device to CUDA"""
    if not gpu_available:
        pytest.skip("CUDA not available")

    def fn(x):
        return x.to(torch.device("cuda"))

    x = torch.randn(1, 3)

    check_functions_are_equivalent(fn, device, [x])


def test_to_with_dtype_keyword(device: str):
    """Test tensor.to() with dtype keyword argument"""

    def fn(x):
        return x.to(dtype=torch.float32)

    x = torch.randint(0, 10, (2, 3))

    check_functions_are_equivalent(fn, device, [x])


def test_to_with_device_keyword(device: str):
    """Test tensor.to() with device keyword argument"""

    def fn(x):
        return x.to(device="cpu")

    x = torch.randn(2, 3)

    check_functions_are_equivalent(fn, device, [x])


def test_to_with_device_dtype_keywords(device: str):
    """Test tensor.to() with both device and dtype keyword arguments"""

    def fn(x):
        return x.to(device="cpu", dtype=torch.float32)

    x = torch.randint(0, 10, (2, 3))

    check_functions_are_equivalent(fn, device, [x])


def test_to_with_torch_device_object(device: str):
    """Test tensor.to() with torch.device object"""

    def fn(x):
        return x.to(torch.device("cpu"))

    x = torch.randn(2, 3)

    check_functions_are_equivalent(fn, device, [x])


def test_to_with_torch_device_object_cuda(device: str, gpu_available: bool):
    """Test tensor.to() with torch.device object for CUDA"""
    if not gpu_available:
        pytest.skip("CUDA not available")

    def fn(x):
        return x.to(torch.device("cuda:0"))

    x = torch.randn(2, 3)

    check_functions_are_equivalent(fn, device, [x])


def test_to_with_dtype_positional(device: str):
    """Test tensor.to() with dtype as positional argument"""

    def fn(x):
        return x.to(torch.float32)

    x = torch.randint(0, 10, (2, 3))

    check_functions_are_equivalent(fn, device, [x])


def test_to_dtype_conversion_int_to_float(device: str):
    """Test converting integer tensor to float"""

    def fn(x):
        return x.to(dtype=torch.float32)

    x = torch.randint(-5, 5, (3, 4))

    check_functions_are_equivalent(fn, device, [x])


def test_to_dtype_conversion_float_to_int(device: str):
    """Test converting float tensor to int"""

    def fn(x):
        return x.to(dtype=torch.int32)

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_to_dtype_conversion_double_to_float(device: str):
    """Test converting double tensor to float"""

    def fn(x):
        return x.to(dtype=torch.float32)

    x = torch.randn(3, 4, dtype=torch.float64)

    check_functions_are_equivalent(fn, device, [x])


def test_to_combined_with_operations(device: str):
    """Test tensor.to() combined with other operations"""

    def fn(x, y):
        x_converted = x.to(dtype=torch.float32)
        return x_converted + y

    x = torch.randint(0, 10, (3, 4))
    y = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x, y])


def test_to_device_transfer_with_computation(device: str):
    """Test device transfer followed by computation"""

    def fn(x):
        x_cpu = x.to("cpu")
        return x_cpu * 2

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_autocast_enter_exit():
    """Test autocast enter and exit functionality"""

    def fn(x):
        with torch.amp.autocast("cuda", enabled=True):
            return x + 1.0

    x = torch.randn(2, 3)

    # Test on CPU device only as autocast behavior may vary
    check_functions_are_equivalent(fn, "cpu", [x])


def test_complex_to_operations(device: str):
    """Test complex combinations of .to() operations"""

    def fn(x):
        # Convert to float first, then back to int
        x_float = x.to(dtype=torch.float32)
        result = x_float * 2.5
        return result.to(dtype=torch.int32)

    x = torch.randint(1, 5, (2, 3))

    check_functions_are_equivalent(fn, device, [x])


def test_mean_no_dim(device: str, tensor_shapes: tuple):
    """Test mean without specifying dimensions (reduce all)"""

    def fn(x):
        return torch.mean(x)

    a = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a])


def test_mean_single_dim(device: str, tensor_shapes: tuple):
    """Test mean with single dimension"""

    def fn(x):
        return torch.mean(x, dim=1)

    a = torch.randn(tensor_shapes) if len(tensor_shapes) > 1 else torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [a])


def test_mean_negative_dim(device: str, tensor_shapes: tuple):
    """Test mean with negative dimension"""

    def fn(x):
        return torch.mean(x, dim=-1)

    a = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a])


def test_mean_keepdim_true(device: str, tensor_shapes: tuple):
    """Test mean with keepdim=True"""

    def fn(x):
        return torch.mean(x, dim=1, keepdim=True)

    a = torch.randn(tensor_shapes) if len(tensor_shapes) > 1 else torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [a])


def test_mean_multiple_dims(device: str):
    """Test mean with multiple dimensions"""

    def fn(x):
        return torch.mean(x, dim=(1, 2))

    a = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [a])


def test_mean_multiple_dims_keepdim(device: str):
    """Test mean with multiple dimensions and keepdim=True"""

    def fn(x):
        return torch.mean(x, dim=(0, 2), keepdim=True)

    a = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [a])


def test_tensor_mean_method(device: str, tensor_shapes: tuple):
    """Test tensor.mean() method"""

    def fn(x):
        return x.mean()

    a = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [a])


def test_tensor_mean_method_with_dim(device: str, tensor_shapes: tuple):
    """Test tensor.mean(dim) method"""

    def fn(x):
        return x.mean(dim=1)

    a = torch.randn(tensor_shapes) if len(tensor_shapes) > 1 else torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [a])


def test_mean_3d_tensor(device: str):
    def fn(x):
        return torch.mean(x, dim=1)

    a = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [a])


def test_mean_3d_tensor_change_dtype(device: str):
    def fn(x):
        return torch.mean(x, dim=1, dtype=torch.float32)

    a = torch.randn(2, 3, 4).to(torch.int32)

    check_functions_are_equivalent(fn, device, [a])


def test_mean_combined_with_arithmetic(device: str, tensor_shapes: tuple):
    """Test mean combined with arithmetic operations"""

    def fn(x, y):
        mean_x = torch.mean(x, dim=-1, keepdim=True)
        return mean_x + y

    a = torch.randn(tensor_shapes)
    # Create y with compatible shape for broadcasting
    if len(tensor_shapes) == 0:
        y = torch.randn(())
    else:
        y_shape = list(tensor_shapes)
        y_shape[-1] = 1  # Make last dimension 1 for broadcasting
        y = torch.randn(y_shape)

    check_functions_are_equivalent(fn, device, [a, y])


def test_rsqrt_function(device: str):
    """Test torch.rsqrt() function"""

    def fn(x):
        return torch.rsqrt(x)

    x = torch.randn(3, 4).abs() + 0.1  # Ensure positive values for rsqrt

    check_functions_are_equivalent(fn, device, [x])


def test_sqrt_function(device: str):
    """Test torch.sqrt() function"""

    def fn(x):
        return torch.sqrt(x)

    x = torch.randn(3, 4).abs() + 0.01  # Ensure positive values for sqrt

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_rsqrt_method(device: str):
    """Test tensor.rsqrt() method"""

    def fn(x):
        return x.rsqrt()

    x = torch.randn(3, 4).abs() + 0.1  # Ensure positive values

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_sqrt_method(device: str):
    """Test tensor.sqrt() method"""

    def fn(x):
        return x.sqrt()

    x = torch.randn(3, 4).abs() + 0.01  # Ensure positive values

    check_functions_are_equivalent(fn, device, [x])


def test_rsqrt_different_shapes(device: str, tensor_shapes: tuple):
    """Test rsqrt with different tensor shapes"""

    def fn(x):
        return torch.rsqrt(x)

    x = torch.randn(tensor_shapes).abs() + 0.1

    check_functions_are_equivalent(fn, device, [x])


def test_sqrt_different_shapes(device: str, tensor_shapes: tuple):
    """Test sqrt with different tensor shapes"""

    def fn(x):
        return torch.sqrt(x)

    x = torch.randn(tensor_shapes).abs() + 0.01

    check_functions_are_equivalent(fn, device, [x])


def test_rsqrt_with_ones(device: str):
    """Test rsqrt with tensor of ones (should return ones)"""

    def fn(x):
        return torch.rsqrt(x)

    x = torch.ones(2, 3)

    check_functions_are_equivalent(fn, device, [x])


def test_sqrt_with_ones(device: str):
    """Test sqrt with tensor of ones (should return ones)"""

    def fn(x):
        return torch.sqrt(x)

    x = torch.ones(2, 3)

    check_functions_are_equivalent(fn, device, [x])


def test_rsqrt_with_powers_of_two(device: str):
    """Test rsqrt with powers of 2 for exact mathematical results"""

    def fn(x):
        return torch.rsqrt(x)

    x = torch.tensor([1.0, 4.0, 16.0, 64.0])  # Powers of 2

    check_functions_are_equivalent(fn, device, [x])


def test_sqrt_with_perfect_squares(device: str):
    """Test sqrt with perfect squares for exact mathematical results"""

    def fn(x):
        return torch.sqrt(x)

    x = torch.tensor([1.0, 4.0, 9.0, 16.0, 25.0])  # Perfect squares

    check_functions_are_equivalent(fn, device, [x])


def test_rsqrt_sqrt_relationship(device: str):
    """Test mathematical relationship: rsqrt(x) * sqrt(x) should equal x"""

    def fn(x):
        return torch.rsqrt(x) * torch.sqrt(x)

    x = torch.randn(3, 4).abs() + 0.1

    check_functions_are_equivalent(fn, device, [x])


def test_rsqrt_combined_with_arithmetic(device: str):
    """Test rsqrt combined with arithmetic operations"""

    def fn(x, y):
        rsqrt_x = torch.rsqrt(x)
        return rsqrt_x + y

    x = torch.randn(3, 4).abs() + 0.1
    y = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x, y])


def test_sqrt_combined_with_arithmetic(device: str):
    """Test sqrt combined with arithmetic operations"""

    def fn(x, y):
        sqrt_x = torch.sqrt(x)
        return sqrt_x * y

    x = torch.randn(3, 4).abs() + 0.01
    y = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x, y])


def test_chained_sqrt_rsqrt_operations(device: str):
    """Test chained sqrt and rsqrt operations"""

    def fn(x):
        # This should approximately equal x (with small numerical errors)
        return torch.sqrt(torch.rsqrt(x)).pow(2)

    x = torch.randn(3, 4).abs() + 0.1

    check_functions_are_equivalent(fn, device, [x])


def test_rsqrt_with_trigonometric_functions(device: str):
    """Test rsqrt combined with trigonometric functions"""

    def fn(x):
        rsqrt_x = torch.rsqrt(x)
        return torch.sin(rsqrt_x)

    x = torch.randn(3, 4).abs() + 0.1

    check_functions_are_equivalent(fn, device, [x])


def test_sqrt_with_trigonometric_functions(device: str):
    """Test sqrt combined with trigonometric functions"""

    def fn(x):
        sqrt_x = torch.sqrt(x)
        return torch.cos(sqrt_x)

    x = torch.randn(3, 4).abs() + 0.01

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_methods_chain_sqrt_rsqrt(device: str):
    """Test chaining tensor methods with sqrt and rsqrt"""

    def fn(x):
        return x.abs().sqrt().rsqrt()

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_sqrt_rsqrt_with_transpose(device: str):
    """Test sqrt and rsqrt with transpose operations"""

    def fn(x):
        x_t = x.transpose(0, 1)
        return torch.sqrt(x_t) + torch.rsqrt(x_t + 0.1)

    x = torch.randn(3, 4).abs() + 0.01

    check_functions_are_equivalent(fn, device, [x])


def test_sqrt_rsqrt_broadcasting(device: str):
    """Test sqrt and rsqrt with broadcasting"""

    def fn(x, y):
        sqrt_x = torch.sqrt(x)
        rsqrt_y = torch.rsqrt(y)
        return sqrt_x + rsqrt_y

    x = torch.randn(3, 1).abs() + 0.01
    y = torch.randn(1, 4).abs() + 0.1

    check_functions_are_equivalent(fn, device, [x, y])


def test_linear_basic(device: str):
    """Test basic linear function without bias"""

    def fn(input, weight):
        return F.linear(input, weight)

    in_features, out_features = 4, 3
    batch_size = 2

    input = torch.randn(batch_size, in_features)
    weight = torch.randn(out_features, in_features)

    check_functions_are_equivalent(fn, device, [input, weight])


def test_linear_with_bias(device: str):
    """Test linear function with bias"""

    def fn(input, weight, bias):
        return F.linear(input, weight, bias)

    in_features, out_features = 4, 3
    batch_size = 2

    input = torch.randn(batch_size, in_features)
    weight = torch.randn(out_features, in_features)
    bias = torch.randn(out_features)

    check_functions_are_equivalent(fn, device, [input, weight, bias])


def test_linear_small_dimensions(device: str):
    """Test linear function with small dimensions"""

    def fn(input, weight):
        return F.linear(input, weight)

    in_features, out_features = 8, 16
    batch_size = 3

    input = torch.randn(batch_size, in_features)
    weight = torch.randn(out_features, in_features)

    check_functions_are_equivalent(fn, device, [input, weight])


def test_linear_medium_dimensions(device: str):
    """Test linear function with medium dimensions"""

    def fn(input, weight):
        return F.linear(input, weight)

    in_features, out_features = 32, 10
    batch_size = 3

    input = torch.randn(batch_size, in_features)
    weight = torch.randn(out_features, in_features)

    check_functions_are_equivalent(fn, device, [input, weight])


def test_linear_single_dimension(device: str):
    """Test linear function with single dimensions"""

    def fn(input, weight):
        return F.linear(input, weight)

    in_features, out_features = 1, 1
    batch_size = 3

    input = torch.randn(batch_size, in_features)
    weight = torch.randn(out_features, in_features)

    check_functions_are_equivalent(fn, device, [input, weight])


def test_linear_3d_input(device: str):
    """Test linear function with 3D input (batch, sequence, features)"""

    def fn(input, weight, bias):
        return F.linear(input, weight, bias)

    batch_size, seq_length = 2, 5
    in_features, out_features = 8, 6

    input = torch.randn(batch_size, seq_length, in_features)
    weight = torch.randn(out_features, in_features)
    bias = torch.randn(out_features)

    check_functions_are_equivalent(fn, device, [input, weight, bias])


def test_linear_4d_input(device: str):
    """Test linear function with 4D input (..., features)"""

    def fn(input, weight):
        return F.linear(input, weight)

    batch_size, height, width = 2, 3, 4
    in_features, out_features = 7, 5

    input = torch.randn(batch_size, height, width, in_features)
    weight = torch.randn(out_features, in_features)

    check_functions_are_equivalent(fn, device, [input, weight])


def test_linear_1d_input(device: str):
    """Test linear function with 1D input (just features)"""

    def fn(input, weight, bias):
        return F.linear(input, weight, bias)

    in_features, out_features = 6, 4

    input = torch.randn(in_features)
    weight = torch.randn(out_features, in_features)
    bias = torch.randn(out_features)

    check_functions_are_equivalent(fn, device, [input, weight, bias])


def test_linear_chained(device: str):
    """Test chained linear functions (simple MLP)"""

    def fn(input, weight1, bias1, weight2, bias2):
        hidden = F.linear(input, weight1, bias1)
        output = F.linear(hidden, weight2, bias2)
        return output

    in_features, hidden_features, out_features = 4, 6, 2
    batch_size = 3

    input = torch.randn(batch_size, in_features)
    weight1 = torch.randn(hidden_features, in_features)
    bias1 = torch.randn(hidden_features)
    weight2 = torch.randn(out_features, hidden_features)
    bias2 = torch.randn(out_features)

    check_functions_are_equivalent(fn, device, [input, weight1, bias1, weight2, bias2])


def test_linear_broadcasting(device: str):
    """Test linear function with broadcasting scenarios"""

    def fn(input, weight, bias):
        return F.linear(input, weight, bias)

    in_features, out_features = 4, 3
    batch_size, seq_length = 2, 5

    # Test with different batch shapes
    input = torch.randn(batch_size, seq_length, in_features)
    weight = torch.randn(out_features, in_features)
    bias = torch.randn(out_features)  # Should broadcast across batch and sequence dims

    check_functions_are_equivalent(fn, device, [input, weight, bias])


def test_linear_single_feature(device: str):
    """Test linear function with single input/output feature"""

    def fn(input, weight, bias):
        return F.linear(input, weight, bias)

    in_features, out_features = 1, 1
    batch_size = 3

    input = torch.randn(batch_size, in_features)
    weight = torch.randn(out_features, in_features)
    bias = torch.randn(out_features)

    check_functions_are_equivalent(fn, device, [input, weight, bias])


def test_linear_large_dimensions(device: str):
    """Test linear function with larger dimensions"""

    def fn(input, weight):
        return F.linear(input, weight)

    in_features, out_features = 128, 64
    batch_size = 4

    input = torch.randn(batch_size, in_features)
    weight = torch.randn(out_features, in_features)

    check_functions_are_equivalent(fn, device, [input, weight], atol=1e-2, rtol=1e-2)


def test_linear_with_transpose(device: str):
    """Test linear function combined with transpose operations"""

    def fn(input, weight, bias):
        # Apply linear first, then transpose the result
        linear_out = F.linear(input, weight, bias)
        return linear_out.transpose(0, 1)  # Transpose output dimensions

    in_features, out_features = 6, 4
    batch_size = 3

    input = torch.randn(batch_size, in_features)
    weight = torch.randn(out_features, in_features)
    bias = torch.randn(out_features)

    check_functions_are_equivalent(fn, device, [input, weight, bias])


def test_linear_zero_bias(device: str):
    """Test linear function with zero bias"""

    def fn(input, weight, bias):
        return F.linear(input, weight, bias)

    in_features, out_features = 5, 3
    batch_size = 2

    input = torch.randn(batch_size, in_features)
    weight = torch.randn(out_features, in_features)
    bias = torch.zeros(out_features)  # Zero bias

    check_functions_are_equivalent(fn, device, [input, weight, bias])


def test_tensor_view_basic(device: str):
    """Test basic tensor.view() operation"""

    def fn(x):
        return x.view(6, 4)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_view_with_negative_one(device: str):
    """Test tensor.view() with -1 (infer dimension)"""

    def fn(x):
        return x.view(-1, 4)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_view_flatten(device: str):
    """Test tensor.view() to flatten tensor"""

    def fn(x):
        return x.view(-1)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_view_2d_to_3d(device: str):
    """Test tensor.view() from 2D to 3D"""

    def fn(x):
        return x.view(2, 3, 4)

    x = torch.randn(6, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_view_3d_to_2d(device: str):
    """Test tensor.view() from 3D to 2D"""

    def fn(x):
        return x.view(6, -1)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_view_same_shape(device: str):
    """Test tensor.view() with same shape (no-op)"""

    def fn(x):
        return x.view(2, 3, 4)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_view_single_dimension(device: str):
    """Test tensor.view() creating single dimension"""

    def fn(x):
        return x.view(24, 1)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_view_multiple_negative_one_dimensions(device: str):
    """Test tensor.view() with multiple inferred dimensions"""

    def fn(x):
        return x.view(2, -1, 2)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_view_with_arithmetic(device: str):
    """Test tensor.view() combined with arithmetic operations"""

    def fn(x, y):
        x_reshaped = x.view(-1, 4)
        return x_reshaped + y

    x = torch.randn(3, 2, 4)
    y = torch.randn(6, 4)

    check_functions_are_equivalent(fn, device, [x, y])


def test_tensor_view_chained_operations(device: str):
    """Test chained tensor.view() operations"""

    def fn(x):
        return x.view(6, 4).view(2, 12).view(-1)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_view_with_transpose(device: str):
    """Test tensor.view() combined with transpose"""

    def fn(x):
        # This should work since we're not changing the transpose result's shape
        x_t = x.transpose(0, 1)
        return x_t.view(3, 2, 4)  # Same total shape, just explicit dimensions

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_view_scalar_like(device: str):
    """Test tensor.view() with scalar-like tensors"""

    def fn(x):
        return x.view(1, 1, 1)

    x = torch.randn(1)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_view_large_dimensions(device: str):
    """Test tensor.view() with larger dimensions"""

    def fn(x):
        return x.view(8, -1)

    x = torch.randn(2, 4, 16)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_view_with_other_methods(device: str):
    """Test tensor.view() combined with other tensor methods"""

    def fn(x):
        return x.abs().view(-1, 4).cos()

    x = torch.randn(3, 2, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_view_broadcasting_prep(device: str):
    """Test tensor.view() for broadcasting preparation"""

    def fn(x, y):
        x_reshaped = x.view(2, 3, 1)
        return x_reshaped + y

    x = torch.randn(6)
    y = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x, y])


def test_tensor_contiguous_basic(device: str):
    """Test basic tensor.contiguous() operation"""

    def fn(x):
        return x.contiguous()

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_contiguous_with_transpose(device: str):
    """Test tensor.contiguous() after transpose"""

    def fn(x):
        x_t = x.transpose(0, 1)
        return x_t.contiguous()

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_contiguous_view_chain(device: str):
    """Test tensor.contiguous().view() chain"""

    def fn(x):
        x_t = x.transpose(0, 1)
        return x_t.contiguous().view(-1, 4)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_unsqueeze_basic(device: str):
    """Test basic tensor.unsqueeze() operation"""

    def fn(x):
        return x.unsqueeze(0)

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_unsqueeze_middle_dim(device: str):
    """Test tensor.unsqueeze() in middle dimension"""

    def fn(x):
        return x.unsqueeze(1)

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_unsqueeze_last_dim(device: str):
    """Test tensor.unsqueeze() at last dimension"""

    def fn(x):
        return x.unsqueeze(-1)

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_unsqueeze_negative_dim(device: str):
    """Test tensor.unsqueeze() with negative dimension"""

    def fn(x):
        return x.unsqueeze(-2)

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_unsqueeze_multiple_ops(device: str):
    """Test multiple tensor.unsqueeze() operations"""

    def fn(x):
        return x.unsqueeze(0).unsqueeze(-1)

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_unsqueeze_with_view(device: str):
    """Test tensor.unsqueeze() combined with view()"""

    def fn(x):
        x_unsq = x.unsqueeze(1)  # (2, 3) -> (2, 1, 3)
        return x_unsq.view(2, 3)  # (2, 1, 3) -> (2, 3)

    x = torch.randn(2, 3)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_unsqueeze_1d_tensor(device: str):
    """Test tensor.unsqueeze() on 1D tensor"""

    def fn(x):
        return x.unsqueeze(0)

    x = torch.randn(5)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_unsqueeze_scalar(device: str):
    """Test tensor.unsqueeze() on scalar tensor"""

    def fn(x):
        return x.unsqueeze(0)

    x = torch.randn(())

    check_functions_are_equivalent(fn, device, [x])


def test_unary_negation(device: str):
    """Test unary negation operator (-x)"""

    def fn(x):
        return -x

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_negation_with_arithmetic(device: str):
    """Test negation combined with arithmetic operations"""

    def fn(x, y):
        return -x + y

    x = torch.randn(3, 4)
    y = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x, y])


def test_double_negation(device: str):
    """Test double negation (-(-x))"""

    def fn(x):
        return -(-x)

    x = torch.randn(3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_negation_different_shapes(device: str, tensor_shapes: tuple):
    """Test negation with different tensor shapes"""

    def fn(x):
        return -x

    x = torch.randn(tensor_shapes)

    check_functions_are_equivalent(fn, device, [x])


def test_max_pool2d_basic(device: str):
    """Test basic max_pool2d operation"""

    def fn(x):
        return F.max_pool2d(x, kernel_size=2)

    batch_size, channels, height, width = 2, 3, 8, 8
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [x])


def test_max_pool2d_with_stride(device: str):
    """Test max_pool2d with custom stride"""

    def fn(x):
        return F.max_pool2d(x, kernel_size=3, stride=2)

    batch_size, channels, height, width = 2, 4, 12, 12
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [x])


def test_max_pool2d_with_padding(device: str):
    """Test max_pool2d with padding"""

    def fn(x):
        return F.max_pool2d(x, kernel_size=2, padding=1)

    batch_size, channels, height, width = 2, 3, 6, 6
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [x])


def test_max_pool2d_asymmetric_kernel(device: str):
    """Test max_pool2d with asymmetric kernel"""

    def fn(x):
        return F.max_pool2d(x, kernel_size=(2, 3), stride=(1, 2), padding=(1, 0))

    batch_size, channels, height, width = 2, 3, 8, 9
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [x])


def test_max_pool2d_various_sizes(device: str):
    """Test max_pool2d with various input sizes"""

    def fn(x):
        return F.max_pool2d(x, kernel_size=2, stride=2)

    # Test different sizes
    for height, width in [(16, 16), (32, 24), (7, 11)]:
        batch_size, channels = 1, 2
        x = torch.randn(batch_size, channels, height, width)

        check_functions_are_equivalent(fn, device, [x])


def test_adaptive_avg_pool2d_global(device: str):
    """Test adaptive_avg_pool2d with (1, 1) output (global pooling)"""

    def fn(x):
        return F.adaptive_avg_pool2d(x, (1, 1))

    batch_size, channels, height, width = 2, 3, 8, 8
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [x])


def test_adaptive_avg_pool2d_7x7(device: str):
    """Test adaptive_avg_pool2d with (7, 7) output like in VGG"""

    def fn(x):
        return F.adaptive_avg_pool2d(x, (7, 7))

    batch_size, channels, height, width = 2, 512, 14, 14
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [x])


def test_adaptive_avg_pool2d_various_outputs(device: str):
    """Test adaptive_avg_pool2d with various output sizes"""

    def fn_2x2(x):
        return F.adaptive_avg_pool2d(x, (2, 2))

    def fn_4x4(x):
        return F.adaptive_avg_pool2d(x, (4, 4))

    batch_size, channels, height, width = 2, 64, 16, 16
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn_2x2, device, [x])
    check_functions_are_equivalent(fn_4x4, device, [x])


def test_avg_pool2d_basic(device: str):
    """Test basic avg_pool2d with 2x2 kernel"""

    def fn(x):
        return F.avg_pool2d(x, kernel_size=2)

    batch_size, channels, height, width = 1, 3, 8, 8
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [x])


def test_avg_pool2d_with_stride(device: str):
    """Test avg_pool2d with custom stride"""

    def fn(x):
        return F.avg_pool2d(x, kernel_size=3, stride=2)

    batch_size, channels, height, width = 2, 16, 10, 10
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [x])


def test_avg_pool2d_with_padding(device: str):
    """Test avg_pool2d with padding"""

    def fn(x):
        return F.avg_pool2d(x, kernel_size=2, stride=2, padding=1)

    batch_size, channels, height, width = 1, 8, 6, 6
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [x])


def test_avg_pool2d_asymmetric_kernel(device: str):
    """Test avg_pool2d with asymmetric kernel size"""

    def fn(x):
        return F.avg_pool2d(x, kernel_size=(2, 3), stride=(1, 2))

    batch_size, channels, height, width = 1, 4, 8, 9
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [x])


def test_avg_pool2d_various_sizes(device: str):
    """Test avg_pool2d with various input sizes and parameters"""

    def fn_small(x):
        return F.avg_pool2d(x, kernel_size=2, stride=1)

    def fn_large(x):
        return F.avg_pool2d(x, kernel_size=4, stride=4)

    # Small input
    x_small = torch.randn(1, 8, 5, 5)
    check_functions_are_equivalent(fn_small, device, [x_small])

    # Larger input
    x_large = torch.randn(2, 32, 16, 16)
    check_functions_are_equivalent(fn_large, device, [x_large])


def test_flatten_basic(device: str):
    """Test basic flatten operation"""

    def fn(x):
        return torch.flatten(x, start_dim=1)

    batch_size, channels, height, width = 2, 3, 4, 5
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [x])


def test_flatten_different_start_dims(device: str):
    """Test flatten with different start dimensions"""

    def fn_start_0(x):
        return torch.flatten(x, start_dim=0)

    def fn_start_2(x):
        return torch.flatten(x, start_dim=2)

    x = torch.randn(2, 3, 4, 5)

    check_functions_are_equivalent(fn_start_0, device, [x])
    check_functions_are_equivalent(fn_start_2, device, [x])


def test_flatten_with_end_dim(device: str):
    """Test flatten with specific end dimension"""

    def fn(x):
        return torch.flatten(x, start_dim=1, end_dim=2)

    x = torch.randn(2, 3, 4, 5)

    check_functions_are_equivalent(fn, device, [x])


def test_flatten_negative_dims(device: str):
    """Test flatten with negative dimensions"""

    def fn(x):
        return torch.flatten(x, start_dim=-2, end_dim=-1)

    x = torch.randn(2, 3, 4, 5)

    check_functions_are_equivalent(fn, device, [x])


def test_dropout_inference(device: str):
    """Test dropout in inference mode (should be no-op)"""

    def fn(x):
        return F.dropout(x, p=0.5, training=False)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


def test_dropout_different_probabilities(device: str):
    """Test dropout with different dropout probabilities in inference"""

    def fn_p01(x):
        return F.dropout(x, p=0.1, training=False)

    def fn_p05(x):
        return F.dropout(x, p=0.5, training=False)

    def fn_p09(x):
        return F.dropout(x, p=0.9, training=False)

    x = torch.randn(3, 4, 5)

    check_functions_are_equivalent(fn_p01, device, [x])
    check_functions_are_equivalent(fn_p05, device, [x])
    check_functions_are_equivalent(fn_p09, device, [x])


def test_combined_vgg_like_ops(device: str):
    """Test combining VGG-like operations together"""

    def fn(x, weight, bias):
        # Simulate a VGG-like block
        conv_out = F.conv2d(x, weight, bias, padding=1)
        relu_out = F.relu(conv_out)
        pool_out = F.max_pool2d(relu_out, kernel_size=2, stride=2)
        return pool_out

    batch_size, in_channels, height, width = 2, 3, 8, 8
    out_channels, kernel_size = 64, 3

    x = torch.randn(batch_size, in_channels, height, width)
    weight = torch.randn(out_channels, in_channels, kernel_size, kernel_size)
    bias = torch.randn(out_channels)

    check_functions_are_equivalent(fn, device, [x, weight, bias])


def test_max_pool2d_ceil_mode(device: str):
    """Test max_pool2d with ceil_mode=True"""

    def fn(x):
        return F.max_pool2d(x, kernel_size=2, stride=2, ceil_mode=True)

    # Use odd spatial dimensions to test ceil_mode effect
    batch_size, channels, height, width = 2, 3, 7, 7
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [x])


def test_max_pool2d_with_conv2d_chain(device: str):
    """Test max_pool2d chained with conv2d operations"""

    def fn(x, weight1, bias1, weight2, bias2):
        conv1 = F.conv2d(x, weight1, bias1)
        pool1 = F.max_pool2d(conv1, kernel_size=2)
        conv2 = F.conv2d(pool1, weight2, bias2)
        pool2 = F.max_pool2d(conv2, kernel_size=2)
        return pool2

    batch_size, in_channels = 2, 3
    hidden_channels, out_channels = 16, 32
    height, width = 16, 16

    x = torch.randn(batch_size, in_channels, height, width)
    weight1 = torch.randn(hidden_channels, in_channels, 3, 3)
    bias1 = torch.randn(hidden_channels)
    weight2 = torch.randn(out_channels, hidden_channels, 3, 3)
    bias2 = torch.randn(out_channels)

    check_functions_are_equivalent(fn, device, [x, weight1, bias1, weight2, bias2])


def test_flatten_after_pooling(device: str):
    """Test flatten operation after pooling (common CNN pattern)"""

    def fn(x):
        pooled = F.adaptive_avg_pool2d(x, (4, 4))
        flattened = torch.flatten(pooled, 1)
        return flattened

    batch_size, channels, height, width = 3, 64, 12, 12
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.xfail(reason="Dropout training mode not implemented yet")
def test_dropout_training_mode(device: str):
    """Test dropout in training mode (should raise NotImplementedError)"""

    def fn(x):
        return F.dropout(x, p=0.5, training=True)

    x = torch.randn(2, 3, 4)

    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.xfail(reason="max_pool2d with return_indices not implemented yet")
def test_max_pool2d_return_indices(device: str):
    """Test max_pool2d with return_indices=True (should raise NotImplementedError)"""

    def fn(x):
        return F.max_pool2d(x, kernel_size=2, return_indices=True)

    batch_size, channels, height, width = 2, 3, 4, 4
    x = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [x])


def test_tril_basic(device: str):
    """Test basic tril operation on 2D tensor"""

    def fn(x):
        return torch.tril(x)

    x = torch.randn(4, 4)
    check_functions_are_equivalent(fn, device, [x])


def test_tril_with_positive_diagonal(device: str):
    """Test tril with positive diagonal offset"""

    def fn(x):
        return torch.tril(x, diagonal=1)

    x = torch.randn(5, 5)
    check_functions_are_equivalent(fn, device, [x])


def test_tril_with_negative_diagonal(device: str):
    """Test tril with negative diagonal offset"""

    def fn(x):
        return torch.tril(x, diagonal=-1)

    x = torch.randn(4, 4)
    check_functions_are_equivalent(fn, device, [x])


def test_tril_rectangular_matrix_tall(device: str):
    def fn(x):
        return torch.tril(x)

    # Test both tall and wide matrices
    x_tall = torch.randn(6, 4)

    check_functions_are_equivalent(fn, device, [x_tall])


def test_tril_rectangular_matrix_wide(device: str):
    def fn(x):
        return torch.tril(x)

    # Test both tall and wide matrices
    x_wide = torch.randn(3, 7)
    check_functions_are_equivalent(fn, device, [x_wide])


def test_tril_3_dimensions(device: str):
    """Test tril on 3D tensor (should apply tril to each 2D slice)"""

    def fn(x):
        return torch.tril(x)

    x = torch.randn(2, 4, 6)  # 2 slices of 4x4 matrices
    check_functions_are_equivalent(fn, device, [x])


def test_tril_4_dimensions(device: str):
    """Test tril on 4D tensor (should apply tril to each 2D slice)"""

    def fn(x):
        return torch.tril(x)

    x = torch.randn(2, 3, 4, 5)  # 2 batches of 3 slices of 4x4 matrices
    check_functions_are_equivalent(fn, device, [x])


def test_tril_int32(device: str):
    """Test tril with float32 tensors"""

    def fn(x):
        return torch.tril(x)

    # Test with float32 (main supported type)
    x_float32 = torch.randint(0, 5, (3, 3), dtype=torch.int32)
    check_functions_are_equivalent(fn, device, [x_float32])


def test_split_basic(device: str):
    """Test basic tensor splitting"""

    def fn(x):
        return torch.split(x, 2, 0)

    x = torch.randn(6, 4)
    check_functions_are_equivalent(fn, device, [x])


def test_split_uneven_second_dim(device: str):
    """Test tensor splitting with uneven split sizes"""

    def fn(x):
        return torch.split(x, 3, 1)

    # 7 elements split by 3 should give splits of [3, 3, 1]
    x = torch.randn(2, 7)
    check_functions_are_equivalent(fn, device, [x])


def test_split_uneven(device: str):
    """Test tensor splitting with uneven split sizes"""

    def fn(x):
        return torch.split(x, 3, 0)

    # 7 elements split by 3 should give splits of [3, 3, 1]
    x = torch.randn(7, 4)
    check_functions_are_equivalent(fn, device, [x])


def test_split_different_dims(device: str):
    """Test tensor splitting along different dimensions"""

    def fn_dim0(x):
        return torch.split(x, 2, 0)

    def fn_dim1(x):
        return torch.split(x, 3, 1)

    x = torch.randn(4, 6)

    check_functions_are_equivalent(fn_dim0, device, [x])
    check_functions_are_equivalent(fn_dim1, device, [x])


def test_split_single_element(device: str):
    """Test tensor splitting into single elements"""

    def fn(x):
        return torch.split(x, 1, 0)

    x = torch.randn(3, 2)
    check_functions_are_equivalent(fn, device, [x])


def test_chunk_basic(device: str):
    """Test basic tensor chunking"""

    def fn(x):
        return torch.chunk(x, 2, 0)

    x = torch.randn(6, 4, device=device)
    check_functions_are_equivalent(fn, device, [x])


def test_chunk_uneven(device: str):
    """Test tensor chunking with uneven split"""

    def fn(x):
        return torch.chunk(x, 3, 0)

    x = torch.randn(8, 4, device=device)  # 8 doesn't divide evenly by 3
    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.parametrize("chunks", [2, 3, 4])
def test_chunk_different_num_chunks(device: str, chunks: int):
    """Test tensor chunking with different number of chunks"""

    def fn(x):
        return torch.chunk(x, chunks, 0)

    x = torch.randn(12, 8, device=device)
    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.parametrize("dim", [0, 1, -1])
def test_chunk_different_dims(device: str, dim: int):
    """Test tensor chunking along different dimensions"""

    def fn(x):
        return torch.chunk(x, 2, dim)

    x = torch.randn(4, 6, device=device)
    check_functions_are_equivalent(fn, device, [x])


def test_chunk_3d_tensor(device: str):
    """Test tensor chunking on 3D tensor"""

    def fn(x):
        return torch.chunk(x, 2, 1)

    x = torch.randn(2, 8, 3, device=device)
    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.parametrize("shapes", [(8,), (3, 4), (2, 3, 4)])
def test_torch_clamp_both_bounds(device: str, shapes):
    """Test torch.clamp with both min and max bounds."""

    def fn(x):
        return torch.clamp(x, min=-0.5, max=0.5)

    a = torch.randn(shapes)

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("shapes", [(8,), (3, 4), (2, 3, 4)])
def test_torch_clamp_min_only(device: str, shapes):
    """Test torch.clamp with only min bound."""

    def fn(x):
        return torch.clamp(x, min=-1.0)

    a = torch.randn(shapes)

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("shapes", [(8,), (3, 4), (2, 3, 4)])
def test_torch_clamp_max_only(device: str, shapes):
    """Test torch.clamp with only max bound."""

    def fn(x):
        return torch.clamp(x, max=1.0)

    a = torch.randn(shapes)

    check_functions_are_equivalent(fn, device, [a])


def test_torch_clamp_tensor_bounds(device: str, tensor_shapes: tuple):
    """Test torch.clamp with tensor bounds (min and max as tensors)."""

    def fn(x, min_tensor, max_tensor):
        return torch.clamp(x, min=min_tensor, max=max_tensor)

    a = torch.randn(tensor_shapes)
    min_tensor = torch.full(tensor_shapes, -0.5)
    max_tensor = torch.full(tensor_shapes, 0.5)

    check_functions_are_equivalent(fn, device, [a, min_tensor, max_tensor])


def test_torch_clamp_edge_cases(device: str):
    """Test torch.clamp edge cases with specific values."""

    def fn_identical_bounds(x):
        # When min equals max, all values should be set to that value
        return torch.clamp(x, min=0.5, max=0.5)

    def fn_inverted_bounds(x):
        # When min > max, PyTorch sets all values to max
        return torch.clamp(x, min=1.0, max=0.5)

    a = torch.tensor([-2.0, -0.5, 0.0, 0.5, 1.0, 2.0])

    check_functions_are_equivalent(fn_identical_bounds, device, [a])
    check_functions_are_equivalent(fn_inverted_bounds, device, [a])


def test_torch_arange_single_arg_int(device: str):
    def fn():
        return torch.arange(5, device=torch.device(device))

    check_functions_are_equivalent(fn, device, [])


def test_torch_arange_two_args(device: str):
    def fn():
        return torch.arange(1, 8, device=torch.device(device))

    check_functions_are_equivalent(fn, device, [])


def test_torch_arange_two_args_negative(device: str):
    def fn():
        return torch.arange(-3, 2, device=torch.device(device))

    check_functions_are_equivalent(fn, device, [])


def test_torch_arange_three_args(device: str):
    def fn():
        return torch.arange(0, 10, 2, device=torch.device(device))

    check_functions_are_equivalent(fn, device, [])


def test_torch_arange_negative_step(device: str):
    def fn():
        return torch.arange(10, 0, -1, device=torch.device(device))

    check_functions_are_equivalent(fn, device, [])


def test_torch_arange_negative_step_invert_bounds(device: str):
    def fn():
        return torch.arange(10, 0, -1, device=torch.device(device))

    check_functions_are_equivalent(fn, device, [])


def test_torch_arange_force_dtype_float(device: str):
    def fn():
        return torch.arange(5, dtype=torch.float32, device=torch.device(device))

    check_functions_are_equivalent(fn, device, [])


def test_torch_arange_force_dtype_int(device: str):
    def fn():
        return torch.arange(5, dtype=torch.int32, device=torch.device(device))

    check_functions_are_equivalent(fn, device, [])


def test_layer_norm_basic(device: str):
    def fn(x):
        return F.layer_norm(x, normalized_shape=(10,))

    input_tensor = torch.randn(5, 10)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_layer_norm_with_weight_bias(device: str):
    def fn(x, weight, bias):
        return F.layer_norm(x, normalized_shape=(10,), weight=weight, bias=bias)

    input_tensor = torch.randn(5, 10)
    weight = torch.randn(10)
    bias = torch.randn(10)
    check_functions_are_equivalent(fn, device, [input_tensor, weight, bias])


def test_layer_norm_multidim(device: str):
    def fn(x):
        return F.layer_norm(x, normalized_shape=(3, 4))

    input_tensor = torch.randn(2, 5, 3, 4)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_layer_norm_custom_eps(device: str):
    def fn(x):
        return F.layer_norm(x, normalized_shape=(10,), eps=1e-6)

    input_tensor = torch.randn(5, 10)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_gelu_basic(device: str):
    def fn(x):
        return F.gelu(x)

    input_tensor = torch.randn(5, 10)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_gelu_tanh_approx(device: str):
    def fn(x):
        return F.gelu(x, approximate="tanh")

    input_tensor = torch.randn(5, 10)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_gelu_negative_values(device: str):
    def fn(x):
        return F.gelu(x)

    input_tensor = torch.randn(5, 10) - 2.0  # Mostly negative values
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_softmax_basic(device: str):
    def fn(x):
        return F.softmax(x, dim=-1)

    input_tensor = torch.randn(5, 10)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_softmax_dim_0(device: str):
    def fn(x):
        return F.softmax(x, dim=0)

    input_tensor = torch.randn(5, 10)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_softmax_dim_1(device: str):
    def fn(x):
        return F.softmax(x, dim=1)

    input_tensor = torch.randn(5, 10)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_softmax_multidim(device: str):
    def fn(x):
        return F.softmax(x, dim=2)

    input_tensor = torch.randn(3, 4, 5)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_softmax_negative_dim(device: str):
    def fn(x):
        return F.softmax(x, dim=-2)

    input_tensor = torch.randn(3, 4, 5)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_sum_basic(device: str):
    def fn(x):
        return torch.sum(x)

    input_tensor = torch.randn(5, 10)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_sum_with_dim(device: str):
    def fn(x):
        return torch.sum(x, dim=1)

    input_tensor = torch.randn(5, 10)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_sum_with_keepdim(device: str):
    def fn(x):
        return torch.sum(x, dim=1, keepdim=True)

    input_tensor = torch.randn(5, 10)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_sum_multiple_dims(device: str):
    def fn(x):
        return torch.sum(x, dim=[1, 2])

    input_tensor = torch.randn(3, 4, 5)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_sum_multiple_dims_keepdim(device: str):
    def fn(x):
        return torch.sum(x, dim=[1, 2], keepdim=True)

    input_tensor = torch.randn(3, 4, 5)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_sum_negative_dim(device: str):
    def fn(x):
        return torch.sum(x, dim=-1)

    input_tensor = torch.randn(3, 4, 5)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_cumsum_basic(device: str):
    """Test basic cumsum operation along dimension 0"""

    def fn(x):
        return torch.cumsum(x, dim=0)

    input_tensor = torch.randn(5, 3)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_cumsum_different_dims(device: str):
    """Test cumsum along different dimensions"""

    def fn_dim0(x):
        return torch.cumsum(x, dim=0)

    def fn_dim1(x):
        return torch.cumsum(x, dim=1)

    def fn_dim2(x):
        return torch.cumsum(x, dim=2)

    input_tensor = torch.randn(3, 4, 5)

    check_functions_are_equivalent(fn_dim0, device, [input_tensor])
    check_functions_are_equivalent(fn_dim1, device, [input_tensor])
    check_functions_are_equivalent(fn_dim2, device, [input_tensor])


def test_cumsum_negative_dim(device: str):
    """Test cumsum with negative dimension index"""

    def fn(x):
        return torch.cumsum(x, dim=-1)

    input_tensor = torch.randn(3, 4, 5)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_cumsum_with_dtype(device: str):
    """Test cumsum with dtype conversion"""

    def fn(x):
        return torch.cumsum(x, dim=1, dtype=torch.float32)

    # Start with integer tensor to test dtype conversion
    input_tensor = torch.randint(
        0, 10, (4, 6)
    ).float()  # Convert to float for consistency
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_cumsum_1d_tensor(device: str):
    """Test cumsum on 1D tensor"""

    def fn(x):
        return torch.cumsum(x, dim=0)

    input_tensor = torch.randn(10)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_cumsum_large_tensor(device: str):
    """Test cumsum on larger tensor"""

    def fn(x):
        return torch.cumsum(x, dim=1)

    input_tensor = torch.randn(8, 16, 4)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_masked_fill_basic(device: str):
    def fn(x, mask):
        return x.masked_fill(mask, -float("inf"))

    input_tensor = torch.randn(5, 10)
    mask = torch.randint(0, 2, (5, 10), dtype=torch.bool)
    check_functions_are_equivalent(fn, device, [input_tensor, mask])


def test_masked_fill_scalar_value(device: str):
    def fn(x, mask):
        return x.masked_fill(mask, 0.0)

    input_tensor = torch.randn(5, 10)
    mask = torch.randint(0, 2, (5, 10), dtype=torch.bool)
    check_functions_are_equivalent(fn, device, [input_tensor, mask])


def test_masked_fill_broadcast(device: str):
    def fn(x, mask):
        return x.masked_fill(mask, 99.0)

    input_tensor = torch.randn(3, 4, 5)
    mask = torch.randint(0, 2, (4, 5), dtype=torch.bool)
    check_functions_are_equivalent(fn, device, [input_tensor, mask])


def test_reshape_basic(device: str):
    def fn(x):
        return x.reshape(6, 4)

    input_tensor = torch.randn(3, 8)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_reshape_flatten(device: str):
    def fn(x):
        return x.reshape(-1)

    input_tensor = torch.randn(2, 3, 4)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_reshape_with_negative_dim(device: str):
    def fn(x):
        return x.reshape(2, -1, 3)

    input_tensor = torch.randn(2, 4, 3)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_unbind_basic(device: str):
    def fn(x):
        # unbind returns a tuple, so we convert to list for testing
        return list(x.unbind(dim=0))

    input_tensor = torch.randn(3, 4, 5)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_unbind_different_dim(device: str):
    def fn(x):
        return list(x.unbind(dim=1))

    input_tensor = torch.randn(2, 3, 4)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_unbind_negative_dim(device: str):
    def fn(x):
        return list(x.unbind(dim=-1))

    input_tensor = torch.randn(2, 3, 4)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_repeat_basic(device: str):
    def fn(x):
        return x.repeat(2, 3)

    input_tensor = torch.randn(2, 3)
    check_functions_are_equivalent(fn, device, [input_tensor])


@pytest.mark.parametrize("repeats", [(2,), (2, 3), (1, 2, 3), (2, 1, 3)])
def test_repeat_different_repeats(device: str, repeats):
    def fn(x):
        return x.repeat(*repeats)

    # Create tensor with appropriate shape for the repeat operation
    if len(repeats) == 1:
        input_tensor = torch.randn(3)
    elif len(repeats) == 2:
        input_tensor = torch.randn(2, 3)
    elif len(repeats) == 3:
        input_tensor = torch.randn(2, 3, 4)
    else:
        input_tensor = torch.randn(2, 3)

    check_functions_are_equivalent(fn, device, [input_tensor])


def test_repeat_1d(device: str):
    def fn(x):
        return x.repeat(3)

    input_tensor = torch.randn(4)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_repeat_2d(device: str):
    def fn(x):
        return x.repeat(2, 3)

    input_tensor = torch.randn(2, 4)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_repeat_3d(device: str):
    def fn(x):
        return x.repeat(2, 1, 3)

    input_tensor = torch.randn(1, 3, 2)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_repeat_interleave_basic(device: str):
    def fn(x):
        return x.repeat_interleave(2, dim=0)

    input_tensor = torch.randn(3, 4)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_repeat_interleave_different_dim(device: str):
    def fn(x):
        return x.repeat_interleave(3, dim=1)

    input_tensor = torch.randn(2, 4, 5)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_repeat_interleave_negative_dim(device: str):
    def fn(x):
        return x.repeat_interleave(2, dim=-1)

    input_tensor = torch.randn(3, 4, 5)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_torch_full_basic(device: str):
    def fn():
        return torch.full((3, 4), -float("inf"))

    check_functions_are_equivalent(fn, device, [])


def test_torch_full_with_dtype(device: str):
    def fn():
        return torch.full((2, 3), 5.5, dtype=torch.float32)

    check_functions_are_equivalent(fn, device, [])


def test_torch_triu_basic(device: str):
    def fn(x):
        return torch.triu(x)

    input_tensor = torch.randn(4, 4)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_torch_triu_with_diagonal(device: str):
    def fn(x):
        return torch.triu(x, diagonal=1)

    input_tensor = torch.randn(3, 3)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_silu_activation(device: str):
    def fn(x):
        return F.silu(x)

    input_tensor = torch.randn(3, 4, 5)
    check_functions_are_equivalent(fn, device, [input_tensor])


def test_mse_loss_default_reduction(device: str):
    """Test MSE loss with default mean reduction"""

    def fn(input_tensor, target):
        return F.mse_loss(input_tensor, target)

    input_tensor = torch.randn(3, 4)
    target = torch.randn(3, 4)
    check_functions_are_equivalent(fn, device, [input_tensor, target])


def test_mse_loss_mean_reduction(device: str):
    """Test MSE loss with explicit mean reduction"""

    def fn(input_tensor, target):
        return F.mse_loss(input_tensor, target, reduction="mean")

    input_tensor = torch.randn(2, 5)
    target = torch.randn(2, 5)
    check_functions_are_equivalent(fn, device, [input_tensor, target])


def test_mse_loss_sum_reduction(device: str):
    """Test MSE loss with sum reduction"""

    def fn(input_tensor, target):
        return F.mse_loss(input_tensor, target, reduction="sum")

    input_tensor = torch.randn(3, 3)
    target = torch.randn(3, 3)
    check_functions_are_equivalent(fn, device, [input_tensor, target])


def test_mse_loss_none_reduction(device: str):
    """Test MSE loss with no reduction (returns element-wise squared differences)"""

    def fn(input_tensor, target):
        return F.mse_loss(input_tensor, target, reduction="none")

    input_tensor = torch.randn(2, 3)
    target = torch.randn(2, 3)
    check_functions_are_equivalent(fn, device, [input_tensor, target])


def test_mse_loss_1d(device: str):
    """Test MSE loss on 1D tensors"""

    def fn(input_tensor, target):
        return F.mse_loss(input_tensor, target)

    input_tensor = torch.randn(10)
    target = torch.randn(10)
    check_functions_are_equivalent(fn, device, [input_tensor, target])


def test_mse_loss_3d(device: str):
    """Test MSE loss on 3D tensors"""

    def fn(input_tensor, target):
        return F.mse_loss(input_tensor, target)

    input_tensor = torch.randn(2, 3, 4)
    target = torch.randn(2, 3, 4)
    check_functions_are_equivalent(fn, device, [input_tensor, target])


def test_addmm_basic(device: str):
    """Test basic torch.addmm operation"""

    def fn(bias, mat1, mat2):
        return torch.addmm(bias, mat1, mat2)

    bias = torch.randn(3, 4)
    mat1 = torch.randn(3, 5)
    mat2 = torch.randn(5, 4)
    check_functions_are_equivalent(fn, device, [bias, mat1, mat2])


def test_addmm_with_alpha_beta(device: str):
    """Test torch.addmm with custom alpha and beta parameters"""

    def fn(bias, mat1, mat2):
        return torch.addmm(bias, mat1, mat2, alpha=2.0, beta=0.5)

    bias = torch.randn(3, 4)
    mat1 = torch.randn(3, 5)
    mat2 = torch.randn(5, 4)
    check_functions_are_equivalent(fn, device, [bias, mat1, mat2])


def test_addmm_different_shapes(device: str):
    """Test torch.addmm with different matrix shapes"""

    def fn(bias, mat1, mat2):
        return torch.addmm(bias, mat1, mat2)

    bias = torch.randn(2, 8)
    mat1 = torch.randn(2, 6)
    mat2 = torch.randn(6, 8)
    check_functions_are_equivalent(fn, device, [bias, mat1, mat2])


def test_addmm_broadcast_bias(device: str):
    """Test torch.addmm with bias that needs broadcasting"""

    def fn(bias, mat1, mat2):
        return torch.addmm(bias, mat1, mat2)

    bias = torch.randn(4)  # Will broadcast to (3, 4)
    mat1 = torch.randn(3, 5)
    mat2 = torch.randn(5, 4)
    check_functions_are_equivalent(fn, device, [bias, mat1, mat2])


def test_bmm_basic(device: str):
    """Test basic torch.bmm operation (batch matrix multiplication)"""

    def fn(input, mat2):
        return torch.bmm(input, mat2)

    # Create batch matrix multiplication inputs: [batch, n, m] x [batch, m, p] = [batch, n, p]
    batch_size, n, m, p = 4, 3, 5, 6
    input = torch.randn(batch_size, n, m)
    mat2 = torch.randn(batch_size, m, p)

    check_functions_are_equivalent(fn, device, [input, mat2])


def test_bmm_different_batch_sizes(device: str):
    """Test torch.bmm with different batch sizes and matrix dimensions"""

    def fn(input, mat2):
        return torch.bmm(input, mat2)

    # Different batch size and matrix dimensions
    batch_size, n, m, p = 2, 4, 3, 7
    input = torch.randn(batch_size, n, m)
    mat2 = torch.randn(batch_size, m, p)

    check_functions_are_equivalent(fn, device, [input, mat2])


def test_bmm_single_batch(device: str):
    """Test torch.bmm with single batch dimension"""

    def fn(input, mat2):
        return torch.bmm(input, mat2)

    # Single batch case
    input = torch.randn(1, 2, 4)
    mat2 = torch.randn(1, 4, 3)

    check_functions_are_equivalent(fn, device, [input, mat2])


def test_exp(device: str):
    def fn(input):
        return torch.exp(input)

    # Single batch case
    input = torch.randn(1, 2, 4)

    check_functions_are_equivalent(fn, device, [input])


def test_group_norm(device: str):
    """Test F.group_norm with various configurations"""

    def fn(input):
        return F.group_norm(input, 2)

    # Test case: 4 channels, 2 groups
    batch_size, channels, height, width = 2, 4, 8, 8
    input = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [input])


def test_group_norm_with_weight_bias(device: str):
    """Test F.group_norm with weight and bias parameters"""

    def fn(input, weight, bias):
        return F.group_norm(input, 3, weight, bias)

    # Test case: 6 channels, 3 groups
    batch_size, channels, height, width = 1, 6, 4, 4
    input = torch.randn(batch_size, channels, height, width)
    weight = torch.randn(channels)
    bias = torch.randn(channels)

    check_functions_are_equivalent(fn, device, [input, weight, bias])


def test_group_norm_eps(device: str):
    """Test F.group_norm with custom eps parameter"""

    def fn(input):
        return F.group_norm(input, 4, eps=1e-6)

    # Test case: 8 channels, 4 groups
    batch_size, channels, height, width = 1, 8, 2, 2
    input = torch.randn(batch_size, channels, height, width)

    check_functions_are_equivalent(fn, device, [input])


def test_logical_not_bool(device: str):
    """Test torch.logical_not with boolean tensors"""

    def fn(x):
        return torch.logical_not(x)

    # Test with boolean tensor
    a = torch.tensor([True, False, True, False])

    check_functions_are_equivalent(fn, device, [a])


def test_logical_not_numeric(device: str):
    """Test torch.logical_not with numeric tensors"""

    def fn(x):
        return torch.logical_not(x)

    # Test with numeric tensor (non-zero values are treated as True)
    a = torch.tensor([0, 1, 2, -1, 0.0])

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("shapes", [(3, 4), (2, 3, 4), (5,)])
def test_logical_not_shapes(device: str, shapes):
    """Test torch.logical_not with different tensor shapes"""

    def fn(x):
        return torch.logical_not(x)

    # Test with various shapes and numeric values
    a = torch.randint(0, 2, shapes, dtype=torch.int32)

    check_functions_are_equivalent(fn, device, [a])


def test_logical_xor_bool(device: str):
    """Test torch.logical_xor with boolean tensors"""

    def fn(x, y):
        return torch.logical_xor(x, y)

    # Test with boolean tensors - various XOR combinations
    a = torch.tensor([True, False, True, False])
    b = torch.tensor([True, True, False, False])

    check_functions_are_equivalent(fn, device, [a, b])


def test_logical_xor_numeric(device: str):
    """Test torch.logical_xor with numeric tensors"""

    def fn(x, y):
        return torch.logical_xor(x, y)

    # Test with numeric tensors (non-zero treated as True)
    a = torch.tensor([0, 1, 2, -1, 0.0])
    b = torch.tensor([0, 0, 1, -1, 3.0])

    check_functions_are_equivalent(fn, device, [a, b])


def test_logical_xor_mixed_types(device: str):
    """Test torch.logical_xor with mixed boolean and numeric tensors"""

    def fn(x, y):
        return torch.logical_xor(x, y)

    # Test boolean tensor with numeric tensor
    a = torch.tensor([True, False, True, False])
    b = torch.tensor([0, 1, 0, 2])

    check_functions_are_equivalent(fn, device, [a, b])


@pytest.mark.parametrize("shapes", [(3, 4), (2, 3, 4), (5,)])
def test_logical_xor_shapes(device: str, shapes):
    """Test torch.logical_xor with different tensor shapes"""

    def fn(x, y):
        return torch.logical_xor(x, y)

    # Test with various shapes
    a = torch.randint(0, 2, shapes, dtype=torch.int32)
    b = torch.randint(0, 2, shapes, dtype=torch.int32)

    check_functions_are_equivalent(fn, device, [a, b])


def test_logical_xor_edge_cases(device: str):
    """Test torch.logical_xor with edge cases"""

    def fn(x, y):
        return torch.logical_xor(x, y)

    # Test with specific edge case values
    test_cases = [
        # All False XOR All False = All False
        (torch.tensor([False, False, False]), torch.tensor([False, False, False])),
        # All True XOR All False = All True
        (torch.tensor([True, True, True]), torch.tensor([False, False, False])),
        # All True XOR All True = All False
        (torch.tensor([True, True, True]), torch.tensor([True, True, True])),
        # Mixed numeric values
        (torch.tensor([0.0, -1.0, 2.5]), torch.tensor([0.0, 1.0, 0.0])),
    ]

    for a, b in test_cases:
        check_functions_are_equivalent(fn, device, [a, b])


def test_any_basic(device: str):
    """Test torch.any basic functionality"""

    def fn(x):
        return torch.any(x)

    # Test with tensor containing non-zero values (should return True)
    a = torch.tensor([0, 0, 1, 0])
    check_functions_are_equivalent(fn, device, [a])

    # Test with tensor containing all zeros (should return False)
    b = torch.tensor([0, 0, 0, 0])
    check_functions_are_equivalent(fn, device, [b])


@pytest.mark.parametrize("dim", [0, 1, -1])
def test_any_with_dim(device: str, dim: int):
    """Test torch.any with dimension parameter"""

    def fn(x):
        return torch.any(x, dim=dim)

    # Test with 2D tensor
    a = torch.tensor([[1, 0], [0, 0], [0, 1]])

    check_functions_are_equivalent(fn, device, [a])


def test_any_keepdim(device: str):
    """Test torch.any with keepdim parameter"""

    def fn(x):
        return torch.any(x, dim=1, keepdim=True)

    # Test with 2D tensor and keepdim=True
    a = torch.tensor([[1, 0], [0, 0], [0, 1]])

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("shapes", [(3, 4), (2, 3, 4), (5,)])
def test_any_shapes(device: str, shapes):
    """Test torch.any with different tensor shapes"""

    def fn(x):
        return torch.any(x)

    # Test with various shapes and random binary values
    a = torch.randint(0, 2, shapes, dtype=torch.int32)

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize(
    "dtype",
    [torch.int8, torch.int32, torch.int64, torch.float32, torch.float64, torch.bool],
)
def test_any_dtypes(device: str, dtype):
    """Test torch.any with different data types"""

    def fn(x):
        return torch.any(x)

    if dtype == torch.bool:
        # For boolean dtype, create tensor with True/False values
        a = torch.tensor([True, False, False, True], dtype=dtype)
    elif dtype.is_floating_point:
        # For float dtypes, use values including 0.0 and non-zero
        a = torch.tensor([0.0, 1.5, 0.0, -2.3], dtype=dtype)
    else:
        # For integer dtypes, use mix of zero and non-zero values
        a = torch.tensor([0, 1, 0, -2], dtype=dtype)

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("dtype", [torch.int32, torch.float32, torch.bool])
@pytest.mark.parametrize("dim", [0, 1])
def test_any_dtypes_with_dim(device: str, dtype, dim):
    """Test torch.any with different data types and dimensions"""

    def fn(x):
        return torch.any(x, dim=dim)

    if dtype == torch.bool:
        # For boolean dtype
        a = torch.tensor([[True, False], [False, False], [True, True]], dtype=dtype)
    elif dtype == torch.float32:
        # For float dtype
        a = torch.tensor([[1.0, 0.0], [0.0, 0.0], [2.5, -1.5]], dtype=dtype)
    else:
        # For integer dtype
        a = torch.tensor([[1, 0], [0, 0], [2, -1]], dtype=dtype)

    check_functions_are_equivalent(fn, device, [a])


@pytest.mark.parametrize("tensor_shapes", [(2, 3), (1, 5), (4,), (2, 3, 4)])
def test_full_like_basic(device: str, tensor_shapes: tuple):
    """Test torch.full_like with different shapes and fill values"""

    def fn(x):
        return torch.full_like(x, 5.0)

    x = torch.randn(tensor_shapes, device=device)

    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.parametrize("fill_value", [0, 1, -1, 3.14, -2.5])
def test_full_like_different_values(device: str, fill_value):
    """Test torch.full_like with different fill values"""

    def fn(x):
        return torch.full_like(x, fill_value)

    x = torch.randn(3, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.parametrize(
    "dtype", [torch.float32, torch.float64, torch.int32, torch.int64]
)
def test_full_like_dtype(device: str, dtype):
    """Test torch.full_like with different dtype specifications"""

    def fn(x):
        return torch.full_like(x, 7, dtype=dtype)

    x = torch.randn(2, 3, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_full_like_scalar_tensor(device: str):
    """Test torch.full_like with scalar tensor"""

    def fn(x):
        return torch.full_like(x, 42.0)

    x = torch.tensor(1.0, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_full_like_zero_fill(device: str):
    """Test torch.full_like with zero fill value"""

    def fn(x):
        return torch.full_like(x, 0)

    x = torch.randn(2, 5, 3, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_full_like_negative_fill(device: str):
    """Test torch.full_like with negative fill value"""

    def fn(x):
        return torch.full_like(x, -10)

    x = torch.randn(4, 2, device=device)

    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.parametrize("tensor_shapes", [(1, 1), (10,), (2, 2, 2, 2)])
def test_full_like_edge_cases(device: str, tensor_shapes: tuple):
    """Test torch.full_like with edge case shapes"""

    def fn(x):
        return torch.full_like(x, 100)

    x = torch.ones(tensor_shapes, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_scaled_dot_product_attention_basic(device: str):
    """Test basic scaled dot-product attention"""

    def fn(query, key, value):
        return torch.nn.functional.scaled_dot_product_attention(query, key, value)

    batch_size, seq_len, embed_dim = 2, 8, 64
    query = torch.randn(batch_size, seq_len, embed_dim, device=device)
    key = torch.randn(batch_size, seq_len, embed_dim, device=device)
    value = torch.randn(batch_size, seq_len, embed_dim, device=device)

    check_functions_are_equivalent(fn, device, [query, key, value])


def test_scaled_dot_product_attention_with_mask(device: str):
    """Test scaled dot-product attention with attention mask"""

    def fn(query, key, value, attn_mask):
        return torch.nn.functional.scaled_dot_product_attention(
            query, key, value, attn_mask=attn_mask
        )

    batch_size, seq_len, embed_dim = 2, 4, 32
    query = torch.randn(batch_size, seq_len, embed_dim, device=device)
    key = torch.randn(batch_size, seq_len, embed_dim, device=device)
    value = torch.randn(batch_size, seq_len, embed_dim, device=device)

    # Create a simple causal mask (lower triangular)
    attn_mask = torch.tril(torch.ones(seq_len, seq_len, device=device))
    attn_mask = attn_mask.masked_fill(attn_mask == 0, float("-inf"))
    attn_mask = attn_mask.masked_fill(attn_mask == 1, 0.0)

    check_functions_are_equivalent(fn, device, [query, key, value, attn_mask])


def test_scaled_dot_product_attention_different_kv_length(device: str):
    """Test scaled dot-product attention with different key/value sequence length"""

    def fn(query, key, value):
        return torch.nn.functional.scaled_dot_product_attention(query, key, value)

    batch_size, q_len, kv_len, embed_dim = 2, 6, 10, 64
    query = torch.randn(batch_size, q_len, embed_dim, device=device)
    key = torch.randn(batch_size, kv_len, embed_dim, device=device)
    value = torch.randn(batch_size, kv_len, embed_dim, device=device)

    check_functions_are_equivalent(fn, device, [query, key, value])


def test_scaled_dot_product_attention_multihead(device: str):
    """Test scaled dot-product attention with multiple heads"""

    def fn(query, key, value):
        return torch.nn.functional.scaled_dot_product_attention(query, key, value)

    batch_size, num_heads, seq_len, head_dim = 2, 8, 12, 64
    query = torch.randn(batch_size, num_heads, seq_len, head_dim, device=device)
    key = torch.randn(batch_size, num_heads, seq_len, head_dim, device=device)
    value = torch.randn(batch_size, num_heads, seq_len, head_dim, device=device)

    check_functions_are_equivalent(fn, device, [query, key, value])


def test_scaled_dot_product_attention_with_dropout_mask(device: str):
    """Test scaled dot-product attention with dropout mask"""

    def fn(query, key, value):
        # Note: for testing we use dropout_p=0 to ensure deterministic results
        dropout_p = 0.0  # No dropout for deterministic testing
        return torch.nn.functional.scaled_dot_product_attention(
            query, key, value, dropout_p=dropout_p
        )

    batch_size, seq_len, embed_dim = 2, 6, 32
    query = torch.randn(batch_size, seq_len, embed_dim, device=device)
    key = torch.randn(batch_size, seq_len, embed_dim, device=device)
    value = torch.randn(batch_size, seq_len, embed_dim, device=device)

    check_functions_are_equivalent(fn, device, [query, key, value])


def test_scaled_dot_product_attention_small_dimensions(device: str):
    """Test scaled dot-product attention with small dimensions"""

    def fn(query, key, value):
        return torch.nn.functional.scaled_dot_product_attention(query, key, value)

    batch_size, seq_len, embed_dim = 1, 3, 16
    query = torch.randn(batch_size, seq_len, embed_dim, device=device)
    key = torch.randn(batch_size, seq_len, embed_dim, device=device)
    value = torch.randn(batch_size, seq_len, embed_dim, device=device)

    check_functions_are_equivalent(fn, device, [query, key, value])


def test_scaled_dot_product_attention_single_token(device: str):
    """Test scaled dot-product attention with single token sequence"""

    def fn(query, key, value):
        return torch.nn.functional.scaled_dot_product_attention(query, key, value)

    batch_size, seq_len, embed_dim = 2, 1, 32
    query = torch.randn(batch_size, seq_len, embed_dim, device=device)
    key = torch.randn(batch_size, seq_len, embed_dim, device=device)
    value = torch.randn(batch_size, seq_len, embed_dim, device=device)

    check_functions_are_equivalent(fn, device, [query, key, value])


@pytest.mark.parametrize("embed_dim", [32, 64, 128])
def test_scaled_dot_product_attention_different_embed_dims(device: str, embed_dim: int):
    """Test scaled dot-product attention with different embedding dimensions"""

    def fn(query, key, value):
        return torch.nn.functional.scaled_dot_product_attention(query, key, value)

    batch_size, seq_len = 2, 8
    query = torch.randn(batch_size, seq_len, embed_dim, device=device)
    key = torch.randn(batch_size, seq_len, embed_dim, device=device)
    value = torch.randn(batch_size, seq_len, embed_dim, device=device)

    check_functions_are_equivalent(fn, device, [query, key, value])


def test_scaled_dot_product_attention_is_causal(device: str):
    """Test scaled dot-product attention with causal masking"""

    def fn(query, key, value):
        return torch.nn.functional.scaled_dot_product_attention(
            query, key, value, is_causal=True
        )

    batch_size, seq_len, embed_dim = 2, 6, 32
    query = torch.randn(batch_size, seq_len, embed_dim, device=device)
    key = torch.randn(batch_size, seq_len, embed_dim, device=device)
    value = torch.randn(batch_size, seq_len, embed_dim, device=device)

    check_functions_are_equivalent(fn, device, [query, key, value])


def test_scaled_dot_product_attention_cross_attention(device: str):
    """Test scaled dot-product attention for cross-attention (encoder-decoder)"""

    def fn(query, key, value):
        return torch.nn.functional.scaled_dot_product_attention(query, key, value)

    batch_size = 2
    tgt_len, src_len = 8, 12  # Different lengths for cross-attention
    embed_dim = 64

    query = torch.randn(batch_size, tgt_len, embed_dim, device=device)  # From decoder
    key = torch.randn(batch_size, src_len, embed_dim, device=device)  # From encoder
    value = torch.randn(batch_size, src_len, embed_dim, device=device)  # From encoder

    check_functions_are_equivalent(fn, device, [query, key, value])


def test_scaled_dot_product_attention_with_scale(device: str):
    """Test scaled dot-product attention with custom scale"""

    def fn(query, key, value):
        custom_scale = 0.125  # Custom scale instead of 1/sqrt(embed_dim)
        return torch.nn.functional.scaled_dot_product_attention(
            query, key, value, scale=custom_scale
        )

    batch_size, seq_len, embed_dim = 2, 4, 32
    query = torch.randn(batch_size, seq_len, embed_dim, device=device)
    key = torch.randn(batch_size, seq_len, embed_dim, device=device)
    value = torch.randn(batch_size, seq_len, embed_dim, device=device)

    check_functions_are_equivalent(fn, device, [query, key, value])


@pytest.mark.parametrize("dims", [(0, 1), (1, 0)])
def test_permute_2d(device: str, dims: tuple):
    """Test torch.permute with 2D tensors"""

    def fn(x):
        return x.permute(dims)

    x = torch.randn(3, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.parametrize(
    "dims", [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
)
def test_permute_3d(device: str, dims: tuple):
    """Test torch.permute with 3D tensors - all permutations"""

    def fn(x):
        return x.permute(dims)

    x = torch.randn(2, 3, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_permute_4d_nchw_to_nhwc(device: str):
    """Test common permutation: NCHW to NHWC format conversion"""

    def fn(x):
        # Convert from [N, C, H, W] to [N, H, W, C]
        return x.permute(0, 2, 3, 1)

    x = torch.randn(2, 3, 8, 8, device=device)  # Batch=2, Channels=3, Height=8, Width=8

    check_functions_are_equivalent(fn, device, [x])


def test_permute_4d_nhwc_to_nchw(device: str):
    """Test common permutation: NHWC to NCHW format conversion"""

    def fn(x):
        # Convert from [N, H, W, C] to [N, C, H, W]
        return x.permute(0, 3, 1, 2)

    x = torch.randn(2, 8, 8, 3, device=device)  # Batch=2, Height=8, Width=8, Channels=3

    check_functions_are_equivalent(fn, device, [x])


def test_permute_with_negative_indices(device: str):
    """Test torch.permute with negative dimension indices"""

    def fn(x):
        # Equivalent to (0, 2, 1) for 3D tensor
        return x.permute(0, -1, -2)

    x = torch.randn(2, 3, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_permute_identity(device: str):
    """Test permute with identity permutation (no change)"""

    def fn(x):
        return x.permute(0, 1, 2)

    x = torch.randn(2, 3, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_permute_reverse_order(device: str):
    """Test permute that reverses all dimensions"""

    def fn(x):
        return x.permute(2, 1, 0)

    x = torch.randn(2, 3, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.parametrize("tensor_shapes", [(5,), (1, 10), (2, 3, 4), (1, 2, 3, 4, 5)])
def test_permute_different_shapes(device: str, tensor_shapes: tuple):
    """Test permute with various tensor shapes"""

    def fn(x):
        # Create a permutation that reverses the dimensions
        dims = tuple(range(len(x.shape) - 1, -1, -1))
        return x.permute(dims)

    x = torch.randn(tensor_shapes, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_permute_with_arithmetic(device: str):
    """Test permute combined with arithmetic operations"""

    def fn(x, y):
        x_permuted = x.permute(1, 0, 2)
        y_permuted = y.permute(1, 0, 2)
        return x_permuted + y_permuted

    x = torch.randn(2, 3, 4, device=device)
    y = torch.randn(2, 3, 4, device=device)

    check_functions_are_equivalent(fn, device, [x, y])


def test_permute_chain(device: str):
    """Test chaining multiple permute operations"""

    def fn(x):
        # Apply permute twice
        step1 = x.permute(2, 1, 0)  # Reverse all dims
        step2 = step1.permute(2, 1, 0)  # Reverse again (should be back to original)
        return step2

    x = torch.randn(2, 3, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_permute_transpose_equivalent(device: str):
    """Test that permute(1, 0) is equivalent to transpose for 2D tensors"""

    def fn(x):
        return x.permute(1, 0)

    x = torch.randn(3, 4, device=device)

    # This should be equivalent to x.t() or x.transpose(0, 1)
    check_functions_are_equivalent(fn, device, [x])


def test_permute_1d_identity(device: str):
    """Test permute with 1D tensor (identity operation)"""

    def fn(x):
        # 1D tensors can only be permuted with (0,)
        return x.permute(0)

    x = torch.randn(5, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_movedim_basic(device: str):
    """Test basic movedim operation - move single dimension"""

    def fn(x):
        return torch.movedim(x, 0, 2)

    x = torch.randn(3, 4, 5)
    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.parametrize(
    "source,destination", [(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)]
)
def test_movedim_different_positions(device: str, source: int, destination: int):
    """Test movedim with different source and destination positions"""

    def fn(x):
        return torch.movedim(x, source, destination)

    x = torch.randn(3, 4, 5)
    check_functions_are_equivalent(fn, device, [x])


def test_movedim_negative_indices(device: str):
    """Test movedim with negative indices"""

    def fn(x):
        return torch.movedim(x, -1, 0)

    x = torch.randn(3, 4, 5)
    check_functions_are_equivalent(fn, device, [x])


def test_movedim_multiple_dims(device: str):
    """Test movedim with multiple dimensions"""

    def fn(x):
        return torch.movedim(x, [0, 1], [2, 0])

    x = torch.randn(3, 4, 5)
    check_functions_are_equivalent(fn, device, [x])


def test_movedim_4d_tensor(device: str):
    """Test movedim on 4D tensor (common in computer vision)"""

    def fn(x):
        # Move channels from dim 1 to dim 3 (NCHW to NHWC)
        return torch.movedim(x, 1, 3)

    x = torch.randn(2, 3, 4, 5)  # N, C, H, W
    check_functions_are_equivalent(fn, device, [x])


def test_movedim_identity(device: str):
    """Test movedim identity operation"""

    def fn(x):
        return torch.movedim(x, 1, 1)

    x = torch.randn(3, 4, 5)
    check_functions_are_equivalent(fn, device, [x])


def test_movedim_2d_tensor(device: str):
    """Test movedim on 2D tensor"""

    def fn(x):
        return torch.movedim(x, 0, 1)

    x = torch.randn(3, 4)
    check_functions_are_equivalent(fn, device, [x])


# TODO: support list as input too
def test_aten_index_select_basic(device: str):
    """Test basic torch.index_select operation"""

    def fn(x, indices):
        return x[indices]

    x = torch.randn(5, 3, device=device)
    idx = torch.tensor([1, 2, 3], device=device, dtype=torch.int32)

    check_functions_are_equivalent(fn, device, [x, idx])


def test_aten_index_select_second_dim(device: str):
    """Test basic torch.index_select operation"""

    def fn(x, indices):
        return x[:, indices]

    x = torch.randn(5, 10, device=device)
    idx = torch.tensor([1, 2, 3], device=device, dtype=torch.int32)

    check_functions_are_equivalent(fn, device, [x, idx])


@pytest.mark.parametrize("dtype", [torch.int32, torch.int64])
def test_aten_index_select_multiple_dtypes(device: str, dtype):
    """Test basic torch.index_select operation"""

    def fn(x, indices):
        return x[:, indices]

    x = torch.randn(5, 10, device=device)
    idx = torch.tensor([1, 2, 3], device=device, dtype=dtype)

    check_functions_are_equivalent(fn, device, [x, idx])


def test_aten_index_select_multiple_dims(device: str):
    """Test basic torch.index_select operation"""

    def fn(x, indices1, indices2):
        return x[indices1, indices2, indices2]

    x = torch.randn(4, 5, 6, 7, 8, device=device)
    idx1 = torch.tensor([1, 2, 3], device=device, dtype=torch.int32)
    idx2 = torch.tensor([0, 2, 4], device=device, dtype=torch.int32)

    check_functions_are_equivalent(fn, device, [x, idx1, idx2])


def test_aten_index_select_multiple_dims_start_nonzero(device: str):
    """Test basic torch.index_select operation"""

    def fn(x, indices1, indices2):
        return x[:, indices1, indices2, indices2]

    x = torch.randn(4, 5, 6, 7, 8, device=device)
    idx1 = torch.tensor([1, 2, 3], device=device, dtype=torch.int32)
    idx2 = torch.tensor([0, 2, 4], device=device, dtype=torch.int32)

    check_functions_are_equivalent(fn, device, [x, idx1, idx2])


def test_nonzero_function(device: str):
    """Test torch.nonzero() function"""

    def fn(x):
        return torch.nonzero(x)

    # Test with a simple tensor that has some zeros
    x = torch.tensor(
        [[1, 0, 2], [0, 3, 0], [4, 0, 5]], device=device, dtype=torch.float32
    )

    check_functions_are_equivalent(fn, device, [x])


def test_nonzero_all_zeros(device: str):
    """Test torch.nonzero() with all zeros"""

    def fn(x):
        return torch.nonzero(x)

    x = torch.zeros(3, 3, device=device, dtype=torch.float32)

    check_functions_are_equivalent(fn, device, [x])


def test_nonzero_all_nonzeros(device: str):
    """Test torch.nonzero() with all non-zero values"""

    def fn(x):
        return torch.nonzero(x)

    x = torch.ones(2, 3, device=device, dtype=torch.float32)

    check_functions_are_equivalent(fn, device, [x])


def test_tensor_nonzero_method(device: str):
    """Test tensor.nonzero() method"""

    def fn(x):
        return x.nonzero()

    x = torch.tensor([1, 0, 3, 0, 5], device=device, dtype=torch.float32)

    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.parametrize("tensor_shapes", [(2,), (3, 4), (2, 3, 4)])
def test_nonzero_different_shapes(device: str, tensor_shapes: tuple):
    """Test nonzero with different tensor shapes"""

    def fn(x):
        return torch.nonzero(x)

    # Create a tensor with some zeros and non-zeros
    x = torch.randn(*tensor_shapes, device=device)
    # Set some elements to zero
    if len(tensor_shapes) == 1:
        x[0] = 0
    elif len(tensor_shapes) == 2:
        x[0, 0] = 0
        x[1, 1] = 0
    else:
        x[0, 0, 0] = 0
        x[1, 1, 1] = 0

    check_functions_are_equivalent(fn, device, [x])


def test_interpolate_nearest_upsampling_2d(device: str):
    """Test F.interpolate with nearest upsampling for 2D tensors"""

    def fn(x):
        return torch.nn.functional.interpolate(x, scale_factor=2, mode="nearest")

    # Input shape: [batch, channels, height, width]
    x = torch.randn(2, 3, 4, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_interpolate_bilinear_upsampling_2d(device: str):
    """Test F.interpolate with bilinear upsampling for 2D tensors"""

    def fn(x):
        return torch.nn.functional.interpolate(
            x, scale_factor=2, mode="bilinear", align_corners=False
        )

    # Input shape: [batch, channels, height, width]
    x = torch.randn(2, 3, 4, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_interpolate_nearest_downsampling_2d(device: str):
    """Test F.interpolate with nearest downsampling for 2D tensors"""

    def fn(x):
        return torch.nn.functional.interpolate(x, scale_factor=0.5, mode="nearest")

    # Input shape: [batch, channels, height, width]
    x = torch.randn(2, 3, 8, 8, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_interpolate_with_size_2d(device: str):
    """Test F.interpolate with explicit output size for 2D tensors"""

    def fn(x):
        return torch.nn.functional.interpolate(x, size=(16, 16), mode="nearest")

    # Input shape: [batch, channels, height, width]
    x = torch.randn(2, 3, 8, 8, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_interpolate_bilinear_with_size_2d(device: str):
    """Test F.interpolate with bilinear and explicit output size"""

    def fn(x):
        return torch.nn.functional.interpolate(
            x, size=(12, 12), mode="bilinear", align_corners=False
        )

    # Input shape: [batch, channels, height, width]
    x = torch.randn(2, 3, 6, 6, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_interpolate_linear_1d(device: str):
    """Test F.interpolate with linear interpolation for 1D tensors"""

    def fn(x):
        return torch.nn.functional.interpolate(
            x, scale_factor=2, mode="linear", align_corners=False
        )

    # Input shape: [batch, channels, length]
    x = torch.randn(2, 3, 8, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_interpolate_nearest_3d(device: str):
    """Test F.interpolate with nearest interpolation for 3D tensors"""

    def fn(x):
        return torch.nn.functional.interpolate(x, scale_factor=2, mode="nearest")

    # Input shape: [batch, channels, depth, height, width]
    x = torch.randn(1, 2, 4, 4, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_interpolate_trilinear_3d(device: str):
    """Test F.interpolate with trilinear interpolation for 3D tensors"""

    def fn(x):
        return torch.nn.functional.interpolate(
            x, scale_factor=1.5, mode="trilinear", align_corners=False
        )

    # Input shape: [batch, channels, depth, height, width]
    x = torch.randn(1, 2, 4, 4, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.parametrize("scale_factor", [0.5, 1.5, 2.0, 3.0])
def test_interpolate_different_scale_factors(device: str, scale_factor: float):
    """Test F.interpolate with various scale factors"""

    def fn(x):
        return torch.nn.functional.interpolate(
            x, scale_factor=scale_factor, mode="nearest"
        )

    # Input shape: [batch, channels, height, width]
    x = torch.randn(1, 2, 8, 8, device=device)

    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.parametrize("mode", ["nearest", "bilinear"])
def test_interpolate_different_modes_2d(device: str, mode: str):
    """Test F.interpolate with different interpolation modes for 2D"""

    def fn(x):
        if mode == "bilinear":
            return torch.nn.functional.interpolate(
                x, scale_factor=2, mode=mode, align_corners=False
            )
        else:
            return torch.nn.functional.interpolate(x, scale_factor=2, mode=mode)

    # Input shape: [batch, channels, height, width]
    x = torch.randn(2, 3, 4, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_interpolate_align_corners_true(device: str):
    """Test F.interpolate with align_corners=True"""

    def fn(x):
        return torch.nn.functional.interpolate(
            x, scale_factor=2, mode="bilinear", align_corners=True
        )

    # Input shape: [batch, channels, height, width]
    x = torch.randn(2, 3, 4, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_interpolate_small_tensor(device: str):
    """Test F.interpolate with small tensor dimensions"""

    def fn(x):
        return torch.nn.functional.interpolate(x, size=(8, 8), mode="nearest")

    # Input shape: [batch, channels, height, width]
    x = torch.randn(1, 1, 2, 2, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_interpolate_single_channel(device: str):
    """Test F.interpolate with single channel input"""

    def fn(x):
        return torch.nn.functional.interpolate(x, scale_factor=3, mode="nearest")

    # Input shape: [batch, channels, height, width]
    x = torch.randn(1, 1, 4, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_interpolate_asymmetric_scaling(device: str):
    """Test F.interpolate with different scaling factors for different dimensions"""

    def fn(x):
        return torch.nn.functional.interpolate(x, size=(6, 12), mode="nearest")

    # Input shape: [batch, channels, height, width]
    x = torch.randn(2, 3, 3, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_interpolate_large_upsampling(device: str):
    """Test F.interpolate with large upsampling factor"""

    def fn(x):
        return torch.nn.functional.interpolate(x, scale_factor=4, mode="nearest")

    # Input shape: [batch, channels, height, width]
    x = torch.randn(1, 2, 3, 3, device=device)

    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.parametrize("size", [(5, 5), (7, 9), (16, 16)])
def test_interpolate_various_output_sizes(device: str, size: tuple):
    """Test F.interpolate with various output sizes"""

    def fn(x):
        return torch.nn.functional.interpolate(x, size=size, mode="nearest")

    # Input shape: [batch, channels, height, width]
    x = torch.randn(1, 2, 4, 4, device=device)

    check_functions_are_equivalent(fn, device, [x])


def test_interpolate_preserve_aspect_ratio(device: str):
    """Test F.interpolate preserving aspect ratio with rectangular input"""

    def fn(x):
        return torch.nn.functional.interpolate(
            x, size=(8, 16), mode="bilinear", align_corners=False
        )

    # Input shape: [batch, channels, height, width] - rectangular
    x = torch.randn(2, 3, 4, 8, device=device)

    check_functions_are_equivalent(fn, device, [x])


@pytest.mark.parametrize("dtype", [torch.float32, torch.float64])
def test_native_batch_norm_legit_no_training_basic(device: str, dtype: torch.dtype):
    """Test basic batch normalization inference with different dtypes"""

    def fn(input_tensor, weight, bias, running_mean, running_var):
        return aten._native_batch_norm_legit_no_training.default(
            input_tensor, weight, bias, running_mean, running_var, 0.1, 1e-5
        )

    # Create test tensors
    batch_size, channels, height, width = 2, 3, 4, 4
    input_tensor = torch.randn(
        batch_size, channels, height, width, dtype=dtype, device=device
    )
    weight = torch.randn(channels, dtype=dtype, device=device)
    bias = torch.randn(channels, dtype=dtype, device=device)
    running_mean = torch.randn(channels, dtype=dtype, device=device)
    running_var = torch.abs(torch.randn(channels, dtype=dtype, device=device)) + 1e-5

    check_functions_are_equivalent(
        fn, device, [input_tensor, weight, bias, running_mean, running_var]
    )


@pytest.mark.parametrize("channels", [1, 4, 16])
def test_native_batch_norm_legit_no_training_different_channels(
    device: str, channels: int
):
    """Test batch norm with different numbers of channels"""

    def fn(input_tensor, weight, bias, running_mean, running_var):
        return aten._native_batch_norm_legit_no_training.default(
            input_tensor, weight, bias, running_mean, running_var, 0.1, 1e-5
        )

    # Create test tensors with varying channel dimensions
    batch_size, height, width = 2, 8, 8
    input_tensor = torch.randn(batch_size, channels, height, width, device=device)
    weight = torch.randn(channels, device=device)
    bias = torch.randn(channels, device=device)
    running_mean = torch.randn(channels, device=device)
    running_var = torch.abs(torch.randn(channels, device=device)) + 1e-5

    # Test that compilation works and outputs match
    check_functions_are_equivalent(
        fn, device, [input_tensor, weight, bias, running_mean, running_var]
    )


def test_native_batch_norm_legit_no_training_none_weight_bias(device: str):
    """Test batch norm with None weight and bias"""

    def fn(input_tensor, running_mean, running_var):
        return aten._native_batch_norm_legit_no_training.default(
            input_tensor, None, None, running_mean, running_var, 0.1, 1e-5
        )

    # Create test tensors
    batch_size, channels, height, width = 2, 3, 4, 4
    input_tensor = torch.randn(batch_size, channels, height, width, device=device)
    running_mean = torch.randn(channels, device=device)
    running_var = torch.abs(torch.randn(channels, device=device)) + 1e-5

    # Test that compilation works and outputs match
    check_functions_are_equivalent(
        fn, device, [input_tensor, running_mean, running_var]
    )


@pytest.mark.parametrize("eps", [1e-5, 1e-3])
def test_native_batch_norm_legit_no_training_different_eps(device: str, eps: float):
    """Test batch norm with different epsilon values"""

    def fn(input_tensor, weight, bias, running_mean, running_var):
        return aten._native_batch_norm_legit_no_training.default(
            input_tensor, weight, bias, running_mean, running_var, 0.1, eps
        )

    # Create test tensors
    batch_size, channels, height, width = 2, 3, 4, 4
    input_tensor = torch.randn(batch_size, channels, height, width, device=device)
    weight = torch.randn(channels, device=device)
    bias = torch.randn(channels, device=device)
    running_mean = torch.randn(channels, device=device)
    running_var = torch.abs(torch.randn(channels, device=device)) + eps * 10

    # Test that compilation works and outputs match
    check_functions_are_equivalent(
        fn, device, [input_tensor, weight, bias, running_mean, running_var]
    )


def test_native_batch_norm_legit_no_training_2d_input(device: str):
    """Test batch norm with 2D input (N, C)"""

    def fn(input_tensor, weight, bias, running_mean, running_var):
        return aten._native_batch_norm_legit_no_training.default(
            input_tensor, weight, bias, running_mean, running_var, 0.1, 1e-5
        )

    # Create 2D test tensors (batch_size, channels)
    batch_size, channels = 10, 5
    input_tensor = torch.randn(batch_size, channels, device=device)
    weight = torch.randn(channels, device=device)
    bias = torch.randn(channels, device=device)
    running_mean = torch.randn(channels, device=device)
    running_var = torch.abs(torch.randn(channels, device=device)) + 1e-5

    # Test that compilation works and outputs match
    check_functions_are_equivalent(
        fn, device, [input_tensor, weight, bias, running_mean, running_var]
    )
