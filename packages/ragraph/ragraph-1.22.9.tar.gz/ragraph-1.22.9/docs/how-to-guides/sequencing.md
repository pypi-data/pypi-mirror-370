# Sequencing analysis

This page describes what a sequencing analysis is and how to perform one using RaGraph. Sequencing
is an analysis form where one usually attempts to find an optimal ordering of nodes according to
some objective (function). If nodes represent dependent tasks with deliverables, you can imagine
that you would want to start a task only when (most) of the deliverables it depends on are done
first. Or, if you are modeling a system of components by their input and output dependencies, you
might want to view them more or less chronologically, too.

The sequencing algorithms are included in [the `ragraph.analysis.sequence`
module][ragraph.analysis.sequence]. Let's import the
[`ragraph.datasets.shaja8`][ragraph.datasets.shaja8] dataset that is an example from
literature.

```python
from ragraph import datasets

g = datasets.get("shaja8")
print(g.get_ascii_art())
"""
 ┌───┬───┬───┬───┬───┬───┬───┬───┐
1┥ ■ │   │   │   │   │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
2┥ X │ ■ │   │   │ X │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
3┥ X │ X │ ■ │   │ X │   │   │ X │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
4┥ X │   │ X │ ■ │ X │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
5┥ X │   │   │ X │ ■ │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
6┥   │   │   │ X │ X │ ■ │ X │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
7┥   │   │   │   │   │ X │ ■ │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
8┥   │ X │   │   │   │   │   │ ■ │
 └───┴───┴───┴───┴───┴───┴───┴───┘
"""
```

Here, the marks above the diagonal represent **feedback marks**, meaning that you are missing a
deliverable if you would do the activities in the order given on the left hand side (the same labels
are always assumed to be in identical order on the X-axis). If you were to make an assumption
regarding these deliverables, you could still start your tasks in this order, but might find that
this assumption is wrong in the end. The later you find this mistake, the higher the probability
that it cascades through your design process. Or in other words, the further the feedback mark is
from the diagonal (e.g. the top right), the higher the risk.

Plenty of metrics have been introduced to quantify the **badness** or **penalty** of a given
sequence of nodes. Some of these have been included in
[`ragraph.analysis.sequence.metrics`][ragraph.analysis.sequence.metrics]. Let's quantify the
baseline of the graph we just imported. An often used metric is the **feedback distance with respect
to the diagonal**. E.g. the sum of distances to the diagonal of each feedback mark that is present:

```python
from ragraph import datasets
from ragraph.analysis import sequence

g = datasets.get("shaja8")

score, contrib = sequence.metrics.feedback_distance(g.get_adjacency_matrix())

assert score == 12, "Score at import is 12 (=3 + 2 + 5 + 1 + 1)"
assert contrib.tolist() == [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [-0, 0, 0, 0, 3, 0, 0, 0],
    [-0, -0, 0, 0, 2, 0, 0, 5],
    [-0, -0, -0, 0, 1, 0, 0, 0],
    [-0, -0, -0, -0, 0, 0, 0, 0],
    [-0, -0, -0, -0, -0, 0, 1, 0],
    [-0, -0, -0, -0, -0, -0, 0, 0],
    [-0, -0, -0, -0, -0, -0, -0, 0],
], "The minuses are artifacts from the calculation method."
```

Here you can see both the penalty score (12.0) and the contribution of each cell in the matrix.
Let's see if we can improve things with an algorithm!

```python
from ragraph import datasets
from ragraph.analysis import sequence

g = datasets.get("shaja8")

g, seq = sequence.markov(g, inf=1.0, dep=1.0, mu=2.0, scale=False, names=False)

score, contrib = sequence.metrics.feedback_distance(g.get_adjacency_matrix(nodes=seq))

assert score == 5.0, "Significant improvement!"
assert contrib.tolist() == [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [-0, 0, 1, 0, 0, 0, 0, 0],
    [-0, -0, 0, 1, 0, 0, 0, 0],
    [-0, -0, -0, 0, 0, 2, 0, 0],
    [-0, -0, -0, -0, 0, 0, 0, 0],
    [-0, -0, -0, -0, -0, 0, 0, 0],
    [-0, -0, -0, -0, -0, -0, 0, 1],
    [-0, -0, -0, -0, -0, -0, -0, 0],
]

print(g.get_ascii_art(nodes=seq))
"""
 ┌───┬───┬───┬───┬───┬───┬───┬───┐
1┥ ■ │   │   │   │   │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
8┥   │ ■ │ X │   │   │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
2┥ X │   │ ■ │ X │   │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
5┥ X │   │   │ ■ │   │ X │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
3┥ X │ X │ X │ X │ ■ │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
4┥ X │   │   │ X │ X │ ■ │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
7┥   │   │   │   │   │   │ ■ │ X │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
6┥   │   │   │ X │   │ X │ X │ ■ │
 └───┴───┴───┴───┴───┴───┴───┴───┘
"""
```

Much better! There are now less feedback marks and the distance of the remaining ones is quite close
to the diagonal. This also shows from the overall penalty score that now sits at 5.0 and the
contribution matrix.

By the way, it's impossible to sequence this [`Graph`][ragraph.graph.Graph] without any feedback
marks, as there are cycles present! It's not a Directed Acyclic Graph (DAG) so there is no trivial
solution.

If you would like to check whether your graph has any cycles at all, you can utilize [Johnson's
heuristic `ragraph.analysis.heuristics.johnson][ragraph.analysis.heuristics.johnson].

```python
from ragraph import datasets
from ragraph.analysis import heuristics

g = datasets.get("shaja8")

cycles = heuristics.johnson(g, names=True)  # Returns a generator.
first = next(cycles)
assert first is not None, "We should have a cycle here!"
assert first == [
    "2",
    "8",
    "3",
    "4",
    "5",
], "The node names, in case you were wondering."
```

Yup, we found our first cycle!

To list all cycles at once, you can use the following snippet. Be careful however, for large graphs
the amount of cycles can be **very long** and keep your CPU occupied for a while.

```python
from ragraph import datasets
from ragraph.analysis import heuristics

g = datasets.get("shaja8")

assert list(heuristics.johnson(g, names=True)) == [
    ["2", "8", "3", "4", "5"],
    ["2", "3", "4", "5"],
    ["3", "4", "5"],
    ["5", "4"],
    ["6", "7"],
]
```

Can you spot the cycles in the graph now, too? This heuristics provides a nice insight. If, and only
if, there are **no cycles present**, you can use the
[`ragraph.analysis.sequence.tarjans_dfs`][ragraph.analysis.sequence.tarjans_dfs] method to quickly
find a sequence **without any feedback marks** at all. Other algorithms might find this, too, but
this one in particular is one of the more efficient algorithms for this use case.

## Breaking cycles with tearing

The computational advantage of not having cycles is huge, especially for large datasets. This has
led to sequencing strategies that incorporate **tearing**. Tearing is a two-fold procedure. You pick
a node from the first cycle and fix its position as the next in the sequence. You then try to see if
the remainder of the problem is (partially) free of cycles and continue to tear any subsequent cycle
by fixing a node there, too.

If you tear often enough, you can eventually sequence the remainder of the graph as a directed
acyclic graph. This leaves one problem:

> How to decide which node to tear?

### SCC tearing

This is where [`ragraph.analysis.sequence.scc_tearing`][ragraph.analysis.sequence.scc_tearing] comes
into play. It's a sequencing algorithm (or heuristic, really) that uses Tarjans Strongly Connected
Components (SCC) to identify the largest possible cycles. These cycles themselves form a directed
acyclic graph by definition. A nice byproduct of the SCC algorithm is that it outputs the cycles in
the (reversed) ideal ordering to put them in for a topological sort (ideal sequence so to speak).

These SCCs are then torn using a decision function. By default it utilizes the same calculations as
the Markov sequencing algorithm to pick the node with the lowest penalty score
([`ragraph.analysis.sequence.utils.markov_decision`][ragraph.analysis.sequence.utils.markov_decision]).
An example:

```python
from ragraph import datasets
from ragraph.analysis import sequence

g = datasets.get("shaja8")

g, seq = sequence.scc_tearing(g, names=False)

score, contrib = sequence.metrics.feedback_distance(g.get_adjacency_matrix(nodes=seq))
assert score == 5.0, "Still 5 here!"
assert contrib.tolist() == [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [-0, 0, 0, 2, 0, 0, 0, 0],
    [-0, -0, 0, 0, 0, 0, 0, 0],
    [-0, -0, -0, 0, 0, 2, 0, 0],
    [-0, -0, -0, -0, 0, 0, 0, 0],
    [-0, -0, -0, -0, -0, 0, 0, 0],
    [-0, -0, -0, -0, -0, -0, 0, 1],
    [-0, -0, -0, -0, -0, -0, -0, 0],
], "But with a different contribution distribution."

print(g.get_ascii_art(nodes=seq))
"""
 ┌───┬───┬───┬───┬───┬───┬───┬───┐
1┥ ■ │   │   │   │   │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
2┥ X │ ■ │   │ X │   │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
8┥   │ X │ ■ │   │   │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
5┥ X │   │   │ ■ │   │ X │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
3┥ X │ X │ X │ X │ ■ │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
4┥ X │   │   │ X │ X │ ■ │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
7┥   │   │   │   │   │   │ ■ │ X │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
6┥   │   │   │ X │   │ X │ X │ ■ │
 └───┴───┴───┴───┴───┴───┴───┴───┘
"""
```

### SCC tearing with options

The last result wasn't bad, although it features one slightly larger feedback loop than the regular
Markov sequencing example. However, we can tweak the Markov decision function to always take into
account the complete context of nodes when calculating the "flow matrices" behind the scenes. To do
this, we can explicitly provide arguments that should be passed to the (this time explicitly set)
decision function:

```python
from ragraph import datasets
from ragraph.analysis import sequence

g = datasets.get("shaja8")

g, seq = sequence.scc_tearing(
    g,
    names=False,
    decision=sequence.utils.markov_decision,
    decision_args=dict(context=g.nodes),
)
score, contrib = sequence.metrics.feedback_distance(g.get_adjacency_matrix(nodes=seq))

assert score == 5.0, "Yup, still 5."
assert contrib.tolist() == [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [-0, 0, 0, 0, 0, 4, 0, 0],
    [-0, -0, 0, 0, 0, 0, 0, 0],
    [-0, -0, -0, 0, 0, 0, 0, 0],
    [-0, -0, -0, -0, 0, 0, 0, 0],
    [-0, -0, -0, -0, -0, 0, 0, 0],
    [-0, -0, -0, -0, -0, -0, 0, 1],
    [-0, -0, -0, -0, -0, -0, -0, 0],
], "And there's the new distribution!"

print(g.get_ascii_art(nodes=seq))
"""
 ┌───┬───┬───┬───┬───┬───┬───┬───┐
1┥ ■ │   │   │   │   │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
5┥ X │ ■ │   │   │   │ X │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
2┥ X │ X │ ■ │   │   │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
8┥   │   │ X │ ■ │   │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
3┥ X │ X │ X │ X │ ■ │   │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
4┥ X │ X │   │   │ X │ ■ │   │   │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
7┥   │   │   │   │   │   │ ■ │ X │
 ├───┼───┼───┼───┼───┼───┼───┼───┤
6┥   │ X │   │   │   │ X │ X │ ■ │
 └───┴───┴───┴───┴───┴───┴───┴───┘
"""
```

Et voilà! Still on a score of 5. Calculating the complete context over and over comes at a slight
computational cost, though.
