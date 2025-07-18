from typing import Protocol
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from config import settings
from src.app.schemas.llm import ModelResponse


class LLMConfig(Protocol):
    api_key: str
    model_name: str


    def create_llm(self):
        ... 



class OpenAIConfig(LLMConfig):
    def __init__(self, model_version: str, temperature: float = 0, api_key: str = settings.OPENAI_API_KEY,model_name: str = "GPT"):
        self.model_name = model_name
        self.model_version = model_version
        self.api_key = api_key
        self.temperature = temperature


    def create_llm(self):
        return ChatOpenAI(
            model=self.model_version,
            temperature=self.temperature,
            api_key=self.api_key
        )
    


MODEL_REGISTRY = {
    "gpt-4o": OpenAIConfig("gpt-4o"),
    "gpt-4o-mini": OpenAIConfig("gpt-4o-mini")
}



def get_model(model_version: str) -> BaseChatModel:
    if model_version not in MODEL_REGISTRY:
        raise ValueError(f"Модель {model_version} не найдена в реестре")
    
    model_config = MODEL_REGISTRY[model_version]
    return model_config.create_llm()



def create_llm_chain(llm: BaseChatModel) -> ModelResponse:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You're an assistant. Ask my question"),
        ("user", "Question: {question}")
    ])

    chain = prompt | llm.with_structured_output(ModelResponse)
    return chain


