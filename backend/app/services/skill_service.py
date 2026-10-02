"""
Skill Service — High-level interface for skill extraction, matching, and gap analysis.
"""

from typing import Dict, List, Any
from app.services.skill_extraction_service import SkillExtractionService


class SkillService:
    """Service wrapper for skill extraction and matching operations."""

    def __init__(self):
        self.extractor = SkillExtractionService()

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Extract technical and soft skills from raw text and return categorized skills.
        """
        extracted_tuples = self.extractor.extract_skills_from_text(text)
        categorized: Dict[str, List[str]] = {cat: [] for cat in self.extractor.taxonomy.keys()}

        for skill, _ in extracted_tuples:
            cat = self.extractor.get_skill_category(skill)
            if cat in categorized and skill not in categorized[cat]:
                categorized[cat].append(skill)

        # Flatten list of all unique skills
        all_skills = [skill for skill, _ in extracted_tuples]

        return {
            "total_skills": len(all_skills),
            "skills": all_skills,
            "categorized_skills": categorized
        }

    def match_skills(self, candidate_skills: List[str], job_skills: List[str]) -> Dict[str, List[str]]:
        """
        Match candidate skills against job requirements with alias normalization.
        """
        cand_normalized = {
            self.extractor.normalize_skill(s) or s.title(): s
            for s in candidate_skills
        }
        job_normalized = {
            self.extractor.normalize_skill(s) or s.title(): s
            for s in job_skills
        }

        matched = []
        missing = []

        for norm_job_skill in job_normalized:
            if norm_job_skill in cand_normalized:
                matched.append(norm_job_skill)
            else:
                missing.append(norm_job_skill)

        return {
            "matched": matched,
            "missing": missing,
            "partial": []
        }

    def get_skill_suggestions(self, missing_skills: List[str]) -> List[str]:
        """Get suggestions for missing skills."""
        return [f"Learn {skill} to improve role compatibility" for skill in missing_skills]
