"""# GRIP format support"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
from uuid import UUID, uuid4

from lxml import etree

from ragraph import logger
from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node

REPORT_CATEGORIES = [
    "Documenten",
    "Functies",
    "Objecttypen",
    "Organisaties",
    "Systeemeisen",
    "Scope",
    "Raakvlakken",
    "Begrippen",
    "StructuurItems",
    "Managementeisen",
    "Klanteisen",
    "Objecten",
    "Keuzevragen",
    "Producteisen",
    "Processtructuur",
    "RIsicos",
    "Procesrisicos",
    "Onderhoudsproducten",
    "Proceseisen",
    "Onderhoudsactiviteiten",
]

REPORT_CATEGORY_PARAMS = {
    "Documenten": ["ID", "User"],
    "Functies": ["ID", "User"],
    "Objecttypen": ["ID", "User"],
    "Organisaties": ["ID", "User", "Type_uitwisseling"],
    "Systeemeisen": ["ID", "User", "Type_uitwisseling"],
    "Scope": [
        "ID",
        "User",
        "Type_uitwisseling",
        "Eisteksten_aanbieden_als",
        "HerkomstID_vullen_met",
        "Versie_specificatie",
    ],
    "Raakvlakken": ["ID", "User", "Type_uitwisseling"],
    "Begrippen": ["ID", "User", "Type_uitwisseling"],
    "StructuurItems": ["ID", "User", "Type_uitwisseling"],
    "Managementeisen": ["ID", "User", "Type_uitwisseling"],
    "Klanteisen": ["ID", "User", "Type_uitwisseling"],
    "Objecten": ["ID", "User", "Type_uitwisseling"],
    "Keuzevragen": ["ID", "User", "Type_uitwisseling"],
    "Producteisen": ["ID", "User", "Type_uitwisseling"],
    "Processtructuur": ["ID", "User", "Type_uitwisseling"],
    "RIsicos": ["ID", "User", "Type_uitwisseling"],
    "Procesrisicos": ["ID", "User", "Type_uitwisseling"],
    "Onderhoudsproducten": ["ID", "User", "Type_uitwisseling"],
    "Proceseisen": ["ID", "User", "Type_uitwisseling"],
    "Onderhoudsactiviteiten": ["ID", "User", "Type_uitwisseling"],
}


OBJECT_KIND = "object"
OBJECTTYPE_KIND = "objecttype"
FUNCTIE_KIND = "functie"
SYSTEEMEIS_KIND = "systeemeis"
SCOPE_KIND = "scope"
RAAKVLAK_KIND = "raakvlak"
ACTIVITY_KIND = "activity"
PARAMETER_KIND = "param"
INHERITANCE_KIND = "inheritance"


HIERARCHY_MODE_ROOTREFS = {
    "bottom-up": "e0021f8f-114b-ee11-b6a6-001dd8d7027d",
    "top-down": "855342d6-3895-e211-81b6-001d09fa6b1e",
}


def from_grip(path: Union[str, Path], hierarchy_mode: str = "top-down") -> Graph:
    """Decode GRIP XML file, string, or element into a Graph.

    Arguments:
        path: GRIP XML file path.
        hierarchy_mode: One of "bottom-up" or "top-down".
            Defines how the hierarchy relations are stored.

    Returns:
        Graph object.
    """

    tree = etree.parse(str(path))
    root = tree.getroot()

    graph = Graph(
        uuid=root.attrib.get("WorkspaceID"),
        name=root.attrib.get("WorkspaceName"),
        annotations=dict(root.attrib),
    )
    parse_params(graph, root)

    parse_collection(graph, root, "Objecten", "Object", OBJECT_KIND)
    parse_objectenboom(graph, root, hierarchy_mode)

    parse_collection(graph, root, "Objecttypen", "Objecttype", OBJECTTYPE_KIND)
    parse_objecttypenboom(graph, root)

    parse_collection(graph, root, "Functies", "Functie", FUNCTIE_KIND)
    parse_collection(graph, root, "Systeemeisen", "Systeemeis", SYSTEEMEIS_KIND)
    parse_collection(graph, root, "Onderhoudsactiviteiten", "Onderhoudsactiviteit", ACTIVITY_KIND)
    parse_collection(graph, root, "Scope", "Scope", SCOPE_KIND)
    parse_collection(graph, root, "Raakvlakken", "Raakvlak", RAAKVLAK_KIND)

    parse_systeemeis_edges(graph, root)
    parse_object_edges(graph, root)
    parse_scope_edges(graph, root)
    parse_raakvlak_edges(graph, root)
    parse_activity_edges(graph, root)

    # Enrich graph.
    add_raakvlak_annotations(graph)
    add_labels(graph)

    return graph


def parse_params(graph: Graph, root: etree.Element):
    """Decode parameter section of GRIP XML file.

    Arguments:
       graph: Graph object to add nodes to.
       root: Root of XML file.
    """
    scope = root.find("Scope")
    for param in scope.find("RelaticsParameters").iterfind("RelaticsParameter"):
        graph.add_node(Node(kind=PARAMETER_KIND, annotations=param.attrib))


def parse_eisteksten(el: etree.Element, annotations: Dict):
    """Parse eisteksten and store within annotations.

    Arguments:
       el: Systeemeis to be parsed
       annotations: Dictionary in which information must be stored
    """
    if el.find("CI_EistekstDefinitief") is not None:
        annotations.update(
            {
                "CI_EistekstDefinitief": {
                    "R1Sequence": el.find("CI_EistekstDefinitief").attrib["R1Sequence"],
                    "R2Sequence": el.find("CI_EistekstDefinitief").attrib["R2Sequence"],
                    "RootRef": el.find("CI_EistekstDefinitief").attrib["RootRef"],
                    "Type": el.find("CI_EistekstDefinitief").attrib["Type"],
                    "Eistekst": el.find("CI_EistekstDefinitief").find("Eistekst").attrib,
                }
            }
        )

    if el.find("CI_EistekstOrigineel") is not None:
        annotations.update(
            {
                "CI_EistekstOrigineel": {
                    "R1Sequence": el.find("CI_EistekstOrigineel").attrib["R1Sequence"],
                    "R2Sequence": el.find("CI_EistekstOrigineel").attrib["R2Sequence"],
                    "RootRef": el.find("CI_EistekstOrigineel").attrib["RootRef"],
                    "Type": el.find("CI_EistekstOrigineel").attrib["Type"],
                    "EistekstOrigineel": el.find("CI_EistekstOrigineel")
                    .find("EistekstOrigineel")
                    .attrib,
                }
            }
        )


def parse_CI_MEEisObjects(el: etree.Element, annotations: Dict):
    """Parse CI_MEEisObjects and store within annotations.

    Arguments:
       el: Systeemeis to be parsed
       annotations: Dictionary in which information must be stored
    """
    annotations["CI_MEEisObjects"] = []

    for MObj in el.iterfind("CI_MEEisObject"):
        annotations["CI_MEEisObjects"].append(
            {
                "CI_MEEisObject": {
                    "R1Sequence": MObj.attrib["R1Sequence"],
                    "R2Sequence": MObj.attrib["R2Sequence"],
                    "RootRef": MObj.attrib["RootRef"],
                    "Type": MObj.attrib["Type"],
                    "EisObject": {
                        "Name": MObj.find("EisObject").attrib["Name"],
                        "ConfigurationOfRef": MObj.find("EisObject").attrib["ConfigurationOfRef"],
                        "Type": MObj.find("EisObject").attrib["Type"],
                        "GUID": MObj.find("EisObject").attrib["GUID"],
                        "SI_Object": {
                            "R1Sequence": MObj.find("EisObject")
                            .find("SI_Object")
                            .attrib["R1Sequence"],
                            "R2Sequence": MObj.find("EisObject")
                            .find("SI_Object")
                            .attrib["R2Sequence"],
                            "RootRef": MObj.find("EisObject").find("SI_Object").attrib["RootRef"],
                            "Type": MObj.find("EisObject").find("SI_Object").attrib["Type"],
                            "Object": MObj.find("EisObject")
                            .find("SI_Object")
                            .find("Object")
                            .attrib,
                        },
                    },
                }
            }
        )


def parse_CI_MEEisObjecttypen(el: etree.Element, annotations: Dict):
    """Parse CI_MEEisObjectypen and store within annotations.

    Arguments:
       el: Systeemeis to be parsed
       annotations: Dictionary in which information must be stored
    """
    annotations["CI_MEEisObjecttypen"] = []

    for MObjtype in el.iterfind("CI_MEEisObjecttype"):
        annotations["CI_MEEisObjecttypen"].append(
            {
                "CI_MEEisObjecttype": {
                    "R1Sequence": MObjtype.attrib["R1Sequence"],
                    "R2Sequence": MObjtype.attrib["R2Sequence"],
                    "RootRef": MObjtype.attrib["RootRef"],
                    "Type": MObjtype.attrib["Type"],
                    "EisObjecttype": {
                        "Name": MObjtype.find("EisObjecttype").attrib["Name"],
                        "ConfigurationOfRef": MObjtype.find("EisObjecttype").attrib[
                            "ConfigurationOfRef"
                        ],
                        "Type": MObjtype.find("EisObjecttype").attrib["Type"],
                        "GUID": MObjtype.find("EisObjecttype").attrib["GUID"],
                        "SI_Objecttype": {
                            "R1Sequence": MObjtype.find("EisObjecttype")
                            .find("SI_Objecttype")
                            .attrib["R1Sequence"],
                            "R2Sequence": MObjtype.find("EisObjecttype")
                            .find("SI_Objecttype")
                            .attrib["R2Sequence"],
                            "RootRef": MObjtype.find("EisObjecttype")
                            .find("SI_Objecttype")
                            .attrib["RootRef"],
                            "Type": MObjtype.find("EisObjecttype")
                            .find("SI_Objecttype")
                            .attrib["Type"],
                            "Objecttype": MObjtype.find("EisObjecttype")
                            .find("SI_Objecttype")
                            .find("Objecttype")
                            .attrib,
                        },
                    },
                }
            }
        )

def parse_SI_Eistype(el: etree.Element, annotations: Dict):
    """Parse information attached to an SI_Eistype."""
    st = el.find("SI_Eistype")

    annotations["SI_Eistype"] = {
        "R1Sequence": st.attrib["R1Sequence"],
        "R2Sequence": st.attrib["R2Sequence"],
        "RootRef": st.attrib["RootRef"],
        "Type": st.attrib["Type"],
        "Eistype": {
            "Name": st.find("Eistype").attrib["Name"],
            "ConfigurationOfRef": st.find("Eistype").attrib["ConfigurationOfRef"],
            "GUID": st.find("Eistype").attrib["GUID"]
        }
    }


def parse_SI_Periode(el: etree.Element, annotations: Dict):
    """Parse information attached to an SI_Periode."""
    st = el.find("SI_Periode")

    annotations["SI_Periode"] = {
        "R1Sequence": st.attrib["R1Sequence"],
        "R2Sequence": st.attrib["R2Sequence"],
        "RootRef": st.attrib["RootRef"],
        "Type": st.attrib["Type"],
        "Periode": {
            "Name": st.find("Periode").attrib["Name"],
            "ConfigurationOfRef": st.find("Periode").attrib["ConfigurationOfRef"],
            "GUID": st.find("Periode").attrib["GUID"]
        }
    }


def parse_SI_Systeemeisgroepering(el: etree.Element, annotations: Dict):
    """Parse information attached to an SI_Systeemeisgroepering."""
    annotations["SI_Systeemeisgroepering"] = []

    for st in el.iterfind("SI_Systeemeisgroepering"):

        annotations["SI_Systeemeisgroepering"].append({
            "R1Sequence": st.attrib["R1Sequence"],
            "R2Sequence": st.attrib["R2Sequence"],
            "RootRef": st.attrib["RootRef"],
            "Type": st.attrib["Type"],
            "Systeemeisgroepering": {
                "Name": st.find("Systeemeisgroepering").attrib["Name"],
                "ConfigurationOfRef": st.find("Systeemeisgroepering").attrib["ConfigurationOfRef"],
                "GUID": st.find("Systeemeisgroepering").attrib["GUID"]
            }
        })


def parse_CI_Verificatievoorschrift(el: etree.Element, annotations: Dict):
    """Parse information attached to an CI verificationvoorschrift"""
    
    annotations["CI_Verificatievoorschrift"] = []

    for cvv in el.iterfind("CI_Verificatievoorschrift"):
        info = {
            "R1Sequence": cvv.attrib["R1Sequence"],
            "R2Sequence": cvv.attrib["R2Sequence"],
            "RootRef": cvv.attrib["RootRef"],
            "Type": cvv.attrib["Type"],
        }

        parse_verificatie(cvv, info)

        annotations["CI_Verificatievoorschrift"].append(info)


def parse_verificatie(el: etree.Element, annotations: Dict):
    """Parse information attached to Verificatie."""
    v = el.find("Verificatie")

    annotations["Verificatie"] = {
        "Name": v.attrib["Name"],
        "ConfigurationOfRef": v.attrib["ConfigurationOfRef"],
        "GUID": v.attrib["GUID"],
        "Criterium": {
            "RootRef": v.find("Criterium").attrib["RootRef"],
            "Type": v.find("Criterium").attrib["Type"]
        }
    }

    parse_SI_Methode(v, annotations["Verificatie"])
    parse_SI_Fase(v, annotations["Verificatie"])
    parse_CI_Toelichting(v, annotations["Verificatie"])


def parse_SI_Methode(el: etree.Element, annotations: Dict):
    """Parse information attached to an SI_Methode."""
    st = el.find("SI_Methode")

    annotations["SI_Methode"] = {
        "R1Sequence": st.attrib["R1Sequence"],
        "R2Sequence": st.attrib["R2Sequence"],
        "RootRef": st.attrib["RootRef"],
        "Type": st.attrib["Type"],
        "Methode": {
            "Name": st.find("Methode").attrib["Name"],
            "ConfigurationOfRef": st.find("Methode").attrib["ConfigurationOfRef"],
            "GUID": st.find("Methode").attrib["GUID"]
        }
    }


def parse_SI_Fase(el: etree.Element, annotations: Dict):
    """Parse information attached to an SI_Fase."""
    st = el.find("SI_Fase")

    annotations["SI_Fase"] = {
        "R1Sequence": st.attrib["R1Sequence"],
        "R2Sequence": st.attrib["R2Sequence"],
        "RootRef": st.attrib["RootRef"],
        "Type": st.attrib["Type"],
        "Fase": {
            "Name": st.find("Fase").attrib["Name"],
            "ConfigurationOfRef": st.find("Fase").attrib["ConfigurationOfRef"],
            "GUID": st.find("Fase").attrib["GUID"]
        }
    }


def parse_CI_Toelichting(el: etree.Element, annotations: Dict):
    """Parse information attached to an CI_Toelichting."""
    st = el.find("CI_Toelichting")

    annotations["CI_Toelichting"] = {
        "R1Sequence": st.attrib["R1Sequence"],
        "R2Sequence": st.attrib["R2Sequence"],
        "RootRef": st.attrib["RootRef"],
        "Type": st.attrib["Type"],
        "Toelichting": {
            "Name": st.find("Toelichting").attrib["Name"],
            "Description": st.find("Toelichting").attrib.get("Description", ""),
            "ConfigurationOfRef": st.find("Toelichting").attrib["ConfigurationOfRef"],
            "GUID": st.find("Toelichting").attrib["GUID"]
        }
    }

def parse_CI_MEOnderhoudsactiviteitObject(el: etree.Element, annotations: Dict):
    """Parse information for Activity object"""
    annotations["CI_MEOnderhoudsactiviteitObjecten"] = []

    for MEOa in el.iterfind("CI_MEOnderhoudsactiviteitObject"):
        annotations["CI_MEOnderhoudsactiviteitObjecten"].append(
            {
                "CI_MEOnderhoudsactiviteitObject": {
                    "R1Sequence": MEOa.attrib["R1Sequence"],
                    "R2Sequence": MEOa.attrib["R2Sequence"],
                    "RootRef": MEOa.attrib["RootRef"],
                    "Type": MEOa.attrib["Type"],
                    "MEOnderhoudsactiviteitObject": {
                        "Name": MEOa.find("MEOnderhoudsactiviteitObject").attrib["Name"],
                        "ConfigurationOfRef": MEOa.find("MEOnderhoudsactiviteitObject").attrib[
                            "ConfigurationOfRef"
                        ],
                        "Type": MEOa.find("MEOnderhoudsactiviteitObject").attrib["Type"],
                        "GUID": MEOa.find("MEOnderhoudsactiviteitObject").attrib["GUID"],
                        "SI_Object": {
                            "R1Sequence": MEOa.find("MEOnderhoudsactiviteitObject")
                            .find("SI_Object")
                            .attrib["R1Sequence"],
                            "R2Sequence": MEOa.find("MEOnderhoudsactiviteitObject")
                            .find("SI_Object")
                            .attrib["R2Sequence"],
                            "RootRef": MEOa.find("MEOnderhoudsactiviteitObject")
                            .find("SI_Object")
                            .attrib["RootRef"],
                            "Type": MEOa.find("MEOnderhoudsactiviteitObject")
                            .find("SI_Object")
                            .attrib["Type"],
                            "Object": MEOa.find("MEOnderhoudsactiviteitObject")
                            .find("SI_Object")
                            .find("Object")
                            .attrib,
                        },
                    },
                }
            }
        )

def parse_element(el: etree.Element, item: str) -> Dict:
    """Parsing element and store relevant information within Node annotations

    Arguments:
      el: Element to parse.
      item: item kind being parsed.

    Returns:
      Name string and Annotations dictionary.
    """
    annotations = dict(el.attrib)

    if el.find("ID") is not None:
        annotations.update(dict(ID=el.find("ID").attrib))
        if item == "Onderhoudsactiviteit":
            id1 = el.find("ID").attrib.get("IDOA")
        else:
            id1 = el.find("ID").attrib.get("ID1")
        name = el.attrib.get("Name")
        if name and id1 not in name:
            name = f"{name} | {id1}"
        elif not name:
            name = id1
    else:
        name = el.attrib.get("Name")

    for key in ["Code", "BronID", "Eiscodering", "ExterneCode"]:
        if el.find(key) is None:
            continue
        annotations.update({key: el.find(key).attrib})

    if item == "Systeemeis":
        parse_eisteksten(el, annotations)

        if el.find("CI_MEEisObject") is not None:
            parse_CI_MEEisObjects(el=el, annotations=annotations)

        if el.find("CI_MEEisObjecttype") is not None:
            parse_CI_MEEisObjecttypen(el=el, annotations=annotations)

        if el.find("SI_Eistype") is not None:
            parse_SI_Eistype(el=el, annotations=annotations)

        if el.find("SI_Periode") is not None:
            parse_SI_Periode(el=el, annotations=annotations)

        if el.find("SI_Systeemeisgroepering") is not None:
            parse_SI_Systeemeisgroepering(el=el, annotations=annotations)

        if el.find("CI_Verificatievoorschrift") is not None:
            parse_CI_Verificatievoorschrift(el=el, annotations=annotations)

        if el.find("CI_Toelichting") is not None:
            parse_CI_Toelichting(el=el, annotations=annotations)
                

    # Store information for activities
    if item == "Onderhoudsactiviteit":
        if el.find("CI_MEOnderhoudsactiviteitObject") is not None:
            parse_CI_MEOnderhoudsactiviteitObject(el=el, annotations=annotations)
        if el.find("Aard") is not None:
            annotations["Aard"] = el.find("Aard").attrib
        if el.find("Onderhoudsactiviteittype") is not None:
            annotations["Onderhoudsactiviteittype"] = el.find("Onderhoudsactiviteittype").attrib

    # Parse hierarchy relations for objects
    if el.find("SI_Onderliggend") is not None:
        annotations.update({"RootRefOnderliggend": el.find("SI_Onderliggend").attrib["RootRef"]})

    if el.find("SI_Bovenliggend") is not None:
        annotations.update({"RootRefBovenliggend": el.find("SI_Bovenliggend").attrib["RootRef"]})

    # Parse hiearchy relations for objecttypes.
    if el.find("SI_Onderliggende") is not None:
        annotations.update({"RootRefOnderliggende": el.find("SI_Onderliggende").attrib["RootRef"]})

    # Parse relations to functions.
    if el.find("SI_Functie") is not None:
        annotations.update({"RootRefFunctie": el.find("SI_Functie").attrib["RootRef"]})

    # Parse assignment relations to objectttpes.
    if el.find("SI_Objecttype") is not None:
        annotations.update({"RootRefObjecttype": el.find("SI_Objecttype").attrib["RootRef"]})

    return name, annotations


def parse_collection(graph: Graph, root: etree.Element, collection: str, item: str, kind: str):
    """Decode contents of XML file.

    Arguments:
       graph: Graph object to add nodes to
       root: Root of XML file
       collection: Sub-collection to parse (e.g. objecten or Objecttypen)
       item: item kind to parse.
       kind: kind to assign to created nodes.
    """
    coll = root.find(collection)

    if coll is None:
        "No collection found, return."
        return 

    for el in coll.iterfind(item):
        name, annotations = parse_element(el=el, item=item)
        graph.add_node(
            Node(
                uuid=el.attrib.get("GUID"),
                name=name,
                kind=kind,
                annotations=annotations,
            )
        )


def parse_objectenboom(graph: Graph, root: etree.Element, hierarchy_mode: str = "bottom-up"):
    collection = root.find("Objecten")
    for el in collection.iterfind("Object"):
        if hierarchy_mode == "top-down":
            parent = graph[UUID(el.attrib.get("GUID"))]
            for sub in el.iterfind("SI_Onderliggend"):
                for obj in sub.iterfind("ObjectOnderliggend"):
                    child_id = UUID(obj.attrib.get("GUID"))
                    graph[child_id].parent = parent
        elif hierarchy_mode == "bottom-up":
            child = graph[UUID(el.attrib.get("GUID"))]
            for sub in el.iterfind("SI_Bovenliggend"):
                for obj in sub.iterfind("ObjectBovenliggend"):
                    parent_id = UUID(obj.attrib.get("GUID"))
                    child.parent = graph[parent_id]


def parse_objecttypenboom(graph: Graph, root: etree.Element):
    collection = root.find("Objecttypen")
    for el in collection.iterfind("Objecttype"):
        parent = graph[UUID(el.attrib.get("GUID"))]
        for sub in el.iterfind("SI_Onderliggende"):
            for obj in sub.iterfind("Objecttype"):
                child_id = UUID(obj.attrib.get("GUID"))
                graph.add_edge(Edge(source=graph[child_id], target=parent, kind="inheritance"))


def parse_systeemeis_edges(graph: Graph, root: etree.Element):
    elems = root.find("Systeemeisen").iterfind("Systeemeis")
    for el in elems:
        source = graph[UUID(el.attrib.get("GUID"))]

        for me_eis in el.iterfind("CI_MEEisObject"):
            eis_obj = me_eis.find("EisObject")
            eis_obj.attrib.get("GUID")
            object_id = eis_obj.find("SI_Object").find("Object").attrib.get("GUID")
            target = graph[UUID(object_id)]
            graph.add_edge(Edge(source, target, kind=SYSTEEMEIS_KIND))
            graph.add_edge(Edge(target, source, kind=SYSTEEMEIS_KIND))

        for me_eis in el.iterfind("CI_MEEisObjecttype"):
            eis_obj = me_eis.find("EisObjecttype")
            eis_obj.attrib.get("GUID")
            object_id = eis_obj.find("SI_Objecttype").find("Objecttype").attrib.get("GUID")
            target = graph[UUID(object_id)]
            graph.add_edge(Edge(source, target, kind=SYSTEEMEIS_KIND))
            graph.add_edge(Edge(target, source, kind=SYSTEEMEIS_KIND))

        for sub in el.iterfind("SI_Functie"):
            annotations = dict(RootRef=sub.attrib["RootRef"])
            for functie in sub.iterfind("Functie"):
                functie_id = UUID(functie.attrib.get("GUID"))
                target = graph[functie_id]
                graph.add_edge(Edge(source, target, kind=OBJECT_KIND, annotations=annotations))
                graph.add_edge(Edge(target, source, kind=OBJECT_KIND, annotations=annotations))


def parse_object_edges(graph: Graph, root: etree.Element):
    collection = root.find("Objecten")
    for el in collection.iterfind("Object"):
        source = graph[UUID(el.attrib.get("GUID"))]

        for sub in el.iterfind("SI_Functie"):
            annotations = dict(RootRef=sub.attrib["RootRef"])
            for functie in sub.iterfind("Functie"):
                functie_id = UUID(functie.attrib.get("GUID"))
                target = graph[functie_id]
                graph.add_edge(Edge(source, target, kind=OBJECT_KIND, annotations=annotations))
                graph.add_edge(Edge(target, source, kind=OBJECT_KIND, annotations=annotations))

        for sub in el.iterfind("SI_Objecttype"):
            annotations = dict(RootRef=sub.attrib["RootRef"])
            for objecttype in sub.iterfind("Objecttype"):
                objecttype_id = UUID(objecttype.attrib.get("GUID"))
                target = graph[objecttype_id]
                graph.add_edge(Edge(source, target, kind="inheritance", annotations=annotations))
                graph.add_edge(Edge(target, source, kind="inheritance", annotations=annotations))


def parse_scope_edges(graph: Graph, root: etree.Element):
    elems = root.find("Scope").iterfind("Scope")
    for el in elems:
        source = graph[UUID(el.attrib.get("GUID"))]

        for eis in el.iterfind("SI_Systeemeis"):
            annotations = dict(
                RootRef=eis.attrib.get("RootRef"),
                R1Sequence=eis.attrib.get("R1Sequence"),
                R2Sequence=eis.attrib.get("R2Sequence"),
            )
            eis_id = eis.find("Systeemeis").attrib.get("GUID")
            target = graph[UUID(eis_id)]
            graph.add_edge(Edge(source, target, kind=SCOPE_KIND, annotations=annotations))
            graph.add_edge(Edge(target, source, kind=SCOPE_KIND, annotations=annotations))

        for functie in el.iterfind("SI_Functie"):
            annotations = dict(
                RootRef=functie.attrib.get("RootRef"),
                R1Sequence=functie.attrib.get("R1Sequence"),
                R2Sequence=functie.attrib.get("R2Sequence"),
                RootRefFunctie=functie.attrib.get("RootRef")
            )
            functie_id = functie.find("Functie").attrib.get("GUID")
            target = graph[UUID(functie_id)]
            graph.add_edge(Edge(source, target, kind=SCOPE_KIND, annotations=annotations))
            graph.add_edge(Edge(target, source, kind=SCOPE_KIND, annotations=annotations))

        for raakvlak in el.iterfind("SI_Raakvlak"):
            annotations = dict(
                RootRef=raakvlak.attrib.get("RootRef"),
                R1Sequence=raakvlak.attrib.get("R1Sequence"),
                R2Sequence=raakvlak.attrib.get("R2Sequence"),
            )
            if raakvlak.find("SI_Objecttype") is not None:
                annotations["SI_ObjecttypeRootRef"] = raakvlak.find("SI_Objecttype")["RootRef"]

            raakvlak_id = raakvlak.find("Raakvlak").attrib.get("GUID")

            try:
                target = graph[UUID(raakvlak_id)]
            except KeyError:
                logger.warning(f"UUID {UUID(raakvlak_id)} not found.")

            graph.add_edge(Edge(source, target, kind=SCOPE_KIND, annotations=annotations))
            graph.add_edge(Edge(target, source, kind=SCOPE_KIND, annotations=annotations))

        for obj in el.iterfind("SI_Object"):
            annotations = dict(
                RootRef=obj.attrib.get("RootRef"),
                R1Sequence=obj.attrib.get("R1Sequence"),
                R2Sequence=obj.attrib.get("R2Sequence"),
            )
            obj_id = obj.find("Object").attrib.get("GUID")

            try:
                target = graph[UUID(obj_id)]
            except KeyError:
                logger.warning(f"UUID {UUID(obj_id)} not found.")

            graph.add_edge(Edge(source, target, kind=SCOPE_KIND, annotations=annotations))
            graph.add_edge(Edge(target, source, kind=SCOPE_KIND, annotations=annotations))


def parse_activity_edges(graph: Graph, root: etree.Element):
    if root.find("Onderhoudsactiviteiten") is None:
        "No 'Onderhoudsactiviteiten', return."
        return
    
    elems = root.find("Onderhoudsactiviteiten").iterfind("Onderhoudsactiviteit")
    for el in elems:
        source = graph[UUID(el.attrib.get("GUID"))]

        for ci_obj in el.iterfind("CI_MEOnderhoudsactiviteitObject"):
            me_obj = ci_obj.find("MEOnderhoudsactiviteitObject")
            object_id = me_obj.find("SI_Object").find("Object").attrib.get("GUID")
            target = graph[UUID(object_id)]
            graph.add_edge(Edge(source, target, kind=ACTIVITY_KIND))
            graph.add_edge(Edge(target, source, kind=ACTIVITY_KIND))


def parse_raakvlak_edges(graph: Graph, root: etree.Element):
    elems = root.find("Raakvlakken").iterfind("Raakvlak")
    for el in elems:
        raakvlak = graph[UUID(el.attrib.get("GUID"))]

        rootrefs = [item.attrib["RootRef"] for item in el.iterfind("SI_Objecttype")]

        objecten = []
        for item in el.iterfind("SI_Objecttype"):
            try:
                objecten.append(graph[UUID(item.find("Objecttype").attrib.get("GUID"))])
            except KeyError:
                logger.warning(f"UUID {UUID(item.find('Objecttype').attrib.get('GUID'))} not found")

        functies = [
            graph[UUID(item.find("Functie").attrib.get("GUID"))]
            for item in el.iterfind("SI_Functie")
        ]

        for i, obj in enumerate(objecten):
            annotations = dict(RootRef=rootrefs[i])
            graph.add_edge(Edge(raakvlak, obj, kind=RAAKVLAK_KIND, annotations=annotations))
            graph.add_edge(Edge(obj, raakvlak, kind=RAAKVLAK_KIND, annotations=annotations))
            for func in functies:
                graph.add_edge(Edge(obj, func, kind=RAAKVLAK_KIND, annotations=annotations))
                graph.add_edge(Edge(func, obj, kind=RAAKVLAK_KIND, annotations=annotations))

            for other in objecten[i + 1 :]:
                graph.add_edge(Edge(obj, other, kind=RAAKVLAK_KIND, annotations=annotations))
                graph.add_edge(Edge(other, obj, kind=RAAKVLAK_KIND, annotations=annotations))

        for func in functies:
            graph.add_edge(Edge(raakvlak, func, kind=RAAKVLAK_KIND, annotations=annotations))
            graph.add_edge(Edge(func, raakvlak, kind=RAAKVLAK_KIND, annotations=annotations))


def to_grip(
    graph: Graph, path: Optional[Union[str, Path]] = None, hierarchy_mode: str = "top-down"
) -> Optional[str]:
    """Convert a graph with GRIP content structure to a GRIP XML.

    Arguments:
        graph: Graph to convert.
        path: Optional path to write converted XML text to.

    Returns:
        String contents when no path was given.
    """
    report = _build_report(graph, hierarchy_mode)
    byte = etree.tostring(
        report,
        encoding="UTF-8",
        xml_declaration=True,
        pretty_print=True,
    )
    if path:
        Path(path).write_bytes(byte)
    else:
        return byte.decode()


def _build_report(graph: Graph, hierarchy_mode: str = "top-down") -> etree.Element:
    """Convert Graph object to GRIP Compatible XML.

    Note: Only works for Graphs objects that are created using the from_grip function.

    Arguments:
        graph: Graph object to be converted.
        hierarchy_mode: One of "top-down" or "bottom-up".
            Defines how hierarchy relations between objects are stored within the XML file.

    Returns
        XML report.
    """
    a = graph.annotations
    report = etree.Element("Report")
    report.attrib["ReportName"] = a.get("ReportName", str(uuid4()))
    report.attrib["EnvironmentID"] = a.get("EnvironmentID", str(uuid4()))
    report.attrib["EnvironmentName"] = a.get("EnvironmentName", "Rijkswaterstaat")
    report.attrib["EnvironmentURL"] = a.get(
        "EnvironmentURL", "https://rijkswaterstaat.relaticsonline.com"
    )
    report.attrib["GeneratedOn"] = datetime.now().strftime("%Y-%m-%d")
    report.attrib["WorkspaceID"] = a.get("WorkspaceID", str(uuid4()))
    report.attrib["WorkspaceName"] = a.get("WorkspaceName", report.attrib["WorkspaceID"])
    report.attrib["TargetDevice"] = a.get("TargetDevice", "Pc")

    param_nodes = graph.get_nodes_by_kind(PARAMETER_KIND)
    for cat in REPORT_CATEGORIES:
        el = etree.SubElement(report, cat)
        _add_params(
            el, *[p for p in param_nodes if p.annotations["Name"] in REPORT_CATEGORY_PARAMS[cat]]
        )

    for node in graph.nodes:
        if node.kind == OBJECT_KIND:
            _add_object_node(report.find("Objecten"), node, graph, hierarchy_mode)
        elif node.kind == OBJECTTYPE_KIND:
            _add_objecttype_node(report.find("Objecttypen"), node, graph)
        elif node.kind == FUNCTIE_KIND:
            _add_functie_node(report.find("Functies"), node, graph)
        elif node.kind == SYSTEEMEIS_KIND:
            _add_systeemeis_node(report.find("Systeemeisen"), node, graph)
        elif node.kind == SCOPE_KIND:
            _add_scope_node(report.find("Scope"), node, graph)
        elif node.kind == RAAKVLAK_KIND:
            _add_raakvlak_node(report.find("Raakvlakken"), node, graph)
        elif node.kind == ACTIVITY_KIND:
            _add_activity_node(report.find("Onderhoudsactiviteiten"), node)
        elif node.kind == PARAMETER_KIND:
            pass
        else:
            raise ValueError(f"Don't know this node kind '{node.kind}'")

    return report

def _add_objecttype_node(el: etree.Element, node: Node, graph: Graph):
    """Add objecttype instance to Objecttypen collection in XML.

    Arguments:
      el: Collection to add objecttype node to
      node: The objectttpe node to be added.
      graph: Source graph.
    """
    sub = etree.SubElement(
        el,
        "Objecttype",
        attrib=dict(
            Name=node.annotations["Name"],
            ConfigurationOfRef=node.annotations["ConfigurationOfRef"],
            GUID=node.annotations["GUID"],
            Type="ELEMENT",
        ),
    )

    # Add general information.
    etree.SubElement(sub, "ID", attrib=node.annotations["ID"])
    etree.SubElement(sub, "ExterneCode", attrib=node.annotations["ExterneCode"])

    # Add links to functions
    fcount = 1
    objtcount = 1
    for t in graph.targets_of(node):
        if t.kind == "functie":
            subsub = etree.SubElement(
                sub,
                "SI_Functie",
                attrib=dict(
                    R1Sequence="1",
                    R2Sequence=str(fcount),
                    Type="RELATION_ELEMENT",
                    RootRef=node.annotations["RootRefFunctie"],
                ),
            )
            etree.SubElement(
                subsub,
                t.kind.capitalize(),
                attrib=dict(
                    ConfigurationOfRef=t.annotations["ConfigurationOfRef"],
                    GUID=t.annotations["GUID"],
                ),
            )

            fcount += 1

    # Add inheritance links to other Objecttypes.
    for s in graph.sources_of(node):
        if s.kind == "objecttype" and node.annotations.get("RootRefOnderliggende", None):
            subsub = etree.SubElement(
                sub,
                "SI_Onderliggende",
                attrib=dict(
                    R1Sequence="1",
                    R2Sequence=str(objtcount),
                    Type="RELATION_ELEMENT",
                    RootRef=node.annotations["RootRefOnderliggende"],
                ),
            )

            etree.SubElement(
                subsub,
                "Objecttype",
                attrib=dict(
                    ConfigurationOfRef=s.annotations["ConfigurationOfRef"],
                    GUID=s.annotations["GUID"],
                ),
            )

            objtcount += 1


def _add_object_node(
    el: etree.Element,
    node: Node,
    graph: Graph,
    hierarchy_mode: str = "top-down",
    hierarchy_mode_rootrefs=HIERARCHY_MODE_ROOTREFS,
):
    """Add object instance to Objecten collection in XML.

    Arguments:
      el: Collection to add object node to
      node: The objectttpe node to be added.
      graph: Source graph.
      hierarchy_mode_rootrefs: GRIP specific rootrefs for different hierarchy modes.
    """
    sub = etree.SubElement(
        el,
        "Object",
        attrib=dict(
            Name=node.annotations["Name"],
            ConfigurationOfRef=node.annotations["ConfigurationOfRef"],
            GUID=node.annotations["GUID"],
            Type="ELEMENT",
        ),
    )

    # Add general information.
    etree.SubElement(sub, "ID", attrib=node.annotations["ID"])
    etree.SubElement(sub, "Code", attrib=node.annotations["Code"])

    # Add references to sub-objects in "top-down" mode.
    if hierarchy_mode == "top-down":
        for idx, c in enumerate(node.children):
            subsub = etree.SubElement(
                sub,
                "SI_Onderliggend",
                attrib=dict(
                    R1Sequence="1",
                    R2Sequence=str(idx + 1),
                    Type="RELATION_ELEMENT",
                    RootRef=hierarchy_mode_rootrefs["top-down"],
                ),
            )

            etree.SubElement(
                subsub,
                "ObjectOnderliggend",
                attrib=dict(
                    ConfigurationOfRef=c.annotations["ConfigurationOfRef"],
                    GUID=c.annotations["GUID"],
                ),
            )

    # Add reference to parent in "bottom-up" mode.
    elif hierarchy_mode == "bottom-up" and node.parent:
        subsub = etree.SubElement(
            sub,
            "SI_Bovenliggend",
            attrib=dict(
                Type="RELATION_ELEMENT",
                RootRef=hierarchy_mode_rootrefs["bottom-up"],
            ),
        )

        etree.SubElement(
            subsub,
            "ObjectBovenliggend",
            attrib=dict(
                ConfigurationOfRef=node.parent.annotations["ConfigurationOfRef"],
                GUID=node.parent.annotations["GUID"],
            ),
        )

    # Add relations to functions and object types.
    fcount = 1
    objtcount = 1
    for t in graph.targets_of(node):
        if t.kind == "functie":
            subsub = etree.SubElement(
                sub,
                "SI_Functie",
                attrib=dict(
                    R1Sequence="1",
                    R2Sequence=str(fcount),
                    Type="RELATION_ELEMENT",
                    RootRef="e9dc9736-558d-e211-81b6-001d09fa6b1e",
                ),
            )
            etree.SubElement(
                subsub,
                t.kind.capitalize(),
                attrib=dict(
                    ConfigurationOfRef=t.annotations["ConfigurationOfRef"],
                    GUID=t.annotations["GUID"],
                ),
            )

            fcount += 1

        elif t.kind == "objecttype":
            subsub = etree.SubElement(
                sub,
                "SI_Objecttype",
                attrib=dict(
                    R1Sequence="1",
                    R2Sequence=str(objtcount),
                    Type="RELATION_ELEMENT",
                    RootRef=node.annotations["RootRefObjecttype"],
                ),
            )
            etree.SubElement(
                subsub,
                t.kind.capitalize(),
                attrib=dict(
                    ConfigurationOfRef=t.annotations["ConfigurationOfRef"],
                    GUID=t.annotations["GUID"],
                ),
            )

            objtcount += 1


def add_SI_Functie(sub: etree.Element, func: Dict[str, Any], fcount: int, node: Node):
    """Add function reference to super element.

    Note: This is a bit of a weird quirk of the GRIP data structure.

    Arguments:
        sub: super element to add function element to
        func: function reference.
        fcount: Number of referenced function.
        node: Node to which the reference is added.
    """
    subsub = etree.SubElement(
        sub,
        "SI_Functie",
        attrib=dict(
            R1Sequence="1",
            R2Sequence=str(fcount),
            Type="RELATION_ELEMENT",
            RootRef=node.annotations["RootRefFunctie"],
        ),
    )

    etree.SubElement(
        subsub,
        func.kind.capitalize(),
        attrib=dict(
            ConfigurationOfRef=func.annotations["ConfigurationOfRef"],
            GUID=func.annotations["GUID"],
        ),
    )


def _add_functie_node(el: etree.Element, node: Node, graph: Graph):
    """Add functie instance to Functies collection in XML.

    Arguments:
      el: Collection to add object node to
      node: The objectttpe node to be added.
      graph: Source graph.
    """
    sub = etree.SubElement(
        el,
        "Functie",
        attrib=dict(
            Name=node.annotations["Name"],
            ConfigurationOfRef=node.annotations["ConfigurationOfRef"],
            GUID=node.annotations["GUID"],
            Type="ELEMENT",
        ),
    )

    etree.SubElement(sub, "ID", attrib=node.annotations["ID"])
    etree.SubElement(sub, "ExterneCode", attrib=node.annotations["ExterneCode"])


def _add_CI_MEEisObject(sub: etree.Element, MObj: Dict[str, Any]):
    """Add object reference to super element.

    Note: This is a bit of a weird quirk of the GRIP data structure.

    Arguments:
        sub: super element to add function element to
        Mobj: Object reference.
    """
    subsub = etree.SubElement(
        sub,
        "CI_MEEisObject",
        attrib=dict(
            R1Sequence=MObj["CI_MEEisObject"]["R1Sequence"],
            R2Sequence=MObj["CI_MEEisObject"]["R2Sequence"],
            RootRef=MObj["CI_MEEisObject"]["RootRef"],
            Type=MObj["CI_MEEisObject"]["Type"],
        ),
    )

    subsubsub = etree.SubElement(
        subsub,
        "EisObject",
        attrib=dict(
            Name=MObj["CI_MEEisObject"]["EisObject"]["Name"],
            ConfigurationOfRef=MObj["CI_MEEisObject"]["EisObject"]["ConfigurationOfRef"],
            GUID=MObj["CI_MEEisObject"]["EisObject"]["GUID"],
            Type=MObj["CI_MEEisObject"]["EisObject"]["Type"],
        ),
    )

    subsubsubsub = etree.SubElement(
        subsubsub,
        "SI_Object",
        attrib=dict(
            R1Sequence=MObj["CI_MEEisObject"]["EisObject"]["SI_Object"]["R1Sequence"],
            R2Sequence=MObj["CI_MEEisObject"]["EisObject"]["SI_Object"]["R2Sequence"],
            RootRef=MObj["CI_MEEisObject"]["EisObject"]["SI_Object"]["RootRef"],
            Type=MObj["CI_MEEisObject"]["EisObject"]["SI_Object"]["Type"],
        ),
    )

    etree.SubElement(
        subsubsubsub,
        "Object",
        attrib=MObj["CI_MEEisObject"]["EisObject"]["SI_Object"]["Object"],
    )


def _add_CI_MEEisObjecttype(sub: etree.Element, MObjtype: Dict[str, Any]):
    """Add object reference to super element.

    Note: This is a bit of a weird quirk of the GRIP data structure.

    Arguments:
        sub: super element to add function element to
        Mobjtype: Objecttype reference.
    """
    subsub = etree.SubElement(
        sub,
        "CI_MEEisObjecttype",
        attrib=dict(
            R1Sequence=MObjtype["CI_MEEisObjecttype"]["R1Sequence"],
            R2Sequence=MObjtype["CI_MEEisObjecttype"]["R2Sequence"],
            RootRef=MObjtype["CI_MEEisObjecttype"]["RootRef"],
            Type=MObjtype["CI_MEEisObjecttype"]["Type"],
        ),
    )

    subsubsub = etree.SubElement(
        subsub,
        "EisObjecttype",
        attrib=dict(
            Name=MObjtype["CI_MEEisObjecttype"]["EisObjecttype"]["Name"],
            ConfigurationOfRef=MObjtype["CI_MEEisObjecttype"]["EisObjecttype"][
                "ConfigurationOfRef"
            ],
            GUID=MObjtype["CI_MEEisObjecttype"]["EisObjecttype"]["GUID"],
            Type=MObjtype["CI_MEEisObjecttype"]["EisObjecttype"]["Type"],
        ),
    )

    subsubsubsub = etree.SubElement(
        subsubsub,
        "SI_Objecttype",
        attrib=dict(
            R1Sequence=MObjtype["CI_MEEisObjecttype"]["EisObjecttype"]["SI_Objecttype"][
                "R1Sequence"
            ],
            R2Sequence=MObjtype["CI_MEEisObjecttype"]["EisObjecttype"]["SI_Objecttype"][
                "R2Sequence"
            ],
            RootRef=MObjtype["CI_MEEisObjecttype"]["EisObjecttype"]["SI_Objecttype"]["RootRef"],
            Type=MObjtype["CI_MEEisObjecttype"]["EisObjecttype"]["SI_Objecttype"]["Type"],
        ),
    )

    etree.SubElement(
        subsubsubsub,
        "Objecttype",
        attrib=MObjtype["CI_MEEisObjecttype"]["EisObjecttype"]["SI_Objecttype"]["Objecttype"],
    )


def _add_CI_Eistekst(sub: etree.Element, node: Node):
    """Parse requirement tekst and add them to systeemeis element

    Arguments:
      sub: Systeemeis element
      node: Node to fetch data form.
    """
    if node.annotations.get("CI_EistekstDefinitief", None):
        subsub = etree.SubElement(
            sub,
            "CI_EistekstDefinitief",
            attrib=dict(
                R1Sequence=node.annotations["CI_EistekstDefinitief"]["R1Sequence"],
                R2Sequence=node.annotations["CI_EistekstDefinitief"]["R2Sequence"],
                RootRef=node.annotations["CI_EistekstDefinitief"]["RootRef"],
                Type=node.annotations["CI_EistekstDefinitief"]["Type"],
            ),
        )

        etree.SubElement(subsub, "Eistekst", node.annotations["CI_EistekstDefinitief"]["Eistekst"])

    if node.annotations.get("CI_EistekstOrigineel", None):
        subsub = etree.SubElement(
            sub,
            "CI_EistekstOrigineel",
            attrib=dict(
                R1Sequence=node.annotations["CI_EistekstOrigineel"]["R1Sequence"],
                R2Sequence=node.annotations["CI_EistekstOrigineel"]["R2Sequence"],
                RootRef=node.annotations["CI_EistekstOrigineel"]["RootRef"],
                Type=node.annotations["CI_EistekstOrigineel"]["Type"],
            ),
        )

        etree.SubElement(
            subsub,
            "EistekstOrigineel",
            attrib=node.annotations["CI_EistekstOrigineel"]["EistekstOrigineel"],
        )

def _add_Eistype(sub:etree.Element, node: Node):
    etree.SubElement(
        sub,
        "Eistype",
        attrib=dict(
            Name=node.annotations["SI_Eistype"]["Eistype"]["Name"],
            ConfigurationOfRef=node.annotations["SI_Eistype"]["Eistype"]["ConfigurationOfRef"],
            GUID=node.annotations["SI_Eistype"]["Eistype"]["GUID"]
        )
    )


def _add_SI_Eistype(sub:etree.Element, node: Node):
    subsub = etree.SubElement(
        sub,
        "SI_Eistype",
        attrib=dict(
            R1Sequence=node.annotations["SI_Eistype"]["R1Sequence"],
            R2Sequence=node.annotations["SI_Eistype"]["R2Sequence"],
            RootRef=node.annotations["SI_Eistype"]["RootRef"],
            Type=node.annotations["SI_Eistype"]["Type"],
        )
    )

    _add_Eistype(sub=subsub, node=node)

def _add_Periode(sub:etree.Element, node: Node):
    etree.SubElement(
        sub,
        "Periode",
        attrib=dict(
            Name=node.annotations["SI_Periode"]["Periode"]["Name"],
            ConfigurationOfRef=node.annotations["SI_Periode"]["Periode"]["ConfigurationOfRef"],
            GUID=node.annotations["SI_Periode"]["Periode"]["GUID"]
        )
    )


def _add_SI_Periode(sub:etree.Element, node: Node):
    subsub = etree.SubElement(
        sub,
        "SI_Periode",
        attrib=dict(
            R1Sequence=node.annotations["SI_Periode"]["R1Sequence"],
            R2Sequence=node.annotations["SI_Periode"]["R2Sequence"],
            RootRef=node.annotations["SI_Periode"]["RootRef"],
            Type=node.annotations["SI_Periode"]["Type"],
        )
    )

    _add_Periode(sub=subsub, node=node)


def _add_Systeemeisgroepering(sub:etree.Element, group: Dict):
    etree.SubElement(
        sub,
        "Systeemeisgroepering",
        attrib=dict(
            Name=group["Name"],
            ConfigurationOfRef=group["ConfigurationOfRef"],
            GUID=group["GUID"]
        )
    )


def _add_SI_Systeemeisgroepering(sub:etree.Element, sg: Dict):
    subsub = etree.SubElement(
        sub,
        "SI_Systeemeisgroepering",
        attrib=dict(
            R1Sequence=sg["R1Sequence"],
            R2Sequence=sg["R2Sequence"],
            RootRef=sg["RootRef"],
            Type=sg["Type"],
        )
    )

    _add_Systeemeisgroepering(sub=subsub, group=sg["Systeemeisgroepering"])


def _add_Methode(sub:etree.Element, v: Dict):
    etree.SubElement(
        sub,
        "Methode",
        attrib=dict(
            Name=v["SI_Methode"]["Methode"]["Name"],
            ConfigurationOfRef=v["SI_Methode"]["Methode"]["ConfigurationOfRef"],
            GUID=v["SI_Methode"]["Methode"]["GUID"]
        )
    )


def _add_SI_Methode(sub:etree.Element, v: Dict):
    subsub = etree.SubElement(
        sub,
        "SI_Methode",
        attrib=dict(
            R1Sequence=v["SI_Methode"]["R1Sequence"],
            R2Sequence=v["SI_Methode"]["R2Sequence"],
            RootRef=v["SI_Methode"]["RootRef"],
            Type=v["SI_Methode"]["Type"],
        )
    )

    _add_Methode(subsub, v)
    
def _add_Fase(sub:etree.Element, v: Dict):
    etree.SubElement(
        sub,
        "Fase",
        attrib=dict(
            Name=v["SI_Fase"]["Fase"]["Name"],
            ConfigurationOfRef=v["SI_Fase"]["Fase"]["ConfigurationOfRef"],
            GUID=v["SI_Fase"]["Fase"]["GUID"]
        )
    )


def _add_SI_Fase(sub:etree.Element, v: Dict):
    subsub = etree.SubElement(
        sub,
        "SI_Fase",
        attrib=dict(
            R1Sequence=v["SI_Fase"]["R1Sequence"],
            R2Sequence=v["SI_Fase"]["R2Sequence"],
            RootRef=v["SI_Fase"]["RootRef"],
            Type=v["SI_Fase"]["Type"],
        )
    )

    _add_Fase(sub=subsub, v=v)


def _add_Toelichting(sub:etree.Element, v: Dict):
    etree.SubElement(
        sub,
        "Toelichting",
        attrib=dict(
            Name=v["CI_Toelichting"]["Toelichting"]["Name"],
            ConfigurationOfRef=v["CI_Toelichting"]["Toelichting"]["ConfigurationOfRef"],
            GUID=v["CI_Toelichting"]["Toelichting"]["GUID"],
            Description=v["CI_Toelichting"]["Toelichting"]["Description"],
        )
    )


def _add_CI_Toelichting(sub:etree.Element, v: Dict):
    subsub = etree.SubElement(
        sub,
        "CI_Toelichting",
        attrib=dict(
            R1Sequence=v["CI_Toelichting"]["R1Sequence"],
            R2Sequence=v["CI_Toelichting"]["R2Sequence"],
            RootRef=v["CI_Toelichting"]["RootRef"],
            Type=v["CI_Toelichting"]["Type"],
        )
    )

    _add_Toelichting(sub=subsub, v=v)

def _add_Criterium(sub:etree.Element, v: Dict):
    etree.SubElement(
        sub,
        "Criterium",
        attrib=v["Criterium"]
    )


def _add_Verificatie(sub:etree.Element, v: Dict):
    subsub = etree.SubElement(
        sub,
        "Verificatie",
        attrib=dict(
            Name=v["Name"],
            ConfigurationOfRef=v["ConfigurationOfRef"],
            GUID=v["GUID"],
        )
    )

    _add_Criterium(sub=subsub, v=v)
    _add_SI_Methode(sub=subsub, v=v)
    _add_SI_Fase(sub=subsub, v=v)
    _add_CI_Toelichting(sub=subsub, v=v)
    


def _add_CI_Verificatievoorschrift(sub:etree.Element, vv: Dict):
    subsub = etree.SubElement(
        sub,
        "CI_Verificatievoorschrift",
        attrib=dict(
            R1Sequence=vv["R1Sequence"],
            R2Sequence=vv["R2Sequence"],
            RootRef=vv["RootRef"],
            Type=vv["Type"],
        )
    )

    _add_Verificatie(sub=subsub, v=vv["Verificatie"])


def _add_systeemeis_node(el: etree.Element, node: Node, graph: Graph):
    """Add systemeisen instance to Systeemeisen collection in XML.

    Arguments:
      el: Collection to add object node to
      node: Node to fetch data from.
    """
    sub = etree.SubElement(
        el,
        "Systeemeis",
        attrib=dict(
            Name=node.annotations["Name"],
            ConfigurationOfRef=node.annotations["ConfigurationOfRef"],
            GUID=node.annotations["GUID"],
            Type="ELEMENT",
        ),
    )

    etree.SubElement(sub, "ID", attrib=node.annotations["ID"])
    etree.SubElement(sub, "BronID", attrib=node.annotations["BronID"])
    etree.SubElement(sub, "Eiscodering", attrib=node.annotations["Eiscodering"])

    _add_CI_Eistekst(sub=sub, node=node)

    # Add references to objects
    for MObj in node.annotations.get("CI_MEEisObjects", []):
        _add_CI_MEEisObject(sub=sub, MObj=MObj)

    # Add references to objectypes.
    for MObjtype in node.annotations.get("CI_MEEisObjecttypen", []):
        _add_CI_MEEisObjecttype(sub=sub, MObjtype=MObjtype)

    # Add requirement type.
    if node.annotations.get("SI_Eistype", None):
        _add_SI_Eistype(sub=sub, node=node)    

     # Add requirement period.
    if node.annotations.get("SI_Periode", None):
        _add_SI_Periode(sub=sub, node=node)  

    # Add requirement period.
    if node.annotations.get("SI_Periode", None):
        _add_SI_Periode(sub=sub, node=node)  

    # Add requirement groepering.
    for sg in node.annotations.get("SI_Systeemeisgroepering", []):
        _add_SI_Systeemeisgroepering(sub=sub, sg=sg)  

    for vv in node.annotations.get("CI_Verificatievoorschrift", []):
        _add_CI_Verificatievoorschrift(sub=sub, vv=vv)

    if node.annotations.get("CI_Toelichting"):
        _add_CI_Toelichting(sub=sub, v=node.annotations)

    # Add references to functions.
    fcount = 1
    for t in graph.targets_of(node):
        if t.kind == "functie":
            add_SI_Functie(sub=sub, func=t, fcount=fcount, node=node)
            fcount += 1


def _add_scope_node(el: etree.Element, node: Node, graph: Graph):
    """Add scope instance to Scope collection in XML.

    Arguments:
      el: Collection to add object node to
      node: Node to fetch data from.
    """
    sub = etree.SubElement(
        el,
        "Scope",
        attrib=dict(
            Name=node.annotations["Name"],
            GUID=node.annotations["GUID"],
            ConfigurationOfRef=node.annotations["ConfigurationOfRef"],
            Type=node.annotations["Type"],
        ),
    )

    counts = dict(functie=0, raakvlak=0, systeemeis=0, object=0)

    # Add relations to elements part of scope.
    for e in graph.edges_from(node):
        t = e.target

        counts[t.kind] += 1

        subsub = etree.SubElement(
            sub,
            f"SI_{t.kind.capitalize()}",
            attrib=dict(
                R1Sequence="1",
                R2Sequence=str(counts[t.kind]),
                Type="RELATION_ELEMENT",
                RootRef=e.annotations["RootRef"],
            ),
        )
        etree.SubElement(
            subsub,
            t.kind.capitalize(),
            attrib={
                t.kind.capitalize(): t.annotations["Name"],
                "ConfigurationOfRef": t.annotations["ConfigurationOfRef"],
                "GUID": t.annotations["GUID"],
            },
        )


def _add_raakvlak_node(el: etree.Element, node: Node, graph: Graph):
    """Add raakvlak instance to Raakvlakken collection in XML.

    Arguments:
      el: Collection to add object node to
      node: Node to fetch data from.
      graph: Graph to fetch data from.
    """
    sub = etree.SubElement(
        el,
        "Raakvlak",
        attrib=dict(
            Name=node.annotations["Name"],
            Description=node.annotations["Description"],
            ConfigurationOfRef=node.annotations["ConfigurationOfRef"],
            GUID=node.annotations["GUID"],
            Type="ELEMENT",
        ),
    )

    etree.SubElement(sub, "ID", attrib=node.annotations["ID"])

    etree.SubElement(sub, "BronID", attrib=node.annotations["BronID"])

    count = 1
    for t in graph.targets_of(node):
        if t.kind != "object":
            continue

        subsub = etree.SubElement(
            sub,
            f"SI_{t.kind.capitalize()}type",
            attrib=dict(
                R1Sequence="1",
                R2Sequence=str(count),
                Type="RELATION_ELEMENT",
                RootRef=[e for e in graph[node.name, t.name]][0].annotations["RootRef"],
            ),
        )
        etree.SubElement(
            subsub,
            f"{t.kind.capitalize()}type",
            attrib=dict(
                ConfigurationOfRef=t.annotations["ConfigurationOfRef"],
                GUID=t.annotations["GUID"],
            ),
        )

        count += 1


def _add_activity_node(el: etree.Element, node: Node):
    """Add activity instance to Onderhoudsactiviteiten collection in XML.

    Arguments:
      el: Collection to add object node to
      node: Node to fetch data from.
      graph: Graph to fetch data from.
    """
    sub = etree.SubElement(
        el,
        "Onderhoudsactiviteit",
        attrib=dict(
            Name=node.annotations["Name"],
            ConfigurationOfRef=node.annotations["ConfigurationOfRef"],
            GUID=node.annotations["GUID"],
            Type="ELEMENT",
        ),
    )

    etree.SubElement(
        sub, 
        "ID", 
        attrib=dict(
            IDOA=node.annotations["ID"]["IDOA"],
            RootRef=node.annotations["ID"]["RootRef"]
        )
    )

    etree.SubElement(
        sub,
        "Onderhoudsactiviteittype", 
        attrib=node.annotations["Onderhoudsactiviteittype"]
    )

    etree.SubElement(
        sub,
        "Aard", 
        attrib=node.annotations["Aard"]
    )

    for MOa in node.annotations["CI_MEOnderhoudsactiviteitObjecten"]:
        _add_CI_MEOnderhoudsactiviteitObject(sub, MOa)


def _add_CI_MEOnderhoudsactiviteitObject(sub: etree.Element, MObj: Dict[str, Any]):
    """Add object reference to Object.

    Note: This is a bit of a weird quirk of the GRIP data structure.

    Arguments:
        sub: super element to add function element to
        Mobj: Object reference.
    """
    subsub = etree.SubElement(
        sub,
        "CI_MEOnderhoudsactiviteitObject",
        attrib=dict(
            R1Sequence=MObj["CI_MEOnderhoudsactiviteitObject"]["R1Sequence"],
            R2Sequence=MObj["CI_MEOnderhoudsactiviteitObject"]["R2Sequence"],
            RootRef=MObj["CI_MEOnderhoudsactiviteitObject"]["RootRef"],
            Type=MObj["CI_MEOnderhoudsactiviteitObject"]["Type"],
        ),
    )

    subsubsub = etree.SubElement(
        subsub,
        "MEOnderhoudsactiviteitObject",
        attrib=dict(
            Name=MObj["CI_MEOnderhoudsactiviteitObject"]["MEOnderhoudsactiviteitObject"]["Name"],
            ConfigurationOfRef=MObj["CI_MEOnderhoudsactiviteitObject"]["MEOnderhoudsactiviteitObject"]["ConfigurationOfRef"],
            GUID=MObj["CI_MEOnderhoudsactiviteitObject"]["MEOnderhoudsactiviteitObject"]["GUID"],
            Type=MObj["CI_MEOnderhoudsactiviteitObject"]["MEOnderhoudsactiviteitObject"]["Type"],
        ),
    )

    subsubsubsub = etree.SubElement(
        subsubsub,
        "SI_Object",
        attrib=dict(
            R1Sequence=MObj["CI_MEOnderhoudsactiviteitObject"]["MEOnderhoudsactiviteitObject"]["SI_Object"]["R1Sequence"],
            R2Sequence=MObj["CI_MEOnderhoudsactiviteitObject"]["MEOnderhoudsactiviteitObject"]["SI_Object"]["R2Sequence"],
            RootRef=MObj["CI_MEOnderhoudsactiviteitObject"]["MEOnderhoudsactiviteitObject"]["SI_Object"]["RootRef"],
            Type=MObj["CI_MEOnderhoudsactiviteitObject"]["MEOnderhoudsactiviteitObject"]["SI_Object"]["Type"],
        ),
    )

    etree.SubElement(
        subsubsubsub,
        "Object",
        attrib=MObj["CI_MEOnderhoudsactiviteitObject"]["MEOnderhoudsactiviteitObject"]["SI_Object"]["Object"],
    )


def _add_params(el: etree.Element, *params: Node):
    """Add parameter instance to Paramer collection in XML.

    Arguments:
      el: Collection to add object node to
      params: Nodes to fetch data from.
    """
    sub = etree.SubElement(el, "RelaticsParameters")
    for p in params:
        etree.SubElement(sub, "RelaticsParameter", attrib=p.annotations)


def add_raakvlak_annotations(g: Graph):
    """Adding Raakvlak ID's as a string to edges annotations."""
    for e in g.edges:
        if e.source.kind != "object" or e.target.kind != "object":
            continue

        sr = set([t for t in g.targets_of(e.source) if t.kind == "raakvlak"])
        tr = set([t for t in g.targets_of(e.target) if t.kind == "raakvlak"])

        if not sr.intersection(tr):
            e.annotations.raakvlakken = ""
            continue

        raakvlakken = ",".join([r.name.split(" | ")[-1] for r in sr.intersection(tr)])

        e.annotations.raakvlakken = raakvlakken


def add_labels(g: Graph):
    """Add labels to edges based on the description of Raakvlakken."""
    for n in [node for node in g.nodes if node.kind == "raakvlak"]:
        if not n.annotations.get("Description", None):
            # No labels to derive.
            continue
        labels = [label.strip() for label in n.annotations.Description.split(",")]
        variants = [s for s in g.sources_of(n)] + [t for t in g.targets_of(n)]
        for e in g.edges_between_all(variants, variants):
            e.labels = list(set(e.labels + labels))

            if len(e.labels) >= 1 and "default" in e.labels:
                e.labels.remove("default")
