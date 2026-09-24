from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# SQLAlchemy needs an actual low-level MySQL driver underneath it -- we use
# PyMySQL for that (pure Python, no extra build tools needed to install).
# We never call pymysql directly anywhere else; SQLAlchemy is the only
# thing that talks to it.
DATABASE_URL = (
    f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}"
    f"@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"
)

# pool_pre_ping tests a connection is still alive before handing it to a
# query, so a connection MySQL quietly closed after being idle too long
# doesn't cause a confusing "server has gone away" error later.
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Every ORM model class (in repositories/models.py) inherits from this, so
# SQLAlchemy knows which Python classes map to which database tables.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that hands a route a database session, and always
    closes it afterwards -- even if the route raises an error.

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

