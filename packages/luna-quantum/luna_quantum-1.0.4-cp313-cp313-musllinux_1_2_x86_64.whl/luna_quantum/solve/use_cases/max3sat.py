from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import Field

from luna_quantum.solve.use_cases.base import UseCase

if TYPE_CHECKING:
    from luna_quantum.solve.use_cases.type_aliases import Clause


class Max3SAT(UseCase):
    r"""
    # Maximum 3-SAT.

    Description
    -----------

    For a formula in conjunctive normal form (CNF) with three literals per clause, the
    Maximum 3-SAT problem determines the maximum number of clauses that can be
    simultaneously satisfied by an assignment.

    Q-Bit Interpretation
    --------------------

    Let _n_ be the number of different variables and let _m_ be the number of clauses.
    Then, each of the first _n_ qubits corresponds to the truth value of one of the
    variables, to be precise: _sorted(variables)[i] == True_ iff. _qubits[i] == 1_. Each
    of the last _m_ qubits tells whether the corresponding clause is fulfilled,
    formally: _clauses[i]_ is fulfilled iff. _qubits[n + i] == 1_.

    Links
    -----

    [Wikipedia](https://en.wikipedia.org/wiki/MAX-3SAT)

    [Transformation](https://canvas.auckland.ac.nz/courses/14782/files/574983/download?verifier=1xqRikUjTEBwm8PnObD8YVmKdeEhZ9Ui8axW8HwP&wrap=1)

    Attributes
    ----------
    ### clauses: List[Tuple[Tuple[int, bool], Tuple[int, bool], Tuple[int, bool]]]
        \n A list containing all clauses of the formula in CNF in form of tuples.
        \n (e.g. the formula _x0 * x1 * -x2 + -x1 * x2 * x3_:
        \n _[((0, True), (1, True), (2, False)), ((1, False), (2, True), (3, True))]_ )
        \n It is possible to use arbitrary variable indices.

    ### n_vars: Optional[int]
        \n The number of different variables. Can be used to check whether the input
        clauses have the desired number of different variables.
    """

    name: Literal["M3SAT"] = "M3SAT"
    clauses: list[Clause] = Field(name="clauses")  # type: ignore[call-overload]
    n_vars: int | None = None
