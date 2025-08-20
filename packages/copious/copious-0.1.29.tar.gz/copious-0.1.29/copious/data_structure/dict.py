from collections import defaultdict


def defaultdict2dict(input_dict: defaultdict) -> dict:
    """
    Recursively convert a defaultdict to a normal dict.

    Args:
        input_dict (defaultdict): The defaultdict to convert.

    Returns:
        dict: A normal dict with the same structure and values as the input defaultdict.
    """
    result = {}
    for key, value in input_dict.items():
        if isinstance(value, defaultdict):
            result[key] = defaultdict2dict(value)
        elif isinstance(value, (list, tuple)):
            result[key] = type(value)(defaultdict2dict(item) if isinstance(item, defaultdict) else item for item in value)
        else:
            result[key] = value
    return result

