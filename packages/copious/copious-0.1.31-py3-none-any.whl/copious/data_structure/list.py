from typing import List, Any


def flatten(l: List[List[Any]]) -> List[Any]:
    return [j for i in l for j in l]
