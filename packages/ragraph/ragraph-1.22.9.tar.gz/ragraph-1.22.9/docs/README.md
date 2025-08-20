# Introduction

Welcome to RaGraph's documentation! RaGraph is a library to create, manipulate, and analyze graphs
consisting of nodes and edges. Nodes usually represent (hierarchies of) objects and edges the
dependencies or relationships between them.

These graphs, or networks if you will, lend themselves well to applied analyses like clustering and
sequencing, as well as analyses involving the calculation of various insightful metrics.

It's aim is to provide an easy-to-use and versatile library.

In this documentation you can find

1. [Tutorials](./tutorials/README.md) for step-by-step educational content,
1. [How-to guides](./how-to-guides/README.md) for a more use-case centric approach, the package's,
1. [Reference](./reference/README.md) including source code
1. Some [Explanation](./explanation/README.md) and rationale behind the library,
1. The [Changelog](./CHANGELOG.md) outlining all changes following the
   [https://keepachangelog.com](https://keepachangelog.com) conventions.

# Installation instructions

RaGraph is installable via pip or your favorite Python dependency manager. If you want all the
goods, get going with:

```bash
pip install ragraph[all]
```

or for instance for Poetry:

```bash
poetry add ragraph -E all
```

For a development installation, head over to [the GitLab
repository](https://gitlab.com/ratio-case-os/python/ragraph) for instructions.

# Hello world!

Perhaps the most _"Hello world!"_ thing to do with a `Graph` is to make a single source `Node`, a
target `Node` and create an `Edge` between them and put them in a `Graph`. The snippet below uses a
**very** rudimentary ASCII-art representation of a Dependency Structure Matrix (DSM) of the `Graph`
where _"the X marks the spot"_ of our `Edge`.

```python
from ragraph.graph import Graph, Node, Edge

source = Node(name="the source")
target = Node(name="the target")
edge = Edge(source, target)
g = Graph(
    nodes=[source, target],
    edges=[edge],
)
print(g.get_ascii_art())
"""
          ┌───┬───┐
the source┥ ■ │   │
          ├───┼───┤
the target┥ X │ ■ │
          └───┴───┘
"""
```

This is also your first Dependency Structure Matrix (DSM) for you! You might know it as the
_adjacency matrix_ of a graph. Each row and column in the matrix corresponds to the nodes. They are
both in identical order from the top-left to bottom-right. Imagine each node itself is one of the
`■`-squares on the diagonal. The single `Edge` is marked using an `X` here. All of the incoming
edges towards a node are in it's row and at the column corresponding to the source. All outgoing
edges of a node are therefore in it's column. This is called the _IR/FAD convention_ (Inputs in
Rows/Feedback Above Diagonal).

Congratulations! You'll see plenty more (way prettier!) DSM visualizations of graphs in our
documentation.

Where to next? You might want a [step-by-step start using the tutorials](./tutorials/README.md) or a
[use case approach using the how-to guides](./how-to-guides/README.md).

# License and contributions

For contribution instructions, head over to the [open-source GitLab
repository](https://gitlab.com/ratio-case-os/python/ragraph)!

All code snippets in the tutorial and how-to guide sections of this documentation are free to use.

If you find any documentation worthwhile citing, please do so with a proper reference to our
documentation!

RaGraph is licensed following a dual licensing model. In short, we want to provide anyone that
wishes to use our published software under the GNU GPLv3 to do so freely and without any further
limitation. The GNU GPLv3 is a strong copyleft license that promotes the distribution of free,
open-source software. In that spirit, it requires dependent pieces of software to follow the same
route. This might be too restrictive for some. To accommodate users with specific requirements
regarding licenses, we offer a proprietary license. The terms can be discussed by reaching out to
Ratio.
