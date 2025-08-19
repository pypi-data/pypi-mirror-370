from pydantic import Field

from luna_quantum.solve.domain.abstract.luna_algorithm import LunaAlgorithm
from luna_quantum.solve.interfaces.backend_i import IBackend
from luna_quantum.solve.parameters.backends.dwave import DWave


class FlexibleParameterAlgorithm(LunaAlgorithm[IBackend]):
    """Define an algorithm with flexible parameter.

    This class is used to represent algorithms with flexible parameters designed
    to work with a specific backend system. It also provides methods to interact
    with default and compatible backends.
    """

    luna_algorithm_name: str = Field(
        ..., exclude=True, repr=False, alias="algorithm_name"
    )

    @property
    def algorithm_name(self) -> str:
        """
        Get the name of the algorithm.

        Returns
        -------
        str
            The name of the algorithm used.
        """
        return self.luna_algorithm_name

    @classmethod
    def get_default_backend(cls) -> DWave:
        """
        Get the default backend for computations.

        The method returns a default instance of the DWave class, which can
        be used as a backend for computations.

        Returns
        -------
        DWave
            An instance of the DWave class.
        """
        return DWave()

    @classmethod
    def get_compatible_backends(cls) -> tuple[type[IBackend], ...]:
        """
        Get compatible backend classes.

        Return a tuple of backend types that are compatible with the current class.

        Returns
        -------
        tuple of type[IBackend, ...]
            Tuple containing classes of compatible backends.
        """
        return (IBackend,)
