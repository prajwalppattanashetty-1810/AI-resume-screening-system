"""
Pydantic Schemas for Skill Gap Analysis & Personalized Learning Recommendations.

Part of Phase 7: Skill Gap Analysis & Personalized Learning Recommendations.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class SkillGapRequest(BaseModel):
    file_id: Optional[str] = Field(None, description="Resume file_id from upload/analysis")
    resume_id: Optional[str] = Field(None, description="Alias for file_id")
    job_id: str = Field(..., description="Job identifier code (e.g. JOB-ML-001) or numeric id")
    candidate_skills: Optional[List[str]] = Field(default=None, description="Optional override for resume skills")


class LearningResource(BaseModel):
    title: str
    url: Optional[str] = None
    resource_type: str = "Official Documentation"


class LearningRecommendation(BaseModel):
    skill_name: str
    category: str
    current_proficiency: Optional[str] = None
    target_proficiency: str
    priority: str = Field(..., description="'High', 'Medium', or 'Low'")
    reason: str
    learning_topics: List[str]
    project_ideas: List[str]
    estimated_duration: str
    resources: List[LearningResource] = Field(default_factory=list)


class SkillItemDetail(BaseModel):
    name: str
    status: str = Field(..., description="'matched', 'partial', or 'missing'")
    requirement_type: str = Field(..., description="'required' or 'preferred'")
    category: str
    current_proficiency: Optional[str] = None
    proficiency_evidence: List[str] = Field(default_factory=list)
    reason: str
    transferable_from: Optional[str] = None


class SkillCoverageMetrics(BaseModel):
    total_required: int
    matched_required: int
    partial_required: int
    missing_required: int
    total_preferred: int
    matched_preferred: int
    partial_preferred: int
    missing_preferred: int
    required_match_percentage: float
    preferred_coverage_percentage: float
    overall_coverage_percentage: float


class SkillGapResponse(BaseModel):
    job_id: str
    job_numeric_id: int
    job_title: str
    company: str
    category: str
    experience_level: str
    location: str
    candidate_name: Optional[str] = None
    metrics: SkillCoverageMetrics
    matched_skills: List[str]
    partial_skills: List[str]
    missing_skills: List[str]
    required_skills_analysis: List[SkillItemDetail]
    preferred_skills_analysis: List[SkillItemDetail]
    learning_recommendations: List[LearningRecommendation]
    summary: str
