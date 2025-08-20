from pathlib import Path

from ragraph import plot
from ragraph.graph import Graph
from ragraph.io.grip import from_grip


def test_grip_format(datadir: Path, tmpdir: Path):
    g: Graph = from_grip(datadir / "grip" / "grip.xml")
    assert g.nodes, "I want nodes."

    fig = plot.mdm(
        g.leafs, g.edges, style=plot.Style(piemap=(dict(display="kinds", mode="relative")))
    )
    fig.write_image(tmpdir / "grip.svg", format="svg")


def test_grip_objecttype(datadir: Path, tmpdir: Path):
    g: Graph = from_grip(datadir / "grip" / "lock-head-example.xml")

    assert g.nodes, "I want nodes."

    objecttypes = sorted([n.name for n in g.nodes if n.kind == "objecttype"])

    assert objecttypes == [
        "LBS - S_L1.3.1 - Nivelleersysteem constructief | OBT-00062",
        "LBS - S_L1.4.1 - Sluishoofd | OBT-00060",
        "LBS - S_L1.4.1.5 - IJsbestrijdingsysteem | OBT-00065",
        "LBS - S_L1.4.3 - Sluisdeur (constructief) | OBT-00058",
        "LBS - S_L1.4.4 - Dynamisch sluisdeur systeem | OBT-00057",
        "LBS - S_L5.1 - Nivelleersysteem | OBT-00061",
        "LBS - S_L6.1.2 - Bewegingswerk nivelleerschuif (constructief) | OBT-00064",
        "LBS - S_L6.1.2 - Bewegingswerk sluisdeur (constructief) | OBT-00063",
        "NEN2767 - 101 - Aandrijving en bewegingswerk (elektrohydraulisch) | OBT-00067",
        "NEN2767 - 102 - Aandrijving en bewegingswerk (elektromechanisch) | OBT-00068",
        "NEN2767 - 1203 - Frame | OBT-00066",
        "NEN2767 - 1375 - Nivelleerschuif | OBT-00069",
        "NEN2767 - 1383 - Omloopriool | OBT-00070",
        "NEN2767 - 198 - Sluisdeur (hef, punt, rol) | OBT-00072",
        "NEN2767 - 199 - Sluishoofd | OBT-00071",
        "UCS - Beschoeiing - Sluisdeur - Punt - Hout | OBT-00024",
        "UCS - Beschoeiing - Sluisdeur - Punt - Staal | OBT-00025",
        "UCS - Beschoeiing - Sluisdeur - Punt | OBT-00031",
        "UCS - Beschoeiing - Sluisdeur | OBT-00030",
        "UCS - Beschoeiing | OBT-00029",
        "UCS - Bewegingswerk - Nivelleersysteem -  Elektrohydraulische cilinder | OBT-00051",
        "UCS - Bewegingswerk - Nivelleersysteem - Elektromechanische cilinder | OBT-00052",
        "UCS - Bewegingswerk - Nivelleersysteem | OBT-00046",
        "UCS - Bewegingswerk - Sluisdeur - Elektrohydraulische cilinder | OBT-00042",
        "UCS - Bewegingswerk - Sluisdeur - Elektromechanische cilinder | OBT-00041",
        "UCS - Bewegingswerk - Sluisdeur - Horizontaal lierwerk | OBT-00043",
        "UCS - Bewegingswerk - Sluisdeur - Vertikaal  lierwerk | OBT-00044",
        "UCS - Bewegingswerk - Sluisdeur | OBT-00045",
        "UCS - Bewegingswerk | OBT-00040",
        "UCS - Frame - Sluisdeur - Punt - Hout | OBT-00049",
        "UCS - Frame - Sluisdeur - Punt - Staal | OBT-00050",
        "UCS - Frame - Sluisdeur - Punt | OBT-00048",
        "UCS - Frame - Sluisdeur | OBT-00047",
        "UCS - Frame | OBT-00033",
        "UCS - IJsbestrijdingsinstallatie - Bellenscherm | OBT-00054",
        "UCS - IJsbestrijdingsinstallatie | OBT-00053",
        "UCS - Nivelleersysteem - Omloopriolen bodemvulling | OBT-00038",
        "UCS - Nivelleersysteem - Omloopriolen met woelkelder | OBT-00037",
        "UCS - Nivelleersysteem - Omloopriolen overdwars | OBT-00036",
        "UCS - Nivelleersysteem - Omloopriolen wandvulling | OBT-00039",
        "UCS - Nivelleersysteem - Rinketten | OBT-00035",
        "UCS - Nivelleersysteem | OBT-00034",
        "UCS - Sluisdeur - Hef | OBT-00021",
        "UCS - Sluisdeur - Punt | OBT-00020",
        "UCS - Sluisdeur - Rol | OBT-00022",
        "UCS - Sluisdeur - Vierkantkerend | OBT-00023",
        "UCS - Sluisdeur | OBT-00028",
        "UCS - Sluishoofd - standaard | OBT-00059",
    ]

    inheritance_edges = [(e.source.name, e.target.name) for e in g.edges if e.kind == "inheritance"]

    assert len(inheritance_edges) == len(
        [
            (
                "UCS - Nivelleersysteem | OBT-00034",
                "LBS - S_L1.3.1 - Nivelleersysteem constructief | OBT-00062",
            ),
            ("UCS - Sluishoofd - standaard | OBT-00059", "LBS - S_L1.4.1 - Sluishoofd | OBT-00060"),
            (
                "UCS - IJsbestrijdingsinstallatie | OBT-00053",
                "LBS - S_L1.4.1.5 - IJsbestrijdingsysteem | OBT-00065",
            ),
            (
                "UCS - Sluisdeur | OBT-00028",
                "LBS - S_L1.4.3 - Sluisdeur (constructief) | OBT-00058",
            ),
            (
                "UCS - Sluisdeur | OBT-00028",
                "LBS - S_L1.4.4 - Dynamisch sluisdeur systeem | OBT-00057",
            ),
            ("UCS - Nivelleersysteem | OBT-00034", "LBS - S_L5.1 - Nivelleersysteem | OBT-00061"),
            (
                "UCS - Bewegingswerk - Nivelleersysteem | OBT-00046",
                "LBS - S_L6.1.2 - Bewegingswerk nivelleerschuif (constructief) | OBT-00064",
            ),
            (
                "UCS - Bewegingswerk - Sluisdeur | OBT-00045",
                "LBS - S_L6.1.2 - Bewegingswerk sluisdeur (constructief) | OBT-00063",
            ),
            (
                "UCS - Bewegingswerk - Nivelleersysteem -  "
                "Elektrohydraulische cilinder | OBT-00051",
                "NEN2767 - 101 - Aandrijving en bewegingswerk (elektrohydraulisch) | OBT-00067",
            ),
            (
                "UCS - Bewegingswerk - Sluisdeur - Elektrohydraulische cilinder | OBT-00042",
                "NEN2767 - 101 - Aandrijving en bewegingswerk (elektrohydraulisch) | OBT-00067",
            ),
            (
                "UCS - Bewegingswerk - Nivelleersysteem - Elektromechanische cilinder | OBT-00052",
                "NEN2767 - 102 - Aandrijving en bewegingswerk (elektromechanisch) | OBT-00068",
            ),
            (
                "UCS - Bewegingswerk - Sluisdeur - Elektromechanische cilinder | OBT-00041",
                "NEN2767 - 102 - Aandrijving en bewegingswerk (elektromechanisch) | OBT-00068",
            ),
            (
                "UCS - Bewegingswerk - Sluisdeur - Horizontaal lierwerk | OBT-00043",
                "NEN2767 - 102 - Aandrijving en bewegingswerk (elektromechanisch) | OBT-00068",
            ),
            (
                "UCS - Bewegingswerk - Sluisdeur - Vertikaal  lierwerk | OBT-00044",
                "NEN2767 - 102 - Aandrijving en bewegingswerk (elektromechanisch) | OBT-00068",
            ),
            ("UCS - Frame | OBT-00033", "NEN2767 - 1203 - Frame | OBT-00066"),
            (
                "UCS - Nivelleersysteem - Rinketten | OBT-00035",
                "NEN2767 - 1375 - Nivelleerschuif | OBT-00069",
            ),
            (
                "UCS - Nivelleersysteem - Omloopriolen bodemvulling | OBT-00038",
                "NEN2767 - 1383 - Omloopriool | OBT-00070",
            ),
            (
                "UCS - Nivelleersysteem - Omloopriolen met woelkelder | OBT-00037",
                "NEN2767 - 1383 - Omloopriool | OBT-00070",
            ),
            (
                "UCS - Nivelleersysteem - Omloopriolen overdwars | OBT-00036",
                "NEN2767 - 1383 - Omloopriool | OBT-00070",
            ),
            (
                "UCS - Nivelleersysteem - Omloopriolen wandvulling | OBT-00039",
                "NEN2767 - 1383 - Omloopriool | OBT-00070",
            ),
            (
                "UCS - Sluisdeur | OBT-00028",
                "NEN2767 - 198 - Sluisdeur (hef, punt, rol) | OBT-00072",
            ),
            ("UCS - Sluishoofd - standaard | OBT-00059", "NEN2767 - 199 - Sluishoofd | OBT-00071"),
            ("UCS - Beschoeiing - Sluisdeur | OBT-00030", "UCS - Beschoeiing | OBT-00029"),
            (
                "UCS - Beschoeiing - Sluisdeur - Punt | OBT-00031",
                "UCS - Beschoeiing - Sluisdeur | OBT-00030",
            ),
            (
                "UCS - Beschoeiing - Sluisdeur - Punt - Hout | OBT-00024",
                "UCS - Beschoeiing - Sluisdeur - Punt | OBT-00031",
            ),
            (
                "UCS - Beschoeiing - Sluisdeur - Punt - Staal | OBT-00025",
                "UCS - Beschoeiing - Sluisdeur - Punt | OBT-00031",
            ),
            ("UCS - Bewegingswerk - Sluisdeur | OBT-00045", "UCS - Bewegingswerk | OBT-00040"),
            (
                "UCS - Bewegingswerk - Nivelleersysteem | OBT-00046",
                "UCS - Bewegingswerk | OBT-00040",
            ),
            (
                "UCS - Bewegingswerk - Nivelleersysteem -  "
                "Elektrohydraulische cilinder | OBT-00051",
                "UCS - Bewegingswerk - Nivelleersysteem | OBT-00046",
            ),
            (
                "UCS - Bewegingswerk - Nivelleersysteem - "
                "Elektromechanische cilinder | OBT-00052",
                "UCS - Bewegingswerk - Nivelleersysteem | OBT-00046",
            ),
            (
                "UCS - Bewegingswerk - Sluisdeur - Vertikaal  lierwerk | OBT-00044",
                "UCS - Bewegingswerk - Sluisdeur | OBT-00045",
            ),
            (
                "UCS - Bewegingswerk - Sluisdeur - Horizontaal lierwerk | OBT-00043",
                "UCS - Bewegingswerk - Sluisdeur | OBT-00045",
            ),
            (
                "UCS - Bewegingswerk - Sluisdeur - Elektrohydraulische cilinder | OBT-00042",
                "UCS - Bewegingswerk - Sluisdeur | OBT-00045",
            ),
            (
                "UCS - Bewegingswerk - Sluisdeur - Elektromechanische cilinder | OBT-00041",
                "UCS - Bewegingswerk - Sluisdeur | OBT-00045",
            ),
            ("UCS - Frame - Sluisdeur | OBT-00047", "UCS - Frame | OBT-00033"),
            ("UCS - Frame - Sluisdeur - Punt | OBT-00048", "UCS - Frame - Sluisdeur | OBT-00047"),
            (
                "UCS - Frame - Sluisdeur - Punt - Hout | OBT-00049",
                "UCS - Frame - Sluisdeur - Punt | OBT-00048",
            ),
            (
                "UCS - Frame - Sluisdeur - Punt - Staal | OBT-00050",
                "UCS - Frame - Sluisdeur - Punt | OBT-00048",
            ),
            (
                "UCS - IJsbestrijdingsinstallatie - Bellenscherm | OBT-00054",
                "UCS - IJsbestrijdingsinstallatie | OBT-00053",
            ),
            (
                "UCS - Nivelleersysteem - Rinketten | OBT-00035",
                "UCS - Nivelleersysteem | OBT-00034",
            ),
            (
                "UCS - Nivelleersysteem - Omloopriolen overdwars | OBT-00036",
                "UCS - Nivelleersysteem | OBT-00034",
            ),
            (
                "UCS - Nivelleersysteem - Omloopriolen met woelkelder | OBT-00037",
                "UCS - Nivelleersysteem | OBT-00034",
            ),
            (
                "UCS - Nivelleersysteem - Omloopriolen bodemvulling | OBT-00038",
                "UCS - Nivelleersysteem | OBT-00034",
            ),
            (
                "UCS - Nivelleersysteem - Omloopriolen wandvulling | OBT-00039",
                "UCS - Nivelleersysteem | OBT-00034",
            ),
            ("UCS - Sluisdeur - Vierkantkerend | OBT-00023", "UCS - Sluisdeur | OBT-00028"),
            ("UCS - Sluisdeur - Rol | OBT-00022", "UCS - Sluisdeur | OBT-00028"),
            ("UCS - Sluisdeur - Hef | OBT-00021", "UCS - Sluisdeur | OBT-00028"),
            ("UCS - Sluisdeur - Punt | OBT-00020", "UCS - Sluisdeur | OBT-00028"),
            (
                "VARIANT - Bellenscherm | OBJ-02472",
                "UCS - IJsbestrijdingsinstallatie - Bellenscherm | OBT-00054",
            ),
            (
                "UCS - IJsbestrijdingsinstallatie - Bellenscherm | OBT-00054",
                "VARIANT - Bellenscherm | OBJ-02472",
            ),
            (
                "VARIANT - Elektrohydraulische cilinder | OBJ-02468",
                "UCS - Bewegingswerk - Sluisdeur - Elektrohydraulische cilinder | OBT-00042",
            ),
            (
                "UCS - Bewegingswerk - Sluisdeur - Elektrohydraulische cilinder | OBT-00042",
                "VARIANT - Elektrohydraulische cilinder | OBJ-02468",
            ),
            (
                "VARIANT - Elektrohydraulische cilinder | OBJ-02470",
                "UCS - Bewegingswerk - Nivelleersysteem -  "
                "Elektrohydraulische cilinder | OBT-00051",
            ),
            (
                "UCS - Bewegingswerk - Nivelleersysteem -  "
                "Elektrohydraulische cilinder | OBT-00051",
                "VARIANT - Elektrohydraulische cilinder | OBJ-02470",
            ),
            (
                "VARIANT - Elektromechanische cilinder | OBJ-02469",
                "UCS - Bewegingswerk - Sluisdeur - Elektromechanische cilinder | OBT-00041",
            ),
            (
                "UCS - Bewegingswerk - Sluisdeur - Elektromechanische cilinder | OBT-00041",
                "VARIANT - Elektromechanische cilinder | OBJ-02469",
            ),
            (
                "VARIANT - Elektromechanische cilinder | OBJ-02471",
                "UCS - Bewegingswerk - Nivelleersysteem - Elektromechanische cilinder | OBT-00052",
            ),
            (
                "UCS - Bewegingswerk - Nivelleersysteem - Elektromechanische cilinder | OBT-00052",
                "VARIANT - Elektromechanische cilinder | OBJ-02471",
            ),
            ("VARIANT - Hef | OBJ-02460", "UCS - Sluisdeur - Hef | OBT-00021"),
            ("UCS - Sluisdeur - Hef | OBT-00021", "VARIANT - Hef | OBJ-02460"),
            (
                "VARIANT - Horizontaal lierwerk | OBJ-02463",
                "UCS - Bewegingswerk - Sluisdeur - Horizontaal lierwerk | OBT-00043",
            ),
            (
                "UCS - Bewegingswerk - Sluisdeur - Horizontaal lierwerk | OBT-00043",
                "VARIANT - Horizontaal lierwerk | OBJ-02463",
            ),
            (
                "VARIANT - Hout | OBJ-02474",
                "UCS - Beschoeiing - Sluisdeur - Punt - Hout | OBT-00024",
            ),
            (
                "UCS - Beschoeiing - Sluisdeur - Punt - Hout | OBT-00024",
                "VARIANT - Hout | OBJ-02474",
            ),
            ("VARIANT - Hout | OBJ-02478", "UCS - Frame - Sluisdeur - Punt - Hout | OBT-00049"),
            ("UCS - Frame - Sluisdeur - Punt - Hout | OBT-00049", "VARIANT - Hout | OBJ-02478"),
            (
                "VARIANT - Omloopriolen bodemvulling | OBJ-06485",
                "UCS - Nivelleersysteem - Omloopriolen bodemvulling | OBT-00038",
            ),
            (
                "UCS - Nivelleersysteem - Omloopriolen bodemvulling | OBT-00038",
                "VARIANT - Omloopriolen bodemvulling | OBJ-06485",
            ),
            (
                "VARIANT - Omloopriolen met woelkelder | OBJ-02466",
                "UCS - Nivelleersysteem - Omloopriolen met woelkelder | OBT-00037",
            ),
            (
                "UCS - Nivelleersysteem - Omloopriolen met woelkelder | OBT-00037",
                "VARIANT - Omloopriolen met woelkelder | OBJ-02466",
            ),
            (
                "VARIANT - Omloopriolen overdwars | OBJ-06486",
                "UCS - Nivelleersysteem - Omloopriolen overdwars | OBT-00036",
            ),
            (
                "UCS - Nivelleersysteem - Omloopriolen overdwars | OBT-00036",
                "VARIANT - Omloopriolen overdwars | OBJ-06486",
            ),
            (
                "VARIANT - Omloopriolen wandvulling | OBJ-06484",
                "UCS - Nivelleersysteem - Omloopriolen wandvulling | OBT-00039",
            ),
            (
                "UCS - Nivelleersysteem - Omloopriolen wandvulling | OBT-00039",
                "VARIANT - Omloopriolen wandvulling | OBJ-06484",
            ),
            ("VARIANT - Punt | OBJ-02458", "UCS - Sluisdeur - Punt | OBT-00020"),
            ("UCS - Sluisdeur - Punt | OBT-00020", "VARIANT - Punt | OBJ-02458"),
            ("VARIANT - Rinketten | OBJ-02465", "UCS - Nivelleersysteem - Rinketten | OBT-00035"),
            ("UCS - Nivelleersysteem - Rinketten | OBT-00035", "VARIANT - Rinketten | OBJ-02465"),
            ("VARIANT - Rol | OBJ-02461", "UCS - Sluisdeur - Rol | OBT-00022"),
            ("UCS - Sluisdeur - Rol | OBT-00022", "VARIANT - Rol | OBJ-02461"),
            ("VARIANT - Staal | OBJ-02479", "UCS - Frame - Sluisdeur - Punt - Staal | OBT-00050"),
            ("UCS - Frame - Sluisdeur - Punt - Staal | OBT-00050", "VARIANT - Staal | OBJ-02479"),
            (
                "VARIANT - Staal | OBJ-02475",
                "UCS - Beschoeiing - Sluisdeur - Punt - Staal | OBT-00025",
            ),
            (
                "UCS - Beschoeiing - Sluisdeur - Punt - Staal | OBT-00025",
                "VARIANT - Staal | OBJ-02475",
            ),
            ("VARIANT - Standaard | OBJ-02452", "UCS - Sluishoofd - standaard | OBT-00059"),
            ("UCS - Sluishoofd - standaard | OBT-00059", "VARIANT - Standaard | OBJ-02452"),
            (
                "VARIANT - Verticaal lierwerk | OBJ-02464",
                "UCS - Bewegingswerk - Sluisdeur - Vertikaal  lierwerk | OBT-00044",
            ),
            (
                "UCS - Bewegingswerk - Sluisdeur - Vertikaal  lierwerk | OBT-00044",
                "VARIANT - Verticaal lierwerk | OBJ-02464",
            ),
            (
                "VARIANT - Vierkantkerend | OBJ-02459",
                "UCS - Sluisdeur - Vierkantkerend | OBT-00023",
            ),
            (
                "UCS - Sluisdeur - Vierkantkerend | OBT-00023",
                "VARIANT - Vierkantkerend | OBJ-02459",
            ),
        ]
    )
