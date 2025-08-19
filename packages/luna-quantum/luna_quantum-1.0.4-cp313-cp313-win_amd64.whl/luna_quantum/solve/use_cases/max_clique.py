from __future__ import annotations

from typing import Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase


class MaxClique(UseCase):
    r"""
    # Maximum Clique.

    Description
    -----------

    The Maximum Clique problem describes the task of finding the largest sized clique in
    a given graph. A clique is a set of nodes in a graph, where every node has an edge
    to every other node in the clique. A k-clique denotes a clique with exactly k nodes.
    The maximum clique of a graph is the clique with the highest possible k value.

    There is a closely related problem, the decisional clique problem, which describes
    the challenge of determining whether a clique of at least size k exists in the given
    graph.

    Math
    ----

    ![Formula](https://www.matthiasknoll.net/storage/img/max_clique.svg)


    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Clique_problem#Finding_a_single_maximal_clique)

    [Transformation](https://arxiv.org/pdf/1801.08649.pdf)

    Attributes
    ----------
    ### graph: Dict[int, Dict[int, Dict[str, float]]]
        \n Problem graph for the maximum clique problem in form of nested dictionaries.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )

    ### hard_constraints: Dict
        \n Hard constraints that must be fulfilled by any valid instance. They are
        defined in _aqcore.transformator.specifications.graph_specifications_.

    ### soft_constraints: Optional[Dict]
        \n Desirable traits that instances should fulfill.

    ### check_soft_constraints: bool
        \n Defines whether soft constraints should also be fulfilled. Default is
        _False_.
    """

    name: Literal["MCQ"] = "MCQ"
    graph: dict[str, dict[str, dict[str, float]]] = Field(name="graph")  # type: ignore[call-overload]
