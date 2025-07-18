import enum
from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import relationship

from src.app.database.base import Base

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole, name="user_role_enum", values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=UserRole.USER)

    conversations = relationship("Conversation", back_populates="owner", cascade="all, delete-orphan")

