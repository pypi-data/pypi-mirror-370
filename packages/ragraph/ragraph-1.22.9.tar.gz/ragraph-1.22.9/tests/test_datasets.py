"""Tests for datasets module."""

from ragraph import datasets


def test_datasets():
    assert datasets.enum()
    for i in datasets.enum():
        assert datasets.info(i)
        assert datasets.get(i)


def test_symmetry():
    symmetrical = ["climate_control", "localbus", "overlap"]
    for ds in symmetrical:
        g = datasets.get(ds)
        leafs = g.leafs
        dim = len(leafs)

        error = False
        msg = "{}: '{}' weight between '{}' and '{}' does not match."
        for weight in g.edge_weight_labels:
            adj = g.get_adjacency_matrix(nodes=leafs, only=[weight])
            for i in range(dim):
                for j in range(dim):
                    if adj[i][j] != adj[j][i]:
                        print(msg.format(ds, weight, leafs[i].name, leafs[j].name))
                        error = True
        # Fail on the last one. Logged output already shows all.
        assert not error, msg.format(ds, weight, leafs[i].name, leafs[j].name)
