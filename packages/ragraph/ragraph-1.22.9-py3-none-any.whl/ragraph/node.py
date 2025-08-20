"""# Node class module"""

from typing import Any, Dict, Generator, Iterable, List, Optional, Union
from uuid import UUID

from ragraph.generic import Annotations, Metadata


class Node(Metadata):
    """Generic node class.

    Arguments:
        name: Instance name. Given a UUID if none provided.
        parent: Parent node.
        children: List of child nodes.
        kind: Kind or main category of this instance.
        labels: Labels categorizing this instance.
        weights: Dictionary of weights attached to this instance.
        annotations: Miscellaneous properties of this instance.
        uuid: Fixed UUID if desired, generated when left set to None.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional["Node"] = None,
        children: Optional[Iterable["Node"]] = None,
        is_bus: bool = False,
        kind: str = "node",
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
        self._parent: Optional[Node] = None
        self._children: List[Node] = []
        self._is_bus: bool = False
        setattr(self, "parent", parent)
        setattr(self, "children", children)
        setattr(self, "is_bus", is_bus)

    def __str__(self) -> str:
        return "{}(name='{}')".format(self.__class__.__name__, self.name)

    def __repr__(self) -> str:
        parent = None if self.parent is None else repr(self.parent.name)
        kwargdict = dict(
            name=repr(self.name),
            parent=parent,
            children=[str(c) for c in self.children],
            is_bus=self.is_bus,
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
    def parent(self) -> Optional["Node"]:
        """Parent node. Defaults to `None`."""
        return self._parent

    @parent.setter
    def parent(self, value: Optional["Node"]):
        # Check type.
        if value is not None and not isinstance(value, Node):
            raise TypeError("Parent should be of type {}, got {}.".format(Node, type(value)))
        previous = getattr(self, "_parent")
        if previous is not None:
            # Previous parent, need to unset first!
            previous._children.remove(self)
            self._parent = None
        if value is not None:
            # Re-set if value is not None.
            self._parent = value
            self._parent._children.append(self)

    @property
    def children(self) -> List["Node"]:
        """Child nodes. Default is empty."""
        return self._children

    @children.setter
    def children(self, value: Optional[Iterable["Node"]]):
        # Unset previous children's private parent properties, bypassing parent setter.
        for c in self._children:
            c._parent = None
        self._children = []
        # New children: set parent publicly to also unset any previous parent and adds
        # it to self._children.
        if value is not None:
            for c in list(value).copy():
                c.parent = self

    @property
    def is_bus(self):
        """Whether this node is a bus node for its parent."""
        return self._is_bus

    @is_bus.setter
    def is_bus(self, value: bool):
        value = bool(value)
        if value and not self._parent:
            raise ValueError("Cannot be a bus without a parent to be it for. Set a parent first!")
        self._is_bus = bool(value)

    @property
    def ancestors(self) -> List["Node"]:
        """Get all ancestors of this node."""
        return list(self.ancestor_gen)

    @property
    def ancestor_gen(self) -> Generator["Node", None, None]:
        """Yield all ancestors of this node."""
        if self.parent:
            yield self.parent
            yield from self.parent.ancestors

    @property
    def descendants(self) -> List["Node"]:
        """Get all descendants of this node."""
        return list(self.descendant_gen)

    @property
    def descendant_gen(self) -> Generator["Node", None, None]:
        """Yield all descendants of this node."""
        for child in self.children:
            yield child
            yield from child.descendants

    @property
    def depth(self) -> int:
        """Depth of this node, e.g. the number of levels from the node to the root."""
        if self.parent:
            return self.parent.depth + 1
        return 0

    @property
    def height(self) -> int:
        """Height of this node, e.g. the longest simple path to a leaf node."""
        if self._children:
            return max([child.height for child in self._children]) + 1
        return 0

    @property
    def width(self) -> int:
        """Width of this node, e.g. the number of leaf nodes in this node's branch."""
        if self.is_leaf:
            return 1
        return sum(c.width for c in self.children)

    @property
    def is_leaf(self) -> bool:
        """Whether this node is a leaf node (has no children)."""
        return not bool(self.children)

    @property
    def is_root(self) -> bool:
        """Whether this node is a root node (has no parent)."""
        return not bool(self.parent)

    @property
    def json_dict(self) -> Dict[str, Any]:
        """JSON dictionary representation.

        Returns:
            name: Name as str.
            parent: Parent name (not Node) as str.
            children: Children names (not Nodes) as str.
            is_bus: is_bus as bool.
            kind: Kind as str.
            labels: Labels as a list of strings.
            weights: Weights as dict.
            annotations: Annotations as per
                [`ragraph.generic.Mapping.as_dict`][ragraph.generic.Mapping.as_dict].
        """
        return self.as_dict(use_uuid=True)

    def as_dict(self, use_uuid: bool = False) -> Dict[str, Any]:
        """Return a copy as a (serializable) dictionary.

        Returns:
            name: Name as str.
            parent: Parent name or UUID (not Node) as str.
            children: Children names (not Nodes) as str.
            is_bus: is_bus as bool.
            kind: Kind as str.
            labels: Labels as a list of strings.
            weights: Weights as dict.
            annotations: Annotations as per
                [`ragraph.generic.Mapping.as_dict`][ragraph.generic.Mapping.as_dict].
            uuid: UUID as str if toggled.
        """
        if use_uuid:
            return dict(
                name=self.name,
                parent=None if self.parent is None else str(self.parent.uuid),
                children=[str(n.uuid) for n in self.children],
                is_bus=self.is_bus,
                kind=self.kind,
                labels=self.labels,
                weights=self.weights,
                annotations=self.annotations.as_dict(),
                uuid=str(self.uuid),
            )
        else:
            return dict(
                name=self.name,
                parent=getattr(self.parent, "name", None),
                children=[n.name for n in self.children],
                is_bus=self.is_bus,
                kind=self.kind,
                labels=self.labels,
                weights=self.weights,
                annotations=self.annotations.as_dict(),
            )
