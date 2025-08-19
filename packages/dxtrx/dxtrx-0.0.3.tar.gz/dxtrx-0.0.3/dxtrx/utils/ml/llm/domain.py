from typing import List
from pydantic import BaseModel, Field
from typing_extensions import Literal

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., description="The content of the message in the chat.")


class AssistantPrompt(BaseModel):
    messages: List[Message] = Field(..., description="List of chat messages to prime the assistant.")
