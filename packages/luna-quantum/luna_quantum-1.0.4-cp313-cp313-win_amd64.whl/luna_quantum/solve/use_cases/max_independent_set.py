from __future__ import annotations

from typing import Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase


class MaxIndependentSet(UseCase):
    r"""
    # Maximum Independent Set.

    Description
    -----------

    An independent set of a graph _G_ is a set of vertices of _G_, where every two
    vertices are not connected by an edge in _G_. The Maximum Independent Set problem
    tries to find the largest independent set of a graph.

    Links
    -----

    [Description and Transformation](https://arxiv.org/pdf/1801.08653.pdf)

    Attributes
    ----------
    ### graph: Dict[int, Dict[int, Dict[str, float]]]
        \n Problem graph for the maximum independent set problem in form of nested
        dictionaries.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )
    """

    name: Literal["MIS"] = "MIS"
    graph: dict[int, dict[int, dict[str, float]]] = Field(name="graph")  # type: ignore[call-overload]
