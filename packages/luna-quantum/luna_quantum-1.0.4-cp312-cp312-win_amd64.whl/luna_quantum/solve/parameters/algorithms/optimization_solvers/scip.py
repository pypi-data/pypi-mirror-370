from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.backends.zib import ZIB


class SCIP(LunaAlgorithm[ZIB]):
    """Parameters for the "Solve Constraint Integer Programming" (SCIP) solver."""

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
        return "SCIP"

    @classmethod
    def get_default_backend(cls) -> ZIB:
        """
        Return the default backend implementation.

        This property must be implemented by subclasses to provide
        the default backend instance to use when no specific backend
        is specified.

        Returns
        -------
            BACKEND_TYPE
                An instance of a class implementing the IBackend interface that serves
                as the default backend.
        """
        return ZIB()

    @classmethod
    def get_compatible_backends(cls) -> tuple[type[ZIB], ...]:
        """
        Check at runtime if the used backend is compatible with the solver.

        Returns
        -------
        tuple[type[IBackend], ...]
            True if the backend is compatible with the solver, False otherwise.

        """
        return (ZIB,)
