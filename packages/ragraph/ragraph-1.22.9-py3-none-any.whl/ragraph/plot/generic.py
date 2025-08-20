"""# RaGraph generic plotting classes"""

from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from plotly import graph_objs as go
from plotly.basedatatypes import BaseTraceType

from ragraph import colors
from ragraph.generic import Convention, Mapping, field
from ragraph.plot import svg

MODEBAR_BUTTONS = {
    "toImage",
    "sendDataToCloud",
    "editInChartStudio",
    "zoom2d",
    "pan2d",
    "select2d",
    "lasso2d",
    "zoomIn2d",
    "zoomOut2d",
    "autoScale2d",
    "resetScale2d",
    "hoverClosestCartesian",
    "hoverCompareCartesian",
    "zoom3d",
    "pan3d",
    "orbitRotation",
    "tableRotation",
    "resetCameraDefault3d",
    "resetCameraLastSave3d",
    "hoverClosest3d",
    "zoomInGeo",
    "zoomOutGeo",
    "resetGeo",
    "hoverClosestGeo",
    "hoverClosestGl2d",
    "hoverClosestPie",
    "resetSankeyGroup",
    "toggleHover",
    "resetViews",
    "toggleSpikelines",
    "resetViewMapbox",
}


class TreeStyle(Mapping):
    """RaGraph tree plot component style mapping.

    Arguments:
        line: Line style mapping for hierarchy tree lines.
        xaxis: Plotly X-axis settings.
        yaxis: Plotly Y-axis settings.
    """

    _defaults = dict(
        line=svg.Line(color="gray"),
        xaxis=go.layout.XAxis(
            showgrid=False,
            showticklabels=False,
            automargin=False,
            scaleratio=1.0,
            zeroline=False,
            showline=False,
            autorange=False,
        ),
        yaxis=go.layout.YAxis(
            autorange=False,
            scaleratio=1.0,
            automargin=False,
            showgrid=True,
            showticklabels=False,
            scaleanchor="x",
            zeroline=False,
            showline=False,
        ),
    )

    def __init__(
        self,
        line: Optional[Union[svg.Line, Dict[str, Any]]] = None,
        xaxis: Optional[Union[go.layout.XAxis, Dict[str, Any]]] = None,
        yaxis: Optional[Union[go.layout.YAxis, Dict[str, Any]]] = None,
    ):
        if isinstance(xaxis, dict):
            _xaxis = deepcopy(self._defaults["xaxis"])
            for k, v in xaxis.items():
                setattr(_xaxis, k, v)
            xaxis = _xaxis

        if isinstance(yaxis, dict):
            _yaxis = deepcopy(self._defaults["yaxis"])
            for k, v in yaxis.items():
                setattr(_yaxis, k, v)
            yaxis = _yaxis

        super().__init__(line=line, xaxis=xaxis, yaxis=yaxis)

    @field
    def line(self) -> svg.Line:  # type: ignore
        """Line style mapping for hierarchy tree lines."""

    @field
    def xaxis(self) -> go.layout.XAxis:  # type: ignore
        """Plotly X-axis settings."""

    @field
    def yaxis(self) -> go.layout.YAxis:  # type: ignore
        """Plotly Y-axis settings."""


class LabelsStyle(Mapping):
    """Labels plot component style mapping.

    Arguments:
        fontcolor: Font color used for labels.
        fontfamily: Font family used for labels.
        fontsize: Fontsize used for labels.
        fontaspectratio: Font width per fontsize ratio.
        textorientation: Orientation of label text, one of "horizontal", "vertical".
        xaxis: Plotly X-axis settings.
        yaxis: Plotly Y-axis settings.
    """

    _defaults = dict(
        fontcolor="black",
        fontfamily="Fira Code,Hack,Courier New,monospace",
        fontsize=None,
        fontaspectratio=0.6005,
        shorten=True,
        textorientation="horizontal",
        xaxis=go.layout.XAxis(
            automargin=False,
            scaleanchor="y",
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        yaxis=go.layout.YAxis(
            automargin=False,
            autorange=False,
            scaleratio=1.0,
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
    )

    def __init__(
        self,
        fontcolor: Optional[str] = None,
        fontfamily: Optional[str] = None,
        fontsize: Optional[int] = None,
        fontaspectratio: Optional[float] = None,
        shorten=None,
        textorientation: Optional[str] = None,
        xaxis: Optional[Union[go.layout.XAxis, Dict[str, Any]]] = None,
        yaxis: Optional[Union[go.layout.YAxis, Dict[str, Any]]] = None,
    ):
        if isinstance(xaxis, dict):
            _xaxis = deepcopy(self._defaults["xaxis"])
            for k, v in xaxis.items():
                setattr(_xaxis, k, v)
            xaxis = _xaxis

        if isinstance(yaxis, dict):
            _yaxis = deepcopy(self._defaults["yaxis"])
            for k, v in yaxis.items():
                setattr(_yaxis, k, v)
            yaxis = _yaxis

        super().__init__(
            fontcolor=fontcolor,
            fontfamily=fontfamily,
            fontsize=fontsize,
            fontaspectratio=fontaspectratio,
            shorten=shorten,
            textorientation=textorientation,
            xaxis=xaxis,
            yaxis=yaxis,
        )

    @field
    def fontcolor(self) -> str:  # type: ignore
        """Font color used for labels."""

    @field
    def fontfamily(self) -> str:  # type: ignore
        """Font family used for labels."""

    @field
    def fontsize(self) -> int:  # type: ignore
        """Fontsize used for labels."""

    @field
    def fontaspectratio(self) -> float:  # type: ignore
        """Font width per fontsize ratio."""

    @field
    def shorten(self) -> Union[bool, Callable[[str], str]]:  # type: ignore
        """Label shortening toggle or function. When set to `True` everything after
        the last dot '.' is kept.
        """

    @field
    def textorientation(self) -> float:  # type: ignore
        """Orientation of text."""

    @field
    def xaxis(self) -> go.layout.XAxis:  # type: ignore
        """Plotly X-axis settings."""

    @field
    def yaxis(self) -> go.layout.YAxis:  # type: ignore
        """Plotly Y-axis settings."""


class PieMapStyle(Mapping):
    """Piechart map's plot component style mapping.

    Arguments:
        busarea: Bus area SVG mapping. Used for styling the bus area.
        display: What to display. One of 'kinds', 'labels', 'weight labels', 'weights'.
        fields: The fields to plot (the selection of kinds, labels, or weights). Leave set to `None`
            to display all the available fields automatically.
        gridline: Grid line options mapping.
        highlight_col_annotation: Annotation that signals what columns should be highlighted.
            Value should be True-ish.
        highlight_col_color: Default color to use for column highlights.
        highlight_row_annotation: Annotation that signals what rows should be highlighted.
            Value should be True-ish.
        highlight_row_color: Default color to use for row highlights.
        inherit: Whether to display edges between descendants of the axis nodes.
        kindline: Node kind separation lines options mapping.
        mode: How to divide the pie-charts per category: 'equal' or 'relative'.
            'equal' divides the piechart evenly.
            'relative' divides the piechart according to category value.
        radius: The piechart radius between 0.0 and 0.5.
        scale_weight: Edge weight label that should contain values between 0.0 and 1.0 to scale the
            radius with.
        customhoverkeys: List of keys for information to be displayed on hover.
        xaxis: Plotly X-axis settings.
        yaxis: Plotly Y-axis settings.

    Note:
        The `display` argument determines what is going to be plotted as piecharts in the plot area.
        The `fields` argument is a filter on the possible values for that display mode. The `mode`
        argument then tunes how the wedges that make up the piecharts should be distributed. Most of
        the time, 'equal' gives the most predictable and clear results.
    """

    _defaults = dict(
        busarea=svg.SVG(fillcolor="rgba(150,150,150,0.2)", line=svg.Line(width=0), layer="below"),
        clusterline=svg.Line(width=2, color="gray", dash="solid"),
        display="kinds",
        fields=None,
        gridline=svg.Line(color="#dfdfdf", width=2, dash="solid"),
        highlight_col_annotation=None,
        highlight_col_color=None,
        highlight_row_annotation=None,
        highlight_row_color=None,
        inherit=False,
        kindline=svg.Line(color="gray", width=2, dash="dot"),
        mode="equal",
        radius=0.4,
        scale_weight=None,
        customhoverkeys=[],
        xaxis=go.layout.XAxis(
            automargin=False,
            scaleanchor="y",
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        yaxis=go.layout.YAxis(
            automargin=False,
            autorange=False,
            scaleratio=1.0,
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
    )

    def __init__(
        self,
        busarea: Optional[svg.SVG] = None,
        clusterline: Optional[svg.Line] = None,
        display: Optional[str] = None,
        fields: Optional[List[str]] = None,
        gridline: Optional[svg.Line] = None,
        highlight_col_annotation: Optional[str] = None,
        highlight_col_color: Optional[str] = None,
        highlight_row_annotation: Optional[str] = None,
        highlight_row_color: Optional[str] = None,
        inherit: Optional[bool] = None,
        kindline: Optional[svg.Line] = None,
        mode: Optional[str] = None,
        radius: Optional[float] = None,
        scale_weight: Optional[str] = None,
        customhoverkeys: Optional[List[str]] = None,
        xaxis: Optional[Dict[str, Any]] = None,
        yaxis: Optional[Dict[str, Any]] = None,
    ):
        if isinstance(xaxis, dict):
            _xaxis = deepcopy(self._defaults["xaxis"])
            for k, v in xaxis.items():
                setattr(_xaxis, k, v)
            xaxis = _xaxis

        if isinstance(yaxis, dict):
            _yaxis = deepcopy(self._defaults["yaxis"])
            for k, v in yaxis.items():
                setattr(_yaxis, k, v)
            yaxis = _yaxis

        super().__init__(
            busarea=busarea,
            clusterline=clusterline,
            display=display,
            fields=fields,
            gridline=gridline,
            highlight_col_annotation=highlight_col_annotation,
            highlight_col_color=highlight_col_color,
            highlight_row_annotation=highlight_row_annotation,
            highlight_row_color=highlight_row_color,
            inherit=inherit,
            kindline=kindline,
            mode=mode,
            radius=radius,
            scale_weight=scale_weight,
            customhoverkeys=customhoverkeys,
            xaxis=xaxis,
            yaxis=yaxis,
        )

    @field
    def busarea(self) -> svg.SVG:  # type: ignore
        """Bus area SVG mapping. Used for styling the bus area."""

    @field
    def display(self) -> str:  # type: ignore
        """What to display. One of 'kinds', 'labels', 'weight labels', 'weights'."""

    @field
    def fields(self) -> List[str]:  # type: ignore
        """The fields to plot (the selection of kinds, labels, or weights). Leave set
        to `None` to display all the available fields automatically.
        """

    @field
    def gridline(self) -> svg.Line:  # type: ignore
        """Grid line style."""

    @field
    def highlight_col_annotation(self) -> Optional[str]:  # type: ignore
        """Annotation that signals what columns should be highlighted.
        Value should be True-ish.
        """

    @field
    def highlight_col_color(self) -> Optional[str]:  # type: ignore
        """Default color to use for column highlights."""

    @field
    def highlight_row_annotation(self) -> Optional[str]:  # type: ignore
        """Annotation that signals what rows should be highlighted.
        Value should be True-ish.
        """

    @field
    def highlight_row_color(self) -> Optional[str]:  # type: ignore
        """Default color to use for row highlights."""

    @field
    def inherit(self) -> bool:  # type: ignore
        """Whether to display edges between descendants of the axis nodes."""

    @field
    def kindline(self) -> svg.Line:  # type: ignore
        """Node kind separation lines options mapping."""

    @field
    def mode(self) -> str:  # type: ignore
        """How to divide the piecharts per field. Either 'equal' or 'relative'.
        'equal' divides the piecharts evenly.
        'relative' divides the piechart according to field value.
        """

    @field
    def radius(self) -> float:  # type: ignore
        """The piechart radius between 0.0 and 0.5."""

    @field
    def scale_weight(self) -> str:  # type: ignore
        """Edge weight label that should contain values between 0.0 and 1.0 to scale the
        radius with.
        """

    @field
    def customhoverkeys(self) -> List[str]:  # type: ignore
        """Custom keys for information to be displayed on hover."""

    @field
    def xaxis(self) -> go.layout.XAxis:  # type: ignore
        """Plotly X-axis settings."""

    @field
    def yaxis(self) -> go.layout.YAxis:  # type: ignore
        """Plotly Y-axis settings."""


class FieldPalette(Mapping):
    """Palettes for a field in a plot.

    Argument:
        categorical: Categorical color for this field.
        continuous: Continuous (numeric) data color palette for this field.
    """

    _defaults = dict(
        categorical=None,
        continuous=None,
    )

    def __init__(
        self,
        categorical: Optional[Union[str, List[str]]] = None,
        continuous: Optional[List[str]] = None,
    ):
        super().__init__(self, categorical=categorical, continuous=continuous)

    @field
    def categorical(self) -> Optional[str]:  # type: ignore
        """Categorical color for this field."""

    @field
    def continuous(self) -> Optional[List[str]]:  # type: ignore
        """Continuous (numeric) data color palette for this field."""


class Palettes(Mapping):
    """Plot palettes mapping.

    Arguments:
        categorical: Categorical data color palette.
        continuous: Continuous (numeric) data color palette.
        fields: Palette override dictionary per display field.
        domains: Value domains to interpolate palettes between per field as a tuple of
            (lower, upper) bounds. Only used for continuous fields.
    """

    _defaults = dict(
        categorical=colors.get_categorical(),
        continuous=colors.get_continuous(),
        fields=dict(),
        domains=dict(),
    )

    def __init__(
        self,
        categorical: Optional[List[str]] = None,
        continuous: Optional[List[str]] = None,
        fields: Optional[Dict[str, FieldPalette]] = None,
        domains: Optional[Dict[str, Tuple[float, float]]] = None,
    ):
        super().__init__(
            categorical=categorical,
            continuous=continuous,
            fields=fields,
            domains=domains,
        )

    def get_categorical_palette(self, field: Optional[str] = None) -> Union[str, List[str]]:
        """Get a categorical color (palette). Might be an overridden color, colorlist,
        or the default palette for the given field."""
        palette = self.fields.get(field, self.categorical)

        # Handle when it's a dictionary/FieldPalette override.
        if isinstance(palette, dict) or isinstance(palette, FieldPalette):
            palette = palette.get("categorical", self.categorical)

        # Failsafe backup.
        if palette is None:
            palette = self.categorical

        return palette

    def get_categorical_color(self, idx: int, field: Optional[str] = None) -> str:
        """Get a color from a categorical palette."""
        palette = self.get_categorical_palette(field=field)

        if isinstance(palette, str):
            return palette
        else:
            return palette[idx]

    def get_continuous_palette(self, field: Optional[str] = None) -> List[str]:
        """Get a continuous color palette."""
        palette = self.fields.get(field, self.continuous)

        # Handle when it's a dictionary/FieldPalette override.
        if isinstance(palette, dict) or isinstance(palette, FieldPalette):
            palette = palette.get("continuous", self.continuous)

        # Failsafe backup.
        return self.continuous if palette is None else palette

    def get_continuous_color(
        self,
        value: float,
        lower: float,
        upper: float,
        field: Optional[str] = None,
    ) -> str:
        """Get a color from the continuous palette by its interpolated index.

        Arguments:
            value: Value to get an interpolated color for.
            lower: Lower bound value (overridden if selected field is in domains).
            upper: Upper bound value (overridden if selected field is in domains).
            field: Optional field to fetch the palette for.
        """
        palette = self.get_continuous_palette(field=field)

        # Override lower and upper if domains are set.
        if field in self.domains:
            lower, upper = self.domains[field]

        # No scale, return highest.
        if lower == upper:
            return palette[-1]

        step = (upper - lower) / (len(palette) - 1)
        idx = int((value - lower) // step)

        idx = min(max(idx, 0), len(palette) - 1)
        return palette[idx]

    @field
    def categorical(self) -> List[str]:  # type: ignore
        """Categorical data color palette."""

    @field
    def continuous(self) -> List[str]:  # type: ignore
        """Continuous (numeric) data color palette."""

    @field
    def fields(self) -> Dict[str, Union[str, List[str], FieldPalette]]:  # type: ignore
        """Palette override dictionary per display field."""

    @field
    def domains(self) -> Dict[str, Tuple[float, float]]:  # type: ignore
        """Value domains to interpolate palettes between per field as a tuple of
        (lower, upper), bounds. Only used for continuous fields.
        """


class LegendStyle(Mapping):
    """Legend plot component style mapping.

    Arguments:
        fontcolor: Font color used for labels.
        fontfamily: Font family used for labels.
        fontsize: Fontsize used for labels.
        fontaspectratio: Font width per fontsize ratio.
        height: Height of the swatch plot in number of box sizes when
            plotting a numerical legend.
        n_ticks: Number of ticks in the swatch plot when plotting a numerical legend.
        xaxis: Plotly X-axis settings.
        yaxis: Plotly Y-axis settings.
    """

    _defaults = dict(
        fontcolor="black",
        fontfamily="Fira Code,Hack,Courier New,monospace",
        fontsize=None,
        fontaspectratio=0.6005,
        height=10,
        n_ticks=5,
        xaxis=go.layout.XAxis(
            automargin=False,
            scaleanchor="y",
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        yaxis=go.layout.YAxis(
            automargin=False,
            autorange=False,
            scaleratio=1.0,
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
    )

    def __init__(
        self,
        fontcolor: Optional[str] = None,
        fontfamily: Optional[str] = None,
        fontsize: Optional[int] = None,
        fontaspectratio: Optional[float] = None,
        height: Optional[int] = None,
        n_ticks: Optional[int] = None,
        xaxis: Optional[Union[go.layout.XAxis, Dict[str, Any]]] = None,
        yaxis: Optional[Union[go.layout.YAxis, Dict[str, Any]]] = None,
    ):
        if isinstance(xaxis, dict):
            _xaxis = deepcopy(self._defaults["xaxis"])
            for k, v in xaxis.items():
                setattr(_xaxis, k, v)
            xaxis = _xaxis

        if isinstance(yaxis, dict):
            _yaxis = deepcopy(self._defaults["yaxis"])
            for k, v in yaxis.items():
                setattr(_yaxis, k, v)
            yaxis = _yaxis

        super().__init__(
            fontcolor=fontcolor,
            fontfamily=fontfamily,
            fontsize=fontsize,
            fontaspectratio=fontaspectratio,
            height=height,
            n_ticks=n_ticks,
            xaxis=xaxis,
            yaxis=yaxis,
        )

    @field
    def fontcolor(self) -> str:  # type: ignore
        """Font color used for labels."""

    @field
    def fontfamily(self) -> str:  # type: ignore
        """Font family used for labels."""

    @field
    def fontsize(self) -> int:  # type: ignore
        """Fontsize used for labels."""

    @field
    def fontaspectratio(self) -> float:  # type: ignore
        """Font width per fontsize ratio."""

    @field
    def height(self) -> int:  # type: ignore
        """Height of the swatch plot in number of box sizes when plotting a numerical legend."""

    @field
    def n_ticks(self) -> int:  # type: ignore
        """Number of ticks in the swatch plot when plotting a numerical legend."""

    @field
    def xaxis(self) -> go.layout.XAxis:  # type: ignore
        """Plotly X-axis settings."""

    @field
    def yaxis(self) -> go.layout.YAxis:  # type: ignore
        """Plotly Y-axis settings."""


class ChordStyle(Mapping):
    """RaGraph chord style mapping.

    Arguments:
        radius: Radius of the Chord plot.
        padding: Padding to apply around the Chord plot.
        gap_size: Gap size between the nodes in the Chord plot.
        ribbon_gap: Gap size between the outside arc (circle) and ribbons.
        ribbon_stiffness: Tweaks the curvature of the ribbons (0.0 straight, 1.0 delayed curve).
        arc_thickness: Thickness of the outside arc (circle).
        bg_color: Background color of the Chord plot.
        bg_transparency: Background color transparency of the Chord plot.
        fontsize: Chord plot font size.
        fontfactor: Font factor to calculate the padding with.
        fontfamily: Chord plot font family.
    """

    _defaults = dict(
        radius=200,
        padding=None,
        gap_size=0.008,
        ribbon_gap=0.0,
        ribbon_stiffness=0.6,
        arc_thickness=0.05,
        bg_color="#ffffff",
        bg_transparency=0.0,
        fontsize=10,
        fontfactor=0.72,
        fontfamily="Fira Code,Noto Sans,Courier New,monospace",
    )

    def __init__(
        self,
        radius: Optional[Union[int, float]] = None,
        padding: Optional[Union[int, float]] = None,
        gap_size: Optional[float] = None,
        ribbon_gap: Optional[float] = None,
        ribbon_stiffness: Optional[float] = None,
        arc_thickness: Optional[float] = None,
        bg_color: Optional[str] = None,
        bg_transparency: Optional[float] = None,
        fontsize: Optional[float] = None,
        fontfactor: Optional[float] = None,
        fontfamily: Optional[str] = None,
    ):
        super().__init__(
            radius=radius,
            padding=padding,
            gap_size=gap_size,
            ribbon_gap=ribbon_gap,
            ribbon_stiffness=ribbon_stiffness,
            arc_thickness=arc_thickness,
            bg_color=bg_color,
            bg_transparency=bg_transparency,
            fontsize=fontsize,
            fontfactor=fontfactor,
            fontfamily=fontfamily,
        )

    @field
    def radius(self) -> Union[int, float]:  # type: ignore
        """Radius of the Chord plot."""

    @field
    def padding(self) -> Union[int, float]:  # type: ignore
        """Padding to apply around the Chord plot."""

    @field
    def gap_size(self) -> float:  # type: ignore
        """Gap size between the nodes in the Chord plot."""

    @field
    def ribbon_gap(self) -> float:  # type: ignore
        """Gap size between the outside arc (circle) and ribbons."""

    @field
    def ribbon_stiffness(self) -> float:  # type: ignore
        """Tweaks the curvature of the ribbons (0.0 straight, 1.0 delayed curve)."""

    @field
    def arc_thickness(self) -> float:  # type: ignore
        """Thickness of the outside arc (circle)."""

    @field
    def bg_color(self) -> str:  # type: ignore
        """Background color of the Chord plot."""

    @field
    def bg_transparency(self) -> float:  # type: ignore
        """Background color transparency of the Chord plot."""

    @field
    def fontsize(self) -> Union[int, float]:  # type: ignore
        """Chord plot font size."""

    @field
    def fontfactor(self) -> float:  # type: ignore
        """Font factor to calculate the padding with."""

    @field
    def fontfamily(self) -> str:  # type: ignore
        """Chord plot font family."""


class Style(Mapping):
    """RaGraph plot style mapping.

    Arguments:
        convention: Convention to use when drawing edges.
        boxsize: Size in pixels per row or column.
        config: Plotly Figure.show() config.
        highlight_annotation: Annotation key of instances that should be highlighted.
            Value should be True-ish. Set key to `None` to disable.
        highlight_color: Default color to use for highlights.
        labels: Labels plot style.
        layout: Layout options.
        palettes: Plot palettes options.
        piemap: Piechart map plot style.
        tree: Tree plot style.
        legend: Legend plot style.
        show_legend: Bool to display legend.
        chord: Chord plot style.
        row_col_numbers: Bool to display row and column numbers.
        xstep: Axis increment per row or column in plots (usually 1).
        ystep: Axis increment per row or column in plots (usually 1).
    """

    _defaults = dict(
        convention=Convention.IR_FAD,
        boxsize=20,
        config=dict(
            displaylogo=False,
            modeBarButtonsToRemove=list(
                MODEBAR_BUTTONS - {"resetScale2d", "toImage", "toggleSpikelines"}
            ),
            responsive=False,
            scrollZoom=False,
        ),
        highlight_annotation="highlight",
        highlight_color="rgba(130, 163, 254, 0.25)",
        labels=LabelsStyle(),
        layout=go.Layout(
            autosize=False,
            margin=go.layout.Margin(l=0, r=0, b=0, t=25, pad=0),
            modebar=dict(orientation="h"),
            hovermode="closest",
            paper_bgcolor="rgba(256,256,256,1)",
            plot_bgcolor="rgba(256,256,256,0)",
        ),
        palettes=Palettes(),
        piemap=PieMapStyle(),
        tree=TreeStyle(),
        legend=LegendStyle(),
        show_legend=True,
        chord=ChordStyle(),
        row_col_numbers=True,
        xstep=1,
        ystep=1,
    )

    def __init__(
        self,
        convention: Optional[Convention] = None,
        boxsize: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None,
        highlight_annotation: Optional[str] = None,
        highlight_color: Optional[str] = None,
        labels: Optional[Union[LabelsStyle, Dict[str, Any]]] = None,
        layout: Optional[Union[go.Layout, Dict[str, Any]]] = None,
        palettes: Optional[Palettes] = None,
        piemap: Optional[Union[PieMapStyle, Dict[str, Any]]] = None,
        tree: Optional[Union[TreeStyle, Dict[str, Any]]] = None,
        legend: Optional[Union[LegendStyle, Dict[str, Any]]] = None,
        show_legend: Optional[bool] = None,
        chord: Optional[Union[ChordStyle, Dict[str, Any]]] = None,
        row_col_numbers: Optional[bool] = None,
        xstep: Optional[str] = None,
        ystep: Optional[str] = None,
    ):
        super().__init__(
            convention=convention,
            boxsize=boxsize,
            config=config,
            highlight_annotation=highlight_annotation,
            highlight_color=highlight_color,
            labels=labels,
            layout=layout,
            palettes=palettes,
            piemap=piemap,
            tree=tree,
            legend=legend,
            show_legend=show_legend,
            chord=chord,
            row_col_numbers=row_col_numbers,
            xstep=xstep,
            ystep=ystep,
        )

    @field
    def convention(self) -> Convention:  # type: ignore
        """Convention to use when drawing edges."""

    @field
    def boxsize(self) -> int:  # type: ignore
        """Size in pixels per row or column."""

    @field
    def config(self) -> Dict[str, Any]:  # type: ignore
        """Plotly Figure.show() config."""

    @field
    def highlight_annotation(self) -> Optional[str]:  # type: ignore
        """Annotation key of instances that should be highlighted.
        Value should be True-ish. Set key to `None` to disable."""

    @field
    def highlight_color(self) -> str:  # type: ignore
        """Default color to use for highlights."""

    @field
    def labels(self) -> LabelsStyle:  # type: ignore
        """Labels plot style."""

    @field
    def layout(self) -> go.Layout:  # type: ignore
        """Layout options."""

    @field
    def palettes(self) -> Palettes:  # type: ignore
        """Plot palettes options."""

    @field
    def piemap(self) -> PieMapStyle:  # type: ignore
        """Piechart map plot style."""

    @field
    def tree(self) -> TreeStyle:  # type: ignore
        """Tree plot style."""

    @field
    def legend(self) -> LegendStyle:  # type: ignore
        """Legend plot style."""

    @field
    def show_legend(self) -> bool:  # type: ignore
        """Boolean to display a legend."""

    @field
    def chord(self) -> ChordStyle:  # type: ignore
        """Chord plot style."""

    @field
    def row_col_numbers(self) -> bool:  # type: ignore
        """Boolean to display row and column numbers."""

    @field
    def xstep(self) -> float:  # type: ignore
        """Axis increment per row or column in plots (usually 1)."""

    @field
    def ystep(self) -> float:  # type: ignore
        """Axis increment per row or column in plots (usually 1)."""


class Component(Mapping):
    """Plot component. The basic building block to create compound Plotly figures with.

    Arguments:
        width: Width in pixels.
        height: Height in pixels.
        traces: Traces to plot in this domain.
        shapes: SVG shapes from this component.
        xaxis: Plotly X-axis options.
        yaxis: Plotly Y-axis options.
    """

    _defaults: Dict[str, Any] = dict(
        width=0.0,
        height=0.0,
        traces=[],
        shapes=[],
        annotations=[],
        xaxis=go.layout.XAxis(),
        yaxis=go.layout.YAxis(),
    )

    def __init__(
        self,
        width: Optional[float] = None,
        height: Optional[float] = None,
        traces: Optional[List[BaseTraceType]] = None,
        shapes: Optional[List[Dict[str, Any]]] = None,
        annotations: Optional[List[Dict[str, Any]]] = None,
        xaxis: Optional[Union[go.layout.XAxis, Dict[str, Any]]] = None,
        yaxis: Optional[Union[go.layout.YAxis, Dict[str, Any]]] = None,
    ):
        if isinstance(xaxis, dict):
            _xaxis = deepcopy(self._defaults["xaxis"])
            for k, v in xaxis.items():
                setattr(_xaxis, k, v)
            xaxis = _xaxis

        if isinstance(yaxis, dict):
            _yaxis = deepcopy(self._defaults["yaxis"])
            for k, v in yaxis.items():
                setattr(_yaxis, k, v)
            yaxis = _yaxis

        super().__init__(
            width=width,
            height=height,
            traces=traces,
            shapes=shapes,
            annotations=annotations,
            xaxis=xaxis,
            yaxis=yaxis,
        )

    @field
    def width(self) -> float:  # type: ignore
        """Width in pixels."""

    @field
    def height(self) -> float:  # type: ignore
        """Height in pixels."""

    @field
    def traces(self) -> List[BaseTraceType]:  # type: ignore
        """Traces to plot in this domain."""

    @field
    def shapes(self) -> List[Dict[str, Any]]:  # type: ignore
        """SVG shapes from this component."""

    @field
    def annotations(self) -> List[Dict[str, Any]]:  # type: ignore
        """Annotations from this component."""

    @field
    def xaxis(self) -> go.layout.XAxis:  # type: ignore
        """Plotly X-axis options."""

    @field
    def yaxis(self) -> go.layout.YAxis:  # type: ignore
        """Plotly Y-axis options."""

    def get_figure(self, style: Style = Style(), show: bool = True) -> Optional[go.Figure]:
        """Get a Plotly figure of this component alone."""
        from ragraph.plot.utils import get_subplots, process_fig

        fig = get_subplots([[self]], style=style)
        return process_fig(fig, style=style, show=show)
