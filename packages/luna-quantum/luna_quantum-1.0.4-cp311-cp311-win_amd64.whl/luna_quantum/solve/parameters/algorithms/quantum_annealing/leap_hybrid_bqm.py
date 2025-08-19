from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.backends import DWaveQpu


class LeapHybridBqm(LunaAlgorithm[DWaveQpu]):
    """
    D-Wave's Leap Hybrid Binary Quadratic Model (BQM) solver.

    Leap's hybrid BQM solver is a cloud-based service that combines quantum and
    classical resources to solve unconstrained binary optimization problems that are
    larger than what can fit directly on a quantum processor. It automatically handles
    decomposition, quantum processing, and solution reconstruction.

    The hybrid solver is particularly useful for problems with thousands of variables,
    offering better scaling than classical solvers for many problem types.

    Attributes
    ----------
    time_limit: float | int | None
        Maximum running time in seconds. Longer time limits generally produce better
        solutions but increase resource usage and cost. Default is None, which uses
        the service's default time limit (typically problem-size dependent).

    Note
    ------
    For a D-Wave backend, this will ignore the decompose parameters as the hybrid
    solver handles decomposition internally.
    """

    time_limit: float | int | None = None

    @property
    def algorithm_name(self) -> str:
        """
        Returns the name of the algorithm.

        This abstract property method is intended to be overridden by subclasses.
        It should provide the name of the algorithm being implemented.

        Returns
        -------
        str
            The name of the algorithm.
        """
        return "LBQM"

    @classmethod
    def get_default_backend(cls) -> DWaveQpu:
        """
        Return the default backend implementation.

        This property must be implemented by subclasses to provide
        the default backend instance to use when no specific backend
        is specified.

        Returns
        -------
            IBackend
                An instance of a class implementing the IBackend interface that serves
                as the default backend.
        """
        return DWaveQpu()

    @classmethod
    def get_compatible_backends(cls) -> tuple[type[DWaveQpu], ...]:
        """
        Check at runtime if the used backend is compatible with the solver.

        Returns
        -------
        tuple[type[IBackend], ...]
            True if the backend is compatible with the solver, False otherwise.

        """
        return (DWaveQpu,)
