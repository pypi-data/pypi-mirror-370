from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class SetPartitioning(UseCase):
    r"""
    # Set Partitioning.

    Description
    -----------

    The Set Partitioning problem partitions a set of items into a selection of possible
    subsets so that each item of the set occurs in one and only one subset and the cost
    of the chosen subsets is minimized.

    Q-Bit Interpretation
    --------------------

    Subset _i_ is part of the partitioning iff. qubit _i_ is 1.

    Links
    -----

    [Description and Transformation](https://arxiv.org/pdf/1811.11538.pdf)

    Attributes
    ----------
    ### set_: List[int]
        \n The set of items which has to be partitioned.

    ### subsets: List[List[int]]
        \n The possible subsets of set_.
        \n e.g. for _set=[1, 2, 3]_ and the possible subsets _{1, 2}_ and _{3}_ one
        has to specify _subsets=[[1, 2], [3]]_.

    ### costs: List[int]
        \n The cost of each possible subset. Has to be of the same length as _subsets_.

    ### P: int
        \n Positive, scalar penalty value to penalize items that occur in more than one
        subset.
        \n Default: _10_
    """

    name: Literal["SPP"] = "SPP"
    set_: list[int]
    subsets: list[list[int]]
    costs: list[int]
    P: int = 10
