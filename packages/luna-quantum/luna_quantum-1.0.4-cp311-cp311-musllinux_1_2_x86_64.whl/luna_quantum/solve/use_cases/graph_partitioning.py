from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class GraphPartitioning(UseCase):
    r"""
    Graph Partitioning.

    Description
    -----------

    The Graph Partitioning problem tries to find two equal sized partitions for a given
    undirected graph with an even number of vertices, so that the number of edges
    connecting the two subsets is minimized.

    Links
    -----

    [Transformation](https://arxiv.org/abs/1302.5843)

    Attributes
    ----------
    ### graph : Dict[int, Dict[int, Dict[str, float]]]
        \n The graph, for which the partitions are to be foundin form of nested
        dictionaries.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )

    ### A : Optional[int]
        \n Penalty parameter A panalizes violation of the constraint that makes sure
        both partitions are of equal size. It can be left "None" to be estimated from
        the problem graph via the papers suggestion.

    ### B : Optional[int]
        \n Optimization penalty parameter B penalizes each edge connecting two nodes of
        different partitions. If not given it defaults to 1.
    """

    name: Literal["GP"] = "GP"
    graph: dict[str, dict[str, dict[str, float]]]
    A: int | None = None
    B: int | None = 1
