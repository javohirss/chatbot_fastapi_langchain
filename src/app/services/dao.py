from sqlalchemy import insert, select

from src.app.models import Conversation, User, ChatMessage, MessageSender
from src.app.database.session import async_session_maker


class BaseService:
    model = None   
    
    @classmethod
    async def get_by_id(cls, id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        

class UserService(BaseService):
    model = User

    @classmethod
    async def get_by_email(cls, email: str):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.email == email)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        

class ConversationService(BaseService):
    model = Conversation

    
    @classmethod
    async def create(cls, user_id: int):
        async with async_session_maker() as session:
            query = insert(cls.model).values(user_id=user_id).returning(cls.model.id)
            result = await session.execute(query)
            conversation_id = result.scalar_one_or_none()
            await session.commit()
            return conversation_id
        

class MessageService(BaseService):
    model = ChatMessage


    @classmethod
    async def create(cls, conversation_id: int, sender_type: MessageSender, content: str):
        async with async_session_maker() as session:
            query = insert(cls.model).values(
                conversation_id=conversation_id,
                sender_type=sender_type,
                content=content
            )
            await session.execute(query)
            await session.commit()
