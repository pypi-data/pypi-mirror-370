from __future__ import annotations

from typing import Literal

from luna_quantum.solve.use_cases.base import UseCase


class SatelliteScheduling(UseCase):
    r"""
    # Satellite Scheduling.

    Description
    -----------

    We assume a satellite can occupy three states: charging (*c*), downlink (*d*) and
    experiment (*e*). We discretize the time and assume time steps *t ∈ {0,1,...,T}*.
    The variable *x_st* tells us if the satellite is in the state *s ∈ {c,d,e}* at time
    *t*. With this, the time sequence of these variables represents the schedule we want
    to optimize. The optimization goal is to record as much data as possible during the
    mission. [1]

    There are two satellite variables which may change over time: The charge of the
    battery *C* and the data stored on the memory *D*. The rate with which these
    variables are changing depending on state *s* are denoted by *c_s* and *d_s*
    respectively. [1]

    For example the experiment state will increase the data *dd > 0* and decrease the
    charge *dc < 0*. Both the battery and the memory define an upper and lower limit
    for  the charge and the data, respectively. Not every state can be occupied at each
    instance in time. For example, the charging through solar panels is only possible
    in sunlight, or the downlink is only possible in the vicinity of a ground station.
    Therefore for each state s there is a subset of times `τ_s ⊆ {0,1,...,T}* at which
    the satellite can occupy this state. To enforce this constraint, we remove all
    variables *x_st ∈ {x_st |t ∈ τ_s}*. [1]

    For the sake of simplicity, we assume that each state has minimum duration of *1*.

    Links
    -----

    [Transformation (Experiences with Scheduling Problems on Adiabatic Quantum Computers)](https://elib.dlr.de/110044/1/43.pdf)

    Attributes
    ----------
    ### T: int
        \n T is the latest included time step. Note that the earliest included time step
        is always *0*.

    ### P: Tuple[int, int, int, int, int, int]
        \n The penalties for each constraint.

    ### Tau: List[List[int]]
        \n Times to be removed for each state.

    ### d: Dict
        \n Dict describing downlink state which includes entries *rate*, *initial*,
        *max*, *min*.

    ### c: Dict
        \n Dict describing charging state which includes entries *rate*, *initial*,
        *max*, *min*.

    ### S: int
        \n *S* is the total number of possible states.
    """

    name: Literal["SSC"] = "SSC"
    T: int
    P: tuple[int, int, int, int, int, int]
    Tau: list[list[int]]
    d: dict[str, float]
    c: dict[str, float]
    S: int = 3
