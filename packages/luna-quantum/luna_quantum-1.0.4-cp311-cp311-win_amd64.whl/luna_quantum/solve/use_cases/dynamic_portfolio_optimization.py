from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class DynamicPortfolioOptimization(UseCase):
    r"""
    # Dynamic Portfolio Optimization.

    Description
    -----------

    The Dynamic Portfolio Optimization problem tries to find the optimal portfolio for a
    given set of assets and a fixed investment amount. It aims to find the portfolio
    with optimal returns for a given risk tolerance. It considers transaction costs when
    rebalancing across multiple time steps. The optimal portfolio is defined by the
    binary choices whether to invest in a specific asset and how much to invest in it.
    The investment amount is split into several so called packages defined as
    2^(package number). The total number of packages determines the granularity of the
    result. It defines the amount of possible investment sums in one asset as well as
    the maximum possible investment in any one asset, which is
    2^(Number of packages) - 1.

    Links
    -----

    [Transformation](https://journals.aps.org/prresearch/pdf/10.1103/PhysRevResearch.4.013006)

    Attributes
    ----------
    ### tickers: List
        \n Tickers of assets being tested.
    ### mu: List[List[float]]
        \n Expected Returns of the assets.
        \n Shape: [time_steps][number_of_assets]
    ### sigma: List[List[List[float]]]
        \n Coviariance Matrix of the assets.
        \n Shape: [time_steps][number_of_assets][number_of_assets]
    ### packages: int
        \n Number of packages per asset, determines granularity of investment.
        \n _Package value = 2^(package number)_
    ### K: int
        \n Total investment amount, which is fixed.
    ### gamma: float
        \n Risk Aversion Coefficient.
        \n Range: Risk Seeking 0-100 Very Risk Averse.
        \n Divided by factor 2 as a convention, as stated in paper.
    ### nu: float
        \n Transaction Cost percentage, e.g., 0.01 = 1% of transaction size.
    ### rho: float
        \n Total investment size constraint factor, Lagrange Multiplier.
    """

    name: Literal["DPO"] = "DPO"
    tickers: list[str | int]
    mu: list[list[float]]
    sigma: list[list[list[float]]]
    packages: int
    K: int
    gamma: float
    nu: float
    rho: float
