from fastapi import APIRouter
from app.schemas.job import SkillAnalysisRequest, SkillGapAnalysis
from app.services.skill_gap_service import SkillGapService

router = APIRouter()
skill_gap_service = SkillGapService()


@router.post("/analyze", response_model=SkillGapAnalysis)
def analyze_skills(request: SkillAnalysisRequest):
    """Analyze skills gap from raw resume and job skill arrays."""
    resume_skills = request.resume_skills or []
    job_skills = request.job_skills or []

    result = skill_gap_service.analyze_skill_gap(
        candidate_skills=resume_skills,
        required_skills=job_skills,
        preferred_skills=[],
        job_title="Target Position"
    )

    return SkillGapAnalysis(
        matched_skills=result["matched_skills"],
        missing_skills=result["missing_skills"],
        partial_skills=result["partial_skills"],
        learning_recommendations=result["learning_recommendations"]
    )

