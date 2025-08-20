import difflib
import shutil
import uuid
from pathlib import Path

import pytest

from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node

HERE = Path(__file__).parent
UPDATE_PATH = HERE / ".update"
UPDATE = UPDATE_PATH.exists()
INSPECT_PATH = HERE / ".inspect"
INSPECT = INSPECT_PATH.exists()
SPECS_PATH = HERE / "data" / "specs"
DOCS_DIR = HERE.parent / "docs"


@pytest.fixture(autouse=True, scope="session")
def generated_docs():
    path = DOCS_DIR / "generated"
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(exist_ok=True)


# Fix UUID generation during tests:
def generate_int_uuids():
    index = 0
    while True:
        yield uuid.UUID(int=index)
        index += 1


@pytest.fixture
def inspect():
    return INSPECT


@pytest.fixture(autouse=True, scope="function")
def reset_uuids():
    int_uuid = generate_int_uuids()
    uuid.uuid4 = lambda: next(int_uuid)


@pytest.fixture
def update():
    return UPDATE


@pytest.fixture
def datadir():
    return Path(__file__).parent / "data"


@pytest.fixture
def a():
    return Node("a")


@pytest.fixture
def b():
    return Node("b")


@pytest.fixture
def c():
    return Node("c")


@pytest.fixture
def d():
    return Node("d")


@pytest.fixture
def e():
    return Node("e")


@pytest.fixture
def f():
    return Node("f")


@pytest.fixture
def empty_graph():
    return Graph()


@pytest.fixture
def edge_ab(a, b):
    return Edge(a, b, name="a->b")


@pytest.fixture
def graph_ab(a, b, edge_ab):
    return Graph(nodes=[a, b], edges=[edge_ab], name="graph_ab")


@pytest.fixture
def rich_graph(graph_ab):
    graph = graph_ab
    graph.name = "rich"
    c = Node("c", parent=graph.node_dict["a"], kind="rich", weights=dict(dollars=1))
    d = Node("d", parent=graph.node_dict["a"], kind="wealthy", weights=dict(euros=0.5))
    graph.add_node(c)
    graph.add_node(d)
    graph.add_edge(Edge(c, d, name="c->d", kind="money", labels=["euros"], weights=dict(dollars=1)))
    return graph


@pytest.fixture
def esl_file(datadir):
    return datadir / "esl/test.esl"


@pytest.fixture
def esl_graph(esl_file):
    from ragraph.io.esl import from_esl

    return from_esl(esl_file)


@pytest.fixture
def check_diff():
    """Check whether there is a diff w.r.t. to the reference path."""

    def _check_diff(path: Path, ref_path: Path, sort: bool = False):
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        ref_text = ref_path.read_text(encoding="utf-8") if path.exists() else ""

        lines = text.splitlines(False)
        ref_lines = ref_text.splitlines(False)
        if sort:
            lines, ref_lines = sorted(lines), sorted(ref_lines)

        diff = difflib.unified_diff(
            ref_lines,
            lines,
            fromfile=str(ref_path),
            tofile=str(path),
            lineterm="",
        )
        diffstr = "\n".join(diff)

        if diffstr and UPDATE:
            if not ref_path.parent.exists():
                ref_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, ref_path)
        else:
            assert not diffstr, diffstr

    return _check_diff


@pytest.fixture
def check_plotly(datadir: Path, inspect: bool):
    """Plotly output check function."""
    from plotly import io as pio
    from plotly.graph_objs import Figure

    def _check_plotly(fig: Figure, fname: str):
        """Checking if the figure data and shapes are equal to the data and shapes
        stored in the reference file.

        Arguments:
            fig: The figure to be tested.
            fname: The relative path to the reference file.
        """
        if inspect:
            fig.show()

        fpath = datadir / "plotly" / fname
        if UPDATE:
            pio.write_json(fig, fpath)
        reference = pio.read_json(fpath)

        assert fig == reference, "Figures should match."

    return _check_plotly
