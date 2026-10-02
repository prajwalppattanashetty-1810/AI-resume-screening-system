"""
Recommendation Service — High-level orchestration for AI Job Recommendation (Phase 6).
"""

import logging
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.database import Job, ResumeAnalysis
from app.ml.recommender import JobRecommender
from app.services.job_service import format_job_schema
from app.schemas.job import (
    RecommendationRequest,
    RecommendationResponse,
    JobRecommendation,
    SkillMatch
)

logger = logging.getLogger(__name__)


class RecommendationService:
    """Orchestrates candidate profile retrieval, job corpus management, and recommendation ranking."""

    def __init__(self):
        self.recommender = JobRecommender()
        self._cached_job_count = -1

    def _sync_jobs_cache(self, db: Session) -> List[Job]:
        """Fetch active jobs and update the recommender's TF-IDF matrix if changed."""
        active_jobs = db.query(Job).filter(Job.job_status == "Active").all()
        if len(active_jobs) != self._cached_job_count or self.recommender.vectorizer is None:
            self.recommender.fit(active_jobs)
            self._cached_job_count = len(active_jobs)
        return active_jobs

    def get_recommendations(
        self,
        db: Session,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """
        Generate ranked recommendations for a candidate based on TF-IDF cosine similarity and skill match.
        """
        resume_text = ""
        candidate_skills: List[str] = list(request.skills or [])

        # 1. Resolve candidate profile (from file_id or raw request)
        if request.file_id:
            record = db.query(ResumeAnalysis).filter(ResumeAnalysis.file_id == request.file_id).first()
            if not record:
                raise HTTPException(
                    status_code=404,
                    detail=f"Resume analysis not found for file ID: {request.file_id}"
                )

            resume_text = record.extracted_text or ""

            # Extract structured skills from analysis record if present
            if record.skills_json and isinstance(record.skills_json, dict):
                skills_list = record.skills_json.get("skills", [])
                for s in skills_list:
                    if isinstance(s, dict) and "name" in s:
                        candidate_skills.append(s["name"])
                    elif isinstance(s, str):
                        candidate_skills.append(s)

            if not candidate_skills and record.analysis_json and isinstance(record.analysis_json, dict):
                profile_skills = record.analysis_json.get("profile", {}).get("skills", {})
                if isinstance(profile_skills, dict):
                    for domain_skills in profile_skills.values():
                        if isinstance(domain_skills, list):
                            candidate_skills.extend(domain_skills)

        elif request.resume_text is not None:
            resume_text = request.resume_text
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'file_id' or 'resume_text' must be provided to generate recommendations."
            )

        # Deduplicate candidate skills
        candidate_skills = list(dict.fromkeys([s.strip() for s in candidate_skills if s and s.strip()]))

        # 2. Sync and query active jobs
        active_jobs = self._sync_jobs_cache(db)
        if not active_jobs:
            return RecommendationResponse(
                recommendations=[],
                total_jobs_analyzed=0,
                candidate_skills_used=candidate_skills,
                category_filter=request.category,
                location_filter=request.location
            )

        # 3. Compute recommendations via JobRecommender
        raw_recommendations = self.recommender.recommend(
            resume_text=resume_text,
            candidate_skills=candidate_skills,
            jobs=active_jobs,
            top_n=request.top_n,
            category_filter=request.category,
            location_filter=request.location,
            experience_filter=request.experience_level,
            tfidf_weight=request.tfidf_weight,
            skill_weight=request.skill_weight
        )

        # 4. Format into Pydantic schema
        formatted_recommendations: List[JobRecommendation] = []
        for r in raw_recommendations:
            job_model = r["job_raw"]
            schema_job = format_job_schema(job_model)

            skill_match_obj = SkillMatch(
                matched=r["matched_skills"],
                missing=r["missing_skills"],
                partial=[]
            )
            suggested = [f"Learn {s} to qualify" for s in r["missing_skills"][:3]]

            rec = JobRecommendation(
                job=schema_job,
                job_id=r["job_id"],
                title=r["title"],
                company=r["company"],
                category=r["category"],
                location=r["location"],
                work_mode=r.get("work_mode", "Hybrid"),
                experience_level=r.get("experience_level", "Entry-level"),
                salary_range=r.get("salary_range"),
                tfidf_similarity=r["tfidf_similarity"],
                skill_match_percentage=r["skill_match_percentage"],
                match_score=r["match_score"],
                matched_skills=r["matched_skills"],
                missing_skills=r["missing_skills"],
                preferred_skill_matches=r["preferred_skill_matches"],
                skill_match=skill_match_obj,
                explanation=r["explanation"],
                suggested_skills=suggested
            )
            formatted_recommendations.append(rec)

        return RecommendationResponse(
            recommendations=formatted_recommendations,
            total_jobs_analyzed=len(active_jobs),
            candidate_skills_used=candidate_skills,
            category_filter=request.category,
            location_filter=request.location
        )
