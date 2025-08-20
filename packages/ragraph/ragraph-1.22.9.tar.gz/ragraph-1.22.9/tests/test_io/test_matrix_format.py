import pytest
from ragraph.io import matrix


def test_from_matrix():
    mat = [[1, 0, 1, 0], [0, 2, 3, 4]]
    rows = ["a", "b"]
    cols = ["a", "c", "d", "e"]
    weight_label = "num"
    empty = 0
    graph = matrix.from_matrix(
        mat, rows, cols=cols, weight_label=weight_label, empty=empty, name="graph_ab"
    )
    assert set(graph.node_dict.keys()) == {"a", "b", "c", "d", "e"}
    assert len(graph.edges) == 5
    assert graph.edge_weight_labels == ["num"]


def test_round_trip(graph_ab):
    mat = matrix.to_matrix(graph_ab)
    assert graph_ab == matrix.from_matrix(mat, graph_ab.nodes, name="graph_ab")
    assert matrix.from_matrix(mat).node_dict.get("node0", False)


def test_errors():
    with pytest.raises(ValueError) as e:
        matrix.from_matrix([[0]], ["a", "b"])
        assert "matrix dimensions" in str(e.value).lower()


def test_round_trip_no_numpy(graph_ab):
    matrix.np = None

    mat = matrix.to_matrix(graph_ab)
    assert graph_ab == matrix.from_matrix(mat, graph_ab.nodes, name="graph_ab")

    try:
        import numpy as np

        matrix.np = np
    except ImportError:
        pass
