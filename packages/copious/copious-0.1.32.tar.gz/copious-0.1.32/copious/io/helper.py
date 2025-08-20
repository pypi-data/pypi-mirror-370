def is_numpy_array(value):
    return type(value).__name__ == 'ndarray' and type(value).__module__ == 'numpy'


def is_torch_tensor(value):
    return type(value).__name__ == 'Tensor' and type(value).__module__.startswith('torch')


def default_if_none_or_empty(value, default):
    if value is None:
        return default

    if is_numpy_array(value) or is_torch_tensor(value):
        return value if value.size > 0 else default

    return value or default
