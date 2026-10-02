"""
Pydantic schemas for skill extraction, normalization, and categorization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ExtractedSkillItem(BaseModel):
    name: str = Field(..., description="Canonical name of the skill")
    category: str = Field(..., description="Taxonomy category")
    proficiency: str = Field(..., description="Heuristic proficiency: Beginner, Intermediate, Advanced, Unknown")
    proficiency_reason: str = Field(..., description="Explanation of evidence supporting proficiency")
    sources: List[str] = Field(default_factory=list, description="Sections where the skill was found")
    occurrences: int = Field(default=1, description="Number of mentions across the resume")
    evidence: List[str] = Field(default_factory=list, description="Contextual text snippets showing usage")


class CategorizedSkills(BaseModel):
    programming_languages: List[str] = Field(default_factory=list)
    frontend: List[str] = Field(default_factory=list)
    backend: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    machine_learning: List[str] = Field(default_factory=list)
    cloud_devops: List[str] = Field(default_factory=list)
    development_tools: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)


class SkillExtractionRequest(BaseModel):
    file_id: Optional[str] = None
    fileId: Optional[str] = None
    resume_text: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None

    def get_file_id(self) -> str:
        return self.file_id or self.fileId or ""


class SkillExtractionResponse(BaseModel):
    file_id: Optional[str] = None
    total_skills: int
    categorized_skills: Dict[str, List[str]]
    skills: List[ExtractedSkillItem]
    message: str = "Skills extracted and categorized successfully."
