from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """Pydantic model for user going OUT."""

    email: EmailStr
    first_name: str
    last_name: str
    groups: list[str] = []
    orgs: list[str] = []
