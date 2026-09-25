from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.repositories.customer_repository import CustomerRepository
from src.repositories.models import User
from src.routers.auth_router import get_current_user_dep
from src.schemas.claim_schema import ClaimResponse, ClaimSubmitRequest, PolicyResponse
from src.services import claim_service

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post("/submit", response_model=ClaimResponse, status_code=201)
async def submit_claim(
    request: ClaimSubmitRequest,
    current_user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """
    Submit a new claim against one of the logged-in customer's policies.
    """
    claim = await claim_service.submit_claim(db, current_user, request)
    return claim


@router.get("/policies/mine", response_model=List[PolicyResponse])
def list_my_policies(
    current_user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Every policy the logged-in customer holds."""
    policies = CustomerRepository(db).get_policies_for_customer(current_user.customer_id)
    return policies


@router.get("/mine", response_model=List[ClaimResponse])
def list_my_claims(
    current_user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Every claim the logged-in customer has filed."""
    claims = claim_service.get_my_claims(db, current_user)
    return claims


@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim(
    claim_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """One specific claim's full detail, if it belongs to the logged-in customer."""
    claim = claim_service.get_claim_detail(db, current_user, claim_id)
    return claim


