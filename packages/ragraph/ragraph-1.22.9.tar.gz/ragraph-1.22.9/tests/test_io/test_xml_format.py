"""XML format support tests."""

import shutil
from pathlib import Path

import pytest
from lxml import etree
from ragraph import datasets
from ragraph.edge import Edge
from ragraph.generic import Annotations
from ragraph.io import xml
from ragraph.node import Node


def test_xml_annotations():
    # Check conversion.
    a = Annotations(foo=4815162342, bar="foo", baz=-4.815162342, fee=True, empty=None)
    elems = xml._annotations_to_elements(a)
    values = [[(a.tag, a.attrib, a.text) for a in e] for e in elems]
    assert values == [
        [("name", {}, "foo"), ("type", {}, "integer"), ("value", {}, "4815162342")],
        [("name", {}, "bar"), ("type", {}, "string"), ("value", {}, "foo")],
        [("name", {}, "baz"), ("type", {}, "float"), ("value", {}, "-4.815162342")],
        [("name", {}, "fee"), ("type", {}, "boolean"), ("value", {}, "true")],
    ]

    # Check roundtrip.
    rt = xml._elements_to_annotations(elems)
    assert rt == a

    # Check for TypeError on invalid type.
    with pytest.raises(TypeError) as e:
        unsupported = Annotations(a=dict(b=2))
        xml._annotations_to_elements(unsupported)
    assert "Cannot export annotation" in str(e.value)


def test_xml_node():
    parent = Node("parent")
    child = Node("child")
    a = Node(
        "A",
        kind="test",
        parent=parent,
        children=[child],
        is_bus=True,
        labels=["first", "second"],
        weights=dict(a=1, b=2),
        annotations=Annotations(extra="A very nice string\nwith two lines."),
    )

    element_a = xml._node_to_element(a)

    assert element_a.tag == "{http://ratio-case.nl/ragraph}Node"
    assert element_a.attrib == {
        "{http://www.omg.org/spec/XMI/20100901}id": ("_n_00000000-0000-0000-0000-000000000002")
    }

    values = [(e.tag, e.attrib, e.text, [(a.tag, a.attrib, a.text) for a in e]) for e in element_a]
    assert values == [
        ("name", {}, "A", []),
        ("uuid", {}, "00000000-0000-0000-0000-000000000002", []),
        ("kind", {}, "test", []),
        ("label", {}, "first", []),
        ("label", {}, "second", []),
        ("{http://ratio-case.nl/ragraph}Weight", {"value": "1"}, "a", []),
        ("{http://ratio-case.nl/ragraph}Weight", {"value": "2"}, "b", []),
        (
            "{http://ratio-case.nl/ragraph}Annotation",
            {},
            None,
            [
                ("name", {}, "extra"),
                ("type", {}, "string"),
                ("value", {}, "A very nice string\nwith two lines."),
            ],
        ),
        ("parent", {}, "_n_00000000-0000-0000-0000-000000000000", []),
        ("child", {}, "_n_00000000-0000-0000-0000-000000000001", []),
        ("is_bus", {}, "true", []),
    ]

    rt = xml._element_to_node(element_a)
    node_dict = {
        "_n_00000000-0000-0000-0000-000000000002": rt,
        "_n_00000000-0000-0000-0000-000000000000": parent,
        "_n_00000000-0000-0000-0000-000000000001": child,
    }
    xml._resolve_node_references(node_dict)

    assert rt.as_dict(use_uuid=False) == a.as_dict(use_uuid=False)


def test_xml_edge():
    source = Node("source")
    target = Node("target")
    edge = Edge(
        source,
        target,
        name="test",
        kind="test",
        labels=["first", "second"],
        weights=dict(a=1, b=2),
        annotations=Annotations(extra="A very nice string\nwith two lines."),
    )

    elem = xml._edge_to_element(edge)

    assert elem.tag == "{http://ratio-case.nl/ragraph}Edge"

    eid = "_e_00000000-0000-0000-0000-000000000002"
    assert elem.attrib == {"{http://www.omg.org/spec/XMI/20100901}id": eid}

    values = [(e.tag, e.attrib, e.text, [(a.tag, a.attrib, a.text) for a in e]) for e in elem]
    assert values == [
        ("name", {}, "test", []),
        ("uuid", {}, "00000000-0000-0000-0000-000000000002", []),
        ("kind", {}, "test", []),
        ("label", {}, "first", []),
        ("label", {}, "second", []),
        ("{http://ratio-case.nl/ragraph}Weight", {"value": "1"}, "a", []),
        ("{http://ratio-case.nl/ragraph}Weight", {"value": "2"}, "b", []),
        (
            "{http://ratio-case.nl/ragraph}Annotation",
            {},
            None,
            [
                ("name", {}, "extra"),
                ("type", {}, "string"),
                ("value", {}, "A very nice string\nwith two lines."),
            ],
        ),
        ("source", {}, "_n_00000000-0000-0000-0000-000000000000", []),
        ("target", {}, "_n_00000000-0000-0000-0000-000000000001", []),
    ]

    node_dict = {
        "_n_00000000-0000-0000-0000-000000000000": source,
        "_n_00000000-0000-0000-0000-000000000001": target,
    }
    rt = xml._element_to_edge(elem, node_dict)
    rt._source = source
    rt._target = target
    assert rt.as_dict(use_uuid=False) == edge.as_dict(use_uuid=False)


def test_to_xml(tmpdir, datadir, update):
    graph = datasets.get("aircraft_engine")
    path = tmpdir / "aircraft_engine.xml"
    xml.to_xml(
        graph,
        path=path,
        bundle_schemas=False,
    )
    if update:
        shutil.copy2(path, datadir / "xml" / "aircraft_engine.xml")

    p = Path(tmpdir)
    assert p / "XMI-Canonical.xsd" not in p.iterdir()
    assert p / "ragraph.xsd" not in p.iterdir()

    xml.to_xml(graph, path=tmpdir / "test2.xml", bundle_schemas=True)
    assert p / "XMI-Canonical.xsd" in p.iterdir()
    assert p / "ragraph.xsd" in p.iterdir()

    doc = etree.parse(str(xml.here / "bare.xml"))
    xml.to_xml(graph, elem=doc.getroot())

    assert xml.schema.validate(doc)


def test_from_xml(datadir):
    p = datadir / "xml" / "aircraft_engine.xml"
    ref = datasets.get("aircraft_engine")
    ref.name = "aircraft_engine"  # Fix name to be non-unique

    g1 = xml.from_xml(path=p, validate=False)
    assert g1 == ref

    g2 = xml.from_xml(enc=p.read_bytes())
    assert g2 == ref

    g3 = xml.from_xml(elem=etree.parse(str(p)).getroot())
    assert g3 == ref

    with pytest.raises(ValueError) as e:
        xml.from_xml()
    assert "arguments should be set" in str(e.value)

    with pytest.raises(ValueError) as e:
        xml.from_xml(path=datadir / "xml" / "faulty.xml")
    assert "Weiiight" in str(e.value)
