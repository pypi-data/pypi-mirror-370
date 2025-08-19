from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from luna_quantum.util.pretty_base import PrettyBase

Numeric = float | int
Sample = dict[str, Numeric]


class Runtime(BaseModel):
    """
    Pydantic model for runtime of a solution.

    Attributes
    ----------
    total: float
        Total time of solution processing
    qpu: Optional[float]
        Total time of the quantum computing processes
    """

    total: float
    qpu: float | None
    # ...


class ConstraintResult(BaseModel):
    """
    Represents the evaluation result of a constraint in an optimization.

    Attributes
    ----------
    satisfied: bool
        Indicates whether the constraint is satisfied by the solution.
    extra: dict[str, Any] | None
        Additional information related to the constraint evaluation.
    """

    satisfied: bool
    extra: dict[str, Any] | None


class Result(PrettyBase):
    """
    A single result of a solution.

    Attributes
    ----------
    sample: List[List[bool]]
        Binary solutions vectors
    energies: List[float]
        Energy corresponding to binary solution vector
    solver: str
        Solver's name
    params: Dict
        Solver params
    runtime: Runtime
        Solution runtime information
    metadata: Optional[Dict]
        Solution's metadata
    """

    sample: Sample
    obj_value: float
    feasible: bool
    constraints: dict[str, ConstraintResult]


class UseCaseResult(BaseModel):
    """
    Represents the result of an optimization use case solution.

    This class stores the outcome of solving an optimization problem,
    containing both the solution representation and its objective value.

    Attributes
    ----------
    representation: Any
        The representation of the solution, which could be in various forms
        depending on the optimization problem.
    obj_value: float
        The objective function value achieved by this solution.
    """

    representation: Any
    obj_value: float | None


class UseCaseRepresentation(PrettyBase):
    """
    Representation of an optimization problem use case.

    Attributes
    ----------
    results: list[UseCaseResult]
        A collection of results obtained from solving this
        optimization use case.
    description: str
        A human-readable description of the optimization use case.
    """

    results: list[UseCaseResult]
    description: str
