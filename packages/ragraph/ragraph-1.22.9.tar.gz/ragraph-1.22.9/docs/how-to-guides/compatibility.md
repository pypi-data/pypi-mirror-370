# Compatibility analysis

The compatibility analysis considers an exploration and optimization problem, most often encountered
when developing product families. It assumes a product or system consists of various functional
modules or components for which multiple variants exist. The goal is to find an optimal
configuration, or variant selection for each component, given a set of performance criteria and
performance ratings for each variant.

Some variants might be incompatible with each other, which is where the computation of feasible
configurations comes into play. Finding a solution therefore becomes a two-step process:

1.  What are the feasible configurations of variants given their compatibility?
2.  What is the performance of each configuration, if there are any?

## Modeling the problem

The problem can be visualized using a Compatibility Matrix. To this end, we model a
[`Graph`][ragraph.graph.Graph] equivalent with the following contents:

- A node for each component variant.
  - A variant node may include any number of performance weights, which can later be combined into a
    performance score per node.
- An edge between variants that are compatible, with a predefined weight to signal this. Here, we'll
  use `"compatibility"`.

For an absolute minimal example, see the [compatibility dataset][ragraph.datasets.compatibility].
In this dataset's info, we find:

> Minimal example to illustrate the compatibility analysis.
>
> Contains 6 component variant nodes. They are divided in three node kinds (e.g. components), which
> correspond to the first character in their node names: A1, B1, B2, C1, C2, C3. For ease of use the
> "performance" weight of each node is set to it's node name's second character.
>
> Compatibility between nodes is signalled using edges with a "compatibility" kind.

```python
from ragraph import datasets

g = datasets.get("compatibility")
print(g.get_ascii_art())
"""
  ┌───┬───┬───┬───┬───┬───┐
A1┥ ■ │ X │ X │   │ X │ X │
  ├───┼───┼───┼───┼───┼───┤
B1┥ X │ ■ │   │ X │ X │ X │
  ├───┼───┼───┼───┼───┼───┤
B2┥ X │   │ ■ │ X │ X │ X │
  ├───┼───┼───┼───┼───┼───┤
C1┥   │ X │ X │ ■ │   │   │
  ├───┼───┼───┼───┼───┼───┤
C2┥ X │ X │ X │   │ ■ │   │
  ├───┼───┼───┼───┼───┼───┤
C3┥ X │ X │ X │   │   │ ■ │
  └───┴───┴───┴───┴───┴───┘
"""
```

E.g., there are three components for which variants exist. For component `"A"` we only have a single
variant, for `"B"` we have two, and for `"C"` we have three. A configuration would therefore be
represented by `[(A1, B2, C1)]`. But is that the only feasible one?

## Feasible configurations

Using the [`ragraph.analysis.compatibility` module][ragraph.analysis.compatibility], we can generate
feasible configurations for this problem. First we create a dictionary of elements (A, B, C) to
their respective variant nodes, which we can pass into a
[`CompatibilityAnalysis`][ragraph.analysis.compatibility.CompatibilityAnalysis]:

```python
from ragraph import datasets
from ragraph.analysis import compatibility as comp
from collections import defaultdict

# Load the dataset and do some pre-processing
# that utilizes the node naming scheme.
g = datasets.get("compatibility")
variants_by_element = defaultdict(list)
for n in g.nodes:
    variants_by_element[n.name[0]].append(n)
    # {"A": [Node("A1")], "B": [Node("B1"), Node("B2")], ...}

# Create CompatibilityAnalysis object
ca = comp.CompatibilityAnalysis(
    g,
    variants=variants_by_element,
    compatibility_method=comp.get_compatibility_method(
        compatibility_kind="compatibility",
        incompatibility_kind=None,
    ),
)

configs = ca.yield_feasible_configurations()
# Convert to node names.
names = [tuple(n.name for n in config) for config in configs]
assert names == [
    ("A1", "B2", "C3"),
    ("A1", "B2", "C2"),
    ("A1", "B1", "C3"),
    ("A1", "B1", "C2"),
], "Voilá! Four compatible configurations."
```

So currently, there's four feasible configurations. These are feasible since the
`compatibility_method` with the given arguments checks for edges with an edge kind of
`"compatibility"` between the given variant nodes. The variants of all elements have to be
compatible with each other element's variant in order to achieve a feasible configuration.

Note that the `configs` variable has been set with a generator rather than a direct list (note the
`yield` instead of `get` in the method's name). Using a generator you could find and parse one
configuration at a time, which is helpful as these problems tend to get computationally expensive to
calculate all at once.

## Configuration performance

Generating feasible configurations is one thing, but which configuration is the most performant one?
Let's find out! In the example's dataset the performance of each variant is equal to the digit in
its name. By default, the scoring method takes the sum of all node weights for each component
variant node to calculate a variant's performance. The score for a configuration is the aggregated
sum of all variants used.

### Generator approach

```python
from ragraph import datasets
from ragraph.analysis import compatibility as comp
from collections import defaultdict

# Load the dataset and do some pre-processing
# that utilizes the node naming scheme.
g = datasets.get("compatibility")
variants_by_element = defaultdict(list)
for n in g.nodes:
    variants_by_element[n.name[0]].append(n)
    # {"A": [Node("A1")], "B": [Node("B1"), Node("B2")], ...}

# Create CompatibilityAnalysis object
# With score method!
ca = comp.CompatibilityAnalysis(
    g,
    variants=variants_by_element,
    compatibility_method=comp.get_compatibility_method(
        compatibility_kind="compatibility",
        incompatibility_kind=None,
    ),
    score_method=comp.get_score_method(
        variant_agg="sum",
        config_agg="sum",
        weights=None,
    ),
)
# Note the "yield" here.
scored_configs = ca.yield_scored_configurations()
named = [(tuple(n.name for n in result[0]), result[1]) for result in scored_configs]
assert named == [
    (("A1", "B2", "C3"), 6.0),
    (("A1", "B2", "C2"), 5.0),
    (("A1", "B1", "C3"), 5.0),
    (("A1", "B1", "C2"), 4.0),
], "And now you know their performance!"
```

From which we can conclude that configuration `[(A1, B2, C3)]` is the most performant with a score
of 6.

!!! note

    Note the **`yield`** in `scored_configs = ca.yield_scored_configurations()`. This function
    returns a generator, as the total number of feasible configurations can rapidly explode for
    larger problems.

For large problems, you might want to store the best, or a top 5 instead of all configurations.

### List approach

If you would want to generate a complete sorted list of all feasible variants, that is possible as
well. Although this might take a while for larger problems:

```python
from ragraph import datasets
from ragraph.analysis import compatibility as comp
from collections import defaultdict

# Load the dataset and do some pre-processing
# that utilizes the node naming scheme.
g = datasets.get("compatibility")
variants_by_element = defaultdict(list)
for n in g.nodes:
    variants_by_element[n.name[0]].append(n)
    # {"A": [Node("A1")], "B": [Node("B1"), Node("B2")], ...}

# Create CompatibilityAnalysis object
ca = comp.CompatibilityAnalysis(
    g,
    variants=variants_by_element,
    compatibility_method=comp.get_compatibility_method(
        compatibility_kind="compatibility",
        incompatibility_kind=None,
    ),
    score_method=comp.get_score_method(
        variant_agg="sum",
        config_agg="sum",
        weights=None,
    ),
)
# Note the "get" in the function name below.
ranked_configs = ca.get_ranked_configurations(
    descending=True
)  # This is a sorted list, now.
named = [(tuple(n.name for n in result[0]), result[1]) for result in ranked_configs]
assert named == [
    (("A1", "B2", "C3"), 6.0),
    (("A1", "B2", "C2"), 5.0),
    (("A1", "B1", "C3"), 5.0),
    (("A1", "B1", "C2"), 4.0),
], "This list is guaranteed to be sorted in descending order."
```

So that's the same result, but pre-cast as a sorted list. If your performance metric is a penalty,
you can set `descending=False` to get your most performant results first, too.

## Adding constraints

Especially in the context of product platforms you might want to add constraints to the element
variants to accommodate for different scenario's. For instance, in case of bridges and waterway
locks the soil might be different, or the waterway that needs to be crossed exceeds a certain width,
which excludes certain variants of being applicable.

This can be modeled by adding constraint nodes, to which we could add applicability edges or
inapplicability edges, depending on what suits the modeling approach best. Let's discuss adding a
constraint in our example that disables `"C3"` when it's active.

```python
from ragraph.node import Node
from ragraph.edge import Edge
from ragraph import datasets
from ragraph.analysis import compatibility as comp
from collections import defaultdict

# Load the dataset and do some pre-processing
# that utilizes the node naming scheme.
g = datasets.get("compatibility")
variants_by_element = defaultdict(list)
for n in g.nodes:
    variants_by_element[n.name[0]].append(n)
    # {"A": [Node("A1")], "B": [Node("B1"), Node("B2")], ...}

# Add the constraint and build the CompatibilityAnalysis.
constraint = Node(name="C3-not-suitable", kind="constraint")
g.add_node(constraint)
g.add_edge(
    Edge(
        source=constraint,
        target=g["C3"],
        kind="inapplicability",
    )
)
ca = comp.CompatibilityAnalysis(
    g,
    variants=variants_by_element,
    compatibility_method=comp.get_compatibility_method(
        compatibility_kind="compatibility",
        incompatibility_kind=None,
    ),
    score_method=comp.get_score_method(
        variant_agg="sum",
        config_agg="sum",
        weights=None,
    ),
    constraints=[constraint],
    applicability_method=comp.get_applicability_method(
        applicability_kind=None,
        inapplicability_kind="inapplicability",
    ),
)

ranked_configs = ca.get_ranked_configurations(descending=True)
named = [(tuple(n.name for n in result[0]), result[1]) for result in ranked_configs]

assert named == [
    (("A1", "B2", "C2"), 5.0),
    (("A1", "B1", "C2"), 4.0),
], "C3 is a no-go, so this is what is left."

assert ca.disabled_elements == [], "Should be an empty list in this example."
```

Which shows that we have successfully disabled `"C3"` in this scenario. Note that disabling _all_
variants of an element just disables the entire element without warning. Make sure to check whether
the [`disabled_elements`
property][ragraph.analysis.compatibility.CompatibilityAnalysis.disabled_elements] does not hold any
element you would deem essential while trying to satisfy your current constraints:

## Further customization

The analysis can be tailored to work with your data model in the
following ways:

- Setting a different (in)compatibility method. Please refer to
  [`ragraph.analysis.compatibility.get_compatibility_method`][ragraph.analysis.compatibility.get_compatibility_method]
  for the built-in options. Type: `[Callable[[Graph, Node, Node], bool]]`.
- Setting a different scoring method. Please refer to
  [`ragraph.analysis.compatibility.get_score_method`][ragraph.analysis.compatibility.get_score_method]
  for the built-in options. Type: `[Callable[[Tuple[Node, ...]], float]]`.
- Setting a different applicability method to filter variants. Please refer to
  [`ragraph.analysis.compatibility.get_applicability_method`][ragraph.analysis.compatibility.get_applicability_method]
  for the built-in options. Type: `[Callable[[Graph, Node, Node], bool]]`.

All of these method getters return some preset methods that do rudimentary things. Providing your
own could be as an inline lambda function that satisfies the call signatures. For instance, some
custom methods could look like this:

```python
from ragraph.node import Node
from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph import datasets
from ragraph.analysis import compatibility as comp
from collections import defaultdict

# Load the dataset and do some pre-processing
# that utilizes the node naming scheme.
g = datasets.get("compatibility")
variants_by_element = defaultdict(list)
for n in g.nodes:
    variants_by_element[n.name[0]].append(n)
    # {"A": [Node("A1")], "B": [Node("B1"), Node("B2")], ...}

# Add the constraint!
constraint = Node(name="C3-not-suitable", kind="constraint")
g.add_node(constraint)
g.add_edge(
    Edge(
        source=constraint,
        target=g["C3"],
        kind="inapplicability",
    )
)


# At least one edge between nodes
def my_compat(graph: Graph, var1: Node, var2: Node) -> bool:
    return len(graph[var1, var2]) + len(graph[var2, var1]) > 0


# Just the sum of the penalty weight
def my_score(*config: Node) -> float:
    return sum(variant.weights['penalty'] for variant in config)


# No edges with any constraint
def my_appli(graph: Graph, var: Node, con: Node) -> bool:
    return not (len(graph[var, con]) + len(graph[con, var]))


ca = comp.CompatibilityAnalysis(
    g,
    variants=variants_by_element,
    compatibility_method=my_compat,
    score_method=my_score,
    applicability_method=my_appli,
    constraints=[constraint],
)
```

## Write to CSV

If you would like to let the calculations run for a while and generate a
CSV file with all results, please refer to the
[`ragraph.analysis.compatibility.CompatibilityAnalysis.write_csv` method
][ragraph.analysis.compatibility.CompatibilityAnalysis.write_csv].

## Design space estimate

To get an idea of the maximum number of configurations that would have
to be checked of an exhaustive search, take the product of your element
variation counts:

```python
from ragraph.node import Node
from ragraph.edge import Edge
from ragraph import datasets
from ragraph.analysis import compatibility as comp
from collections import defaultdict
from math import prod

# Load the dataset and do some pre-processing
# that utilizes the node naming scheme.
g = datasets.get("compatibility")
variants_by_element = defaultdict(list)
for n in g.nodes:
    variants_by_element[n.name[0]].append(n)
    # {"A": [Node("A1")], "B": [Node("B1"), Node("B2")], ...}

# Add the constraint and build the CompatibilityAnalysis.
constraint = Node(name="C3-not-suitable", kind="constraint")
g.add_node(constraint)
g.add_edge(
    Edge(
        source=constraint,
        target=g["C3"],
        kind="inapplicability",
    )
)
ca = comp.CompatibilityAnalysis(
    g,
    variants=variants_by_element,
    compatibility_method=comp.get_compatibility_method(
        compatibility_kind="compatibility",
        incompatibility_kind=None,
    ),
    score_method=comp.get_score_method(
        variant_agg="sum",
        config_agg="sum",
        weights=None,
    ),
    constraints=[constraint],
    applicability_method=comp.get_applicability_method(
        applicability_kind=None,
        inapplicability_kind="inapplicability",
    ),
)

assert prod(ca.element_nums) == 4, "Note, C3 is still disabled! So we expect 4, not 5."
```

Luckily, concept compatibility exploration is invalidated as soon as an
incompatible concept combination is encountered.
