import itertools
from typing import List, Tuple, Union


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return '#' + ''.join(f'{c:02x}' for c in rgb)

def get_colors(cmap_name: str = "rainbow", n_desired_colors: int = 5, representation: str = "rgb") -> List[Union[Tuple[int, int, int], str]]:
    import matplotlib.pyplot as plt
    import numpy as np

    cmap = plt.cm.get_cmap(cmap_name, n_desired_colors)
    try:
        colors = cmap.colors
    except AttributeError:
        colors = cmap(np.linspace(0, 1, n_desired_colors))
    colors = (colors[:, :3] * 255).astype(np.int32)
    if representation == "hex":
        colors = [rgb_to_hex(tuple(color)) for color in colors]
    elif representation == "rgb":
        colors = colors.tolist()
    else:
        raise ValueError(f"Unsupported representation: {representation}")
    return colors

def color_generator(cmap_name: str = "rainbow", n_desired_colors: int = 5, cyclic: bool = True, representation: str = "rgb"):
    colors = get_colors(cmap_name=cmap_name, n_desired_colors=n_desired_colors, representation=representation)
    if cyclic:
        colors = itertools.cycle(colors)
    for color in colors:
        yield color


__all__ = ["rgb_to_hex", "get_colors", "color_generator"]
