from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class PortfolioOptimizationInvestmentBandsTargetVolatility(UseCase):
    r"""
    # Portfolio Optimization with Investment Bands and Target Volatility.

    Description
    -----------

    The Portfolio Optimization problem tries to find the optimal portfolio of assets
    which achieves an equal or higher return than the target return with the lowest
    risk possible. The optimal portfolio is defined by the binary choices whether to
    invest in a specific asset or not.

    This special case of portfolio optimization handles to additional constraints. On
    the one hand, it tries to find optimal investment portfolios with a fixed
    volatility. On the other hand, it imposes investment bands in the computed
    portfolios, i.e. the investment for each asset is between a minimum and a maximum.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Portfolio_optimization)

    [Transformation](https://arxiv.org/pdf/2106.06735.pdf)

    Attributes
    ----------
    ### log_returns: List[float]
        \n Log return of each asset.

    ### sigma: List[List[float]]
        \n Risk matrix.

    ### investment_bands: List[Tuple[float, float]]
        \n Investment bands for each asset.

    ### target_volatility: float
        \n Target volatility of portfolio.

    ### max_budget: int
        \n Maximum budget.

    ### budget_weight: float
        \n Budget penalty factor.

    ### volatility_weight: float
        \n Volatility penalty factor.
    """

    name: Literal["POIBTV"] = "POIBTV"
    log_returns: list[float]
    sigma: list[list[float]]
    investment_bands: list[tuple[float, float]]
    target_volatility: float
    max_budget: int
    budget_weight: float = 5.0
    volatility_weight: float = 50.0
