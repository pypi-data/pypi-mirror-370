"""Tests for the Mapping object used in the plot module."""

import pytest
from ragraph.generic import Mapping, MappingValidationError


def test_mapping_basics():
    class SimpleMap(Mapping):
        _protected = False

    # Test instantiation
    m = SimpleMap(a=1, c=SimpleMap(bla="bla"))
    assert m.get("_data") == m._data
    assert m.a == 1

    # Update
    m.update(SimpleMap(a=2, b="2", c=SimpleMap(foo="bar")))

    # Check the getting methods
    assert m.get("a") == 2
    assert m.a == 2
    assert m["a"] == 2
    assert m.get("b") == "2"
    assert m.b == "2"
    assert m["b"] == "2"

    # Check updating a submap
    m["c"] = dict(foo="qux")
    assert m.c.as_dict() == dict(bla="bla", foo="qux")

    # Some other datatypes
    m.d = {"baz"}
    assert m["d"] == {"baz"}
    m["e"] = []
    assert m.get("e") == []

    # Check iterator
    for k, v in m:
        assert m.get(k) == v

    # Check final dict representation
    assert m.as_dict() == {
        "a": 2,
        "b": "2",
        "c": {"bla": "bla", "foo": "qux"},
        "d": {"baz"},
        "e": [],
    }

    # Validation should not do anything, but certainly not fail.
    m.validate()


def test_mapping_validation():
    def assert_int(x):
        assert isinstance(x, int)

    class SimpleMap(Mapping):
        _protected = False
        _validators = dict(foo=assert_int, bar=assert_int)

    m = SimpleMap()
    m.foo = 2
    m.bar = "2"

    assert m._data["foo"] == 2
    assert str(m) == "SimpleMap({'foo': 2, 'bar': '2'})"

    # Check validation.
    with pytest.raises(MappingValidationError) as e:
        m.validate()
    assert "validation of 'bar' failed" in str(e).lower()


def test_mapping_post_validation():
    msg = "If you never fail, you will never succeed."

    class SimpleMap(Mapping):
        def _post_validation():
            raise Exception(msg)

    m = SimpleMap()

    with pytest.raises(MappingValidationError) as e:
        m.validate()
    assert "Post-validation did not succeed" in str(e)


def test_mapping_update_error():
    m = Mapping()

    with pytest.raises(TypeError) as e:
        m.update(6)
    assert "Expected a dictionary or a Mapping" in str(e)
