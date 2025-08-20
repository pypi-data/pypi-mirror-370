# RaGraph

RaGraph is a package to create, manipulate, and analyze graphs consisting of nodes and edges. Nodes
usually represent (hierarchies of) objects and edges the dependencies or relationships between them.

These graphs, or networks if you will, lend themselves well to applied analyses like clustering and
sequencing, as well as analyses involving the calculation of various insightful metrics.

## User documentation

For all user-facing documentation, please head over to our beautiful documentation over at
[https://ragraph.ratio-case.nl](https://ragraph.ratio-case.nl)!

## Development installation

This project is packaged using [uv](https://docs.astral.sh/uv/) as the environment manager and build
frontend. Packaging information as well as dependencies are stored in
[pyproject.toml](./pyproject.toml).

For ease of use, this project uses the [just](https://github.com/casey/just) command runner to
simplify common tasks. Installing the project and its development dependencies can be done by
running `just install` in the cloned repository directory or manually by running `uv sync`.

Please consult the [justfile](./justfile) for the underlying commands or run `just` to display a
list of all available commands.

### Tests

Tests can be run using `just test` and subsequent arguments will be passed to pytest.

### Linting

Linting the project can be done using `just lint`, automatic fixes can be applied using `just fix`.
Linting config is included in [pyproject.toml](./pyproject.toml) for both Black and Ruff.

## Contributions and license

To get contributing, feel free to fork, pick up an issue or file your own and get going for your
first merge! We'll be more than happy to help.

For contribution instructions, head over to the [open-source GitLab
repository](https://gitlab.com/ratio-case-os/python/ragraph)!

All code snippets in the tutorial and how-to guide sections of the package documentation are free to
use.

If you find any documentation worthwhile citing, please do so with a proper reference to our
documentation!

RaGraph is licensed following a dual licensing model. In short, we want to provide anyone that
wishes to use our published software under the GNU GPLv3 to do so freely and without any further
limitation. The GNU GPLv3 is a strong copyleft license that promotes the distribution of free,
open-source software. In that spirit, it requires dependent pieces of software to follow the same
route. This might be too restrictive for some. To accommodate users with specific requirements
regarding licenses, we offer a proprietary license. The terms can be discussed by reaching out to
Ratio.
