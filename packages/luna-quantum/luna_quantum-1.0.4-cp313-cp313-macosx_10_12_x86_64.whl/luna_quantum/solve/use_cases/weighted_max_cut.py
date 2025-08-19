from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class WeightedMaxCut(UseCase):
    r"""
    # Weighted Maximum Cut.

    Description
    -----------

    The Weighted Maximum Cut problem tries to find a cut that maximizes the weight of
    intersecting edges in an undirected weighted graph.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Maximum_cut)

    [Transformation](https://arxiv.org/pdf/2009.05008.pdf)

    Attributes
    ----------
    ### graph: Dict[int, Dict[int, Dict[str, float]]]
        \n Problem graph for the weighted maximum cut problem in form of nested
        dictionaries.
        \n Every edge has to have an assigned weight.
        \n (e.g. fully connected graph with 3 nodes and edge weights:
        \n _{0: {1: {"weight": 1}, 2: {"weight": 1}}, 1: {0: {"weight": 1},
        2: {"weight": 1}}, 2: {0: {"weight": 1}, 1: {"weight": 1}}}_ )
    """

    name: Literal["WMC"] = "WMC"
    graph: dict[int, dict[int, dict[str, float]]]
