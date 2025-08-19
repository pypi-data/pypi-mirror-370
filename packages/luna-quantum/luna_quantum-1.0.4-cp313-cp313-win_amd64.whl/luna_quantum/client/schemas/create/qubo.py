from __future__ import annotations

from pydantic import BaseModel


class QUBOIn(BaseModel):
    """
    Pydantic model for QUBO.

    Attributes
    ----------
    name: str
        Name of the Model
    matrix: List[List[float]]
        QUBO matrix
    """

    name: str
    matrix: list[list[float]]
