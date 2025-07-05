from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import insert

from src.app.schemas.auth import LoginResponse
from src.app.schemas.user import UserAuth
from src.app.database.session import async_session_maker
from src.app.models import User
from src.app.services.dao import UserService
from src.app.security.auth import create_access_token, get_password_hash, verify_password

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register")
async def register_user(user_data: UserAuth):
    await UserService.add_user(user_data)


@router.post("/login", response_model=LoginResponse)
async def login_user(response: Response,user_data: UserAuth):
    async with async_session_maker() as session:
        user = await UserService.get_by_email(user_data.email)
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        access_token = create_access_token({'sub': str(user.id)})
        response.set_cookie("access_token", access_token, httponly=True, secure=True)
        return LoginResponse(access_token=access_token, role=user.role)
    

