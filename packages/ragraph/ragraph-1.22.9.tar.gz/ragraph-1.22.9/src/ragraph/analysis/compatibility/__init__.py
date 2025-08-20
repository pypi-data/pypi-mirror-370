"""# Compatibility analysis

Calculate compatibility between different variants for several functional elements.
"""

from copy import deepcopy
from itertools import combinations
from math import prod
from pathlib import Path
from typing import Callable, Dict, Generator, Iterable, List, Optional, Tuple, Union

from plotly import graph_objs as go

from ragraph.analysis.compatibility.bdd import yield_feasible_configurations
from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node
from ragraph.plot import generic, mdm

try:  # pragma: no cover
    import numpy as np

    HAVE_NUMPY = True
except ImportError:
    HAVE_NUMPY = False


def is_feasible(
    compat: Union["np.ndarray", List[List[Union[bool, int]]]], config: Tuple[int, ...]
) -> bool:
    """Return whether this configuration is feasible based on a compatibility matrix."""
    coords = combinations(config, 2)
    return all(compat[row][col] > 0 for row, col in coords)


def get_variant_score(
    variant: Node, weights: Optional[List[str]] = None, aggregation: str = "sum"
) -> float:
    """Score a single variant node as an aggregation of selected weights.

    Arguments:
        variant: Variant node.
        weights: Optional list of weights to take into account.
        aggregation: Aggregation method, either "sum" or "product".

    Returns:
        Variant score.
    """
    values = [variant.weights[k] for k in weights] if weights else variant.weights.values()
    if aggregation == "sum":
        return sum(values)
    return prod(values)


def get_configuration_score(variant_scores: Iterable[float], aggregation: str = "sum") -> float:
    """Score a configuration by aggregating variant scores by either taking the
    sum or product.

    Arguments:
        variant_scores: List of scores for all selected variants.

    Returns:
        Config score.
    """
    if aggregation == "sum":
        return sum(variant_scores)
    return prod(variant_scores)


def get_interface_method(
    interface_kind: Optional[str] = None,
) -> Callable[[Graph, Node, Node], bool]:
    """Get a basic interface checking method. Will check for the existence of edges
    between the ascendants of the variants (optionally filtered with an edge kind).
    """

    def has_interface(graph: Graph, var1: Node, var2: Node) -> bool:
        return any(
            e
            for e in graph.edges_between_all(var1.ancestor_gen, var2.ancestor_gen)
            if interface_kind is None or e.kind == interface_kind
        )

    return has_interface


def get_compatibility_method(
    compatibility_kind: Optional[str] = "compatibility",
    incompatibility_kind: Optional[str] = None,
) -> Callable[[Graph, Node, Node], bool]:
    """Get a method dat signals whether two variants are compatible.

    Arguments:
        compatibility_kind: Optional Edge kind that signals variant compatibility.
        incompatibility_kind: Optional Edge kind that signals variant incompatibility.

    Returns:
        Method of checking compatibility of two variants as nodes. Takes a Graph
        containing Edge data and an A and a B node to check.
    """
    if compatibility_kind is None and incompatibility_kind is None:
        raise ValueError("Compatibility and incompatibility kind can't both be None.")
    if compatibility_kind and incompatibility_kind:
        raise ValueError("Compatibility and incompatibility kind can't both be set.")

    def is_compatible(graph: Graph, var1: Node, var2: Node) -> bool:
        """Check whether these two nodes are compatible."""
        compatible = (
            True
            if compatibility_kind is None
            else any(e.kind == compatibility_kind for e in graph[var1.name, var2.name])
            or any(e.kind == compatibility_kind for e in graph[var2.name, var1.name])
        )
        if not compatible:
            return False
        incompatible = (
            False
            if incompatibility_kind is None
            else any(e.kind == incompatibility_kind for e in graph[var1.name, var2.name])
            or any(e.kind == incompatibility_kind for e in graph[var2.name, var1.name])
        )
        return not incompatible

    return is_compatible


def get_applicability_method(
    applicability_kind: Optional[str] = "applicability",
    inapplicability_kind: Optional[str] = None,
) -> Callable[[Graph, Node, Node], bool]:
    """Get a method dat signals whether an element is applicable when a certain
    constraint is active.

    Arguments:
        applicability_kind: Optional Edge kind that signals variant applicability.
        inapplicability_kind: Optional Edge kind that signals variant inapplicability.

    Returns:
        Method of checking applicability of an element for a constraint. Takes a Graph
        containing Edge data and an element and a constraint node to check.
    """
    if applicability_kind is None and inapplicability_kind is None:
        raise ValueError("Applicability and inapplicability kind can't both be None.")
    if applicability_kind and inapplicability_kind:
        raise ValueError("Applicability and inapplicability kind can't both be set.")

    def is_applicable(graph: Graph, element: Node, constraint: Node) -> bool:
        """Check whether these two nodes are compatible."""
        applicable = (
            True
            if applicability_kind is None
            else any(e.kind == applicability_kind for e in graph[element.name, constraint.name])
            or any(e.kind == applicability_kind for e in graph[constraint.name, element.name])
        )
        if not applicable:
            return False
        inapplicable = (
            False
            if inapplicability_kind is None
            else any(e.kind == inapplicability_kind for e in graph[element.name, constraint.name])
            or any(e.kind == inapplicability_kind for e in graph[constraint.name, element.name])
        )
        return not inapplicable

    return is_applicable


def get_score_method(
    variant_agg: str = "sum",
    config_agg: str = "sum",
    weights: Optional[List[str]] = None,
) -> Callable[[Tuple[Node, ...]], float]:
    """Get a configuration scoring method.

    Arguments:
        variant_agg: Variant node weights aggregation method. Either "sum" or "product".
        config_agg: Variant nodes' score aggregation method. Either "sum" or "product".
        weights: Optional selection of node weights to take into account.

    Returns:
        A method accepting a tuple of variant nodes and returning a single
        performance score.
    """

    def get_score(config: Tuple[Node, ...]) -> float:
        """Get the performance score of a configuration of element variants."""
        variant_scores = [get_variant_score(n, weights, variant_agg) for n in config]
        config_score = get_configuration_score(variant_scores, config_agg)
        return config_score

    return get_score


class CompatibilityAnalysis:
    """Compatibility analysis class.

    The input graph is expected to contain nodes that represent *variants* of certain
    (functional) elements. A variant is a variation of an element that fulfills the same
    functionality as other variants of that elements.

    Arguments:
        graph: Graph containing compatibility data between different variants.
        variants: Dictionary of element names to lists of variant nodes.
        interface_method: An optional method accepting a Graph and two variant nodes
            that returns whether the two given variants have an interface. Acts as a
            guard for whether compatibility checking is necessary when
            `interface_compatibility` is set.
        compatibility_method: A method accepting a Graph and two variant nodes to check
            whether the two given variants are compatible (by returning `True`).
        interface_compatibility: When set, the compatibility of two variants is only
            checked when they share an interface.
        score_method: A method accepting a tuple of variant nodes and
            returning a single performance score. See
            [`get_score_method`][ragraph.analysis.compatibility.get_score_method].
        constraints: Optional list of constraint nodes ("project scope") for which
            variants must be applicable in order to be taken into account.
        applicability_method: A method accepting a graph, a variant node and a
            constraint node that returns whether a variant is applicable when that
            constraint is set.
    """

    style = generic.Style(
        palettes=generic.Palettes(
            fields=dict(
                compatible=generic.FieldPalette(categorical="green"),
                incompatible=generic.FieldPalette(categorical="red"),
            )
        ),
        piemap=generic.PieMapStyle(
            display="labels",
            fields=["compatible", "incompatible"],
            scale_weight="scale",
            mode="relative",
        ),
        labels=generic.LabelsStyle(shorten=False),
    )

    def __init__(
        self,
        graph: Graph,
        variants: Dict[str, List[Node]],
        interface_method: Optional[Callable[[Graph, Node, Node], bool]] = None,
        compatibility_method: Callable[[Graph, Node, Node], bool] = get_compatibility_method(
            compatibility_kind="compatibility", incompatibility_kind=None
        ),
        interface_compatibility: bool = True,
        score_method: Callable[[Tuple[Node, ...]], float] = get_score_method(
            variant_agg="sum", config_agg="sum", weights=None
        ),
        constraints: Optional[List[Node]] = None,
        applicability_method: Callable[[Graph, Node, Node], bool] = get_applicability_method(
            applicability_kind="applicability", inapplicability_kind=None
        ),
    ):
        self.graph = graph
        """Graph containing compatibility data between different variants."""

        self.interface_method = interface_method
        """An optional method accepting a Graph and two variant nodes that returns whether the two
        given variants have an interface. Acts as a guard for whether compatibility checking is
        necessary when `interface_compatibility` is set."""

        self.compatibility_method = compatibility_method
        """A method accepting a Graph and two variant nodes to check whether the two given variants
        are compatible (by returning `True`)."""

        self.interface_compatibility = interface_compatibility
        """When set, the compatibility of two variants is only checked when they share an interface.
        """

        self.applicability_method = applicability_method
        """A method accepting a graph, a variant node and a constraint node that returns whether a
        variant is applicable when that constraint is set."""

        self.score_method = score_method
        """A method accepting a tuple of variant nodes and returning a single performance score.
        See [`get_score_method`][ragraph.analysis.compatibility.get_score_method]."""

        self._elements: List[str] = []
        self._element_nums: List[int] = []
        self._disabled_elements: List[str] = []

        self._constraints: List[Node] = [] if constraints is None else constraints

        self._variants: Dict[str, List[Node]] = dict()
        self._variants_list: List[Node] = []
        self.variants = variants

    @property
    def variants(self) -> Dict[str, List[Node]]:
        """Variants as lists by element name."""
        return self._variants

    @variants.setter
    def variants(self, value: Dict[str, List[Node]]):
        self._variants = value
        self._elements = []
        self._element_nums = []
        self._variants_list = []
        for el, variants in value.items():
            variants = [v for v in value[el] if self.is_applicable(v)]
            if variants:
                self._elements.append(el)
            else:
                self._disabled_elements.append(el)
                continue
            self._variants_list.extend(sorted(variants, key=lambda x: x.name))
            self._element_nums.append(len(variants))

    @property
    def constraints(self) -> List[Node]:
        """List of constraint nodes."""
        return self._constraints

    @constraints.setter
    def constraints(self, value: List[Node]):
        self._constraints = value
        self.variants = self._variants  # Re-trigger variants setter.

    @property
    def elements(self) -> List[str]:
        """Enabled elements with at least one applicable variant.
        See `self.constraints` and `self.applicability_method`.
        """
        return self._elements

    @property
    def disabled_elements(self) -> List[str]:
        """Disabled elements with no applicable variant.
        See `self.constraints` and `self.applicability_method`.
        """
        return self._disabled_elements

    @property
    def element_nums(self) -> List[int]:
        """Number of applicable variants per element."""
        return self._element_nums

    @property
    def variants_list(self) -> List[Node]:
        """Flat list of applicable variants sorted by (enabled) element."""
        return self._variants_list

    def is_applicable(self, variant: Node) -> bool:
        """Whether a variant is applicable to the currently set of constraints."""
        if self.constraints:
            return all(
                self.applicability_method(self.graph, variant, constraint)
                for constraint in self.constraints
            )
        return True

    def has_interface(self, var1: Node, var2: Node) -> bool:
        """Whether two variants have an interface that needs a compatibility check."""
        return (self.interface_method is None) or self.interface_method(self.graph, var1, var2)

    def is_compatible(self, var1: Node, var2: Node) -> bool:
        """Whether the two given variants are compatible according to
        [`self.applicability_method`][ragraph.analysis.compatibility.CompatibilityAnalysis.applicability_method]
        """

        if self.interface_compatibility:
            return (
                self.compatibility_method(self.graph, var1, var2)
                if self.has_interface(var1, var2)
                else True
            )

        return self.compatibility_method(self.graph, var1, var2)

    def get_compatibility_matrix(
        self, variants: Optional[List[Node]] = None
    ) -> Union["np.ndarray", List[List[float]]]:
        """Compatibility matrix between variants.

        Arguments:
            variants: Optional list of variants to return the compatibility matrix for.
                Also see `compatibility_method`.

        Returns:
            Compatibility matrix as a list of lists or numpy array (if numpy is
            available).
        """
        variants = self._variants_list if variants is None else variants
        dim = len(variants)
        mat = (
            np.zeros((dim, dim)) if HAVE_NUMPY else [[0.0 for j in range(dim)] for i in range(dim)]
        )
        for i in range(dim):
            var1 = variants[i]
            for j in range(i + 1, dim):
                if self.is_compatible(var1, variants[j]):
                    mat[i][j] = 1.0
                    mat[j][i] = 1.0
        return mat

    def yield_feasible_configurations(self) -> Generator[Tuple[Node, ...], None, None]:
        """Yield the feasible configurations for this problem."""
        variants = self._variants_list
        compat = self.get_compatibility_matrix(variants)
        configs = yield_feasible_configurations(compat, self._element_nums)
        for config in configs:
            yield tuple(variants[idx] for idx in config)

    def get_config_score(self, config: Tuple[Node, ...]) -> float:
        """Score a configuration. Does NOT check if the supplied config is valid!

        Arguments:
            config: Configuration as a tuple of variant nodes.

        Returns:
            Configuration score.
        """
        return self.score_method(config)

    def yield_scored_configurations(
        self,
    ) -> Generator[Tuple[Tuple[Node, ...], float], None, None]:
        """Yield the feasible configurations and their scores."""
        for config in self.yield_feasible_configurations():
            yield config, self.get_config_score(config)

    def get_ranked_configurations(
        self, descending: bool = True
    ) -> List[Tuple[Tuple[Node, ...], float]]:
        """Get the feasible configurations, sorted by score.

        Arguments:
            descending: Whether highest scores should go first.

        Returns:
            Sorted tuples of configurations and scores.
        """
        return sorted(self.yield_scored_configurations(), key=lambda x: x[-1], reverse=descending)

    def write_csv(self, path: Union[str, Path], scored: bool = True, limit: int = -1) -> int:
        """Write feasible configurations and optional scores to a CSV file."""
        path = Path(path)
        num = 0
        with open(path, mode="w+", encoding="utf-8") as f:
            f.write(";".join(self._elements))

        def append(content: str):
            with open(path, mode="a", encoding="utf-8") as f:
                f.write(content)

        if scored:
            gen = self.yield_scored_configurations()
            append(";score\n")
            if limit > 0:
                while num < limit:
                    cfg, score = next(gen)
                    append(";".join(n.name for n in cfg))
                    append(f";{score}\n")
                    num += 1
            else:
                for cfg, score in gen:
                    append(";".join(n.name for n in cfg))
                    append(f";{score}\n")
                    num += 1
        else:
            cfgs = self.yield_feasible_configurations()
            append("\n")
            if limit > 0:
                while num < limit:
                    cfg = next(cfgs)
                    append(";".join(n.name for n in cfg))
                    append("\n")
                    num += 1
            else:
                for cfg in cfgs:
                    append(";".join(n.name for n in cfg))
                    append("\n")
                    num += 1
        return num

    def get_plot_graph(self) -> Graph:
        """Get a plot ready graph for the current compatibility analysis problem."""
        g = Graph(add_parents=True, add_children=True)
        variants = deepcopy(self.variants_list)
        for variant in variants:
            g.add_node(variant)

        for i, el1 in enumerate(self.elements[:-1]):
            variants1 = self.variants[el1]
            for el2 in self.elements[i + 1 :]:
                variants2 = self.variants[el2]
                for var1 in variants1:
                    for var2 in variants2:
                        e1 = Edge(
                            g[var1.name],
                            g[var2.name],
                            kind="compatibility",
                            labels=[],
                        )
                        if self.has_interface(var1, var2):
                            e1.labels.append("interface")
                            e1.labels.append(
                                "compatible" if self.is_compatible(var1, var2) else "incompatible"
                            )
                        else:
                            e1.labels.append("no interface")
                            e1.labels.append("compatible")
                            e1.weights["scale"] = 0.25
                        e2 = Edge(
                            g[var2.name],
                            g[var1.name],
                            kind="compatibility",
                            labels=e1.labels.copy(),
                            weights=e1.weights.copy(),
                        )
                        g.add_edge(e1)
                        g.add_edge(e2)
        return g

    def plot(self, **mdm_args) -> "go.Figure":
        """Visualize the compatibility analysis problem."""
        g = self.get_plot_graph()
        variants = [g[n.name] for n in self.variants_list]

        # Merge styles if provided.
        if "style" in mdm_args:
            style = deepcopy(self.style)
            style.update(mdm_args["style"])
            mdm_args["style"] = style
        else:
            mdm_args["style"] = self.style

        return mdm(leafs=variants, edges=g.edges, **mdm_args)
