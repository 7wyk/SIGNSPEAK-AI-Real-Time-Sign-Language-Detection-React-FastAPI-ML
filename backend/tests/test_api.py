"""
API endpoint tests for SignSpeak AI FastAPI backend.
Run with: backend\venv\Scripts\python.exe -m pytest backend\tests\test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


# --- Root ---

def test_root(client):
    """GET / should return API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "SignSpeak AI API"
    assert "version" in data


# --- Registration ---

def test_register_success(client, tmp_path, monkeypatch):
    """POST /register should create a new user."""
    # Point to a temp users file so we don't pollute real data
    import app.config as config_module
    monkeypatch.setattr(config_module.settings, "USERS_FILE", str(tmp_path / "users.json"))

    response = client.post("/register", json={
        "username": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Registration successful"


def test_register_duplicate(client, tmp_path, monkeypatch):
    """POST /register should reject duplicate usernames."""
    import app.config as config_module
    monkeypatch.setattr(config_module.settings, "USERS_FILE", str(tmp_path / "users.json"))

    # Register first time
    client.post("/register", json={
        "username": "test@example.com",
        "password": "testpass123"
    })
    # Try again
    response = client.post("/register", json={
        "username": "test@example.com",
        "password": "testpass123"
    })
    data = response.json()
    assert data["success"] is False
    assert "already exists" in data["message"]


def test_register_missing_fields(client):
    """POST /register should return 422 for missing fields."""
    response = client.post("/register", json={})
    assert response.status_code == 422


# --- Login ---

def test_login_success(client, tmp_path, monkeypatch):
    """POST /login should return a JWT token."""
    import app.config as config_module
    monkeypatch.setattr(config_module.settings, "USERS_FILE", str(tmp_path / "users.json"))

    # Register
    client.post("/register", json={
        "username": "test@example.com",
        "password": "testpass123"
    })
    # Login
    response = client.post("/login", json={
        "username": "test@example.com",
        "password": "testpass123"
    })
    data = response.json()
    assert data["success"] is True
    assert "token" in data
    assert data["token"] is not None


def test_login_invalid_credentials(client, tmp_path, monkeypatch):
    """POST /login should reject wrong password."""
    import app.config as config_module
    monkeypatch.setattr(config_module.settings, "USERS_FILE", str(tmp_path / "users.json"))

    client.post("/register", json={
        "username": "test@example.com",
        "password": "testpass123"
    })
    response = client.post("/login", json={
        "username": "test@example.com",
        "password": "wrongpassword"
    })
    data = response.json()
    assert data["success"] is False


# --- Protected Routes ---

def test_start_detection_unauthorized(client):
    """POST /start_detection without token should return 403."""
    response = client.post("/start_detection")
    assert response.status_code == 403


def test_start_detection_invalid_token(client):
    """POST /start_detection with invalid token should return 401."""
    response = client.post("/start_detection", headers={
        "Authorization": "Bearer invalidtoken123"
    })
    assert response.status_code == 401


# --- Prediction ---

def test_get_prediction(client):
    """GET /get_prediction should return current prediction."""
    response = client.get("/get_prediction")
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data


# --- Stop Detection ---

def test_stop_detection(client):
    """POST /stop_detection should work without auth."""
    response = client.post("/stop_detection")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# --- Feedback ---

def test_feedback_submit(client, tmp_path, monkeypatch):
    """POST /feedback should save feedback."""
    import app.config as config_module
    monkeypatch.setattr(config_module.settings, "FEEDBACK_FILE", str(tmp_path / "feedback.json"))

    response = client.post("/feedback", json={
        "feedback": "Great app!"
    })
    data = response.json()
    assert data["success"] is True


def test_feedback_missing_field(client):
    """POST /feedback should return 422 for missing feedback."""
    response = client.post("/feedback", json={})
    assert response.status_code == 422


# --- Translation ---

def test_translate_missing_fields(client):
    """POST /translate should return 422 for missing fields."""
    response = client.post("/translate", json={})
    assert response.status_code == 422


# --- CORS ---

def test_cors_headers(client):
    """OPTIONS request should include CORS headers."""
    response = client.options("/", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
    })
    # CORS middleware should allow the configured origin
    assert response.status_code == 200
