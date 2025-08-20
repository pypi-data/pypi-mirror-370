"""Markov clustering tests."""

import numpy as np
from ragraph.analysis import cluster
from ragraph.analysis.cluster._markov import MarkovFlow
from ragraph.graph import Graph


def test_markov_flow():
    matrix = np.array([[0.0, 0.0], [1.0, 0.0]])

    mf = MarkovFlow(matrix, 2.0, False)
    assert mf.dim == 2
    assert mf.sink_matrix.tolist() == [
        [0.0, 0.0, 0.0],
        [0.5, 0.0, 0.0],
        [0.5, 1.0, 0.0],
    ]
    assert mf.sensitivity_matrix.tolist() == [
        [1.0, 0.0, 0.0],
        [0.5, 1.0, 0.0],
        [1.0, 1.0, 1.0],
    ]
    assert mf.in_vector.flatten().tolist() == [1.0, 1.0, 0.0]
    assert mf.flow_vector.flatten().tolist() == [1.0, 1.5, 2.0]
    assert mf.flow_matrix.tolist() == [
        [0.0, 0.0, 0.0],
        [0.5, 0.0, 0.0],
        [0.5, 1.5, 0.0],
    ]


def test_markov_defaults(graph: Graph):
    notinplace, _ = cluster.markov(graph, inplace=False)
    cluster.markov(graph)
    assert graph.get_hierarchy_dict() == {
        "f": {},
        "node.node0": {"a": {}, "b": {}, "c": {}, "d": {}, "e": {}},
    }
    assert notinplace.get_hierarchy_dict() == graph.get_hierarchy_dict()


def test_hierarchical_markov_defaults(graph: Graph):
    ref = {
        "f": {},
        "node.node2": {
            "node.node0": {"a": {}, "b": {}},
            "node.node1": {"c": {}, "d": {}, "e": {}},
        },
    }
    notinplace, _ = cluster.hierarchical_markov(graph, beta=4.0, mu=6.0, inplace=False)
    assert notinplace.get_hierarchy_dict() == ref
    cluster.hierarchical_markov(graph, beta=4.0, mu=6.0)
    value = graph.get_hierarchy_dict()
    assert value == ref


def test_single_node_edge(graph: Graph):
    assert cluster.markov(graph, leafs=["a"], names=True)[1] == ["a"]
    assert cluster.hierarchical_markov(graph, leafs=["a"], names=True)[1] == ["a"]


def test_cluster_markov_cases(case: Graph):
    cluster.markov(case)


def test_cluster_hierarchical_markov_cases(case: Graph):
    cluster.hierarchical_markov(case)


def test_hierarchical_markov_paper_case(paper: Graph):
    graph, roots = cluster.hierarchical_markov(paper, alpha=2, beta=3.0, mu=3.0, inplace=False)
    assert graph
