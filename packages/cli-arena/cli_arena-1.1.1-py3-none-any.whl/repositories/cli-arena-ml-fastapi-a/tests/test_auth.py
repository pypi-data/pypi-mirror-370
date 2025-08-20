import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.app.main import app
from src.app import database, auth, models
import tempfile
import os
# Create test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Override dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
app.dependency_overrides[database.get_db] = override_get_db
# Create tables
database.Base.metadata.create_all(bind=engine)
client = TestClient(app)
@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: Create tables
    database.Base.metadata.create_all(bind=engine)
    yield
    # Teardown: Drop tables
    database.Base.metadata.drop_all(bind=engine)
def test_register_user():
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert data["is_active"] == True
def test_register_duplicate_username():
    # Register first user
    client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test1@example.com",
            "password": "testpassword123"
        }
    )
    
    # Try to register with same username
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]
def test_register_duplicate_email():
    # Register first user
    client.post(
        "/register",
        json={
            "username": "testuser1",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/register",
        json={
            "username": "testuser2",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]
def test_login_success():
    # Register user first
    client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    # Login
    response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
def test_login_invalid_credentials():
    response = client.post(
        "/login",
        json={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]
def test_protected_endpoint_with_valid_token():
    # Register and login user
    client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    login_response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
def test_protected_endpoint_without_token():
    response = client.get("/me")
    assert response.status_code == 403
def test_protected_endpoint_with_invalid_token():
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "Invalid authentication credentials" in response.json()["detail"]
def test_refresh_token():
    # Register and login user
    client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    login_response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # Use refresh token
    response = client.post(
        "/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
def test_refresh_token_invalid():
    response = client.post(
        "/refresh",
        json={"refresh_token": "invalid_refresh_token"}
    )
    assert response.status_code == 401
    assert "Invalid refresh token" in response.json()["detail"]
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
# Cleanup
@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    # Clean up test database
    if os.path.exists("test.db"):
        os.remove("test.db")
