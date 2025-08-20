"""Tests for Markov sequencing."""

from ragraph import datasets
from ragraph.analysis import sequence
from ragraph.analysis.sequence.utils import markov_decision
from ragraph.io.matrix import from_matrix


def test_markov_sequencing_chain(chain_graph):
    assert chain_graph is not None
    _, seq = sequence.markov(chain_graph, inf=1.0, dep=1.0, mu=2.0, names=True)
    assert seq == ["4", "3", "2", "1", "0"]

    single = [chain_graph.nodes[0]]
    assert sequence.markov(chain_graph, nodes=single)[1] == single


def test_markov_sequencing_ucav():
    casename = "ucav"
    case = datasets.get(casename)
    _, seq = sequence.markov(
        case,
        nodes=[n.name for n in case.leafs],
        inf=1.0,
        dep=1.0,
        mu=1.5,
        edge_weights=["binary"],
        names=True,
    )
    ref = [
        "Prepare UCAV Preliminary DR&O",
        "Develop Structural Design Conditions",
        "Perform Aerodynamics Analyses & Evaluation",
        "Perform Weights & Inertias Analyses & Evaluation",
        "Create UCAV Preliminary Design Configuration",
        "Prepare Structural Geometry & Notes for FEM",
        "Prepare & Distribute Surfaced Models & Internal Drawings",
        "Perform S&C Analyses & Evaluation",
        "Establish Internal Load Distributions",
        "Preliminary Manufacturing Planning & Analyses",
        "Develop Balanced Freebody Diagrams & External Loads",
        "Evaluate Structural Strength, Stiffness, & Life",
        "Create Initial Structural Geometry",
        "Prepare UCAV Proposal",
    ]
    assert seq == ref


def test_markov_sequencing_cases(case):
    assert case is not None
    sequence.markov(case, nodes=[n.name for n in case.leafs], inf=2.0, dep=1.0, mu=2.0)


def test_markov_sequence_bus_behavior():
    graph = from_matrix(
        [
            [0, 5, 5, 5],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
        ],
        rows="abcd",
    )

    _, seq = sequence.markov(graph, names=True)

    assert seq[-1] == "a"

    seq = sequence.branchsort(graph, algo=sequence.scc_tearing, names=True)[2]

    assert seq[-1] == "a"

    nodes = graph.leafs
    assert nodes[markov_decision(graph, nodes)] != "a"
