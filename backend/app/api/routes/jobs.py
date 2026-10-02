"""
API routes for Job Dataset Management and Explorer (Phase 5).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.database import get_db, Job
from app.schemas.job import (
    JobSchema,
    JobListResponse,
    JobCategoryItem,
    JobSkillItem,
    JobStatsResponse,
    JobSeedResponse,
    RecommendationRequest,
    RecommendationResponse
)
from app.services.job_service import JobService, format_job_schema
from app.services.recommendation_service import RecommendationService

router = APIRouter()
job_service = JobService()
recommendation_service = RecommendationService()


@router.get("", response_model=JobListResponse)
@router.get("/", response_model=JobListResponse)
def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by job category"),
    experience_level: Optional[str] = Query(None, description="Filter by experience level (Entry-level, Junior, Intermediate, Senior)"),
    location: Optional[str] = Query(None, description="Filter by location keyword"),
    work_mode: Optional[str] = Query(None, description="Filter by work mode (Remote, Hybrid, On-site)"),
    employment_type: Optional[str] = Query(None, description="Filter by employment type (Full-time, Internship, Contract)"),
    skill: Optional[str] = Query(None, description="Filter by required or preferred skill"),
    search: Optional[str] = Query(None, description="Search keyword in title, company, description"),
    db: Session = Depends(get_db)
):
    """
    Get paginated job listings with flexible multi-criteria filtering.
    """
    jobs, total, pages = job_service.get_jobs(
        db=db,
        page=page,
        limit=limit,
        category=category,
        experience_level=experience_level,
        location=location,
        work_mode=work_mode,
        employment_type=employment_type,
        skill=skill,
        search=search
    )

    return JobListResponse(
        jobs=[format_job_schema(j) for j in jobs],
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get("/categories", response_model=List[JobCategoryItem])
def get_job_categories(db: Session = Depends(get_db)):
    """Get all unique job categories with active opportunity counts."""
    return job_service.get_categories(db)


@router.get("/skills", response_model=List[JobSkillItem])
def get_job_skills(db: Session = Depends(get_db)):
    """Get all distinct skills across active jobs with occurrence frequency."""
    return job_service.get_skills_distribution(db)


@router.get("/stats", response_model=JobStatsResponse)
def get_job_stats(db: Session = Depends(get_db)):
    """Return comprehensive dataset statistics across categories, experience, and work modes."""
    return job_service.get_stats(db)


@router.post("/seed", response_model=JobSeedResponse)
def seed_jobs_dataset(db: Session = Depends(get_db)):
    """Safely seed/update the job dataset from the verified synthetic dataset JSON file."""
    try:
        res = job_service.seed_dataset(db)
        return JobSeedResponse(
            message="Job dataset successfully synchronized.",
            inserted=res["inserted"],
            updated=res["updated"],
            total_in_db=res["total"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to seed job dataset: {str(e)}")


@router.get("/search", response_model=List[JobSchema])
def search_jobs(
    q: Optional[str] = Query(None, description="Search keyword"),
    category: Optional[str] = Query(None, description="Category filter"),
    location: Optional[str] = Query(None, description="Location filter"),
    skill: Optional[str] = Query(None, description="Skill filter"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Fast keyword search across active jobs by title, skills, category, or location."""
    jobs = job_service.search_jobs(
        db,
        query=q,
        category=category,
        location=location,
        skill=skill,
        limit=limit
    )
    return [format_job_schema(j) for j in jobs]


@router.post("/recommend", response_model=RecommendationResponse)
def recommend_jobs(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate ranked job recommendations for a candidate based on TF-IDF
    cosine similarity (70%) and transparent required skill matching (30%).
    """
    return recommendation_service.get_recommendations(db=db, request=request)


@router.get("/{job_id}", response_model=JobSchema)
def get_job_detail(job_id: str, db: Session = Depends(get_db)):
    """Get single job details by numeric ID or job code."""
    job = job_service.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job opportunity not found.")

    return format_job_schema(job)
