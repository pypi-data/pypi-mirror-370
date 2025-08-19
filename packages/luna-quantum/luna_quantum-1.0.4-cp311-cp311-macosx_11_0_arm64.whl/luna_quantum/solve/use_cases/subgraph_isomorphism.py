from typing import Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase
from luna_quantum.solve.use_cases.type_aliases import NestedDictIntGraph


class SubGraphIsomorphism(UseCase):
    r"""
    # Subgraph Isomorphism.

    Description
    -----------

    The Subgraph Isomorphism problem tries to find out whether, for two graphs _G1_ and
    _G2_, _G2_ contains a subgraph _G3_ that is isomorphic to _G1_, i.e. there exists a
    bijective, edge-invariant vertex mapping from _G1_ to _G3_. It returns the best such
    mapping it is able to find.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Subgraph_isomorphism_problem)

    [Transformation](https://researchspace.auckland.ac.nz/bitstream/handle/2292/31756/CDMTCS499.pdf?sequence=1)

    Attributes
    ----------
    ### graph1: Dict[int, Dict[int, Dict[str, float]]]
        \n The graph (in form of nested dictionaries) for which to check whether it is
        isomorphic to a subgraph of graph2.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )

    ### graph2: Dict[int, Dict[int, Dict[str, float]]]
        \n The graph (in form of nested dictionaries) for which to check whether it
        contains a subgraph that is isomorphic to graph1.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )

    ### a: float = 1
        \n A penalty value enforcing the bijectivity of the isomorphism.

    ### b: float = 2
        \n A penalty value (b > a) enforcing the edge-invariance of the isomorphism.
    """

    name: Literal["SGI"] = "SGI"
    graph1: NestedDictIntGraph = Field(name="graph")  # type: ignore[call-overload]
    graph2: NestedDictIntGraph = Field(name="graph")  # type: ignore[call-overload]
    a: float = 1
    b: float = 2
