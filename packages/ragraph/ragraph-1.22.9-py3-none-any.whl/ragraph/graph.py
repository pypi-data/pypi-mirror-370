"""# Graph class module

The [`Graph`][ragraph.graph.Graph] class is the core of this package. It is the internal storage
format that facilitates all conversions. These class definitions are designed to
accommodate a wide range of graph formats.
"""

from collections import OrderedDict, defaultdict
from copy import deepcopy
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)
from uuid import UUID

from ragraph import utils
from ragraph.edge import Edge
from ragraph.generic import Annotations, Metadata
from ragraph.generic import Convention
from ragraph.node import Node

try:
    import numpy as np

except ImportError:
    np = None  # type: ignore


class ConsistencyError(Exception):
    pass


class Graph(Metadata):
    """Graph of [`Node`][ragraph.node.Node] objects and [`Edge`][ragraph.edge.Edge] objects between
    them.

    Arguments:
        nodes: Iterable of graph nodes.
        edges: Iterable of graph edges.
        add_parents: Recursively add parent nodes of the provided nodes.
        add_children: Recursively add child nodes of the provided nodes.
        name: Instance name. Given a UUID if none provided.
        kind: Kind or main category of this instance.
        labels: Labels categorizing this instance.
        weights: Dictionary of weights attached to this instance.
        annotations: Miscellaneous properties of this instance.
        uuid: Fixed UUID if desired, generated when left set to None.
    """

    def __init__(
        self,
        nodes: Optional[Iterable[Node]] = None,
        edges: Optional[Iterable[Edge]] = None,
        add_parents: bool = False,
        add_children: bool = False,
        name: Optional[str] = None,
        kind: Optional[str] = None,
        labels: Optional[List[str]] = None,
        weights: Optional[Dict[str, Union[int, float]]] = None,
        annotations: Optional[Union[Annotations, Dict[str, Any]]] = None,
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
        self._nodes: Dict[str, Node] = OrderedDict()
        self._node_uuid_dict: Optional[Dict[UUID, Node]] = None  # Lazy
        self._edges: Dict[str, Edge] = OrderedDict()
        self._edge_uuid_dict: Optional[Dict[UUID, Edge]] = None  # lazy
        self._directed_edges: defaultdict = defaultdict(lambda: defaultdict(list))
        self._reversed_edges: defaultdict = defaultdict(lambda: defaultdict(list))
        self.add_parents = add_parents
        self.add_children = add_children
        setattr(self, "nodes", nodes)
        setattr(self, "edges", edges)

    def __str__(self) -> str:
        nodes, edges = self.node_count, self.edge_count
        ns, es = "" if nodes == 1 else "s", "" if edges == 1 else "s"
        counts = f"{nodes} node{ns}, {edges} edge{es}"
        return f"{self.__class__.__name__}(name={self.name}, {counts})"

    def __repr__(self) -> str:
        kwargdict = dict(
            name=repr(self.name),
            kind=repr(self.kind),
            labels=self.labels,
            weights=self.weights,
            annotations=self.annotations,
            uuid=repr(self.uuid),
        )
        kwargs = ", ".join([str(k) + "=" + str(v) for k, v in kwargdict.items()])
        nodes, edges = self.node_count, self.edge_count
        ns, es = "" if nodes == 1 else "s", "" if edges == 1 else "s"
        counts = f"{nodes} node{ns}, {edges} edge{es}"
        return "<{}.{}({}), {} at {}>".format(
            self.__class__.__module__,
            self.__class__.__name__,
            kwargs,
            counts,
            hex(id(self)),
        )

    def __eq__(self, other) -> bool:
        return self.as_dict(use_uuid=False) == other.as_dict(use_uuid=False)

    def __getitem__(self, key: Union[str, UUID, Tuple[str, str]]):
        if isinstance(key, str):
            return self._nodes[key]

        if isinstance(key, (tuple, list)) and len(key) == 2:
            return self._directed_edges[key[0]][key[1]]

        if isinstance(key, UUID):
            if key in self.node_uuid_dict:
                return self.node_uuid_dict[key]
            if key in self.edge_uuid_dict:
                return self.edge_uuid_dict[key]
            raise KeyError(f"Cannot find any Node or Edge with UUID '{key}'.")

        raise TypeError(
            f"Key '{key}' should be a node name string or "
            'a ("source", "target") tuple of strings.'
        )

    def __contains__(self, key: Union[str, UUID, Tuple[str, str]]):
        try:
            return bool(self.__getitem__(key))
        except KeyError:
            return False

    def __copy__(self):
        cp = Metadata.__copy__(self)
        cp._node_uuid_dict = None
        cp._edge_uuid_dict = None
        return cp

    def __deepcopy__(self, memo):
        cp = Metadata.__deepcopy__(self, memo)
        cp._node_uuid_dict = None
        cp._edge_uuid_dict = None
        return cp

    @property
    def nodes(self) -> List[Node]:
        """Nodes as a list."""
        return self.node_list

    @nodes.setter
    def nodes(self, value: Optional[Iterable[Node]]):
        self._nodes = OrderedDict()
        if isinstance(value, dict):
            value = value.values()
        if value:
            for node in value:
                self.add_node(node)

    @property
    def node_count(self) -> int:
        """Number of nodes in the graph."""
        return len(self._nodes)

    @property
    def node_list(self) -> List[Node]:
        """Nodes as a list."""
        return list(self._nodes.values())

    @property
    def node_dict(self) -> Dict[str, Node]:
        """Node dictionary by node name."""
        return self._nodes

    @property
    def node_uuid_dict(self) -> Dict[UUID, Node]:
        """Node dictionary by node UUID."""
        if self._node_uuid_dict is None:
            self._node_uuid_dict = {n.uuid: n for n in self.node_gen}
        return self._node_uuid_dict

    @property
    def node_gen(self) -> Generator[Node, None, None]:
        """Yield nodes."""
        yield from self._nodes.values()

    @property
    def edges(self) -> List[Edge]:
        """Edges as a list."""
        return self.edge_list

    @edges.setter
    def edges(self, value: Optional[Iterable[Edge]]):
        self._edges = OrderedDict()
        self._directed_edges = defaultdict(lambda: defaultdict(list))
        self._reversed_edges = defaultdict(lambda: defaultdict(list))
        if isinstance(value, dict):
            for source in value:
                for target in value[source]:
                    for edge in value[source][target]:
                        self.add_edge(edge)
        elif value:
            for edge in value:
                self.add_edge(edge)

    @property
    def edge_list(self) -> List[Edge]:
        """Edges as a list."""
        return list(self._edges.values())

    @property
    def edge_dict(self) -> Dict[str, Edge]:
        """Edge dictionary by edge name."""
        return self._edges

    @property
    def edge_uuid_dict(self) -> Dict[UUID, Edge]:
        """Edge dictionary by node UUID."""
        if self._edge_uuid_dict is None:
            self._edge_uuid_dict = {e.uuid: e for e in self.edge_gen}
        return self._edge_uuid_dict

    @property
    def directed_edges(self) -> Dict[str, Dict[str, List[Edge]]]:
        """Nested edge dictionary from source name to target name to a list of edges."""
        return self._directed_edges

    @property
    def reversed_edges(self) -> Dict[str, Dict[str, List[Edge]]]:
        """Nested edge dictionary from target name to source name to a list of edges."""
        return self._reversed_edges

    @property
    def edge_gen(self) -> Generator[Edge, None, None]:
        """Yield edges."""
        for source in self._directed_edges:
            for target in self._directed_edges[source]:
                yield from self._directed_edges[source][target]

    @property
    def edge_count(self) -> int:
        """Number of edges in the graph."""
        return len(self._edges)

    def add_node(self, node: Node):
        """Add a new node to this graph.

        If the node instance already exists in the graph, it is ignored.

        Arguments:
            node: Node to add.
        """
        if not isinstance(node, Node):
            raise TypeError("%r is not an instance of Node but of %r." % (node, type(node)))

        # Append own node if not exists.
        if node.name in self._nodes:
            if node == self._nodes[node.name]:
                return
            raise ValueError(f"Another Node named '{node.name}' already exists in this Graph.")
        if node.uuid in self.node_uuid_dict:
            if node == self.node_uuid_dict[node.uuid]:
                return
            raise ValueError(f"Another Node with UUID '{node.uuid}' already exists in this Graph.")
        self._nodes[node.name] = node
        self.node_uuid_dict[node.uuid] = node

        # Append parent
        if self.add_parents and node.parent:
            self.add_node(node.parent)

        # Append children
        if self.add_children and node.children:
            for child in node.children:
                self.add_node(child)

    def del_node(self, node: Union[Node, str, UUID], inherit: bool = False):
        """Remove a node and related edges from the graph by name or Node instance.

        Arguments:
            node: Node to remove.
            inherit: Whether to inherit hierarchy for underlying nodes to the parent.
        """
        if isinstance(node, str):
            node = self._nodes[node]
        elif isinstance(node, UUID):
            node = self.node_uuid_dict[node]

        if inherit and node.parent and node.children:
            for child in node.children:  # Is bus does not carry over to new parent.
                child.is_bus = False
            node.parent.children = node.parent.children + node.children
        node.children = []
        node.parent = None
        for e in list(self.edges_from(node)):
            self.del_edge(e)
        for e in list(self.edges_to(node)):
            self.del_edge(e)
        self.node_uuid_dict.pop(node.uuid)
        self._nodes.pop(node.name)

    def add_edge(self, edge: Edge):
        """Add a new edge to the graph. Source and target need to exist in the graph.

        Arguments:
            edge: Edge to add.

        Raises:
            ValueError: if the source or target doesn't exist or the edge instance already does.
        """
        source = edge.source.name
        target = edge.target.name
        if source not in self.node_dict:
            raise ValueError("Source node %r does not exist in graph." % edge.source)
        if target not in self.node_dict:
            raise ValueError("Target node %r does not exist in graph." % edge.target)
        if edge.name in self._edges:
            if edge == self._edges[edge.name]:
                return
            raise ValueError(f"Edge name '{edge.name}' already exists in the graph.")
        if edge.uuid in self.edge_uuid_dict:
            if edge == self.edge_uuid_dict[edge.uuid]:
                return
            raise ValueError(f"Edge UUID '{edge.name}' already exists in the graph.")
        self._edges[edge.name] = edge
        self.edge_uuid_dict[edge.uuid] = edge
        self._directed_edges[source][target].append(edge)
        self._reversed_edges[target][source].append(edge)

    def del_edge(self, edge: Union[Edge, str, UUID]):
        """Remove an edge from the graph."""
        if isinstance(edge, str):
            edge = self._edges[edge]
        elif isinstance(edge, UUID):
            edge = self.edge_uuid_dict[edge]

        self.edge_uuid_dict.pop(edge.uuid)
        self._edges.pop(edge.name)

        source = edge.source.name
        target = edge.target.name

        self._directed_edges[source][target].remove(edge)
        if not self._directed_edges[source][target]:
            self._directed_edges[source].pop(target)

        self._reversed_edges[target][source].remove(edge)
        if not self._reversed_edges[source][target]:
            self._reversed_edges[source].pop(target)

    @property
    def node_kinds(self) -> List[str]:
        """List of unique node kinds in the graph."""
        return self.get_kinds(self.node_gen)

    @property
    def edge_kinds(self) -> List[str]:
        """List of unique edge kinds in the graph."""
        return self.get_kinds(self.edge_gen)

    def get_kinds(self, elements: Union[Iterable[Node], Iterable[Edge]]) -> List[str]:
        """Get an alphabetically sorted list of unique node/edge kinds in the graph."""
        return sorted(set(elem.kind for elem in elements), key=str)

    def get_nodes_by_kind(self, kind: str) -> List[Node]:
        """Get nodes/edges by kind."""
        return [node for node in self.node_gen if node.kind == kind]

    def get_edges_by_kind(self, kind: str) -> List[Edge]:
        """Get edges by kind."""
        return [edge for edge in self.edge_gen if edge.kind == kind]

    @property
    def node_weight_labels(self) -> List[str]:
        """List of unique node weight labels in the graph."""
        return self.get_weight_labels(self.node_gen)

    @property
    def edge_weight_labels(self) -> List[str]:
        """List of unique edge weight labels in the graph."""
        return self.get_weight_labels(self.edge_gen)

    def get_weight_labels(self, elements: Union[Iterable[Node], Iterable[Edge]]) -> List[str]:
        """Get an alphabetically sorted list of unique labels of node/edge weights."""
        labels: Set[str] = set()
        for elem in elements:
            labels.update(elem.weights.keys())
        return sorted(labels, key=str)

    @property
    def node_labels(self) -> List[str]:
        """Alphabetically sorted list of unique node labels in the graph."""
        labels = {label for node in self.node_gen for label in node.labels}
        return sorted(labels, key=str)

    @property
    def edge_labels(self) -> List[str]:
        """Alphabetically sorted list of unique edge labels in the graph."""
        labels = {label for edge in self.edge_gen for label in edge.labels}
        return sorted(labels, key=str)

    @property
    def roots(self) -> List[Node]:
        """List of roots in the graph."""
        return [node for node in self.node_gen if node.is_root]

    @property
    def leafs(self) -> List[Node]:
        """List of roots in the graph."""
        return [node for node in self.node_gen if node.is_leaf]

    @property
    def max_depth(self) -> int:
        """Maximum node depth in the graph."""
        return max([node.depth for node in self.leafs], default=0)

    def edges_from(self, source: Union[str, Node]) -> Generator[Edge, None, None]:
        """Yield edges originating from a given source node."""
        if isinstance(source, Node):
            source = source.name
        for target in self._directed_edges[source]:
            yield from self._directed_edges[source][target]

    def targets_of(self, source: Union[str, Node]) -> Generator[Node, None, None]:
        """Yield target nodes of a given source node."""
        if isinstance(source, Node):
            source = source.name
        yield from [
            self._nodes[target]
            for target in self._directed_edges[source]
            if self._directed_edges[source][target]
        ]

    def edges_to(self, target: Union[str, Node]) -> Generator[Edge, None, None]:
        """Yield edges towards a given target node."""
        if isinstance(target, Node):
            target = target.name
        for source in self._reversed_edges[target]:
            yield from self._reversed_edges[target][source]

    def sources_of(self, target: Union[str, Node]) -> Generator[Node, None, None]:
        """Yield source nodes of a given target node."""
        if isinstance(target, Node):
            target = target.name
        yield from [
            self._nodes[source]
            for source in self._reversed_edges[target]
            if self._reversed_edges[target][source]
        ]

    def edges_between(
        self,
        source: Union[str, Node],
        target: Union[str, Node],
        inherit: bool = False,
        loops: bool = True,
    ) -> Generator[Edge, None, None]:
        """Yield edges between source and target node.

        Arguments:
            source: Source node.
            target: Target node.
            inherit: Whether to include edges between descendants of given nodes.
            loops: Whether to include self-loop edges.
        """
        if source == target and not loops:
            return
        source_node = source if isinstance(source, Node) else self._nodes[source]
        target_node = target if isinstance(target, Node) else self._nodes[target]
        sources, targets = [source_node.name], [target_node.name]
        if inherit:
            sources.extend(n.name for n in source_node.descendant_gen)
            targets.extend(n.name for n in target_node.descendant_gen)

        for source in sources:
            for target in targets:
                if source == target and not loops:
                    continue
                yield from self._directed_edges[source][target]

    def edges_between_all(
        self,
        sources: Iterable[Union[str, Node]],
        targets: Iterable[Union[str, Node]],
        inherit: bool = False,
        loops: bool = True,
    ) -> Generator[Edge, None, None]:
        """Yield all edges between a set of source and a set of target nodes.

        Arguments:
            sources: Source nodes.
            targets: Target nodes.
            inherit: Whether to include edges between descendants of given nodes.
            loops: Whether to include self-loop edges.
        """
        for source in sources:
            for target in targets:
                yield from self.edges_between(source, target, inherit=inherit, loops=loops)

    def get_graph_slice(
        self,
        nodes: Optional[Iterable[Node]] = None,
        edges: Optional[Iterable[Edge]] = None,
        inherit: bool = False,
    ) -> "Graph":
        """Return the graph slice with only the given nodes and the edges between those.

        Arguments:
            nodes: Optional set of nodes to include in the new deep copy.
                Defaults to all.
            edges: Optional set of edges to include in the new deep copy.
                Defaults to all between selected nodes.
            inherit: Whether to include child nodes of the given nodes and edges
                between them (unless edges are explicitly specified).

        Note:
            This returns a deepcopy, so the copied nodes and edges do NOT share any
            changes! All parent and child nodes not in the list are excluded.
        """
        nodes = self.nodes if nodes is None else list(nodes)
        edges = self.edges_between_all(nodes, nodes, inherit) if edges is None else list(edges)

        # Get a deepcopy to prevent changing nodes in the current graph instance.
        graph = deepcopy(Graph(nodes=nodes, edges=edges, add_children=inherit))

        # Reinstate relationships only between given nodes.
        graph_nodes = graph.nodes
        for node in graph_nodes:
            if node.parent:
                node.parent = graph[node.parent.name] if node.parent in graph.nodes else None
            node.children = [c for c in node.children if c in graph.nodes]
            if node.is_bus and not node.parent:
                node.is_bus = False

        return graph

    def get_node_selection(
        self,
        node_kinds: Optional[List[str]] = None,
        edge_kinds: Optional[List[str]] = None,
        depth: int = 2,
        selection_mode: str = "dependent",
    ) -> List[Node]:
        """Select specific nodes from this graph in a structured order.

        Arguments:
            node_kinds: The kind of nodes to be selected.
            edge_kinds: The kind of edges to be selected.
            depth: The maximum depth of node to be selected.
            selection_mode: The selection mode. Either 'dependent' or 'independent'.

        Note:
            The selection mode argument determines how nodes of different kinds are
            selected. If the selection mode is set to 'dependent', the first node kind
            in the `node_kinds` list is considered to be the 'lead node kind'.
            Nodes of different kind than the lead node kind, are only selected if they
            have a dependency with at least one of the selected nodes of the lead node
            kind. If the selection mode is set to 'independent' this dependency
            condition is dropped.
        """
        nkinds = node_kinds or self.node_kinds
        ekinds = edge_kinds or self.edge_kinds
        return utils.select_nodes(self, nkinds, ekinds, depth, selection_mode)

    def get_edge_selection(
        self, nodes: Optional[List[Node]] = None, edge_kinds: Optional[List[str]] = None
    ) -> List[Edge]:
        """Select specific edges from this graph.

        Arguments:
            nodes: The list of nodes between which the edges must be selected.
            edge_kinds: The kinds of edges to be selected.

        Returns:
            List of selected edges.
        """

        nlist = nodes or self.get_node_selection(edge_kinds=edge_kinds)
        ekinds = edge_kinds or self.edge_kinds
        ekinds = sorted(set(ekinds))

        return [e for e in self.edges_between_all(sources=nlist, targets=nlist) if e.kind in ekinds]

    def get_node_and_edge_selection(
        self,
        node_kinds: Optional[List[str]] = None,
        edge_kinds: Optional[List[str]] = None,
        depth: int = 2,
        selection_mode: str = "dependent",
    ) -> Tuple[List[Node], List[Edge]]:
        """Select specific nodes and edges from this graph in a structured order.

        Arguments:
            node_kinds: The kind of nodes to be selected.
            edge_kinds: The kind of edges to be selected.
            depth: The maximum depth of node to be selected.
            selection_mode: The selection mode. Either 'dependent' or 'independent'.

        Note:
            The selection mode argument determines how nodes of different kinds are
            selected. If the selection mode is set to 'dependent', the first node kind
            in the `node_kinds` list is considered to be the 'lead node kind'.
            Nodes of different kind than the lead node kind, are only selected if they
            have a dependency with at least one of the selected nodes of the lead node
            kind. If the selection mode is set to 'independent' this dependency
            condition is dropped.
        """

        nodes = self.get_node_selection(
            node_kinds=node_kinds,
            edge_kinds=edge_kinds,
            depth=depth,
            selection_mode=selection_mode,
        )

        edges = self.get_edge_selection(nodes=nodes, edge_kinds=edge_kinds)

        return nodes, edges

    def get_hierarchy_dict(self, roots: Optional[List[Node]] = None, levels: Optional[int] = None):
        """Return a dictionary of the (partial) hierarchical node structure.

        Arguments:
            roots: Root nodes of the hierarchy to calculate.
            levels: Number of levels to include below the roots.
        """
        if roots is None:
            roots = self.roots

        if levels is None:
            return {root.name: self.get_hierarchy_dict(root.children) for root in roots}
        elif levels > 0:
            return {
                root.name: self.get_hierarchy_dict(root.children, levels=levels - 1)
                for root in roots
            }

        return {root.name: dict() for root in roots}

    def get_adjacency_matrix(
        self,
        nodes: Optional[Union[List[Node], List[str]]] = None,
        inherit: bool = False,
        loops: bool = False,
        only: Optional[List[str]] = None,
        convention: Convention = Convention.IR_FAD,
    ) -> Union["np.ndarray", List[List[float]]]:
        """Convert graph data into a numerical adjacency matrix.

        Arguments:
            nodes: Optional list of nodes for which to get the adjacency matrix.
            inherit: Whether to count weights between children of the given nodes.
            loops: Whether to calculate self-loops from a node to itself.
            only: Optional subset of edge weights to consider. See [`Edge`][ragraph.edge.Edge] for
                default edge weight implementation.

        Returns:
            Adjacency matrix as a 2D numpy array if numpy is present. Otherwise it will
            return a 2D nested list.
        """
        from ragraph.io.matrix import to_matrix

        return to_matrix(
            self,
            rows=nodes,
            cols=nodes,
            inherit=inherit,
            loops=loops,
            only=only,
            convention=convention,
        )

    def get_mapping_matrix(
        self,
        rows: Optional[Union[List[Node], List[str]]] = None,
        cols: Optional[Union[List[Node], List[str]]] = None,
        inherit: bool = False,
        loops: bool = False,
        only: Optional[List[str]] = None,
        convention: Convention = Convention.IR_FAD,
    ) -> Union["np.ndarray", List[List[float]]]:
        """Convert graph data into a numerical mapping matrix.

        Arguments:
            rows: Nodes representing the matrix rows.
            cols: Nodes representing the matrix columns if different from the rows.
            inherit: Whether to count weights between children of the given nodes.
            loops: Whether to calculate self-loops from a node to itself.
            only: Optional subset of edge weights to consider. See [`Edge`][ragraph.edge.Edge] for
                default edge weight implementation.

        Returns:
            Adjacency matrix as a 2D numpy array if numpy is present. Otherwise it will
            return a 2D nested list.
        """
        from ragraph.io.matrix import to_matrix

        return to_matrix(
            self,
            rows=rows,
            cols=cols,
            inherit=inherit,
            loops=loops,
            only=only,
            convention=convention,
        )

    def get_ascii_art(
        self,
        nodes: Optional[List[Node]] = None,
        edge: str = "X",
        diag: str = "\u25a0",
        show: bool = False,
        convention: Convention = Convention.IR_FAD,
    ) -> Optional[str]:
        """Get a unicode ASCII art representation of a binary adjacency matrix for a
        given set of nodes.

        Arguments:
            nodes: Nodes to include in the art.
            edge: Mark to use when there's an edge between nodes. (X by default)
            diag: Mark to use on the diagonal.
            show: Whether to directly print the ASCII art.

        Returns:
            ASCII art representation of this graph.
        """
        if nodes is None:
            nodes = self.leafs
        if not nodes:
            raise ValueError("Empty graph, cannot create ASCII art.")

        namelens = [len(n.name) for n in nodes]
        maxlen = max(namelens, default=0)
        dim = len(nodes)

        ddd = "\u2500\u2500\u2500"  # ---
        pad = maxlen * " "

        # Grid lines
        topline = pad + "\u250c" + (dim - 1) * (ddd + "\u252c") + ddd + "\u2510"
        sepline = pad + "\u251c" + (dim - 1) * (ddd + "\u253c") + ddd + "\u2524"
        endline = pad + "\u2514" + (dim - 1) * (ddd + "\u2534") + ddd + "\u2518"

        lines = [topline]

        for i, row in enumerate(nodes):
            line = (maxlen - namelens[i]) * " " + row.name + "\u2525"
            for j, col in enumerate(nodes):
                if i == j:
                    mark = diag
                else:
                    if convention == Convention.IR_FAD:
                        src = col
                        tgt = row
                    elif convention == Convention.IC_FBD:
                        src = row
                        tgt = col
                    else:
                        raise ValueError("Unknown matrix convention type.")
                    if self._directed_edges.get(src.name, dict()).get(tgt.name, False):
                        mark = edge
                    else:
                        mark = " "
                line += " {} \u2502".format(mark)

            lines.append(line)
            lines.append(sepline)
        lines[-1] = endline
        txt = "\n".join(lines)
        if show:
            print(txt)
            return None
        else:
            return txt

    @property
    def json_dict(self) -> Dict[str, Any]:
        """JSON dictionary representation."""
        return self.as_dict(use_uuid=True)

    def as_dict(self, use_uuid: bool = False) -> Dict[str, Any]:
        """Return a copy as a (serializable) dictionary.

        Arguments:
            use_uuid: Whether to use UUIDs instead of names.

        Returns:
            nodes: Node names or UUIDs to Node dictionaries.
            kind: Kind as str.
            labels: Labels as list of str.
            weights: Weights as dict.
            annotations: Annotations as a dictionary.
            uuid: UUID as str if toggled.

        """
        if use_uuid:
            return dict(
                nodes={str(n.uuid): n.json_dict for n in self.nodes},
                edges={str(e.uuid): e.json_dict for e in self.edges},
                name=self.name,
                kind=self.kind,
                labels=self.labels,
                weights=self.weights,
                annotations=self.annotations.as_dict(),
                uuid=str(self.uuid),
            )
        else:
            return dict(
                nodes={n.name: n.as_dict(use_uuid=False) for n in self.nodes},
                edges={e.name: e.as_dict(use_uuid=False) for e in self.edges},
                name=self.name,
                kind=self.kind,
                labels=self.labels,
                weights=self.weights,
                annotations=self.annotations.as_dict(),
            )

    def check_consistency(self, raise_error: bool = True) -> bool:
        """Check the consistency of this graph.

        Arguments:
            raise_error: Whether to raise an error instead of returning a bool.

        Returns:
            Whether nodes aren't their own ancestor/descendant and if all their children
            and parents exist in the graph. Raises an error for inconsistencies if
            `raise_error` is set to `True`.
        """
        consistent = True

        try:
            for node in self.node_list:
                a = node
                while a.parent:
                    if a.parent == node:
                        raise ConsistencyError("Node {} is in its own ancestors.".format(node))
                    a = a.parent
                ds = node.children
                while ds:
                    if node in ds:
                        raise ConsistencyError("Node {} is in its own descendants.".format(node))
                    ds = [c for d in ds for c in d.children]
                if node.parent and node.parent not in self.node_list:
                    raise ConsistencyError(
                        "Node {}'s parent {} is missing in the graph.".format(node, node.parent)
                    )
                if node.parent and node not in node.parent.children:
                    raise ConsistencyError(
                        "Node {}'s does not occur in parent {}'s children.".format(
                            node, node.parent
                        )
                    )
                for child in node.children:
                    if child not in self.node_list:
                        raise ConsistencyError(
                            "Node {}'s child {} is missing in the graph.".format(node, child)
                        )
                    if child.parent != node:
                        raise ConsistencyError(
                            "Node {}'s child has a different parent {}.".format(node, child.parent)
                        )
                if node.is_bus and not node.parent:
                    raise ConsistencyError(
                        "Node {} is a bus node, but has no parent to be it for.".format(node)
                    )

            for edge in self.edge_list:
                if edge.source.name not in self.node_dict:
                    raise ConsistencyError(f"Edge source not in Graph: {repr(edge.source)}")
                if edge.target.name not in self.node_dict:
                    raise ConsistencyError(f"Edge target not in Graph: {repr(edge.source)}")

        except ConsistencyError as e:
            consistent = False
            if raise_error:
                raise e

        return consistent


class GraphView(Graph):
    """A view on a [`Graph`][ragraph.graph.Graph] object. It works exactly like the
    [`Graph`][ragraph.graph.Graph] object, except for that the nodes and edges are filtered
    according to the view function.

    Arguments:
        graph: Graph to provide a view on.
        view_func: View function that filters the [`Graph`][ragraph.graph.Graph]'s nodes and edges.
        view_kwargs: Optional arguments to pass to the view function.
    """

    def __init__(
        self,
        graph: Graph,
        view_func: Optional[
            Callable[
                [Any],
                Tuple[
                    Union[Iterable[Node], Dict[str, Node]],
                    Union[Iterable[Edge], Dict[str, Edge]],
                ],
            ]
        ] = None,
        view_kwargs: Optional[Dict[str, Any]] = None,
    ):
        Metadata.__init__(
            self,
            name=graph.name,
            kind=graph.kind,
            labels=graph.labels,
            weights=graph.weights,
            annotations=graph.annotations,
        )
        self._graph = graph
        self._view_func = view_func
        self._view_kwargs = view_kwargs

        self._vnodes: Optional[Dict[str, Node]] = None
        self._vnode_uuid_dict: Optional[Dict[UUID, Node]] = None
        self._vedges: Optional[Dict[str, Edge]] = None
        self._vedge_uuid_dict: Optional[Dict[UUID, Edge]] = None
        self._vdirected_edges: Optional[defaultdict] = None
        self._vreversed_edges: Optional[defaultdict] = None
        self.update()

    @property
    def graph(self) -> Graph:
        """Graph to provide a view on."""
        return self._graph

    @graph.setter
    def graph(self, value: Graph):
        self._graph = value
        self.reset()

    @property
    def view_func(
        self,
    ) -> Optional[
        Callable[
            [Any],
            Tuple[
                Union[Iterable[Node], Dict[str, Node]],
                Union[Iterable[Edge], Dict[str, Edge]],
            ],
        ]
    ]:
        """View function that filters the [`Graph`][ragraph.graph.Graph]'s nodes and edges."""
        return self._view_func

    @view_func.setter
    def view_func(
        self,
        value: Optional[
            Callable[
                [Any],
                Tuple[
                    Union[Iterable[Node], Dict[str, Node]],
                    Union[Iterable[Edge], Dict[str, Edge]],
                ],
            ]
        ],
    ):
        self._view_func = value
        self.reset()

    @property
    def view_kwargs(self) -> Dict[str, Any]:
        """Optional arguments to pass to the view function."""
        if self._view_kwargs is None:
            return dict()
        return self._view_kwargs

    @view_kwargs.setter
    def view_kwargs(self, value: Dict[str, Any]):
        self._view_kwargs = value
        self.reset()

    def update(self, **kwargs):
        """Apply the set view function with arguments."""
        # Just proxy if no view function is set.
        if self.view_func is None:
            return self.proxy()

        # Get view filter results.
        view_kwargs = kwargs or self.view_kwargs
        nodes, edges = self.view_func(self.graph, **view_kwargs)

        # Cast to dicts.
        ndict = nodes if isinstance(nodes, dict) else {n.name: n for n in nodes}
        edict = edges if isinstance(edges, dict) else {e.name: e for e in edges}

        # Populate directed/reversed edges.
        directed_edges = defaultdict(lambda: defaultdict(list))
        reversed_edges = defaultdict(lambda: defaultdict(list))
        for e in edict.values():
            directed_edges[e.source.name][e.target.name].append(e)
            reversed_edges[e.target.name][e.source.name].append(e)

        # Update private views.
        self._vnodes, self._vedges = ndict, edict
        self._vnode_uuid_dict = {n.uuid: n for n in ndict.values()}
        self._vedge_uuid_dict = {e.uuid: e for e in edict.values()}
        self._vdirected_edges, self._vreversed_edges = directed_edges, reversed_edges

        # Save view kwargs after view succeeded.
        self._view_kwargs = view_kwargs

    def proxy(self):
        """Undo any filtering and just set this view to proxy the Graph 1:1."""
        self._vnodes, self._vedges = self.graph._nodes, self.graph._edges
        self._vnode_uuid_dict = self.graph.node_uuid_dict
        self._vedge_uuid_dict = self.graph.edge_uuid_dict
        self._vdirected_edges = self.graph._directed_edges
        self._vreversed_edges = self.graph._reversed_edges

    def reset(self):
        """Reset the private properties after the original graph might have changed."""
        self._vnodes = None
        self._vnode_uuid_dict = None
        self._vedges = None
        self._vedge_uuid_dict = None
        self._vdirected_edges = None
        self._vreversed_edges = None

    @property  # type: ignore
    def _nodes(self) -> Optional[Dict[str, Node]]:  # type: ignore
        if self._vnodes is None:
            self.update()
        return self._vnodes

    @_nodes.setter
    def _nodes(self, value: Dict[str, Node]):
        self.graph._nodes = value
        self.reset()

    @property  # type: ignore
    def node_uuid_dict(self) -> Optional[Dict[UUID, Node]]:  # type: ignore
        if self._vnode_uuid_dict is None:
            self.update()
        return self._vnode_uuid_dict

    @property  # type: ignore
    def _edges(self) -> Optional[Dict[str, Edge]]:  # type: ignore
        if self._vedges is None:
            self.update()
        return self._vedges

    @_edges.setter
    def _edges(self, value: Dict[str, Edge]):
        self.graph._edges = value
        self.reset()

    @property  # type: ignore
    def edge_uuid_dict(self) -> Optional[Dict[UUID, Edge]]:  # type: ignore
        if self._vedge_uuid_dict is None:
            self.update()
        return self._vedge_uuid_dict

    @property  # type: ignore
    def _directed_edges(self) -> defaultdict:  # type: ignore
        if self._vdirected_edges is None:
            self.update()
        assert self._vdirected_edges is not None
        return self._vdirected_edges

    @_directed_edges.setter
    def _directed_edges(self, value: defaultdict):
        self.graph._directed_edges = value
        self.reset()

    @property  # type: ignore
    def _reversed_edges(self) -> defaultdict:  # type: ignore
        if self._vreversed_edges is None:
            self.update()
        assert self._vreversed_edges is not None
        return self._vreversed_edges

    @_reversed_edges.setter
    def _reversed_edges(self, value: defaultdict):
        self.graph._reversed_edges = value
        self.reset()

    def add_node(self, node: Node):
        self.graph.add_node(node)
        self.reset()

    def del_node(self, node: Union[Node, str, UUID], inherit: bool = False):
        self.graph.del_node(node, inherit=inherit)
        self.reset()

    def add_edge(self, edge: Edge):
        self.graph.add_edge(edge)
        self.reset()

    def del_edge(self, edge: Union[Edge, str, UUID]):
        self.graph.del_edge(edge)
        self.reset()
