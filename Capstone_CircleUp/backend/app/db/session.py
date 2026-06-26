"""
Database engine and session management.

`get_db` is used as a FastAPI dependency in routers, e.g.:

    @router.get("/activities")
    def list_activities(db: Session = Depends(get_db)):
        ...

It guarantees the session is closed after the request, even if an
exception is raised mid-request.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()