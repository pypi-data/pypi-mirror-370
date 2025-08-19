from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

from luna_quantum.client.schemas.wrappers import (
    PydanticDatetimeWrapper,  # noqa: TC001 Otherwise Pydantic will break
)
from luna_quantum.factories.luna_solve_client_factory import LunaSolveClientFactory

if TYPE_CHECKING:
    from luna_quantum.aqm_overwrites import Model
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve


class ModelMetadata(BaseModel):
    """Metadata of an AQ model."""

    id: str

    created_date: PydanticDatetimeWrapper
    created_by: str

    modified_date: PydanticDatetimeWrapper | None = None
    modified_by: str | None = None

    def fetch_model(self, client: ILunaSolve | str | None = None) -> Model:
        """
        Fetch a Model instance using the provided client input.

        The method uses the client input, which can be an instance of ILunaSolve or a
        string, to create a client. It then loads the Model instance based on the
        metadata tied to the client.

        Parameters
        ----------
        client : Optional[Union[ILunaSolve, str]]
            The client object or identifier used to retrieve model metadata.

        Returns
        -------
        Model
            An Model instance loaded based on provided client metadata.
        """
        c = LunaSolveClientFactory.get_client(client=client)

        from luna_quantum.factories.usecase_factory import UseCaseFactory

        aq_model: Model = UseCaseFactory.model_load_by_metadata(client=c).__call__(
            model_metadata=self
        )

        return aq_model
