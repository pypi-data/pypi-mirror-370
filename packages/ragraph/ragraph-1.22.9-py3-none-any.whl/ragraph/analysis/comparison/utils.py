"""# Comparison analysis utilities"""

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, FrozenSet, Tuple

from ragraph.edge import Edge
from ragraph.generic import Metadata
from ragraph.graph import Graph
from ragraph.node import Node

try:
    StrEnum = enum.StrEnum
except Exception:
    from strenum import StrEnum  # type: ignore
finally:
    if TYPE_CHECKING:
        StrEnum = enum.StrEnum


class NodeDescriptorLike(ABC):
    """A class that takes a node and describes it by returning a fixed (hashable) output.

    Hashable means that the description can be used to determine uniqueness by set operations.
    """

    @classmethod
    @abstractmethod
    def from_node(cls, node: Node) -> "NodeDescriptorLike":
        """Create a node descriptor from a node."""
        raise NotImplementedError

    @abstractmethod
    def to_node(self, graph: Graph) -> Node:
        """Create a node from a descriptor in a graph and return it for convenience."""
        raise NotImplementedError


@dataclass(frozen=True)
class NodeDescriptor(NodeDescriptorLike):
    """Describe a node based on its name, kind, labels and weights."""

    name: str
    kind: str
    labels: FrozenSet[str]
    weights: FrozenSet[Tuple[str, float]]

    @classmethod
    def from_node(cls, node: Node) -> "NodeDescriptor":
        return cls(
            node.name,
            node.kind,
            frozenset(node.labels),
            frozenset(node.weights.items()),
        )

    def to_node(self, graph: Graph) -> Node:
        node = Node(
            name=self.name,
            kind=self.kind,
            labels=list(self.labels),
            weights=dict(self.weights),
        )
        graph.add_node(node)
        return node


class EdgeDescriptorLike(ABC):
    """A class that takes an edge and describes it by returning a fixed (hashable) output.

    Hashable means that the description can be used to determine uniqueness by set operations.
    """

    @classmethod
    @abstractmethod
    def from_edge(cls, edge: Edge) -> "EdgeDescriptor":
        """Create an edge descriptor from an edge. Ignores annotations."""
        ...

    @abstractmethod
    def to_edge(self, graph: Graph) -> Edge:
        """Create an edge from a descriptor in a graph."""
        ...


@dataclass(frozen=True)
class EdgeDescriptor(EdgeDescriptorLike):
    """Describe a node based on its source name, target name, kind, labels, and weights."""

    source: str
    target: str
    kind: str
    labels: FrozenSet[str]
    weights: FrozenSet[Tuple[str, float]]

    @classmethod
    def from_edge(cls, edge: Edge) -> "EdgeDescriptor":
        return EdgeDescriptor(
            edge.source.name,
            edge.target.name,
            edge.kind,
            frozenset(edge.labels),
            frozenset(edge.weights.items()),
        )

    def to_edge(self, graph: Graph) -> Edge:
        edge = Edge(
            graph[self.source],
            graph[self.target],
            kind=self.kind,
            labels=list(self.labels),
            weights=dict(self.weights),
        )
        graph.add_edge(edge)
        return edge


class TagMode(StrEnum):
    """How to tag nodes as unique to one of the given inputs or common."""

    KIND = enum.auto()
    LABEL = enum.auto()
    ANNOTATION = enum.auto()


def tag(item: Metadata, tag: str, mode: TagMode):
    """Tag an item using a given tagging mode."""
    if mode == TagMode.KIND:
        item.kind = tag
    elif mode == TagMode.LABEL:
        item.labels = item.labels + [tag]
    elif mode == TagMode.ANNOTATION:
        item.annotations[tag] = True
    else:
        raise ValueError("Unknown tagging mode.")
