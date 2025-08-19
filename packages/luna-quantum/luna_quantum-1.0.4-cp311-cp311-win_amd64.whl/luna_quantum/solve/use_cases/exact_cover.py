from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class ExactCover(UseCase):
    r"""
    # Exact Cover.

    Description
    -----------

    Given a set _S_ and a list of subsets of _S_, an exact cover is a family _C_ of
    these subsets so that all elements of _S_ are contained in exactly one subset of
    _C_. For a set _S_ and a list of subsets of _S_, the Exact Cover problem tries to
    find the smallest exact cover, i.e. the one that uses the least subsets.

    Q-Bit Interpretation
    --------------------

    Subset _i_ is part of the exact cover iff. qubit _i_ is 1.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Exact_cover)

    [Transformation](https://arxiv.org/pdf/1302.5843.pdf)

    Attributes
    ----------
    ### subset_matrix: List[List[float]]
        \n A matrix containing all subsets.
        \n e.g. for the set _{1, 2, 3}_ and the subsets _{1, 2}_, _{2, 3}_, and _{3}_:
        \n _[[1, 1, 0], [0, 1, 1], [0, 0, 1]]_
        \n or:
        \n _ExactCover.gen_subsets_matrix([1, 2, 3], [[1, 2], [2, 3], [3]])_

    ### A: int
        \n A constant enforcing the exact cover of the solution.

    ### B: int
        \n A constant (_A > nB_) helping find the smallest exact cover.
    """

    name: Literal["EC"] = "EC"
    subset_matrix: list[list[int]]
    A: int = 2
    B: int = 2
