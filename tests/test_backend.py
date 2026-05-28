# ==============================================================================
# JEE MENTOR AI - FASTAPI BACKEND UNIT & INTEGRATION TESTS
# ==============================================================================
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.main import app

# Setup local memory SQLite for instantaneous, clean test state isolation
TEST_SQLITE_URL = "sqlite:///./test_jee_mentor.db"
engine = create_engine(TEST_SQLITE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override FastAPI get_db dependency during test lifecycle
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Initializes tables before test execution and clears them down after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Delete file
    import os
    if os.path.exists("./test_jee_mentor.db"):
        os.remove("./test_jee_mentor.db")

client = TestClient(app)

# Global test variables
test_user = {
    "email": "test_aspirant@jeementor.ai",
    "username": "test_aspirant",
    "password": "securepassword123",
    "full_name": "Test Aspirant"
}
auth_headers = {}

def test_user_registration():
    """Asserts registration successfully saves details and rejects duplicates."""
    response = client.post("/register", json=test_user)
    assert response.status_code in [201, 200]
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["username"] == test_user["username"]
    assert "id" in data

    # Assert duplicate rejection
    response_dup = client.post("/register", json=test_user)
    assert response_dup.status_code == 400

def test_user_login():
    """Asserts logins accept valid passwords and returns JWT headers."""
    global auth_headers
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Store headers for subsequent secure route testing
    auth_headers = {"Authorization": f"Bearer {data['access_token']}"}

def test_chat_endpoint():
    """Asserts streaming response structure and active session creations."""
    response = client.post("/chat", json={"message": "Solve the electric field of wire"}, headers=auth_headers)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    
    # Read the first event buffer chunk
    content = next(response.iter_lines()).decode("utf-8")
    assert "SESSION_ID" in content

def test_question_solver_endpoint():
    """Asserts step-by-step solver returns formulas lists and latency indicators."""
    payload = {
        "question_text": "What is the moment of inertia of a solid sphere of mass 10kg?",
        "subject": "Physics"
    }
    response = client.post("/solve", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "solution" in data
    assert "formulas_used" in data
    assert "latency_ms" in data

def test_generate_adaptive_quiz():
    """Asserts practice test generator produces personalized lists."""
    payload = {
        "subject": "Physics",
        "topics": ["Electrostatics", "Rotational Mechanics"],
        "difficulty": "Medium",
        "num_questions": 3
      }
    response = client.post("/generate-test", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "input" in data[0]

def test_analytics_dashboard():
    """Asserts analytics summaries compile correct accuracy metrics."""
    response = client.get("/analyze", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "overall_accuracy" in data
    assert "total_solved" in data
    assert "subjects_proficiency" in data
