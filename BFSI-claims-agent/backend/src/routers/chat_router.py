from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.repositories.models import User
from src.routers.auth_router import get_current_user_dep
from src.schemas.chat_schema import ChatMessageRequest, ChatMessageResponse
from src.services import chat_service

router = APIRouter(prefix="/claims", tags=["chat"])


@router.post("/{claim_id}/chat", response_model=ChatMessageResponse)
def chat_about_claim(
    claim_id: str,
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """
    Ask a follow-up question about one of the logged-in customer's own
    claims. Only works once that claim already has an AI recommendation.
    """
    reply = chat_service.send_message(db, current_user, claim_id, request.message)
    return ChatMessageResponse(reply=reply)