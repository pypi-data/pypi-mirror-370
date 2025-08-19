from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class BinaryIntegerLinearProgramming(UseCase):
    r"""
    # Binary Integer Linear Programming.

    Description
    -----------

    For a binary decision vector _x_ and some vector _c_ of length _N_, the Binary
    Integer Linear Programming problem maximizes _c * x_, given the constraint _Sx = b_
    with _S_ being an _m x N_ matrix and _b_ a vector with _m_ components.

    Q-Bit Interpretation
    --------------------

    The vector of qubits is simply the decision vector _x_.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Integer_programming)

    [Transformation](https://arxiv.org/pdf/1302.5843.pdf)

    Attributes
    ----------
    ### S: List[List[int]]
        \n The _m x N_ matrix.

    ### b: List[int]
        \n Vector with _m_ components.

    ### c: List[int]
        \n Custom vector of length _N_.

    ### A: int
        \n A constant enforcing, if possible, that _Sx = b_.

    ### B: int
        \n A constant (_B << A_) helping maximize _c * x_.
    """

    name: Literal["BIP"] = "BIP"
    S: list[list[int]]
    b: list[int]
    c: list[int]
    A: int = 10
    B: int = 2
