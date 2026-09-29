from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.repositories.models import User
from src.routers.auth_router import get_current_user_dep
from src.schemas.chat_schema import ChatMessageRequest, ChatMessageResponse, ChatTurn
from src.services import chat_service

# No shared prefix: "/claims/{claim_id}/chat" and "/policies/chat" live under
# different roots, and a "/claims" prefix would let "/claims/policies/chat"
# be swallowed by the {claim_id} route.
router = APIRouter(tags=["chat"])


@router.post("/claims/{claim_id}/chat", response_model=ChatMessageResponse)
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


@router.post("/policies/chat", response_model=ChatMessageResponse)
def chat_about_policies(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """
    Ask about any of the logged-in customer's own policies, including what
    their policy documents say (clauses, exclusions, waiting periods).
    """
    reply = chat_service.send_policies_message(db, current_user, request.message)
    return ChatMessageResponse(reply=reply)



@router.get("/claims/{claim_id}/chat", response_model=List[ChatTurn])
def claim_chat_history(
    claim_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Earlier chat messages about one of the logged-in customer's own claims."""
    return chat_service.get_claim_history(db, current_user, claim_id)


@router.get("/policies/chat", response_model=List[ChatTurn])
def policies_chat_history(current_user: User = Depends(get_current_user_dep)):
    """Earlier messages in the logged-in customer's Policies-tab chat."""
    return chat_service.get_policies_history(current_user)
