from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase

if TYPE_CHECKING:
    from luna_quantum.solve.use_cases.type_aliases import NestedDictGraph


class MinimalSpanningTree(UseCase):
    r"""
    # Minimal Spanning Tree with maximal degree constraint.

    Description
    -----------

    The Minimal Spanning Tree problem tries to find a spanning tree over all nodes in a
    given input graph such that the cost of the covered edges (the sum of the weights
    inside the tree) is minimal. The addition maximal degree constraint, i.e. limiting
    the degree of the tree at each node to a maximum value, makes this problem NP-hard.

    Convention on depth index of vertex and edge:
    Zero index is vertex root and all the edges leaving from root, etc.
    That means there are N/2 possible depths for edges and N/2 + 1 possible depths for
    vertices.

    Q-Bit Interpretation
    --------------------

    Assume we have a graph with _m_ nodes, _n_ edges, a max degree of _k_, and the qubit
    vector _q_.
    Then, for _i = 0, ..., n-1_, _q[i] = 1_ iff. edge _i_ is included in the tree.
    Variables _n, ..., n + ⌈ m / 2 ⌉_ keep track of the depth of a node in the tree.
    Now, let _a := n + ⌈ m / 2 ⌉_. Variables _a, ..., a + 2 * n_ tell for each edge in
    the graph which vertex is closer to the root of the tree.
    Finally, with _b := a * 2 * n_, the variables
    _b, ..., b + m * ⌊ log2(maxDegree) + 1 ⌋_ count the degree of a node in the tree.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Degree-constrained_spanning_tree),
    [Without degree constraint](https://en.wikipedia.org/wiki/Minimum_spanning_tree)

    [Transformation](https://arxiv.org/abs/1302.5843)

    Attributes
    ----------
    ### graph: Dict[int, Dict[int, Dict[str, float]]
        \n Problem graph for the minimal spanning tree problem in form of nested
        dictionaries. Each vertex needs to be weighted.
        \n (e.g. Wikipedia example
        \n _{
            0: {1: {"weight": 1}, 3: {"weight": 4}, 4: {"weight": 3}},
            1: {3: {"weight": 4}, 4: {"weight": 2}},
            2: {4: {"weight": 4}, 5: {"weight": 5}},
            3: {4: {"weight": 4}},
            4: {5: {"weight": 7}}
        }_ )

    ### max_degree : int
        \n The maximum degree at one joint of the tree. (e.g. 2 is a special case of the
        travelling salesman problem).

    ### A : Optional[float] = None.
        \n The penalty factor for constraints. Can be left _None_ to be estimated from
        the problem graph via the papers suggestion.
        \n Default: _None_

    ### B : Optional[float] = 1.
        \n The optimization penalty factor.
        \n Deafult: _1_

    ### ba_ratio : Optional[float] = 0.1
        \n A factor that increases or decreases the ratio between constraint and
        model penalty factors in the automatic estimation. If constraints are
        violated, this ratio needs to be decreased as the _A_ penalty needs to be
        increased. _0.1_ is a good starting point.
        \n Default: _0.1_
    """

    name: Literal["MST"] = "MST"
    graph: NestedDictGraph = Field(name="graph")  # type: ignore[call-overload]
    max_degree: int
    A: float | None = None
    B: float | None = 1.0
    ba_ratio: float | None = 0.1
