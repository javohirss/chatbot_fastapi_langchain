import enum
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Enum as SQLEnum, String
from sqlalchemy.orm import relationship

from src.app.database.base import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))


    owner = relationship("User", back_populates="conversations")
    
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")


class MessageSender(str, enum.Enum):
    USER = "user"
    BOT = "bot"


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(SQLEnum(MessageSender, name="message_sender_enum", values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="messages")
