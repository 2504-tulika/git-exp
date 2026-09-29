from fastapi import APIRouter
from sqlalchemy import text

from src.config.database import engine
from src.schemas.response_schema import HealthResponse
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    """"ok" if the API and its database connection are both working, "degraded" if the DB is unreachable."""
    status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error(f"Health check: database unreachable -- {exc}")
        status = "degraded"

    health_response = HealthResponse(status=status)
    return health_response


