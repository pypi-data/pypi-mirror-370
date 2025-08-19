from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class BinaryPaintShopProblem(UseCase):
    r"""
    # Binary Paint Shop.

    Description
    -----------

    The Binary Paint Shop Problem tries to minimize the color change of a paint job with
    two colors of a sequence of cars. The sequence consists of a fixed number of cars,
    in which each car type occurs exactly twice and these are to be colored in different
    colors. Therefore, the car sequence consists of exactly twice as many cars as there
    are car types.

    Links
    -----

    [Transformation](https://arxiv.org/pdf/2011.03403.pdf)

    Attributes
    ----------
    ### n_cars: int
        \n Amount of different car types.

    ### sequence: List[int]
        \n Sequence of the cars.
    """

    name: Literal["BPSP"] = "BPSP"
    n_cars: int
    sequence: list[int]
