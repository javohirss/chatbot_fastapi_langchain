from pydantic import BaseModel, Field


class ModelResponse(BaseModel):
    answer: str = Field(description="The answer to user's question")