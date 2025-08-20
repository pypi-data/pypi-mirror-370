"""# Binary Decision Diagram compatibility calculation

Binary Decision Diagram (BDD) implementation of the compatibility problem.
"""

from typing import Generator, List, Tuple, Union

import dd.autoref as _bdd
import numpy as np


def _yield_ranges(nums: List[int], start: int = 0) -> Generator[range, None, None]:
    """Generate matrix index ranges."""
    for i in nums:
        yield range(start, start + i)
        start += i


def _recursive(operation: str, bdd: _bdd.BDD, items: List[_bdd.Function]) -> _bdd.Function:
    """Construct a recursive operation function over all items."""
    if len(items) == 1:
        return items[0]
    return bdd.apply(operation, items[0], _recursive(operation, bdd, items[1:]))


def yield_feasible_configurations(
    compat: Union["np.ndarray", List[List[Union[bool, int]]]],
    comp_variant_nums: List[int],
) -> Generator[Tuple[int, ...], None, None]:
    """Get the feasible configurations based on a compatibility matrix between different
    variants of elements and the "bucket" sizes (number of variants of each element).

    Arguments:
        compat: Compatibility matrix (square) between different variants of elements.
            Size is determined by the total number of variants.
        comp_variant_nums: The number of variants for each element. The matrix has to
            be sorted accordingly.

    Returns:
        Feasible configurations as a tuple with a variant's (absolute) index for
        each element.
    """
    bdd = _bdd.BDD()
    dim = len(compat)

    # All constraints that should be met.
    constraints = []

    # Variant toggles
    toggles = [bdd.add_var(i) for i in range(dim)]

    # Variant incompatibilities
    for i in range(dim):
        row = bdd.var(i)
        for j in range(i + 1, dim):
            if compat[i][j]:
                continue
            col = bdd.var(j)
            constraints.append(bdd.apply("=>", row, ~col))

    # Element picking constraints.
    ranges = _yield_ranges(comp_variant_nums)
    for rng in ranges:
        if rng.stop - rng.start == 1:
            constraints.append(bdd.var(rng.start))
            continue
        # Adding this xor guarantees an uneven number is selected.
        constraints.append(_recursive("xor", bdd, [bdd.var(i) for i in rng]))
        # Adding the ands guarantees no duo is selected.
        ands = [
            bdd.apply("=>", bdd.var(i), ~bdd.var(j))
            for i in range(rng.start, rng.stop - 1)
            for j in range(i + 1, rng.stop)
        ]
        constraints.append(_recursive("and", bdd, ands))

    # Construct system and yield solutions.
    system = _recursive("and", bdd, constraints)
    for config in bdd.pick_iter(system, care_vars=toggles):
        yield tuple(k for k, v in config.items() if v)
