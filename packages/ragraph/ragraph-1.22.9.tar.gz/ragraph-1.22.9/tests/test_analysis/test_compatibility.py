"""Tests for compatibility analysis module."""

from collections import defaultdict
from pathlib import Path

import numpy as np
import pytest
from ragraph import datasets
from ragraph.analysis import compatibility
from ragraph.graph import Graph


@pytest.fixture
def compat():
    return datasets.get("compatibility").get_adjacency_matrix()


@pytest.fixture
def compat_graph():
    return datasets.get("compatibility")


def test_feasible_configs(compat):
    assert compatibility.is_feasible(compat, (1, 4)), "Should be feasible."
    # [1,2,2] means: always pick 0, pick 1 or 2, pick 3 or 4
    # in this example, we skip 5.
    assert list(compatibility.yield_feasible_configurations(compat, [1, 2, 2])) == [
        (0, 2, 4),
        (0, 1, 4),
    ]


def test_compatibility_analysis(compat_graph: Graph, compat: np.ndarray, datadir: Path, tmpdir):
    variants = defaultdict(list)
    for n in compat_graph.nodes:
        variants[n.kind].append(n)
    ca = compatibility.CompatibilityAnalysis(
        compat_graph,
        variants=variants,
    )
    comps = ca._variants_list
    assert [n.name for n in comps] == ["A1", "B1", "B2", "C1", "C2", "C3"]

    assert np.all(np.array(ca.get_compatibility_matrix()) == np.array(compat))

    assert list(ca.yield_feasible_configurations()) == [
        tuple(comps[i] for i in (0, 2, 5)),
        tuple(comps[i] for i in (0, 2, 4)),
        tuple(comps[i] for i in (0, 1, 5)),
        tuple(comps[i] for i in (0, 1, 4)),
    ], "Feasible configs in terms of nodes."

    assert ca.get_ranked_configurations() == [
        (tuple(comps[i] for i in (0, 2, 5)), 6.0),
        (tuple(comps[i] for i in (0, 2, 4)), 5.0),
        (tuple(comps[i] for i in (0, 1, 5)), 5.0),
        (tuple(comps[i] for i in (0, 1, 4)), 4.0),
    ], "Ranked configs."

    ca.score_method = compatibility.get_score_method(variant_agg="product", config_agg="product")
    assert ca.get_config_score(tuple(comps[i] for i in (0, 2, 4))) == 4.0

    ca.write_csv(datadir / "csv" / "feasible.csv")
    assert Path(datadir / "csv" / "feasible.csv").read_text().split("\n") == [
        "A;B;C;score",
        "A1;B2;C3;6.0",
        "A1;B2;C2;4.0",
        "A1;B1;C3;3.0",
        "A1;B1;C2;2.0",
        "",
    ]

    fig = ca.plot()
    fig.write_image(tmpdir / "ca.svg", format="svg")
