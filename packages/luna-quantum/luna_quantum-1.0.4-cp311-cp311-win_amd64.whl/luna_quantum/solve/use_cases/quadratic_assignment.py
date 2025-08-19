from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class QuadraticAssignment(UseCase):
    r"""
    # Quadratic Assignment.

    Description
    -----------

    There are a set of _n_ facilities and a set of _n_ locations. For each pair of
    locations, a distance is specified and for each pair of facilities a weight or flow
    is specified. The Quadratic Assignment problem assigns all facilities to different
    locations with the goal of minimizing the sum of products of the distances and the
    corresponding flows.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Quadratic_assignment_problem)

    [Transformation](https://arxiv.org/pdf/1811.11538.pdf)

    Attributes
    ----------
    ### flow_matrix: List[List]
        \n A matrix denoting the flow (or weight) between the facilities.
        \n e.g. for two facilities with a flow of 3, the flow_matrix will be
        _[[0, 3], [3, 0]]_.

    ### distance_matrix: List[List]
        \n A matrix denoting the distance between the locations.
        \n e.g. for two places with a distance of 8, the flow_matrix will be
        _[[0, 8], [8, 0]]_.

    ### P: int
        \n Positive, scalar penalty value to penalize when a facility is mapped to two
        different locations or vice versa.
        \n Default: _200_
    """

    name: Literal["QA"] = "QA"
    flow_matrix: list[list[float]]
    distance_matrix: list[list[float]]
    P: int = 200
