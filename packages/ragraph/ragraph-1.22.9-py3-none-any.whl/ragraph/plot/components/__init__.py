"""# Plot components.

This module contains several re-usable plot components that contain the data for a Plotly (sub-)
figure. See [`Component`][ragraph.plot.generic.Component] for the definition of a plot component.
"""

from ragraph.plot.components.blank import Blank
from ragraph.plot.components.labels import Labels
from ragraph.plot.components.legend import Legend
from ragraph.plot.components.piemap import PieMap
from ragraph.plot.components.tree import Tree

__all__ = ["Blank", "Labels", "Legend", "PieMap", "Tree"]
