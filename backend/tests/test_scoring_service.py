"""
Tests for ScoringService and Phase 8 Integration Endpoints.
"""

import pytest
from app.services.scoring_service import ScoringService


@pytest.fixture
def scoring_service():
    return ScoringService()


def test_calculate_skill_score_empty(scoring_service):
    assert scoring_service.calculate_skill_score(None) == 0.0
    assert scoring_service.calculate_skill_score([]) == 0.0
    assert scoring_service.calculate_skill_score({}) == 0.0


def test_calculate_skill_score_valid(scoring_service):
    skills_data = {
        "categorized_skills": {
            "Programming Languages": ["Python", "JavaScript", "C++"],
            "Frameworks": ["FastAPI", "React"],
            "Databases": ["PostgreSQL", "MongoDB"],
            "Cloud & DevOps": ["Docker", "AWS", "Git"]
        }
    }
    score = scoring_service.calculate_skill_score(skills_data)
    assert score >= 50.0
    assert score <= 100.0


def test_calculate_projects_score_empty(scoring_service):
    assert scoring_service.calculate_projects_score([]) == 0.0
    assert scoring_service.calculate_projects_score(None) == 0.0


def test_calculate_projects_score_valid(scoring_service):
    projects = [
        {
            "name": "E-Commerce System",
            "description": "Developed a full-stack platform with high-volume transaction processing and payment integration.",
            "technologies": ["Python", "FastAPI", "React", "PostgreSQL"]
        },
        {
            "name": "AI Resume Screener",
            "description": "Built an intelligent applicant screening engine using NLP, TF-IDF cosine similarity, and skill taxonomy.",
            "technologies": ["Python", "scikit-learn", "NLTK", "FastAPI"]
        }
    ]
    score = scoring_service.calculate_projects_score(projects)
    assert score >= 60.0
    assert score <= 100.0


def test_calculate_experience_score(scoring_service):
    assert scoring_service.calculate_experience_score([]) == 0.0

    exp = [
        {
            "title": "Software Engineer Intern",
            "company": "Tech Corp",
            "duration": "June 2024 - August 2024",
            "description": "Engineered microservices and optimized API throughput by 25%."
        }
    ]
    score = scoring_service.calculate_experience_score(exp)
    assert score >= 50.0
    assert score <= 100.0


def test_calculate_education_score(scoring_service):
    assert scoring_service.calculate_education_score([]) == 0.0

    edu = [
        {
            "degree": "B.Tech in Computer Science",
            "institution": "National Institute of Technology",
            "graduation_year": "2025",
            "cgpa": "8.8"
        }
    ]
    score = scoring_service.calculate_education_score(edu)
    assert score == 100.0


def test_calculate_completeness_score(scoring_service):
    incomplete = {
        "profile": {
            "name": "John Doe"
        }
    }
    assert scoring_service.calculate_completeness_score(incomplete) == 10.0

    complete = {
        "profile": {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "+91-9876543210",
            "education": [{"degree": "B.Tech"}],
            "skills": {"programming_languages": ["Python"]},
            "projects": [{"name": "AI App"}],
            "experience": [{"title": "Intern"}],
            "certifications": ["AWS Cloud Practitioner"]
        }
    }
    assert scoring_service.calculate_completeness_score(complete) == 100.0


def test_calculate_resume_score_composite(scoring_service):
    resume_data = {
        "profile": {
            "name": "Alex Taylor",
            "email": "alex@example.com",
            "phone": "+1-555-0199",
            "education": [
                {
                    "degree": "B.S. in Computer Science",
                    "institution": "University of Tech",
                    "graduation_year": "2024",
                    "cgpa": "3.8/4.0"
                }
            ],
            "experience": [
                {
                    "title": "Junior Developer",
                    "company": "Cloud Inc",
                    "duration": "2023 - 2024",
                    "description": "Maintained and tested backend endpoints with PyTest and Docker."
                }
            ],
            "projects": [
                {
                    "name": "Portfolio Website",
                    "description": "Responsive personal website featuring live deployment and analytics.",
                    "technologies": ["React", "Tailwind CSS"]
                }
            ],
            "skills": ["Python", "FastAPI", "React", "Docker", "Git"],
            "certifications": ["AWS Certified Developer"]
        },
        "skills_analysis": {
            "categorized_skills": {
                "Programming Languages": ["Python"],
                "Frameworks": ["FastAPI", "React"],
                "Cloud & DevOps": ["Docker", "Git"]
            }
        }
    }

    scores = scoring_service.calculate_resume_score(resume_data)
    assert "overall" in scores
    assert "skills" in scores
    assert "projects" in scores
    assert "experience" in scores
    assert "education" in scores
    assert "completeness" in scores
    assert 50.0 <= scores["overall"] <= 100.0


def test_get_improvement_suggestions_freshman(scoring_service):
    fresher = {
        "profile": {
            "name": "New Student",
            "email": "student@college.edu",
            "education": [{"degree": "B.E. CS"}],
            "experience": [],
            "projects": [],
            "certifications": []
        }
    }
    scores = scoring_service.calculate_resume_score(fresher)
    suggestions = scoring_service.get_improvement_suggestions(fresher, scores)

    categories = [s["category"] for s in suggestions]
    assert "Work Experience" in categories
    assert "Projects" in categories
    assert "Certifications" in categories


def test_api_dashboard_stats(test_client):
    response = test_client.get("/api/resume/dashboard-stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_resumes" in data
    assert "total_jobs" in data
    assert "avg_resume_score" in data
    assert "total_skills_catalog" in data
    assert "category_distribution" in data
    assert "experience_distribution" in data
    assert "recent_resumes" in data
    assert isinstance(data["recent_resumes"], list)


def test_api_history(test_client):
    response = test_client.get("/api/resume/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "resumes" in data
    assert isinstance(data["resumes"], list)


def test_api_improvements_with_db_record(test_client):
    # Fetch first resume from history to get valid ID
    h_res = test_client.get("/api/resume/history?limit=1")
    assert h_res.status_code == 200
    history_data = h_res.json()
    if history_data["total"] > 0:
        first_id = history_data["resumes"][0]["file_id"]
        imp_res = test_client.get(f"/api/resume/improvements/{first_id}")
        assert imp_res.status_code == 200
        imp_data = imp_res.json()
        assert "scores" in imp_data
        assert "suggestions" in imp_data
        assert "profile_summary" in imp_data
        assert "overall" in imp_data["scores"]
