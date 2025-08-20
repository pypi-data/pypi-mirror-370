"""# Pre-clustered Ford climate control system using the Markov-Gamma heuristic

Pre-clustered using bus detection plus hierarchical clustering.

Reference:
    Pimmler, T. U., & Eppinger, S. D. (1994). Integration Analysis of Product Decompositions. ASME
    Design Theory and Methodology Conference.
"""

edge_weights = [
    "adjacency",
    "spatial",
    "energy flow",
    "information flow",
    "material flow",
]
