from ragraph.graph import Graph
from ragraph.io.esl import from_esl


def test_from_esl(esl_file):
    g: Graph = from_esl(esl_file)

    assert g.node_count == 8, "Graph of test.esl should have 5 nodes, not %d." % g.node_count
    assert g.edge_count == 1, "Graph of test.esl should have 9 edges, not %d." % g.edge_count

    g.check_consistency()
