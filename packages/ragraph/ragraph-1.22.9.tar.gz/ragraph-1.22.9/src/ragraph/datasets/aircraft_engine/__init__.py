"""# Pratt & Whitney Aircraft Engine

A directed graph describing the Pratt & Whitney PW4098 commercial high bypass-ratio turbofan engine.
The graph describes a combination of the actual hardware dependencies of the engine and those of the
development teams involved with them. It is a weighted and directed graph featuring 60 elements,
four of which are sometimes left out as they represent the integration teams and no individual
hardware components. Weak and strong dependencies are distinguished using weights of 1 and 2,
respectively.

Reference:
    Rowles, C. M. (1999). System integration analysis of a large commercial aircraft engine.
"""

edge_weights = ["adjacency"]
