"""
Unit and API integration tests for Phase 5: Job Dataset and Management.
"""

import pytest
import os
import json
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import SessionLocal, Job, create_tables
from app.services.job_service import JobService
from scripts.seed_jobs import seed_jobs


@pytest.fixture(scope="module")
def client():
    create_tables()
    seed_jobs()
    return TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


class TestJobDataset:
    def test_jobs_json_dataset_exists(self):
        """Verify jobs.json dataset file exists and has 200+ records."""
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "jobs.json")
        assert os.path.exists(path), "data/jobs.json does not exist"

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) >= 200, f"Expected >= 200 jobs, found {len(data)}"

    def test_job_fields_completeness(self):
        """Verify each job in the dataset has all required attributes."""
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "jobs.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_keys = {
            "job_id", "title", "company", "category", "description",
            "required_skills", "preferred_skills", "min_experience",
            "experience_level", "education", "employment_type", "work_mode",
            "location", "job_status"
        }

        job_ids = set()
        for job in data:
            for k in required_keys:
                assert k in job, f"Job {job.get('job_id')} missing field {k}"

            # Check uniqueness
            assert job["job_id"] not in job_ids, f"Duplicate job_id: {job['job_id']}"
            job_ids.add(job["job_id"])

            # Check skills are non-empty list
            assert isinstance(job["required_skills"], list) and len(job["required_skills"]) > 0
            assert isinstance(job["preferred_skills"], list)

            # Check valid experience
            assert job["min_experience"] >= 0

    def test_database_persistence_and_seeder_idempotency(self, db):
        """Verify jobs are persisted in SQLite and re-seeding is idempotent."""
        initial_count = db.query(Job).count()
        assert initial_count >= 200

        # Run seed again
        res = seed_jobs()
        after_count = db.query(Job).count()
        assert after_count == initial_count, "Seeder created duplicates"
        assert res["inserted"] == 0


class TestJobEndpoints:
    def test_get_jobs_pagination(self, client):
        """Test GET /api/jobs with default and custom pagination."""
        resp = client.get("/api/jobs?page=1&limit=10")
        assert resp.status_code == 200
        data = resp.json()

        assert "jobs" in data
        assert "total" in data
        assert len(data["jobs"]) == 10
        assert data["page"] == 1
        assert data["limit"] == 10
        assert data["total"] >= 200

    def test_get_jobs_category_filter(self, client):
        """Test filtering jobs by category."""
        target_cat = "Machine Learning Engineer"
        resp = client.get(f"/api/jobs?category={target_cat}")
        assert resp.status_code == 200
        data = resp.json()

        assert len(data["jobs"]) > 0
        for job in data["jobs"]:
            assert job["category"] == target_cat

    def test_get_jobs_experience_filter(self, client):
        """Test filtering jobs by experience level (e.g. Entry-level)."""
        resp = client.get("/api/jobs?experience_level=Entry-level")
        assert resp.status_code == 200
        data = resp.json()

        assert len(data["jobs"]) > 0
        for job in data["jobs"]:
            assert job["experience_level"] == "Entry-level"
            assert job["min_experience"] <= 1

    def test_get_jobs_work_mode_filter(self, client):
        """Test filtering jobs by work mode (e.g. Remote)."""
        resp = client.get("/api/jobs?work_mode=Remote")
        assert resp.status_code == 200
        data = resp.json()

        assert len(data["jobs"]) > 0
        for job in data["jobs"]:
            assert job["work_mode"] == "Remote"

    def test_get_jobs_skill_filter(self, client):
        """Test filtering jobs by required skill (e.g. Python)."""
        resp = client.get("/api/jobs?skill=Python")
        assert resp.status_code == 200
        data = resp.json()

        assert len(data["jobs"]) > 0
        for job in data["jobs"]:
            has_python = any("python" in s.lower() for s in job["required_skills"] + job["preferred_skills"])
            assert has_python

    def test_get_job_by_id(self, client):
        """Test retrieving a single job by id and by code."""
        # Get first job
        list_resp = client.get("/api/jobs?limit=1")
        first_job = list_resp.json()["jobs"][0]

        # By numeric id
        resp1 = client.get(f"/api/jobs/{first_job['id']}")
        assert resp1.status_code == 200
        assert resp1.json()["title"] == first_job["title"]

        # By string code
        resp2 = client.get(f"/api/jobs/{first_job['job_id']}")
        assert resp2.status_code == 200
        assert resp2.json()["id"] == first_job["id"]

    def test_get_job_not_found(self, client):
        """Test 404 response for nonexistent job."""
        resp = client.get("/api/jobs/NONEXISTENT-999999")
        assert resp.status_code == 404

    def test_get_categories_endpoint(self, client):
        """Test GET /api/jobs/categories returns all 14 categories with counts."""
        resp = client.get("/api/jobs/categories")
        assert resp.status_code == 200
        cats = resp.json()

        assert len(cats) >= 14
        cat_names = [c["category"] for c in cats]
        assert "Machine Learning Engineer" in cat_names
        assert "Full Stack Developer" in cat_names
        assert "DevOps Engineer" in cat_names

        for c in cats:
            assert c["count"] > 0

    def test_get_skills_endpoint(self, client):
        """Test GET /api/jobs/skills returns distinct skills with occurrence counts."""
        resp = client.get("/api/jobs/skills")
        assert resp.status_code == 200
        skills = resp.json()

        assert len(skills) > 10
        skill_names = [s["skill"] for s in skills]
        assert "Python" in skill_names
        assert "Git" in skill_names

    def test_search_jobs_endpoint(self, client):
        """Test GET /api/jobs/search endpoint."""
        resp = client.get("/api/jobs/search?q=Python")
        assert resp.status_code == 200
        results = resp.json()

        assert len(results) > 0
        for r in results:
            text_corpus = f"{r['title']} {r['company']} {r['category']} {r['description']} {r.get('location', '')}".lower()
            assert "python" in text_corpus or any("python" in s.lower() for s in r["required_skills"])

    def test_get_stats_endpoint(self, client):
        """Test GET /api/jobs/stats returns dataset statistics."""
        resp = client.get("/api/jobs/stats")
        assert resp.status_code == 200
        stats = resp.json()

        assert stats["total_jobs"] >= 200
        assert stats["total_categories"] >= 15
        assert len(stats["categories"]) >= 15
        assert "Entry-level" in stats["experience_levels"]
        assert "Remote" in stats["work_modes"]
        assert "Full-time" in stats["employment_types"]
        assert len(stats["top_locations"]) > 0
        assert len(stats["top_skills"]) > 0

    def test_seed_api_endpoint(self, client):
        """Test POST /api/jobs/seed triggers safe database re-synchronization."""
        resp = client.post("/api/jobs/seed")
        assert resp.status_code == 200
        data = resp.json()

        assert "Job dataset successfully synchronized" in data["message"]
        assert data["total_in_db"] >= 200
        assert data["inserted"] == 0  # Idempotent re-seed should not create duplicates

    def test_job_responsibilities_and_date_posted(self, client):
        """Test that jobs contain structured responsibilities list and date_posted."""
        resp = client.get("/api/jobs?limit=5")
        assert resp.status_code == 200
        jobs = resp.json()["jobs"]

        for j in jobs:
            assert "responsibilities" in j
            assert isinstance(j["responsibilities"], list) and len(j["responsibilities"]) > 0
            assert "date_posted" in j and j["date_posted"] is not None

    def test_get_jobs_location_filter(self, client):
        """Test filtering jobs by location keyword."""
        resp = client.get("/api/jobs?location=Bengaluru")
        assert resp.status_code == 200
        data = resp.json()

        assert len(data["jobs"]) > 0
        for j in data["jobs"]:
            assert "Bengaluru" in j["location"]

    def test_required_categories_presence(self, client):
        """Verify all categories including Database Administrator, UI/UX Designer, Software Developer exist."""
        resp = client.get("/api/jobs/categories")
        assert resp.status_code == 200
        cats = [c["category"] for c in resp.json()]

        required = [
            "Software Developer", "Python Developer", "Java Developer",
            "Full Stack Developer", "Frontend Developer", "Backend Developer",
            "Data Analyst", "Data Scientist", "Machine Learning Engineer",
            "AI Engineer", "DevOps Engineer", "Cloud Engineer",
            "Cybersecurity Analyst", "Database Administrator", "UI/UX Designer"
        ]

        for req in required:
            assert req in cats, f"Required category '{req}' not found in categories endpoint"

