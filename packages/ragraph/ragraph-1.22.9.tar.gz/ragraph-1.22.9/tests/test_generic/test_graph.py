"""Tests for generic.py module."""

import numpy as np
import pytest

from ragraph.datasets import esl
from ragraph.graph import ConsistencyError, Edge, Graph, Node


def test_empty_graph(empty_graph, a, b):
    assert empty_graph.node_count == 0, "empty_graph shouldn't have nodes."
    assert empty_graph.edge_count == 0, "empty_graph shouldn't have edges."
    assert list(empty_graph.edges_between(a, b)) == []
    assert list(empty_graph.edges_between_all([a], [b])) == []


def test_create_graph_ab(graph_ab):
    assert graph_ab.node_count == 2, "graph_ab should have 2 nodes."
    assert graph_ab.edge_count == 1, "graph_ab should have 1 edge."

    assert set(graph_ab.edges) == set(graph_ab.edges_from(graph_ab["a"]))

    assert set(graph_ab.edges) == set(graph_ab.edges_to(graph_ab["b"]))

    assert {graph_ab["b"]} == set(graph_ab.targets_of(graph_ab["a"]))

    assert {graph_ab["a"]} == set(graph_ab.sources_of(graph_ab["b"]))


def test_add_incorrect_node():
    with pytest.raises(TypeError):
        Graph(nodes=[1])

    with pytest.raises(ValueError):
        Graph(nodes=[Node("a"), Node("a")])


def test_add_incorrect_edge(graph_ab):
    c = Node("c")
    a = graph_ab["a"]
    with pytest.raises(ValueError) as e:
        graph_ab.add_edge(Edge(c, a))
    assert str(e.value) == "Source node {} does not exist in graph.".format(repr(c))

    with pytest.raises(ValueError) as e:
        graph_ab.add_edge(Edge(a, c))
    assert str(e.value) == "Target node {} does not exist in graph.".format(repr(c))


def test_add_dupe_edge(graph_ab):  # Has initial a->b edge.
    e = Edge(graph_ab["b"], graph_ab["a"])
    graph_ab.add_edge(e)
    graph_ab.add_edge(e)
    assert graph_ab.edge_count == 2, "Dupe edge should only be added once."


def test_delete_ab_nodes(graph_ab):
    a = graph_ab["a"]
    b = graph_ab["b"]
    graph_ab.del_node("a")
    graph_ab.del_node(b)
    assert graph_ab.nodes == []
    assert not graph_ab[a.name, b.name]
    assert graph_ab.max_depth == 0


def test_delete_ba_nodes(graph_ab):
    a = graph_ab["a"]
    b = graph_ab["b"]
    graph_ab.del_node(b)
    graph_ab.del_node("a")
    assert graph_ab.nodes == []
    assert not graph_ab[a.name, b.name]
    assert graph_ab.max_depth == 0


def test_delete_ab_edge(graph_ab):
    edge = graph_ab.edges[0]
    graph_ab.del_edge(edge)
    assert graph_ab.edges == []
    assert list(graph_ab.edges_from("a")) == []
    assert list(graph_ab.edges_to("b")) == []


def test_deletes_rich_a(rich_graph):
    rich_graph.del_node("a")
    assert rich_graph["c"].parent is None


def test_deletes_rich_c(rich_graph):
    c = rich_graph["c"]
    rich_graph.del_node(c)
    assert c not in rich_graph["a"].children


def test_rich_graph_properties(rich_graph):
    assert rich_graph.node_kinds == ["node", "rich", "wealthy"]
    assert rich_graph.edge_kinds == ["edge", "money"]
    assert rich_graph.get_nodes_by_kind("rich") == [rich_graph["c"]]
    assert rich_graph.get_edges_by_kind("money") == rich_graph["c", "d"]
    assert rich_graph.node_weight_labels == ["default", "dollars", "euros"]
    assert rich_graph.edge_weight_labels == ["default", "dollars"]
    assert rich_graph.edge_labels == ["default", "euros"]
    assert rich_graph.roots == rich_graph.node_list[:2]  # a, b
    assert rich_graph.leafs == rich_graph.node_list[1:]  # b, c, d
    assert rich_graph.max_depth == 1
    assert list(rich_graph.edges_between_all(["c"], ["d"])) == rich_graph["c", "d"]
    assert rich_graph.get_hierarchy_dict() == {"a": {"c": {}, "d": {}}, "b": {}}
    assert rich_graph.check_consistency(raise_error=False)
    assert rich_graph.get_hierarchy_dict(levels=0) == {"a": {}, "b": {}}


def test_get_graph_slice(rich_graph):
    gslice = rich_graph.get_graph_slice(nodes=rich_graph.nodes[:2])
    assert gslice.node_count == 2
    assert gslice.edge_count == 1

    gslice = rich_graph.get_graph_slice(nodes=[rich_graph["a"], rich_graph["c"]])
    assert gslice["c"].parent == gslice["a"]


def test_no_edges_from(graph_ab):
    assert list(graph_ab.edges_from(graph_ab["b"])) == [], "Should be no edges from 'b'."


def test_inconsistency_recursion(graph_ab):
    a = graph_ab["a"]
    b = graph_ab["b"]
    a.parent = b
    b.parent = a
    with pytest.raises(ConsistencyError) as e:
        graph_ab.check_consistency()
    assert str(e.value) == "Node {} is in its own ancestors.".format(a)

    a._parent = None
    with pytest.raises(ConsistencyError) as e:
        graph_ab.check_consistency()
    assert str(e.value) == "Node {} is in its own descendants.".format(a)


def test_inconsistency_parent(graph_ab, c):
    a = graph_ab["a"]
    b = graph_ab["b"]

    a._parent = c
    with pytest.raises(ConsistencyError) as e:
        graph_ab.check_consistency()
    assert str(e.value) == "Node {}'s parent {} is missing in the graph.".format(a, c)

    c._children = []
    graph_ab.add_node(c)
    with pytest.raises(ConsistencyError) as e:
        graph_ab.check_consistency()
    assert str(e.value) == "Node {}'s does not occur in parent {}'s children.".format(a, c)

    c._children = [a, b]
    b._parent = None
    with pytest.raises(ConsistencyError) as e:
        graph_ab.check_consistency()
    assert str(e.value) == "Node {}'s child has a different parent {}.".format(c, b.parent)
    b._parent = c

    c._is_bus = True
    with pytest.raises(ConsistencyError) as e:
        graph_ab.check_consistency()
    assert str(e.value) == "Node {} is a bus node, but has no parent to be it for.".format(c)

    graph_ab._nodes.pop("a")
    with pytest.raises(ConsistencyError) as e:
        graph_ab.check_consistency()
    assert str(e.value) == "Node {}'s child {} is missing in the graph.".format(c, a)


def test_art_empty_graph(empty_graph):
    with pytest.raises(ValueError) as e:
        empty_graph.get_ascii_art()
    assert str(e.value) == "Empty graph, cannot create ASCII art."


def test_art_graph_ab(graph_ab, capsys):
    art = graph_ab.get_ascii_art(show=False)
    ref = """ ┌───┬───┐
a┥ ■ │   │
 ├───┼───┤
b┥ X │ ■ │
 └───┴───┘"""
    assert art == ref

    graph_ab.get_ascii_art(show=True)
    captured = capsys.readouterr()
    assert captured.out == art + "\n"

    a = graph_ab["a"]
    art = graph_ab.get_ascii_art(nodes=[a], show=False)
    ref = """ ┌───┐
a┥ ■ │
 └───┘"""
    assert art == ref


def test_adj_graph_ab(graph_ab):
    adj = graph_ab.get_adjacency_matrix()

    mat = [[0.0, 0.0], [1.0, 0.0]]
    if np:
        assert (adj == np.array(mat)).all()
    else:
        assert adj == mat


def test_matrices_rich_graph(rich_graph: Graph):
    b = rich_graph["b"]
    e = Node("e", parent=b)
    rich_graph.add_node(e)
    c = rich_graph["c"]  # Child of a.

    # Add an edge between children of a and b
    rich_graph.add_edge(Edge(c, e, weights=dict(default=5)))

    # Add a self loop to b
    rich_graph.add_edge(Edge(b, b, weights=dict(default=3)))

    gam = rich_graph.get_adjacency_matrix
    roots = rich_graph.roots

    assert (gam(roots, inherit=False, loops=False) == np.array([[0.0, 0.0], [1.0, 0.0]])).all()
    assert (gam(roots, inherit=True, loops=False) == np.array([[0.0, 0.0], [6.0, 0.0]])).all()
    assert (gam(roots, inherit=True, loops=True) == np.array([[1.0, 0.0], [6.0, 3.0]])).all()
    assert (gam(roots, inherit=False, loops=True) == np.array([[0.0, 0.0], [1.0, 3.0]])).all()
    assert (
        gam(roots, inherit=True, loops=True, only=["dollars"]) == np.array([[1.0, 0.0], [0.0, 0.0]])
    ).all()
    gmm = rich_graph.get_mapping_matrix
    assert np.all(gmm(roots, roots) == gam(roots))
    assert (gmm(rows=["e"], cols=["c", "d"]) == np.array([[5.0, 0.0]])).all()


def test_graph_indexing(rich_graph):
    assert rich_graph["a"] == rich_graph["a"]
    assert rich_graph["a", "b"] == rich_graph["a", "b"]
    with pytest.raises(TypeError) as e:
        rich_graph[{"q"}]
    assert "should be a node name" in str(e.value)


def test_graph_contains(rich_graph):
    assert "a" in rich_graph
    assert ("a", "b") in rich_graph
    assert "dummy" not in rich_graph
    with pytest.raises(TypeError) as e:
        {"q"} in rich_graph
    assert "should be a node name" in str(e.value)


def test_del_node_inherit(a, b, c, d, e, f):
    a.children = [b, c, d]
    d.children = [e, f]
    g = Graph(nodes=[a, b, c, d, e, f])
    g.del_node(d, inherit=True)
    assert a.children == [b, c, e, f]


def test_graph_get_node_and_edge_selection():
    g = esl.get("pump")

    # Dependent selection
    nodes, edges = g.get_node_and_edge_selection(
        node_kinds=["component", "function_spec", "variable"],
        edge_kinds=["functional_dependency", "mapping_dependency"],
        depth=2,
        selection_mode="dependent",
    )

    # Check selected nodes.
    assert sorted([node.name for node in nodes]) == [
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor-control-signal",
        "world.drive-mechanism.motor.convert-power",
        "world.drive-mechanism.power",
        "world.drive-mechanism.power-potential",
        "world.drive-mechanism.power-source",
        "world.drive-mechanism.power-source.convert-potential",
        "world.drive-mechanism.power-switch",
        "world.drive-mechanism.provide-power",
        "world.drive-mechanism.send-control-signal",
        "world.provide-torque",
        "world.pump",
        "world.pump-length",
        "world.pump.convert-torque",
        "world.torque",
        "world.water-flow",
    ]

    # Check sources of selected edges of kind functional_dependency.
    assert sorted([edge.source.name for edge in edges if edge.kind == "functional_dependency"]) == [
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor.convert-power",
        "world.drive-mechanism.power",
        "world.drive-mechanism.power-potential",
        "world.drive-mechanism.power-source",
        "world.drive-mechanism.power-source",
        "world.drive-mechanism.power-source",
        "world.drive-mechanism.power-source.convert-potential",
        "world.drive-mechanism.power-switch",
        "world.drive-mechanism.provide-power",
        "world.provide-torque",
        "world.pump",
        "world.pump",
        "world.pump",
        "world.torque",
    ]

    # Check targets of selected edges of kind functional_dependency
    assert sorted([edge.target.name for edge in edges if edge.kind == "functional_dependency"]) == [
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor.convert-power",
        "world.drive-mechanism.power",
        "world.drive-mechanism.power-source",
        "world.drive-mechanism.power-source",
        "world.drive-mechanism.power-source",
        "world.drive-mechanism.power-switch",
        "world.drive-mechanism.provide-power",
        "world.provide-torque",
        "world.pump",
        "world.pump",
        "world.pump",
        "world.pump.convert-torque",
        "world.torque",
        "world.water-flow",
    ]

    # Check sources of selected edges of kind mapping_dependency.
    assert sorted([edge.source.name for edge in edges if edge.kind == "mapping_dependency"]) == [
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor",
        "world.drive-mechanism.motor.convert-power",
        "world.drive-mechanism.motor.convert-power",
        "world.drive-mechanism.power-source",
        "world.drive-mechanism.power-source",
        "world.drive-mechanism.power-source",
        "world.drive-mechanism.power-source",
        "world.drive-mechanism.power-source",
        "world.drive-mechanism.power-source.convert-potential",
        "world.drive-mechanism.power-source.convert-potential",
        "world.drive-mechanism.power-switch",
        "world.drive-mechanism.power-switch",
        "world.drive-mechanism.provide-power",
        "world.drive-mechanism.send-control-signal",
        "world.provide-torque",
        "world.pump",
        "world.pump",
        "world.pump",
        "world.pump",
        "world.pump",
        "world.pump",
        "world.pump.convert-torque",
        "world.pump.convert-torque",
    ]

    # Check targets of selected edges of kind mapping_dependency
    assert sorted([edge.target.name for edge in edges if edge.kind == "mapping_dependency"]) == [
        "world.drive-mechanism.motor-control-signal",
        "world.drive-mechanism.motor-control-signal",
        "world.drive-mechanism.motor-control-signal",
        "world.drive-mechanism.motor.convert-power",
        "world.drive-mechanism.power",
        "world.drive-mechanism.power",
        "world.drive-mechanism.power",
        "world.drive-mechanism.power",
        "world.drive-mechanism.power",
        "world.drive-mechanism.power",
        "world.drive-mechanism.power",
        "world.drive-mechanism.power-potential",
        "world.drive-mechanism.power-potential",
        "world.drive-mechanism.power-source.convert-potential",
        "world.drive-mechanism.provide-power",
        "world.drive-mechanism.provide-power",
        "world.drive-mechanism.send-control-signal",
        "world.drive-mechanism.send-control-signal",
        "world.provide-torque",
        "world.provide-torque",
        "world.pump-length",
        "world.pump.convert-torque",
        "world.torque",
        "world.torque",
        "world.torque",
        "world.torque",
        "world.torque",
        "world.torque",
        "world.torque",
        "world.water-flow",
        "world.water-flow",
    ]

    # Check if no other edge kinds are selected.
    assert set([e.kind for e in edges]) == {
        "functional_dependency",
        "mapping_dependency",
    }

    # Check selected nodes based on different depth and selection mode.
    nodes, edges = g.get_node_and_edge_selection(
        node_kinds=["component", "function_spec", "variable"],
        edge_kinds=["functional_dependency", "mapping_dependency"],
        depth=1,
        selection_mode="independent",
    )

    assert sorted([node.name for node in nodes]) == [
        "world.drive-length",
        "world.drive-mechanism",
        "world.drive-mechanism.convert-power-potential",
        "world.drive-mechanism.motor-control-signal",
        "world.drive-mechanism.motor.conversion",
        "world.drive-mechanism.motor.convert-power",
        "world.drive-mechanism.power",
        "world.drive-mechanism.power-potential",
        "world.drive-mechanism.power-source.convert-potential",
        "world.drive-mechanism.provide-power",
        "world.drive-mechanism.send-control-signal",
        "world.provide-torque",
        "world.pump",
        "world.pump-length",
        "world.pump.convert-torque",
        "world.torque",
        "world.water-flow",
    ]
