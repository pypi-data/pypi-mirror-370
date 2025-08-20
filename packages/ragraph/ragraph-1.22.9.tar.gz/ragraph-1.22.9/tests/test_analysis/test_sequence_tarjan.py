import pytest
from ragraph.analysis import sequence
from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node


def test_dfs():
    a = Node("a")
    b = Node("b")
    c = Node("c")
    g = Graph(nodes=[a, b, c], edges=[Edge(a, c), Edge(a, b)])

    _, seq = sequence.tarjans_dfs(g, names=True)
    assert seq == ["a", "b", "c"]

    with pytest.raises(ValueError):
        g = Graph(nodes=[a, b], edges=[Edge(a, b), Edge(b, a)])  # Not a DAG.
        sequence.tarjans_dfs(g)


def test_dfs_chain(chain_graph):
    _, seq = sequence.tarjans_dfs(chain_graph, names=True)
    assert seq == ["4", "3", "2", "1", "0"]


def test_dfs_cases(case: Graph):
    try:
        sequence.tarjans_dfs(case)
    except ValueError as e:
        if str(e) == "Not a Directed Acyclic Graph (DAG).":
            pass
        else:
            raise e
