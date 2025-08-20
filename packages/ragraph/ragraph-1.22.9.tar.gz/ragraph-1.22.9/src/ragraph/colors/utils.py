"""# Color utilities"""

from typing import Tuple


def rgb1_to_rgb(r: float, g: float, b: float) -> Tuple[int, int, int]:
    """Convert [0.0-1.0] scaled RGB to [0-255]."""
    return round(r * 255), round(g * 255), round(b * 255)


def rgb_to_rgb1(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert [0-255] scaled RGB to [0.0-1.0]."""
    return r / 255, g / 255, b / 255


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB color to hex code."""
    return "#{0:02x}{1:02x}{2:02x}".format(r, g, b)


def hex_to_rgb(h: str) -> Tuple[int, int, int]:
    """Convert hex code to RGB tuple."""
    h = h.lstrip("#")
    n = len(h)
    rgb = tuple(int(h[i : i + n // 3], 16) for i in range(0, n, n // 3))
    return rgb[0], rgb[1], rgb[2]
