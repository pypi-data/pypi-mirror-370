from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class PortfolioOptimization(UseCase):
    r"""
    # Portfolio Optimization.

    Description
    -----------

    The Portfolio Optimization problem tries to find the optimal portfolio of assets
    which achieves an equal or higher return than the target return with the lowest
    risk possible. The optimal portfolio is defined by the binary choices whether to
    invest in a specific asset or not.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Portfolio_optimization)

    [Transformation](https://arxiv.org/pdf/2012.01121.pdf)

    Attributes
    ----------
    ### returns: List[List[float]]
        \n Returns matrix which contains time-series of returns per asset i.

    ### R: float
        \n Target for overall return of portfolio.

    ### n: int
        \n Number of wanted assets in set.

    ### lambda0: int = 1
        \n Default lagrange multiplier.
    """

    name: Literal["PO"] = "PO"
    returns: list[list[float]]
    R: float
    n: int
    lambda0: int = 1
