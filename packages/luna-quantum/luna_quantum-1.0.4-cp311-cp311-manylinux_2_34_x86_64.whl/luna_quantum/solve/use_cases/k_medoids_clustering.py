from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class KMedoidsClustering(UseCase):
    r"""
    # K-Medoids Clustering.

    Description
    -----------

    The authors are concerned with k-medoids clustering and propose a quadratic
    unconstrained binary optimization (*QUBO*) formulation of the problem of
    identifying *k* medoids among *n* data points without having to cluster the data.
    Given our *QUBO* formulation of this NP-hard problem, it should be possible to solve
    it on adiabatic quantum computers.

    Q-Bit Interpretation
    --------------------

    "The qubit vector at index _k_ is 1 iff. data point _k_ from the distance matrix is
    chosen as medoid of a cluster. The step of assigning the remaining data points to
    clusters is not covered in this problem but can be easily done in linear time with
    respect to the number of data points."

    Links
    -----

    [Transformation](http://ceur-ws.org/Vol-2454/paper_39.pdf)

    Attributes
    ----------
    D : List[List[float]]
        \n The (*n x n*) similarity matrix (diagonal elements are *1* (*one*)).

    k : int
        \n The number of medoids.

    gamma :  float
        \n Penalty coefficient to enforce feasibility.
    """

    name: Literal["KMC"] = "KMC"
    D: list[list[float]]
    k: int
    gamma: float
