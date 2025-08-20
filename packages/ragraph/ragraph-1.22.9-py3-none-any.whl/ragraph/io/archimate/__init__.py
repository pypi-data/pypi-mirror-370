"""XML format support using The Open Group ArchiMate® Model Exchange File Format.

Reference:
    https://www.opengroup.org/xsd/archimate/
"""

import shutil
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Union

from lxml import etree
from lxml.builder import ElementMaker

from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.io.xml import _get_xmi_id
from ragraph.node import Node

here = Path(__file__).parent
schema_doc = etree.parse(str(here / "archimate3_Model.xsd"))
schema = etree.XMLSchema(schema_doc)
schema_root = schema_doc.getroot()

nsmap = {
    None: "http://www.opengroup.org/xsd/archimate/3.0/",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xml": "http://www.w3.org/XML/1998/namespace",
}
archi = nsmap[None]
xsi = nsmap["xsi"]
xml = nsmap["xml"]
maker = ElementMaker(nsmap=nsmap)

q_type = etree.QName(xsi, "type")
q_lang = etree.QName(xml, "lang")

annot_types = {bool: "boolean", int: "number", float: "number", str: "string"}


def _make_property_definitions(g: Graph) -> etree.Element:
    """Make a propertyDefinitions element to include in the Archimate XML file.

    Arguments:
        g: Graph to inspect and create required property fields for.

    Returns:
        Property definitions XML element.

    Note:
        Labels, Weight and Annotations all get their own prefixed properties.
    """
    propdefs = maker.propertyDefinitions(
        maker.propertyDefinition(maker.name("kind"), {"identifier": "kind", "type": "string"}),
        maker.propertyDefinition(maker.name("is_bus"), {"identifier": "is_bus", "type": "boolean"}),
    )

    for label in sorted(set(g.node_labels + g.edge_labels)):
        propdefs.append(
            maker.propertyDefinition(
                maker.name(f"label: {label}"),
                dict(identifier=f"_l_{label}", type="boolean"),
            )
        )

    for weight in sorted(set(g.node_weight_labels + g.edge_weight_labels)):
        propdefs.append(
            maker.propertyDefinition(
                maker.name(f"weight: {weight}"),
                dict(identifier=f"_w_{weight}", type="number"),
            )
        )

    annots = set.union(
        {
            (k, annot_types[type(v)])
            for n in g.nodes
            for k, v in n.annotations.items()
            if type(v) in annot_types
        },
        {
            (k, annot_types[type(v)])
            for e in g.edges
            for k, v in e.annotations.items()
            if type(v) in annot_types
        },
    )

    for annot in annots:
        propdefs.append(
            maker.propertyDefinition(
                maker.name(f"annotation({annot[1]}): {annot[0]}"),
                dict(identifier=f"_a_{annot[1]}_{annot[0]}", type=annot[1]),
            )
        )

    return propdefs


def _get_properties(obj: Union[Node, Edge]) -> etree.Element:
    """Get the properties element for an object being a Node or Edge.

    Arguments:
        obj: Node or Edge to fetch the properties element for.

    Returns:
        Properties XML element.
    """
    props = maker.properties()

    props.append(maker.property(maker.value(obj.kind), propertyDefinitionRef="kind"))

    for i in sorted(obj.labels):
        props.append(maker.property(maker.value("true"), propertyDefinitionRef=f"_l_{i}"))

    for k in sorted(obj.weights.keys()):
        v = obj.weights[k]
        props.append(maker.property(maker.value(str(float(v))), propertyDefinitionRef=f"_w_{k}"))

    for k in sorted(obj.annotations.keys()):
        v = getattr(obj.annotations, k)
        if type(v) not in annot_types:
            continue
        t = annot_types[type(v)]
        props.append(maker.property(maker.value(str(v)), propertyDefinitionRef=f"_a_{t}_{k}"))

    if isinstance(obj, Node) and obj.is_bus:
        props.append(maker.property(maker.value("true"), propertyDefinitionRef="is_bus"))

    return props


def _node_to_element(node: Node) -> etree.Element:
    """Convert a Node into an XML element.

    Arguments:
        node: Node to convert into an XML element.

    Returns:
        Node XML element.

    Note:
        node.annotations.archimate["type"] determines the type (and therefore layer).
        node.annotations.archimate["documentation"] populates the documentation field.
    """
    # Archimate element name.
    archi_name = maker.name(node.name, {q_lang: "en"})

    # Rudimentary element fields including Archimate element type.
    # Type is determined from the "archimate" annotation:
    archi_type = getattr(node.annotations, "archimate", {}).get("type", "Node")
    archi_fields = {"identifier": _get_xmi_id(node, "_n_"), q_type: archi_type}

    # Archimate element properties (kind/labels/weights/annotations with a value)
    archi_properties = _get_properties(node)

    # Get documentation field if the respective annotation is found.
    documentation = getattr(node.annotations, "archimate", {}).get("documentation", None)

    # Make element with or without documentation.
    if documentation is None:
        elem = maker.element(archi_name, archi_properties, archi_fields)
    else:
        archi_docs = maker.documentation(str(documentation).replace("\n", "\r\n"), {q_lang: "en"})
        elem = maker.element(archi_name, archi_docs, archi_properties, archi_fields)

    return elem


def _hierarchy_to_relationships(graph: Graph) -> Generator[etree.Element, None, None]:
    """Generate relationships of a Graph's Node hierarchy.

    Arguments:
        graph: Graph to generate hierarchical relationship of.

    Yields:
        Composition relationship XML elements.
    """
    for node in graph.nodes:
        if node.parent is None:
            continue
        parent_id = _get_xmi_id(node.parent, "_n_")
        child_id = _get_xmi_id(node, "_n_")

        yield maker.relationship(
            maker.name(f"{node.parent.name} contains {node.name}", {q_lang: "en"}),
            {
                "source": parent_id,
                "target": child_id,
                "identifier": f"_h_{parent_id}_{child_id}",
                q_type: "Composition",
            },
        )


def _edge_to_relationship(edge: Edge) -> etree.Element:
    """Convert an Edge into an XML element.

    Arguments:
        edge: Edge to convert into an XML relationship element.

    Returns:
        Relationship XML element.

    Note:
        edge.annotations.archimate["type"] determines the type (and therefore layer).
        edge.annotations.archimate["documentation"] populates the documentation field.
    """
    # Archimate element name.
    archi_name = maker.name(f"{edge.source.name} to {edge.target.name}", {q_lang: "en"})

    # Rudimentary element fields including Archimate element type.
    # Type is determined from the "archimate" annotation:
    archi_type = getattr(edge.annotations, "archimate", {}).get("type", "Association")
    archi_fields = {
        "source": _get_xmi_id(edge.source, "_n_"),
        "target": _get_xmi_id(edge.target, "_n_"),
        "identifier": _get_xmi_id(edge, "_e_"),
        q_type: archi_type,
    }

    # Archimate element properties (kind/labels/weights/annotations with a value)
    archi_properties = _get_properties(edge)

    # Get documentation field if the respective annotation is found.
    documentation = getattr(edge.annotations, "archimate", {}).get("documentation", None)

    # Make element with or without documentation.
    if documentation is None:
        elem = maker.relationship(
            archi_name,
            archi_properties,
            archi_fields,
        )
    else:
        archi_docs = maker.documentation(str(documentation).replace("\n", "\r\n"), {q_lang: "en"})
        elem = maker.relationship(archi_name, archi_docs, archi_properties, archi_fields)

    return elem


def _expand_requirements_constraints(node: Node, elems: etree.Element, rels: etree.Element):
    """Expand requirements and constraints so that they become an ApplicationFunction
    and Requirement/Constraint combination.

    Arguments:
        node: Nodes to expand.
        elems: XML element to append elements to.
        rels: XML element to append relationships to.

    Note:
        Looks for annotations.archimate["requirement"] or
            annotations.archimate["constraint"] and builds additional elements when
            found.
    """
    # Check whether constraint/requirement field exists and get content.
    annot = getattr(node.annotations, "archimate", {})
    if "constraint" in annot:
        archi_type = "Constraint"
        contents = annot["constraint"]
    elif "requirement" in annot:
        archi_type = "Requirement"
        contents = annot["requirement"]
    else:
        return

    # Append Requirement/Constraint element.
    xmi_id = _get_xmi_id(node, "_r_")
    archi_name = maker.name(node.name, {q_lang: "en"})
    archi_fields = {"identifier": xmi_id, q_type: archi_type}
    archi_docs = maker.documentation(contents, {q_lang: "en"})
    elems.append(maker.element(archi_name, archi_fields, archi_docs))

    # Append Realization edge.
    archi_name = maker.name(f"Realization of {node.name}", {q_lang: "en"})
    archi_fields = {
        "source": _get_xmi_id(node, "_n_"),
        "target": xmi_id,
        "identifier": _get_xmi_id(node, "_e_"),
        q_type: "Realization",
    }
    rels.append(maker.relationship(archi_name, archi_fields))


def to_archimate(
    graph: Graph,
    path: Optional[Union[str, Path]] = None,
    elem: Optional[etree.Element] = None,
    tostring_args: Optional[Dict[str, Any]] = None,
    bundle_schemas: bool = False,
) -> str:
    """Encode Graph to an Archimate model XML element.

    Arguments:
        graph: Graph to convert to XML.
        path: Optional file path to write XML to.
        elem: Optional object to append the Graph to.
        tostring_args: Optional argument overrides to
            [`lxml.etree.tostring`][lxml.etree.tostring].
        bundle_schemas: When exporting to a file, bundle the .xsd schemas.

    Returns:
        XML element.

    Note:
        For both nodes and edges we use the following:
        The `annotations.archimate["type"]` determines the type (and therefore layer).
        The `annotations.archimate["documentation"]` populates the documentation field.
        Refer to https://www.opengroup.org/xsd/archimate/ and the XSD scheme for all
        possible XML element types.
    """
    if elem is None:
        parser = etree.XMLParser(remove_blank_text=True)
        doc = etree.parse(str(here / "bare.xml"), parser)
        root = doc.getroot()
    else:
        root = elem

    elements = maker.elements()
    elements.extend(_node_to_element(n) for n in graph.nodes)
    if len(elements):
        root.append(elements)

    relationships = maker.relationships()
    relationships.extend(_hierarchy_to_relationships(graph))
    relationships.extend(_edge_to_relationship(e) for e in graph.edges)
    if len(relationships):
        root.append(relationships)

    propdefs = _make_property_definitions(graph)
    if len(propdefs):
        root.append(propdefs)

    for n in graph.nodes:
        _expand_requirements_constraints(n, elements, relationships)

    if path is not None:
        p = Path(path)

        args = dict(encoding="UTF-8", xml_declaration=True, pretty_print=True)
        if tostring_args is not None:
            args.update(tostring_args)

        string = etree.tostring(root, **args)
        p.write_bytes(string)

        if bundle_schemas:
            shutil.copy2(here / "archimate3_Model.xsd", p.parent)

    return root


def from_archimate(*args, **kwargs):
    """Archimate XML import is not implemented."""
    raise NotImplementedError("Archimate XML import is not implemented.")
