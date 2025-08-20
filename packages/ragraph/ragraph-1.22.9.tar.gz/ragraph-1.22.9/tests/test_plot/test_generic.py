"""Tests for the plot generic module."""

from plotly import graph_objs as go
from ragraph.plot import generic


def test_treestyle():
    foo = generic.TreeStyle(xaxis=dict(showgrid=True), yaxis=dict(zeroline=True))
    assert isinstance(foo.xaxis, go.layout.XAxis)

    assert foo.xaxis.showgrid
    assert foo.yaxis.zeroline

    assert not foo.xaxis.showline
    assert not foo.yaxis.showline

    assert foo.line.color == "gray"


def test_labelsstyle():
    foo = generic.LabelsStyle(
        xaxis=dict(automargin=True), yaxis=dict(autorange=False), fontfamily="Arial"
    )

    assert foo.xaxis.automargin
    assert foo.yaxis == foo._defaults["yaxis"]

    assert foo.fontfamily == "Arial"


def test_piemapstyle():
    foo = generic.PieMapStyle(
        xaxis=dict(automargin=True), yaxis=dict(scaleratio=0.5), mode="relative"
    )

    assert foo.xaxis.automargin
    assert foo.yaxis.scaleratio == 0.5
    assert foo.mode == "relative"
    assert foo.display == "kinds"


def test_legendstyle():
    foo = generic.LegendStyle(height=7, n_ticks=3)
    assert foo.height == 7
    assert foo.n_ticks == 3


def test_palettes():
    foo = generic.Palettes()
    assert len(foo.categorical) == 10
    assert len(foo.continuous) == 256
    assert isinstance(foo.fields, dict)
    assert isinstance(foo.domains, dict)


def test_style():
    from ragraph.generic import Mapping

    foo = generic.Style()

    assert isinstance(foo.piemap, Mapping)


def test_component():
    from plotly import graph_objs as go

    foo = generic.Component(
        xaxis=dict(zeroline=False), yaxis=dict(automargin=False), width=10, height=10
    )

    assert not foo.xaxis.zeroline
    assert not foo.yaxis.automargin

    assert isinstance(foo.get_figure(show=False), go.Figure)
