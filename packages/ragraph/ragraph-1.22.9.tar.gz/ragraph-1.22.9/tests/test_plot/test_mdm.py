from pathlib import Path

from pytest import mark
from ragraph import datasets
from ragraph.analysis.heuristics import markov_gamma
from ragraph.colors import get_cyan, get_green, get_purple, get_red
from ragraph.edge import Edge
from ragraph.node import Node
from ragraph.plot import mdm
from ragraph.plot.generic import Style

SHOW_FIGURES = True


@mark.skip(reason="Dict comparison fails randomly.")
def test_mdm_0(check_plotly):
    g = datasets.get("climate_control")

    # Categorical plot of weight labels with custom colors
    fig = mdm(
        leafs=g.leafs,
        edges=g.edges,
        style=Style(
            piemap={
                "display": "weight labels",
                "mode": "equal",
            },
            palettes={
                "fields": {
                    "spatial": "#d21404",
                    "energy flow": "#d7be69",
                    "information flow": "#ffa500",
                    "material flow": "#ffa500",
                }
            },
        ),
        sort=False,
    )

    fname = "categorical_plot_with_custom_colors.json"
    check_plotly(fig, fname)


@mark.skip(reason="Dict comparison fails randomly.")
def test_mdm_1(check_plotly):
    g = datasets.get("climate_control")

    # Numerical plot of weights with custom colors.
    fig = mdm(
        leafs=g.leafs,
        edges=g.edges,
        style=Style(
            piemap={
                "display": "weights",
                "mode": "equal",
            },
            palettes={
                "fields": {
                    "spatial": get_red(),
                    "energy flow": get_green(),
                    "information flow": get_cyan(),
                    "material flow": get_purple(),
                }
            },
        ),
        sort=False,
    )

    fname = "numerical_plot_with_custom_colors.json"
    check_plotly(fig, fname)


@mark.skip(reason="Dict comparision fails randomly.")
def test_mdm_2(check_plotly):
    g = datasets.get("climate_control")

    # Plot clustered matrix
    markov_gamma(g, alpha=2, beta=2.0, mu=2.0, gamma=2.0, local_buses=True)
    fig = mdm(
        leafs=g.leafs,
        edges=g.edges,
        style=Style(
            piemap={
                "display": "weight labels",
                "mode": "equal",
                "busarea": {"fillcolor": "#d21404"},
            },
        ),
        sort=True,
    )

    fname = "clustered_matrix_plot.json"
    check_plotly(fig, fname)


@mark.skip(reason="Dict comparision fails randomly.")
def test_mdm_3(check_plotly):
    # Plot matrix with more than 10 edge labels.
    nodes = [Node("A", kind="component"), Node("B", kind="component")]
    edges = [
        Edge(
            source=nodes[0],
            target=nodes[1],
            kind="functional_dependency",
            labels=[str(idx) for idx in range(12)],
        )
    ]

    fig = mdm(
        leafs=nodes,
        edges=edges,
        style=Style(piemap={"display": "labels", "mode": "relative"}),
        sort=False,
    )

    fname = "graph_with_more_than_10_edge_labels.json"
    check_plotly(fig, fname)


@mark.skip(reason="Dict comparision fails randomly.")
def test_mdm_4(check_plotly):
    g = datasets.get("aircraft_engine")

    # Plot clustered matrix
    markov_gamma(g, alpha=2, beta=2.0, mu=2.0, gamma=2.0, local_buses=True)
    fig = mdm(
        leafs=g.leafs,
        edges=g.edges,
        style=Style(
            piemap={
                "display": "weight labels",
                "mode": "equal",
            },
        ),
        sort=True,
    )

    fname = "aircraft_engine.json"
    check_plotly(fig, fname)


@mark.skip(reason="Dict comparision fails randomly.")
def test_mdm_5(check_plotly):
    g = datasets.get("climate_control")

    fig = mdm(
        leafs=g.leafs,
        edges=g.edges,
        style=Style(
            piemap={
                "display": "weight labels",
                "mode": "equal",
            },
            palettes={
                "fields": {
                    "spatial": "#d21404",
                    "energy flow": "#d7be69",
                    "information flow": "#ffa500",
                    "material flow": "#ffa500",
                }
            },
            row_col_numbers=False,
        ),
        sort=False,
    )

    fname = "mdm_no_row_col_numbers.json"
    check_plotly(fig, fname)


@mark.skip(reason="Dict comparision fails randomly.")
def test_mdm_6(check_plotly):
    from ragraph.generic import Annotations

    g = datasets.get("climate_control")

    num = [idx for idx in range(len(g.edges))]

    for idx, e in enumerate(g.edges):
        e.annotations = Annotations(blab=num[idx], blib=num[idx])

    fig = mdm(
        leafs=g.leafs,
        edges=g.edges,
        style=Style(
            piemap={
                "customhoverkeys": ["blib", "blab"],
            },
        ),
        sort=False,
    )

    fname = "mdm_custom_hover.json"
    check_plotly(fig, fname)


def test_highlight(tmpdir):
    g = datasets.get("climate_control_mg")
    g["Accumulator"].annotations.highlight = True
    fig = mdm(g.leafs, g.edges)
    fig.write_image(Path(tmpdir / "highlight.png"), format="png")

    g["Heater Core"].annotations.highlight = "red"
    fig = mdm(g.leafs, g.edges)
    fig.write_image(Path(tmpdir / "custom_highlight.png"), format="png")
