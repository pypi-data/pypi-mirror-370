from pathlib import Path

import pytest
from ragraph.io.json import from_json, to_json


def test_simple_json(datadir, tmpdir, update):
    path = datadir / "json" / "simple.json"
    g = from_json(path=path, use_uuid=True)
    if update:
        path.write_text(to_json(g))
    assert g.node_count == 6
    assert g.edge_count == 12
    assert to_json(g) == path.read_text()
    to_json(g, (Path(tmpdir) / "simple.json"))  # Test writing to file.


def test_rich_json(datadir, update):
    path = datadir / "json" / "rich.json"
    g = from_json(path=path, use_uuid=True)
    if update:
        path.write_text(to_json(g))
    assert g.node_kinds == ["broke", "dagobert", "empty", "poor", "rich", "wealthy"]
    assert g.node_weight_labels == ["bank"]
    assert g.edge_kinds == ["dollars", "euros"]
    assert g.edge_labels == ["eu", "money", "us"]
    assert g.node_dict["e"].is_bus
    assert g.get_hierarchy_dict() == {"a": {"b": {}, "c": {}, "f": {}}, "d": {"e": {}}}
    assert g["a"].annotations.comment == "much nice, very comment"
    assert g["a", "b"][0].annotations.comment == "super useful"
    assert to_json(g) == path.read_text()


# JSON should default to default encoder for a random object and let that throw errors
def test_random_obj():
    class Dummy:
        pass

    with pytest.raises(TypeError):
        to_json(Dummy)


def test_from_json(datadir):
    with pytest.raises(ValueError) as e:
        from_json()
    assert str(e.value) == "`path` and `enc` arguments cannot both be `None`."

    with pytest.raises(ValueError) as e:
        from_json("", "")
    assert str(e.value) == "`path` and `enc` arguments cannot both be set."
