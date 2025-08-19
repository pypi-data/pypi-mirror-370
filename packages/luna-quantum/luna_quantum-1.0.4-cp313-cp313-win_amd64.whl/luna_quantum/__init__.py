from luna_quantum._core import __luna_quantum_version__
from luna_quantum.aqm_overwrites.model import Model
from luna_quantum.client.controllers import LunaQ, LunaSolve
from luna_quantum.config import config
from luna_quantum.factories.luna_solve_client_factory import LunaSolveClientFactory
from luna_quantum.factories.usecase_factory import UseCaseFactory
from luna_quantum.solve import DefaultToken
from luna_quantum.solve.parameters import algorithms, backends, constants
from luna_quantum.solve.usecases import (
    ModelDeleteUseCase,
    ModelFetchMetadataUseCase,
    ModelGetSolutionUseCase,
    ModelGetSolveJobsUseCase,
    ModelLoadByIdUseCase,
    ModelLoadByMetadataUseCase,
    ModelLoadMetadataByHashUseCase,
    ModelSaveUseCase,
    SolveJobCancelUseCase,
    SolveJobCreateUseCase,
    SolveJobDeleteUseCase,
    SolveJobFetchUpdatesUseCase,
    SolveJobGetResultUseCase,
)
from luna_quantum.util.debug_info import debug_info
from luna_quantum.util.log_utils import Logging

from ._core import (
    Bounds,
    Comparator,
    Constant,
    Constraint,
    Constraints,
    Environment,
    Expression,
    ExpressionIterator,
    HigherOrder,
    Linear,
    Quadratic,
    Result,
    ResultIterator,
    ResultView,
    Sample,
    SampleIterator,
    Samples,
    SamplesIterator,
    Sense,
    Solution,
    Timer,
    Timing,
    Unbounded,
    Variable,
    Vtype,
    errors,
    transformations,
    translator,
    utils,
)
from .utils import quicksum

__version__ = __luna_quantum_version__
UseCaseFactory.set_model_fetch_class(ModelFetchMetadataUseCase)
UseCaseFactory.set_model_delete_class(ModelDeleteUseCase)
UseCaseFactory.set_model_get_solution_class(ModelGetSolutionUseCase)
UseCaseFactory.set_model_get_solve_job_class(ModelGetSolveJobsUseCase)
UseCaseFactory.set_model_load_by_id_class(ModelLoadByIdUseCase)
UseCaseFactory.set_model_load_by_hash_class(ModelLoadMetadataByHashUseCase)
UseCaseFactory.set_model_load_by_metadata_class(ModelLoadByMetadataUseCase)
UseCaseFactory.set_model_save_class(ModelSaveUseCase)
UseCaseFactory.set_solve_job_cancel_class(SolveJobCancelUseCase)
UseCaseFactory.set_solve_job_create_class(SolveJobCreateUseCase)
UseCaseFactory.set_solve_job_delete_class(SolveJobDeleteUseCase)
UseCaseFactory.set_solve_job_get_result_class(SolveJobGetResultUseCase)
UseCaseFactory.set_solve_job_fetch_updates_class(SolveJobFetchUpdatesUseCase)
LunaSolveClientFactory.set_client_class(client_class=LunaSolve)
__all__ = [
    "Bounds",
    "Comparator",
    "Constant",
    "Constraint",
    "Constraints",
    "DefaultToken",
    "Environment",
    "Expression",
    "ExpressionIterator",
    "HigherOrder",
    "Linear",
    "Logging",
    "LunaQ",
    "LunaSolve",
    "LunaSolveClientFactory",
    "Model",
    "Quadratic",
    "Result",
    "ResultIterator",
    "ResultView",
    "Sample",
    "SampleIterator",
    "Samples",
    "SamplesIterator",
    "Sense",
    "Solution",
    "Timer",
    "Timing",
    "Unbounded",
    "UseCaseFactory",
    "Variable",
    "Vtype",
    "__version__",
    "algorithms",
    "backends",
    "config",
    "constants",
    "debug_info",
    "errors",
    "quicksum",
    "transformations",
    "translator",
    "utils",
]
