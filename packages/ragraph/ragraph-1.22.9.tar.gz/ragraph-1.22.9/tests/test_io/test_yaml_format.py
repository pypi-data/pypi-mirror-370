from ragraph.io.yaml import from_yaml, to_yaml


def test_yaml(rich_graph, datadir, tmpdir, update):
    tmp = tmpdir / "test.yaml"
    ref = datadir / "yaml/test.yaml"

    if update:
        to_yaml(rich_graph, ref)

    # Test loading
    ref_data = from_yaml(ref)
    assert ref_data.json_dict == rich_graph.json_dict

    # Test a round trip
    to_yaml(rich_graph, tmp)
    round_trip = from_yaml(tmp)
    assert round_trip.json_dict == rich_graph.json_dict
