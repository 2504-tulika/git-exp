import pytest
from datetime import date, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.activity import Activity
from app.constants import ActivityStatus

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    # connect_args is only needed for SQLite to support multi-threading in tests
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create all tables in the in-memory SQLite database once for the session."""
    from app.db.base import Base # assuming DeclarativeBase lives here
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Yield a new transaction-isolated session per test, rolling back changes at the end."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """Override the get_db dependency to use the isolated test database session."""
    def _get_test_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = _get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user_1(db):
    """Create a persistent user record representing Alice (Creator)."""
    user = User(
        name="Alice Johnson",
        email="alice@example.com",
        password_hash="mocked_hash_alice",
        phone="1234567890",
        gender="Female",
        city="Seattle",
        bio="Hello, I am Alice.",
        social_handle="@alice_j"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def mock_user_2(db):
    """Create a persistent user record representing Bob (Applicant)."""
    user = User(
        name="Bob Smith",
        email="bob@example.com",
        password_hash="mocked_hash_bob",
        phone="0987654321",
        gender="Male",
        city="Seattle",
        bio="Hi, I am Bob.",
        social_handle="@bob_s"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def mock_user_3(db):
    """Create an unrelated third-party user record representing Charlie."""
    user = User(
        name="Charlie Brown",
        email="charlie@example.com",
        password_hash="mocked_hash_charlie",
        phone="5551234567",
        gender="Male",
        city="Portland",
        bio="Hey, I am Charlie.",
        social_handle="@charlie_b"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_client(client, mock_user_1):
    """Override get_current_user dependency to mock Alice as the logged-in user."""
    def _get_mock_user():
        return mock_user_1
        
    app.dependency_overrides[get_current_user] = _get_mock_user
    yield client
    # Overrides are cleared by the base client fixture, but clean up here to be safe
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]


@pytest.fixture
def mock_activity(db, mock_user_1):
    """Create a default active future activity with Alice as the creator."""
    activity = Activity(
        creator_id=mock_user_1.id,
        title="Seattle Board Games Night",
        description="Playing strategy board games in Seattle.",
        category="Games",
        location="Greenwood Public Library",
        activity_date=date(2026, 12, 1),
        activity_time=time(18, 30),
        max_participants=5,
        status=ActivityStatus.OPEN.value
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity