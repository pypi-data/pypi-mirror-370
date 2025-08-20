"""Tests for node.py."""

import pytest

from ragraph.node import Node


@pytest.fixture
def rich_node():
    return Node(
        "rich",
        kind="wealthy",
        parent=Node("parent"),
        children=[Node("a"), Node("b", children=[Node("c")])],
        weights=dict(dollars=1, euros=0.5),
        annotations=dict(foo="bar"),
    )


def test_node_properties(rich_node):
    assert str(rich_node), "Should be able to get str()."
    assert repr(rich_node), "Should be able to get repr()."
    assert rich_node.name == "rich"
    assert rich_node.kind == "wealthy"
    assert rich_node.parent.name == "parent"
    assert [c.name for c in rich_node.children] == ["a", "b"]
    assert rich_node.weights == dict(dollars=1, euros=0.5)
    assert rich_node.weight == 1.5
    assert rich_node.annotations.foo == "bar"
    assert rich_node.ancestors == [rich_node.parent]
    assert rich_node.descendants == rich_node.children + rich_node.children[1].children
    assert rich_node.depth == 1
    assert rich_node.height == 2
    assert rich_node.width == 2
    assert not rich_node.is_leaf
    assert not rich_node.is_root

    rich_node.parent = None
    assert str(rich_node), "Should be able to get str() with empty parent."


def test_node_instantiations():
    assert Node(6).name == "6"

    assert Node("test", kind=None).kind == "default", "Node should have 'default' kind."

    assert (
        Node("test", annotations=dict(a=1)).annotations.a == 1
    ), "Node annotations should accept a dict as argument."

    with pytest.raises(TypeError) as e:
        Node("test", parent=5)
    assert str(e.value) == "Parent should be of type {}, got {}.".format(Node, int)

    with pytest.raises(ValueError) as e:
        Node("test", is_bus=True)
    assert str(e.value) == "Cannot be a bus without a parent to be it for. Set a parent first!"


def test_node_representation(rich_node):
    assert str(rich_node) == "Node(name='rich')"
    non_id = repr(rich_node).split(", uuid=")[0]
    ref = (
        "<ragraph.node.Node(name='rich', "
        + "parent='parent', children=[\"Node(name='a')\", \"Node(name='b')\"], "
        + "is_bus=False, kind='wealthy', labels=['default'], "
        + "weights={'dollars': 1, 'euros': 0.5}, "
        + "annotations=Annotations({'foo': 'bar'})"
    )
    assert non_id == ref


def test_node_hierarchy_changes(a, b, c, d, e, f):
    a.children = [b, c]
    assert a.children == [b, c]
    assert b.parent == a
    assert c.parent == a

    # Different way of adding children
    d.children = [e]
    f.parent = d
    assert d.children == [e, f]
    assert e.parent == d
    assert f.parent == d

    # Resetting parent of f
    f.parent = None
    assert d.children == [e]
    assert f.parent is None

    # Move children of a to f
    f.children = a.children
    assert b.parent == f
    assert c.parent == f
    assert a.children == []

    # Changing parent of b back to a
    b.parent = a
    assert f.children == [c]
    assert c.parent == f
    assert a.children == [b]
    assert b.parent == a
    assert b.parent == a
