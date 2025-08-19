from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class TrafficFlow(UseCase):
    r"""
    # Traffic Flow Optimization.

    Description
    -----------

    The Traffic Flow Optimization problem tries to minimize the total time for a given
    set of cars to travel between their individual sources and destinations. This is
    achieved by minimizing the number of overlapping segments between assigned routes
    for each car.

    Links
    -----

    [Description and Transformation](https://www.frontiersin.org/articles/10.3389/fict.2017.00029/full)

    Attributes
    ----------
    ### car_routes: List[List[List[int]]]
        \n The route segments of each possible route for each car.
        \n (e.g. for two cars, where car 1 can take either route 0, 1, 2 or route 0, 3,
        4 and car 2 can take either route 3, 0, 5 or route 6, 7, 5:
        \n _[[[0, 1, 2], [0, 3, 4]], [[3, 0, 5], [6, 7, 5]]]_
    """

    name: Literal["TFO"] = "TFO"
    car_routes: list[list[list[int]]]
