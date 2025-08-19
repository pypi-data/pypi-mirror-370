from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class CreditScoringFeatureSelection(UseCase):
    r"""
    # Feature Selection for Credit Scoring.

    Description
    -----------

    Find the optimal feature subset with regard to independence and influence of
    features for credit scoring of credit applicants.

    Links
    -----

    [Transformation](https://1qbit.com/files/white-papers/1QBit-White-Paper-%E2%80%93-Optimal-Feature-Selection-in-Credit-Scoring-and-Classification-Using-a-Quantum-Annealer_-_2017.04.13.pdf)

    Attributes
    ----------
    ### U: List[List[float]]
        \n The matrix U is the design matrix, where each column represents a feature
        and each row represents the specific values for a feature set.

    ### V: List[int]
        \n The binary label vector for the respective row in matrix U.

    ### alpha: float
        \n The balance between feature influence and feature independence in the range
        _[0, 1]_.
    """

    name: Literal["CSFS"] = "CSFS"
    U: list[list[float]]
    V: list[int]
    alpha: float
