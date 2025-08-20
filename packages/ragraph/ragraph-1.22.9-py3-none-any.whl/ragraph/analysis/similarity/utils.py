"""#Similarity analysis utilities"""

from typing import Any, Callable, List


def on_hasattrs(attrs: List[str]) -> Callable[[Any], List[bool]]:
    """Get an object description function that checks whether an instance possesses certain
    attributes. It does not check the values thereof!

    Arguments:
        attrs: List of attributes to check the existence of.

    Returns:
        Object description function indicating attribute possession.
    """
    return lambda obj: [hasattr(obj, attr) for attr in attrs]


def on_checks(checks: List[Callable[[Any], bool]]) -> Callable[[Any], List[bool]]:
    """Get an object description function that runs a predefined set of checks (which should be in a
    fixed order) and returns their boolean results.

    Arguments:
        checks: Checks to perform.

    Returns:
        Object description function indicating check passings.
    """
    return lambda obj: [check(obj) for check in checks]


def on_hasweights(weights: List[str], threshold: float = 0.0) -> Callable[[Any], List[bool]]:
    """Check whether an objects has certain weights above a threshold in its weights dictionary
    property.

    Arguments:
        weights: Keys to the `obj.weights` dictionary to check.
        threshold: Threshold to verify against.

    Returns:
        Object description function indicating weights exceeding a threshold.
    """
    return lambda obj: [obj.weights.get(w, 0.0) >= threshold for w in weights]


def on_contains(contents: List[Any]) -> Callable[[Any], List[bool]]:
    """Check whether an object contains certain contents.

    Arguments:
        contents: Contents to check for with `lambda x: x in obj`.

    Returns:
        Object description function indicating content presence.
    """
    return lambda obj: [content in obj for content in contents]
