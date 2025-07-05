from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserAuth(UserBase):
    password: str


class UserInfo(UserBase):
    id: int

    class Config:
        from_attributes = True