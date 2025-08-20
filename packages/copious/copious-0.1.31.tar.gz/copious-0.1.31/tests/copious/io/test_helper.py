import pytest
import numpy as np
from copious.io.helper import is_numpy_array, is_torch_tensor, default_if_none_or_empty

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class TestIsNumpyArray:
    def test_numpy_array_returns_true(self):
        arr = np.array([1, 2, 3])
        assert is_numpy_array(arr) is True

    def test_numpy_empty_array_returns_true(self):
        arr = np.array([])
        assert is_numpy_array(arr) is True

    def test_numpy_multidimensional_array_returns_true(self):
        arr = np.array([[1, 2], [3, 4]])
        assert is_numpy_array(arr) is True

    def test_list_returns_false(self):
        arr = [1, 2, 3]
        assert is_numpy_array(arr) is False

    def test_tuple_returns_false(self):
        arr = (1, 2, 3)
        assert is_numpy_array(arr) is False

    def test_string_returns_false(self):
        arr = "hello"
        assert is_numpy_array(arr) is False

    def test_none_returns_false(self):
        assert is_numpy_array(None) is False

    @pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not available")
    def test_torch_tensor_returns_false(self):
        tensor = torch.tensor([1, 2, 3])
        assert is_numpy_array(tensor) is False


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not available")
class TestIsTorchTensor:
    def test_torch_tensor_returns_true(self):
        tensor = torch.tensor([1, 2, 3])
        assert is_torch_tensor(tensor) is True

    def test_torch_empty_tensor_returns_true(self):
        tensor = torch.tensor([])
        assert is_torch_tensor(tensor) is True

    def test_torch_multidimensional_tensor_returns_true(self):
        tensor = torch.tensor([[1, 2], [3, 4]])
        assert is_torch_tensor(tensor) is True

    def test_torch_cuda_tensor_returns_true(self):
        if torch.cuda.is_available():
            tensor = torch.tensor([1, 2, 3]).cuda()
            assert is_torch_tensor(tensor) is True

    def test_list_returns_false(self):
        arr = [1, 2, 3]
        assert is_torch_tensor(arr) is False

    def test_numpy_array_returns_false(self):
        arr = np.array([1, 2, 3])
        assert is_torch_tensor(arr) is False

    def test_string_returns_false(self):
        arr = "hello"
        assert is_torch_tensor(arr) is False

    def test_none_returns_false(self):
        assert is_torch_tensor(None) is False


class TestDefaultIfNoneOrEmpty:
    def test_none_returns_default(self):
        result = default_if_none_or_empty(None, "default")
        assert result == "default"

    def test_non_none_value_returns_value(self):
        result = default_if_none_or_empty("value", "default")
        assert result == "value"

    def test_empty_string_returns_default(self):
        result = default_if_none_or_empty("", "default")
        assert result == "default"

    def test_empty_list_returns_default(self):
        result = default_if_none_or_empty([], "default")
        assert result == "default"

    def test_non_empty_list_returns_value(self):
        value = [1, 2, 3]
        result = default_if_none_or_empty(value, "default")
        assert result == value

    def test_zero_returns_default(self):
        result = default_if_none_or_empty(0, "default")
        assert result == "default"

    def test_false_returns_default(self):
        result = default_if_none_or_empty(False, "default")
        assert result == "default"

    def test_non_empty_string_returns_value(self):
        result = default_if_none_or_empty("hello", "default")
        assert result == "hello"

    def test_numpy_empty_array_returns_default(self):
        arr = np.array([])
        result = default_if_none_or_empty(arr, "default")
        assert result == "default"

    def test_numpy_non_empty_array_returns_value(self):
        arr = np.array([1, 2, 3])
        result = default_if_none_or_empty(arr, "default")
        assert np.array_equal(result, arr)

    @pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not available")
    def test_torch_empty_tensor_returns_default(self):
        tensor = torch.tensor([])
        result = default_if_none_or_empty(tensor, "default")
        assert result == "default"

    @pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not available")
    def test_torch_non_empty_tensor_returns_value(self):
        tensor = torch.tensor([1, 2, 3])
        result = default_if_none_or_empty(tensor, "default")
        assert torch.equal(result, tensor)

    def test_numpy_multidimensional_empty_array_returns_default(self):
        arr = np.array([]).reshape(0, 3)
        result = default_if_none_or_empty(arr, "default")
        assert result == "default"

    @pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not available")
    def test_torch_multidimensional_empty_tensor_returns_default(self):
        tensor = torch.tensor([]).reshape(0, 3)
        result = default_if_none_or_empty(tensor, "default")
        assert result == "default"