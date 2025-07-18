from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserAuth(UserBase):
    password: str

