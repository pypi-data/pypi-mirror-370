from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class LinearRegression(UseCase):
    r"""
    # Linear Regression.

    Description
    -----------

    In statistics, linear regression is a linear approach to modelling the relationship
    between a real-valued dependent variable and one or more real-valued independent
    variables.

    Q-Bit Interpretation
    --------------------

    For interpretation, the qubit vector has to be cut into (n_features + 1) sublists of
    length K (specified below). The sum of each of the product of each of these sublists
    and the precision vector gives an estimated feature weight.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Linear_regression)

    [Transformation](https://doi.org/10.1038/s41598-021-89461-4)

    Attributes
    ----------
    ### X: List[List[float]]
        \n Training data set in form of a nested list.
        \n All inner lists have to be of the same length.
        \n (e.g. 3 data points with 2 features:
        \n _[[1.1, 4.23], [0.1, -2.4], [-2.3, 1.11]]_ )

    ### Y: List[int]
        \n Regression labels of the training data set.
        \n (e.g. for 3 data points:
        \n _[1.2, -3.4, 2.41]_ )

    ### K: int
        \n Length of the precision vector.
        \n As the problem outputs are supposed to be real values but the qubo only gives
        a binary vector, we need a precision vector, consisting of powers of 2, to
        simulate real values. This parameter determines the length of this vector.
        \n (e.g. for K = 6, the precision vector is _[-2, -1, -0.5, 0.5, 1, 2]_)
        \n This parameter also determines the size of the qubo matrix together with the
        number of features _d_:
        \n _size = (d + 1) * K_
    """

    name: Literal["LR"] = "LR"
    X: list[list[float]]
    Y: list[float]
    K: int = 24
