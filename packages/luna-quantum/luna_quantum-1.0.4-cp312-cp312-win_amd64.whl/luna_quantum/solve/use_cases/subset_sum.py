from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class SubsetSum(UseCase):
    r"""
    # Subset Sum.

    Description
    -----------

    The Subset Sum problem finds a subset of numbers from a given set of integers where
    the total sum over the subset is equal or maximally close to a target value t.
    Example: Set _{5, 8, 4, 6}_ and Target _9_ returns the Subset _{5, 4}_

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Subset_sum_problem)

    [Transformation](https://arxiv.org/pdf/1911.08043.pdf) (section 3.2.3)

    Attributes
    ----------
    ### numbers: List[int]
        \n Set of integers from which the subset is chosen.

    ### t: int
        \n Target value for sum over all numbers in subset.
    """

    name: Literal["SS"] = "SS"
    numbers: list[int]
    t: int
