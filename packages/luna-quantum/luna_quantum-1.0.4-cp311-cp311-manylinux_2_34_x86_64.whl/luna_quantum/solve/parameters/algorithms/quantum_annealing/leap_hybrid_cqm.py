from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.backends import DWaveQpu


class LeapHybridCqm(LunaAlgorithm[DWaveQpu]):
    """
    Parameters for D-Wave's Leap Hybrid Constrained Quadratic Model (CQM) solver.

    The Leap Hybrid CQM solver extends hybrid quantum-classical optimization to handle
    constrained problems, allowing both linear and quadratic constraints alongside
    the quadratic objective function. This enables solving many practical optimization
    problems in their natural formulation without manual penalty conversion.

    The solver is suitable for mixed binary, integer, and continuous problems with
    thousands of variables and constraints.

    Attributes
    ----------
    time_limit: float | int | None
        Maximum running time in seconds. Longer limits generally yield better solutions
        but increase resource usage. Default is None, which uses the service's default
        time limit (typically problem-size dependent).
    spin_variables: list[str] | None
        Variables to represent as spins (-1/+1) rather than binary (0/1) values.
        Useful for problems naturally formulated in spin space. Default is None,
        which uses binary representation for all discrete variables.
    """

    time_limit: float | int | None = None
    spin_variables: list[str] | None = None

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
        return "LCQM"

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
