"""Tests for sequence metrics module."""

import numpy as np
from ragraph.analysis.sequence import metrics as mx


def test_sequence_metric_feedback_marks(matrix):
    val, contrib = mx.feedback_marks(matrix)
    expected = np.array(
        [
            [0.0, 9.0, 1.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]
    )
    assert (contrib == expected).all()
    assert val == expected.sum()


def test_sequence_metric_feedback_distance(matrix):
    val, contrib = mx.feedback_distance(matrix)
    expected = np.array(
        [
            [0.0, 9.0, 2.0, 0.0, 4.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 3.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 2.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]
    )
    assert (contrib == expected).all()
    assert val == expected.sum()


def test_sequence_metric_lower_left(matrix):
    val, contrib = mx.lower_left(matrix)
    expected = np.array(
        [
            [0.0, 54.0, 7.0, 0.0, 9.0, 0.0],
            [36.0, 0.0, 0.0, 0.0, 8.0, 0.0],
            [3.0, 0.0, 0.0, 0.0, 7.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 6.0, 0.0],
            [1.0, 2.0, 3.0, 4.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]
    )
    assert (contrib == expected).all()
    assert val == expected.sum()


def test_sequence_metric_feedback_lower_left(matrix):
    val, contrib = mx.feedback_lower_left(matrix)
    expected = np.array(
        [
            [0.00e0, 4.41e4, 6.40e3, 0.00e0, 1.00e4, 0.00e0],
            [2.25e2, 0.00e0, 0.00e0, 0.00e0, 8.10e3, 0.00e0],
            [1.60e1, 0.00e0, 0.00e0, 0.00e0, 6.40e3, 0.00e0],
            [0.00e0, 0.00e0, 0.00e0, 0.00e0, 4.90e3, 0.00e0],
            [4.00e0, 9.00e0, 1.60e1, 2.50e1, 0.00e0, 0.00e0],
            [0.00e0, 0.00e0, 0.00e0, 0.00e0, 0.00e0, 0.00e0],
        ]
    )
    assert (contrib == expected).all()
    assert val == expected.sum()


def test_sequence_metric_feedback_crossover(matrix):
    val, mats = mx.feedback_crossover(matrix, fb=0.9, co=0.1)
    fb_expected = np.array(
        [
            [0.0, 1.0, 1.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]
    )
    co_expected = np.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]
    )
    assert (mats[0] == fb_expected).all()
    assert (mats[1] == co_expected).all()
    assert val == 5.5
