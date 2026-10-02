"""
Job Service — Handles querying, filtering, search, and metadata for the job dataset.
Part of Phase 5: Job Dataset Creation and Management.
"""

from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, text, String
from app.models.database import Job
from app.schemas.job import JobSchema
import json
import math


def format_job_schema(j: Job) -> JobSchema:
    """Helper to convert SQLAlchemy Job model instance to JobSchema."""
    return JobSchema(
        id=j.id,
        job_id=j.job_id or f"JOB-{j.id}",
        title=j.title,
        company=j.company,
        category=j.category,
        description=j.description,
        responsibilities=j.responsibilities if isinstance(j.responsibilities, list) else [],
        required_skills=j.required_skills if isinstance(j.required_skills, list) else [],
        preferred_skills=j.preferred_skills if isinstance(j.preferred_skills, list) else [],
        min_experience=j.min_experience or 0,
        max_experience=j.max_experience,
        experience_level=j.experience_level or "Entry-level",
        education=j.education,
        employment_type=j.employment_type or "Full-time",
        work_mode=j.work_mode or "Hybrid",
        location=j.location or "Bengaluru, India",
        salary_range=j.salary_range,
        job_status=j.job_status or "Active",
        date_posted=j.date_posted or (j.created_at.strftime("%Y-%m-%d") if j.created_at else None),
        created_at=j.created_at.strftime("%Y-%m-%d") if j.created_at else None
    )


class JobService:
    def get_jobs(
        self,
        db: Session,
        page: int = 1,
        limit: int = 20,
        category: Optional[str] = None,
        experience_level: Optional[str] = None,
        location: Optional[str] = None,
        work_mode: Optional[str] = None,
        employment_type: Optional[str] = None,
        skill: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Job], int, int]:
        """
        Query jobs with flexible filtering and pagination.
        Returns (jobs_list, total_count, total_pages).
        """
        query = db.query(Job).filter(Job.job_status == "Active")

        # Filters
        if category and category.lower() != "all":
            query = query.filter(Job.category == category)

        if experience_level and experience_level.lower() != "all":
            query = query.filter(Job.experience_level == experience_level)

        if work_mode and work_mode.lower() != "all":
            query = query.filter(Job.work_mode == work_mode)

        if employment_type and employment_type.lower() != "all":
            query = query.filter(Job.employment_type == employment_type)

        if location and location.lower() != "all":
            query = query.filter(Job.location.ilike(f"%{location}%"))

        # Skill filtering (searches in required_skills JSON or preferred_skills JSON)
        if skill and skill.strip():
            skill_clean = skill.strip().lower()
            query = query.filter(
                or_(
                    Job.required_skills.cast(String).ilike(f"%{skill_clean}%"),
                    Job.preferred_skills.cast(String).ilike(f"%{skill_clean}%")
                )
            )

        # Free text search across title, description, company, category, location, and skills
        if search and search.strip():
            search_term = f"%{search.strip().lower()}%"
            query = query.filter(
                or_(
                    func.lower(Job.title).ilike(search_term),
                    func.lower(Job.company).ilike(search_term),
                    func.lower(Job.category).ilike(search_term),
                    func.lower(Job.location).ilike(search_term),
                    func.lower(Job.description).ilike(search_term),
                    Job.required_skills.cast(String).ilike(search_term)
                )
            )

        total = query.count()
        pages = max(1, math.ceil(total / limit)) if limit > 0 else 1

        offset = (page - 1) * limit
        jobs = query.order_by(Job.id.asc()).offset(offset).limit(limit).all()

        return jobs, total, pages

    def get_job_by_id(self, db: Session, job_id_or_code: str) -> Optional[Job]:
        """Get single job record by numeric database ID or string job_id code."""
        if str(job_id_or_code).isdigit():
            job = db.query(Job).filter(Job.id == int(job_id_or_code)).first()
            if job:
                return job

        return db.query(Job).filter(Job.job_id == str(job_id_or_code)).first()

    def get_categories(self, db: Session) -> List[Dict[str, Any]]:
        """Get unique job categories with active job counts."""
        results = (
            db.query(Job.category, func.count(Job.id))
            .filter(Job.job_status == "Active")
            .group_by(Job.category)
            .order_by(func.count(Job.id).desc())
            .all()
        )
        return [{"category": r[0], "count": r[1]} for r in results]

    def get_skills_distribution(self, db: Session) -> List[Dict[str, Any]]:
        """Extract and tally all required and preferred skills across active jobs."""
        jobs = db.query(Job.required_skills, Job.preferred_skills).filter(Job.job_status == "Active").all()
        skill_counts: Dict[str, int] = {}

        for req_skills, pref_skills in jobs:
            if isinstance(req_skills, list):
                for s in req_skills:
                    s_str = str(s).strip()
                    if s_str:
                        skill_counts[s_str] = skill_counts.get(s_str, 0) + 1

            if isinstance(pref_skills, list):
                for s in pref_skills:
                    s_str = str(s).strip()
                    if s_str:
                        skill_counts[s_str] = skill_counts.get(s_str, 0) + 1

        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"skill": s[0], "count": s[1]} for s in sorted_skills]

    def search_jobs(
        self,
        db: Session,
        query: Optional[str] = None,
        category: Optional[str] = None,
        location: Optional[str] = None,
        skill: Optional[str] = None,
        limit: int = 10
    ) -> List[Job]:
        """Search active jobs by title, skills, category, or location."""
        jobs, _, _ = self.get_jobs(
            db,
            page=1,
            limit=limit,
            category=category,
            location=location,
            skill=skill,
            search=query
        )
        return jobs

    def get_stats(self, db: Session) -> Dict[str, Any]:
        """Aggregate high-level dataset statistics."""
        active_query = db.query(Job).filter(Job.job_status == "Active")
        total_jobs = active_query.count()

        categories = self.get_categories(db)

        # Experience breakdown
        exp_results = (
            db.query(Job.experience_level, func.count(Job.id))
            .filter(Job.job_status == "Active")
            .group_by(Job.experience_level)
            .all()
        )
        experience_levels = {r[0]: r[1] for r in exp_results}

        # Work mode breakdown
        mode_results = (
            db.query(Job.work_mode, func.count(Job.id))
            .filter(Job.job_status == "Active")
            .group_by(Job.work_mode)
            .all()
        )
        work_modes = {r[0]: r[1] for r in mode_results}

        # Employment type breakdown
        emp_results = (
            db.query(Job.employment_type, func.count(Job.id))
            .filter(Job.job_status == "Active")
            .group_by(Job.employment_type)
            .all()
        )
        employment_types = {r[0]: r[1] for r in emp_results}

        # Top locations
        loc_results = (
            db.query(Job.location, func.count(Job.id))
            .filter(Job.job_status == "Active")
            .group_by(Job.location)
            .order_by(func.count(Job.id).desc())
            .limit(10)
            .all()
        )
        top_locations = [{"location": r[0], "count": r[1]} for r in loc_results]

        top_skills = self.get_skills_distribution(db)[:20]

        return {
            "total_jobs": total_jobs,
            "total_categories": len(categories),
            "categories": categories,
            "experience_levels": experience_levels,
            "work_modes": work_modes,
            "employment_types": employment_types,
            "top_locations": top_locations,
            "top_skills": top_skills,
        }

    def seed_dataset(self, db: Session, filepath: Optional[str] = None) -> Dict[str, int]:
        """Trigger idempotent dataset seeding from JSON file."""
        import os
        from scripts.seed_jobs import seed_jobs_from_records

        if not filepath:
            filepath = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "..",
                "data",
                "jobs.json"
            )
            filepath = os.path.normpath(filepath)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Jobs dataset file not found at {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            records = json.load(f)

        return seed_jobs_from_records(db, records)

