from fastapi import APIRouter, Depends

from src.app.security.dependencies import get_current_admin_user
from src.app.schemas.user import UserAuth, UserInfo
from src.app.services.dao import UserService


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin_user)]
)


@router.post("/register")
async def register_admin(user_data: UserAuth):
    admin_user = await UserService.add_admin(user_data)
    return admin_user


@router.get("/users", response_model=list[UserInfo])
async def get_all_users():
    users = await UserService.get_all()
    return users


@router.get("/{user_id}")
async def get_user_message_history(user_id: int):
    chat_history = await UserService.get_message_history(user_id)
    return chat_history