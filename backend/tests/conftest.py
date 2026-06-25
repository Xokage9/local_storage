import uuid
from collections.abc import Generator
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user, get_db
from app.main import app
from app.models import Base
from app.models.user import User

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Generator[Session]:
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_user(db: Session) -> User:
    user = User(
        id=uuid.uuid4(),
        keycloak_id="test-kc-id",
        email="test@example.com",
        display_name="Test User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def second_user(db: Session) -> User:
    user = User(
        id=uuid.uuid4(),
        keycloak_id="second-kc-id",
        email="second@example.com",
        display_name="Second User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def client(db: Session, test_user: User) -> TestClient:
    def override_get_db():
        yield db

    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_second_user(db: Session, second_user: User) -> TestClient:
    def override_get_db():
        yield db

    def override_get_current_user():
        return second_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
