from ragraph import datasets
from ragraph.analysis import heuristics
from ragraph.analysis.heuristics import markov_gamma
from ragraph.graph import Graph


def test_markov_gamma_global_bus(graph: Graph):
    markov_gamma(graph, alpha=2, beta=2.0, mu=2.0, gamma=2.0, local_buses=False)
    assert graph.check_consistency(raise_error=True)
    assert graph.get_hierarchy_dict() == {
        "f": {},
        "node.node0": {"d": {}, "e": {}, "node.node1": {"a": {}, "b": {}, "c": {}}},
    }
    assert [n.name for n in graph.nodes if n.is_bus] == ["e"]


def test_markov_gamma_local_bus(graph: Graph):
    notinplace, _ = markov_gamma(
        graph, alpha=2, beta=2.0, mu=2.0, gamma=2.0, local_buses=True, inplace=False
    )
    markov_gamma(graph, alpha=2, beta=2.0, mu=2.0, gamma=2.0, local_buses=True)

    assert graph.check_consistency(raise_error=True)
    assert graph.get_hierarchy_dict() == {
        "f": {},
        "node.node0": {"d": {}, "e": {}, "node.node1": {"a": {}, "b": {}, "c": {}}},
    }
    assert [n.name for n in graph.nodes if n.is_bus] == ["a", "e"]
    assert graph.get_hierarchy_dict() == notinplace.get_hierarchy_dict()


def test_markov_gamma_reproduceability():
    g = datasets.get("elevator175")

    markov_gamma(
        g,
        root=None,
        leafs=[n.name for n in g.leafs],
        alpha=2,
        beta=2.0,
        mu=2.0,
        gamma=2.0,
        inplace=True,
    )
    res1 = g.get_hierarchy_dict()

    markov_gamma(
        g,
        root=None,
        leafs=[n.name for n in g.leafs],
        alpha=2,
        beta=2.0,
        mu=2.0,
        gamma=2.0,
        inplace=True,
    )
    res2 = g.get_hierarchy_dict()

    assert res1 == res2

    g2, _ = markov_gamma(
        g,
        root=None,
        leafs=[n.name for n in g.leafs],
        alpha=2,
        beta=2.0,
        mu=2.0,
        gamma=2.0,
        inplace=False,
    )
    res3 = g2.get_hierarchy_dict()
    assert res3 == res1


def test_markov_gamma_single_node(graph: Graph):
    assert markov_gamma(graph, leafs=["a"], names=True)[1] == ["a"]


def test_markov_gamma_cases(case: Graph):
    heuristics.markov_gamma(case)
