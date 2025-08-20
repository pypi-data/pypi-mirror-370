"""Tests for _classes module."""

import pytest
from ragraph import datasets
from ragraph.analysis import _classes
from ragraph.node import Node


def test_cast_abstract():
    with pytest.raises(Exception):
        _classes.Cast()  # Cannot instantiate an abstract class.

    class Dummy(_classes.Cast):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, value):
            super().__call__(value)

    d = Dummy()
    assert d(None) is None


def test_node_cast():
    graph = datasets.get("climate_control")
    nc = _classes.NodeCast(graph)
    node = nc("Accumulator")
    assert isinstance(node, Node)

    ref = graph.node_dict["Radiator"]
    assert nc(ref) == ref

    with pytest.raises(ValueError) as e:
        nc.graph = None
        nc("Accumulator")
    assert "must be set" in str(e.value)


def test_parameter_numeric():
    p = _classes.Parameter(
        "test",
        float,
        description="descr.",
        default=True,
        cast=float,
        lower=_classes.Bound(0.0, report="error"),
        upper=_classes.Bound(3.0, report="error"),
    )
    assert p.default == 1.0 and isinstance(p.default, float)
    assert p.parse(2) == 2.0

    with pytest.raises(ValueError) as e:
        p.parse(-1.0)
    assert "below" in str(e.value)

    with pytest.raises(ValueError) as e:
        p.parse(3.1)
    assert "above" in str(e.value)


def test_parameter_enum():
    opts = ["yes", 1, "maybe"]
    p = _classes.Parameter("test", str, description="descr.", default=True, cast=str, enum=opts)
    assert p.enum == {"yes", "1", "maybe"}

    p.parse("yes")

    with pytest.raises(ValueError) as e:
        p.parse("nope")
    assert "not allowed" in str(e.value)
