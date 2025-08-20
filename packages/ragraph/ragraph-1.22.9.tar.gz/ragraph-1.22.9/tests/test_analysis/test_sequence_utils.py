from ragraph import datasets
from ragraph.analysis import cluster, sequence
from ragraph.graph import Graph
from ragraph.node import Node


def test_branchsort():
    g = datasets.get("tarjans8")

    g.node_dict["1"].children = [g.node_dict[n] for n in ["7", "4", "5"]]
    g.node_dict["2"].children = [g.node_dict[n] for n in ["8", "3", "6"]]

    roots = ["2", "1"]

    graph, roots, leafs = sequence.utils.branchsort(
        algo=sequence.name,
        graph=g,
        root=None,
        nodes=roots,
        inplace=True,
        recurse=True,
        names=True,
    )

    s1 = ["4", "5", "7"]
    s2 = ["3", "6", "8"]

    assert roots == ["1", "2"]
    assert [n.name for n in graph.node_dict[roots[0]].children] == s1
    assert [n.name for n in graph.node_dict[roots[1]].children] == s2
    assert leafs == s1 + s2


def test_branchsort_cases(case):
    graph, roots = cluster.hierarchical_markov(case, inplace=True)
    graph, roots, leafs = sequence.utils.branchsort(
        algo=sequence.markov,
        graph=case,
        root=None,
        recurse=False,
        inplace=True,
        algo_args=dict(inf=1.0, dep=1.0, mu=2.0),
    )


def test_branchsort_leafs():
    """Test whether the branchsort util keeps leaves intact."""
    nodes = {i: Node(name=i) for i in "abcdefghijkl"}
    nodes["a"].children = [nodes["c"], nodes["b"]]  # notice it's reversed.
    nodes["d"].children = [nodes["f"], nodes["e"]]  # also.
    nodes["f"].children = [nodes["h"], nodes["g"]]  # also.
    nodes["e"].children = [nodes["j"], nodes["i"]]  # also.
    nodes["h"].children = [nodes["l"], nodes["k"]]  # also.

    graph = Graph(nodes=nodes.values())

    # Sequence by name, but set "a" and "f" as leaf nodes (e.g. protect them).
    graph, roots, leafs = sequence.utils.branchsort(
        algo=sequence.name,
        graph=graph,
        root=None,
        recurse=True,
        inplace=True,
        nodes=graph.roots,
        leafs=["a", "f"],
    )

    assert nodes["a"].children == [nodes["c"], nodes["b"]], "Should be intact."
    assert nodes["d"].children == [nodes["f"], nodes["e"]][::-1], "Should be reversed."
    assert nodes["f"].children == [nodes["h"], nodes["g"]], "Should be intact."
    assert nodes["e"].children == [nodes["j"], nodes["i"]][::-1], "Should be reversed."
    assert nodes["h"].children == [nodes["l"], nodes["k"]], "Should be intact."
