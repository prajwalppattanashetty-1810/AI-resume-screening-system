"""
Comprehensive Integration Tests for Resume Parser and Skill Extraction Engine across different resume profiles.

Tests:
1. Resume with Education and Skills only (Student / Early-career).
2. Resume with Education, Projects, and Skills (Unnumbered projects, student portfolio).
3. Full Resume with Education, Work Experience, Projects, Certifications, and Skills.
4. Edge cases: C vs C++, JavaScript vs Java, candidate name with initials and dots.
"""

import pytest
from app.services.nlp_service import ResumeParser
from app.services.skill_extraction_service import SkillExtractionService


RESUME_EDUCATION_AND_SKILLS_ONLY = """
ANANYA ROY
Kolkata, West Bengal | +91 9123456780 | ananya.roy@email.com
LinkedIn: linkedin.com/in/ananyaroy

CAREER OBJECTIVE
First-year engineering student looking to develop strong foundations in computer science and software development.

EDUCATION
Bachelor of Technology in Information Technology
2023 - 2027
Heritage Institute of Technology, Kolkata
CGPA: 8.9/10

TECHNICAL SKILLS
Programming: Python, C, C++, Java
Web: HTML, CSS, JavaScript
Databases: MySQL
Tools: Git, VS Code
"""


RESUME_EDUCATION_PROJECTS_AND_SKILLS = """
ARAVIND K.
Mysuru, Karnataka | +91 9876500002 | aravind.k@example.com
LinkedIn Profile

PROFESSIONAL SUMMARY
Second-year CSBS student at JSS Science and Technology University with an interest in machine learning, artificial intelligence.

EDUCATION
Bachelor of Engineering - Computer Science and Business Systems (CSBS)
2025 - 2029
JSS Science and Technology University, Mysuru, Karnataka
Currently in 2nd year | Relevant coursework: Programming, Data Structures, Machine Learning

TECHNICAL SKILLS
Programming: Python, C, C++
Web: HTML, CSS, JavaScript
Core Areas: Machine Learning, Artificial Intelligence
Tools: VS Code, Git, GitHub
Additional: Problem-solving, teamwork, technical documentation

PROJECTS
Machine Learning-Based Resume Recommendation Project
• Developing a project focused on resume analysis and recommendation.
• Exploring NLP-based information extraction and skill identification to support candidate matching.

Insurance Policy Document Simplification Tool | TCS Technology Day Hackathon
• Collaborated on an AI-based tool to convert complex insurance policy language into clearer explanations.
• Worked on the problem-solving and prototype development process as part of a five-member team.

Personal Portfolio Website
• Built a personal website to present academic details, technical skills, and projects.
• Used web development tools and Visual Studio Code; exploring Git and GitHub for version control.

STRENGTHS & INTERESTS
Strengths: Team collaboration, problem-solving, adaptability, quick learning, communication.
Interests: Machine Learning, Artificial Intelligence, Natural Language Processing.
"""


RESUME_FULL_PROFILE = """
VIKRAM ADITYA
Bengaluru, Karnataka | +91 9887766554 | vikram.aditya@techcorp.com

PROFESSIONAL SUMMARY
Experienced Software Engineer with 3 years specializing in distributed backend systems and cloud computing.

EDUCATION
Master of Science in Computer Science
2019 - 2021
Indian Institute of Science, Bengaluru
CGPA: 9.2

Bachelor of Technology in Computer Science
2015 - 2019
National Institute of Technology, Surathkal
CGPA: 8.8

WORK EXPERIENCE
Software Engineer | Microsoft India
July 2021 - Present
• Designed and developed scalable cloud microservices using Python and Docker on Azure.
• Optimized PostgreSQL query performance, reducing 95th percentile latency by 35%.
• Mentored junior engineers and led Agile sprint ceremonies.

Backend Engineering Intern | Amazon
January 2021 - June 2021
• Implemented caching layers using Redis and FastAPI.

PROJECTS
Real-Time Distributed Event Streamer
• Architected a stream processing engine using Python, Kafka, and Docker.
• Technologies: Python, Kafka, Docker, Kubernetes

Automated Vulnerability Scanner
• Built a CI/CD security scanner for containerized microservices.
• Technologies: Go, Docker, Bash, GitHub Actions

TECHNICAL SKILLS
Languages: Python, Go, C++, SQL
Frameworks: FastAPI, Flask, Django
Cloud & DevOps: Azure, Docker, Kubernetes, CI/CD, Linux
Databases: PostgreSQL, Redis, MongoDB
Tools: Git, Postman

CERTIFICATIONS
- Microsoft Certified: Azure Solutions Architect Expert
- AWS Certified Developer - Associate
- Certified Kubernetes Administrator (CKA)
"""


@pytest.fixture
def parser():
    return ResumeParser()


@pytest.fixture
def extractor():
    return SkillExtractionService()


class TestResumeScenarios:
    def test_resume_education_and_skills_only(self, parser, extractor):
        """Test resume containing only education and skills without projects or experience."""
        profile = parser.parse_resume(RESUME_EDUCATION_AND_SKILLS_ONLY)

        # Contact Info
        assert profile["name"] == "ANANYA ROY"
        assert profile["email"] == "ananya.roy@email.com"
        assert profile["phone"] == "+91 9123456780"

        # Education
        assert len(profile["education"]) == 1
        assert "Bachelor of Technology" in profile["education"][0]["degree"]
        assert profile["education"][0]["graduation_year"] == "2027"

        # Experience & Projects & Certs should be empty
        assert len(profile["experience"]) == 0
        assert len(profile["projects"]) == 0
        assert len(profile["certifications"]) == 0

        # Skills
        assert profile["skills"] is not None and len(profile["skills"]) > 0

        # Skill Extraction and Proficiency
        skills_res = extractor.extract_skills_from_profile(profile, full_text=RESUME_EDUCATION_AND_SKILLS_ONLY)
        assert skills_res["total_skills"] >= 7

        # All skills must be Beginner because they are only listed in the skills section
        for s in skills_res["skills"]:
            assert s["proficiency"] == "Beginner", f"Skill {s['name']} should be Beginner, got {s['proficiency']}"
            assert s["sources"] == ["skills_section"]

    def test_resume_education_projects_and_skills(self, parser, extractor):
        """Test resume containing education, unnumbered projects, and skills (like student resume)."""
        profile = parser.parse_resume(RESUME_EDUCATION_PROJECTS_AND_SKILLS)

        # Name with dot/initial
        assert profile["name"] == "ARAVIND K."
        assert profile["email"] == "aravind.k@example.com"
        assert profile["phone"] == "+91 9876500002"

        # Education
        assert len(profile["education"]) == 1
        assert "Bachelor of Engineering" in profile["education"][0]["degree"]
        assert profile["education"][0]["graduation_year"] == "2029"

        # Experience & Certs are 0 (accurate for this resume)
        assert len(profile["experience"]) == 0
        assert len(profile["certifications"]) == 0

        # Projects: must correctly extract 3 unnumbered projects
        assert len(profile["projects"]) == 3
        proj_names = [p["name"] for p in profile["projects"]]
        assert "Machine Learning-Based Resume Recommendation Project" in proj_names[0]
        assert "Insurance Policy Document Simplification Tool" in proj_names[1]
        assert "Personal Portfolio Website" in proj_names[2]

        # Skill Extraction
        skills_res = extractor.extract_skills_from_profile(profile, full_text=RESUME_EDUCATION_PROJECTS_AND_SKILLS)
        skill_dict = {s["name"]: s for s in skills_res["skills"]}

        # Check C and C++ are distinguished
        assert "C" in skill_dict
        assert "C++" in skill_dict
        assert skill_dict["C"]["category"] == "programming_languages"
        assert skill_dict["C++"]["category"] == "programming_languages"

        # Check JavaScript is present and not Java
        assert "JavaScript" in skill_dict
        assert "Java" not in skill_dict

        # Check that skills used in projects are rated Intermediate
        assert "Machine Learning" in skill_dict
        assert skill_dict["Machine Learning"]["proficiency"] == "Intermediate"
        assert "projects" in skill_dict["Machine Learning"]["sources"]

        assert "Git" in skill_dict
        assert skill_dict["Git"]["proficiency"] == "Intermediate"
        assert "projects" in skill_dict["Git"]["sources"]

        assert "VS Code" in skill_dict
        assert skill_dict["VS Code"]["proficiency"] == "Intermediate"

        # Check that skills ONLY in skills list are Beginner
        assert skill_dict["Python"]["proficiency"] == "Beginner"
        assert skill_dict["Python"]["sources"] == ["skills_section"]
        assert skill_dict["C"]["proficiency"] == "Beginner"
        assert skill_dict["C++"]["proficiency"] == "Beginner"

        # No skills should be Advanced because there is no work experience
        advanced_skills = [s["name"] for s in skills_res["skills"] if s["proficiency"] == "Advanced"]
        assert len(advanced_skills) == 0

    def test_resume_full_experience_projects_certs_education(self, parser, extractor):
        """Test full professional resume with experience, projects, certs, and education."""
        profile = parser.parse_resume(RESUME_FULL_PROFILE)

        assert profile["name"] == "VIKRAM ADITYA"
        assert profile["email"] == "vikram.aditya@techcorp.com"

        # Education
        assert len(profile["education"]) >= 1

        # Work Experience
        assert len(profile["experience"]) >= 1
        companies = [e["company"] for e in profile["experience"]]
        assert any("Microsoft" in c for c in companies)

        # Projects
        assert len(profile["projects"]) == 2

        # Certifications
        assert len(profile["certifications"]) >= 2

        # Skill Extraction & Proficiency
        skills_res = extractor.extract_skills_from_profile(profile, full_text=RESUME_FULL_PROFILE)
        skill_dict = {s["name"]: s for s in skills_res["skills"]}

        # Python & Docker & PostgreSQL used in work experience -> Advanced
        assert "Python" in skill_dict
        assert skill_dict["Python"]["proficiency"] == "Advanced"
        assert "experience" in skill_dict["Python"]["sources"]

        assert "Docker" in skill_dict
        assert skill_dict["Docker"]["proficiency"] == "Advanced"
        assert "experience" in skill_dict["Docker"]["sources"]

        assert "PostgreSQL" in skill_dict
        assert skill_dict["PostgreSQL"]["proficiency"] == "Advanced"

        # Kafka & Kubernetes used in projects -> Intermediate
        assert "Kafka" in skill_dict
        assert skill_dict["Kafka"]["proficiency"] == "Intermediate"
        assert "projects" in skill_dict["Kafka"]["sources"]
