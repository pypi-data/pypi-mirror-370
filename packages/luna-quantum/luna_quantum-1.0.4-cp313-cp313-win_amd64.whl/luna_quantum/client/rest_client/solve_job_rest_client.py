from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import BaseModel

from luna_quantum._core import Solution
from luna_quantum.client.interfaces.clients.solve_job_rest_client_i import (
    ISolveJobRestClient,
)
from luna_quantum.client.schemas import TokenProvider
from luna_quantum.client.schemas.create.solve_job_create import SolveJobCreate
from luna_quantum.client.schemas.enums.timeframe import TimeframeEnum
from luna_quantum.client.schemas.qpu_token.token_provider import RestAPITokenProvider
from luna_quantum.client.schemas.solution import (
    UseCaseRepresentation,
    UseCaseResult,
)
from luna_quantum.client.schemas.solve_job import SolveJobSchema
from luna_quantum.client.utils.qpu_token_utils import QpuTokenUtils
from luna_quantum.util.log_utils import Logging

if TYPE_CHECKING:
    from logging import Logger


class SolveJobRestClient(ISolveJobRestClient):
    """Impelentation of a solve job REST client."""

    logger: ClassVar[Logger] = Logging.get_logger(__name__)

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
        response = self._client.get(f"{self._endpoint}/data/{solve_job_id}", **kwargs)

        response.raise_for_status()

        return Solution.deserialize(response.content)

    def cancel(self, solve_job_id: str, **kwargs: Any) -> SolveJobSchema:
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
        response = self._client.post(
            f"{self._endpoint}/metadata/{solve_job_id}/cancel", **kwargs
        )

        response.raise_for_status()

        return SolveJobSchema.model_validate(response.json())

    @property
    def _endpoint(self) -> str:
        return "/solve-jobs"

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
        response = self._client.get(
            f"{self._endpoint}/metadata/{solve_job_id}", **kwargs
        )

        response.raise_for_status()

        return SolveJobSchema.model_validate(response.json())

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
        params = {}
        if timeframe and timeframe != TimeframeEnum.all_time:  # no value == all_time
            params["timeframe"] = timeframe.value

        limit = max(limit, 1)

        if model_id is not None:
            params["model_id"] = str(model_id)

        params["limit"] = str(limit)
        params["offset"] = str(offset)
        response = self._client.get(
            f"{self._endpoint}/metadata", params=params, **kwargs
        )

        response.raise_for_status()

        return [SolveJobSchema.model_validate(i) for i in response.json()]

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
        self._client.delete(f"{self._endpoint}/{solve_job_id}", **kwargs)

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
        if qpu_tokens is not None:
            rest_qpu_tokens = RestAPITokenProvider.from_sdk_token_provider(
                TokenProvider.model_validate(qpu_tokens)
            )
        else:
            rest_qpu_tokens = None
        # try to retrieve qpu tokens from env variables

        if rest_qpu_tokens is None:
            qpu_tokens = QpuTokenUtils.patch_qpu_tokens_from_env()
            if qpu_tokens is not None:
                rest_qpu_tokens = RestAPITokenProvider.from_sdk_token_provider(
                    qpu_tokens
                )
        params: dict[str, Any]

        if isinstance(solver_parameters, BaseModel):
            params = solver_parameters.model_dump()
        elif isinstance(solver_parameters, dict):
            params = solver_parameters
        else:
            params = {}

        solve_job_create = SolveJobCreate(
            model_id=model_id,
            solver_name=solver_name,
            provider=provider,
            parameters=params,
            qpu_tokens=rest_qpu_tokens,
            name=name,
        )
        SolveJobRestClient.logger.info(
            solve_job_create.model_dump_json(exclude={"qpu_tokens"})
        )
        response = self._client.post(
            self._endpoint, content=solve_job_create.model_dump_json(), **kwargs
        )
        response.raise_for_status()

        return SolveJobSchema.model_validate(response.json())

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
        response = self._client.get(
            f"{self._endpoint}/use-case/{solve_job_id}/representation", **kwargs
        )
        response.raise_for_status()
        return UseCaseRepresentation.model_validate(response.json())

    def get_best_use_case_result(
        self,
        use_case_representation: UseCaseRepresentation,  # noqa: ARG002
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
        return None
