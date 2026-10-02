import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def sample_resume_text():
    return "Experienced Software Engineer with 5 years of experience in Python, FastAPI, and Machine Learning."

@pytest.fixture
def sample_skills():
    return ["Python", "FastAPI", "Machine Learning", "SQL"]
