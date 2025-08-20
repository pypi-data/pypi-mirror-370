from collections import defaultdict
from pathlib import Path

import numpy as np
import pytest
from ragraph.analysis import compatibility as comp
from ragraph.graph import Edge, Graph, Node
from ragraph.io import canopy, csv

EXPORT_GRAPH = False
EXPORT_FIG = False


@pytest.mark.skipif(not EXPORT_GRAPH, reason="No graph export.")
def test_make_rws_graph(datadir):
    import pandas as pd

    r = datadir / "rws"
    mod_fun_con_emb = pd.read_csv(r / "modules-functions-concepts-embodiments.csv", sep=";")
    con_incompat = pd.read_csv(r / "concept-incompatibility-interfaces.csv", sep=";")
    obj_domains = pd.read_csv(r / "objects-domains.csv", sep=";")
    objs = pd.read_csv(r / "objects.csv", sep=";")
    func_if = pd.read_csv(r / "function-interfaces.csv", sep=";")
    domains = pd.read_csv(r / "domains.csv", sep=";")
    con_domains = pd.read_csv(r / "concepts-domains.csv", sep=";")

    obj_nodes = {
        id: Node(name=id, kind="object", annotations=dict(display_name=name))
        for _, id, name in objs.itertuples()
    }

    dom_nodes = {
        name: Node(name=name, kind="constraint")
        for name in set(domains.Domain.unique()).union(domains.Subdomain.unique())
    }
    for _, dom, subdom in domains.itertuples():
        dom_nodes[subdom].parent = dom_nodes[dom]

    elem_nodes = {}
    con_name_to_id = {}
    for (
        _,
        mid,
        mname,
        fid,
        fname,
        cid,
        cname,
        eid,
        ename,
    ) in mod_fun_con_emb.itertuples():
        if mid not in elem_nodes:
            elem_nodes[mid] = Node(
                name=mid,
                kind="element",
                labels=["module"],
                annotations=dict(display_name=mname),
            )
        if fid not in elem_nodes:
            elem_nodes[fid] = Node(
                name=fid,
                kind="element",
                labels=["function"],
                parent=elem_nodes[mid],
                annotations=dict(display_name=fname),
            )
        if cid not in elem_nodes:
            con_name_to_id[cname] = cid
            elem_nodes[cid] = Node(
                name=cid,
                kind="element",
                labels=["concept"],
                parent=elem_nodes[fid],
                annotations=dict(display_name=cname),
            )
        if eid not in elem_nodes:
            elem_nodes[eid] = Node(
                name=eid,
                kind="element",
                labels=["embodiment"],
                parent=elem_nodes[cid],
                annotations=dict(display_name=ename),
            )

    graph = Graph(
        nodes=list(obj_nodes.values()) + list(dom_nodes.values()) + list(elem_nodes.values())
    )

    doms_by_obj = obj_domains.set_index("Object code").drop("Name", axis=1)
    doms_by_con = con_domains.set_index("Concepts")

    for dom_node in dom_nodes.values():
        if dom_node.name in doms_by_obj:
            dom_col = doms_by_obj[dom_node.name].notna()
            for obj_name in dom_col.index[dom_col]:
                obj_node = obj_nodes[obj_name]
                graph.add_edge(
                    Edge(
                        name=f"scope_{dom_node.name}_{obj_name}",
                        source=dom_node,
                        target=obj_node,
                        kind="scope",
                    )
                )
                graph.add_edge(
                    Edge(
                        name=f"scope_{obj_name}_{dom_node.name}",
                        source=obj_node,
                        target=dom_node,
                        kind="scope",
                    )
                )

        if dom_node.name in doms_by_con:
            dom_col = doms_by_con[dom_node.name].notna()
            for con_name in dom_col.index[dom_col]:
                con_node = elem_nodes[con_name_to_id[con_name]]
                graph.add_edge(
                    Edge(
                        name=f"applicability_{dom_node.name}_{con_name}",
                        source=dom_node,
                        target=con_node,
                        kind="applicability",
                    )
                )
                graph.add_edge(
                    Edge(
                        name=f"applicability_{con_name}_{dom_node.name}",
                        source=con_node,
                        target=dom_node,
                        kind="applicability",
                    )
                )

    for _, f_a, fn_a, _, f_b, fn_b, _ in func_if.itertuples():
        a = elem_nodes[f_a]
        b = elem_nodes[f_b]
        assert a.annotations.display_name == fn_a
        assert b.annotations.display_name == fn_b
        try:
            graph.add_edge(
                Edge(
                    name=f"interface_{a.name}_{b.name}",
                    source=a,
                    target=b,
                    kind="interface",
                )
            )
            graph.add_edge(
                Edge(
                    name=f"interface_{b.name}_{a.name}",
                    source=b,
                    target=a,
                    kind="interface",
                )
            )
        except ValueError:
            pass

    for row, c_a, cn_a, _, c_b, cn_b in con_incompat.itertuples():
        a = elem_nodes[c_a]
        b = elem_nodes[c_b]
        assert a.annotations.display_name == cn_a, f"{row}: {a.annotations.display_name} != {cn_a}"
        assert b.annotations.display_name == cn_b, f"{row}: {b.annotations.display_name} != {cn_b}"
        try:
            graph.add_edge(
                Edge(
                    name=f"incompatibility_{a.name}_{b.name}",
                    source=a,
                    target=b,
                    kind="incompatibility",
                )
            )
            graph.add_edge(
                Edge(
                    name=f"incompatibility_{b.name}_{a.name}",
                    source=b,
                    target=a,
                    kind="incompatibility",
                )
            )
        except ValueError:
            pass

    csv.to_csv(graph, r / "config_graph")
    canopy.to_canopy(graph, r / "config_graph.json", fmt="graph")


@pytest.fixture
def rws_graph(datadir: Path):
    r = datadir / "rws"
    return csv.from_csv(r / "config_graph_nodes.csv", r / "config_graph_edges.csv")


def test_rws(rws_graph: Graph, tmpdir):
    variants = defaultdict(list)
    for n in rws_graph.nodes:
        if n.kind == "element" and "concept" in n.labels:
            assert n.parent is not None
            variants[n.parent.name].append(n)

    ca = comp.CompatibilityAnalysis(
        rws_graph,
        variants=variants,
        compatibility_method=comp.get_compatibility_method(
            compatibility_kind=None, incompatibility_kind="incompatibility"
        ),
    )
    assert len(ca._variants_list) == 132
    assert len(ca.variants) == 70

    mat = ca.get_compatibility_matrix()
    assert isinstance(mat, np.ndarray)
    assert np.sum(mat) == 16506.0

    comp.HAVE_NUMPY = False
    mat = ca.get_compatibility_matrix()
    assert isinstance(mat, list)

    if EXPORT_FIG:
        fig = ca.plot()
        fig.write_image(tmpdir / "cim.svg", format="svg")


def test_rws_locks(rws_graph: Graph, datadir: Path):
    variants = defaultdict(list)
    for n in rws_graph.nodes:
        if n.kind == "element" and "concept" in n.labels:
            if not n.parent:
                raise ValueError("Should have a parent.")
            variants[n.parent.name].append(n)

    for obj in [n for n in rws_graph.nodes if n.kind == "object"]:
        constraints = [n for n in rws_graph.targets_of(obj) if n.kind == "constraint"]

        ca = comp.CompatibilityAnalysis(
            rws_graph,
            variants=variants,
            constraints=constraints,
            compatibility_method=comp.get_compatibility_method(
                compatibility_kind=None, incompatibility_kind="incompatibility"
            ),
        )
        ca.write_csv(
            datadir / "rws" / f"{obj.name}_{obj.annotations['display_name']}_feasible.csv",
            scored=False,
        )

    assert ca.disabled_elements == [
        "f17",
        "f18",
        "f24",
        "f25",
        "f31",
        "f32",
        "f35",
        "f38",
    ]


def test_rws_plot(rws_graph: Graph, tmpdir: Path):
    variants = defaultdict(list)
    for n in rws_graph.nodes:
        if n.kind == "element" and "concept" in n.labels:
            assert n.parent is not None
            variants[n.parent.name].append(n)

    ca = comp.CompatibilityAnalysis(
        rws_graph,
        variants=variants,
        interface_method=comp.get_interface_method(),
        compatibility_method=comp.get_compatibility_method(
            compatibility_kind=None, incompatibility_kind="incompatibility"
        ),
    )
    graph = ca.get_plot_graph()
    assert set(graph.node_labels) == {"function", "concept", "module", "embodiment"}
    if EXPORT_FIG:
        fig = ca.plot()
        fig.write_image(tmpdir / "cim.svg", format="svg")
