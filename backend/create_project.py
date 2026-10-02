import os

base_dir = r"c:\Users\Prajwal P\OneDrive\Desktop\ML PROJECT\backend"
os.makedirs(base_dir, exist_ok=True)

files = [
    ("requirements.txt", """fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
PyMuPDF==1.23.7
nltk==3.8.1
scikit-learn==1.3.2
pandas==2.1.4
numpy==1.26.2
sqlalchemy==2.0.23
aiofiles==23.2.1
pytest==7.4.3
httpx==0.25.2
python-jose==3.3.0
"""),
    (".env.example", """BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=true
DATABASE_URL=sqlite:///./data/resume_screener.db
MAX_UPLOAD_SIZE_MB=10
UPLOAD_DIR=uploads
FRONTEND_URL=http://localhost:5173
SECRET_KEY=change-this-to-a-random-secret-key
"""),
    ("data/.gitkeep", ""),
    ("trained_models/.gitkeep", ""),
    ("uploads/.gitkeep", ""),
    ("app/__init__.py", '"""AI Resume Screening & Job Recommendation System - Backend Application"""\n'),
    ("app/config.py", """from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    debug: bool = True
    database_url: str = "sqlite:///./data/resume_screener.db"
    max_upload_size_mb: int = 10
    upload_dir: str = "uploads"
    frontend_url: str = "http://localhost:5173"
    secret_key: str = "change-this-to-a-random-secret-key"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
"""),
    ("app/main.py", """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from app.config import get_settings
from app.api.routes import health, resume, jobs, skills

settings = get_settings()

app = FastAPI(
    title='AI Resume Screening & Job Recommendation System',
    description='Backend API for Resume Screening and Job Recommendation',
    version='1.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])

@app.on_event("startup")
async def startup_event():
    os.makedirs(settings.upload_dir, exist_ok=True)

@app.get("/")
def root():
    return {"message": "API is running", "version": "1.0.0", "docs": "/docs"}

if __name__ == '__main__':
    uvicorn.run("app.main:app", host=settings.backend_host, port=settings.backend_port, reload=settings.debug)
"""),
    ("app/api/__init__.py", '"""API package"""\n'),
    ("app/api/routes/__init__.py", '"""API Routes"""\n'),
    ("app/api/routes/health.py", """from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/")
def health_check():
    return {"status": "ok", "version": "1.0.0", "timestamp": datetime.now().isoformat()}
"""),
    ("app/api/routes/resume.py", """from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
import os
from app.config import get_settings
from app.schemas.resume import ResumeAnalysisResponse, ResumeProfile, ScoreBreakdown, ExtractedSkills

router = APIRouter()
settings = get_settings()

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File size exceeds {settings.max_upload_size_mb}MB limit")
        
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.pdf"
    filepath = os.path.join(settings.upload_dir, filename)
    
    with open(filepath, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    return {"file_id": file_id, "filename": file.filename}

@router.post("/analyze", response_model=ResumeAnalysisResponse)
def analyze_resume(file_id: str):
    # TODO: Phase 2-8 will implement actual analysis
    profile = ResumeProfile(
        name="", email="", phone="", education=[], experience=[], projects=[],
        skills=ExtractedSkills(programming_languages=[], frameworks=[], libraries=[], databases=[], cloud=[], tools=[], soft_skills=[]),
        certifications=[]
    )
    scores = ScoreBreakdown(overall=0.0, skills=0.0, projects=0.0, experience=0.0, education=0.0, completeness=0.0)
    return ResumeAnalysisResponse(file_id=file_id, profile=profile, scores=scores, improvement_suggestions=[])
"""),
    ("app/api/routes/jobs.py", """from fastapi import APIRouter
from app.schemas.job import RecommendationRequest, RecommendationResponse

router = APIRouter()

@router.get("/")
def list_jobs():
    # TODO: implement
    return []

@router.post("/recommend", response_model=RecommendationResponse)
def recommend_jobs(request: RecommendationRequest):
    # TODO: implement
    return RecommendationResponse(recommendations=[], total_jobs_analyzed=0)
"""),
    ("app/api/routes/skills.py", """from fastapi import APIRouter
from app.schemas.job import SkillAnalysisRequest, SkillGapAnalysis

router = APIRouter()

@router.post("/analyze", response_model=SkillGapAnalysis)
def analyze_skills(request: SkillAnalysisRequest):
    # TODO: implement
    return SkillGapAnalysis(matched_skills=[], missing_skills=[], partial_skills=[], learning_recommendations=[])
"""),
    ("app/services/__init__.py", '"""Services package"""\n'),
    ("app/services/pdf_service.py", """class PDFService:
    def extract_text(self, file_path: str) -> str:
        \"\"\"Extract text from a PDF file.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def validate_pdf(self, file_path: str) -> bool:
        \"\"\"Validate if the file is a valid PDF.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
"""),
    ("app/services/nlp_service.py", """class NLPService:
    def preprocess_text(self, text: str) -> str:
        \"\"\"Preprocess text for NLP tasks.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def extract_entities(self, text: str) -> dict:
        \"\"\"Extract entities from text.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def tokenize(self, text: str) -> list[str]:
        \"\"\"Tokenize text.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
"""),
    ("app/services/skill_service.py", """class SkillService:
    def extract_skills(self, text: str) -> dict:
        \"\"\"Extract technical and soft skills from text.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def match_skills(self, candidate_skills: list, job_skills: list) -> dict:
        \"\"\"Match candidate skills against job requirements.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def get_skill_suggestions(self, missing_skills: list) -> list:
        \"\"\"Get suggestions for missing skills.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
"""),
    ("app/services/recommendation_service.py", """class RecommendationService:
    def get_recommendations(self, resume_text: str, skills: list) -> list:
        \"\"\"Get job recommendations based on resume and skills.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def calculate_similarity(self, resume_vector, job_vector) -> float:
        \"\"\"Calculate similarity between resume and job vectors.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def explain_recommendation(self, matched_skills: list, missing_skills: list, score: float) -> str:
        \"\"\"Provide explanation for the recommendation.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
"""),
    ("app/services/scoring_service.py", """class ScoringService:
    def calculate_resume_score(self, resume_data: dict) -> dict:
        \"\"\"Calculate overall resume score.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def calculate_skill_score(self, skills: list) -> float:
        \"\"\"Calculate skill matching score.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def calculate_experience_score(self, experience: list) -> float:
        \"\"\"Calculate experience score.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def calculate_education_score(self, education: dict) -> float:
        \"\"\"Calculate education score.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def calculate_completeness_score(self, resume_data: dict) -> float:
        \"\"\"Calculate completeness score of the resume.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def get_improvement_suggestions(self, resume_data: dict, scores: dict) -> list:
        \"\"\"Get suggestions to improve resume score.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
"""),
    ("app/services/job_service.py", """class JobService:
    def get_all_jobs(self) -> list:
        \"\"\"Get all available jobs.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def get_job_by_id(self, job_id: int) -> dict:
        \"\"\"Get job details by ID.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def search_jobs(self, query: str) -> list:
        \"\"\"Search for jobs based on a query.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def load_job_dataset(self, filepath: str) -> None:
        \"\"\"Load job dataset from a file.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
"""),
    ("app/ml/__init__.py", '"""ML package"""\n'),
    ("app/ml/preprocessor.py", """class TextPreprocessor:
    \"\"\"Text preprocessing for NLP tasks.\"\"\"
    def clean_text(self, text: str) -> str:
        \"\"\"Clean raw text.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def remove_stopwords(self, tokens: list[str]) -> list[str]:
        \"\"\"Remove stopwords from tokens.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def lemmatize(self, tokens: list[str]) -> list[str]:
        \"\"\"Lemmatize tokens.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def preprocess_pipeline(self, text: str) -> str:
        \"\"\"Chain all preprocessing steps.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
"""),
    ("app/ml/feature_extractor.py", """class FeatureExtractor:
    \"\"\"Extract features using TF-IDF.\"\"\"
    def fit_tfidf(self, documents: list[str]) -> None:
        \"\"\"Fit TF-IDF model on documents.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def transform_tfidf(self, text: str):
        \"\"\"Transform text to TF-IDF features.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def get_feature_names(self) -> list[str]:
        \"\"\"Get TF-IDF feature names.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
"""),
    ("app/ml/recommender.py", """class JobRecommender:
    \"\"\"Job recommendation system using cosine similarity.\"\"\"
    def fit(self, job_descriptions: list[str], job_metadata: list[dict]) -> None:
        \"\"\"Fit the recommender model.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def recommend(self, resume_text: str, top_n: int = 5) -> list[dict]:
        \"\"\"Recommend top N jobs for a given resume.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def calculate_cosine_similarity(self, vec1, vec2) -> float:
        \"\"\"Calculate cosine similarity between two vectors.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
"""),
    ("app/ml/evaluator.py", """class ModelEvaluator:
    \"\"\"Evaluate ML model performance.\"\"\"
    def evaluate_recommendations(self, actual: list, predicted: list) -> dict:
        \"\"\"Evaluate job recommendations.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def calculate_precision_at_k(self, actual: list, predicted: list, k: int) -> float:
        \"\"\"Calculate precision at K.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
        
    def generate_evaluation_report(self) -> dict:
        \"\"\"Generate comprehensive evaluation report.\"\"\"
        # TODO: implement
        raise NotImplementedError("To be implemented")
"""),
    ("app/models/__init__.py", '"""Database models"""\n'),
    ("app/models/database.py", """from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from app.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    description = Column(Text)
    required_skills = Column(JSON)
    experience_level = Column(String)
    location = Column(String)
    category = Column(String)
    salary_range = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)
    original_filename = Column(String)
    extracted_text = Column(Text)
    skills_json = Column(JSON)
    analysis_json = Column(JSON)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

def create_tables():
    Base.metadata.create_all(bind=engine)
"""),
    ("app/schemas/__init__.py", '"""Pydantic schemas"""\n'),
    ("app/schemas/resume.py", """from pydantic import BaseModel
from typing import Optional, List

class ResumeUploadResponse(BaseModel):
    file_id: str
    filename: str
    message: str = "Upload successful"

class ExtractedEducation(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[str] = None
    cgpa: Optional[str] = None

class ExtractedExperience(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None

class ExtractedProject(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str]

class ExtractedSkills(BaseModel):
    programming_languages: List[str]
    frameworks: List[str]
    libraries: List[str]
    databases: List[str]
    cloud: List[str]
    tools: List[str]
    soft_skills: List[str]

class ResumeProfile(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education: List[ExtractedEducation]
    experience: List[ExtractedExperience]
    projects: List[ExtractedProject]
    skills: ExtractedSkills
    certifications: List[str]

class ScoreBreakdown(BaseModel):
    overall: float
    skills: float
    projects: float
    experience: float
    education: float
    completeness: float

class ImprovementSuggestion(BaseModel):
    category: str
    suggestion: str
    priority: str

class ResumeAnalysisResponse(BaseModel):
    file_id: str
    profile: ResumeProfile
    scores: ScoreBreakdown
    improvement_suggestions: List[ImprovementSuggestion]
"""),
    ("app/schemas/job.py", """from pydantic import BaseModel
from typing import Optional, List

class JobSchema(BaseModel):
    id: int
    title: str
    company: str
    description: str
    required_skills: List[str]
    experience_level: str
    location: str
    category: str
    salary_range: Optional[str] = None

class JobListResponse(BaseModel):
    jobs: List[JobSchema]
    total: int

class RecommendationRequest(BaseModel):
    resume_text: str
    skills: List[str]

class SkillMatch(BaseModel):
    matched: List[str]
    missing: List[str]
    partial: List[str]

class JobRecommendation(BaseModel):
    job: JobSchema
    match_score: float
    skill_match: SkillMatch
    explanation: str
    suggested_skills: List[str]

class RecommendationResponse(BaseModel):
    recommendations: List[JobRecommendation]
    total_jobs_analyzed: int

class SkillAnalysisRequest(BaseModel):
    resume_skills: List[str]
    job_skills: List[str]

class SkillGapAnalysis(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    partial_skills: List[str]
    learning_recommendations: List[dict]
"""),
    ("app/utils/__init__.py", '"""Utilities"""\n'),
    ("app/utils/text_cleaner.py", """import re

def sanitize_text(text: str) -> str:
    \"\"\"Basic text sanitization.\"\"\"
    if not text:
        return ""
    text = re.sub(r'[\\x00-\\x08\\x0b\\x0c\\x0e-\\x1f\\x7f-\\xff]', '', text)
    text = re.sub(r'\\s+', ' ', text).strip()
    return text

def truncate_text(text: str, max_length: int = 10000) -> str:
    \"\"\"Truncate text safely.\"\"\"
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length]
"""),
    ("app/utils/validators.py", """import re

def validate_file_extension(filename: str, allowed: list[str] = ['.pdf']) -> bool:
    \"\"\"Validate file extension.\"\"\"
    if not filename:
        return False
    return any(filename.lower().endswith(ext) for ext in allowed)

def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
    \"\"\"Validate file size.\"\"\"
    return file_size <= max_size_mb * 1024 * 1024

def is_valid_email(email: str) -> bool:
    \"\"\"Validate email format.\"\"\"
    pattern = r'^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$'
    return bool(re.match(pattern, email))

def is_valid_phone(phone: str) -> bool:
    \"\"\"Validate phone format.\"\"\"
    pattern = r'^\\+?[0-9\\-\\s()]{7,15}$'
    return bool(re.match(pattern, phone))
"""),
    ("tests/__init__.py", ""),
    ("tests/conftest.py", """import pytest
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
"""),
    ("tests/test_api.py", """def test_root_endpoint(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()

def test_health_endpoint(test_client):
    response = test_client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_upload_no_file(test_client):
    response = test_client.post("/api/resume/upload")
    assert response.status_code == 422  # Unprocessable Entity (Missing field)

def test_upload_invalid_file_type(test_client):
    files = {'file': ('test.txt', b'Hello world', 'text/plain')}
    response = test_client.post("/api/resume/upload", files=files)
    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]
"""),
    ("tests/test_validators.py", """from app.utils.validators import validate_file_extension, validate_file_size, is_valid_email, is_valid_phone

def test_valid_pdf_extension():
    assert validate_file_extension("resume.pdf") == True
    assert validate_file_extension("RESUME.PDF") == True

def test_invalid_extension():
    assert validate_file_extension("resume.docx") == False
    assert validate_file_extension("resume.txt") == False

def test_valid_file_size():
    assert validate_file_size(5 * 1024 * 1024, 10) == True  # 5MB < 10MB
    assert validate_file_size(10 * 1024 * 1024, 10) == True # 10MB = 10MB

def test_oversized_file():
    assert validate_file_size(11 * 1024 * 1024, 10) == False # 11MB > 10MB

def test_valid_email():
    assert is_valid_email("test@example.com") == True
    assert is_valid_email("user.name+tag@domain.co.uk") == True

def test_invalid_email():
    assert is_valid_email("invalid-email") == False
    assert is_valid_email("test@") == False
    assert is_valid_email("@example.com") == False

def test_valid_phone():
    assert is_valid_phone("+1234567890") == True
    assert is_valid_phone("123-456-7890") == True

def test_invalid_phone():
    assert is_valid_phone("abc") == False
""")
]

for filename, content in files:
    filepath = os.path.join(base_dir, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created {filename}")

print("All files created successfully!")
