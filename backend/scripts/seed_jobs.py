"""
Database Seeder for Phase 5: Job Dataset.
Idempotently loads jobs from backend/data/jobs.json into SQLite resume_screener.db.
Preserves existing resume records and avoids duplicate job insertion.
"""

import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Job, create_tables


def seed_jobs_from_records(db: SessionLocal, job_records: list) -> dict:
    """Idempotently seed or update jobs from a list of dict records."""
    existing_jobs = {j.job_id: j for j in db.query(Job).all()}
    inserted = 0
    updated = 0

    for item in job_records:
        job_code = item.get("job_id")
        if not job_code:
            continue

        if job_code in existing_jobs:
            existing = existing_jobs[job_code]
            existing.title = item.get("title", existing.title)
            existing.company = item.get("company", existing.company)
            existing.category = item.get("category", existing.category)
            existing.description = item.get("description", existing.description)
            existing.responsibilities = item.get("responsibilities", existing.responsibilities or [])
            existing.required_skills = item.get("required_skills", existing.required_skills)
            existing.preferred_skills = item.get("preferred_skills", existing.preferred_skills)
            existing.min_experience = item.get("min_experience", existing.min_experience)
            existing.max_experience = item.get("max_experience", existing.max_experience)
            existing.experience_level = item.get("experience_level", existing.experience_level)
            existing.education = item.get("education", existing.education)
            existing.employment_type = item.get("employment_type", existing.employment_type)
            existing.work_mode = item.get("work_mode", existing.work_mode)
            existing.location = item.get("location", existing.location)
            existing.salary_range = item.get("salary_range", existing.salary_range)
            existing.job_status = item.get("job_status", existing.job_status)
            existing.date_posted = item.get("date_posted", existing.date_posted)
            updated += 1
        else:
            new_job = Job(
                job_id=job_code,
                title=item["title"],
                company=item["company"],
                category=item["category"],
                description=item["description"],
                responsibilities=item.get("responsibilities", []),
                required_skills=item.get("required_skills", []),
                preferred_skills=item.get("preferred_skills", []),
                min_experience=item.get("min_experience", 0),
                max_experience=item.get("max_experience"),
                experience_level=item.get("experience_level", "Entry-level"),
                education=item.get("education", "Bachelor's in Computer Science or related field"),
                employment_type=item.get("employment_type", "Full-time"),
                work_mode=item.get("work_mode", "Hybrid"),
                location=item.get("location", "Bengaluru, India"),
                salary_range=item.get("salary_range"),
                job_status=item.get("job_status", "Active"),
                date_posted=item.get("date_posted") or item.get("created_date")
            )
            db.add(new_job)
            inserted += 1

    # Remove any obsolete/stale test jobs not present in the current dataset
    valid_job_ids = {item.get("job_id") for item in job_records if item.get("job_id")}
    if valid_job_ids:
        db.query(Job).filter(~Job.job_id.in_(valid_job_ids)).delete(synchronize_session=False)

    db.commit()
    total = db.query(Job).count()
    return {"inserted": inserted, "updated": updated, "total": total}


def seed_jobs(json_path: str = None) -> dict:
    if not json_path:
        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "jobs.json")

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Job dataset file not found at: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        job_records = json.load(f)

    # Ensure tables and migrations exist
    create_tables()

    db = SessionLocal()
    try:
        res = seed_jobs_from_records(db, job_records)
        print(f"[OK] Job Seeder completed: {res['inserted']} inserted, {res['updated']} updated, {res['total']} total jobs in database.")
        return res
    except Exception as e:
        db.rollback()
        print(f"[FAIL] Error seeding jobs: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_jobs()
