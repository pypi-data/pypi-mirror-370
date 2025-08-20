"""# RaGraph colors and palettes

This module contains several convenient methods to obtain color palettes as lists of
hex-coded colors. The defaults for categorical and continuous data are
[`get_categorical`][ragraph.colors.get_categorical] and
[`get_continuous`][ragraph.colors.get_continuous], respectively.

Additional methods are included, most of which are based on the
[`cubehelix palette`][ragraph.colors.cubehelix.cubehelix_palette] with certain preset options.
[`get_hue`][ragraph.colors.get_hue] is a great way to get a sequential color palette for any hue
where the hue value corresponds to anything between red (1.0), green (2.0) or blue (3.0).

In our plots, these colors are *not* interpolated. This opens up an easy way to visualize your
colors in a discrete fashion, since you merely need to supply a list with less colors (e.g. the
desired number of discrete steps).
"""

from typing import Any, Dict, List

from ragraph.colors.cubehelix import cubehelix_palette


def get_categorical(n_colors: int = 10, **kwargs) -> List[str]:
    """Get a color palette suitable for categorical data.

    Arguments:
        n_colors: Number of colors to generate.

    Returns:
        A list of colors as hex codes.

    Note:
        Additional keyword arguments are passed on to
        [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette].
    """
    n_colors = max(n_colors, 1)
    base_light = 0.6
    if n_colors <= 10:
        dark = base_light
        light = base_light
    else:
        excess = n_colors - 10
        dark = max(0.3, base_light - excess * 0.05)
        light = min(0.8, base_light + excess * 0.05)
    opts: Dict[str, Any] = dict(
        n_colors=n_colors,
        start=2.8,
        rotations=(n_colors - 1) / n_colors,
        dark=light,  # Get the darker colors first.
        light=dark,
        gamma=1.0,
        saturation=1.8,
        categorical=True,
    )
    opts.update(kwargs)
    return cubehelix_palette(**opts)


def get_continuous(n_colors: int = 256, **kwargs) -> List[str]:
    """Get a default color palette suitable for continuous valued data.

    Arguments:
        n_colors: Number of colors to generate.

    Returns:
        A list of colors as hex codes.

    Note:
        Additional keyword arguments are passed on to
        [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette].
    """
    n_colors = max(n_colors, 1)
    opts: Dict[str, Any] = dict(
        n_colors=n_colors,
        start=2.25,
        end=3.45,
        dark=0.2,
        light=0.85,
        gamma=1.0,
        saturation=1.2,
        categorical=False,
    )
    opts.update(kwargs)
    return cubehelix_palette(**opts)


def get_hue(n_colors: int = 256, hue: float = 1.0, **kwargs) -> List[str]:
    """Get a sequential color palette with the given hue.

    Arguments:
        n_colors: Number of colors to generate.
        hue: Hue for this sequential color palette.

    Returns:
        A list of colors as hex codes.

    Note:
        Additional keyword arguments are passed on to
        [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette].
    """
    n_colors = max(n_colors, 1)
    opts: Dict[str, Any] = dict(
        n_colors=n_colors,
        start=hue,
        end=hue,
        dark=0.25,
        light=1.0,
        gamma=1.0,
        saturation=1.8,
        categorical=False,
    )
    opts.update(**kwargs)
    return cubehelix_palette(**opts)


def get_purple(n_colors: int = 256, **kwargs) -> List[str]:
    """Get a purple sequential color palette.

    Arguments:
        n_colors: Number of colors to generate.

    Returns:
        A list of colors as hex codes.

    Note:
        Additional keyword arguments are passed on to
        [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette].
    """
    opts: Dict[str, Any] = dict(hue=0.15, n_colors=n_colors)
    opts.update(**kwargs)
    return get_hue(**opts)


def get_red(n_colors: int = 256, **kwargs) -> List[str]:
    """Get a red sequential color palette.

    Arguments:
        n_colors: Number of colors to generate.

    Returns:
        A list of colors as hex codes.

    Note:
        Additional keyword arguments are passed on to
        [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette].
    """
    opts: Dict[str, Any] = dict(hue=0.95, n_colors=n_colors)
    opts.update(**kwargs)
    return get_hue(**opts)


def get_orange(n_colors: int = 256, **kwargs) -> List[str]:
    """Get an orange sequential color palette.

    Arguments:
        n_colors: Number of colors to generate.

    Returns:
        A list of colors as hex codes.

    Note:
        Additional keyword arguments are passed on to
        [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette].
    """
    opts: Dict[str, Any] = dict(hue=1.2, n_colors=n_colors)
    opts.update(**kwargs)
    return get_hue(**opts)


def get_green(n_colors: int = 256, **kwargs) -> List[str]:
    """Get a green sequential color palette.

    Arguments:
        n_colors: Number of colors to generate.

    Returns:
        A list of colors as hex codes.

    Note:
        Additional keyword arguments are passed on to
        [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette].
    """
    opts: Dict[str, Any] = dict(hue=1.8, n_colors=n_colors)
    opts.update(**kwargs)
    return get_hue(**opts)


def get_cyan(n_colors: int = 256, **kwargs) -> List[str]:
    """Get a cyan sequential color palette.

    Arguments:
        n_colors: Number of colors to generate.

    Returns:
        A list of colors as hex codes.

    Note:
        Additional keyword arguments are passed on to
        [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette].
    """
    opts: Dict[str, Any] = dict(hue=2.45, n_colors=n_colors)
    opts.update(**kwargs)
    return get_hue(**opts)


def get_blue(n_colors: int = 256, **kwargs) -> List[str]:
    """Get a blue sequential color palette.

    Arguments:
        n_colors: Number of colors to generate.

    Returns:
        A list of colors as hex codes.

    Note:
        Additional keyword arguments are passed on to
        [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette].
    """
    opts: Dict[str, Any] = dict(hue=2.85, n_colors=n_colors)
    opts.update(**kwargs)
    return get_hue(**opts)


def get_diverging_hues(
    n_colors: int = 257,
    lower_hue: float = 0.95,
    upper_hue: float = 2.85,
    midpoint: float = 0.5,
    **kwargs,
) -> List[str]:
    """Get a diverging color palette between two hues.

    Arguments:
        n_colors: Number of colors (will always return an uneven number of colors).
        lower_hue: Lower bound hue value.
        upper_hue: Upper bound hue value.
        midpoint: Fraction between [0.0, 1.0] where to put the midpoint.

    Returns:
        A list of colors as hex codes.

    Note:
        Additional keyword arguments are passed on to
        [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette].
    """
    if n_colors <= 1:
        return ["#ffffff"]

    midindex = round(midpoint * (n_colors - 1))
    lower = get_hue(hue=lower_hue, n_colors=midindex + 1, **kwargs)
    upper = get_hue(hue=upper_hue, n_colors=n_colors - midindex, **kwargs)
    return lower[::-1] + upper[1:]


def get_diverging_redblue(n_colors: int = 257, **kwargs) -> List[str]:
    """Get a red-white-blue diverging color palette.

    Arguments:
        n_colors: Number of colors to generate.

    Returns:
        A list of colors as hex codes.

    Note:
        Additional keyword arguments are passed on to
        [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette].
    """
    opts: Dict[str, Any] = dict(lower_hue=0.95, upper_hue=2.85, n_colors=n_colors)
    opts.update(kwargs)
    return get_diverging_hues(**opts)


def get_diverging_orangecyan(n_colors: int = 257, **kwargs) -> List[str]:
    """Get a orange-white-cyan diverging color palette.

    Arguments:
        n_colors: Number of colors to generate.

    Returns:
        A list of colors as hex codes.

    Note:
        Additional keyword arguments are passed on to
        [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette].
    """
    opts: Dict[str, Any] = dict(lower_hue=1.2, upper_hue=2.45, n_colors=n_colors)
    opts.update(kwargs)
    return get_diverging_hues(**opts)


def get_diverging_purplegreen(n_colors: int = 257, **kwargs) -> List[str]:
    """Get a purple-white-green diverging color palette.

    Arguments:
        n_colors: Number of colors to generate.

    Returns:
        A list of colors as hex codes.

    Note:
        Additional keyword arguments are passed on to
        [`cubehelix_palette`][ragraph.colors.cubehelix.cubehelix_palette].
    """
    opts: Dict[str, Any] = dict(lower_hue=0.15, upper_hue=1.8, n_colors=n_colors)
    opts.update(kwargs)
    return get_diverging_hues(**opts)


def get_colormaps(
    n_colors: int = 1,
    kind: str = "categorical",
    amount: int = 1,
    flip: bool = False,
) -> List[List[str]]:
    """Get multiple colormaps of a certain kind.

    Arguments:
        n_colors: Number of colors per colormap to generate.
        kind: Kind of colormap. One of 'categorical', 'sequential', or 'diverging'.
        amount: Number of colormaps to generate.
        flip: Whether to reverse the generated colormaps.
    """
    if kind == "categorical":
        return [get_categorical(n_colors=n_colors)]
    elif kind == "sequential":
        if amount == 1:
            colormaps = [get_continuous(n_colors=n_colors)]
        else:
            colormaps = [
                get_hue(n_colors=n_colors, hue=2.85 + 3 * i / amount) for i in range(amount)
            ]
    elif kind == "diverging":
        colormaps = [
            get_diverging_hues(
                n_colors=n_colors,
                lower_hue=0.95 - 1.0 * i / amount,
                upper_hue=2.85 - 2 * i / amount,
            )
            for i in range(amount)
        ]
    else:
        allowed = ["categorical", "sequential", "diverging"]
        raise ValueError(f"Unknown colormap kind. Pick one of '{allowed}'.")

    if flip:
        return [colormap[::-1] for colormap in colormaps]
    else:
        return colormaps
