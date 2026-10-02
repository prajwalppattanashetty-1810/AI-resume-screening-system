"""
Resume API Routes — Handles resume upload, validation, and analysis.

The upload endpoint saves the PDF and validates it.
The analyze endpoint extracts text and returns the extracted data.
(Full NLP analysis will be added in Phase 3+)
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
import uuid
import os
from typing import Optional, List, Dict, Any
from app.config import get_settings
from app.services.pdf_service import PDFService
from app.services.nlp_service import ResumeParser
from app.ml.preprocessor import TextPreprocessor
from app.services.skill_extraction_service import SkillExtractionService
from app.services.scoring_service import ScoringService
from app.models.database import get_db, ResumeAnalysis, Job
from app.schemas.skill import SkillExtractionRequest, SkillExtractionResponse
from app.schemas.resume import (
    ResumeUploadResponse,
    ResumeAnalysisResponse,
    ResumeProfile,
    ScoreBreakdown,
    ExtractedSkills,
)

router = APIRouter()
settings = get_settings()
pdf_service = PDFService()
nlp_parser = ResumeParser()
text_preprocessor = TextPreprocessor()
skill_extractor = SkillExtractionService()
scoring_service = ScoringService()


class AnalyzeRequest(BaseModel):
    file_id: Optional[str] = None
    fileId: Optional[str] = None

    def get_file_id(self) -> str:
        return self.file_id or self.fileId or ""


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a PDF resume for analysis.

    Validates:
    - File extension is .pdf
    - File size is within limit
    - PDF is readable and contains extractable text
    """
    # Validate file extension
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed. Please upload a .pdf file."
        )

    # Read file content and check size
    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File size ({file_size // 1024}KB) exceeds the "
                   f"{settings.max_upload_size_mb}MB limit."
        )

    # Save file with UUID name (never use original filename for security)
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.pdf"
    filepath = os.path.join(settings.upload_dir, filename)

    os.makedirs(settings.upload_dir, exist_ok=True)
    with open(filepath, "wb") as buffer:
        buffer.write(content)

    # Validate that the PDF is readable and has extractable text
    validation = pdf_service.validate_pdf(filepath)
    if not validation["is_valid"]:
        # Clean up the invalid file
        os.remove(filepath)
        raise HTTPException(status_code=400, detail=validation["error"])

    return ResumeUploadResponse(
        file_id=file_id,
        filename=file.filename,
        message=f"Resume uploaded successfully. "
                f"{validation['page_count']} page(s) detected."
    )


@router.post("/analyze")
async def analyze_resume(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    Analyze an uploaded resume.

    Extracts raw text, runs NLP preprocessing, parses candidate profile,
    and extracts categorized technical skills with evidence-based proficiency.
    """
    target_id = request.get_file_id()
    if not target_id:
        raise HTTPException(status_code=400, detail="Missing file_id parameter.")

    filepath = os.path.join(settings.upload_dir, f"{target_id}.pdf")

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail="Resume not found. It may have been deleted or the ID is invalid."
        )

    try:
        # 1. Extract text and metadata from PDF
        extracted_text = pdf_service.extract_text(filepath)
        metadata = pdf_service.get_metadata(filepath)
        pages = pdf_service.extract_text_by_page(filepath)

        # 2. NLP Preprocessing
        cleaned_text = text_preprocessor.clean_text(extracted_text)
        tokens = text_preprocessor.get_tokens(extracted_text)

        # 3. Information Extraction with ResumeParser
        profile = nlp_parser.parse_resume(extracted_text)

        # 4. Phase 4: Skill Extraction & Categorization
        skills_analysis = skill_extractor.extract_skills_from_profile(profile, full_text=extracted_text)

        # 5. Phase 8: Scoring & Improvement Recommendations
        resume_payload = {"profile": profile, "skills_analysis": skills_analysis}
        scores = scoring_service.calculate_resume_score(resume_payload)
        improvement_suggestions = scoring_service.get_improvement_suggestions(resume_payload, scores)

        # 6. Database persistence
        try:
            record = db.query(ResumeAnalysis).filter(ResumeAnalysis.file_id == target_id).first()
            if not record:
                record = ResumeAnalysis(
                    file_id=target_id,
                    original_filename=f"{target_id}.pdf",
                    extracted_text=extracted_text,
                    skills_json=skills_analysis,
                    analysis_json={"profile": profile, "token_count": len(tokens), "scores": scores, "suggestions": improvement_suggestions},
                    score=scores["overall"]
                )
                db.add(record)
            else:
                record.extracted_text = extracted_text
                record.skills_json = skills_analysis
                record.analysis_json = {"profile": profile, "token_count": len(tokens), "scores": scores, "suggestions": improvement_suggestions}
                record.score = scores["overall"]
            db.commit()
        except Exception as db_err:
            db.rollback()
            # Non-fatal database persistence warning
            print(f"Database save warning: {db_err}")

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the resume: {str(e)}"
        )

    return {
        "file_id": target_id,
        "status": "analyzed",
        "extracted_text": extracted_text,
        "cleaned_text": cleaned_text,
        "tokens": tokens,
        "token_count": len(tokens),
        "metadata": metadata,
        "pages": [
            {"page_number": p["page_number"], "char_count": p["char_count"]}
            for p in pages
        ],
        "text_length": len(extracted_text),
        "profile": profile,
        "skills_analysis": skills_analysis,
        "scores": scores,
        "improvement_suggestions": improvement_suggestions,
        "message": "Resume text extracted and parsed successfully."
    }


@router.post("/extract-skills", response_model=SkillExtractionResponse)
async def extract_resume_skills(request: SkillExtractionRequest, db: Session = Depends(get_db)):
    """
    Dedicated endpoint for Phase 4 Skill Extraction.
    Accepts file_id, structured profile, or raw resume_text.
    Returns normalized, categorized skills with proficiency levels and evidence.
    """
    target_id = request.get_file_id()
    profile = request.profile
    resume_text = request.resume_text or ""
    skills_result = None

    if target_id and not profile and not resume_text:
        record = db.query(ResumeAnalysis).filter(ResumeAnalysis.file_id == target_id).first()
        if record and record.skills_json:
            skills_result = record.skills_json
        else:
            filepath = os.path.join(settings.upload_dir, f"{target_id}.pdf")
            if not os.path.exists(filepath):
                raise HTTPException(status_code=404, detail="Resume not found.")
            resume_text = pdf_service.extract_text(filepath)
            profile = nlp_parser.parse_resume(resume_text)

    if not skills_result:
        if not profile and resume_text:
            profile = nlp_parser.parse_resume(resume_text)

        if not profile:
            profile = {}

        skills_result = skill_extractor.extract_skills_from_profile(profile, full_text=resume_text)

        # Persist in SQLite database if file_id is provided
        if target_id:
            try:
                record = db.query(ResumeAnalysis).filter(ResumeAnalysis.file_id == target_id).first()
                if not record:
                    record = ResumeAnalysis(
                        file_id=target_id,
                        original_filename=f"{target_id}.pdf",
                        extracted_text=resume_text,
                        skills_json=skills_result
                    )
                    db.add(record)
                else:
                    record.skills_json = skills_result
                db.commit()
            except Exception as db_err:
                db.rollback()
                print(f"Database skill save warning: {db_err}")

    return SkillExtractionResponse(
        file_id=target_id or None,
        total_skills=skills_result["total_skills"],
        categorized_skills=skills_result["categorized_skills"],
        skills=skills_result["skills"],
        message="Skills extracted and categorized successfully."
    )


@router.get("/status/{file_id}")
async def get_resume_status(file_id: str):
    """Check if a resume file exists and is ready for analysis."""
    filepath = os.path.join(settings.upload_dir, f"{file_id}.pdf")

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Resume not found.")

    metadata = pdf_service.get_metadata(filepath)
    return {
        "file_id": file_id,
        "exists": True,
        "metadata": metadata,
    }


@router.get("/dashboard-stats")
def get_dashboard_stats(
    file_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Comprehensive dashboard statistics aggregating:
    - Overall platform counts (resumes, jobs, average scores)
    - Category and experience distributions
    - Score band distributions
    - Total catalog skills
    - Recent resume activity
    - Optional candidate-specific summary when file_id is provided
    """
    total_resumes = db.query(ResumeAnalysis).count()
    total_jobs = db.query(Job).count()

    avg_score_scalar = db.query(func.avg(ResumeAnalysis.score)).scalar()
    avg_resume_score = round(float(avg_score_scalar), 1) if avg_score_scalar is not None else 74.5

    # Category distribution across jobs
    cat_counts = (
        db.query(Job.category, func.count(Job.id))
        .group_by(Job.category)
        .order_by(func.count(Job.id).desc())
        .all()
    )
    category_distribution = [{"category": c, "count": count} for c, count in cat_counts]

    # Experience level distribution across jobs
    exp_counts = (
        db.query(Job.experience_level, func.count(Job.id))
        .group_by(Job.experience_level)
        .order_by(func.count(Job.id).desc())
        .all()
    )
    experience_distribution = [{"level": lvl, "count": count} for lvl, count in exp_counts]

    # Work mode distribution across jobs
    mode_counts = (
        db.query(Job.work_mode, func.count(Job.id))
        .group_by(Job.work_mode)
        .order_by(func.count(Job.id).desc())
        .all()
    )
    work_mode_distribution = [{"mode": m, "count": count} for m, count in mode_counts]

    # Score bands distribution across analyzed resumes
    all_resumes = db.query(ResumeAnalysis).all()
    score_bands = {
        "Needs Work (<60)": 0,
        "Fair (60-74)": 0,
        "Good (75-89)": 0,
        "Exceptional (90+)": 0,
    }
    for r in all_resumes:
        sc = r.score if r.score is not None else 70.0
        if sc < 60:
            score_bands["Needs Work (<60)"] += 1
        elif sc < 75:
            score_bands["Fair (60-74)"] += 1
        elif sc < 90:
            score_bands["Good (75-89)"] += 1
        else:
            score_bands["Exceptional (90+)"] += 1
    score_distribution = [{"band": b, "count": count} for b, count in score_bands.items()]

    # Skill catalog: unique required and preferred skills across all jobs
    all_skills_set = set()
    jobs = db.query(Job.required_skills, Job.preferred_skills).all()
    for req, pref in jobs:
        if isinstance(req, list):
            all_skills_set.update(req)
        if isinstance(pref, list):
            all_skills_set.update(pref)
    total_skills_catalog = len(all_skills_set)

    # Recent resumes table
    recent_records = (
        db.query(ResumeAnalysis)
        .order_by(ResumeAnalysis.created_at.desc())
        .limit(10)
        .all()
    )
    recent_resumes = []
    for rec in recent_records:
        prof = rec.analysis_json.get("profile", {}) if rec.analysis_json else {}
        name = prof.get("name") or "Candidate"
        s_count = rec.skills_json.get("total_skills", 0) if rec.skills_json else 0
        recent_resumes.append({
            "file_id": rec.file_id,
            "filename": rec.original_filename or f"{rec.file_id}.pdf",
            "name": name,
            "score": rec.score,
            "skills_count": s_count,
            "created_at": rec.created_at.strftime("%Y-%m-%d %H:%M") if rec.created_at else None,
        })

    # Candidate summary if specific file_id is provided
    candidate_summary = None
    if file_id and file_id != "sample":
        target_rec = db.query(ResumeAnalysis).filter(ResumeAnalysis.file_id == file_id).first()
        if target_rec:
            prof = target_rec.analysis_json.get("profile", {}) if target_rec.analysis_json else {}
            sk = target_rec.skills_json or {}
            scores = scoring_service.calculate_resume_score({"profile": prof, "skills_analysis": sk})
            candidate_summary = {
                "file_id": target_rec.file_id,
                "name": prof.get("name") or "Candidate",
                "email": prof.get("email"),
                "phone": prof.get("phone"),
                "scores": scores,
                "total_skills": sk.get("total_skills", 0),
                "experience_count": len(prof.get("experience", [])),
                "projects_count": len(prof.get("projects", [])),
                "education_count": len(prof.get("education", [])),
                "certifications_count": len(prof.get("certifications", [])),
            }

    return {
        "total_resumes": total_resumes,
        "total_jobs": total_jobs,
        "avg_resume_score": avg_resume_score,
        "total_skills_catalog": total_skills_catalog,
        "category_distribution": category_distribution,
        "experience_distribution": experience_distribution,
        "work_mode_distribution": work_mode_distribution,
        "score_distribution": score_distribution,
        "recent_resumes": recent_resumes,
        "candidate_summary": candidate_summary,
    }


@router.get("/improvements/{file_id}")
def get_resume_improvements(file_id: str, db: Session = Depends(get_db)):
    """
    Get detailed score breakdowns and actionable, prioritized improvement
    recommendations for a candidate's resume.
    """
    record = db.query(ResumeAnalysis).filter(ResumeAnalysis.file_id == file_id).first()
    profile = {}
    skills_analysis = {}

    if record:
        if record.analysis_json and "profile" in record.analysis_json:
            profile = record.analysis_json["profile"]
        if record.skills_json:
            skills_analysis = record.skills_json
    else:
        filepath = os.path.join(settings.upload_dir, f"{file_id}.pdf")
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Resume not found.")
        text = pdf_service.extract_text(filepath)
        profile = nlp_parser.parse_resume(text)
        skills_analysis = skill_extractor.extract_skills_from_profile(profile, full_text=text)

    resume_payload = {"profile": profile, "skills_analysis": skills_analysis}
    scores = scoring_service.calculate_resume_score(resume_payload)
    suggestions = scoring_service.get_improvement_suggestions(resume_payload, scores)

    # Persist score if missing
    if record and record.score is None:
        try:
            record.score = scores["overall"]
            db.commit()
        except Exception:
            db.rollback()

    return {
        "file_id": file_id,
        "candidate_name": profile.get("name") or "Candidate",
        "scores": scores,
        "suggestions": suggestions,
        "total_suggestions": len(suggestions),
        "profile_summary": {
            "skills_count": len(skills_analysis.get("skills", [])),
            "experience_count": len(profile.get("experience", [])),
            "projects_count": len(profile.get("projects", [])),
            "education_count": len(profile.get("education", [])),
            "certifications_count": len(profile.get("certifications", [])),
        },
    }


@router.get("/history")
def get_resume_history(limit: int = Query(25, ge=1, le=100), db: Session = Depends(get_db)):
    """
    Get list of recently analyzed resumes with scores and profile summaries.
    """
    records = db.query(ResumeAnalysis).order_by(ResumeAnalysis.created_at.desc()).limit(limit).all()
    items = []
    for r in records:
        prof = r.analysis_json.get("profile", {}) if r.analysis_json else {}
        items.append({
            "file_id": r.file_id,
            "filename": r.original_filename or f"{r.file_id}.pdf",
            "candidate_name": prof.get("name") or "Candidate",
            "score": r.score,
            "skills_count": r.skills_json.get("total_skills", 0) if r.skills_json else 0,
            "experience_count": len(prof.get("experience", [])),
            "projects_count": len(prof.get("projects", [])),
            "education_count": len(prof.get("education", [])),
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else None,
        })
    return {"total": len(items), "resumes": items}

