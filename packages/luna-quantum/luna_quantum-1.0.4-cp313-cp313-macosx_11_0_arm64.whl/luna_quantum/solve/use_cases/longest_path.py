from __future__ import annotations

from typing import Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase


class LongestPath(UseCase):
    r"""
    # Longest Path.

    Description
    -----------

    The longest path problem is the problem of finding a simple path of maximum length
    from a given start node to a given terminal node in a given graph. A path is called
    simple if it does not have any repeated vertices.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Longest_path_problem)

    [Transformation](https://www.sciencedirect.com/science/article/abs/pii/S030439752100092X#!)

    Attributes
    ----------
    ### graph: Dict[int, Dict[int, Dict[str, float]]]
        \n Problem graph for the longest path problem in form of nested dictionaries.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )

    ### start_node:
        \n At which node to start.

    ### terminal_node:
        \n At which node to stop.

    ### steps:
        \n How many nodes to include in the path.
    """

    name: Literal["LP"] = "LP"
    graph: dict[str, dict[str, dict[str, float]]] = Field(name="graph")  # type: ignore[call-overload]
    start_node: str
    terminal_node: str
    steps: int
