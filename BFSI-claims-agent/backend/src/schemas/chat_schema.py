from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """One message a customer sends in a claim's chat."""
    message: str = Field(..., min_length=1, max_length=1000)


class ChatMessageResponse(BaseModel):
    """The assistant's reply to one chat message. Not saved anywhere --
    the conversation only lives in the chat agent's in-memory checkpointer
    for as long as the backend keeps running."""
    reply: str