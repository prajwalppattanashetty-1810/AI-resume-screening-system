"""
Unit and API Integration Tests for Phase 7: Skill Gap Analysis & Personalized Learning Recommendations.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.skill_gap_service import SkillGapService, VERIFIED_RESOURCES
from app.models.database import SessionLocal, Job, ResumeAnalysis

client = TestClient(app)


# ============================================================================
# 1. UNIT TESTS: SKILL GAP SERVICE
# ============================================================================

class TestSkillGapMatching:
    """Tests core skill comparison, classification, and metrics."""

    def setup_method(self):
        self.service = SkillGapService()

    def test_complete_skill_matching(self):
        """Test candidate who possesses all required and preferred skills."""
        candidate_skills = ["Python", "TensorFlow", "Pandas", "Scikit-Learn", "Git"]
        required_skills = ["Python", "TensorFlow", "Pandas"]
        preferred_skills = ["Git", "Scikit-learn"]

        result = self.service.analyze_skill_gap(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            job_title="ML Engineer",
            job_exp_level="Entry-level"
        )

        metrics = result["metrics"]
        assert metrics["total_required"] == 3
        assert metrics["matched_required"] == 3
        assert metrics["partial_required"] == 0
        assert metrics["missing_required"] == 0
        assert metrics["required_match_percentage"] == 100.0
        assert metrics["preferred_coverage_percentage"] == 100.0
        assert metrics["overall_coverage_percentage"] == 100.0
        assert len(result["missing_skills"]) == 0
        # No high-priority recommendations needed when all required are matched
        high_recs = [r for r in result["learning_recommendations"] if r["priority"] == "High"]
        assert len(high_recs) == 0

    def test_partial_matching_via_transferable_skills(self):
        """Test transferable skill credit (e.g. candidate has TensorFlow, job requires PyTorch)."""
        candidate_skills = ["Python", "TensorFlow", "Pandas"]
        required_skills = ["PyTorch", "Python"]  # PyTorch is transferable from TensorFlow

        result = self.service.analyze_skill_gap(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            preferred_skills=[],
            job_title="Deep Learning Specialist",
            job_exp_level="Entry-level"
        )

        metrics = result["metrics"]
        assert metrics["total_required"] == 2
        assert metrics["matched_required"] == 1  # Python
        assert metrics["partial_required"] == 1  # PyTorch
        assert metrics["missing_required"] == 0
        assert "PyTorch" in result["partial_skills"]

        # Check required match % = (1 + 0.5 * 1) / 2 * 100 = 75.0%
        assert metrics["required_match_percentage"] == 75.0

        # Partial required skill should generate Medium priority recommendation
        medium_recs = [r for r in result["learning_recommendations"] if r["skill_name"] == "PyTorch"]
        assert len(medium_recs) == 1
        assert medium_recs[0]["priority"] == "Medium"
        assert "TensorFlow" in medium_recs[0]["reason"]

    def test_partial_matching_via_proficiency_gap(self):
        """Test senior job requiring advanced experience when candidate is beginner."""
        candidate_skills = [
            {
                "name": "Python",
                "proficiency": "Beginner",
                "evidence": ["Listed in skills section"]
            }
        ]
        required_skills = ["Python"]

        result = self.service.analyze_skill_gap(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            job_title="Senior Python Architect",
            job_exp_level="Senior"
        )

        metrics = result["metrics"]
        assert metrics["partial_required"] == 1
        assert metrics["matched_required"] == 0
        assert "Python" in result["partial_skills"]
        # Required match % = (0 + 0.5 * 1) / 1 * 100 = 50.0%
        assert metrics["required_match_percentage"] == 50.0

    def test_missing_skill_detection(self):
        """Test detection of completely missing skills."""
        candidate_skills = ["HTML", "CSS", "JavaScript"]
        required_skills = ["Docker", "Kubernetes", "AWS"]

        result = self.service.analyze_skill_gap(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            preferred_skills=["Terraform"],
            job_title="Cloud DevOps Engineer"
        )

        metrics = result["metrics"]
        assert metrics["matched_required"] == 0
        assert metrics["missing_required"] == 3
        assert metrics["required_match_percentage"] == 0.0
        assert set(result["missing_skills"]) == {"Docker", "Kubernetes", "AWS", "Terraform"}

        # Missing required skills must have High priority
        high_recs = [r for r in result["learning_recommendations"] if r["priority"] == "High"]
        assert len(high_recs) == 3
        assert {r["skill_name"] for r in high_recs} == {"Docker", "Kubernetes", "AWS"}

        # Missing preferred skill must have Low priority
        low_recs = [r for r in result["learning_recommendations"] if r["priority"] == "Low"]
        assert len(low_recs) == 1
        assert low_recs[0]["skill_name"] == "Terraform"

    def test_case_insensitive_and_alias_normalization(self):
        """Test case differences, acronyms, and alias variations."""
        candidate_skills = ["py", "js", "postgres", "sklearn", "reactjs"]
        required_skills = ["PYTHON", "JavaScript", "PostgreSQL", "Scikit-Learn", "React"]

        result = self.service.analyze_skill_gap(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            job_title="Full Stack Developer"
        )

        metrics = result["metrics"]
        assert metrics["total_required"] == 5
        assert metrics["matched_required"] == 5
        assert metrics["missing_required"] == 0
        assert metrics["required_match_percentage"] == 100.0

    def test_duplicate_skill_handling(self):
        """Test duplicates in candidate skills or job skills are safely consolidated."""
        candidate_skills = ["Python", "python", "Python", "PYTHON", "Django"]
        required_skills = ["Python", "Python", "Django", "Django"]

        result = self.service.analyze_skill_gap(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            job_title="Backend Engineer"
        )

        metrics = result["metrics"]
        assert metrics["total_required"] == 2
        assert metrics["matched_required"] == 2
        assert metrics["required_match_percentage"] == 100.0

    def test_empty_resume_skills(self):
        """Test graceful handling of empty resume skills."""
        result = self.service.analyze_skill_gap(
            candidate_skills=[],
            required_skills=["Python", "FastAPI"],
            preferred_skills=["Docker"],
            job_title="Junior Developer"
        )

        metrics = result["metrics"]
        assert metrics["total_required"] == 2
        assert metrics["matched_required"] == 0
        assert metrics["missing_required"] == 2
        assert metrics["required_match_percentage"] == 0.0
        assert metrics["overall_coverage_percentage"] == 0.0
        assert len(result["learning_recommendations"]) == 3

    def test_empty_job_requirements(self):
        """Test graceful handling of job with zero required skills."""
        result = self.service.analyze_skill_gap(
            candidate_skills=["Python", "SQL"],
            required_skills=[],
            preferred_skills=[],
            job_title="General Tech Role"
        )

        metrics = result["metrics"]
        assert metrics["total_required"] == 0
        assert metrics["required_match_percentage"] == 100.0
        assert metrics["overall_coverage_percentage"] == 100.0
        assert len(result["missing_skills"]) == 0
        assert len(result["learning_recommendations"]) == 0

    def test_coverage_formula_calculations(self):
        """Verify the exact mathematical coverage formulas."""
        # 4 required: 2 matched, 1 partial, 1 missing -> (2 + 0.5*1)/4 = 2.5/4 = 62.5%
        # 2 preferred: 1 matched, 1 missing -> (1 + 0)/2 = 50.0%
        # Overall = 0.75 * 62.5 + 0.25 * 50.0 = 46.875 + 12.5 = 59.375 -> 59.4%
        candidate_skills = ["Python", "SQL", "TensorFlow"]  # PyTorch will be partial from TensorFlow
        required_skills = ["Python", "SQL", "PyTorch", "Kubernetes"]
        preferred_skills = ["Git", "AWS"]  # Let's say candidate doesn't have Git or AWS, but wait:
        candidate_skills.append("Git")  # Matched preferred: Git

        result = self.service.analyze_skill_gap(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            job_title="MLOps Engineer"
        )

        metrics = result["metrics"]
        assert metrics["required_match_percentage"] == 62.5
        assert metrics["preferred_coverage_percentage"] == 50.0
        assert metrics["overall_coverage_percentage"] == 59.4

    def test_learning_recommendation_contents_and_verified_urls(self):
        """Verify learning roadmap structure and official documentation URL validity."""
        candidate_skills = ["Python"]
        required_skills = ["Docker", "PyTorch"]
        preferred_skills = ["CustomNonExistentSkill"]

        result = self.service.analyze_skill_gap(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            job_title="AI Research Engineer"
        )

        recs = result["learning_recommendations"]
        assert len(recs) == 3

        # Docker recommendation
        docker_rec = next(r for r in recs if r["skill_name"] == "Docker")
        assert docker_rec["priority"] == "High"
        assert len(docker_rec["learning_topics"]) >= 3
        assert len(docker_rec["project_ideas"]) >= 1
        assert "1-2 weeks" in docker_rec["estimated_duration"]
        assert len(docker_rec["resources"]) > 0
        assert docker_rec["resources"][0]["url"] == VERIFIED_RESOURCES["Docker"]["url"]

        # Unknown skill fallback (must not invent broken URLs)
        custom_rec = next(r for r in recs if r["skill_name"] == "Customnonexistentskill")
        assert custom_rec["resources"][0]["url"] is None


# ============================================================================
# 2. API INTEGRATION TESTS: /api/skill-gap/analyze
# ============================================================================

class TestSkillGapAPI:
    """Tests the FastAPI routes for skill gap analysis."""

    def test_analyze_with_candidate_skills_override(self):
        """POST /api/skill-gap/analyze with direct candidate_skills payload."""
        db = SessionLocal()
        try:
            job = db.query(Job).first()
            job_id = job.job_id if job else "1"
        finally:
            db.close()

        payload = {
            "job_id": job_id,
            "candidate_skills": ["Python", "TensorFlow", "Pandas"]
        }
        response = client.post("/api/skill-gap/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert "metrics" in data
        assert "required_skills_analysis" in data
        assert "learning_recommendations" in data

    def test_analyze_with_file_id_from_db(self):
        """POST /api/skill-gap/analyze using real SQLite ResumeAnalysis record."""
        # Find any existing resume record in database
        db = SessionLocal()
        try:
            resume = db.query(ResumeAnalysis).first()
            job = db.query(Job).first()
            if not resume or not job:
                pytest.skip("No existing resume or job in DB to test file_id resolution")

            payload = {
                "file_id": resume.file_id,
                "job_id": job.job_id
            }
            response = client.post("/api/skill-gap/analyze", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["job_id"] == job.job_id
            assert data["metrics"]["total_required"] >= 0
            assert isinstance(data["learning_recommendations"], list)
        finally:
            db.close()

    def test_analyze_invalid_file_id_returns_404(self):
        """POST /api/skill-gap/analyze with non-existent file_id returns 404."""
        payload = {
            "file_id": "non-existent-uuid-12345",
            "job_id": "JOB-ML-001"
        }
        response = client.post("/api/skill-gap/analyze", json=payload)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_analyze_invalid_job_id_returns_404(self):
        """POST /api/skill-gap/analyze with non-existent job_id returns 404."""
        payload = {
            "job_id": "NON-EXISTENT-JOB-9999",
            "candidate_skills": ["Python"]
        }
        response = client.post("/api/skill-gap/analyze", json=payload)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_analyze_missing_identifiers_returns_400(self):
        """POST /api/skill-gap/analyze without file_id or candidate_skills returns 400."""
        payload = {
            "job_id": "JOB-ML-001"
        }
        response = client.post("/api/skill-gap/analyze", json=payload)
        assert response.status_code == 400
        assert "file_id" in response.json()["detail"]

    def test_get_convenience_endpoint(self):
        """GET /api/skill-gap/analyze/{file_id}/{job_id}."""
        db = SessionLocal()
        try:
            resume = db.query(ResumeAnalysis).first()
            job = db.query(Job).first()
            if not resume or not job:
                pytest.skip("No existing resume or job in DB to test GET endpoint")

            response = client.get(f"/api/skill-gap/analyze/{resume.file_id}/{job.job_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["job_id"] == job.job_id
            assert "metrics" in data
        finally:
            db.close()

    def test_skills_analyze_backward_compatibility(self):
        """POST /api/skills/analyze returns SkillGapAnalysis schema."""
        payload = {
            "resume_skills": ["Python", "Flask"],
            "job_skills": ["Python", "FastAPI", "Docker"]
        }
        response = client.post("/api/skills/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "matched_skills" in data
        assert "missing_skills" in data
        assert "partial_skills" in data
        assert "learning_recommendations" in data
        assert "Python" in data["matched_skills"]
