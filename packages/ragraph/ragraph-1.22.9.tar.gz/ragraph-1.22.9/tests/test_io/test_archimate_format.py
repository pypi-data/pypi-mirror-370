"""Tests for the Archimate XML format."""

from pathlib import Path

import pytest
from lxml import etree
from ragraph.datasets import esl
from ragraph.edge import Edge
from ragraph.io import archimate
from ragraph.node import Node


def test_archimate_propdefs(datadir: Path, update: bool):
    g = esl.get("pump")
    elem = archimate._make_property_definitions(g)

    text = etree.tostring(elem, pretty_print=True).decode()
    ref = datadir / "archimate" / "propdefs.xml"
    if update:
        ref.write_text(text)
    assert text == ref.read_text()


def test_archimate_node(datadir: Path, update: bool):
    parent = Node("parent")
    node = Node(
        "testnode",
        parent=parent,
        kind="test",
        labels=["label1", "label2"],
        weights=dict(weight_a=1, weight_b=2),
        annotations=dict(
            annotation_a=1,
            archimate=dict(type="BusinessActor", documentation="Docu with\ntwo strings."),
        ),
    )
    node.is_bus = True
    elem = archimate._node_to_element(node)

    text = etree.tostring(elem, pretty_print=True).decode()
    ref = datadir / "archimate" / "node.xml"
    if update:
        ref.write_text(text)
    assert text == ref.read_text()


def test_archimate_edge(datadir: Path, update: bool):
    edge = Edge(
        name="test",
        source=Node("source"),
        target=Node("target"),
        kind="test",
        labels=["label1", "label2"],
        weights=dict(weight_a=1, weight_b=2),
        annotations=dict(
            annotation_a=1,
            archimate=dict(type="Flow", documentation="Doc with\ntwo lines."),
        ),
    )
    elem = archimate._edge_to_relationship(edge)

    text = etree.tostring(elem, pretty_print=True).decode()
    ref = datadir / "archimate" / "edge.xml"
    if update:
        ref.write_text(text)
    assert text == ref.read_text()


# @pytest.mark.skip(reason="Test fails on UUIDs.")
def test_to_archimate(datadir: Path, update: bool, tmpdir):
    g = esl.get("pump")
    annots = g["world"].annotations
    annots.test_annotation = 12
    annots.archimate = dict(type="CommunicationNetwork", documentation="Docu with\ntwo lines.")

    gr = g["world.drive-mechanism.provide-power"]
    gr.annotations = dict(archimate=dict(type="ApplicationFunction", requirement=gr.name))

    elem = archimate.to_archimate(g, path=Path(tmpdir) / "pump.xml", bundle_schemas=True)

    text = etree.tostring(elem, pretty_print=True).decode()
    ref = datadir / "archimate" / "pump.xml"
    if update:
        ref.write_text(text)
    assert text == ref.read_text()


def test_from_archimate():
    with pytest.raises(NotImplementedError):
        archimate.from_archimate(None)
