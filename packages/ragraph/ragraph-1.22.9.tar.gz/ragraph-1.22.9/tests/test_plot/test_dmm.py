from pytest import mark
from ragraph import datasets
from ragraph.plot import dmm
from ragraph.plot.generic import Style


@mark.skip(reason="Dict comparision fails randomly.")
def test_dmm_0(check_plotly):
    g = datasets.get("climate_control")
    rows = g.leafs[0:5]
    cols = g.leafs
    fig = dmm(
        rows=rows,
        cols=cols,
        edges=[e for e in g.edges_between_all(sources=cols, targets=rows)],
    )

    fname = "dmm_0.json"
    check_plotly(fig, fname)


@mark.skip(reason="Dict comparision fails randomly.")
def test_dmm_1(check_plotly):
    g = datasets.get("climate_control")

    # Categorical plot of weight labels with custom colors
    rows = g.leafs
    cols = g.leafs[0:5]
    fig = dmm(
        rows=rows,
        cols=cols,
        edges=[e for e in g.edges_between_all(sources=cols, targets=rows)],
    )

    fname = "dmm_1.json"
    check_plotly(fig, fname)


@mark.skip(reason="Dict comparision fails randomly.")
def test_dmm_2(check_plotly):
    g = datasets.get("climate_control")

    # Categorical plot of weight labels with custom colors
    rows = g.leafs
    cols = g.leafs[0:5]
    fig = dmm(
        rows=rows,
        cols=cols,
        edges=[e for e in g.edges_between_all(sources=cols, targets=rows)],
        style=Style(row_col_numbers=False),
    )

    fname = "dmm_2.json"
    check_plotly(fig, fname)
