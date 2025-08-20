from pathlib import Path
import pickle
import functools
import tempfile
import json
import yaml
from typing import List, Dict, Union, Any

import numpy as np


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        # Handle integer types
        int_types = [np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, 
                     np.uint8, np.uint16, np.uint32, np.uint64]
        # Add np.int_ if it exists (NumPy < 2.0 compatibility)
        if hasattr(np, 'int_'):
            int_types.append(np.int_)
        
        # Handle float types  
        float_types = [np.float16, np.float32, np.float64]
        # Add np.float_ if it exists (NumPy < 2.0 compatibility)
        if hasattr(np, 'float_'):
            float_types.append(np.float_)
            
        if isinstance(obj, tuple(int_types)):
            return int(obj)
        elif isinstance(obj, tuple(float_types)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def read_json(path: Path) -> Union[Dict, List[Dict]]:
    with open(path) as f:
        j = json.load(f)
    return j


def write_json(json_data: Union[Dict, List[Dict]], path: Path, prettify: bool = True, use_numpy_decoder: bool = False) -> None:
    with open(path, "w") as f:
        kwargs = {}
        if prettify:
            kwargs.update(indent=4)
        if use_numpy_decoder:
            kwargs.update(cls=NumpyEncoder)
        json.dump(json_data, f, **kwargs)


def read_yaml(path: Union[str, Path]) -> Union[Dict, List[Dict]]:
    with open(path) as f:
        y = yaml.safe_load(f)
    return y


def write_yaml(data: Union[Dict, List[Dict]], path: Path) -> None:
    with open(path, "w") as f:
        yaml.dump(data, f)


def read_pickle(path: Path) -> None:
    with open(path, "rb") as f:
        return pickle.load(f)


def write_pickle(data: Any, path: Path) -> None:
    with open(path, "wb") as f:
        pickle.dump(data, f)


def create_empty_temp_file(prefix=None, suffix=None) -> Path:
    _, path = tempfile.mkstemp(prefix=prefix, suffix=suffix, text=True)
    return Path(path)


def mktmpdir():
    tmp_dir = Path(tempfile.mktemp())
    tmp_dir.mkdir()
    return tmp_dir


def create_test_files(root_dir, files):
    root_dir = Path(root_dir)
    _paths = [root_dir / f for f in files]
    for p in _paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch()


def ensured_path(input, ensure_parent=False):
    """Often used in the scenario that the path we want to write things to is ensured to be exist."""
    p = Path(input)
    if ensure_parent:
        p.parent.mkdir(parents=True, exist_ok=True)
    else:
        p.mkdir(parents=True, exist_ok=True)
    return p


parent_ensured_path = functools.partial(ensured_path, ensure_parent=True)

__all__ = [
    "read_json",
    "write_json",
    "create_empty_temp_file",
    "mktmpdir",
    "create_test_files",
    "ensured_path",
    "parent_ensured_path",
]
