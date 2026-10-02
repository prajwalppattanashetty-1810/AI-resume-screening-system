"""
Comprehensive Unit Tests for Phase 4: Skill Extraction Engine.
"""

import pytest
import os
from app.services.skill_extraction_service import SkillExtractionService, SKILL_TAXONOMY
from app.services.skill_service import SkillService
from app.models.database import ResumeAnalysis, get_db

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")


@pytest.fixture
def skill_service():
    return SkillExtractionService()


# ============================================================================
# 1. Skill Extraction & Normalization
# ============================================================================

def test_skill_extraction_from_text(skill_service):
    """Should extract known skills from text."""
    text = "We are seeking a developer proficient in Python, React, PostgreSQL, and Docker."
    skills = skill_service.extract_skills_from_text(text)
    names = [s[0] for s in skills]

    assert "Python" in names
    assert "React" in names
    assert "PostgreSQL" in names
    assert "Docker" in names


def test_skill_normalization(skill_service):
    """Should normalize casing to canonical taxonomy name."""
    assert skill_service.normalize_skill("python") == "Python"
    assert skill_service.normalize_skill("REACT") == "React"
    assert skill_service.normalize_skill("docker") == "Docker"
    assert skill_service.normalize_skill("mongodb") == "MongoDB"
    assert skill_service.normalize_skill("PostgreSQL") == "PostgreSQL"


def test_alias_detection(skill_service):
    """Should resolve common tech aliases to canonical names."""
    assert skill_service.normalize_skill("js") == "JavaScript"
    assert skill_service.normalize_skill("ts") == "TypeScript"
    assert skill_service.normalize_skill("ReactJS") == "React"
    assert skill_service.normalize_skill("react.js") == "React"
    assert skill_service.normalize_skill("nodejs") == "Node.js"
    assert skill_service.normalize_skill("sklearn") == "Scikit-learn"
    assert skill_service.normalize_skill("scikitlearn") == "Scikit-learn"
    assert skill_service.normalize_skill("postgre") == "PostgreSQL"
    assert skill_service.normalize_skill("postgres") == "PostgreSQL"
    assert skill_service.normalize_skill("ml") == "Machine Learning"
    assert skill_service.normalize_skill("dl") == "Deep Learning"
    assert skill_service.normalize_skill("k8s") == "Kubernetes"
    assert skill_service.normalize_skill("golang") == "Go"


# ============================================================================
# 2. Skill Categorization
# ============================================================================

def test_skill_categorization(skill_service):
    """Every extracted skill must be assigned to its correct category."""
    assert skill_service.get_skill_category("Python") == "programming_languages"
    assert skill_service.get_skill_category("C++") == "programming_languages"
    assert skill_service.get_skill_category("React") == "frontend"
    assert skill_service.get_skill_category("Tailwind CSS") == "frontend"
    assert skill_service.get_skill_category("FastAPI") == "backend"
    assert skill_service.get_skill_category("Django") == "backend"
    assert skill_service.get_skill_category("PostgreSQL") == "databases"
    assert skill_service.get_skill_category("MongoDB") == "databases"
    assert skill_service.get_skill_category("Scikit-learn") == "machine_learning"
    assert skill_service.get_skill_category("TensorFlow") == "machine_learning"
    assert skill_service.get_skill_category("AWS") == "cloud_devops"
    assert skill_service.get_skill_category("Docker") == "cloud_devops"
    assert skill_service.get_skill_category("Git") == "development_tools"
    assert skill_service.get_skill_category("VS Code") == "development_tools"
    assert skill_service.get_skill_category("Problem Solving") == "soft_skills"
    assert skill_service.get_skill_category("Leadership") == "soft_skills"


# ============================================================================
# 3. Duplicate Removal & Short Skills (C, R, Go)
# ============================================================================

def test_duplicate_removal(skill_service):
    """Should eliminate duplicate skills regardless of case or alias."""
    profile = {
        "skills": "Python, python, PYTHON, py, JavaScript, JS",
        "projects": [
            {"name": "App", "technologies": ["Python", "JavaScript"]}
        ]
    }
    result = skill_service.extract_skills_from_profile(profile)
    names = [s["name"] for s in result["skills"]]

    assert names.count("Python") == 1
    assert names.count("JavaScript") == 1
    assert result["total_skills"] == 2


def test_short_skill_detection_and_boundaries(skill_service):
    """Should accurately detect single-letter languages C and R without false positives."""
    text = "Programming with C, C++, Python, and R. Vitamin C is healthy. Looking for a car."
    skills = skill_service.extract_skills_from_text(text)
    names = [s[0] for s in skills]

    assert "C" in names
    assert "C++" in names
    assert "R" in names
    assert "Python" in names

    # False-positive prevention: "car" should not match "C" or "R", nor should lower "c"
    assert "Car" not in names


def test_false_positive_prevention(skill_service):
    """Ordinary English prose should not trigger skill extraction."""
    prose = "The candidate is responsible for managing day-to-day administrative tasks and writing reports."
    skills = skill_service.extract_skills_from_text(prose)
    names = [s[0] for s in skills]

    assert len(names) == 0


# ============================================================================
# 4. Extraction from Projects & Experience
# ============================================================================

def test_extraction_from_project_descriptions(skill_service):
    """Should detect skills mentioned inside project narrative text."""
    profile = {
        "skills": "",
        "projects": [
            {
                "name": "E-Commerce System",
                "description": "Implemented microservices using FastAPI and deployed with Kubernetes.",
                "technologies": ["PostgreSQL"]
            }
        ]
    }
    result = skill_service.extract_skills_from_profile(profile)
    names = [s["name"] for s in result["skills"]]

    assert "FastAPI" in names
    assert "Kubernetes" in names
    assert "PostgreSQL" in names


def test_extraction_from_experience_descriptions(skill_service):
    """Should detect skills used in work experience bullet points."""
    profile = {
        "skills": "",
        "experience": [
            {
                "title": "Software Intern",
                "company": "Tech Corp",
                "description": "Automated data pipelines with Apache Kafka and Docker on AWS cloud."
            }
        ]
    }
    result = skill_service.extract_skills_from_profile(profile)
    names = [s["name"] for s in result["skills"]]

    assert "Docker" in names
    assert "AWS" in names
    assert "Kafka" in names


# ============================================================================
# 5. Evidence-Based Proficiency Scoring
# ============================================================================

def test_proficiency_evidence_classification(skill_service):
    """Should correctly assign Beginner, Intermediate, and Advanced based on source evidence."""
    profile = {
        "skills": "Python, React, AWS",
        "projects": [
            {
                "name": "Chatbot",
                "description": "Built using React and Node.js",
                "technologies": ["React"]
            }
        ],
        "experience": [
            {
                "title": "Backend Engineer",
                "company": "Cloud Co",
                "description": "Architected distributed services in Python and Docker."
            }
        ]
    }
    result = skill_service.extract_skills_from_profile(profile)
    skills_by_name = {s["name"]: s for s in result["skills"]}

    # Python: Used in experience -> Advanced
    assert skills_by_name["Python"]["proficiency"] == "Advanced"
    assert "experience" in skills_by_name["Python"]["sources"]

    # React: Used in projects -> Intermediate
    assert skills_by_name["React"]["proficiency"] == "Intermediate"
    assert "projects" in skills_by_name["React"]["sources"]

    # AWS: Only listed in skills section -> Beginner
    assert skills_by_name["AWS"]["proficiency"] == "Beginner"
    assert skills_by_name["AWS"]["sources"] == ["skills_section"]


# ============================================================================
# 6. SkillService Wrapper Verification
# ============================================================================

def test_skill_service_matching():
    """Verify SkillService matching and gap detection."""
    service = SkillService()
    candidate = ["Python", "JS", "Docker", "postgres"]
    job_required = ["Python", "JavaScript", "Kubernetes", "PostgreSQL", "AWS"]

    match_result = service.match_skills(candidate, job_required)

    assert "Python" in match_result["matched"]
    assert "JavaScript" in match_result["matched"]
    assert "PostgreSQL" in match_result["matched"]
    assert "Kubernetes" in match_result["missing"]
    assert "AWS" in match_result["missing"]


# ============================================================================
# 7. API Endpoint Verification (POST /api/resume/extract-skills)
# ============================================================================

def test_extract_skills_api_with_payload(test_client):
    """POST /api/resume/extract-skills with structured profile payload."""
    payload = {
        "profile": {
            "name": "Jane Doe",
            "skills": "Python, React, Docker, SQL",
            "projects": [
                {
                    "name": "AI App",
                    "description": "Built using PyTorch and FastAPI",
                    "technologies": ["PyTorch"]
                }
            ],
            "experience": []
        }
    }
    response = test_client.post("/api/resume/extract-skills", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["total_skills"] >= 5
    assert "programming_languages" in data["categorized_skills"]
    assert "Python" in data["categorized_skills"]["programming_languages"]
    assert "React" in data["categorized_skills"]["frontend"]


def test_extract_skills_api_with_uploaded_file(test_client):
    """POST /api/resume/extract-skills with uploaded file_id."""
    pdf_path = os.path.join(TEST_DATA_DIR, "sample_resume.pdf")
    with open(pdf_path, "rb") as f:
        files = {"file": ("sample_resume.pdf", f, "application/pdf")}
        upload_resp = test_client.post("/api/resume/upload", files=files)

    assert upload_resp.status_code == 200
    file_id = upload_resp.json()["file_id"]

    # Call extract-skills with file_id
    response = test_client.post(
        "/api/resume/extract-skills",
        json={"file_id": file_id}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["file_id"] == file_id
    assert data["total_skills"] > 10
    assert len(data["skills"]) == data["total_skills"]

    # Verify proficiency and evidence fields exist on items
    first_skill = data["skills"][0]
    assert "proficiency" in first_skill
    assert "proficiency_reason" in first_skill
    assert "sources" in first_skill
