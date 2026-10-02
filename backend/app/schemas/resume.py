from pydantic import BaseModel
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
