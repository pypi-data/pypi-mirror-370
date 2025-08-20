import pytest
from ragraph.io.csv import _convert_to_num, _load_edges, from_csv, to_csv


def test_from_csv(datadir):
    # Try from csv in increasing complexity.
    from_csv()  # returns an empty graph
    from_csv(nodes_path=datadir / "csv" / "simple_nodes.csv")
    from_csv(edges_path=datadir / "csv" / "simple_edges.csv")
    from_csv(
        nodes_path=datadir / "csv" / "simple_nodes.csv",
        edges_path=datadir / "csv" / "simple_edges.csv",
    )
    from_csv(nodes_path=datadir / "csv" / "rich_nodes.csv", node_weights=["bank"])
    from_csv(edges_path=datadir / "csv" / "rich_edges.csv", edge_weights=["amount"])

    # Check extensive one.
    g = from_csv(
        nodes_path=datadir / "csv" / "rich_nodes.csv",
        edges_path=datadir / "csv" / "rich_edges.csv",
        node_weights=["bank"],
        edge_weights=["amount"],
    )

    assert g.node_kinds == ["broke", "dagobert", "empty", "poor", "rich", "wealthy"]
    assert g.node_labels == ["default", "labeled", "special"]
    assert g.node_weight_labels == ["bank"]
    assert g.edge_kinds == ["dollars", "euros"]
    assert g.edge_labels == ["eu", "money", "us"]
    assert g.node_dict["e"].is_bus
    assert g.get_hierarchy_dict() == {"a": {"b": {}, "c": {}, "f": {}}, "d": {"e": {}}}
    assert g["a"].annotations.comment == "much nice, very comment"
    assert g["a", "b"][0].annotations.comment == "super useful"


def test_from_csv_errors(datadir):
    with pytest.raises(ValueError) as e:
        from_csv(nodes_path=datadir / "csv" / "wrong.csv")
        assert "at least a 'name' column" in str(e.value)

    with pytest.raises(ValueError) as e:
        from_csv(edges_path=datadir / "csv" / "wrong.csv")
        assert "at least a 'source' and 'target' column" in str(e.value)

    with pytest.raises(ValueError) as e:
        _load_edges(datadir / "csv" / "wrong.csv", ";", ";", dict(), list())
        assert "at least a 'source' and 'target' column" in str(e.value)

    with pytest.raises(ValueError) as e:
        from_csv(nodes_path=datadir / "csv" / "dupe_nodes.csv")
        assert "not unique" in str(e.value)


def test_to_csv(datadir, tmpdir, update):
    g = from_csv(
        nodes_path=datadir / "csv" / "rich_nodes.csv",
        edges_path=datadir / "csv" / "rich_edges.csv",
        node_weights=["bank"],
        edge_weights=["amount"],
    )
    if update:
        to_csv(g, datadir / "csv/rich")
    to_csv(g, tmpdir / "graph")

    nodes_expected = (datadir / "csv" / "rich_nodes.csv").read_text("utf-8")
    nodes_output = (tmpdir / "graph_nodes.csv").read_text("utf-8")

    (datadir / "csv" / "rich_nodes.csv").write_text(nodes_output)

    assert nodes_output == nodes_expected

    edges_expected = (datadir / "csv" / "rich_edges.csv").read_text("utf-8")
    edges_output = (tmpdir / "graph_edges.csv").read_text("utf-8")
    assert edges_output == edges_expected


def test_num_convert():
    assert _convert_to_num(6) == 6, "Integer convert should do nothing."
    assert _convert_to_num(" true") is True, "String bool convert should return True."
    assert _convert_to_num("FALSE  ") is False, "String bool convert should return False."

    with pytest.warns(UserWarning) as w:
        _convert_to_num("faulty")
    assert w[0].message.args[0] == " ".join(
        [
            "You are assigning a string as a weight property.",
            "Please use a float, integer, or a Bool.",
            "A default value of 1.0 is used as a replacement for {}.".format("faulty"),
        ]
    )
