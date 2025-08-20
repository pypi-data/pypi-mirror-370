"""Abstracted analysis base classes and methods."""

import inspect
from abc import ABC, abstractmethod
from copy import deepcopy
from functools import wraps
from logging import DEBUG
from textwrap import dedent
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from ragraph.analysis import _utils, logger
from ragraph.generic import Bound
from ragraph.graph import Graph
from ragraph.node import Node


class Cast(ABC):
    """Cast for parameters."""

    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def __call__(self, value: Any) -> Any:
        """Cast a value."""
        pass


class GraphCast(Cast):
    """Just check whether the argument is a Graph."""

    def __init__(self):
        pass

    def __call__(self, value: Any) -> Graph:
        if not isinstance(value, Graph):
            raise ValueError(f"Please supply a Graph object, got '{value}'.")
        return value


class NodeCast(Cast):
    """Cast node names into instances.

    Arguments:
        graph: Graph to fetch nodes from.
    """

    def __init__(self, graph: Optional[Graph]):
        self.graph = graph

    def __call__(self, value: Any) -> Optional[Node]:
        if value is None:
            return value
        if self.graph is None:
            raise ValueError("Graph must be set before cast is possible.")
        if isinstance(value, Node):
            if value.name not in self.graph or value not in self.graph.nodes:
                raise ValueError(f"Node '{value}' does not occur in the graph.")
            return value
        return self.graph.node_dict[value]


class NodesCast(Cast):
    """Cast leaf node names into node instances. If an empty list is provided, take
    child nodes below a specific root node or all leafs in the graph.
    """

    def __init__(self, graph: Optional[Graph], root: Optional[Union[Node, str]] = None):
        self.graph = graph
        self.root = root

    def __call__(self, value: Optional[List[str]] = None) -> List[Node]:
        if self.graph is None:
            raise ValueError("Graph must be set before cast is possible.")
        cast = NodeCast(self.graph)
        if value is None:
            root = cast(self.root)
            nodes = self.graph.leafs if root is None else root.children
        else:
            nodes = [n for n in (cast(node) for node in value) if n is not None]
        return nodes


class LeafsCast(Cast):
    """Cast leaf node names into node instances. If an empty list is provided, take
    leaf nodes below a specific root node or all leafs in the graph.
    """

    def __init__(self, graph: Optional[Graph], root: Optional[str] = None):
        self.graph = graph
        self.root = root

    def __call__(self, value: Optional[List[str]] = None) -> List[Node]:
        if self.graph is None:
            raise ValueError("Graph must be set before cast is possible.")
        cast = NodeCast(self.graph)
        if value is None:
            root = cast(self.root)
            leafs = (
                self.graph.leafs if root is None else [n for n in root.descendant_gen if n.is_leaf]
            )
        else:
            leafs = [n for n in (cast(leaf) for leaf in value) if n is not None]
        return leafs


class MethodCast(Cast):
    """Cast a Callable to ensure the method is fetched when it's an Analysis object."""

    def __init__(self):
        pass

    def __call__(self, value: Callable):
        return value.method if isinstance(value, Analysis) else value


class Parameter:
    """Analysis parameter.

    Arguments:
        name: Argument name.
        description: Argument description.
        type: Argument instance type.
        default: Default argument value.
        cast: Optional cast to use for incoming execution values.
        enum: Allowed values if this parameter is an enumeration.
        lower: Lower bound for numeric values (inclusive).
        upper: Upper bound for numeric values (inclusive).
    """

    def __init__(
        self,
        name: str,
        type: Any,
        description: str = "",
        default: Any = None,
        cast: Any = None,
        enum: Optional[Set[Any]] = None,
        lower: Optional[Bound] = None,
        upper: Optional[Bound] = None,
    ):
        self.name = name
        self.description = description
        self.type = type
        self.lower = lower
        self.upper = upper

        # Use built-in conversion for trivial types.
        if cast is None and type in (float, int, str, bool):
            self.cast = type
        else:
            self.cast = cast

        # Cast default, enum, and bounds if possible, else just use input.
        if self.cast is None:
            self.default = default
            self.enum = set(enum) if enum is not None else None
        else:
            self.default = self.cast(default) if default is not None else None
            self.enum = {self.cast(i) for i in enum} if enum is not None else None

    def __str__(self) -> str:
        msg = f"{self.name}: {self.description} "

        if self.default is not None:
            msg += f"Defaults to {self.default}. "

        if self.enum:
            msg += f"Must be one of: '{self.enum}'. "

        if self.lower is not None or self.upper is not None:
            lb = "{}{}".format(
                "(" if self.lower is None or self.lower.inclusive else "[",
                "-inf" if self.lower is None else self.lower.value,
            )
            ub = "{}{}".format(
                "inf" if self.upper is None else self.upper.value,
                ")" if self.upper is None or not self.upper.inclusive else "]",
            )
            msg += f"Bounds: {lb}, {ub}. "

        msg += f"Type should satisfy {self.type}. ".replace("typing.", "")
        return msg

    def parse(self, value: Any) -> Any:
        """Check and parse a value."""
        if self.cast is not None:
            try:
                value = self.cast(value)
            except Exception:
                raise ValueError(
                    f"Error while casting {self.name} value '{value}' using "
                    f"'{self.cast}' into a '{self.type}'."
                )
        if self.enum is not None and value not in self.enum:
            raise ValueError(f"Value '{value}' is not allowed, try one of '{self.enum}'.")
        if self.lower is not None:
            assert value > self.lower
        if self.upper is not None:
            assert value < self.upper
        return value


graph = Parameter(
    "graph",
    Graph,
    description="Graph data object.",
    cast=GraphCast(),
)

root = Parameter(
    "root",
    Optional[Union[str, Node]],
    description="Root node to fetch nodes from.",
    cast=NodeCast(None),
)

nodes = Parameter(
    "nodes",
    Optional[Union[List[str], List[Node]]],
    description="Selected nodes to apply analysis on.",
    cast=NodesCast(None, None),
)


leafs = Parameter(
    "leafs",
    Optional[Union[List[str], List[Node]]],
    description="Selected leaf nodes.",
    cast=LeafsCast(None, None),
)


edge_weights = Parameter(
    "edge_weights",
    Optional[List[str]],
    description="Edge weights to consider during calculations.",
)


names = Parameter(
    "names",
    bool,
    description="Whether to return node names instead of instances.",
    default=False,
)


inplace = Parameter(
    "inplace",
    bool,
    description="Whether to update the input graph inplace or return a copy.",
    default=True,
)

inherit = Parameter(
    "inherit",
    bool,
    description="Whether edges between descendants of nodes should be taken "
    + "into account (if applicable).",
    default=True,
)

loops = Parameter(
    "loops",
    bool,
    description="Whether self-loop edges should be taken into account (if applicable).",
    default=False,
)

safe = Parameter(
    "safe",
    bool,
    description="Whether to check and cast input arguments to their appropriate types.",
    default=True,
)


class Analysis:
    """Analysis interface.

    Arguments:
        name: Analysis name.
        description: Analysis description.
        parameters: Analysis parameter mapping.
    """

    _default_parameters: Dict[str, Parameter] = dict()
    _returns: Optional[List[str]] = None

    def __init__(
        self,
        name: str,
        description: str = "",
        parameters: Optional[Dict[str, Parameter]] = None,
    ):
        self.name = name
        self.description = dedent(description)

        # Store parameters as a dictionary mapping
        self.parameters = deepcopy(self._default_parameters)
        if parameters is not None:
            self.parameters.update(deepcopy(parameters))

        # Initialize method with a placeholder.
        self.method = lambda *a, **kw: None

    def __str__(self) -> str:
        # Basic name and description
        msg = f"{self.name}"

        if self.description:
            msg += f"\n\n{self.description}"

        # Arguments section
        msg += "\n\nArguments:\n    "
        msg += "\n    ".join([str(p) for p in self.parameters.values()])

        # Returns section
        if self._returns is not None:
            msg += "\n\nReturns:\n    "
            msg += "\n    ".join([str(p) for p in self._returns])

        # Final newline
        msg += "\n"

        # Return with some precaution cleanup
        return msg.replace("\n\n\n", "\n\n")

    def __repr__(self) -> str:
        return str(self)

    def __call__(self, func: Callable):
        """Wrap an analysis function to apply docstring and parameter parsing."""
        self._parse_signature(func)
        self._apply_docstring(func)
        self.method = self.wrap(func)
        self.method.__dict__["analysis"] = self
        return self.method

    def _parse_signature(self, func: Callable):
        """Check whether the signature of the function matches with the parameters."""
        sig = inspect.signature(func)

        ref_keys = set(self.parameters.keys())

        diff = ref_keys.symmetric_difference(sig.parameters.keys()) - {"kwargs"}
        if diff:
            raise ValueError(
                f"Parameter mismatch. Analysis has '{ref_keys}', "
                + f"function has '{sig.parameters.keys()}'. Difference: '{diff}'."
            )

        for pname, param in self.parameters.items():
            try:
                f_param = sig.parameters[pname]
            except KeyError:
                raise ValueError(f"Parameter {pname} is missing in the signature of '{func}'.")

            # Inherit default kwarg values.
            func.__annotations__[pname] = param.type
            if f_param.default != inspect._empty:
                param.default = f_param.default

    def _apply_docstring(self, func: Callable):
        """Apply new docstring."""
        func.__doc__ = str(self)

    def _parse_parameters(self, kw: Dict[str, Any]):
        """Parse given arguments using the Parameter specifications."""
        params = self.parameters

        for pname, param in params.items():
            if pname not in kw:
                kw[pname] = param.default

        if "graph" in params:
            kw["graph"] = params["graph"].cast(kw.get("graph"))

        if "root" in params:
            params["root"].cast.graph = kw.get("graph")
            kw["root"] = params["root"].cast(kw.get("root"))

        if "nodes" in params:
            params["nodes"].cast.graph = kw.get("graph")
            params["nodes"].cast.root = kw.get("root")

        if "leafs" in params:
            params["leafs"].cast.graph = kw.get("graph")
            params["leafs"].cast.root = kw.get("root")

        for pname, param in params.items():
            kw[pname] = param.parse(kw.get(pname))

    @abstractmethod
    def wrap(self, func: Callable) -> Callable:
        """Wrapper function to wrap analysis method with."""
        pass

    def log(self, msg: str, level: int = DEBUG):
        """Dispatch a logging message."""
        logger.log(level, f"{self.name}: \n{msg}\n")


class BusAnalysis(Analysis):
    _default_parameters = {
        p.name: p for p in [graph, root, leafs, inherit, loops, edge_weights, names, safe]
    }
    _returns = [
        "Detected bus nodes (or names thereof).",
        "Remaining nonbus nodes (or names thereof).",
    ]

    def wrap(self, func: Callable) -> Callable:
        """Wrapper for all bus detection algorithms.

        Returns:
            Function that preprocesses the arguments and handles some typical/trivial
            cases where nodes are not set or too few to distinguish a bus at all.
        """

        @wraps(func)
        def wrapper(
            *args, **kw
        ) -> Union[Tuple[List[str], List[str]], Tuple[List[Node], List[Node]]]:
            # Process arguments.
            kw.update(zip(func.__code__.co_varnames, args))
            if kw.get("safe", True):
                self._parse_parameters(kw)

            # Trivial case.
            leafs = kw["leafs"]
            if len(leafs) < 3:
                self.log(f"Trivial case, too little nodes {len(leafs)} < 3.")
                bus_leafs, nonbus_leafs = [], leafs
            # Nontrivial case, need to execute:
            else:
                self.log(
                    "Applying bus analysis to leafs " + f"'{[n.name for n in kw['leafs']]}'..."
                )
                bus_leafs, nonbus_leafs = func(**kw)

            # Postprocess results.
            bus_names = [n.name for n in bus_leafs]
            nonbus_names = [n.name for n in nonbus_leafs]
            self.log(f"BUS:    {bus_names}\nNONBUS: {nonbus_names}")

            if kw["names"]:
                return bus_names, nonbus_names
            else:
                return bus_leafs, nonbus_leafs

        return wrapper


class ClusterAnalysis(Analysis):
    _default_parameters = {
        p.name: p
        for p in [
            graph,
            root,
            leafs,
            inherit,
            loops,
            edge_weights,
            inplace,
            names,
            safe,
        ]
    }

    def wrap(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kw) -> Tuple[Graph, Union[List[str], List[Node]]]:
            # Process arguments.
            kw.update(zip(func.__code__.co_varnames, args))
            if kw.get("safe", True):
                self._parse_parameters(kw)

            # Create a deepcopy and update all nodal arguments to the new nodes.
            if not kw["inplace"]:
                kw["graph"] = deepcopy(kw["graph"])
                kw["leafs"] = [kw["graph"].node_dict[n.name] for n in kw["leafs"]]
                kw["root"] = kw["graph"].node_dict[kw["root"].name] if kw.get("root") else None

            # Trivial cases where there is nothing to cluster.
            if len(kw["leafs"]) < 2:
                self.log("Trivial case, less than 2 nodes provided.")
                graph = kw["graph"]
                clusters = kw["leafs"]

            # Non-trivial case, need to execute:
            else:
                # Roots are kept as a list from hereon.
                roots = [kw["root"]] if kw.get("root") else None

                # Cut leafs loose, but preserve root(s) if set.
                for leaf in kw["leafs"]:
                    _utils.unset_parent(kw["graph"], leaf, roots)

                # Execution
                self.log("Applying cluster algorithm...")
                graph, clusters = func(**kw)
                self.log(f"Found {len(clusters)} clusters for {len(kw['leafs'])} leafs.")

            # Postprocess results.
            if kw.get("root"):
                self.log("Setting found clusters as children of root...")
                _utils.set_children(graph, kw["root"], clusters)
                clusters = [kw["root"]]

            cluster_names = [n.name for n in clusters]
            self.log(f"Cluster names: {cluster_names}")
            if kw["names"]:
                return graph, cluster_names
            return graph, clusters

        return wrapper


class SequenceAnalysis(Analysis):
    _default_parameters = {
        p.name: p
        for p in [
            graph,
            root,
            nodes,
            inherit,
            loops,
            edge_weights,
            inplace,
            names,
            safe,
        ]
    }

    def wrap(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kw) -> Tuple[Graph, Union[List[str], List[Node]]]:
            # Process arguments.
            kw.update(zip(func.__code__.co_varnames, args))
            if kw.get("safe", True):
                self._parse_parameters(kw)

            # Preprocessing
            dim = len(kw["nodes"])

            # Trivial case:
            if dim < 2:
                self.log("Trivial case, less than 2 nodes.")
                graph, nodes = kw["graph"], kw["nodes"]
            # Non-trivial case, need to execute:
            else:
                self.log("Applying sequencing algorithm...")
                graph, nodes = func(**kw)

            # Postprocessing
            node_names = [n.name for n in nodes]
            self.log(f"Result: {node_names}.")

            if kw["inplace"] and kw["root"]:
                assert len(nodes) == len(kw["root"].children)
                _utils.set_children(graph, kw["root"], nodes)
                self.log("Re-ordered root node's children in-place.")

            if kw["names"]:
                return graph, node_names
            return graph, nodes

        return wrapper


class BranchsortAnalysis(Analysis):
    _default_parameters = {
        p.name: p
        for p in [
            graph,
            root,
            nodes,
            leafs,
            inherit,
            loops,
            edge_weights,
            Parameter(
                "algo",
                Callable,
                description="Sequencing algorithm to use.",
                cast=MethodCast(),
            ),
            Parameter(
                "algo_args",
                Optional[Dict[str, Any]],
                description="Parameters to pass to the selected sequencing algorithm.",
                cast=lambda value: dict() if value is None else dict(value),
            ),
            Parameter(
                "recurse",
                bool,
                description="Whether to recursively sort branches downwards.",
                default=True,
            ),
            inplace,
            names,
            safe,
        ]
    }

    def wrap(self, func: Callable):
        @wraps(func)
        def wrapper(
            *args, **kw
        ) -> Tuple[Graph, Union[List[str], List[Node]], Union[List[str], List[Node]]]:
            # Process arguments.
            kw.update(zip(func.__code__.co_varnames, args))
            if kw.get("safe", True):
                self._parse_parameters(kw)

            # Preprocessing
            dim = len(kw["nodes"])

            # Trivial case:
            if dim == 0:
                graph, nodes, leafs = kw["graph"], [], []
            # Non-trivial case, need to execute:
            else:
                graph, nodes, leafs = func(**kw)

            # Postprocessing
            node_names = [n.name for n in nodes]
            leaf_names = [n.name for n in leafs]
            self.log(f"Node sequence: {node_names}")
            self.log(f"Leaf sequence: {leaf_names}")

            if kw["inplace"] and kw["root"]:
                assert len(nodes) == len(kw["root"].children)
                _utils.set_children(graph, kw["root"], nodes)
                self.log("Re-ordered root node's children in-place.")

            if kw["names"]:
                return graph, node_names, leaf_names
            return graph, nodes, leafs

        return wrapper
