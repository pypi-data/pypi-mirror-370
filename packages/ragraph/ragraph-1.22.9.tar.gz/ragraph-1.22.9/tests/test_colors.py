"""Tests for the plot colors module."""

import pytest
from ragraph import colors
from ragraph.colors import cubehelix, utils


@pytest.fixture(
    params=[
        (
            "get_categorical",
            [
                "#6a9ffc",
                "#dc69e2",
                "#f27663",
                "#8db32f",
                "#38cc8e",
            ],
        ),
        (
            "get_continuous",
            [
                "#b6ead9",
                "#7dc2d5",
                "#6b86cd",
                "#6b499f",
                "#541d4f",
            ],
        ),
        (
            "get_hue",
            [
                "#ffffff",
                "#ffb9ad",
                "#f67d6a",
                "#cb4b38",
                "#852415",
            ],
        ),
        (
            "get_purple",
            [
                "#ffffff",
                "#debcff",
                "#b581ff",
                "#8750da",
                "#512890",
            ],
        ),
        (
            "get_red",
            [
                "#ffffff",
                "#ffb6b3",
                "#fa7974",
                "#cf4842",
                "#88211d",
            ],
        ),
        (
            "get_orange",
            [
                "#ffffff",
                "#f8c597",
                "#de8f4a",
                "#b25f15",
                "#723300",
            ],
        ),
        (
            "get_green",
            [
                "#ffffff",
                "#afea97",
                "#6dc94a",
                "#3b9b15",
                "#186100",
            ],
        ),
        (
            "get_cyan",
            [
                "#ffffff",
                "#94e8eb",
                "#45c6cb",
                "#10989d",
                "#005e62",
            ],
        ),
        (
            "get_blue",
            [
                "#ffffff",
                "#b7cfff",
                "#7a9fff",
                "#4870da",
                "#224090",
            ],
        ),
        (
            "get_diverging_hues",
            [
                "#88211d",
                "#fa7974",
                "#ffffff",
                "#7a9fff",
                "#224090",
            ],
        ),
        (
            "get_diverging_redblue",
            ["#88211d", "#fa7974", "#ffffff", "#7a9fff", "#224090"],
        ),
        (
            "get_diverging_orangecyan",
            ["#723300", "#de8f4a", "#ffffff", "#45c6cb", "#005e62"],
        ),
        (
            "get_diverging_purplegreen",
            ["#512890", "#b581ff", "#ffffff", "#6dc94a", "#186100"],
        ),
    ]
)
def palettes_exp(request):
    fname, exp5 = request.param
    fn = getattr(colors, fname)
    return fn, exp5


def test_toplevel_palettes(palettes_exp):
    # Unpack the fixture.
    fn, exp5 = palettes_exp

    N = 5  # uneven as we'd like to test middle points in the diverging pals.
    result = fn(N)

    # Expected result for N=5.
    assert len(result) == 5
    assert result == exp5

    # Some smoke testing.
    assert len(fn(1)) == 1
    assert len(fn(0)) == 1


def test_categorical_extra():
    result = colors.get_categorical(12)
    assert result == [
        "#4e85e7",
        "#de4eb2",
        "#ba8322",
        "#35c360",
        "#947cff",
        "#fa668b",
        "#99b030",
        "#40cfab",
        "#d57cf8",
        "#f88c6e",
        "#80d45e",
        "#69ceea",
    ]


def test_cubehelix():
    pure = [
        [round(i, 10) for i in color]
        for color in cubehelix._cubehelix_pure_python(5, categorical=True)
    ]
    nump = [
        [round(i, 10) for i in color] for color in cubehelix._cubehelix_numpy(5, categorical=True)
    ]

    assert pure == nump, "Should be identical except from rounding errors."

    # Fully cover the cubehelix utils, too.
    shuffle_me = [0, 1, 2, 3]
    assert cubehelix._shuffle(shuffle_me, 2) == [0, 2, 1, 3], "should return shuffled."
    assert cubehelix._shuffle(shuffle_me, 8) == [0, 1, 2, 3], "should return input."


def test_utils():
    assert utils.rgb_to_rgb1(51, 0, 255) == (0.2, 0.0, 1.0)
    assert utils.hex_to_rgb("#bffbae") == (191, 251, 174)
