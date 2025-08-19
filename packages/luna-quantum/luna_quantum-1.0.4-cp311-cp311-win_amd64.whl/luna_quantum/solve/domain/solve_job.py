from logging import Logger
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, PrivateAttr

from luna_quantum._core import Solution
from luna_quantum.aqm_overwrites.model import Model
from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.client.schemas.enums.call_style import CallStyle
from luna_quantum.client.schemas.enums.model_format import ModelFormat
from luna_quantum.client.schemas.enums.status import StatusEnum
from luna_quantum.client.schemas.wrappers import PydanticDatetimeWrapper
from luna_quantum.factories.luna_solve_client_factory import LunaSolveClientFactory
from luna_quantum.util.log_utils import Logging


class SolveJob(BaseModel):
    """A model to represent a job for solving model problems."""

    _logger: ClassVar[Logger] = Logging.get_logger(__name__)
    id: str
    status: StatusEnum
    status_timeline: dict[StatusEnum, PydanticDatetimeWrapper]
    error_message: str | None = None
    solver_job_info: str | None = None
    used_format: ModelFormat | None = None
    provider: str | None = None
    is_cancelable: bool = True
    is_cancellation_requested: bool = False

    metadata: dict[str, Any] | None = None
    _result: Solution | None = PrivateAttr(default=None)

    _model: Model | None = PrivateAttr(default=None)

    def set_evaluation_model(self, model: Model | None) -> None:
        """
        Set the evaluation model for the solved job.

        This will be done automatically. Normally there is no need to call this method.

        Parameters
        ----------
        model: Model|None

        """
        self._model = model

    def get_status(
        self,
        client: ILunaSolve | None = None,
        status_source: Literal["cached", "remote"] = "cached",
    ) -> StatusEnum:
        """
        Retrieve the current status of the solve job.

        Parameters
        ----------
        status_source : Literal["cached", "remote"], optional
            If "cached", the status is retrieved from the cached status. If "remote",
            the status is retrieved from the remote service.

        client : Optional[ILunaSolve], optional
            The client to be used. If not provided, a new client is created using

        Returns
        -------
        StatusEnum
            The current status of the solve job, represented as a value
            from the `StatusEnum` enumeration.

        """
        if status_source == "remote":
            c: ILunaSolve = LunaSolveClientFactory.get_client(client)

            from luna_quantum.factories.usecase_factory import UseCaseFactory

            UseCaseFactory.solve_job_fetch_update(client=c).__call__(solve_job=self)

        return self.status

    def result(
        self,
        client: ILunaSolve | None = None,
        sleep_time_max: float = 60.0,
        sleep_time_increment: float = 5.0,
        sleep_time_initial: float = 5.0,
        call_style: CallStyle = CallStyle.ACTIVE_WAITING,
    ) -> Solution | None:
        """
        Get the result of the solve job.

        This function uses the provided client or creates a new one to retrieve
        and the result of this solve job. Depending on the call style, it can
        actively wait for the result or return immediately.

        Parameters
        ----------
        client : Optional[ILunaSolve], optional
            The client to be used. If not provided, a new client is created using
            ClientFactory.
        sleep_time_max : float, optional
            Maximum sleep time in seconds between consecutive active waiting checks.
        sleep_time_increment : float, optional
            Increment value for the sleep time between checks during active waiting.
        sleep_time_initial : float, optional
            Initial sleep time in seconds for the active waiting process.
        call_style : CallStyle, optional
            Determines if this function will actively wait for the result or return
            immediately.

        Returns
        -------
        Optional[Solution]
            The result of the solve job or None if not available.

        Raises
        ------
        Any exceptions raised by the use case's solve job call will propagate.
        """
        if self._result:
            return self._result

        c: ILunaSolve = LunaSolveClientFactory.get_client(client)

        from luna_quantum.factories.usecase_factory import UseCaseFactory

        self._result = UseCaseFactory.solve_job_get_result(client=c).__call__(
            solve_job=self,
            sleep_time_max=sleep_time_max,
            sleep_time_increment=sleep_time_increment,
            sleep_time_initial=sleep_time_initial,
            call_style=call_style,
        )

        if self._result is None:
            return None
        if self._model is None:
            SolveJob._logger.info(
                "The solve job object does not contain a model. "
                "This solution is not evaluated."
            )
        else:
            self._result = self._model.evaluate(self._result)

        return self._result

    def cancel(self, client: ILunaSolve | None = None) -> None:
        """
        Cancel a solve job.

        This method cancels an already initiated solve job using the provided client
        or a default one if no client is specified.

        Parameters
        ----------
        client : Optional[ILunaSolve], optional
            The client instance used to perform the cancel operation. If None, the
            client is obtained via the ClientFactory.

        Returns
        -------
        None
        """
        c: ILunaSolve = LunaSolveClientFactory.get_client(client)

        from luna_quantum.factories.usecase_factory import UseCaseFactory

        UseCaseFactory.solve_job_cancel(client=c).__call__(self)

    def delete(self, client: ILunaSolve | None = None) -> None:
        """
        Delete a job using the specified or default client.

        This method deletes this job and solution. A client can optionally be provided
        otherwise, a default client is obtained through the factory.

        Parameters
        ----------
        client : Optional[ILunaSolve], optional
            The client to be used for job deletion. If not provided, a default client
            is retrieved using `ClientFactory`.
        """
        c: ILunaSolve = LunaSolveClientFactory.get_client(client)

        from luna_quantum.factories.usecase_factory import UseCaseFactory

        UseCaseFactory.solve_job_delete(client=c).__call__(solve_job_id=self.id)
