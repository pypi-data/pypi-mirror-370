from typing import Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase
from luna_quantum.solve.use_cases.type_aliases import NestedDictIntGraph


class GraphIsomorphism(UseCase):
    r"""
    # Graph Isomorphism.

    Description
    -----------

    The Graph Isomorphism problem tries to find out whether two graphs _G1_ and _G2_are
    isomorphic, i.e. there exists a bijective, edge-invariant vertex mapping from _G1_
    to _G2_.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Graph_isomorphism)

    [Transformation](https://researchspace.auckland.ac.nz/bitstream/handle/2292/31756/CDMTCS499.pdf?sequence=1)

    Attributes
    ----------
    ### graph1: Dict[int, Dict[int, Dict[str, float]]]
        \n The first graph (in form of nested dictionaries) to check for isomorphism.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )

    ### graph2: Dict[int, Dict[int, Dict[str, float]]]
        \n The second graph (in form of nested dictionaries) to check for isomorphism.
        \n (e.g. fully connected graph with 3 nodes:
        \n _{0: {1: {}, 2: {}}, 1: {0: {}, 2: {}}, 2: {0: {}, 1: {}}}_
        \n or _networkx.to_dict_of_dicts(networkx.complete_graph(3))_ )

    ### a: float
        \n A penalty value enforcing the bijectivity of the isomorphism.

    ### b: float
        \n A penalty value (b > a) enforcing the edge-invariance of the isomorphism.
    """

    name: Literal["GI"] = "GI"
    graph1: NestedDictIntGraph = Field(name="graph")  # type: ignore[call-overload]
    graph2: NestedDictIntGraph = Field(name="graph")  # type: ignore[call-overload]
    a: float = 1
    b: float = 2
