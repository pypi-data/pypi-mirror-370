"""Gamma bus detection module tests."""

from ragraph import datasets
from ragraph.analysis import bus
from ragraph.analysis._utils import create_parent
from ragraph.analysis.bus import gamma
from ragraph.graph import Edge, Graph


def test_bus_gamma_basic(parent_graph: Graph):
    bus_leafs, nonbus_leafs = gamma(
        parent_graph, root=parent_graph.roots[0].name, gamma=2.0, names=True
    )
    detected = set(bus_leafs)
    expected = {"e"}
    assert (
        detected == expected
    ), "{} should be the detected bus node for gamma 2.0, found {}.".format(expected, detected)

    bus_leafs, nonbus_leafs = gamma(
        parent_graph, root=parent_graph.roots[0].name, gamma=1.5, names=True
    )
    detected = set(bus_leafs)
    expected = {"a", "e"}
    assert (
        detected == expected
    ), "{} should be the detected bus nodes for gamma 1.5, found {}.".format(expected, detected)


def test_bus_gamma_no_bus_below_3_nodes(graph: Graph):
    bus_leafs, nonbus_leafs = gamma(graph, root="a", gamma=2.0)
    assert not bus_leafs, "There can never be bus nodes below 3 nodes."


def test_bus_gamma_no_bus(parent_graph: Graph):
    # Remove all edges.
    parent_graph.edges = []

    # No buses
    bus_leafs, nonbus_leafs = gamma(parent_graph, root=parent_graph.roots[0].name, gamma=2.0)
    assert not bus_leafs, "There can never be bus nodes if there are no edges."

    # "All bus nodes" -> no bus
    for i in parent_graph.node_list:
        for j in parent_graph.node_list:
            if i != j:
                parent_graph.add_edge(Edge(i, j))
    bus_leafs, nonbus_leafs = gamma(parent_graph, root=parent_graph.roots[0].name, gamma=1.0)
    assert not bus_leafs, "If all nodes are detected as bus, actually none should be."


def test_bus_gamma_climate_control():
    g = datasets.get("climate_control")
    r = create_parent(g, g.nodes)
    b, nb = bus.gamma(g, root=r.name, gamma=2.1, names=True)
    assert set(b) == {"Command Distribution"}


def test_bus_gamma_cases(case: Graph):
    r = create_parent(case, case.leafs)
    bus.gamma(case, root=r.name, gamma=2.0)
