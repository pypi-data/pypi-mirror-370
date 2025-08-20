from ragraph import datasets
from ragraph.analysis.sequence._genetic import genetic, genetic_sequencing


def test_sga_seq():
    graph = datasets.get("ucav")
    nodes = list(graph.nodes)

    lin = genetic_sequencing(graph, nodes, 100, 100, 5, 0.3, 0.05, 0.1)

    best = lin.hall_of_fame.chromosomes[0].genes
    _ = [nodes[i] for i in best]

    graph, seq2 = genetic(
        graph,
        nodes=nodes,
        n_chromosomes=100,
        n_generations=100,
        n_hall_of_fame=5,
        p_crossover=0.3,
        p_mutation=0.05,
        p_swap=0.1,
    )
