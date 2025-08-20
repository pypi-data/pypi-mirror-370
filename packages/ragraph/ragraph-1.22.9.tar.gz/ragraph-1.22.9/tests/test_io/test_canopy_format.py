"""Test Canopy data format."""

import pytest
from ragraph import datasets
from ragraph.io import canopy


@pytest.fixture(params=["workspace", "session", "tab", "graph"])
def schema(request):
    return request.param


def test_to_canopy(tmp_path):
    g = datasets.get("climate_control_mg")
    canopy.to_canopy(g, tmp_path / "canopy.json")


def test_from_canopy(datadir, schema):
    gs = canopy.from_canopy(datadir / "canopy" / f"{schema}.canopy.json")
    g = gs[0]
    ref = datasets.get("climate_control_mg")
    assert g.name == ref.name
    assert set(n.name for n in g.nodes) == set([n.name for n in ref.nodes])
    assert len(g.edges) == len(ref.edges)
