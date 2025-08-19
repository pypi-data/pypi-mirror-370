from __future__ import annotations

from typing import Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase


class HamiltonianCycle(UseCase):
    r"""
    # Hamiltonian Cycle.

    Description
    -----------

    The Hamiltonian Cycle problem, either for a directed or undirected graph, asks the
    following: starting at an arbitrary node in the graph, can one travel along the
    edges of the graph so that each graph will be visited exactly once and there is an
    edge between the starting node and the last node?

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Hamiltonian_path_problem)

    [Transformation](https://arxiv.org/pdf/1302.5843.pdf)

    Attributes
    ----------
    ### graph: Dict[int, Dict[int, Dict[str, float]]]
        \n Problem graph for the hamiltonian cycle problem in form of nested
        dictionaries.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )

    ### A: Optional[float]
        \n Positive penalty value which enforces that each node is visited exactly once.
        \n Default: _1.0_
    """

    # Hamiltonian Cycle is just TSP with B = 0.

    name: Literal["HC"] = "HC"
    graph: dict[str, dict[str, dict[str, float]]] = Field(name="graph")  # type: ignore[call-overload]
    directed: bool | None = False
    A: float = 1.0
    B: float = 0.0
