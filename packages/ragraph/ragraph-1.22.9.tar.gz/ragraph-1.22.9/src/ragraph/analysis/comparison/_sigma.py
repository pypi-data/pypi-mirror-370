"""# Sigma analysis"""

import enum
from copy import deepcopy
from typing import TYPE_CHECKING, Iterable

from ragraph.edge import Edge
from ragraph.generic import Metadata
from ragraph.graph import Graph
from ragraph.node import Node

try:
    StrEnum = enum.StrEnum
except Exception:
    from strenum import StrEnum  # type: ignore
finally:
    if TYPE_CHECKING:
        StrEnum = enum.StrEnum


class SigmaMode(StrEnum):
    """Aggregation mode for sigma analysis, absolute counted occurrences or an average per graph."""

    ABSOLUTE = enum.auto()
    AVERAGE = enum.auto()


def sigma_graph(
    graphs: Iterable[Graph], count_prefix: str = "sigma", mode: SigmaMode = SigmaMode.ABSOLUTE
) -> Graph:
    """Get the sigma (summed) graph based on the leaf nodes and the edges in multiple graphs.

    Arguments:
        graphs: Graphs to sum and count edge occurrences in.
        mode: Whether to count absolute occurrence values or an average per graph.
        count_prefix: Which weight key (prefix) to store the occurrence values under. Also used as
            a prefix for label counts that are stored as weights using as well.

    Note:
        Summations are done over (leaf) node names. Edges in an input graph are aggregated first
        using the [`add_meta` method][ragraph.analysis.comparison.add_meta]
        before being aggregated into the resulting graph.
    """
    accumulator = Graph(name="sigma")
    num = 0
    for graph in graphs:
        # Override that first one's results because of default values for a Graph.
        add_graph(accumulator, graph, count_prefix, num == 0)
        num += 1
    if mode == SigmaMode.AVERAGE and num > 0:
        div = 1.0 / num
        for k, v in accumulator.weights.items():
            if k.startswith(f"{count_prefix}_") or k == count_prefix:
                accumulator.weights[k] = div * v
        for n in accumulator.nodes:
            for k, v in n.weights.items():
                if k.startswith(f"{count_prefix}_") or k == count_prefix:
                    n.weights[k] = div * v
        for e in accumulator.edges:
            for k, v in e.weights.items():
                if k.startswith(f"{count_prefix}_") or k == count_prefix:
                    e.weights[k] = div * v
    return accumulator


def add_graph(accumulator: Graph, item: Graph, count_prefix: str, is_first: bool = False) -> Graph:
    """Add a graph to an accumulator graph. Occurrences are counted under the 'count_prefix'."""
    add_meta(accumulator, item, count_prefix, is_first=is_first)
    add_nodes(accumulator, item, count_prefix)
    add_edges(accumulator, item, count_prefix)
    return accumulator


def add_meta(accumulator: Metadata, item: Metadata, count_prefix: str, is_first: bool = False):
    """Add metadata of another item to the accumulator in-place. Annotations are updated and the
    last observed value for any key is kept. Occurrence value is tracked under the 'count_prefix'.
    """
    if is_first:
        initialize_meta(accumulator, item, count_prefix)
    else:
        increment_meta(accumulator, item, count_prefix)


def initialize_meta(accumulator: Metadata, item: Metadata, count_prefix: str):
    """Initialize an accumulator instance with the info from the first item."""
    accumulator.kind = item.kind
    accumulator.labels = deepcopy(item.labels)
    accumulator.weights = deepcopy(item.weights)
    accumulator.weights[count_prefix] = 1
    for label in item.labels:
        k = f"{count_prefix}_label_{label}"
        accumulator.weights[k] = item.weights.get(k, 1)
    accumulator.annotations = deepcopy(item.annotations)


def increment_meta(accumulator: Metadata, item: Metadata, count_prefix: str):
    """Increment the occurrence and label counts as weights in the accumulator with an item."""
    if accumulator.kind != item.kind:
        raise ValueError(f"kinds don't match: '{accumulator.kind}' and '{item.kind}'")

    # Update labels to superset.
    accumulator.labels = sorted(set(accumulator.labels + item.labels))

    # Sum weights
    for k, v in item.weights.items():
        accumulator.weights[k] = accumulator.weights.get(k, 0) + v
    accumulator.annotations.update(item.annotations)

    if count_prefix in item.weights:
        pass  # Is already incremented when summing weights above.
    else:
        accumulator.weights[count_prefix] = accumulator.weights.get(count_prefix, 0) + 1

    # Increment label counts.
    for label in item.labels:
        k = f"{count_prefix}_label_{label}"
        if k in item.weights:
            continue  # Is already summed with weights.
        accumulator.weights[k] = accumulator.weights.get(k, 0) + 1


def add_nodes(accumulator: Graph, item: Graph, count_prefix: str):
    """Add observed nodes in item to the accumulator in-place and keep track of an occurrence count.

    Based on node names.

    Metadata for existing nodes is added using
    [`add_meta` method][ragraph.analysis.comparison.add_meta].
    """
    for n in item.leafs:
        try:
            add_meta(accumulator[n.name], n, count_prefix)
        except KeyError:
            node = Node(name=n.name)
            add_meta(node, n, count_prefix, is_first=True)
            accumulator.add_node(node)


def add_edges(accumulator: Graph, item: Graph, count_prefix: str):
    """Add observed edges in item to the accumulator in-place.

    Based on node names.

    Metadata for existing nodes is added using
    [`add_meta` method][ragraph.analysis.comparison.add_meta].
    """
    for source_name, tgt_map in item.directed_edges.items():
        for target_name, item_edges in tgt_map.items():
            # Take a deepcopy of the list of edges in the item and aggregate those first.
            item_edges = deepcopy(item_edges)
            item_edge = item_edges.pop()
            for e in item_edges:
                add_meta(item_edge, e, count_prefix)

            # Now check whether we already accumulated something here, or add a new entry.
            edges = accumulator.directed_edges[source_name][target_name]
            if len(edges):
                add_meta(edges[0], item_edge, count_prefix)
            else:
                source_node = accumulator.node_dict[source_name]
                target_node = accumulator.node_dict[target_name]
                edge = Edge(source_node, target_node)
                add_meta(edge, item_edge, count_prefix, is_first=True)
                accumulator.add_edge(edge)
