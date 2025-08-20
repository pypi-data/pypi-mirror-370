"""Tests for generic utils."""

import pytest
from ragraph import utils
from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node


@pytest.fixture
def depgraph():
    a = Node("a", kind="lead")
    b = Node("b", kind="lead")
    c = Node("c", kind="other")
    d = Node("d", kind="other")
    e = Node("e", kind="other")
    f = Node("f", kind="other")

    ac = Edge(a, c, kind="include")
    db = Edge(d, b, kind="include")
    ae = Edge(a, e, kind="exclude")
    fb = Edge(f, b, kind="exclude")

    g = Graph(nodes=[a, b, c, d, e, f], edges=[ac, db, ae, fb])
    return g


def test_is_dependent(depgraph: Graph):
    lead = [n for n in depgraph.nodes if n.kind == "lead"]
    other = [n for n in depgraph.nodes if n.kind == "other"]

    assert [utils.is_dependent(depgraph, lead, n, {"include"}) for n in other] == [
        True,
        True,
        False,
        False,
    ]


def test_get_up_to_depth(rich_graph: Graph):
    res = list(utils.get_up_to_depth([rich_graph["a"]], 0))
    assert res == [rich_graph["a"]]
    res = list(utils.get_up_to_depth([rich_graph["a"]], 1))
    assert res == [rich_graph[i] for i in ["c", "d"]]


def test_select_nodes(esl_graph: Graph):
    nodes = utils.select_nodes(
        esl_graph,
        ["component", "variable"],
        [],
        depth=1,
        selection_mode="dependent",
    )
    assert [n.name for n in nodes] == ["world.t", "world.q", "world.r"]

    nodes = utils.select_nodes(
        esl_graph,
        ["component", "variable_type"],
        [],
        depth=2,
        selection_mode="dependent",
    )
    assert [n.name for n in nodes] == ["world.t", "world.q"]

    nodes = utils.select_nodes(
        esl_graph,
        ["component", "variable_type"],
        [],
        depth=2,
        selection_mode="independent",
    )
    assert [n.name for n in nodes] == [
        "world.t",
        "world.q",
        "real",
        "integer",
        "string",
        "boolean",
    ]


def test_select_nodes_bad_mode(depgraph: Graph):
    with pytest.raises(ValueError) as e:
        utils.select_nodes(depgraph, [], [], depth=2, selection_mode="bad mode")
    assert "selection mode" in str(e.value)


def test_graph_get_node_selection(esl_graph):
    ures = utils.select_nodes(
        esl_graph,
        ["component", "variable_type"],
        [],
        depth=2,
        selection_mode="independent",
    )
    gres = esl_graph.get_node_selection(
        ["component", "variable_type"], [], depth=2, selection_mode="independent"
    )
    assert ures == gres
