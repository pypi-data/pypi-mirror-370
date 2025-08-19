from __future__ import annotations

from typing import Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase


class MinimumVertexCover(UseCase):
    r"""
    # Minimum Vertex Cover.

    Description
    -----------

    A vertex cover of an undirected graph is a set of vertices that includes at least
    one endpoint of every edge of this graph. The Minimum Vertex Cover problem tries to
    find the smallest vertex cover in a given graph. The smallest vertex cover is the
    one that contains the least amount of nodes.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Vertex_cover)

    [Transformation](https://arxiv.org/pdf/1811.11538.pdf)

    Attributes
    ----------
    ### graph: Dict[int, Dict[int, Dict[str, float]]]
        \n Problem graph for the minimum vertex cover problem in form of nested
        dictionaries.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )

    ### P: int
        \n Positive, scalar penalty value to penalize edges that are not covered.
        \n Default: _8_
    """

    name: Literal["MVC"] = "MVC"
    graph: dict[str, dict[str, dict[str, float]]] = Field(name="graph")  # type: ignore[call-overload]
    P: int = 8
