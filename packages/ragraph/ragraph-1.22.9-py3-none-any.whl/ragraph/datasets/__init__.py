"""# RaGraph built-in datasets"""

import importlib
from pathlib import Path
from typing import List

from ragraph.graph import Graph
from ragraph.io.csv import from_csv

HERE = Path(__file__).parent


def enum() -> List[str]:
    """Enumerate all available graphs in datasets."""
    return sorted(
        [
            d.name
            for d in HERE.iterdir()
            if d.is_dir()
            and not d.name.startswith(".")
            and not d.name.startswith("_")
            and not d.name == "esl"
        ]
    )


def check(name: str):
    """Check whether a dataset exists."""
    available = enum()
    if name not in available:
        raise ValueError(
            "Dataset {} cannot be found. Please pick one of {}.".format(name, available)
        )


def info(name: str) -> str:
    """Get information about a dataset."""
    check(name)
    mod = importlib.import_module("ragraph.datasets.{}".format(name))
    doc = mod.__doc__
    return str(doc)


def get(name: str) -> Graph:
    """Get a dataset."""
    check(name)

    mod = importlib.import_module("ragraph.datasets.{}".format(name))
    nodes_path = HERE / name / (name + "_nodes.csv")
    edges_path = HERE / name / (name + "_edges.csv")

    node_weights = getattr(mod, "node_weights", None)
    edge_weights = getattr(mod, "edge_weights", None)
    return from_csv(
        nodes_path=nodes_path,
        edges_path=edges_path,
        csv_delimiter=";",
        iter_delimiter=";",
        node_weights=node_weights,
        edge_weights=edge_weights,
        name=name,
        kind="dataset",
    )
