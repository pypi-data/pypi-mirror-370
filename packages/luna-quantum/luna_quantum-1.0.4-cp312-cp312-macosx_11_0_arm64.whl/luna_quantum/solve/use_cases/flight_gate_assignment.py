from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class FlightGateAssignment(UseCase):
    r"""
    # Flight Gate Assignment.

    Description
    -----------

    Flight Gate Assignment is a highly relevant optimization problem in airport
    management. It tries to minimize the total transit time of passengers, considering
    three typical parts of passenger flow in an airport:
    \n 1) After a flight, passengers claim their baggage and leave the airport.
    \n 2) Other passengers switch from one plane to another to get a connecting flight.
    \n 3) A third group of passengers pass the security check and leave with a flight.

    Links
    -----

    [Description and Transformation](https://arxiv.org/pdf/1811.09465.pdf)

    Attributes
    ----------
    ### n_flights: int
        \n Number of flights.

    ### n_gates: int
        \n Number of gates.

    ### n_passengers: List[Tuple[int, int]]
        \n Number of passengers arriving and departing with each flight.
        \n Example: _n_passengers[3][departure_index]_, gives us the number of
        passengers departing with flight _3_.

    ### time_gates: List[Tuple[float, float]]
        \n The time it takes between every gate and check-in (when leaving) or the gate
        and baggage claim (when arriving).
        \n Example: _time_gates[0][arriving_index]_, gives us the time it takes to go
        from gate _0_ to baggage claim.

    ### time_flights: List[Tuple[float, float]]
        \n The time at which a flight arrives/leaves.
        \n Example: _time_flights[2][departure_index]_, gives us the time at which
        flight 2 departs.

    ### transfer_passengers: List[List[int]]
        \n Matrix with the information of the passengers transferring from one flight to
        another.
        \n Example: _transfer_passengers[2][5]_, gives the number of passengers
        transferring from flight 2 to flight 5.

    ### time_between_gates: List[List[float]]
        \n Gives the time it takes to go from one gate to another.

    ### t_buf: float
        \n Time needed for a gate to be free after a flight has departed.

    ### arrival_index, departure_index: int
        \n Index to subscribe the variables _time_gates_, _n_passengers_,
        _time_gates_, _time_flights_.
        \n One of these variables needs to be _0_, the other _1_.
    """

    name: Literal["FGO"] = "FGO"
    n_flights: int
    n_gates: int
    n_passengers: list[tuple[int, int]]
    time_gates: list[tuple[float, float]]
    time_flights: list[tuple[float, float]]
    transfer_passengers: list[list[int]]
    time_between_gates: list[list[float]]
    t_buf: float
    arrival_index: int = 0
    departure_index: int = 1
