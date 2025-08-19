from __future__ import annotations

from typing import Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase


class InducedSubGraphIsomorphism(UseCase):
    r"""
    # Induced Subgraph Isomorphism.

    Description
    -----------

    Given two graphs the induced subgraph isomorphism problem is to decide if there
    exists an edge invariant injective mapping from the vertices of the first graph to
    the second graph.
    The task is slightly different from the subgraph isomorphism problem, because here
    additional edges present between two vertices in the second graph to which the
    isomorphism maps, are prohibited.

    This Implementation is heavily based on the subgraph isomorphism problem
    implementation.
    It uses slack variables to counterbalance unnecessary penalties.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Induced_subgraph_isomorphism_problem)

    [Transformation](https://researchspace.auckland.ac.nz/bitstream/handle/2292/31756/CDMTCS499.pdf)

    Attributes
    ----------
    ### graph1: Dict[int, Dict[int, Dict[str, float]]]
        \n The first graph in form of nested dictionaries.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )

    ### graph2: Dict[int, Dict[int, Dict[str, float]]]
        \n The second graph, on which the first one is to be mapped, also in form of
        nested dictionaries.
    """

    name: Literal["ISGI"] = "ISGI"
    graph1: dict[str, dict[str, dict[str, float]]] = Field(name="graph")  # type: ignore[call-overload]
    graph2: dict[str, dict[str, dict[str, float]]] = Field(name="graph")  # type: ignore[call-overload]
