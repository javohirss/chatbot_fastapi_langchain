from fastapi import Depends, HTTPException, Request, status, WebSocket
from jose import jwt, JWTError

from src.app.models.user import UserRole
from src.app.services.dao import UserService
from config import settings


def get_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return token


def get_token_ws(websocket: WebSocket):
    token = websocket.cookies.get("access_token")
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return token


async def get_current_user(token = Depends(get_token)):
    try:
        payload = jwt.decode(token, settings.JWT_KEY, settings.JWT_ALGORITHM)
        user_id: str | None = payload.get("sub")

        if user_id is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
        
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    
    user = await UserService.get_by_id(int(user_id))
    return user


async def get_current_admin_user(token = Depends(get_token)):
    try:
        payload = jwt.decode(token, settings.JWT_KEY, settings.JWT_ALGORITHM)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    except:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    
    user = await UserService.get_by_id(int(user_id))
    if not (user.role == UserRole.ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="У пользователя нет доступа")
    
    return user