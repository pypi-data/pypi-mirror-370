"""Tests for the plot components module."""

import json

import pytest
from plotly import graph_objs as go

from ragraph import datasets
from ragraph.datasets import get
from ragraph.plot import components
from ragraph.plot.generic import Style


@pytest.fixture
def leafs():
    g = datasets.get("climate_control")

    leafs = sorted(g.leafs, key=lambda x: x.name)
    return leafs


@pytest.fixture
def edges():
    g = datasets.get("climate_control")
    edges = g.edges
    return edges


def test_labels(leafs, tmpdir, datadir, check_diff):
    labels = components.Labels(leafs=leafs)
    fname = "labels_test_expected.json"

    d = labels.as_dict()
    data = dict(width=d["width"], height=d["height"], annotations=d["annotations"])
    (tmpdir / fname).write_text(
        json.dumps(data, sort_keys=True, indent=2),
        encoding="utf-8",
    )

    check_diff(tmpdir / fname, datadir / "json" / fname, sort=True)


def test_empty_labels():
    components.Labels(leafs=[])


def test_tree(leafs):
    tree = components.Tree(leafs=leafs)
    assert tree.as_dict() == {
        "width": 20,
        "height": 320,
        "annotations": [],
        "traces": [
            go.Scatter(
                {
                    "customdata": [
                        {"data": "Accumulator", "pointtype": "tree_node"},
                        {"data": "Actuators", "pointtype": "tree_node"},
                        {"data": "Air Controls", "pointtype": "tree_node"},
                        {"data": "Blower Controller", "pointtype": "tree_node"},
                        {"data": "Blower Motor", "pointtype": "tree_node"},
                        {"data": "Command Distribution", "pointtype": "tree_node"},
                        {"data": "Compressor", "pointtype": "tree_node"},
                        {"data": "Condenser", "pointtype": "tree_node"},
                        {"data": "Engine Fan", "pointtype": "tree_node"},
                        {"data": "Evaporator Case", "pointtype": "tree_node"},
                        {"data": "Evaporator Core", "pointtype": "tree_node"},
                        {"data": "Heater Core", "pointtype": "tree_node"},
                        {"data": "Heater Hoses", "pointtype": "tree_node"},
                        {"data": "Radiator", "pointtype": "tree_node"},
                        {"data": "Refrigeration Controls", "pointtype": "tree_node"},
                        {"data": "Sensors", "pointtype": "tree_node"},
                    ],
                    "hoverinfo": "text",
                    "marker": {"color": "gray"},
                    "mode": "markers",
                    "showlegend": False,
                    "text": [
                        "Accumulator",
                        "Actuators",
                        "Air Controls",
                        "Blower Controller",
                        "Blower Motor",
                        "Command Distribution",
                        "Compressor",
                        "Condenser",
                        "Engine Fan",
                        "Evaporator Case",
                        "Evaporator Core",
                        "Heater Core",
                        "Heater Hoses",
                        "Radiator",
                        "Refrigeration Controls",
                        "Sensors",
                    ],
                    "x": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "y": [
                        15.5,
                        14.5,
                        13.5,
                        12.5,
                        11.5,
                        10.5,
                        9.5,
                        8.5,
                        7.5,
                        6.5,
                        5.5,
                        4.5,
                        3.5,
                        2.5,
                        1.5,
                        0.5,
                    ],
                }
            )
        ],
        "shapes": [],
        "xaxis": go.layout.XAxis(
            {
                "automargin": False,
                "autorange": False,
                "range": [-0.5, 0.5],
                "scaleanchor": "y",
                "scaleratio": 1.0,
                "showgrid": False,
                "showline": False,
                "showticklabels": False,
                "zeroline": False,
            }
        ),
        "yaxis": go.layout.YAxis(
            {
                "automargin": False,
                "autorange": False,
                "range": [0, 16.0],
                "scaleanchor": "x",
                "scaleratio": 1.0,
                "showgrid": True,
                "showline": False,
                "showticklabels": False,
                "zeroline": False,
            }
        ),
    }


def test_legend(update):
    g = get("elevator45")

    # Categorical legend.
    style = Style(
        piemap=dict(
            display="labels",
            mode="relative",
        ),
    )

    legend = components.Legend(edges=g.edges, style=style)

    assert legend.as_dict() == {
        "width": 34.412,
        "height": 100,
        "annotations": [],
        "traces": [
            go.Scatter(
                {
                    "hoverinfo": "text",
                    "marker": {"color": "#6a9ffc"},
                    "mode": "markers",
                    "showlegend": False,
                    "text": ["EE"],
                    "x": [0.5],
                    "y": [4.5],
                }
            ),
            go.Scatter(
                {
                    "hoverinfo": "text",
                    "marker": {"color": "#f27663"},
                    "mode": "markers",
                    "showlegend": False,
                    "text": ["ME"],
                    "x": [0.5],
                    "y": [3.5],
                }
            ),
            go.Scatter(
                {
                    "hoverinfo": "text",
                    "marker": {"color": "#56c950"},
                    "mode": "markers",
                    "showlegend": False,
                    "text": ["i"],
                    "x": [0.5],
                    "y": [2.5],
                }
            ),
            go.Scatter(
                {
                    "hoverinfo": "text",
                    "marker": {"color": "#a57fff"},
                    "mode": "markers",
                    "showlegend": False,
                    "text": ["m"],
                    "x": [0.5],
                    "y": [1.5],
                }
            ),
            go.Scatter(
                {
                    "hoverinfo": "text",
                    "marker": {"color": "#c89336"},
                    "mode": "markers",
                    "showlegend": False,
                    "text": ["s"],
                    "x": [0.5],
                    "y": [0.5],
                }
            ),
            go.Scatter(
                {
                    "hoverinfo": "text",
                    "mode": "text",
                    "showlegend": False,
                    "text": ["EE", "ME", "i", "m", "s"],
                    "textfont": {
                        "color": "black",
                        "family": "Fira Code,Hack,Courier New,monospace",
                        "size": 12,
                    },
                    "textposition": "middle right",
                    "x": [1.0, 1.0, 1.0, 1.0, 1.0],
                    "y": [4.5, 3.5, 2.5, 1.5, 0.5],
                }
            ),
        ],
        "shapes": [],
        "xaxis": go.layout.XAxis(
            {
                "automargin": False,
                "range": [0, 1.7206],
                "scaleanchor": "y",
                "showgrid": False,
                "showline": False,
                "showticklabels": False,
                "zeroline": False,
            }
        ),
        "yaxis": go.layout.YAxis(
            {
                "automargin": False,
                "autorange": False,
                "range": [0, 6],
                "scaleratio": 1.0,
                "showgrid": False,
                "showline": False,
                "showticklabels": False,
                "zeroline": False,
            }
        ),
    }

    # Numerical legend.
    style = Style(
        piemap=dict(
            display="weights",
            mode="relative",
            fields=["sum"],
        ),
        legend=dict(height=10),
    )

    legend = components.Legend(edges=g.edges, style=style)

    assert legend.width == 50
    assert legend.height == 200


def test_piemap(leafs, edges):
    piemap = components.PieMap(rows=leafs, cols=leafs, edges=edges)
    assert len(piemap.traces) == len(edges)
    assert len(piemap.shapes) >= len(edges)
