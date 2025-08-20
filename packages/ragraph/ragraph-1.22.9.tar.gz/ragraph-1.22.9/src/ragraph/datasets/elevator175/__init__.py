"""# Elevator system decomposed into 175 components

The Complex Elevator System is described using an undirected graph with multiple dependency types.
It describes a machine-room-less elevator called the 'Kone MonoSpace'. It is designed for low- to
midrise buildings and uses permanent-magnet electric motors. The five defined edge types are
spatial, material, mechanical energy, electrical energy and information. It was published in a
variation of 175 elements and a less granular variation of 45 elements. The less granular variation
collapses a set of pre-defined modules and therefore contains less detail of the system.

Reference:
    Niutanen, V., Hölttä-otto, K., Rahardjo, A., & Stowe, H. M. (2017). Complex Elevator System DSM
    - Case for a DSM Design Sprint. In 19th International dependency and structure modeling
    conference, DSM 2017.
"""

edge_weights = [
    "spatial",
    "material",
    "information",
    "mechanical energy",
    "electrical energy",
    "sum",
    "binary",
]
