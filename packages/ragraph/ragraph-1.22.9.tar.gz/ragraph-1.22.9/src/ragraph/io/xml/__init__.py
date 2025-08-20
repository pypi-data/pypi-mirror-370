"""XML format support using the XML Metadata Interchange (XMI) standard."""

import shutil
import uuid as _uuid
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

from lxml import etree

from ragraph.edge import Edge
from ragraph.generic import Annotations, Metadata
from ragraph.graph import Graph
from ragraph.node import Node

here = Path(__file__).parent
schema_doc = etree.parse(str(here / "ragraph.xsd"))
schema = etree.XMLSchema(schema_doc)
schema_root = schema_doc.getroot()

nsmap = schema_root.nsmap
q_id = etree.QName(nsmap["xmi"], "id")
q_graph = etree.QName(nsmap["rc"], "Graph")
q_node = etree.QName(nsmap["rc"], "Node")
q_edge = etree.QName(nsmap["rc"], "Edge")
q_weight = etree.QName(nsmap["rc"], "Weight")
q_annotation = etree.QName(nsmap["rc"], "Annotation")


def _get_xmi_id(obj: Metadata, prefix: str) -> str:
    """Convert a string to a valid XMI id."""
    return prefix + str(obj.uuid)


def _metadata_to_subelements(elem: etree.Element, obj: Metadata):
    """Fetch metadata from object and append to element."""
    name = etree.SubElement(elem, "name")
    name.text = obj.name

    uuid = etree.SubElement(elem, "uuid")
    uuid.text = str(obj.uuid)

    kind = etree.SubElement(elem, "kind")
    kind.text = obj.kind

    for lab in obj.labels:
        label = etree.SubElement(elem, "label")
        label.text = lab

    for k, v in obj.weights.items():
        weight = etree.SubElement(elem, q_weight, attrib=dict(value=str(v)))
        weight.text = k

    elem.extend(_annotations_to_elements(obj.annotations))


def _annotations_to_elements(annotations: Annotations) -> List[etree.Element]:
    """Convert Annotations to XML elements."""
    elems = []
    to_str = {int: "integer", float: "float", bool: "boolean"}

    for k, v in annotations.items():
        elem = etree.Element(q_annotation)

        name_elem = etree.SubElement(elem, "name")
        type_elem = etree.SubElement(elem, "type")
        value_elem = etree.SubElement(elem, "value")

        name_elem.text = k

        if v is None:
            type_elem.text = "none"
        elif isinstance(v, str):
            type_elem.text = "string"
            value_elem.text = v
        elif type(v) in to_str:
            type_elem.text = to_str[type(v)]
            value_elem.text = str(v).lower()
        else:
            raise TypeError(
                f"Cannot export annotation '{k}'. ",
                "Only annotations whose type is in {str, bool, int, float, None} are ",
                "supported.",
            )

        elems.append(elem)

    return elems


def _node_to_element(node: Node) -> etree.Element:
    """Convert a Node into an XML element."""

    node_id = _get_xmi_id(node, "_n_")
    elem = etree.Element(q_node, {q_id: node_id})

    _metadata_to_subelements(elem, node)

    if node.parent is not None:
        parent = etree.SubElement(elem, "parent")
        parent.text = _get_xmi_id(node.parent, "_n_")

    for c in node.children:
        child = etree.SubElement(elem, "child")
        child.text = _get_xmi_id(c, "_n_")

    if node.is_bus:
        is_bus = etree.SubElement(elem, "is_bus")
        is_bus.text = "true"

    return elem


def _edge_to_element(edge: Edge) -> etree.Element:
    """Convert an Edge to an XML element."""
    edge_id = _get_xmi_id(edge, "_e_")
    elem = etree.Element(q_edge, {q_id: edge_id})

    _metadata_to_subelements(elem, edge)

    source = etree.SubElement(elem, "source")
    source.text = _get_xmi_id(edge.source, "_n_")

    target = etree.SubElement(elem, "target")
    target.text = _get_xmi_id(edge.target, "_n_")

    return elem


def to_xml(
    graph: Graph,
    path: Optional[Union[str, Path]] = None,
    elem: Optional[etree.Element] = None,
    tostring_args: Optional[Dict[str, Any]] = None,
    bundle_schemas: bool = False,
) -> str:
    """Encode Graph to an XML element.

    Arguments:
        graph: Graph to convert to XML.
        path: Optional file path to write XML to.
        elem: Optional object to append the Graph to.
        tostring_args: Optional argument overrides to
            [`lxml.etree.tostring`][lxml.etree.tostring].
        bundle_schemas: When exporting to a file, bundle the .xsd schemas.

    Returns:
        XML element.
    """

    if elem is None:
        parser = etree.XMLParser(remove_blank_text=True)
        doc = etree.parse(str(here / "bare.xml"), parser)
        elem = doc.getroot()

    graph_elem = etree.SubElement(elem, q_graph, nsmap=nsmap)
    _metadata_to_subelements(graph_elem, graph)
    graph_elem.extend(_node_to_element(n) for n in graph.nodes)
    graph_elem.extend(_edge_to_element(e) for e in graph.edges)

    if path is not None:
        p = Path(path)

        args = dict(encoding="UTF-8", xml_declaration=True, pretty_print=True)
        if tostring_args is not None:
            args.update(tostring_args)

        string = etree.tostring(elem, **args)
        p.write_bytes(string)

        if bundle_schemas:
            shutil.copy2(here / "ragraph.xsd", p.parent)
            shutil.copy2(here / "XMI-Canonical.xsd", p.parent)

    return elem


def _elements_to_annotations(elems: Iterable[etree.Element]) -> Annotations:
    """Convert XML elements of type rc:Annotation to an Annotations object."""
    to_value: Dict[str, Callable] = {
        "integer": int,
        "float": float,
        "boolean": bool,
        "none": lambda x: None,
    }

    annots = Annotations()
    for e in elems:
        name = e.find(".//name").text
        cast = to_value.get(e.find(".//type").text, str)
        value = cast(e.find(".//value").text)
        setattr(annots, name, value)

    return annots


def _elements_to_weights(elems: Iterable[etree.Element]) -> Dict[str, Any]:
    """Convert XML elements of rc:Weight type to a weights dictionary."""
    weights = {
        e.text: float(e.attrib["value"]) if "." in e.attrib["value"] else int(e.attrib["value"])
        for e in elems
    }
    return weights


def _element_to_metadata(elem: etree.Element, obj: Metadata):
    """Extract metadata from element."""
    obj.name = elem.find("name").text
    obj.uuid = _uuid.UUID(elem.find("uuid").text)
    obj.kind = elem.find("kind").text
    obj.labels = [i.text for i in elem.findall("label")]
    obj.weights = _elements_to_weights(elem.findall(f"{q_weight}"))
    obj.annotations = _elements_to_annotations(elem.findall(f"{q_annotation}"))


def _element_to_node(elem: etree.Element) -> Node:
    """Convert an XML element to a Node (parent and children stored as strings)."""
    node = Node()
    _element_to_metadata(elem, node)

    parent = elem.find("parent")
    if parent is not None:
        node._parent = parent.text

    node._children = [i.text for i in elem.findall("child")]

    node.is_bus = (
        elem.find("is_bus").text.lower() == "true" if elem.find("is_bus") is not None else False
    )

    return node


def _element_to_edge(elem: etree.Element, node_dict: Dict[str, Any]) -> Edge:
    """Convert an XML element to an Edge object."""
    source = node_dict[elem.find("source").text]
    target = node_dict[elem.find("target").text]
    edge = Edge(source, target)
    _element_to_metadata(elem, edge)
    return edge


def _resolve_node_references(node_dict: Dict[str, Node]):
    """Resolve parent/child nodal string references from names to nodes."""
    for k, v in node_dict.items():
        if isinstance(v._parent, str):
            v._parent = node_dict[v._parent]
        if v._children:
            if isinstance(v._children[0], str):
                v._children = [node_dict[c] for c in v._children]  # type: ignore


def from_xml(
    path: Optional[Union[str, Path]] = None,
    enc: Optional[str] = None,
    elem: Optional[etree.Element] = None,
    validate: bool = True,
) -> Graph:
    """Decode XML file, string, or element into a Graph.

    Arguments:
        path: XML file path.
        enc: XML encoded string.
        elem: XML Element.
        validate: Whether to validate the XML input.

    Returns:
        Graph object.

    Note:
        You should only provide one of `path`, `enc`, or `elem`, which are handled in that order of
        precedence.
    """
    # Parse input XML.
    if path is not None:
        elem = etree.parse(str(Path(path))).getroot()
    elif enc is not None:
        elem = etree.fromstring(enc)
    elif elem is not None:
        assert isinstance(elem, etree._Element)
    else:
        raise ValueError("At least one of the 'path', 'enc', or 'elem' arguments should be set.")

    # Validate if required.
    if validate and not schema.validate(elem):
        raise ValueError(f"Schema validation failed: \n\n{schema.error_log}")

    # Find the Graph XML element.
    g = elem.find(f".//{q_graph}")

    # Parse nodes.
    node_dict = dict()
    for elem in g.findall(f".//{q_node}"):
        node = _element_to_node(elem)
        node_dict[elem.attrib[q_id]] = node
    _resolve_node_references(node_dict)

    # Parse edges.
    edges = [_element_to_edge(e, node_dict) for e in g.findall(f".//{q_edge}")]

    # Build graph and return.
    graph = Graph(nodes=node_dict.values(), edges=edges)
    _element_to_metadata(g, graph)
    return graph
