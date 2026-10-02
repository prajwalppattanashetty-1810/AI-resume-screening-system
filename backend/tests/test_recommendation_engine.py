"""
Comprehensive Unit and Integration Tests for Phase 6: AI Job Recommendation Engine.

Tests:
1. TF-IDF vectorization
2. Cosine similarity calculation
3. Identical resume and job descriptions (similarity near 1.0)
4. Completely unrelated documents (similarity near 0.0)
5. Skill-based matching & alias normalization
6. Missing required skills & preferred skill matches
7. Empty resume handling (graceful fallback)
8. Empty jobs dataset handling (safe empty response)
9. Combined score computation (70% TF-IDF / 30% Skill)
10. Category filtering
11. Location filtering
12. Recommendation ranking (descending order)
13. API endpoint POST /api/jobs/recommend with file_id
14. API endpoint POST /api/jobs/recommend with raw text & skills
15. API endpoint validation (404 on missing file_id, 400 on empty request)
16. Explainable recommendation text generation
"""

import pytest
import os
import json
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import SessionLocal, Job, ResumeAnalysis, create_tables
from app.ml.recommender import JobRecommender
from app.ml.feature_extractor import FeatureExtractor
from app.schemas.job import RecommendationRequest
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


@pytest.fixture
def sample_jobs():
    return [
        {
            "id": 1,
            "job_id": "JOB-ML-001",
            "title": "Machine Learning Engineer",
            "company": "DataPulse AI Systems (Sample)",
            "category": "Machine Learning Engineer",
            "description": "Design, develop, and deploy scalable machine learning and deep learning pipelines in Python using PyTorch and Scikit-learn.",
            "required_skills": ["Python", "Machine Learning", "PyTorch", "Scikit-learn"],
            "preferred_skills": ["Docker", "AWS", "MLflow"],
            "responsibilities": ["Train neural network architectures", "Optimize model inference latency"],
            "education": "Bachelor's in Computer Science",
            "location": "Bengaluru, Karnataka",
            "work_mode": "Hybrid",
            "experience_level": "Junior"
        },
        {
            "id": 2,
            "job_id": "JOB-FED-002",
            "title": "Senior Frontend Developer",
            "company": "PixelCraft Studios (Demo)",
            "category": "Frontend Developer",
            "description": "Build high-performance web applications using React, TypeScript, Tailwind CSS, and Next.js.",
            "required_skills": ["React", "TypeScript", "JavaScript", "Tailwind CSS"],
            "preferred_skills": ["Next.js", "Redux", "Figma"],
            "responsibilities": ["Develop reusable component systems", "Optimize core web vitals"],
            "education": "Bachelor's in Software Engineering",
            "location": "Remote - India",
            "work_mode": "Remote",
            "experience_level": "Senior"
        },
        {
            "id": 3,
            "job_id": "JOB-CYB-003",
            "title": "Cybersecurity Analyst",
            "company": "Aegis Cyber Defense (Sample)",
            "category": "Cybersecurity Analyst",
            "description": "Monitor security event logs, perform vulnerability scans, and investigate incident response playbooks.",
            "required_skills": ["Linux", "Networking", "Security", "Python"],
            "preferred_skills": ["Wireshark", "SIEM", "Firewalls"],
            "responsibilities": ["Analyze SOC security alarms", "Execute penetration tests"],
            "education": "Bachelor's in Cybersecurity or IT",
            "location": "Hyderabad, Telangana",
            "work_mode": "On-site",
            "experience_level": "Intermediate"
        }
    ]


class TestTFIDFAndCosineSimilarity:
    def test_feature_extractor_tfidf(self):
        """Test FeatureExtractor fits and transforms corpus."""
        extractor = FeatureExtractor()
        corpus = [
            "Python machine learning scikit-learn deep learning",
            "React JavaScript frontend CSS Tailwind TypeScript",
            "Cybersecurity networking penetration testing Linux"
        ]
        extractor.fit_tfidf(corpus)
        assert extractor.is_fitted
        features = extractor.get_feature_names()
        assert len(features) > 0
        assert "python" in features or "learning" in features

        vec = extractor.transform_tfidf("Python machine learning")
        assert vec.shape[0] == 1

    def test_identical_documents_cosine_similarity(self):
        """Identical texts must produce a cosine similarity near 1.0."""
        recommender = JobRecommender()
        doc = "Python developer building FastAPI microservices and PostgreSQL databases with Docker and Redis."
        job = {"id": 1, "title": "Python Developer", "category": "Python Developer", "description": doc, "required_skills": [], "preferred_skills": [], "responsibilities": []}
        recommender.fit([job])

        # Testing with the exact text representation
        exact_text = recommender.job_texts[0]
        resume_vec = recommender.vectorizer.transform([exact_text])
        sim = recommender.calculate_cosine_similarity(resume_vec, recommender.job_tfidf_matrix[0])
        assert sim >= 0.99, f"Expected similarity >= 0.99 for identical documents, got {sim}"

    def test_completely_unrelated_documents_cosine_similarity(self):
        """Completely orthogonal texts must produce a cosine similarity near 0.0."""
        recommender = JobRecommender()
        doc_job = "Kubernetes Docker Terraform AWS Cloud DevOps infrastructure configuration."
        doc_unrelated = "Delicious Italian pizza recipe baking fresh dough tomato basil mozzarella parmesan."

        recommender.fit([{"id": 1, "title": "DevOps", "category": "DevOps", "description": doc_job, "required_skills": [], "preferred_skills": [], "responsibilities": []}])

        unrelated_vec = recommender.vectorizer.transform([doc_unrelated])
        sim = recommender.calculate_cosine_similarity(unrelated_vec, recommender.job_tfidf_matrix[0])
        assert sim <= 0.05, f"Expected similarity near 0.0 for unrelated documents, got {sim}"


class TestSkillMatchingEngine:
    def test_skill_match_exact_and_aliases(self):
        """Test skill match handles alias normalization (e.g. Postgres -> PostgreSQL)."""
        recommender = JobRecommender()
        candidate_skills = ["python", "pytorch", "scikit learn", "postgres"]
        required_skills = ["Python", "PyTorch", "PostgreSQL", "Docker"]
        preferred_skills = ["Scikit-learn", "AWS"]

        matched_req, missing_req, matched_pref, match_pct = recommender.match_skills(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills
        )

        assert "Python" in matched_req
        assert "PyTorch" in matched_req
        assert "PostgreSQL" in matched_req
        assert "Docker" in missing_req
        assert "Scikit-learn" in matched_pref
        assert match_pct == 75.0  # 3 of 4 required matched

    def test_skill_match_zero_skills(self):
        """Test candidate with no matching skills."""
        recommender = JobRecommender()
        candidate_skills = ["HTML", "CSS"]
        required_skills = ["Python", "Machine Learning", "PyTorch"]

        matched_req, missing_req, matched_pref, match_pct = recommender.match_skills(
            candidate_skills=candidate_skills,
            required_skills=required_skills
        )

        assert len(matched_req) == 0
        assert len(missing_req) == 3
        assert match_pct == 0.0

    def test_skill_match_empty_required_skills(self):
        """If a job has no required skills, skill match should be 100%."""
        recommender = JobRecommender()
        matched_req, missing_req, matched_pref, match_pct = recommender.match_skills(
            candidate_skills=["Python"],
            required_skills=[]
        )
        assert match_pct == 100.0


class TestRecommendationRanking:
    def test_combined_scoring_and_ranking(self, sample_jobs):
        """Verify that ML candidate gets ML job ranked first with highest combined score."""
        recommender = JobRecommender(tfidf_weight=0.7, skill_weight=0.3)
        ml_resume = "Experienced Machine Learning Engineer with strong background in Python, PyTorch, Scikit-learn, and neural networks."
        ml_skills = ["Python", "Machine Learning", "PyTorch", "Scikit-learn", "Docker"]

        recs = recommender.recommend(
            resume_text=ml_resume,
            candidate_skills=ml_skills,
            jobs=sample_jobs,
            top_n=3
        )

        assert len(recs) == 3
        # First recommendation must be Machine Learning Engineer
        top_rec = recs[0]
        assert top_rec["title"] == "Machine Learning Engineer"
        assert top_rec["category"] == "Machine Learning Engineer"
        assert top_rec["match_score"] > recs[1]["match_score"]
        assert top_rec["skill_match_percentage"] == 100.0
        assert "Python" in top_rec["matched_skills"]
        assert "Docker" in top_rec["preferred_skill_matches"]

        # Assert descending sort order
        scores = [r["match_score"] for r in recs]
        assert scores == sorted(scores, reverse=True)

    def test_empty_resume_handling(self, sample_jobs):
        """Verify engine gracefully handles empty resume without crashing."""
        recommender = JobRecommender()
        recs = recommender.recommend(
            resume_text="",
            candidate_skills=[],
            jobs=sample_jobs,
            top_n=3
        )
        assert isinstance(recs, list)
        assert len(recs) == 3
        for r in recs:
            assert r["tfidf_similarity"] == 0.0
            assert r["skill_match_percentage"] == 0.0
            assert r["match_score"] == 0.0

    def test_empty_jobs_dataset(self):
        """Verify engine returns empty list if job dataset is empty."""
        recommender = JobRecommender()
        recs = recommender.recommend(
            resume_text="Experienced engineer",
            candidate_skills=["Python"],
            jobs=[],
            top_n=5
        )
        assert recs == []

    def test_category_and_location_filtering(self, sample_jobs):
        """Verify filtering by category and location in recommendation call."""
        recommender = JobRecommender()
        resume = "Software developer with Python, React, and Linux skills."
        skills = ["Python", "React", "Linux"]

        # Filter category = "Frontend Developer"
        cat_recs = recommender.recommend(
            resume_text=resume,
            candidate_skills=skills,
            jobs=sample_jobs,
            category_filter="Frontend Developer",
            top_n=5
        )
        assert len(cat_recs) == 1
        assert cat_recs[0]["category"] == "Frontend Developer"

        # Filter location = "Bengaluru"
        loc_recs = recommender.recommend(
            resume_text=resume,
            candidate_skills=skills,
            jobs=sample_jobs,
            location_filter="Bengaluru",
            top_n=5
        )
        assert len(loc_recs) == 1
        assert "Bengaluru" in loc_recs[0]["location"]


class TestRecommendationAPI:
    def test_recommend_with_raw_text_and_skills(self, client):
        """Test POST /api/jobs/recommend using raw text and skills payload."""
        payload = {
            "resume_text": "Experienced Python Data Scientist proficient in Pandas, Scikit-learn, SQL, and Machine Learning.",
            "skills": ["Python", "Pandas", "Scikit-learn", "SQL", "Machine Learning"],
            "top_n": 5,
            "tfidf_weight": 0.7,
            "skill_weight": 0.3
        }

        resp = client.post("/api/jobs/recommend", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert "recommendations" in data
        assert len(data["recommendations"]) == 5
        assert data["total_jobs_analyzed"] >= 200

        top = data["recommendations"][0]
        assert "job_id" in top
        assert "title" in top
        assert "company" in top
        assert "tfidf_similarity" in top
        assert "skill_match_percentage" in top
        assert "match_score" in top
        assert "matched_skills" in top
        assert "missing_skills" in top
        assert "explanation" in top
        assert len(top["explanation"]) > 10

        # Verify recommendations are strictly in descending score order
        scores = [r["match_score"] for r in data["recommendations"]]
        assert scores == sorted(scores, reverse=True)

    def test_recommend_with_file_id(self, client, db):
        """Test POST /api/jobs/recommend using an existing ResumeAnalysis file_id."""
        analysis_record = db.query(ResumeAnalysis).first()
        assert analysis_record is not None, "Need at least one ResumeAnalysis record"

        payload = {
            "file_id": analysis_record.file_id,
            "top_n": 4,
            "category": "Machine Learning Engineer"
        }

        resp = client.post("/api/jobs/recommend", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert len(data["recommendations"]) <= 4
        assert data["category_filter"] == "Machine Learning Engineer"
        for rec in data["recommendations"]:
            assert rec["category"] == "Machine Learning Engineer"

    def test_recommend_invalid_file_id_returns_404(self, client):
        """Test recommendation fails with 404 for nonexistent file_id."""
        payload = {"file_id": "nonexistent-uuid-99999"}
        resp = client.post("/api/jobs/recommend", json=payload)
        assert resp.status_code == 404

    def test_recommend_empty_request_returns_400(self, client):
        """Test recommendation fails with 400 when neither file_id nor resume_text is provided."""
        payload = {"top_n": 5}
        resp = client.post("/api/jobs/recommend", json=payload)
        assert resp.status_code == 400

    def test_recommend_explanation_generation(self, client):
        """Verify generated explanations are descriptive and include specific skills."""
        payload = {
            "resume_text": "Java backend engineer with Spring Boot, Hibernate, MySQL, and Docker experience.",
            "skills": ["Java", "Spring Boot", "Hibernate", "MySQL"],
            "top_n": 3
        }
        resp = client.post("/api/jobs/recommend", json=payload)
        assert resp.status_code == 200
        recs = resp.json()["recommendations"]

        for rec in recs:
            assert isinstance(rec["explanation"], str)
            assert len(rec["explanation"]) > 0
            if rec["matched_skills"]:
                assert any(s in rec["explanation"] for s in rec["matched_skills"][:2])
