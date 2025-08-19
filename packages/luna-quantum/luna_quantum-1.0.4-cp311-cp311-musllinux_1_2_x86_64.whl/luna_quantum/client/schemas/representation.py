from typing import Any

from pydantic import BaseModel


class Representation(BaseModel):
    """
    Pydantic model for representation of a solution sample.

    Attributes
    ----------
    description: str
        Description of the representation
    solution: Any
        matrix of the solution representation
    """

    description: str
    solution: Any
