from __future__ import annotations

from typing import Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase


class MaxCut(UseCase):
    r"""
    # Maximum Cut.

    Description
    -----------

    The Maximum Cut problem tries to find a cut that maximizes the number of
    intersecting edges in an undirected graph.

    Q-Bit Interpretation
    --------------------
    A cut defines two sets of nodes, 0 and 1.
    The qubits x = (x_0, x_1, ..., x_n) can be interpreted like this:
    x_i = 0 iff. node i belongs to set 0 and x_i = 1 iff. it belongs to set 1.

    Math
    ----

    ![Formula](https://drive.google.com/uc?id=1D41KIt4S6gVkdOefWkwGDWLoIiTyexai)

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Maximum_cut)

    [Transformation](https://arxiv.org/pdf/1811.11538.pdf)

    Attributes
    ----------
    ### graph: Dict[int, Dict[int, Dict[str, float]]]
        \n Problem graph for the maximum cut problem in form of nested dictionaries.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )
    """

    name: Literal["MC"] = "MC"
    graph: dict[str, dict[str, dict[str, float]]] = Field(name="graph")  # type: ignore[call-overload]
