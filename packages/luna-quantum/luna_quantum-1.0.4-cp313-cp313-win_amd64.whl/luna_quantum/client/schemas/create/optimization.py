from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from luna_quantum.solve.use_cases import UseCase

# This works but is kind of ugly.
# In the future, we should find another solution for "dumping" a child of UseCase
# with the name and params.
# OptimizationUseCaseIn can still be created like this:
# `opt = optimizationusecasein(name=name, use_case=use_case)`
# Somehow this tricks pydantic into accepting the child of UseCase and adding
# it to the model_dump_json. Without the Generic[UseCase] only the name will be
# added to the model_dump_json

_UseCase = TypeVar("_UseCase", bound=UseCase)


class OptimizationUseCaseIn(BaseModel, Generic[_UseCase]):
    """
    Input schema for creating an optimization use case.

    Attributes
    ----------
    name : str
        A name for the optimization use case.

    use_case : _UseCase
        The actual use case object containing the problem definition.

    params : dict[str, Any] | None
        Optional dictionary of additional parameters for the optimization.
    """

    name: str
    use_case: _UseCase
    params: dict[str, Any] | None
