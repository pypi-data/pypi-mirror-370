from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class KnapsackIntegerWeights(UseCase):
    r"""
    # Knapsack with Integer Weights.

    Description
    -----------

    Given a knapsack that can only carry a weight _W_ and a set of objects, each object
    having a weight _w_ and a value _c_, the Knapsack with Integer Weights problem tries
    to find objects so that the sum of their values is maximized while, at the same
    time, the sum of their weights does not exceed the capacity of the knapsack.

    Links
    -----

    [Description and Transformation](https://arxiv.org/pdf/1302.5843.pdf)

    Attributes
    ----------
    ### w: List[int]
        \n The weight of each object.

    ### c: List[float]
        \n The value of each object.

    ### W: int
        \n The weight that the knapsack can carry.

    ### B: float
        \n A positive constant to reward putting an object into the knapsack.
        \n Default: _1_

    ### A: Optional[float]
        \n A positive penalty value, enforcing that the maximal weight will not be
        exceeded. If specified, the equation _A > B _max_(c)_ must hold. If not
        specified, will be computed automatically as _A = 1 + B _max_(c)_.

    ### linear_encoding: bool
        \n If false, the number of qubits will be highly reduced, using the log trick
        from section 2.4 of the paper linked above.
    """

    name: Literal["KIW"] = "KIW"
    w: list[int]
    c: list[float]
    W: int
    B: float = 1.0
    A: float | None = None
    linear_encoding: bool = False
