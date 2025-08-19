from __future__ import annotations

from typing import Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase


class ArbitrageNodeBased(UseCase):
    r"""
    # Arbitrage Node Based.

    Description
    -----------

    In economics and finance, arbitrage is the practice of taking advantage of a
    difference in prices in two or more markets; striking a combination of matching
    deals to capitalize on the difference.
    The node based Arbitrage problem tries to find the best cycle in a directed and
    complete graph. In this graph, each node corresponds to an asset and each directed
    edge is weighted with the corresponding conversion rate.
    The problem creates a QUBO with the size
    _(n_nodes * cycle_length) x (n_nodes * cycle_length)_, which produces a solution
    vector where each binary position maps to to a node and its position in the cycle.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/Arbitrage)

    [Transformation](http://1qbit.com/files/white-papers/1QBit-White-Paper-%E2%80%93-Finding-Optimal-Arbitrage-Opportunities-Using-a-Quantum-Annealer.pdf)

    Attributes
    ----------
    ### graph: Dict[str, Dict[str, Dict[str, float]]]
        \n The input graph as described above in the form of nested dictionaries.
        \n Example for three different currencies:\n
        \n _{_
        \n     _0: {1: {'weight': 1.31904}, 2: {'weight': 6.72585}},_
        \n     _1: {0: {'weight': 0.75799}, 2: {'weight': 5.10327},_
        \n     _2: {0: {'weight': 0.14864}, 1: {'weight': 0.19586}}_
        \n _}_

    ### penalty: Optional[float] = None
        \n The penalty term for the QUBO matrix. Has to be greater than 0.

    ### K: Optional[int] = None
        \n The maximum length of the arbitrage cycle.
    """

    name: Literal["ANB"] = "ANB"
    graph: dict[str, dict[str, dict[str, float]]] = Field(name="graph")  # type: ignore[call-overload]
    penalty: float | None = None
    K: int | None = None
