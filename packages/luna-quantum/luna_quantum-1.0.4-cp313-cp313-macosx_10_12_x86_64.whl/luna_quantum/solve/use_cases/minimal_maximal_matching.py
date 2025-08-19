from __future__ import annotations

from typing import Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase


class MinimalMaximalMatching(UseCase):
    r"""
    # Minimal Maximal Matching.

    Description
    -----------

    For a graph _G = (V, E)_, the Minimal Maximal Matching problem tries to find a
    "coloring" _C ⊆ E_ with the following three constraints:
    \n 1. For each edge in _C_, the incident vertices shall be colored and the union of
    all these vertices shall be called _D_.
    \n 2. No two edges in _C_ share a vertex.
    \n 3. If _u, v ∈ D_, then _(uv) ∉ E_.\n

    Links
    -----

    [Description and Transformation](https://arxiv.org/pdf/1302.5843.pdf)

    Attributes
    ----------
    ### graph: Dict[int, Dict[int, Dict[str, float]]]
        \n Problem graph for the minimal maximal matching problem in form of nested
        dictionaries.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )

    ### A: int
        \n A positive constant enforcing that no vertex has two colored edges.

    ### B: int
        \n A constant to penalize when an edge is uncolored although it would not
        violate the coloring condition. For _d_ being the maximal degree in the graph,
        choose _A > (d - 2)B_.

    ### C: int
        \n A constant (C < B) to minimize the number of colored edges.
    """

    name: Literal["MMM"] = "MMM"
    graph: dict[str, dict[str, dict[str, float]]] = Field(name="graph")  # type: ignore[call-overload]
    A: int = 10
    B: int = 2
    C: int = 1
