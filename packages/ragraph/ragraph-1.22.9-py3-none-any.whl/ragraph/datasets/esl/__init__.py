"""# Elephant Specification Language datasets"""

import importlib
from pathlib import Path
from typing import List

HERE = Path(__file__).parent


def enum() -> List[str]:
    """Enumerate all available ESL datasets."""
    return sorted(
        [
            d.name
            for d in HERE.iterdir()
            if d.is_dir() and not d.name.startswith(".") and not d.name.startswith("_")
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
    mod = importlib.import_module("ragraph.datasets.esl.{}".format(name))
    doc = mod.__doc__
    return str(doc)


def get(name: str):
    """Get a dataset.

    Arguments:
        name: Name of the dataset to get (see `ragraph.datasets.esl.enum()`).
    """
    from ragraph.io.esl import from_esl

    check(name)

    esl_files = [str(p) for p in (HERE / name).glob("*.esl")]

    graph = from_esl(*esl_files)
    graph.kind = name

    return graph
