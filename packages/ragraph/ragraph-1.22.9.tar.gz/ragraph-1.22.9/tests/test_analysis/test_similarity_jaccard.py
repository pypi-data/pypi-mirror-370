"""Jaccard Similarity Index tests."""

import numpy as np
import pytest
from ragraph.analysis import similarity
from ragraph.analysis.similarity._jaccard import _calculate, mapping_matrix
from ragraph.analysis.similarity.utils import (
    on_checks,
    on_contains,
    on_hasattrs,
    on_hasweights,
)


@pytest.fixture
def objects():
    return [{"a", 0, "c", "d", 1}, {0, 1, "c", "d", "e"}, {0, "b", "c", "d", "e"}]


@pytest.fixture
def contents():
    return ["a", "b", "c", "d", "e"]


def test_jaccard_calculate():
    a1 = np.array([True, False, True, True, False])
    a2 = np.array([False, False, True, True, True])
    assert _calculate(a1, a2) == 0.5, "Similarity should be 2.0/4.0 == 0.5."
    assert _calculate(np.array([]), np.array([])) == 0.0


def test_on_contents(objects, contents):
    on = on_contains(contents)
    assert on(objects[0]) == [True, False, True, True, False]
    assert on(objects[1]) == [False, False, True, True, True]
    assert on(objects[2]) == [False, True, True, True, True]


def test_on_checks(objects):
    checks = [lambda obj: 0 in obj, lambda obj: 1 in obj, lambda obj: -1 in obj]
    on = on_checks(checks)
    assert on(objects[0]) == [True, True, False]
    assert on(objects[1]) == [True, True, False]
    assert on(objects[2]) == [True, False, False]


def test_on_hasattrs(objects, contents):
    from ragraph.generic import Annotations

    # Only convert strings to key:key values
    dicts = [{k: k for k in obj if isinstance(k, str)} for obj in objects]
    # Convert to Annotations to obtain objects with attributes
    annots = [Annotations(**d) for d in dicts]

    on = on_hasattrs(contents)
    assert on(annots[0]) == [True, False, True, True, False]
    assert on(annots[1]) == [False, False, True, True, True]
    assert on(annots[2]) == [False, True, True, True, True]


def test_on_hasweights():
    from ragraph.node import Node

    nodes = [
        Node("a", weights=dict(a=2, b=4, d=1)),
        Node("b", weights=dict(a=1, b=6, d=2)),
        Node("c", weights=dict(a=1, b=4, c=6, d=1)),
    ]

    on = on_hasweights(["a", "b", "c", "d"], threshold=2.0)
    ref = np.array([[1, 1, 0, 0], [0, 1, 0, 1], [0, 1, 1, 0]])

    assert (mapping_matrix(nodes, on) == ref).all()


def test_mapping_matrix(objects, contents):
    mapping = mapping_matrix(objects, on_contains(contents))
    ref = np.array(
        [
            [True, False, True, True, False],
            [False, False, True, True, True],
            [False, True, True, True, True],
        ]
    )
    assert (mapping == ref).all()


def test_jaccard_index(objects, contents):
    a, b = objects[0], objects[1]
    assert similarity.jaccard_index(a, b, on_contains(["c", "d"])) == 1.0
    assert similarity.jaccard_index(a, b, on_contains(contents)) == 0.5


def test_jaccard_matrix(objects, contents):
    matrix = similarity.jaccard_matrix(objects, on_contains(contents))
    ref = np.array([[1.0, 0.5, 0.4], [0.5, 1.0, 0.75], [0.4, 0.75, 1.0]])
    assert (matrix == matrix.T).all()
    assert (matrix == ref).all()
