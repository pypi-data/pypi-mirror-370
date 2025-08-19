"""Provides the Max2SAT class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase

if TYPE_CHECKING:
    from luna_quantum.solve.use_cases.type_aliases import Clause


class Max2SAT(UseCase):
    r"""
    # Maximum 2-SAT.

    Description
    -----------

    For a formula in conjunctive normal form (CNF) with two literals per clause, the
    Maximum 2-SAT problem determines the maximum number of clauses that can be
    simultaneously satisfied by an assignment.

    Q-Bit Interpretation
    --------------------

    Each qubit corresponds to the truth value of one of the variables, to be precise:
    _sorted(variables)[i] == True_ iff. _qubits[i] == 1_.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/2-satisfiability#Maximum-2-satisfiability)

    [Transformation](https://arxiv.org/pdf/1811.11538.pdf)

    Attributes
    ----------
    ### clauses: List[Tuple[Tuple[int, bool], Tuple[int, bool]]]
        \n A list containing all clauses of the formula in CNF in form of tuples.
        \n (e.g. the formula _x0 * x1 + -x1 * x2_:
        \n _[((0, True), (1, True)), ((1, False), (2, True))]_ )
        \n It is possible to use arbitrary variable indices.

    ### n_vars: Optional[int]
        \n The number of different variables. Can be used to check whether the input
        clauses have the desired number of different variables.
    """

    name: Literal["M2SAT"] = "M2SAT"
    clauses: list[Clause] = Field(name="clauses")  # type: ignore[call-overload]
    n_vars: int | None = None
