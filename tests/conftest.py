import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.auth import get_password_hash
from app import models

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture(scope="function")
def test_user(client):
    response = client.post(
        "/users/signup",
        json={"username": "testuser", "email": "test@example.com", "password": "testpassword", "is_admin": False}
    )
    assert response.status_code == 201
    return response.json()

@pytest.fixture(scope="function")
def test_admin(client):
    response = client.post(
        "/users/signup",
        json={"username": "adminuser", "email": "admin@example.com", "password": "adminpassword", "is_admin": True}
    )
    assert response.status_code == 201
    return response.json()

@pytest.fixture(scope="function")
def user_token(client, test_user):
    response = client.post(
        "/users/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def admin_token(client, test_admin):
    response = client.post(
        "/users/login",
        data={"username": "adminuser", "password": "adminpassword"}
    )
    return response.json()["access_token"]
