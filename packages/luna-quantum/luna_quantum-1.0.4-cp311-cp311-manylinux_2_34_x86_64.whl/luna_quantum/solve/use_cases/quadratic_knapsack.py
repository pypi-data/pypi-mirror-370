from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class QuadraticKnapsack(UseCase):
    r"""
    # Quadratic Knapsack.

    Description
    -----------

    Given an upper bound of budget and a set of potential projects, each having a
    certain cost, a certain value, and value interactions with the other projects, the
    Quadratic Knapsack problem selects the combination of projects with the highest
    total value, without exceeding the budget restraint.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Quadratic_knapsack_problem)

    [Transformation](https://arxiv.org/pdf/1811.11538.pdf)

    Attributes
    ----------
    ### projects: List[List[float]]
        \n A double nested list with entries _projects[i][j]_ corresponding to the value
        gain of choosing both projects i and j at the same time.

    ### costs: List[float]
        \n The individual costs of each project.

    ### budget: float
        \n Budget restraint (upper bound) on projects.

    ### P: int
        \n The weight of the penalty term.
        \n Default: _10_
    """

    name: Literal["QK"] = "QK"
    projects: list[list[float]]
    costs: list[float]
    budget: float
    P: float = 10
