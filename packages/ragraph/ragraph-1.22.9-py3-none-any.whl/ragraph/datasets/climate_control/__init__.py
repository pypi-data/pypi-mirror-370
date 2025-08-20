"""# Ford climate control system

This dataset describes a climate control system as it was to be found in Ford vehicles. Four
different dependency types have been documented, being spatial, energy flow, information flow, and
material flow dependencies. These are weighted from -2 to 2, where the following definitions have
been used:

    * +2: Required
    * +1: Desired
    *  0: Indifferent
    * -1: Undesired
    * -2: Detrimental

We have added an "adjacency" weight, which is the nonnegative sum of all dependencies between
components.

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
