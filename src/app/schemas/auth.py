from pydantic import BaseModel

from src.app.models import UserRole


class LoginResponse(BaseModel):
    access_token: str
    role: UserRole