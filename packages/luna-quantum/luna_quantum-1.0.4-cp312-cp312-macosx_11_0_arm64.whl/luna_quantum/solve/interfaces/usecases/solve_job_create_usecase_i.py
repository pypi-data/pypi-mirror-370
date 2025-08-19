from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luna_quantum.aqm_overwrites.model import Model
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
    from luna_quantum.solve.domain.abstract import LunaAlgorithm
    from luna_quantum.solve.domain.solve_job import SolveJob
    from luna_quantum.solve.interfaces.algorithm_i import BACKEND_TYPE


class ISolveJobCreateUseCase(ABC):
    """
    Abstract base class for a Solve Job Create use case.

    Defines the abstract methods to initialize the use case with a client and
    handle the execution of the use case, which involves processing a model.

    Attributes
    ----------
    client : ILunaSolve
        Instance of the solving client.
    """

    @abstractmethod
    def __init__(self, client: ILunaSolve) -> None:
        pass

    @abstractmethod
    def __call__(
        self,
        model: Model | str,
        luna_solver: LunaAlgorithm[BACKEND_TYPE],
        backend: BACKEND_TYPE,
        name: str | None,
    ) -> SolveJob:
        """
        Abstract base class for objects that are callable and return a Model.

        Classes implementing this interface are designed to be called with a
        Model instance and return a Model.
        """
