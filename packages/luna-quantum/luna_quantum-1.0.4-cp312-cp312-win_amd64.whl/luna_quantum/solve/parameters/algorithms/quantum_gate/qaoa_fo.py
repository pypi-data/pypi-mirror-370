from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.backends import Qctrl


class QAOA_FO(LunaAlgorithm[Qctrl]):  # noqa: N801
    """
    Quantum Approximate Optimization Algorithm via Fire Opal (QAOA_FO).

    QAOA_FO is Q-CTRL's implementation of the Quantum Approximate Optimization Algorithm
    (QAOA) through their Fire Opal framework. It is a hybrid quantum-classical algorithm
    for solving combinatorial optimization problems with enhanced performance through
    Q-CTRL's error mitigation and control techniques. For more details, please refer
    to the `Fire Opal QAOA documentation <https://docs.q-ctrl.com/fire-opal/execute/run-algorithms/solve-optimization-problems/fire-opals-qaoa-solver>`_.

    The algorithm works by preparing a quantum state through alternating applications of
    problem-specific (cost) and mixing Hamiltonians, controlled by variational
    parameters that are optimized classically to maximize the probability of measuring
    the optimal solution.

    QAOA_FO leverages Q-CTRL's expertise in quantum control to improve circuit fidelity
    and optimization performance. It is particularly suited for problems that can be
    encoded as quadratic unconstrained binary optimization (QUBO) or Ising models,
    such as MaxCut, TSP, and portfolio optimization.
    """

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
        return "QAOA_FO"

    @classmethod
    def get_default_backend(cls) -> Qctrl:
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
        return Qctrl()

    @classmethod
    def get_compatible_backends(cls) -> tuple[type[Qctrl]]:
        """
        Check at runtime if the used backend is compatible with the solver.

        Returns
        -------
        tuple[type[IBackend], ...]
            True if the backend is compatible with the solver, False otherwise.

        """
        return (Qctrl,)
