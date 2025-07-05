from fastapi import HTTPException, status
from sqlalchemy import insert, select

from src.app.schemas.user import UserAuth
from src.app.models import Conversation, User, ChatMessage, UserRole, MessageSender
from src.app.database.session import async_session_maker
from src.app.security.auth import get_password_hash


class BaseService:
    model = None   


    @classmethod
    async def get_all(cls):
        async with async_session_maker() as session:
            query = select(cls.model)
            result = await session.execute(query)
            return result.scalars().all()

    
    @classmethod
    async def get_by_id(cls, id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        

class UserService(BaseService):
    model = User

    @classmethod
    async def add_user(cls, user_data: UserAuth):
        async with async_session_maker() as session:
            if await cls.get_by_email(user_data.email):
                raise HTTPException(status.HTTP_409_CONFLICT)
            
            hashed_password = get_password_hash(user_data.password)
            query = insert(User).values(email=user_data.email, hashed_password=hashed_password)
            await session.execute(query)
            await session.commit()

    
    @classmethod
    async def add_admin(cls, user_data: UserAuth):
        async with async_session_maker() as session:
            if await cls.get_by_email(user_data.email):
                raise HTTPException(status.HTTP_409_CONFLICT)
            
            hashed_password = get_password_hash(user_data.password)
            query = (insert(User)
                     .values(email=user_data.email, hashed_password=hashed_password, role=UserRole.ADMIN)
                     .returning(User))

            result = await session.execute(query)
            admin_user = result.scalar_one()

            await session.commit()
            return admin_user


    @classmethod
    async def get_by_email(cls, email: str):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.email == email)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        

    @classmethod
    async def get_message_history(cls, user_id):
        async with async_session_maker() as session:
            query = (select(ChatMessage)
                     .join(ChatMessage.conversation)
                     .where(Conversation.user_id==user_id)
                     .order_by(ChatMessage.timestamp))
            
            result = await session.execute(query)
            return result.scalars().all()


       
        

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
