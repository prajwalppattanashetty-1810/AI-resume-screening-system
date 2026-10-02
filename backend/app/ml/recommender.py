"""
Job Recommendation Engine using TF-IDF Vectorization and Cosine Similarity.

Part of Phase 6: AI Job Recommendation Engine.
Combines textual TF-IDF cosine similarity (70%) with transparent required skill matching (30%).
"""

import re
import logging
from typing import List, Dict, Optional, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.skill_extraction_service import SkillExtractionService
from app.ml.preprocessor import TextPreprocessor

logger = logging.getLogger(__name__)


class JobRecommender:
    """
    ML-based Job Recommendation Engine.
    
    Architecture:
    1. Textual Representation: Builds a unified contextual corpus for each job
       (title, category, description, required skills, preferred skills, responsibilities).
    2. Feature Extraction: Fits a sublinear TF-IDF vectorizer (unigrams + bigrams)
       across the job corpus and transforms candidate resumes into the same vector space.
    3. Cosine Similarity: Computes the directional cosine similarity between resume
       and job TF-IDF vectors (0.0 to 1.0).
    4. Skill Taxonomy Matching: Transparently calculates exact and alias-normalized
       matches for required and preferred skills.
    5. Combined Scoring: Computes a weighted composite score (default 70% TF-IDF, 30% Skill Match).
    """

    def __init__(self, tfidf_weight: float = 0.7, skill_weight: float = 0.3):
        self.tfidf_weight = tfidf_weight
        self.skill_weight = skill_weight
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.job_tfidf_matrix = None
        self.job_records: List[Dict[str, Any]] = []
        self.job_texts: List[str] = []
        self.skill_extractor = SkillExtractionService()
        self.text_preprocessor = TextPreprocessor()

    @staticmethod
    def build_job_text(job: Any) -> str:
        """
        Builds a rich, cohesive text representation of a job for TF-IDF vectorization.
        Accepts SQLAlchemy Job model or dictionary.
        """
        if isinstance(job, dict):
            title = job.get("title", "")
            company = job.get("company", "")
            category = job.get("category", "")
            description = job.get("description", "")
            req_skills = job.get("required_skills", [])
            pref_skills = job.get("preferred_skills", [])
            responsibilities = job.get("responsibilities", [])
            education = job.get("education", "")
            location = job.get("location", "")
            work_mode = job.get("work_mode", "")
            exp_level = job.get("experience_level", "")
        else:
            title = getattr(job, "title", "")
            company = getattr(job, "company", "")
            category = getattr(job, "category", "")
            description = getattr(job, "description", "")
            req_skills = getattr(job, "required_skills", [])
            pref_skills = getattr(job, "preferred_skills", [])
            responsibilities = getattr(job, "responsibilities", [])
            education = getattr(job, "education", "")
            location = getattr(job, "location", "")
            work_mode = getattr(job, "work_mode", "")
            exp_level = getattr(job, "experience_level", "")

        req_str = " ".join(req_skills) if isinstance(req_skills, list) else str(req_skills or "")
        pref_str = " ".join(pref_skills) if isinstance(pref_skills, list) else str(pref_skills or "")
        resp_str = " ".join(responsibilities) if isinstance(responsibilities, list) else str(responsibilities or "")

        # Repeat title, category, and required skills to give appropriate semantic weight in TF-IDF space
        parts = [
            title,
            title,
            category,
            req_str,
            req_str,
            pref_str,
            resp_str,
            description,
            education,
            location,
            work_mode,
            exp_level
        ]
        return " ".join([p.strip() for p in parts if p and str(p).strip()])

    def fit(self, jobs: List[Any], job_metadata: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Fit the TF-IDF vectorizer across all job documents and compute the job TF-IDF matrix.
        """
        if not jobs:
            self.vectorizer = None
            self.job_tfidf_matrix = None
            self.job_records = []
            self.job_texts = []
            return

        self.job_records = jobs
        self.job_texts = [self.build_job_text(j) for j in jobs]

        # Sublinear TF scaling helps prevent long descriptions from dominating short ones
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=12000,
            sublinear_tf=True
        )
        self.job_tfidf_matrix = self.vectorizer.fit_transform(self.job_texts)

    def calculate_cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between two single vectors."""
        if vec1 is None or vec2 is None:
            return 0.0
        # Ensure 2D arrays
        if hasattr(vec1, "reshape") and len(vec1.shape) == 1:
            vec1 = vec1.reshape(1, -1)
        if hasattr(vec2, "reshape") and len(vec2.shape) == 1:
            vec2 = vec2.reshape(1, -1)
        sim = cosine_similarity(vec1, vec2)
        return float(sim[0][0])

    def match_skills(
        self,
        candidate_skills: List[str],
        required_skills: List[str],
        preferred_skills: Optional[List[str]] = None
    ) -> Tuple[List[str], List[str], List[str], float]:
        """
        Calculates exact and alias-normalized skill matches against job requirements.
        
        Returns:
            (matched_required, missing_required, matched_preferred, required_match_percentage)
        """
        cand_normalized: Dict[str, str] = {}
        for s in candidate_skills:
            if not s:
                continue
            norm = self.skill_extractor.normalize_skill(str(s))
            key = norm if norm else str(s).strip().title()
            cand_normalized[key.lower()] = key

        # Normalize required skills
        matched_required: List[str] = []
        missing_required: List[str] = []

        clean_req = required_skills if isinstance(required_skills, list) else []
        for s in clean_req:
            if not s:
                continue
            norm = self.skill_extractor.normalize_skill(str(s))
            target_name = norm if norm else str(s).strip()
            if target_name.lower() in cand_normalized:
                matched_required.append(target_name)
            else:
                missing_required.append(target_name)

        # Normalize preferred skills
        matched_preferred: List[str] = []
        clean_pref = preferred_skills if isinstance(preferred_skills, list) else []
        for s in clean_pref:
            if not s:
                continue
            norm = self.skill_extractor.normalize_skill(str(s))
            target_name = norm if norm else str(s).strip()
            if target_name.lower() in cand_normalized and target_name not in matched_required:
                matched_preferred.append(target_name)

        total_req = len(clean_req)
        if total_req == 0:
            match_percentage = 100.0
        else:
            match_percentage = (len(matched_required) / total_req) * 100.0

        return matched_required, missing_required, matched_preferred, match_percentage

    @staticmethod
    def generate_explanation(
        title: str,
        matched_required: List[str],
        missing_required: List[str],
        matched_preferred: List[str],
        skill_match_pct: float,
        tfidf_similarity: float
    ) -> str:
        """
        Generates a transparent, professional rationale for why a job was recommended.
        Avoids making unsupported claims about the candidate.
        """
        parts = []

        if matched_required:
            skills_str = ", ".join(matched_required[:3])
            parts.append(f"Matches your core proficiencies in {skills_str} ({skill_match_pct:.0f}% of required skills met).")
        elif skill_match_pct == 0 and tfidf_similarity > 0.15:
            parts.append("Matched primarily based on transferable domain keywords and overall experience context.")
        else:
            parts.append("Limited required technical skill overlap identified for this position.")

        if matched_preferred:
            pref_str = ", ".join(matched_preferred[:2])
            parts.append(f"Includes bonus preferred skills: {pref_str}.")

        if missing_required:
            miss_str = ", ".join(missing_required[:2])
            parts.append(f"To maximize competitiveness, consider developing skills in {miss_str}.")

        return " ".join(parts)

    def recommend(
        self,
        resume_text: str,
        candidate_skills: Optional[List[str]] = None,
        jobs: Optional[List[Any]] = None,
        top_n: int = 5,
        category_filter: Optional[str] = None,
        location_filter: Optional[str] = None,
        experience_filter: Optional[str] = None,
        tfidf_weight: Optional[float] = None,
        skill_weight: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Computes hybrid recommendations for a resume against available jobs.
        
        Args:
            resume_text: Raw or preprocessed candidate resume text.
            candidate_skills: Structured candidate skills.
            jobs: Available jobs. If None, uses previously fitted jobs.
            top_n: Number of recommendations to return.
            category_filter: Optional category restriction.
            location_filter: Optional location keyword restriction.
            experience_filter: Optional experience level restriction.
            tfidf_weight: Weight for textual cosine similarity (default: 0.70).
            skill_weight: Weight for required skill match percentage (default: 0.30).
        """
        w_tfidf = self.tfidf_weight if tfidf_weight is None else tfidf_weight
        w_skill = self.skill_weight if skill_weight is None else skill_weight
        skills_list = candidate_skills or []

        # If jobs provided, fit them; otherwise verify fitted state
        if jobs is not None:
            self.fit(jobs)

        if not self.job_records or self.vectorizer is None or self.job_tfidf_matrix is None:
            return []

        # Prepare resume text
        clean_resume = (resume_text or "").strip()
        # Enrich resume text with candidate skills to strengthen signal in feature space
        if skills_list:
            clean_resume = f"{clean_resume} {' '.join(skills_list)}"

        has_resume_content = bool(clean_resume and any(c.isalnum() for c in clean_resume))

        if has_resume_content:
            try:
                resume_vector = self.vectorizer.transform([clean_resume])
                similarities = cosine_similarity(resume_vector, self.job_tfidf_matrix)[0]
            except Exception as e:
                logger.error(f"Error transforming resume vector: {e}")
                similarities = np.zeros(len(self.job_records))
        else:
            similarities = np.zeros(len(self.job_records))

        recommendations = []

        for idx, job in enumerate(self.job_records):
            # Extract job fields safely (works with SQLAlchemy model or dict)
            if isinstance(job, dict):
                job_id = job.get("job_id", f"JOB-{job.get('id', idx)}")
                numeric_id = job.get("id", idx + 1)
                title = job.get("title", "Software Position")
                company = job.get("company", "Tech Company")
                category = job.get("category", "Technology")
                location = job.get("location", "Bengaluru, India")
                work_mode = job.get("work_mode", "Hybrid")
                experience_level = job.get("experience_level", "Entry-level")
                salary_range = job.get("salary_range")
                req_skills = job.get("required_skills", [])
                pref_skills = job.get("preferred_skills", [])
                description = job.get("description", "")
            else:
                job_id = getattr(job, "job_id", f"JOB-{getattr(job, 'id', idx)}")
                numeric_id = getattr(job, "id", idx + 1)
                title = getattr(job, "title", "Software Position")
                company = getattr(job, "company", "Tech Company")
                category = getattr(job, "category", "Technology")
                location = getattr(job, "location", "Bengaluru, India")
                work_mode = getattr(job, "work_mode", "Hybrid")
                experience_level = getattr(job, "experience_level", "Entry-level")
                salary_range = getattr(job, "salary_range", None)
                req_skills = getattr(job, "required_skills", [])
                pref_skills = getattr(job, "preferred_skills", [])
                description = getattr(job, "description", "")

            # Apply runtime filters
            if category_filter and category_filter.lower() != "all" and category.lower() != category_filter.lower():
                continue

            if location_filter and location_filter.lower() != "all" and location_filter.lower() not in location.lower():
                continue

            if experience_filter and experience_filter.lower() != "all" and experience_filter.lower() != experience_level.lower():
                continue

            # 1. Cosine similarity score [0.0 - 1.0]
            raw_tfidf = float(similarities[idx]) if idx < len(similarities) else 0.0
            tfidf_sim = max(0.0, min(1.0, raw_tfidf))

            # 2. Skill match calculation
            matched_req, missing_req, matched_pref, skill_match_pct = self.match_skills(
                skills_list,
                req_skills,
                pref_skills
            )

            # 3. Combined score [0.0 - 100.0]
            # TF-IDF similarity (0-1) scaled to 0-100 * w_tfidf + skill_match_pct (0-100) * w_skill
            combined_score = (tfidf_sim * 100.0 * w_tfidf) + (skill_match_pct * w_skill)
            combined_score = round(max(0.0, min(100.0, combined_score)), 1)

            # 4. Human-readable explanation
            explanation = self.generate_explanation(
                title=title,
                matched_required=matched_req,
                missing_required=missing_req,
                matched_preferred=matched_pref,
                skill_match_pct=skill_match_pct,
                tfidf_similarity=tfidf_sim
            )

            recommendations.append({
                "job_id": job_id,
                "job_numeric_id": numeric_id,
                "title": title,
                "company": company,
                "category": category,
                "location": location,
                "work_mode": work_mode,
                "experience_level": experience_level,
                "salary_range": salary_range,
                "description": description,
                "tfidf_similarity": round(tfidf_sim, 4),
                "skill_match_percentage": round(skill_match_pct, 1),
                "match_score": combined_score,
                "matched_skills": matched_req,
                "missing_skills": missing_req,
                "preferred_skill_matches": matched_pref,
                "explanation": explanation,
                "job_raw": job
            })

        # Sort descending by match_score, then tfidf_similarity
        recommendations.sort(key=lambda x: (x["match_score"], x["tfidf_similarity"]), reverse=True)

        return recommendations[:top_n]
