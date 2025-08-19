from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase

if TYPE_CHECKING:
    from luna_quantum.solve.use_cases.type_aliases import NestedDictGraph


class LabeledMaxWeightedCommonSubgraph(UseCase):
    r"""
    # Labeled Maximum Weighted Common Subgraph.

    Description
    -----------

    The Labeled Maximum Weighted Common Subgraph (LMWCS) problem finds, given two graphs
    _G1_ and _G2_, the largest subgraph of _G1_ that is isomorphic to a subgraph of
    _G2_. A weight is associated with each possible mapping between a node in _G1_ and a
    node in _G2_ to model a difference in importance for different mappings between
    nodes in the first graph and the second graph. The vertex pairs with assigned value
    _1_ form the common subgraph. Besides the constraint on the mappings which follow
    from requiring bijectivity, one can also define user-defined constraints.

    Notes
    -----
    There is an error in definition of _C_ (bijectivity constraint): condition one
    should be: _((i == m)_ or _(j == n))_ and not _((i == j)_ and _(j == n))_.

    We need to map the binary vector elements _b_{i, j}_, where _i_ and _j_ describe a
    node in the graphs 1 and 2 respectively, to an entry in a
    _(graph1.order() * graph2.order())_ dimensional vector. Here, we say that the
    element _b_{i, j}_ is mapped to the _(i * graph2.order() + j)_th entry of the
    vector.

    Generally, we have to fulfill _a_{(i, j), (m, n)} > min(w_{i, j}, w_{m, n})_ with
    _w_ being the weights for the pairs _(i, j)_. Here, we choose _a > max(weights)_ as
    if _a_ fulfills this condition for all _a_{(i, j), (m, n)}_.

    Q-Bit Interpretation
    --------------------

    The tuple _(i, j)_ is part of the mapping iff. qubit _i * graph2.order() + j_ is 1.

    Links
    -----

    [Transformation](https://arxiv.org/pdf/1601.06693.pdf)

    Attributes
    ----------
    ### graph1: Dict[int, Dict[int, Dict[str, float]]]
        \n First problem graph for the lmwcs problem in form of nested dictionaries.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )

    ### graph2: Dict[int, Dict[int, Dict[str, float]]]
        \n Second problem graph for the lmwcs problem in form of nested dictionaries.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )

    ### weigths: List[float]
        \n Weights for all pairs _(i, j)_ in _graph1.nodes x graph2.nodes_.

    ### a: float
        \n Penalty for mapping violating bijectivity or user constraints.

    ### user_constraints: List[Tuple[Tuple[int, int], Tuple[int, int]]]
        \n User given constraints on the vertex mapping.
        \n _((i, j), (m, n))_ being part of the user constraints means that _(i, j)_ and
        _(m, n)_ must not be part of the mapping at the same time.
    """

    name: Literal["LMWCS"] = "LMWCS"
    graph1: NestedDictGraph = Field(name="graph")  # type: ignore[call-overload]
    graph2: NestedDictGraph = Field(name="graph")  # type: ignore[call-overload]
    weights: list[float]
    a: float
    user_constraints: list[tuple[tuple[int, int], tuple[int, int]]] | None = None
