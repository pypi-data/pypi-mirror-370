"""# Delta analysis"""

from typing import Type

from ragraph.analysis.comparison.utils import (
    EdgeDescriptor,
    EdgeDescriptorLike,
    NodeDescriptor,
    NodeDescriptorLike,
    TagMode,
    tag,
)
from ragraph.graph import Graph


def delta_graph(
    graph_a: Graph,
    graph_b: Graph,
    delta_a: str = "delta_a",
    delta_b: str = "delta_b",
    common: str = "common",
    tag_mode: TagMode = TagMode.KIND,
    node_descriptor: Type[NodeDescriptorLike] = NodeDescriptor,
    edge_descriptor: Type[EdgeDescriptorLike] = EdgeDescriptor,
) -> Graph:
    """Get the delta graph between two graphs.

    Arguments:
        graph_a: First graph to compare.
        graph_b: Second graph to compare.
        delta_a: Name for nodes and edges unique to the first graph.
        delta_b: Name for nodes and edges unique to the second graph.
        common: Name for the common nodes and edges occurring in both graphs.

    Note:
        Graphs are compared on leaf node level and compared by name only.
        Please provide appropriate input as such and look to
        [`get_graph_slice`][ragraph.graph.Graph.get_graph_slice] for example on how to obtain a
        subgraph to your liking.
    """
    graph = Graph(name="delta", kind="delta")

    # Compare leaf nodes by name. Set to unique A first and change to common if found again.
    nds_a = set(node_descriptor.from_node(n) for n in graph_a.leafs)
    nds_b = set(node_descriptor.from_node(n) for n in graph_b.leafs)
    for n in nds_a.difference(nds_b):
        node = n.to_node(graph)
        tag(node, delta_a, tag_mode)
    for n in nds_b.difference(nds_a):
        node = n.to_node(graph)
        tag(node, delta_b, tag_mode)
    for n in nds_a.intersection(nds_b):
        node = n.to_node(graph)
        tag(node, common, tag_mode)

    # Compare edges between the nodes in the newly created graph.
    eds_a = set(
        edge_descriptor.from_edge(e)
        for e in graph_a.edges_between_all(graph_a.leafs, graph_a.leafs, inherit=False, loops=True)
    )
    eds_b = set(
        edge_descriptor.from_edge(e)
        for e in graph_b.edges_between_all(graph_b.leafs, graph_b.leafs, inherit=False, loops=True)
    )
    for e in eds_a.difference(eds_b):
        edge = e.to_edge(graph)
        tag(edge, delta_a, tag_mode)
    for e in eds_b.difference(eds_a):
        edge = e.to_edge(graph)
        tag(edge, delta_b, tag_mode)
    for e in eds_a.intersection(eds_b):
        edge = e.to_edge(graph)
        tag(edge, common, tag_mode)

    return graph
