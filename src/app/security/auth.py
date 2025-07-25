from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt 

from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=40)
    to_encode |= {"exp": expire}
    
    encoded = jwt.encode(
        to_encode, settings.JWT_KEY, settings.JWT_ALGORITHM
    )

    return encoded


