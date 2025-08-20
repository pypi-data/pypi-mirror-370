import pytest
import numpy as np
import json

from copious.io.fs import read_yaml, mktmpdir, NumpyEncoder

def test_read_yaml_compatible_with_pathlib_path():
    tmp_dir = mktmpdir()
    with open(tmp_dir / "test.yaml", "w") as f:
        f.write("a: 1\nb: 2")
    test_yaml = tmp_dir / "test.yaml"
    assert read_yaml(test_yaml) == {"a": 1, "b": 2}

def test_numpy_integers():
    arr = np.array([1, 2, 3], dtype=np.int32)
    result = json.dumps(arr, cls=NumpyEncoder)
    assert result == json.dumps([1, 2, 3])

def test_numpy_floats():
    arr = np.array([1.1, 2.2, 3.3], dtype=np.float64)
    result = json.dumps(arr, cls=NumpyEncoder)
    assert result == json.dumps([1.1, 2.2, 3.3])

def test_numpy_scalars():
    scalar = np.int64(5)
    result = json.dumps(scalar, cls=NumpyEncoder)
    assert result == json.dumps(5)

def test_numpy_2d_arrays():
    arr = np.array([[1, 2], [3, 4]], dtype=np.int64)
    result = json.dumps(arr, cls=NumpyEncoder)
    assert result == json.dumps([[1, 2], [3, 4]])

def test_numpy_complex_numbers():
    arr = np.array([1+2j, 3+4j])
    with pytest.raises(TypeError):  # Complex numbers are not serializable to JSON
        json.dumps(arr, cls=NumpyEncoder)

def test_numpy_bools():
    arr = np.array([True, False])
    result = json.dumps(arr, cls=NumpyEncoder)
    assert result == json.dumps([True, False])

def test_numpy_empty_array():
    arr = np.array([], dtype=np.int32)
    result = json.dumps(arr, cls=NumpyEncoder)
    assert result == '[]'

# Additional test case for mixed data types
def test_numpy_mixed_types():
    arr = np.array([1, 2.5, True], dtype=object)
    result = json.dumps(arr, cls=NumpyEncoder)
    assert result == json.dumps([1, 2.5, True])