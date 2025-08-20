"""# Graph handling utilities"""

from typing import TYPE_CHECKING, Generator, List, Set

if TYPE_CHECKING:
    from ragraph.graph import Graph
    from ragraph.node import Node


def select_nodes(
    graph: "Graph", node_kinds: List[str], edge_kinds: List[str], depth: int, selection_mode: str
) -> List["Node"]:
    """Select specific nodes from this graph in a structured order.

    Arguments:
        graph: Graph to fetch data from.
        node_kinds: The kind of nodes to be selected.
        edge_kinds: The kind of edges to be selected.
        depth: The maximum depth of node to be selected.
        selection_mode: The selection mode. Either 'dependent' or 'independent'.

    Note:
        The selection mode argument determines how nodes of different kinds are
        selected. If the selection mode is set to 'dependent', the first node kind
        in the `node_kinds` list is considered to be the 'lead node kind'.
        Nodes of different kind than the lead node kind, are only selected if they
        have a dependency with at least one of the selected nodes of the lead node
        kind. If the selection mode is set to 'independent' this dependency
        condition is dropped.
    """
    node_kinds = node_kinds or graph.node_kinds

    if selection_mode not in ["dependent", "independent"]:
        raise ValueError(
            f'Unrecognized selection mode "{selection_mode}", '
            'should be "independent" or "dependent".'
        )

    node_kind_order = {kind: i for i, kind in enumerate(node_kinds)}
    roots = sorted(
        [n for n in graph.roots if n.kind in node_kinds],
        key=lambda n: node_kind_order[n.kind],
    )

    nodes = list(get_up_to_depth(roots, depth))

    if selection_mode == "independent" or len(node_kinds) == 1:
        return nodes

    lead_kind = node_kinds[0]
    i = 0
    while i < len(nodes) and nodes[i].kind == lead_kind:
        i += 1
    lead_nodes, candidate_nodes = nodes[:i], nodes[i:]

    edge_kinds = edge_kinds or graph.edge_kinds
    edge_kindset = set(edge_kinds)
    dependent_nodes = [
        n for n in candidate_nodes if is_dependent(graph, lead_nodes, n, edge_kindset)
    ]

    return lead_nodes + dependent_nodes


def get_up_to_depth(roots: List["Node"], depth: int) -> Generator["Node", None, None]:
    """Get nodes up to a certain depth with bus nodes at the start of child lists."""
    for node in roots:
        if node.is_leaf or node.depth == depth:
            yield node
            continue

        children = sorted(node.children, key=lambda n: n.is_bus, reverse=True)

        if node.depth == depth - 1:
            yield from children
        else:
            yield from get_up_to_depth(children, depth)


def is_dependent(graph, lead_nodes: List["Node"], node: "Node", edge_kinds=Set[str]) -> bool:
    """Check if a node is dependent on the lead node kind.

    E.g. an edge of the allowed kinds exists to or from the lead nodes.
    """
    return any(
        True for e in graph.edges_between_all(lead_nodes, [node]) if e.kind in edge_kinds
    ) or any(True for e in graph.edges_between_all([node], lead_nodes) if e.kind in edge_kinds)
