from pydantic import BaseModel, Field, field_validator

from src.config import constants


class ChatMessageRequest(BaseModel):
    """One message a customer sends in a claim's chat."""
    message: str = Field(..., min_length=1, max_length=constants.MAX_CHAT_MESSAGE_LENGTH)

    @field_validator("message")
    @classmethod
    def strip_and_require_text(cls, value):
        stripped = value.strip()
        if not stripped:
            raise ValueError("Message cannot be blank")
        return stripped


class ChatMessageResponse(BaseModel):
    """The assistant's reply to one chat message. Not saved anywhere --
    the conversation only lives in the chat agent's in-memory checkpointer
    for as long as the backend keeps running."""
    reply: str


class ChatTurn(BaseModel):
    """One earlier message in a conversation, as shown in the chat box."""
    role: str
    content: str
