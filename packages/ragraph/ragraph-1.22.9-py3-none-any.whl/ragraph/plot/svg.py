"""# SVG shapes

This module contains two base classes, being the [`Line`][ragraph.plot.svg.Line] options for SVG
shapes and an [`SVG`][ragraph.plot.svg.SVG] mapping for the shapes themselves. You will also find
several methods to obtain several basic shapes conveniently.
"""

from math import cos, pi, sin
from typing import Any, Dict, Optional, Union

from ragraph.generic import Mapping, field


class Line(Mapping):
    """SVG line options mapping.

    Arguments:
        color: Line color.
        width: Line width in pixels.
        dash: Dash style of the line.
    """

    _defaults = dict(color="rgba(0,0,0,0)", width=2, dash="solid")

    def __init__(
        self,
        color: Optional[str] = None,
        width: Optional[int] = None,
        dash: Optional[str] = None,
    ):
        super().__init__(color=color, width=width, dash=dash)

    @field
    def color(self) -> str:  # type: ignore
        """Line color."""

    @field
    def width(self) -> int:  # type: ignore
        """Line width in pixels."""

    @field
    def dash(self) -> str:  # type: ignore
        """Dash style of the line."""


class SVG(Mapping):
    """SVG shape mapping.

    Arguments:
        visible: Toggles shape visibility.
        type: One of 'circle', 'rect', 'path' or 'line'.
        layer: 'above' draws shape above traces, 'below' under them.
        xref: x coordinate axis. 'paper' or 'x', 'x1', 'x2', etc.
        xsizemode: 'scaled' or 'pixel'. Relative or absolute sizing w.r.t. axis.
        xanchor: If sizemode is set to 'pixel', reference on axis to anchor shape to.
        x0: Starting x position.
        x1: Ending x position.
        yref: y coordinate axis. 'paper' or 'y', 'y1', 'y2', etc.
        ysizemode: 'scaled' or 'pixel'. Relative or absolute sizing w.r.t. axis.
        yanchor: If sizemode is set to 'pixel', reference on axis to anchor shape to.
        y0: Starting y position.
        y1: Ending y position.
        path: For shapetype 'path', a valid SVG path, with data values as coordinates when
            referencing axis and absolute pixels with respect to anchors when the 'pixel' sizemode
            is set.
        opacity: The opacity between 0.0 and 1.0.
        line: Line mapping options. See [`Line`][ragraph.plot.svg.Line].
        fillcolor: Interior shape color.
        fillrule: Determines which regions of complex paths constitute the interior.
            One of "evenodd" or "nonzero".
        editable: Whether the shape could be activated for edit or not.
        name: Only used with templates.
        templateitemname: Used to refer to a named item in this array in the template.
    """

    _keys = {
        "visible",
        "type",
        "layer",
        "xref",
        "xsizemode",
        "xanchor",
        "x0",
        "x1",
        "yref",
        "ysizemode",
        "yanchor",
        "y0",
        "y1",
        "path",
        "opacity",
        "line",
        "fillcolor",
        "fillrule",
        "editable",
        "name",
        "templateitemname",
    }

    def __init__(
        self,
        visible: Optional[bool] = None,
        type: Optional[str] = None,
        layer: Optional[str] = None,
        xref: Optional[str] = None,
        xsizemode: Optional[str] = None,
        xanchor: Optional[str] = None,
        x0: Optional[float] = None,
        x1: Optional[float] = None,
        yref: Optional[str] = None,
        ysizemode: Optional[str] = None,
        yanchor: Optional[str] = None,
        y0: Optional[float] = None,
        y1: Optional[float] = None,
        path: Optional[str] = None,
        opacity: Optional[float] = None,
        line: Optional[Union[Dict[str, Any], Line]] = None,
        fillcolor: Optional[str] = None,
        fillrule: Optional[str] = None,
        editable: Optional[bool] = None,
        name: Optional[str] = None,
        templateitemname: Optional[str] = None,
    ):
        super().__init__(
            visible=visible,
            type=type,
            layer=layer,
            xref=xref,
            xsizemode=xsizemode,
            xanchor=xanchor,
            x0=x0,
            x1=x1,
            yref=yref,
            ysizemode=ysizemode,
            yanchor=yanchor,
            y0=y0,
            y1=y1,
            path=path,
            opacity=opacity,
            line=line,
            fillcolor=fillcolor,
            fillrule=fillrule,
            editable=editable,
            name=name,
            templateitemname=templateitemname,
        )

    @field
    def visible(self) -> bool:  # type: ignore
        """Toggles shape visibility."""

    @field
    def type(self) -> str:  # type: ignore
        """One of 'circle', 'rect', 'path' or 'line'."""

    @field
    def layer(self) -> str:  # type: ignore
        """'above' draws shape above traces, 'below' under them."""

    @field
    def xref(self) -> str:  # type: ignore
        """x coordinate axis. 'paper' or 'x', 'x1', 'x2', etc."""

    @field
    def xsizemode(self) -> str:  # type: ignore
        """'scaled' or 'pixel'. Relative or absolute sizing w.r.t. axis."""

    @field
    def xanchor(self) -> str:  # type: ignore
        """If sizemode is set to 'pixel', reference on axis to anchor shape to."""

    @field
    def x0(self) -> float:  # type: ignore
        """Starting x position."""

    @field
    def x1(self) -> float:  # type: ignore
        """Ending x position."""

    @field
    def yref(self) -> str:  # type: ignore
        """y coordinate axis. 'paper' or 'y', 'y1', 'y2', etc."""

    @field
    def ysizemode(self) -> str:  # type: ignore
        """'scaled' or 'pixel'. Relative or absolute sizing w.r.t. axis."""

    @field
    def yanchor(self) -> str:  # type: ignore
        """If sizemode is set to 'pixel', reference on axis to anchor shape to."""

    @field
    def y0(self) -> float:  # type: ignore
        """Starting y position."""

    @field
    def y1(self) -> float:  # type: ignore
        """Ending y position."""

    @field
    def path(self) -> str:  # type: ignore
        """For shapetype 'path', a valid SVG path, with data values as coordinates when referencing
        axis and absolute pixels with respect to anchors when the 'pixel' sizemode is set.
        """

    @field
    def opacity(self) -> float:  # type: ignore
        """The opacity between 0.0 and 1.0."""

    @field
    def line(self) -> Line:  # type: ignore
        """Line mapping options. See [`Line`][ragraph.plot.svg.Line]."""

    @field
    def fillcolor(self) -> str:  # type: ignore
        """Interior shape color."""

    @field
    def fillrule(self) -> str:  # type: ignore
        """Determines which regions of complex paths constitute the interior.
        One of 'evenodd' or 'nonzero'.
        """

    @field
    def editable(self) -> bool:  # type: ignore
        """Whether the shape could be activated for edit or not."""

    @field
    def name(self) -> str:  # type: ignore
        """Only used with templates."""

    @field
    def templateitemname(self) -> str:  # type: ignore
        """Used to refer to a named item in this array in the template."""


def get_line(
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    **kwargs: Any,
) -> SVG:
    """Get straight line SVG mapping.

    Arguments:
        x0: Starting x position.
        x1: Ending x position.
        y0: Starting y position.
        y1: Ending y position.
        **kwargs: Overrides for the [`SVG`][ragraph.plot.svg.SVG] object.

    Returns:
        SVG shape mapping.
    """
    return SVG(type="line", x0=x0, x1=x1, y0=y0, y1=y1, **kwargs)


def get_curvedline(
    x0: float,
    x1: float,
    x2: float,
    y0: float,
    y1: float,
    y2: float,
    **kwargs: Any,
) -> SVG:
    """Get curved line (quadratic Bezier) SVG mapping.

    Arguments:
        x0: Starting x position.
        x1: Control point x position.
        x2: Ending x position.
        y0: Starting y position.
        y1: Control point y position.
        y2: Ending y position.
        **kwargs: Overrides for the [`SVG`][ragraph.plot.svg.SVG] object.

    Returns:
        Quadratic Bezier SVG shape mapping.
    """
    path = f"M {x0} {y0} Q {x1} {y1} {x2} {y2}"
    return SVG(type="path", path=path, **kwargs)


def get_rectangle(
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    **kwargs: Any,
) -> SVG:
    """Get a rectangle SVG mapping.

    Arguments:
        x0: Starting x position.
        x1: Ending x position.
        y0: Starting y position.
        y1: Ending y position.
        **kwargs: Overrides for the [`SVG`][ragraph.plot.svg.SVG] object.

    Returns:
        SVG shape mapping.
    """
    return SVG(type="rect", x0=x0, x1=x1, y0=y0, y1=y1, **kwargs)


def get_wedge(
    x: float, y: float, r: float, start_angle: float, end_angle: float, **kwargs: Any
) -> SVG:
    """Get a wedge SVG mapping.

    Arguments:
        x: x position of the wedge center.
        y: y position of the wedge center.
        r: radius of the wedge.
        start_angle: Starting angle (radians) of the wedge.
        end_angle: Ending angle (radians) of the wedge.
        **kwargs: Overrides for the [`SVG`][ragraph.plot.svg.SVG] object.

    Returns:
        SVG shape mapping.
    """
    segments = ["M {} {}".format(x, y)]
    xa = x + round(r * cos(start_angle), 3)
    xb = y + round(r * sin(start_angle), 3)
    segments.append(" L {} {}".format(xa, xb))

    delta = end_angle - start_angle
    max_delta = 0.25 * pi
    while delta > 0:
        if delta >= max_delta:
            angle_step = max_delta
        else:
            angle_step = delta

        # Get curve control points
        xc = round(
            x + r / cos(angle_step / 2) * cos(start_angle + angle_step / 2),
            3,
        )
        yc = round(
            y + r / cos(angle_step / 2) * sin(start_angle + angle_step / 2),
            3,
        )
        xe = round(x + r * cos(start_angle + angle_step), 3)
        ye = round(y + r * sin(start_angle + angle_step), 3)

        # Add the segment.
        segments.append(" Q {} {} {} {}".format(xc, yc, xe, ye))
        delta -= angle_step
        start_angle += angle_step

    segments.append(" Z")

    path = "".join(segments)

    return SVG(type="path", path=path, **kwargs)
