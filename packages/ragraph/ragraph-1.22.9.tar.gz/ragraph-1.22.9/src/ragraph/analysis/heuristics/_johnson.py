"""# Donald B. Johnson's nested circuit finding algorithm"""

from collections import defaultdict
from typing import Dict, Generator, List, Optional, Set, Union

from ragraph.analysis.cluster._tarjan import tarjans_scc_algorithm
from ragraph.graph import Graph
from ragraph.node import Node


def johnson(
    graph: Graph,
    nodes: Optional[List[Node]] = None,
    names: bool = False,
    inherit: bool = True,
    **kwargs,
) -> Generator[Union[List[str], List[Node]], None, None]:
    """Donald B. Johnson's nested circuit finding algorithm. A circuit is a cycle in a
    graph, circuits can overlap or contain duplicate parts.

    Arguments:
        graph: Graph to find circuits in.
        nodes: Nodes to consider during circuit search.
        inherit: Whether to take into account (inherit) edges between children during
            SCC calculations.

    Yields:
        Node circuit lists.

    Note:
        Cannot cluster a graph directly since circuits may overlap in all sorts of ways.
        Therefore, it gives you cluster-related information, but no clear hierarchy.

    Reference:
        Johnson, D. B. (1975). Finding all the elementary circuits of a directed graph.
            In SIAM J. COMPUT (Vol. 4). https://doi.org/10.1137/0204007
    """
    if not nodes:
        nodes = graph.leafs

    # Keep original nodes around for node remapping, get a working copy for the algo.
    translation = {n.name: n for n in nodes}
    graph = graph.get_graph_slice(nodes, inherit=inherit)

    def _unblock(node: Node, blocked: Set[Node], B: Dict[Node, Set[Node]]):
        stack = set([node])
        while stack:
            node = stack.pop()
            if node in blocked:
                blocked.remove(node)
                stack.update(B[node])
                B[node].clear()

    # List of Lists of strongly connected nodes
    sccs = tarjans_scc_algorithm(graph, nodes=graph.roots, inherit=inherit)
    while sccs:
        scc = sccs.pop()
        startnode = scc.pop()
        path = [startnode]
        blocked = set()
        closed = set()
        blocked.add(startnode)
        B: Dict[Node, Set[Node]] = defaultdict(set)
        stack = [(startnode, list(graph.targets_of(startnode)))]
        while stack:
            node, targets = stack[-1]
            if targets:
                target = targets.pop()
                if target == startnode:
                    if names:
                        yield [translation[n.name].name for n in path]  # Original names
                    else:
                        yield [translation[n.name] for n in path]  # Original nodes
                    closed.update(path)
                elif target not in blocked:
                    path.append(target)
                    stack.append((target, list(graph.targets_of(target))))
                    closed.discard(target)
                    blocked.add(target)
                    continue
            else:
                if node in closed:
                    _unblock(node, blocked, B)
                else:
                    for target in graph.targets_of(node):
                        if node not in B[target]:
                            B[target].add(node)
                stack.pop()
                path.pop()
        graph.del_node(node)
        sccs.extend(tarjans_scc_algorithm(graph, scc, inherit))
