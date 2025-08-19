from pydantic import BaseModel


class SolverInfo(BaseModel):
    """Solver info schema."""

    full_name: str
    short_name: str
    available: bool
    params: dict  # type: ignore[type-arg]
    description: str | None
