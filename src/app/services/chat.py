from fastapi import HTTPException, status

from src.app.models import MessageSender
from src.app.llm.models import create_llm_chain, get_model
from src.app.services.dao import ConversationService, MessageService


class ChatService:
    @classmethod
    async def process_new_chat(cls, user_id: int, model_version: str, question: str):
        conversation_id = await ConversationService.create(user_id)

        try:
            chain = create_llm_chain(get_model(model_version))
            model_response = chain.invoke({"question": question})
            answer = model_response.answer

        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка вызова модели: {e}")
        

        await MessageService.create(conversation_id, MessageSender.USER, question)
        await MessageService.create(conversation_id, MessageSender.BOT, answer)

        return conversation_id, answer
    

    @classmethod
    async def process_existing_chat(cls, conversation_id: int, model_version: str, question: str):
        try:
            chain = create_llm_chain(get_model(model_version))
            model_response = chain.invoke({"question": question})
            answer = model_response.answer

        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка вызова модели: {e}")
        

        await MessageService.create(conversation_id, MessageSender.USER, question)
        await MessageService.create(conversation_id, MessageSender.BOT, answer)

        return answer