from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from luna_quantum.solve.domain.abstract.luna_algorithm import LunaAlgorithm
from luna_quantum.solve.errors.solve_base_error import SolveBaseError
from luna_quantum.solve.parameters.algorithms.base_params.qaoa_circuit_params import (
    BasicQAOAParams,
    LinearQAOAParams,
    RandomQAOAParams,
)
from luna_quantum.solve.parameters.algorithms.base_params.scipy_optimizer import (
    ScipyOptimizerParams,
)
from luna_quantum.solve.parameters.backends.aqarios import Aqarios

from .config import AdvancedConfig
from .optimizers import (
    CombinedOptimizerParams,
    InterpolateOptimizerParams,
    LinearOptimizerParams,
)
from .pipeline import PipelineParams


class QAOAParameterOptimizerError(SolveBaseError):
    """QAOA cirucit parameters mismatch with optimizer exception."""

    def __init__(
        self,
        optimizer: ScipyOptimizerParams
        | LinearOptimizerParams
        | CombinedOptimizerParams
        | InterpolateOptimizerParams
        | None,
        params: BasicQAOAParams | LinearQAOAParams | RandomQAOAParams,
        extra: str = "",
    ) -> None:
        super().__init__(
            f"Parameter Mismatch of {optimizer.__class__} and {params.__class__}"
            + ((". " + extra) if extra else "")
        )


class InterpolateOptimizerError(SolveBaseError):
    """Interpolate optimizer error when final number of reps is too small."""

    def __init__(self, reps_end: int, reps_start: int) -> None:
        super().__init__(f"{reps_end=} needs to be larger than {reps_start=}.")


class QAOAParameterDepthMismatchError(SolveBaseError):
    """QAOA circuit params mismatch the specified reps."""

    def __init__(self, params_reps: int, reps: int) -> None:
        super().__init__(f"{params_reps=} needs to match {reps=}.")


class FlexQAOA(LunaAlgorithm[Aqarios], BaseModel):
    """The FlexQAOA Algorithm for constrained quantum optimization.

    The FlexQAOA is an extension to the default QAOA with the capabilities to encode
    inequality constriants with indicator functions as well as one-hot constraints
    through XY-mixers. This algorithm will dynamically extract all constraints from the
    given constraint input optimization model, and construct an accoring QAOA circuit.
    Currently only simulation of the circuit is supported. But due to the constrained
    nature, the subspace of the Hilbertspace required for simulation is smaller,
    depending on the problem instance. This allows for simulation of problems with
    more qubits than ordinary state vector simulation allows. For now, the simulation
    size is limited to Hilbertspaces with less <= 2**18 dimensions.

    The FlexQAOA allows for a dynamic circuit construction depending on input paramters.
    Central to this is the pipeline parameter which allows for different configurations.

    For instance, if one likes to explore ordinary QUBO simulation with all constraints
    represented as quadratic penalties, the `one_hot` and `indicator_function` options
    need to be manually disabled
    ```
    pipeline = {"one_hot": None, "indicator_function": None}
    ```

    If no indicator function is employed, but the input problem contains inequality
    constraints, slack variables are added to the optimization problem. FlexQAOA allows
    for a configuration that discards slack variables as their assignment is not
    necessarily of interest. This option can be enbled by setting
    ```
    qaoa_config = {"discard_slack": True}
    ```

    Following the standard protocol for QAOA, a classical optimizer is required that
    tunes the variational parameters of the circuit. Besides the classical
    `ScipyOptimizer` other optimizers are also featured, allowing for optimizing only a
    linear schedule, starting with optimizing for a linear schedule followed by
    individual parameter fine tuning, and interpolating between different QAOA circuit
    depts.

    Attributes
    ----------
    shots: int
        Number of sampled shots.
    reps: int
        Number of QAOA layer repetitions
    pipeline: PipelineParams | Dict
        The pipeline defines the selected features for QAOA circuit generation. By
        default, all supported features are enabled (one-hot constraints, inequality
        constraints and quadratic penalties).
    optimizer: ScipyOptimizerParams | LinearOptimizerParams | CombinedOptimizerParams |\
        InterpolateOptimizerParams | None | Dict
        The classical optimizer for parameter tuning. Default: ScipyOptimizer. Setting
        to `None` disables the optimization, leading to an evaluation of the initial
        parameters.
    qaoa_config: AdvancedConfig | Dict
        Additional options for the QAOA circuit and evalutation
    initial_params: LinearQAOAParams | BasicQAOAParams | RandomQAOAParams | Dict
        Custom QAOA variational circuit parameters. By default linear
        increasing/decreasing parameters for the selected `reps` are generated.
    """

    shots: int = Field(default=1024, ge=1, description="Number of sampled shots.")
    reps: int = Field(default=1, ge=1, description="Number of QAOA layer repetitions")
    pipeline: PipelineParams = Field(
        default_factory=lambda: PipelineParams(),
        description="The pipeline defines the selected features for QAOA circuit "
        "generation. By default, all supported features are enabled "
        "(one-hot constraints, inequality constraints and quadratic penalties).",
    )
    optimizer: (
        ScipyOptimizerParams
        | LinearOptimizerParams
        | CombinedOptimizerParams
        | InterpolateOptimizerParams
        | None
    ) = Field(
        default_factory=lambda: ScipyOptimizerParams(),
        description="The classical optimizer. Default: ScipyOptimizer",
    )
    qaoa_config: AdvancedConfig = Field(
        default_factory=lambda: AdvancedConfig(),
        description="Additional options for the QAOA circuit and evalutation",
    )
    initial_params: LinearQAOAParams | BasicQAOAParams | RandomQAOAParams = Field(
        default_factory=lambda: LinearQAOAParams(delta_beta=0.5, delta_gamma=0.5),
        description="Custom QAOA circuit parameters. By default linear "
        "increasing/decreasing parameters for the selected `reps` are generated.",
    )

    @model_validator(mode="after")
    def _check_param_type(self) -> FlexQAOA:
        if isinstance(self.optimizer, LinearOptimizerParams) and isinstance(
            self.initial_params, BasicQAOAParams
        ):
            raise QAOAParameterOptimizerError(self.optimizer, self.initial_params)
        if isinstance(self.optimizer, CombinedOptimizerParams) and isinstance(
            self.initial_params, BasicQAOAParams
        ):
            raise QAOAParameterOptimizerError(self.optimizer, self.initial_params)
        if (
            isinstance(self.optimizer, InterpolateOptimizerParams)
            and isinstance(self.optimizer.optimizer, LinearOptimizerParams)
            and isinstance(self.initial_params, BasicQAOAParams)
        ):
            raise QAOAParameterOptimizerError(
                self.optimizer,
                self.initial_params,
                extra="LinearOptimizer used in InterpolateOptimizer.",
            )
        if (
            isinstance(self.optimizer, InterpolateOptimizerParams)
            and self.optimizer.reps_end < self.reps
        ):
            raise InterpolateOptimizerError(self.optimizer.reps_end, self.reps)
        return self

    @model_validator(mode="after")
    def _check_depth(self) -> FlexQAOA:
        if (
            isinstance(self.initial_params, BasicQAOAParams)
            and self.initial_params.reps != self.reps
        ):
            raise QAOAParameterDepthMismatchError(self.initial_params.reps, self.reps)
        return self

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
        return "FlexQAOA"

    @classmethod
    def get_default_backend(cls) -> Aqarios:
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
        return Aqarios()

    @classmethod
    def get_compatible_backends(cls) -> tuple[type[Aqarios]]:
        """
        Check at runtime if the used backend is compatible with the solver.

        Returns
        -------
        tuple[type[IBackend], ...]
            True if the backend is compatible with the solver, False otherwise.

        """
        return (Aqarios,)
