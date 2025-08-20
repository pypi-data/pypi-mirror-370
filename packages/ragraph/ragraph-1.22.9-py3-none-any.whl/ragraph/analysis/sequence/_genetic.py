"""Genetic algorithms for sequencing purposes."""

from typing import List, Optional, Tuple, Union

from ratio_genetic_py import (
    ConvergenceKinds,
    CrossoverKinds,
    EvaluatorKinds,
    EvaluatorMatrix,
    GeneratorKinds,
    Lineage,
    MutatorSwap,
    RecorderKinds,
    SelectorKinds,
    SequencingSettings,
    sequence_sga,
)

from ragraph.analysis._classes import Parameter, SequenceAnalysis
from ragraph.graph import Graph, Node

params = {
    p.name: p
    for p in [
        Parameter(
            "n_chromosomes",
            int,
            description="Number of chromosomes in a generation.",
            default=100,
        ),
        Parameter(
            "n_generations",
            int,
            description="How many generations to go through after which to exit.",
            default=1000,
        ),
        Parameter(
            "p_crossover",
            float,
            description="Probability for a pair to be subjected to crossover.",
            default=0.3,
        ),
        Parameter(
            "p_mutation",
            float,
            description="Probability for each chromosome to be subjected to mutation.",
            default=0.05,
        ),
        Parameter(
            "p_swap",
            float,
            description="Probability for each gene to be swapped during mutation.",
            default=0.05,
        ),
        Parameter("evaluator", str, description="", default="feedback_distance"),
    ]
}


genetic_analysis = SequenceAnalysis("Genetic", parameters=params)


@genetic_analysis
def genetic(
    graph: Graph,
    root: Optional[Union[str, Node]] = None,
    nodes: Optional[Union[List[str], List[Node]]] = None,
    evaluator: Optional[str] = params["evaluator"].default,
    n_chromosomes: Optional[int] = params["n_chromosomes"].default,
    n_generations: Optional[int] = params["n_generations"].default,
    p_crossover: Optional[float] = params["p_crossover"].default,
    p_mutation: Optional[float] = params["p_mutation"].default,
    p_swap: Optional[float] = params["p_swap"].default,
    inherit: bool = True,
    edge_weights: Optional[List[str]] = None,
    loops: bool = False,
    inplace: bool = True,
    names: bool = False,
    safe: bool = True,
    **kwargs,
) -> Tuple[Graph, List[Node]]:
    """docstring stub"""
    lineage = genetic_sequencing(
        graph,
        nodes,  # type: ignore
        n_chromosomes,  # type: ignore
        n_generations,  # type: ignore
        1,
        p_crossover,  # type: ignore
        p_mutation,  # type: ignore
        p_swap,  # type: ignore
        n_records=1,
        inherit=inherit,
        edge_weights=edge_weights,
    )

    best = lineage.hall_of_fame.chromosomes[0].genes

    seq = [nodes[i] for i in best]  # type: ignore
    return graph, seq


def genetic_sequencing(
    graph: Graph,
    nodes: List[Node],
    n_chromosomes: int,
    n_generations: int,
    n_hall_of_fame: int,
    p_crossover: float,
    p_mutation: float,
    p_swap: float,
    evaluator: str = "feedback_distance",
    n_records: Optional[int] = None,
    inherit: bool = True,
    edge_weights: Optional[List[str]] = None,
) -> Lineage:
    """Genetic sequencing of nodes in a graph.

    Arguments:
        graph: Graph holding data.
        nodes: Nodes to sequence.
        evaluator: Evaluation method to use. One of "feedback_distance",
            "feedback_marks", or "lower_left_distance".
        n_chromosomes: Number of chromosomes in each generation.
        n_generations: Number of generations to simulate.
        n_hall_of_fame: Hall of Fame size of best performing chromosomes.
        p_crossover: Probability for a pair to be subjected to crossover.
        p_mutation: Probability for each chromosome to be subjected to mutation.
        p_swap: Probability for each gene to be swapped with another during mutation.
        n_records: Number of generation records to keep.
        inherit: Whether to inherit edges between children when getting the adjacency
            matrix.
        edge_weights: Edge weights to consider when getting the adjacency matrix.

    Returns:
        Lineage object containing generations of chromosomes, generation records and
        a hall of fame of best performing chromosomes.
    """
    matrix = graph.get_adjacency_matrix(nodes, inherit=inherit, only=edge_weights)
    vec = [x for row in matrix for x in row]

    ekinds = dict(
        feedback_distance=EvaluatorKinds.FeedbackDistance,
        feedback_marks=EvaluatorKinds.FeedbackMarks,
        lower_left_distance=EvaluatorKinds.LowerLeftDistance,
    )
    evaluator = EvaluatorMatrix(ekinds[evaluator], vec, 1)

    settings = SequencingSettings(
        n_genes=len(nodes),
        p_crossover=p_crossover,
        p_mutation=p_mutation,
        n_chromosomes=n_chromosomes,
        n_generations=n_generations,
        n_records=n_records,
        n_hall_of_fame=n_hall_of_fame,
    )

    lineage = sequence_sga(
        settings,
        GeneratorKinds.RandomSequence,
        evaluator,
        RecorderKinds.FitnessStatistics,
        SelectorKinds.Roulette,
        CrossoverKinds.IPX,
        MutatorSwap(p_swap),
        ConvergenceKinds.Never,
    )

    return lineage
