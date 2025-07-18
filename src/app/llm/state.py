import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage


class State(TypedDict):
    messages = Annotated[Sequence[BaseMessage], operator.add]
    