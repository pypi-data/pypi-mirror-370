from ragraph.analysis._utils import create_parent
from ragraph.analysis.cluster import tarjans_scc
from ragraph.analysis.sequence import branchsort, scc_tearing
from ragraph.io.matrix import from_matrix


def test_sequence():
    g = from_matrix(
        [
            [0, 1, 1, 0, 0],  # 0 -> 4, only 1 & 2 as input.
            [0, 0, 0, 1, 0],  # 1 -> 2, only 3 as input.
            [0, 1, 0, 0, 0],  # 2 -> 3, only 1 as input.
            [0, 0, 0, 0, 0],  # 3 -> 1, no inputs
            [0, 0, 0, 0, 0],  # 4 -> 0, no inputs
        ]
    )

    # Load the graph.
    _, seq = tarjans_scc(g, names=True)
    assert seq[::-1] == [
        "node4",
        "node3",
        "node1",
        "node2",
        "node0",
    ], "Trivial sequence should be found by SCC reversed."

    create_parent(g, children=["node2", "node0"])
    _, seq = tarjans_scc(g, leafs=g.roots, names=True)
    assert seq[::-1] == [
        "node4",
        "node3",
        "node1",
        "node.node0",
    ], "SCC should work on nested graphs."

    g, root_seq, leaf_seq = branchsort(g, nodes=g.roots, algo=scc_tearing, names=True)
    assert root_seq == [
        "node4",
        "node3",
        "node1",
        "node.node0",
    ], "Branchsort should return trivial sub-sequences correctly."
    assert leaf_seq == [
        "node4",
        "node3",
        "node1",
        "node2",
        "node0",
    ], "Branchsort should return trivial sub-sequences correctly."
