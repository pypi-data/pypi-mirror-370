from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from luna_quantum.client.interfaces.clients.rest_client_i import IRestClient

if TYPE_CHECKING:
    from pydantic import BaseModel

    from luna_quantum import Solution
    from luna_quantum.client.schemas.enums.timeframe import TimeframeEnum
    from luna_quantum.client.schemas.qpu_token.qpu_token import TokenProvider
    from luna_quantum.client.schemas.solution import (
        UseCaseRepresentation,
        UseCaseResult,
    )
    from luna_quantum.client.schemas.solve_job import SolveJobSchema


class ISolveJobRestClient(IRestClient, ABC):
    """Interface for a solve job REST client."""

    @abstractmethod
    def get_all(
        self,
        timeframe: TimeframeEnum | None = None,
        limit: int = 50,
        offset: int = 0,
        model_id: str | None = None,
        **kwargs: Any,
    ) -> list[SolveJobSchema]:
        """
        Get list of available SolveJobs.

        Parameters
        ----------
        timeframe: Optional[TimeframeEnum]
            Only return SolveJobs created within a specified timeframe. Default None.
        limit:
            Limit the number of SolveJobs to be returned. Default value 10.
        offset:
            Offset the list of solve job by this amount. Default value 0.
        model_id: Optional[str]
            Show solve job for only this model id. Default None.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        List[SolveJobSchema]
            List of SolveJob instances.
        """

    @abstractmethod
    def get(self, solve_job_id: str, **kwargs: Any) -> SolveJobSchema:
        """
        Retrieve one SolveJob by id.

        Parameters
        ----------
        solve_job_id: str
            Id of the solve job that should be retrieved.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        SolveJobSchema
            Instance of SolveJob.
        """

    @abstractmethod
    def get_solution(self, solve_job_id: str, **kwargs: Any) -> Solution:
        """
        Retrieve one solution by id.

        Parameters
        ----------
        solve_job_id: str
            Id of the solve job for which a solution should be retrieved.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        Solution
            Solution instance
        """

    @abstractmethod
    def get_use_case_representation(
        self, solve_job_id: str, **kwargs: Any
    ) -> UseCaseRepresentation:
        """
        Get the use-case-specific representation of a solution.

        Parameters
        ----------
        solve_job_id: str
            Id of the solve job that should be retrieved.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        UseCaseRepresentation
            The use-case-specific representation
        """

    @abstractmethod
    def delete(self, solve_job_id: str, **kwargs: Any) -> None:
        """
        Delete one solution by id.

        Parameters
        ----------
        solve_job_id: str
            Id of the solve job that should be deleted.
        **kwargs
            Parameters to pass to `httpx.request`.
        """

    @abstractmethod
    def create(  # noqa: PLR0913
        self,
        model_id: str,
        solver_name: str,
        provider: str,
        qpu_tokens: TokenProvider | None = None,
        solver_parameters: dict[str, Any] | BaseModel | None = None,
        name: str | None = None,
        **kwargs: Any,
    ) -> SolveJobSchema:
        """
        Create a solution for a model.

        Parameters
        ----------
        model_id: str
            The id of the model for which solution should be created.
        solver_name: str
            The name of the solver to use.
        provider: str
            The name of the provider to use.
        qpu_tokens: Optional[TokenProvider]
            The tokens to be used for the QPU.
        solver_parameters: Optional[Union[Dict[str, Any], BaseModel]]
            Parameters to be passed to the solver.
        name: Optional[str]
            Default: None, The name of the solution to create.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        SolveJobSchema
            The created solve job, which can be used to retrieve the solution later.
        """

    @abstractmethod
    def get_best_use_case_result(
        self, use_case_representation: UseCaseRepresentation
    ) -> UseCaseResult | None:
        """
        Retrieve the best result from a solution's use case representation.

        Parameters
        ----------
        use_case_representation : UseCaseRepresentation
            A solution's use case representation.

        Returns
        -------
        Optional[UseCaseResult]
            The best result of the solution. If there are several best solve job with
            the same objective value, return only the first. If the solution results are
            not (yet) available or the solution sense is `None`, `None` is returned.
        """

    @abstractmethod
    def cancel(
        self,
        solve_job_id: str,
        **kwargs: Any,
    ) -> SolveJobSchema:
        """
        Cancel a solve job for an id.

        Parameters
        ----------
        solve_job_id: str
            The id of the solve job which should be canceled.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        SolveJobSchema
            The updated solve job, which can be used to retrieve the solution later.
        """
