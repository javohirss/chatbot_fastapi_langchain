from fastapi import APIRouter, HTTPException, Request, Response, status, Depends

from src.app.services.chat import ChatService
from src.app.security.dependencies import get_current_user
from src.app.services.dao import ConversationService, MessageService
from src.app.schemas.chat import SendMessage, ChatResponse
from src.app.models import Conversation, MessageSender
from src.app.llm.models import get_model, create_llm_chain
from src.app.database.session import async_session_maker


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


def get_model_version(request: Request):
    model_version = request.cookies.get("model_version")
    if model_version is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Чат не был создан")
    
    return model_version


def get_chat_id(request: Request):
    conv_id = request.cookies.get("conversation_id")
    if conv_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Чат не был создан")
    
    return int(conv_id)


@router.post("/", response_model=ChatResponse)
async def start_chat(response: Response, chat_params: SendMessage, current_user = Depends(get_current_user)):
    conversation_id, answer = await ChatService.process_new_chat(
        user_id=int(current_user.id),
        model_version=chat_params.model_version,
        question=chat_params.question
    )

    response.set_cookie("conversation_id", conversation_id)
    # response.set_cookie("model_version", chat_params.model_version)

    return ChatResponse(model_response=answer)


@router.post("/{conversation_id}", response_model=ChatResponse)
async def add_message_to_existing_chat(chat_params: SendMessage, conversation_id: int = Depends(get_chat_id), current_user=Depends(get_current_user)):
    answer = await ChatService.process_existing_chat(
        conversation_id=conversation_id,
        model_version=chat_params.model_version,
        question=chat_params.question
    )

    return ChatResponse(model_response=answer)



    


    
    

    