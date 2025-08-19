from pydantic import Field

from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.algorithms.base_params.qaoa_circuit_params import (
    BasicQAOAParams,
    LinearQAOAParams,
    RandomQAOAParams,
)
from luna_quantum.solve.parameters.algorithms.base_params.scipy_optimizer import (
    ScipyOptimizerParams,
)
from luna_quantum.solve.parameters.backends import AWS, IBM, IQM, IonQ, Rigetti


class QAOA(LunaAlgorithm[AWS | IonQ | IQM | Rigetti | IBM]):
    """
    Quantum Approximate Optimization Algorithm (QAOA).

    QAOA is a hybrid quantum-classical algorithm for solving combinatorial optimization
    problems. It works by preparing a quantum state through alternating applications of
    problem-specific (cost) and mixing Hamiltonians, controlled by variational
    parameters that are optimized classically to maximize the probability of measuring
    the optimal solution.

    QAOA is particularly suited for problems that can be encoded as quadratic
    unconstrained binary optimization (QUBO) or Ising models, such as MaxCut, TSP, and
    portfolio optimization.

    Attributes
    ----------
    reps : int
        Number of QAOA layers (p). Each layer consists of applying both the cost and
        mixing Hamiltonians with different variational parameters. Higher values
        generally lead to better solutions but increase circuit depth and quantum
        resources required. Default is 1.
    shots : int
        Number of measurement samples to collect per circuit execution. Higher values
        reduce statistical noise but increase runtime. Default is 1024.
    optimizer : ScipyOptimizerParams | Dict
        Configuration for the classical optimization routine that updates the
        variational parameters. Default is a ScipyOptimizer instance with default
        settings. See ScipyOptimizerParams class for details of contained parameters.
    initial_params: LinearQAOAParams | BasicQAOAParams | RandomQAOAParams | Dict
        Custom QAOA variational circuit parameters. By default linear
        increasing/decreasing parameters for the selected `reps` are generated.
    """

    reps: int = Field(default=1, ge=1)
    shots: int = Field(default=1024, ge=1)
    optimizer: ScipyOptimizerParams = Field(
        default_factory=lambda: ScipyOptimizerParams()
    )
    initial_params: RandomQAOAParams | BasicQAOAParams | LinearQAOAParams = Field(
        default_factory=lambda: LinearQAOAParams(delta_beta=0.5, delta_gamma=0.5)
    )

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
        return "QAOA"

    @classmethod
    def get_default_backend(cls) -> AWS | IonQ | IQM | Rigetti | IBM:
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
    def get_compatible_backends(
        cls,
    ) -> tuple[type[AWS | IonQ | IQM | Rigetti | IBM], ...]:
        """
        Check at runtime if the used backend is compatible with the solver.

        Returns
        -------
        tuple[type[IBackend], ...]
            True if the backend is compatible with the solver, False otherwise.

        """
        return AWS, IonQ, IQM, Rigetti, IBM
