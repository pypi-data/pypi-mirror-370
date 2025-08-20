"""# RaGraph analysis utilities

Utility functions for managing the graph object during analysis.
"""

from copy import copy
from typing import Iterable, List, Optional, Union

from ragraph.graph import Graph
from ragraph.node import Node


def create_parent(
    graph: Graph,
    children: Union[List[Node], List[str]],
    prefix: str = "node",
    lower: int = 0,
    **node_kwargs,
) -> Node:
    """Add a parent node for given children to a given graph.

    Arguments:
        graph: Graph to create parent in.
        children: Children to add a parent node for.
        prefix: Parent name prefix, will be appended by first available integer.
        lower: Lower bound for integer to append to parent name prefix.
        kwargs:

    Returns:
        Created parent node.
    """
    if isinstance(children[0], str):
        parent_kind = graph.node_dict[children[0]].kind
    else:
        parent_kind = children[0].kind
    child_nodes = [
        graph.node_dict[child] if isinstance(child, str) else child for child in children
    ]
    if "name" not in node_kwargs:
        if parent_kind:
            prefix = ".".join([parent_kind, prefix])

        node_kwargs["name"] = get_available_name(graph, prefix, lower)
    parent = Node(kind=parent_kind, **node_kwargs)
    graph.add_node(parent)
    set_children(graph, parent, child_nodes)
    return parent


def get_available_name(graph: Graph, prefix: str, lower: int) -> str:
    """Get an available node name starting with prefix, appended the first integer
    that is free starting at lower.

    Arguments:
        graph: Graph to check availability in.
        prefix: Node name prefix, will be appended by first available integer.
        lower: Lower bound for integer to append to name prefix.

    Returns:
        First available node name not in [`graph.node_dict`][ragraph.graph.Graph.node_dict].
    """
    available = False
    i = lower
    while not available:
        name = prefix + str(i)
        available = name not in graph.node_dict
        i += 1

    return name


def inherit_edges(
    graph: Graph,
    new_parents: Iterable[Union[str, Node]],
    parent_siblings: Iterable[Union[str, Node]],
) -> None:
    """Let a cluster root nodes inherit all edges from their direct children
    (not descendants).

    Arguments:
        graph: Graph to work in.
        new_parents: New parent nodes to recreate edges for.
        parent_siblings: Already existing parent siblings.

    Note:
        Sometimes a clustering iteration does not introduce a new parent for every node,
        hence the distinction in parent nodes. New parent nodes look for edges from/to
        their children where old parent nodes already have edges (as this method has
        probably been called before). In general, it's better to wait with edge
        recreation until the graph's hierarchy is complete. Inserting and moving nodes
        half-way a tree would have way too many implications for the edges.
    """
    new_parent_nodes = [
        graph.node_dict[node] if isinstance(node, str) else node for node in new_parents
    ]
    parent_sibling_nodes = [
        graph.node_dict[node] if isinstance(node, str) else node for node in parent_siblings
    ]
    assert set(new_parent_nodes).isdisjoint(
        parent_sibling_nodes
    ), "There should be no overlap between new parents and siblings."

    for i in new_parent_nodes:
        for j in new_parent_nodes:
            if i == j:
                continue
            for child_edge_ij in graph.edges_between_all(i.children, j.children):
                edge_ij = copy(child_edge_ij)
                edge_ij.name = None  # type: ignore
                edge_ij.source = i
                edge_ij.target = j
                graph.add_edge(edge_ij)

    for i in new_parent_nodes:
        for j in parent_sibling_nodes:
            for child_edge_ij in graph.edges_between_all(i.children, [j]):
                edge_ij = copy(child_edge_ij)
                edge_ij.name = None  # type: ignore
                edge_ij.source = i
                edge_ij.target = j
                graph.add_edge(edge_ij)
            for child_edge_ji in graph.edges_between_all([j], i.children):
                edge_ji = copy(child_edge_ji)
                edge_ji.name = None  # type: ignore
                edge_ji.source = j
                edge_ji.target = i
                graph.add_edge(edge_ji)


def set_children(graph: Graph, parent: Node, children: List[Node]) -> None:
    """Safely set children of parent node.

    Arguments:
        graph: Graph to work in.
        parent: Parent node.
        children: Children to set.

    Note:
        If the children are attempted to be set to the parent itself, return.
        If children has length 1, the grandchildren are used and child is deleted.
        If children has length 1 and it is a leaf node, a ValueError is raised.
    """
    if not children:
        return

    if len(children) == 1:
        child = children[0]
        if parent == child:
            return
        if child.is_leaf:
            raise ValueError("Cannot set a single leaf node as children.")
        child.parent = parent
        graph.del_node(child, inherit=True)
        return

    for child in children:
        child.parent = parent


def unset_parent(graph: Graph, node: Node, roots: Optional[List[Node]] = None) -> None:
    """Clearing the parent of a node. Moves sole siblings upwards, replacing the parent.

    Arguments:
        graph: Graph to work in.
        node: The node of which the parent must be cleared.
        roots: Roots are protected nodes that are never deleted.

    Note:
        The node is has its parent unset and is therefore removed from the parent's
        children. The parent may have just a single other child left, in which case
        that child node should replace the parent altogether. When it has more children,
        it is kept intact.

    Example:
        Resetting the parent of "a" in the following tree:

        ```
               g
           ____|____
          |         |
          e         f
         _|_     ___|___
        |   |   |   |   |
        a   b   c   d   e
        ```

        leaves the following forest:

        ```
        a        g
             ____|____
            |         |
            b         f
                   ___|___
                  |   |   |
                  c   d   e
        ```

        in which "a" has become a root and "b" has become a child of "g" since "e" has
        been removed.
    """
    parent = node.parent
    if not parent:
        return
    roots = roots or []

    # Remove this node's parent and reset bus prop.
    node.parent = None
    node.is_bus = False

    # Move any potential sole children upwards if possible.
    if parent not in roots and len(parent.children) == 1:
        sole = parent.children[0]
        sole.is_bus = False
        grandparent = parent.parent
        if grandparent:
            # Move up to grandparent's children
            grandparent.children = grandparent.children + parent.children
        else:
            # Sole remaining child becomes a root as well.
            parent.children[0].parent = None
        graph.del_node(parent, inherit=False)


def clear_local_hierarchy(
    graph: Graph, leafs: List[Node], roots: Optional[List[Node]] = None
) -> None:
    """Strip a local hierarchy between a given root node and leaf nodes, removing all
    non-leaf nodes and setting the root as parent.

    Arguments:
        graph: Graph to strip nodes in.
        leafs: Lower bound leaf nodes to start from.
        root: Optional root nodes that are kept intact.
    """
    roots = roots or []
    for leaf in leafs:
        leaf.is_bus = False
        while leaf.parent:
            if leaf.parent in roots:
                leaf.parent = None
            else:
                graph.del_node(leaf.parent, inherit=True)
