from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class SupportVectorMachine(UseCase):
    r"""
    # Support Vector Machine.

    Description
    -----------

    In machine learning, support vector machines are supervised learning models that
    perform linear classification in such a way that the seperating hyperplane is as far
    away from each data point as possible.

    Note that, in this implementation, the model always assumes the separating
    hyperplane to be unbiased, i.e. it goes through the origin.

    Q-Bit Interpretation
    --------------------

    For interpretation, the qubit vector has to be cut into N sublists of length K
    (specified below). The sum of each of the products of each of these sublists and the
    precision vector gives a lagrangian multiplier for each data point.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Support-vector_machine)

    [Transformation](https://doi.org/10.1038/s41598-021-89461-4)

    Attributes
    ----------
    ### X: List[List[float]]
        \n Training data set in form of a nested list.
        \n All inner lists have to be of the same length.
        \n (e.g. 3 data points with 2 features:
        \n _[[1.1, 4.23], [0.1, -2.4], [-2.3, 1.11]]_

    ### Y: List[int]
        \n Classification labels of the training data set.
        \n e.g. for 3 data points:
        \n _[-1, 1, 1]_

    ### K: int
        \n Length of the precision vector.
        \n As the problem outputs are supposed to be real values but the qubo only
        gives a binary vector, we need a precision vector, consisting of positive powers
        of 2, to simulate real values. This parameter determines the length of this
        vector.
        \n (e.g. for K = 5, the precision vector is _[0.25, 0.5, 1, 2, 4]_)
        \n This parameter also determines the size of the qubo matrix together with the
        number of data points _N_:
        \n _size = N * K_
    """

    name: Literal["SVM"] = "SVM"
    X: list[list[float]]
    Y: list[int]
    K: int = 5
