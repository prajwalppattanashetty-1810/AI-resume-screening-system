from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any


class JobSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: str = Field(default="", description="Unique job identifier code e.g. JOB-ML-001")
    title: str
    company: str
    category: str
    description: str
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[str]
    preferred_skills: List[str] = Field(default_factory=list)
    min_experience: int = Field(default=0, ge=0)
    max_experience: Optional[int] = None
    experience_level: str = Field(default="Entry-level")
    education: Optional[str] = "Bachelor's in Computer Science or related field"
    employment_type: str = Field(default="Full-time")
    work_mode: str = Field(default="Hybrid")
    location: str = Field(default="Bengaluru, India")
    salary_range: Optional[str] = None
    job_status: str = Field(default="Active")
    date_posted: Optional[str] = None
    created_at: Optional[str] = None


class JobListResponse(BaseModel):
    jobs: List[JobSchema]
    total: int
    page: int = 1
    limit: int = 20
    pages: int = 1


class JobCategoryItem(BaseModel):
    category: str
    count: int


class JobSkillItem(BaseModel):
    skill: str
    count: int


class JobLocationItem(BaseModel):
    location: str
    count: int


class JobStatsResponse(BaseModel):
    total_jobs: int
    total_categories: int
    categories: List[JobCategoryItem]
    experience_levels: Dict[str, int]
    work_modes: Dict[str, int]
    employment_types: Dict[str, int]
    top_locations: List[JobLocationItem]
    top_skills: List[JobSkillItem]


class JobSeedResponse(BaseModel):
    message: str
    inserted: int
    updated: int
    total_in_db: int



class RecommendationRequest(BaseModel):
    file_id: Optional[str] = Field(None, description="Resume file/analysis ID from Phase 2-4")
    resume_text: Optional[str] = Field(None, description="Raw or preprocessed resume text (optional if file_id provided)")
    skills: Optional[List[str]] = Field(default_factory=list, description="Structured candidate skills")
    category: Optional[str] = Field(None, description="Optional category filter (e.g. Machine Learning Engineer)")
    location: Optional[str] = Field(None, description="Optional location filter (e.g. Bengaluru, Remote)")
    experience_level: Optional[str] = Field(None, description="Optional experience level filter (Entry-level, Junior, etc.)")
    top_n: int = Field(5, ge=1, le=50, description="Number of recommendations to return")
    tfidf_weight: float = Field(0.7, ge=0.0, le=1.0, description="Weight for TF-IDF cosine similarity")
    skill_weight: float = Field(0.3, ge=0.0, le=1.0, description="Weight for required skill match")


class SkillMatch(BaseModel):
    matched: List[str]
    missing: List[str]
    partial: List[str] = Field(default_factory=list)


class JobRecommendation(BaseModel):
    job: JobSchema
    job_id: str
    title: str
    company: str
    category: str
    location: str
    work_mode: Optional[str] = "Hybrid"
    experience_level: Optional[str] = "Entry-level"
    salary_range: Optional[str] = None
    tfidf_similarity: float
    skill_match_percentage: float
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    preferred_skill_matches: List[str] = Field(default_factory=list)
    skill_match: Optional[SkillMatch] = None
    explanation: str
    suggested_skills: List[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    recommendations: List[JobRecommendation]
    total_jobs_analyzed: int
    candidate_skills_used: List[str] = Field(default_factory=list)
    category_filter: Optional[str] = None
    location_filter: Optional[str] = None
    disclaimer: str = Field(
        default="Experimental matching score for exploratory recommendations. Not a hiring guarantee."
    )



class SkillAnalysisRequest(BaseModel):
    resume_skills: List[str]
    job_skills: List[str]


class SkillGapAnalysis(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    partial_skills: List[str]
    learning_recommendations: List[dict]
