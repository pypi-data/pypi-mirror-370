"""Tests for edge.py"""

import pytest
from ragraph.edge import Edge
from ragraph.node import Node


@pytest.fixture
def rich_edge():
    source = Node("source")
    target = Node("target")
    return Edge(
        source,
        target,
        name="rich edge",
        kind="rich",
        labels=["money", "mucho"],
        weights=dict(dollars=1, euros=0.5),
        annotations=dict(foo="bar"),
    )


def test_edge_properties(rich_edge):
    assert rich_edge.source.name == "source"
    assert rich_edge.target.name == "target"
    assert rich_edge.kind == "rich"
    assert rich_edge.labels == ["money", "mucho"]
    assert rich_edge.weights == dict(dollars=1, euros=0.5)
    assert rich_edge.weight == 1.5
    assert rich_edge.annotations.foo == "bar"


def test_edge_instantiations():
    assert Edge("test", "test", kind=None).kind == "default", "Default edge kind should be 'edge'."

    assert (
        Edge("test", "test", annotations=dict(a=1)).annotations.a == 1
    ), "Edge annotations should accept a dict as argument."


def test_edge_representation(rich_edge):
    assert str(rich_edge) == "Edge(source='source', target='target', name='rich edge')"
    non_id = repr(rich_edge).split(", uuid=")[0]
    assert non_id == (
        "<ragraph.edge.Edge(source=Node(name='source'), target=Node(name='target'), "
        + "name='rich edge', kind='rich', labels=['money', 'mucho'], "
        + "weights={'dollars': 1, 'euros': 0.5}, "
        + "annotations=Annotations({'foo': 'bar'})"
    )
