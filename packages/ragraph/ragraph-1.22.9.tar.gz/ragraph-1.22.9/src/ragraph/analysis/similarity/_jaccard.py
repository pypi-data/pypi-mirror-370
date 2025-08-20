"""# Jaccard Similarity Index

The index compares two objects, and is calculated as the size of the overlap in properties divided
by total size of properties they possess.

For examples on 'object description functions', please refer to [`the similarity
utilities`][ragraph.analysis.similarity.utils].

References:
    Kosub, S. (2016). A note on the triangle inequality for the Jaccard distance. Retrieved from
    [arXiv.org](https://arxiv.org/pdf/1612.02696.pdf) Jaccard, P. (1901). Étude comparative de la
    distribution florale dans une portion des Alpes et du Jura. Bulletin de La Société Vaudoise Des
    Sciences Naturelles. [DOI: 10.5169/seals-266450](https://doi.org/10.5169/seals-266450)
"""

from typing import Any, Callable, List

import numpy as np


def _calculate(props1: np.array, props2: np.array) -> float:
    """Calculate the Jaccard Index by the boolean object description arrays."""
    both = np.logical_and(props1, props2).sum()
    either = np.logical_or(props1, props2).sum()
    if either:
        return both / either
    return 0.0


def jaccard_index(obj1: Any, obj2: Any, on: Callable[[Any], List[bool]]) -> float:
    """Calculate the Jaccard Similarity Index between to objects based on an object
    description function.

    Arguments:
        obj1: First object to compare.
        obj2: Second object to compare.
        on: Callable that takes an object and describes it with a list of booleans.
            Each entry indicates the possession of a property.

    Returns:
        Jaccard Similarity between two objects, which is calculated as the size of the
        overlap in properties divided by total size of properties they posess.
    """
    props1 = np.array(on(obj1))
    props2 = np.array(on(obj2))
    return _calculate(props1, props2)


def jaccard_matrix(objects: List[Any], on: Callable[[Any], List[bool]]) -> np.ndarray:
    """Calculate the Jaccard Similarity Index for a set of objects based on an object
    description function.

    Arguments:
        objects: List of objects to generate a similarity matrix for.
        on: Callable that takes an object and describes it with a list of booleans.
            Each entry indicates the possession of a property.
    """
    dim = len(objects)
    mapping = mapping_matrix(objects, on)

    matrix = np.eye(dim, dtype=float)
    for i, obj_i in enumerate(objects):
        for j, obj_j in enumerate(objects):
            if j <= i:
                continue
            value = _calculate(mapping[i, :], mapping[j, :])
            matrix[i, j] = value
            matrix[j, i] = value
    return matrix


def mapping_matrix(objects: List[Any], on: Callable[[Any], List[bool]]) -> np.ndarray:
    """Calculate an object-property mapping matrix where each entry (i,j) indicates the
    possession of property j by object i.

    Arguments:
        objects: List of objects to describe.
        on: Callable that takes an object and describes it with a list of booleans.
            Each entry indicates the possession of a property.
    """
    return np.array([on(obj) for obj in objects])
