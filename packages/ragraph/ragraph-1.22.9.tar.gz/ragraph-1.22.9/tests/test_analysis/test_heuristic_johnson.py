"""Tests for Johnson's circuit finding algorithm."""

from ragraph.analysis import heuristics


def test_heuristic_johnson_cc(graph):
    circuits = list(heuristics.johnson(graph))
    circuits = {tuple(n.name for n in c) for c in circuits}
    ref = {
        ("a", "b", "e", "c"),
        ("a", "c", "e", "b"),
        ("a", "b", "e"),
        ("a", "c", "e"),
        ("a", "e", "b"),
        ("a", "e", "c"),
        ("a", "b"),
        ("a", "c"),
        ("a", "e"),
        ("b", "e"),
        ("c", "e"),
        ("d", "e"),
    }
    assert circuits == ref
