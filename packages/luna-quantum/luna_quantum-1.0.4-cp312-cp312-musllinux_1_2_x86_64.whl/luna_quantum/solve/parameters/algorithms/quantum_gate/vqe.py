import math
from typing import Any, Literal

from pydantic import Field

from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.algorithms.base_params.scipy_optimizer import (
    ScipyOptimizerParams,
)
from luna_quantum.solve.parameters.backends import IBM


class VQE(LunaAlgorithm[IBM]):
    """
    Parameters for the Variational Quantum Eigensolver (VQE) algorithm.

    VQE is a hybrid quantum-classical algorithm designed to find the ground state energy
    of a Hamiltonian by variationally optimizing a parameterized quantum circuit.
    It's widely used in quantum chemistry to compute molecular ground state energies
    and electronic structure properties.

    Attributes
    ----------
    ansatz : Literal["NLocal", "EfficientSU2", "RealAmplitudes", "PauliTwoDesign"]
        The variational form (parameterized circuit) to use. Default is "EfficientSU2",
        a hardware-efficient ansatz using SU(2) rotation gates that works well on NISQ
        devices due to its shallow depth and flexibility.
    ansatz_config : dict[str, Any]
        Configuration options for the selected ansatz, such as:

        - entanglement: Pattern of entangling gates ("linear", "full", etc.)
        - reps: Number of repetitions of the ansatz structure
        - rotation_blocks: Types of rotation gates to use

        Default is an empty dictionary, using the ansatz's default settings.
    shots : int | None
        Number of measurement samples per circuit execution. Higher values improve
        accuracy by reducing statistical noise at the cost of longer runtime.
        Default is 1024, which balances accuracy with execution time.
    optimizer : ScipyOptimizerParams | Dict
        Configuration for the classical optimization routine that updates the
        variational parameters. Default is a ScipyOptimizer instance with default
        settings. See ScipyOptimizer Params class or for details
        of contained parameters.
    initial_params_seed: int | None
        Seed for random number generator for intial params.
    initial_params_range: tuple[float, float]
        Range of initial parameter values.
    """

    ansatz: Literal["NLocal", "EfficientSU2", "RealAmplitudes", "PauliTwoDesign"] = (
        "EfficientSU2"
    )

    ansatz_config: dict[str, Any] = Field(default_factory=dict)
    shots: int | None = 1024  # Number of circuit executions

    optimizer: ScipyOptimizerParams = Field(
        default_factory=lambda: ScipyOptimizerParams()
    )

    initial_params_seed: int | None = None
    initial_params_range: tuple[float, float] = Field(default=(0, 2 * math.pi))

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
        return "VQE"

    @classmethod
    def get_default_backend(cls) -> IBM:
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
        return IBM()

    @classmethod
    def get_compatible_backends(cls) -> tuple[type[IBM]]:
        """
        Check at runtime if the used backend is compatible with the solver.

        Returns
        -------
        tuple[type[IBackend], ...]
            True if the backend is compatible with the solver, False otherwise.

        """
        return (IBM,)
