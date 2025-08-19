from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class MarketGraphClustering(UseCase):
    r"""
    # Market Graph Clustering.

    Description
    -----------

    The authors formulate the index-tracking problem as a QUBO graph-clustering problem.
    Their formulation restricts the number of assets while identifying the most
    representative exemplars of an index. Their thesis is that a portfolio consisting of
    the most representative set of exemplars will minimize tracking-error.
    Initial results are very encouraging. Their tests show they accurately replicate the
    returns of broad market indices, using only a small subset of their constituent
    assets. Moreover, their QUBO formulation allows us to take advantage of recent
    hardware advances to overcome the NP-hard nature of the clustering problem.
    Using these novel architectures they obtain better solutions within small fractions
    of the time required to solve equivalent problems formulated in traditional
    constrained form and solved on traditional hardware. Their initial results certainly
    offer hope and set the stage for larger-scale problems, in finance and beyond.

    Their implementation is based on the work of *Bauckhage et al.*.

    Q-Bit Interpretation
    --------------------

    "The qubit vector at index _k_ is 1 iff. stock _k_ from matrix _G_ (see below) is
    chosen as medoid of a cluster. The step of assigning the remaining stocks to
    clusters is not covered in this problem but can be easily done in linear time with
    respect to the number of data points."

    Links
    -----

    [Transformation (Market Graph Clustering via QUBO and Digital Annealing)](https://www.mdpi.com/1911-8074/14/1/34)

    [Bauckhage et al. (A QUBO Formulation of the k-Medoids Problem)](http://ceur-ws.org/Vol-2454/paper_39.pdf)

    Attributes
    ----------
    ### G: List[List[float]]
        \n An *n x m* matrix, where *n* is the number of stocks and *m* is the number of
        time units with returns for the respective stock at this time.

    ### k: int
        \n The number of representatives desired.

    ### gamma: float
        \n Penalty coefficient to enforce feasibility of the solution.
    """

    name: Literal["MGC"] = "MGC"
    G: list[list[float]]
    k: int
    gamma: float
