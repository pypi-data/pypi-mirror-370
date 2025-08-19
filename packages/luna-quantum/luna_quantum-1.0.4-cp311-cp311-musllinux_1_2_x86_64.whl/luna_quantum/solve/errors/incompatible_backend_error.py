from luna_quantum.solve.errors.solve_base_error import SolveBaseError
from luna_quantum.solve.interfaces.algorithm_i import BACKEND_TYPE, IAlgorithm
from luna_quantum.solve.interfaces.backend_i import IBackend


class IncompatibleBackendError(SolveBaseError):
    """Exception raised if the backend is incompatible with the algorithm."""

    def __init__(
        self, backend: IBackend, algorithm: type[IAlgorithm[BACKEND_TYPE]]
    ) -> None:
        super().__init__(
            f"Backend {backend.__class__.__name__} is incompatible "
            f"with algorithm {algorithm.__name__}."
        )
