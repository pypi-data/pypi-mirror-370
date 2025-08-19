from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class SetCover(UseCase):
    r"""
    # Set Cover.

    Description
    -----------

    Given a set _S_ and a list of subsets of _S_, so that each element of _S_ is
    contained in at least one of the subsets, the Set Cover problem tries to find the
    smallest possible  family _C_ of these subsets so that all elements of _S_ are
    contained in at least one subset of _C_.

    Q-Bit Interpretation
    --------------------

    Let _n_ be the number of elements of _S_ and let _N_ be the number of subsets of
    _S_. Then, the qubit vector _x_ will have length _N + N * n_. For _x[:N]_,
    _x[i] = 1_, iff. subset _i_ is contained in the set cover. For _x[N:]_, _x[i] = 1_,
    iff. the number of subsets which include element _a_ is _m > 0_ and
    _i = N + a * N + m_.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Set_cover_problem)

    [Transformation](https://arxiv.org/pdf/1302.5843.pdf)

    Attributes
    ----------
    ### subset_matrix: List[List[float]]
        \n A matrix containing all subsets.
        \n e.g. for the set _{1, 2, 3}_ and the subsets _{1, 2}_, _{2, 3}_, and _{3}_:
        \n _[[1, 1, 0], [0, 1, 1], [0, 0, 1]]_
        \n or:
        \n _SetCover.gen_subsets_matrix([1, 2, 3], [[1, 2], [2, 3], [3]])_

    ### A: int
        \n A positive constant enforcing that each element of _S_ is contained in at
        least one subset.

    ### B: int
        \n A constant (_0 < B < A) minimizing the number of subsets included.
    """

    name: Literal["SC"] = "SC"
    subset_matrix: list[list[int]]
    A: int = 4
    B: int = 2
