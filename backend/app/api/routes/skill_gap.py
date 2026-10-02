"""
API Routes for Skill Gap Analysis & Personalized Learning Recommendations.

Part of Phase 7: Skill Gap Analysis & Personalized Learning Recommendations.
"""

import logging
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models.database import get_db, Job, ResumeAnalysis
from app.schemas.skill_gap import SkillGapRequest, SkillGapResponse
from app.services.skill_gap_service import SkillGapService

logger = logging.getLogger(__name__)

router = APIRouter()
skill_gap_service = SkillGapService()


def _resolve_job(job_id_param: str, db: Session) -> Optional[Job]:
    """Finds a job by unique job_id code or integer primary key."""
    if not job_id_param:
        return None
    raw_str = str(job_id_param).strip()
    if raw_str.isdigit():
        return db.query(Job).filter((Job.id == int(raw_str)) | (Job.job_id == raw_str)).first()
    return db.query(Job).filter(Job.job_id == raw_str).first()


@router.post("/analyze", response_model=SkillGapResponse)
def analyze_skill_gap(
    request: SkillGapRequest,
    db: Session = Depends(get_db)
):
    """
    Performs intelligent skill gap analysis comparing candidate resume skills
    against a specific job listing's required and preferred requirements.

    Returns:
    - Detailed skill breakdown (matched, partial, missing)
    - Coverage metrics (required %, preferred %, overall %)
    - Prioritized learning recommendations with verified resources
    """
    target_file_id = request.file_id or request.resume_id

    # 1. Validate required candidate input
    if not target_file_id and (request.candidate_skills is None or len(request.candidate_skills) == 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either a valid 'file_id' or a non-empty 'candidate_skills' list."
        )

    # 2. Fetch Job
    job = _resolve_job(request.job_id, db)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job listing with identifier '{request.job_id}' not found."
        )

    # 3. Resolve Candidate Skills and Metadata
    candidate_skills: Any = []
    candidate_name: Optional[str] = None

    if target_file_id:
        resume_record = db.query(ResumeAnalysis).filter(ResumeAnalysis.file_id == str(target_file_id)).first()
        if not resume_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume analysis with file_id '{target_file_id}' not found."
            )

        # Extract structured skills from database record
        skills_data = resume_record.skills_json
        if isinstance(skills_data, dict):
            # Check for Phase 4 structured list with proficiency
            if "skills" in skills_data and isinstance(skills_data["skills"], list):
                candidate_skills = skills_data["skills"]
            elif "categorized_skills" in skills_data and isinstance(skills_data["categorized_skills"], dict):
                # Flatten categorized dict
                flat = []
                for cat_list in skills_data["categorized_skills"].values():
                    if isinstance(cat_list, list):
                        flat.extend(cat_list)
                candidate_skills = flat
        elif isinstance(skills_data, list):
            candidate_skills = skills_data

        # Fallback to extracting on-the-fly if skills_json was empty but text exists
        if not candidate_skills and resume_record.extracted_text:
            extracted_info = skill_gap_service.extractor.extract_skills_from_text(resume_record.extracted_text)
            candidate_skills = [name for name, _ in extracted_info]

        # Extract candidate name if available
        if isinstance(resume_record.analysis_json, dict):
            profile = resume_record.analysis_json.get("profile", {})
            if isinstance(profile, dict):
                candidate_name = profile.get("name")
    elif request.candidate_skills:
        # Client supplied raw skill list directly
        candidate_skills = request.candidate_skills
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either a valid 'file_id' or a non-empty 'candidate_skills' list."
        )

    # Allow request override of candidate_skills if explicitly provided
    if request.candidate_skills:
        candidate_skills = request.candidate_skills

    # 3. Execute Skill Gap Analysis
    req_skills = job.required_skills if isinstance(job.required_skills, list) else []
    pref_skills = job.preferred_skills if isinstance(job.preferred_skills, list) else []

    gap_result = skill_gap_service.analyze_skill_gap(
        candidate_skills=candidate_skills,
        required_skills=req_skills,
        preferred_skills=pref_skills,
        job_title=job.title,
        job_category=job.category,
        job_exp_level=job.experience_level or "Entry-level"
    )

    return SkillGapResponse(
        job_id=job.job_id or f"JOB-{job.id}",
        job_numeric_id=job.id,
        job_title=job.title,
        company=job.company,
        category=job.category,
        experience_level=job.experience_level or "Entry-level",
        location=job.location or "Remote",
        candidate_name=candidate_name,
        metrics=gap_result["metrics"],
        matched_skills=gap_result["matched_skills"],
        partial_skills=gap_result["partial_skills"],
        missing_skills=gap_result["missing_skills"],
        required_skills_analysis=gap_result["required_skills_analysis"],
        preferred_skills_analysis=gap_result["preferred_skills_analysis"],
        learning_recommendations=gap_result["learning_recommendations"],
        summary=gap_result["summary"]
    )


@router.get("/analyze/{file_id}/{job_id}", response_model=SkillGapResponse)
def get_skill_gap_analysis(
    file_id: str,
    job_id: str,
    db: Session = Depends(get_db)
):
    """Convenience GET endpoint for browser navigation and headless verification."""
    req = SkillGapRequest(file_id=file_id, job_id=job_id)
    return analyze_skill_gap(req, db)
