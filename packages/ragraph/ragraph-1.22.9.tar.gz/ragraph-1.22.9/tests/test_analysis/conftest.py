"""pytest test configuration."""

import logging
from typing import List

import numpy as np
import pytest
from ragraph import datasets
from ragraph.graph import Edge, Graph, Node

# Toggle debugging output.
DEBUG_ANALYSIS = True


@pytest.fixture(autouse=DEBUG_ANALYSIS)
def analysis_logging():
    from ragraph.analysis import logger

    logger.setLevel(logging.DEBUG)
    yield logger
    logger.setLevel(logging.INFO)


@pytest.fixture(params=[i for i in datasets.enum() if i != "ledsip"])
def case(request):
    return datasets.get(request.param)


@pytest.fixture
def srcs():
    return [0, 1, 0, 2, 4, 4, 4, 4, 0, 1, 2, 3]


@pytest.fixture
def tgts():
    return [1, 0, 2, 0, 0, 1, 2, 3, 4, 4, 4, 4]


@pytest.fixture
def wgts():
    return [9, 9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


@pytest.fixture
def graph(srcs: List[int], tgts: List[int], wgts: List[int]):
    nodes = [Node(name) for name in ["a", "b", "c", "d", "e", "f"]]

    edges = [
        Edge(nodes[src], nodes[tgt], weights=dict(weight=wgt))
        for src, tgt, wgt in zip(srcs, tgts, wgts)
    ]

    return Graph(nodes=nodes, edges=edges)


@pytest.fixture
def parent_graph(graph: Graph):
    parent = Node("parent", children=graph.node_list)
    for node in graph.nodes:
        node.parent = parent
    graph.add_node(parent)
    return graph


@pytest.fixture
def matrix(srcs, tgts, wgts, graph):
    """Adjacency matrix that should correspond to the graph.
    [[0. 9. 1. 0. 1. 0.]
    [9. 0. 0. 0. 1. 0.]
    [1. 0. 0. 0. 1. 0.]
    [0. 0. 0. 0. 1. 0.]
    [1. 1. 1. 1. 0. 0.]
    [0. 0. 0. 0. 0. 0.]]
    """
    dim = graph.node_count
    matrix = np.zeros((dim, dim))
    for src, tgt, wgt in zip(srcs, tgts, wgts):
        matrix[src, tgt] = wgt
    return matrix


@pytest.fixture
def paper():
    Anb = np.array(
        [
            [0, 0, 1, 0, 1],
            [0, 0, 0, 0, 1],
            [0, 0, 0, 1, 0],
            [1, 0, 1, 0, 0],
            [0, 1, 0, 0, 0],
        ]
    )
    nz = np.transpose(np.nonzero(Anb))
    nodes = [Node(n) for n in ["a", "b", "c", "d", "e"]]
    edges = [Edge(nodes[j], nodes[i]) for (i, j) in nz]
    return Graph(nodes=nodes, edges=edges)


@pytest.fixture
def chain_adj():
    """Simple chain of nodes."""
    return np.diag([1, 1, 1, 1], k=1)


@pytest.fixture
def chain_graph():
    """Simple chain of nodes."""
    ns = [Node(str(i)) for i in range(5)]
    es = [Edge(ns[i + 1], ns[i]) for i in range(4)]
    return Graph(nodes=ns, edges=es)


@pytest.fixture
def hierarchy():
    """Hierarchy with multiple levels and varying widths.

                       q
      _________________|_________________
      |                     |           |
      |              _______p______     |
      |              |            |     |
      |         _____o____        |     |
      |         |         |       |     |
    __k__   ____l___    __m__   __n__   |
    |   |   |   |   |   |   |   |   |   |
    a   b   c   d   e   f   g   h   i   j
    """
    a = Node("a")
    b = Node("b")
    c = Node("c")
    d = Node("d")
    e = Node("e")
    f = Node("f")
    g = Node("g")
    h = Node("h")
    i = Node("i")
    j = Node("j")
    k = Node("k")
    l = Node("l")  # noqa
    m = Node("m")
    n = Node("n")
    o = Node("o")
    p = Node("p")
    q = Node("q")

    q.children = [k, p, j]
    p.children = [o, n]
    o.children = [l, m]
    k.children = [a, b]
    l.children = [c, d, e]
    m.children = [f, g]
    n.children = [h, i]

    return Graph(nodes=[q], add_children=True)
