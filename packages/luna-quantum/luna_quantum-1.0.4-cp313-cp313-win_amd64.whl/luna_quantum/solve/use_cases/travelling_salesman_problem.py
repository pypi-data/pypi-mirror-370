from __future__ import annotations

from typing import Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase


class TravellingSalesmanProblem(UseCase):
    r"""
    # Travelling Salesman.

    Description
    -----------

    The Travelling Salesman problem, either for a directed or undirected graph, asks the
    following: given a graph, where the edges are labeled with the distances between the
    corresponding nodes, what is the shortest possible route that visits each node
    exactly once and returns to the origin node?

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Travelling_salesman_problem)

    [Transformation](https://arxiv.org/pdf/1302.5843.pdf)

    Attributes
    ----------
    graph: Dict[int, Dict[int, Dict[str, float]]]
        \n Problem graph for the travelling salesman problem in form of nested
        dictionaries.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )

    A: Optional[float]
        \n Positive penalty value which enforces that each node is visited exactly once.
        \n if _None_, will be calculated with the equation: _A = B * _max_weight_ + 1_
        \n Default: _None_

    B: Optional[float]
        \n Positive penalty value (_B * _max_weight_) < A_) which helps find the
        shortest route.
        \n Default: _1.0_
    """

    name: Literal["TSP"] = "TSP"
    graph: dict[str, dict[str, dict[str, float]]] = Field(name="graph")  # type: ignore[call-overload]
    directed: bool | None = False
    B: float | None = 1.0
    A: float | None = None
