"""# Minimal compatibility analysis example

Contains 6 component variant nodes. They are divided in three node kinds (e.g. components), which
correspond to the first character in their node names: A1, B1, B2, C1, C2, C3. For ease of usage,
the "performance" weight of each node is set to it's node name's second character.

Compatibility between nodes is signalled using edges with a "compatibility" kind.
"""

node_weights = ["performance"]
