from pydantic import BaseModel


class SendMessage(BaseModel):
    model_version: str
    question: str


class ChatResponse(BaseModel):
    model_response: str
    