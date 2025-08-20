"""# Cubehelix color palette

Reference:
    Green, D. A. (2011). A colour scheme for the display of astronomical intensity images.
    Bull. Astr. Soc. India. Retrieved from
    [http://www.astro.caltech.edu/](http://www.astro.caltech.edu/).
"""

from typing import List, Optional

from ragraph.colors import utils

try:
    import numpy as np

    HAVE_NUMPY = True
except ImportError:
    HAVE_NUMPY = False


def cubehelix_palette(
    n_colors: int,
    start: float = 2.25,
    end: float = 3.45,
    dark: float = 0.2,
    light: float = 0.85,
    gamma: float = 1.0,
    saturation: float = 1.2,
    rotations: Optional[float] = None,
    categorical: bool = False,
) -> List[str]:
    """Calculate a cubehelix color palette as a list of hex codes.

    Arguments:
        n_colors: Number of RGB colour pairs to generate.
        start: Starting color (Red: 1.0, Green: 2.0, Blue: 3.0).
        end: Final color (Red: 1.0, Green: 2.0, Blue: 3.0).
        dark: Lightness of the darkest value [0.0 - 1.0].
        light: Lightness of the lightest value [0.0 - 1.0].
        gamma: Exponential factor applied to lightness to emphasize low intensity values (< 1.0) or
            high intensity values (> 1.0).
        rotations: Number of RGB rotations (1.0 means a full RGB rotation). Overrides `end`.
            Otherwise calculated as `(end - start) / 3`.
        categorical: Whether to shuffle the rotational space optimally for categorical color
            palettes. Similar colors are positioned as far apart as possible.

    Returns:
        Color palette as a list of hex codes.

    Reference:
        Green, D. A. (2011). A colour scheme for the display of astronomical intensity images. Bull.
        Astr. Soc. India. Retrieved from http://www.astro.caltech.edu/
    """
    if HAVE_NUMPY:
        method = _cubehelix_numpy
    else:
        method = _cubehelix_pure_python

    n_colors = max(n_colors, 1)

    rgb1s = method(
        n_colors,
        start=start,
        end=end,
        dark=dark,
        light=light,
        gamma=gamma,
        saturation=saturation,
        rotations=rotations,
        categorical=categorical,
    )

    hexes = [utils.rgb_to_hex(*utils.rgb1_to_rgb(*c)) for c in rgb1s]

    return hexes


def _cubehelix_numpy(
    n_colors: int,
    start: float = 2.25,
    end: float = 3.45,
    dark: float = 0.2,
    light: float = 0.85,
    gamma: float = 1.0,
    saturation: float = 1.2,
    rotations: Optional[float] = None,
    categorical: bool = False,
) -> List[List[float]]:
    """See [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette]."""
    n_colors = max(n_colors, 1)

    if rotations is None:
        rotations = (end - start) / 3

    start = start / 3

    light_space = np.linspace(light, dark, n_colors, endpoint=True) ** gamma
    a_space = saturation / 2 * light_space * (1 - light_space)

    phi_space = 2 * np.pi * np.linspace(start, start + rotations, n_colors)
    if categorical:
        phi_space = np.array(_shuffle(phi_space, n_colors // 3))
    cos_space = np.cos(phi_space)
    sin_space = np.sin(phi_space)

    rot_mat = np.vstack((cos_space, sin_space))

    # Constants from paper.
    col_mat = np.array([[-0.14861, 1.78277], [-0.29227, -0.90649], [1.97294, 0.0]])

    colors = light_space + a_space * (col_mat @ rot_mat)
    colors[colors > 1.0] = 1.0
    colors[colors < 0.0] = 0.0

    return colors.T.tolist()


def _cubehelix_pure_python(
    n_colors: int,
    start: float = 2.25,
    end: float = 3.45,
    dark: float = 0.2,
    light: float = 0.85,
    gamma: float = 1.0,
    saturation: float = 1.2,
    rotations: Optional[float] = None,
    categorical: bool = False,
) -> List[List[float]]:
    """See [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette]."""
    import math

    if rotations is None:
        rotations = (end - start) / 3

    start = start / 3

    light_space = [math.pow(x, gamma) for x in _linspace(light, dark, n_colors)]
    a_space = [saturation / 2 * x * (1 - x) for x in light_space]

    phi_space = [2 * math.pi * x for x in _linspace(start, start + rotations, n_colors)]
    if categorical:
        phi_space = _shuffle(phi_space, n_colors // 3)
    cos_space = [math.cos(x) for x in phi_space]
    sin_space = [math.sin(x) for x in phi_space]

    col_mat = [[-0.14861, 1.78277], [-0.29227, -0.90649], [1.97294, 0.0]]

    colors = []
    for light, a, cos, sin in zip(light_space, a_space, cos_space, sin_space):
        color = []
        for col_row in col_mat:
            value = light + a * (col_row[0] * cos + col_row[1] * sin)
            value = min(1.0, max(0.0, value))
            color.append(value)
        colors.append(color)
    return colors


def _linspace(lower: float, upper: float, n: int) -> List[float]:
    """Linspace between lower and upper bound (inclusive) without Numpy."""
    step = (upper - lower) / (n - 1)
    return [lower + i * step for i in range(n)]


def _shuffle(items: List, n_splits: int = 2) -> List:
    """Shuffle items from by iterating between splits of the items."""
    if n_splits <= 1:
        return items

    n_items = len(items)
    frac = n_items / n_splits
    if frac <= 1:
        return items

    shuffled = [None] * n_items
    taken = 0
    for i in range(n_splits):
        take = len(shuffled[i::n_splits])
        shuffled[i::n_splits] = items[taken : taken + take]
        taken += take

    return shuffled
