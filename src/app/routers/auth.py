from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import insert

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
    async with async_session_maker() as session:
        if await UserService.get_by_email(user_data.email):
            raise HTTPException(status.HTTP_409_CONFLICT)
        
        hashed_password = get_password_hash(user_data.password)
        query = insert(User).values(email=user_data.email, hashed_password=hashed_password)
        await session.execute(query)
        await session.commit()


@router.post("/login")
async def login_user(response: Response,user_data: UserAuth):
    async with async_session_maker() as session:
        user = await UserService.get_by_email(user_data.email)
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status.HTTP_409_CONFLICT)
        
        access_token = create_access_token({'sub': str(user.id)})
        response.set_cookie("access_token", access_token, httponly=True, secure=True)
        return access_token

