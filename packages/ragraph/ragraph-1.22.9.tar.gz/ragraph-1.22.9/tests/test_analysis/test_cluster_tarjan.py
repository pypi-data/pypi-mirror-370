"""Tests for Tarjan's clustering algorithms module."""

from typing import List, Set

from ragraph.analysis import cluster
from ragraph.analysis.cluster._tarjan import (
    tarjans_scc,
    tarjans_scc_algorithm,
)
from ragraph.graph import Graph
from ragraph.node import Node


def test_tarjans_scc_algorithm(graph: Graph):
    sccs = tarjans_scc_algorithm(graph, graph.leafs, True)
    sets: List[Set[Node]] = [set(scc) for scc in sccs]

    assert sets == [
        set(graph.nodes[:-1]),
        set(graph.nodes[-1:]),
    ], "Sets should match predicted output ({a,b,c,d,e}, {f})."
    assert sccs[1] == [graph.node_dict["f"]], "Doublecheck f should be a single SCC."


def test_tarjans_scc_clustering(graph: Graph):
    notinplace, _ = tarjans_scc(graph, root=None, leafs=graph.leafs, edge_weights=[], inplace=False)
    tarjans_scc(graph, root=None, leafs=graph.leafs, edge_weights=[], inplace=True)
    assert graph.get_hierarchy_dict() == {
        "f": {},
        "node.node0": {"a": {}, "b": {}, "c": {}, "d": {}, "e": {}},
    }
    assert notinplace.get_hierarchy_dict() == graph.get_hierarchy_dict()


def test_tarjans_scc_cases(case: Graph):
    cluster.tarjans_scc(case)
