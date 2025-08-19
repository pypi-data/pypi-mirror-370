from __future__ import annotations

from typing import Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase


class SensorPlacement(UseCase):
    r"""
    # Sensor Placement.

    Description
    -----------

    The Sensor Placement problem finds the optimal placement of pressure sensors on a
    water distribution network, which is modelled by a graph where the edges have
    weights assigned to them. A higher weight corresponds to a higher importance that a
    sensor is placed on one of the nodes of the edge. Placing a sensor at a given node
    has a cost attached to it. The total cost of placing the sensors should also be
    minimized. As a constraint, there is a predetermined number of sensors s, which
    should be placed on the network.

    Links
    -----

    [Transformation](https://arxiv.org/pdf/2108.04075.pdf)

    Attributes
    ----------
    ### graph: Dict[int, Dict[int, Dict[str, float]]]
        \n Problem graph for the sensor placement problem in form of nested
        dictionaries.
        \n (e.g. network with 3 nodes:
        \n _{0: {2: {'weight': 1.0}}, 1: {2: {'weight': 6.0}},
            2: {0: {'weight': 1.0}, 1: {'weight': 6.0}}}_
        \n or _networkx.to_dict_of_dicts(networkx.Graph(...))_ )

    ### costs: List[float]
        \n Cost of placing a sensor on specific node.

    ### s: int
        \n Number of sensors.

    ### A: float
        \n Lagrange multiplier in front of constraint in eq. (15).

    ### B: float
        \n Lagrange multiplier in front of constraint in eq. (13).
    """

    name: Literal["SPL"] = "SPL"
    graph: dict[str, dict[str, dict[str, float]]] = Field(name="graph")  # type: ignore[call-overload]
    costs: list[float]
    s: int
    A: float = 1
    B: float = 30
