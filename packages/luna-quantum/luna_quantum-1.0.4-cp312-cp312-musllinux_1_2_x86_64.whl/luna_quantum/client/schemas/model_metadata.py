from pydantic import BaseModel

from luna_quantum.client.schemas.wrappers import PydanticDatetimeWrapper


class ModelMetadataSchema(BaseModel):
    """
    Model metadata schema.

    Attributes
    ----------
    id: str
        Unique identifier for the model.

    created_date: PydanticDatetimeWrapper
        The timestamp when the model was initially created.

    created_by: str
        Identifier of the user that created the model.

    modified_date: PydanticDatetimeWrapper | None
        The timestamp when the model was last modified.
        None if the model has never been modified after creation.

    modified_by: str | None
        Identifierof the user that last modified the model.
        None if the model has never been modified after creation.
    """

    id: str
    created_date: PydanticDatetimeWrapper
    created_by: str

    modified_date: PydanticDatetimeWrapper | None = None
    modified_by: str | None = None
