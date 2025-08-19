from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class PydanticUtils:
    """A utility class for operations on Pydantic models."""

    @staticmethod
    def update_model(to_update: T, other_model: T) -> None:
        """
        Update the attributes of a given pydantic model.

        This function works by iterating over the attributes
        of the second model (provided as input) and assigns the corresponding values
        to the attributes of the first model.

        Parameters
        ----------
        to_update : T
            The model instance whose attributes need to be updated. This instance
            will have its attributes overridden with the corresponding values from
            the other model instance.
        other_model : T
            The model instance providing the new values for the update. Its
            attributes are used to overwrite the attributes of the `to_update`
            instance.

        Returns
        -------
        None
            This function does not return a value. Instead, it updates the
            `to_update` instance in place.
        """
        for key, value in other_model.model_dump().items():
            setattr(to_update, key, value)
