"""Tests for generic Metadata."""

from ragraph import datasets
from ragraph.generic import Bound, MetadataFilter


def test_metadata_filter(rich_graph):
    empty = MetadataFilter()
    assert not empty.get_checks(), "No settings means no checks."
    assert empty.filter(rich_graph.node_list) == rich_graph.node_list

    node_kinds = MetadataFilter(kinds={"node", "rich"})
    assert len(node_kinds.get_checks()) == 1
    assert [n.name for n in node_kinds.filter(rich_graph.node_list)] == ["a", "b", "c"]

    edge_labels_annots = MetadataFilter(labels={"money", "us"}, annotations={"comment"})
    assert len(edge_labels_annots.get_checks()) == 2
    assert [e.name for e in edge_labels_annots.filter(rich_graph.edge_list)] == []


def test_metadata_weights_filter():
    g = datasets.get("climate_control")
    mf = MetadataFilter(
        weight_domains=dict(spatial=(Bound(-2, inclusive=True), Bound(0, inclusive=False)))
    )
    assert mf.filter(g.edges) == []
