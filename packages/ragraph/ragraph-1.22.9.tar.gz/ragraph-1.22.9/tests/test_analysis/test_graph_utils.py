"""Tests for _utils module."""

from copy import deepcopy

import pytest
from ragraph.analysis._utils import (
    clear_local_hierarchy,
    create_parent,
    get_available_name,
    inherit_edges,
    set_children,
    unset_parent,
)
from ragraph.graph import Graph, Node


def test_create_parent(graph: Graph):
    children = [graph.node_dict["a"], graph.node_dict["b"]]
    parent = create_parent(graph, children, prefix="cluster", lower=0)

    assert list(parent.children) == children, "Children should match."

    for child in children:
        assert child.parent == parent, "Parent should be set for children."

    assert parent in graph.nodes, "Parent should be added to the graph."


def test_get_available_name():
    g = Graph()

    name0 = get_available_name(g, prefix="test", lower=0)
    assert name0 == "test0"
    g.add_node(Node(name0))

    name1 = get_available_name(g, prefix="test", lower=0)
    assert name1 == "test1"
    g.add_node(Node(name1))  # Should fail if name already exists.


def test_inherit_edges(graph: Graph):
    ab = create_parent(graph, children=["a", "b"], name="ab")
    cd = create_parent(graph, children=["c", "d"], name="cd")
    inherit_edges(graph, [ab, cd], ["e", "f"])

    assert graph["ab", "e"], "Edge ab-e should exist."

    assert graph["e", "ab"], "Edge e-ab should exist."


def test_set_children_empty(graph: Graph):
    parent = Node("node")
    set_children(graph, parent, [])
    assert not set(parent.children), "Parent shouldn't have children."


def test_set_children_ab(graph: Graph):
    a = graph.node_dict["a"]
    b = graph.node_dict["b"]

    parent = Node("node")
    set_children(graph, parent, [a, b])
    assert set(parent.children) == {a, b}, "Children should be set to {a,b}."


def test_set_children_self(graph: Graph):
    parent = Node("node")
    set_children(graph, parent, [parent])
    assert not set(parent.children), "Should not have changed children."


def test_set_children_single_leaf(graph: Graph):
    parent = Node("node")
    e = graph.node_dict["e"]
    with pytest.raises(ValueError) as excinfo:
        set_children(graph, parent, [e])
        assert "Cannot set a single leaf node as children." in str(excinfo.value)


def test_set_children_single_parent(graph: Graph):
    a = graph.node_dict["a"]
    b = graph.node_dict["b"]
    p0 = create_parent(graph, [a, b], name="p0")
    p1 = Node("p1")
    set_children(graph, p1, [p0])


def test_clear_local_hierarchy():
    a = Node("a")
    b = Node("b")
    c = Node("c")
    c.parent = b
    b.parent = a
    g = Graph([a, b, c])
    clear_local_hierarchy(g, [c], [a])
    assert {a, c} == set(g.nodes), "'b' should no longer be in nodes and 'a' and 'c' should"


def test_unset_parent():
    """Unsetting the parent of "a" in the following tree

           h
       ____|____
      |         |
      f         g
     _|_     ___|___
    |   |   |   |   |
    a   b   c   d   e

    leaves the following forest:

    a      h
       ____|____
      |         |
      b         g
             ___|___
            |   |   |
            c   d   e

    in which "a" has become a root and "b" has become a child of "h" since "f" has
    been removed.

    etc.
    """
    a = Node("a")
    b = Node("b")
    c = Node("c")
    d = Node("d")
    e = Node("e")
    f = Node("f")
    g = Node("g")
    h = Node("h")

    h.children = [f, g]
    f.children = [a, b]
    g.children = [c, d, e]

    graph = Graph(nodes=[a, b, c, d, e, f, g, h])
    graph.check_consistency()
    hierarchy = graph.get_hierarchy_dict

    unset_parent(graph, h)  # Should do nothing
    assert hierarchy() == {"h": {"f": {"a": {}, "b": {}}, "g": {"c": {}, "d": {}, "e": {}}}}

    unset_parent(graph, a)
    assert hierarchy() == {"a": {}, "h": {"b": {}, "g": {"c": {}, "d": {}, "e": {}}}}

    unset_parent(graph, c)
    assert hierarchy() == {"a": {}, "c": {}, "h": {"b": {}, "g": {"d": {}, "e": {}}}}

    unset_parent(graph, d)
    assert hierarchy() == {"a": {}, "c": {}, "d": {}, "h": {"b": {}, "e": {}}}

    unset_parent(graph, e)
    assert hierarchy() == {"a": {}, "b": {}, "c": {}, "d": {}, "e": {}}


def test_unset_parent_and_clear(hierarchy):
    """Clearing a local hierarchy with protected root versus unsetting every leaf's
    parent should result in the same hierarchy."""
    g1 = deepcopy(hierarchy)
    g2 = deepcopy(hierarchy)

    clear_local_hierarchy(g1, g1.leafs, roots=list(g1.roots))

    for leaf in g2.leafs:
        unset_parent(g2, leaf, roots=list(g2.roots))

    assert g1.get_hierarchy_dict() == g2.get_hierarchy_dict()
