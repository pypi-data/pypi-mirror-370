"""Sort nodes in a typical axis-ready format."""

from textwrap import dedent
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from ragraph.analysis._classes import Cast, Parameter, SequenceAnalysis
from ragraph.graph import Graph
from ragraph.node import Node


class KindsCast(Cast):
    def __init__(self, **kwargs):
        pass

    def __call__(self, value: Any) -> Optional[List[str]]:
        if value is None:
            return None
        elif not isinstance(value, list):
            raise ValueError(f"Node kind order should be a list, got '{value}'.")
        else:
            return value


axis_sequencing_analysis = SequenceAnalysis(
    "Plot axis sequencing. Get nodes in a plot-axis-ready order.",
    description=dedent(
        """Order nodes for a typical display on matrix plot axis. They are sorted by:
          1. Node kinds in order of (supplied) occurrence.
          2. Top-down hierarchy.
          3. Optional: Bus-nodes before nonbus-nodes in w.r.t. siblings.
          4. Optional: Node width (e.g. size in terms of leaf nodes).

        Note:
            Axis ready means ordered by kind and buses nodes first where possible.

        Note:
            `inherit`, `loops`, and `edge_weights` are ignored for this analysis.

        Warning:
            When supplying node kinds it's your own responsibility to make sure that each node's
            kind actually is included in that node kind order.
        """
    ),
    parameters={
        "kinds": Parameter(
            "kinds",
            Optional[List[str]],
            description="Optional order of node kinds.",
            cast=KindsCast(),
            default=None,
        ),
        "sort_by_bus": Parameter(
            "sort_by_bus",
            bool,
            description="Whether to put bus nodes first.",
            cast=bool,
            default=True,
        ),
        "sort_by_width": Parameter(
            "sort_by_width",
            bool,
            description="Whether to sort nodes by width in terms of leaf nodes.",
            cast=bool,
            default=True,
        ),
    },
)


def get_axis_sequence(
    nodes: Iterable[Node],
    kinds: Optional[List[str]] = None,
    sort_by_bus: bool = True,
    sort_by_width: bool = True,
    root_cache: Optional[Dict[Node, Node]] = None,
    child_cache: Optional[Dict[Node, List[Node]]] = None,
    width_cache: Optional[Dict[Node, int]] = None,
) -> List[Node]:
    """Get nodes in a plot-axis-ready order.

    Arguments:
        nodes: Axis nodes to order.
        kinds: Optional order of node kinds.
        sort_by_bus: Whether to put bus nodes first.
        sort_by_width: Whether to sort nodes by width in terms of leaf nodes.
        root_cache: Node to resulting root node cache. Any supplied dictionary
            will be updated in-place.
        child_cache: Node to child nodes that have been seen cache.
        width_cache: Node to node width cache.

    Returns:
        Ordered nodes.

    Note:
        Axis ready means ordered by kind and buses nodes first where possible.
        Any supplied cache dictionary will be updated in-place.

    Warning:
        When supplying node kinds it's your own responsibility to make sure
        that each node's kind actually is included in that node kind order.
    """
    root_cache = dict() if root_cache is None else root_cache
    child_cache = dict() if child_cache is None else child_cache
    width_cache = dict() if width_cache is None else width_cache

    kinds = get_kinds(nodes) if kinds is None else kinds
    kind_order = {kind: position for position, kind in enumerate(kinds)}

    roots = get_roots(nodes, root_cache, child_cache)
    roots.sort(key=lambda x: get_root_key(x, kind_order, sort_by_width, width_cache))

    # Sort by is_bus status with buses first, width second, if applicable.
    if sort_by_bus or sort_by_width:
        for parent in child_cache.keys():
            child_cache[parent].sort(
                key=lambda x: get_sibling_key(x, sort_by_bus, sort_by_width, width_cache)
            )

    # Complement width_cache for roots for completeness sake.
    if sort_by_width:
        for root in roots:
            width_cache[root] = sum(
                width_cache.get(child, 1) for child in child_cache.get(root, [])
            )

    leafs = [leaf for root in roots for leaf in get_leafs(root, child_cache)]
    return leafs


def get_root(
    node: Node,
    root_cache: Optional[Dict[Node, Node]] = None,
    child_cache: Optional[Dict[Node, List[Node]]] = None,
) -> Node:
    """Get root node of a node.

    Arguments:
        node: Nodes to find corresponding root nodes for.
        root_cache: Node to resulting root node cache. Any supplied dictionary
            will be updated in-place.
        child_cache: Node to child nodes that have been seen cache. Any supplied
            dictionary will be updated in-place.

    Returns:
        Root node.

    Note:
        Supply cache dictionaries to store intermediate results.
    """

    # Cache from any seen node to the resulting root node.
    root_cache = dict() if root_cache is None else root_cache

    # Cache from any parent we came across to the included children in the search.
    child_cache = dict() if child_cache is None else child_cache

    # Cached, return cache value.
    if node in root_cache:
        return root_cache[node]

    # Is a root, return.
    if node.parent is None:
        return node

    # Find and update caches accordingly.
    if node.parent not in child_cache:
        child_cache[node.parent] = [node]
    else:
        child_cache[node.parent].append(node)
    root = get_root(node.parent, root_cache, child_cache)
    root_cache[node] = root

    return root


def get_roots(
    nodes: Iterable[Node],
    root_cache: Optional[Dict[Node, Node]] = None,
    child_cache: Optional[Dict[Node, List[Node]]] = None,
) -> List[Node]:
    """Get list of root nodes corresponding to some collection of nodes.

    Arguments:
        nodes: Collection of nodes to find corresponding root nodes for.
        root_cache: Node to resulting root node cache. Any supplied dictionary
            will be updated in-place.
        child_cache: Node to child nodes that have been seen cache. Any supplied
            dictionary will be updated in-place.

    Returns:
        Root nodes.

    Note:
        Supply cache dictionaries to store intermediate results.
    """
    # Cache from any seen node to the resulting root node.
    root_cache = dict() if root_cache is None else root_cache

    # Cache from any parent we came across to the included children in the search.
    child_cache = dict() if child_cache is None else child_cache

    seen = set()  # Seen root nodes.
    ordered = []  # Seen root nodes in order of appearance.
    for node in nodes:
        root = get_root(node, root_cache, child_cache)
        if root not in seen:
            seen.add(root)
            ordered.append(root)
    return ordered


def get_kinds(nodes: Iterable[Node]) -> List[str]:
    """Get node kinds in order of occurrence.

    Arguments:
        nodes: Nodes to iterate over.

    Returns:
        List of Node kinds.
    """
    ordered = []
    seen = set()
    for node in nodes:
        kind = node.kind
        if kind not in seen:
            ordered.append(kind)
            seen.add(kind)
    return ordered


def get_leafs(parent: Node, child_cache: Dict[Node, List[Node]]) -> List[Node]:
    """Get leaf nodes from a linked-list style child_cache (e.g. parent to children).

    Arguments:
        parent: Parent node.
        child_cache: Linked-list style parent-children dictionary.

    Returns:
        Displayed leaf nodes as they occur under this parent.
    """
    # Handle the case where this node is actually a leaf node.
    if parent not in child_cache:
        return [parent]

    # Fetch leaf nodes from deeper into the cached hierarchy.
    leafs = []
    for child in child_cache[parent]:
        leafs.extend(get_leafs(child, child_cache))
    return leafs


def get_width(node: Node, width_cache: Optional[Dict[Node, int]] = None) -> int:
    """Get width of a node and update width cache in-place.

    Arguments:
        node: Node to get the width of.
        width_cache: Node to node width cache.

    Returns:
        Node width.
    """
    width_cache = dict() if width_cache is None else width_cache
    if node not in width_cache:
        if node.children:
            width_cache[node] = sum(get_width(child, width_cache) for child in node.children)
        else:
            width_cache[node] = 1
    return width_cache[node]


def get_root_key(
    node: Node,
    kind_order: Dict[str, int],
    sort_by_width: bool,
    width_cache: Optional[Dict[Node, int]] = None,
) -> Union[int, Tuple[int, int]]:
    """Calculate a sorting score for root nodes.

    Arguments:
        node: Root node to obtain a score for.
        kind_order: Node kind to position dictionary.
        sort_by_width: Whether to sort nodes by width in terms of leaf nodes.
        width_cache: Node to node width cache.

    Returns:
        Root node sorting key.

    Note:
        Sort by kinds first, width in terms of actual (not display) leaf nodes second.
    """
    if sort_by_width:
        return (
            kind_order[node.kind],
            -get_width(node, width_cache),
        )
    else:
        return kind_order[node.kind]


def get_sibling_key(
    node: Node,
    sort_by_bus: bool,
    sort_by_width: bool,
    width_cache: Optional[Dict[Node, int]] = None,
) -> Union[int, Tuple[int, int]]:
    """Calculate a sorting score for sibling nodes. Lower scores go first.

    Arguments:
        node: Node to score.
        sort_by_bus: Whether to put bus nodes first.
        sort_by_width: Whether to sort nodes by width in terms of leaf nodes.
        width_cache: Dictionary of nodes to displayed children.

    Returns:
        Sibling node sorting score.

    Note:
        Bus nodes first, width in terms of actual (not display) leaf nodes second."""
    if sort_by_bus and sort_by_width:
        return (not node.is_bus, -get_width(node, width_cache))
    elif sort_by_bus:
        return not node.is_bus
    elif sort_by_width:
        return -get_width(node, width_cache)
    else:
        return 0


@axis_sequencing_analysis
def axis(
    graph: Graph,
    root: Optional[Union[str, Node]] = None,
    nodes: Optional[Union[List[Node], List[str]]] = None,
    kinds: Optional[List[str]] = None,
    sort_by_bus: bool = True,
    sort_by_width: bool = True,
    edge_weights: Optional[List[str]] = None,
    inherit: bool = True,
    loops: bool = False,
    inplace: bool = True,
    names: bool = False,
    safe: bool = True,
    **kwargs,
):
    """docstring stub"""
    seq = get_axis_sequence(nodes, kinds, sort_by_bus, sort_by_width)  # type: ignore
    return graph, seq
