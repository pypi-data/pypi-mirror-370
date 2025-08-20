"""# Edge class module"""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from ragraph.generic import Annotations, Metadata
from ragraph.node import Node


class Edge(Metadata):
    """Edge between a source [`Node`][ragraph.node.Node] and a target [`Node`][ragraph.node.Node].

    Arguments:
        source: Source [`Node`][ragraph.node.Node] of this edge.
        target: Target [`Node`][ragraph.node.Node] of this edge.
        name: Instance name. Given a UUID if none provided.
        kind: Kind or main category of this instance.
        labels: Labels categorizing this instance.
        weights: Dictionary of weights attached to this instance.
        annotations: Miscellaneous properties of this instance.
        uuid: Fixed UUID if desired, generated when left set to None.
    """

    def __init__(
        self,
        source: Node,
        target: Node,
        name: Optional[str] = None,
        kind: str = "edge",
        labels: Optional[List[str]] = None,
        weights: Optional[Dict[str, Union[int, float]]] = None,
        annotations: Union[Annotations, Dict[str, Any], None] = None,
        uuid: Optional[Union[str, UUID]] = None,
    ):
        Metadata.__init__(
            self,
            name=name,
            kind=kind,
            labels=labels,
            weights=weights,
            annotations=annotations,
            uuid=uuid,
        )
        self._source: Node
        self._target: Node
        setattr(self, "source", source)
        setattr(self, "target", target)

    def __str__(self):
        return "{}(source='{}', target='{}', name='{}')".format(
            self.__class__.__name__, self.source.name, self.target.name, self.name
        )

    def __repr__(self):
        kwargdict = dict(
            source=str(self.source),
            target=str(self.target),
            name=repr(self.name),
            kind=repr(self.kind),
            labels=self.labels,
            weights=self.weights,
            annotations=self.annotations,
            uuid=repr(self.uuid),
        )
        kwargs = ", ".join([str(k) + "=" + str(v) for k, v in kwargdict.items()])
        return "<{}.{}({}) at {}>".format(
            self.__class__.__module__, self.__class__.__name__, kwargs, hex(id(self))
        )

    @property
    def source(self) -> Node:
        """Edge source node."""
        return self._source

    @source.setter
    def source(self, value: Node):
        self._source = value

    @property
    def target(self) -> Node:
        """Edge target node."""
        return self._target

    @target.setter
    def target(self, value: Node):
        self._target = value

    @property
    def json_dict(self) -> Dict[str, Any]:
        """JSON dictionary representation.

        Returns:
            source: Source node UUID (not Node) as str.
            target: Target node UUID (not Node) as str.
            kind: Kind as str.
            labels: Labels as list of str.
            weights: Weights as dict.
            annotations: Annotations as a dictionary.
        """
        return self.as_dict(use_uuid=True)

    def as_dict(self, use_uuid: bool = False) -> Dict[str, Any]:
        """Return a copy as a (serializable) dictionary.

        Arguments:
            use_uuid: Whether to use UUIDs instead of names.

        Returns:
            source: Source node name or UUID (not Node) as str.
            target: Target node name or UUID (not Node) as str.
            kind: Kind as str.
            labels: Labels as list of str.
            weights: Weights as dict.
            annotations: Annotations as a dictionary.
            uuid: UUID as str if toggled.
        """
        if use_uuid:
            return dict(
                source=str(self.source.uuid),
                target=str(self.target.uuid),
                name=self.name,
                kind=self.kind,
                labels=self.labels,
                weights=self.weights,
                annotations=self.annotations.as_dict(),
                uuid=str(self.uuid),
            )
        else:
            return dict(
                source=self.source.name,
                target=self.target.name,
                name=self.name,
                kind=self.kind,
                labels=self.labels,
                weights=self.weights,
                annotations=self.annotations.as_dict(),
            )
