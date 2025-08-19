from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class SetPacking(UseCase):
    r"""
    # Set Packing.

    Description
    -----------

    Given a set _S_ and a list of subsets of _S_, a packing is a family _C_ of these
    subsets so that all sets in _C_ are pairwise disjoint. For a set _S_ and a list of
    subsets of _S_, the Set Packing problem assigns a weight to each set and tries to
    find a packing so that the sum of the weights of the used sets is maximized.

    Note that, in contrast to the [transformation](https://arxiv.org/pdf/1811.11538.pdf)
    mentioned below, our QUBO formulation searches for _min x^t Q x_ instead of
    _max x^t Q x_ and thus all signs are flipped.

    Q-Bit Interpretation
    --------------------

    Subset _i_ is part of the packing iff. qubit _i_ is 1.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Set_packing)

    [Transformation](https://arxiv.org/pdf/1811.11538.pdf)

    Attributes
    ----------
    ### subset_matrix: List[List[int]]
        \n A matrix containing all subsets.
        \n e.g. for the set _{1, 2, 3}_ and the subsets _{1, 2}_, _{2, 3}_, and _{3}_:
        \n _[[1, 1, 0], [0, 1, 1], [0, 0, 1]]_

    ### weights: List[int]
        \n An array of length n_subsets which assigns a weight to each subset.

    ### P: int
        \n Positive, scalar penalty value to penalize subsets that are not disjoint.
        \n Default: _6_
    """

    name: Literal["SP"] = "SP"
    subset_matrix: list[list[int]]
    weights: list[float]
    P: int = 6
