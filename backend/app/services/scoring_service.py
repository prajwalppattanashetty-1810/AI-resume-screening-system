"""
Scoring Service — Computes multi-dimensional resume strength scores and generates
actionable, prioritized improvement recommendations for candidates.

Part of Phase 8: Final System Integration, UI Enhancement & Production Readiness.
"""

from typing import Dict, List, Any, Optional
import re


class ScoringService:
    """
    Evaluates resume strength across 5 dimensions:
    1. Technical Skills (diversity, volume, and proficiency)
    2. Projects (technical deliverables, tech stacks, and practical application)
    3. Work Experience (roles, durations, and action-oriented impact)
    4. Education (degree clarity, institution, graduation year, and GPA/CGPA)
    5. Structural Completeness (essential contact and section coverage)
    """

    def calculate_skill_score(self, skills_data: Any) -> float:
        """
        Calculates skill score (0 - 100) based on skill count and domain diversity.
        """
        if not skills_data:
            return 0.0

        all_skills = []
        categories = set()

        if isinstance(skills_data, dict):
            # Categorized skills dict or skills analysis object
            if "skills" in skills_data and isinstance(skills_data["skills"], list):
                for s in skills_data["skills"]:
                    if isinstance(s, dict):
                        all_skills.append(s.get("name", ""))
                        if s.get("category"):
                            categories.add(s["category"])
                    elif isinstance(s, str):
                        all_skills.append(s)
            elif "categorized_skills" in skills_data and isinstance(skills_data["categorized_skills"], dict):
                for cat, s_list in skills_data["categorized_skills"].items():
                    if isinstance(s_list, list) and s_list:
                        categories.add(cat)
                        all_skills.extend(s_list)
            else:
                for k, v in skills_data.items():
                    if isinstance(v, list) and v:
                        categories.add(k)
                        all_skills.extend(v)
        elif isinstance(skills_data, list):
            all_skills = [str(s) for s in skills_data if s]

        count = len(set(all_skills))
        cat_count = len(categories)

        # Baseline: 10 skills = 60 pts; up to 20 skills = 80 pts
        count_score = min(60.0, count * 3.0) + (min(20.0, (count - 10) * 2.0) if count > 10 else 0.0)
        # Domain diversity: each domain gives 5 pts up to 20 pts (4+ domains)
        diversity_score = min(20.0, cat_count * 5.0)

        total_score = min(100.0, max(0.0, count_score + diversity_score))
        return round(total_score, 1)

    def calculate_projects_score(self, projects: List[Any]) -> float:
        """
        Calculates project score (0 - 100) based on project count, descriptions, and tech stacks.
        """
        if not projects or not isinstance(projects, list):
            return 0.0

        p_count = len(projects)
        if p_count == 0:
            return 0.0

        base_score = min(40.0, p_count * 20.0)  # 2 projects = 40 pts

        quality_pts = 0.0
        for p in projects:
            if isinstance(p, dict):
                desc = p.get("description", "") or ""
                techs = p.get("technologies", []) or []
                # Points for detailed description
                if len(desc) > 50:
                    quality_pts += 10.0
                elif len(desc) > 20:
                    quality_pts += 5.0
                # Points for explicit tech stack
                if len(techs) >= 2:
                    quality_pts += 15.0
                elif len(techs) == 1:
                    quality_pts += 8.0

        total = min(100.0, base_score + quality_pts)
        return round(total, 1)

    def calculate_experience_score(self, experience: List[Any]) -> float:
        """
        Calculates experience score (0 - 100) based on roles, durations, and descriptions.
        """
        if not experience or not isinstance(experience, list):
            return 0.0

        exp_count = len(experience)
        if exp_count == 0:
            return 0.0

        # Base score: 1 role = 40 pts, 2 roles = 60 pts, 3+ roles = 70 pts
        base_score = 40.0 if exp_count == 1 else (60.0 if exp_count == 2 else 70.0)

        quality_pts = 0.0
        for exp in experience:
            if isinstance(exp, dict):
                dur = exp.get("duration", "") or ""
                desc = exp.get("description", "") or ""
                if dur:
                    quality_pts += 8.0
                if len(desc) > 50:
                    quality_pts += 10.0
                elif len(desc) > 15:
                    quality_pts += 5.0

        total = min(100.0, base_score + quality_pts)
        return round(total, 1)

    def calculate_education_score(self, education: Any) -> float:
        """
        Calculates education score (0 - 100) based on degree clarity, institution, year, and GPA.
        """
        if not education:
            return 0.0

        edu_list = education if isinstance(education, list) else [education]
        if not edu_list:
            return 0.0

        score = 0.0
        first_edu = edu_list[0] if isinstance(edu_list[0], dict) else {}

        degree = first_edu.get("degree", "") or ""
        institution = first_edu.get("institution", "") or ""
        year = first_edu.get("graduation_year", "") or ""
        cgpa = first_edu.get("cgpa", "") or ""

        if degree:
            score += 40.0  # Clear degree title
        if institution:
            score += 30.0  # College/University identified
        if year:
            score += 15.0  # Graduation year noted
        if cgpa:
            score += 15.0  # Academic metric provided

        return round(min(100.0, max(0.0, score)), 1)

    def calculate_completeness_score(self, resume_data: Dict[str, Any]) -> float:
        """
        Calculates completeness score (0 - 100) checking presence of core resume sections.
        """
        if not resume_data:
            return 0.0

        profile = resume_data.get("profile", {}) if "profile" in resume_data else resume_data
        checks = {
            "name": bool(profile.get("name")),
            "email": bool(profile.get("email")),
            "phone": bool(profile.get("phone")),
            "education": bool(profile.get("education")),
            "skills": bool(profile.get("skills") or resume_data.get("skills_analysis")),
            "projects": bool(profile.get("projects")),
            "experience": bool(profile.get("experience")),
            "certifications": bool(profile.get("certifications")),
        }

        # Weighting:
        # Name: 10, Email: 15, Phone: 10, Education: 20, Skills: 20, Projects: 15, Experience: 5, Certs: 5
        weights = {
            "name": 10.0,
            "email": 15.0,
            "phone": 10.0,
            "education": 20.0,
            "skills": 20.0,
            "projects": 15.0,
            "experience": 5.0,
            "certifications": 5.0
        }

        total = sum(weights[k] for k, v in checks.items() if v)
        return round(min(100.0, max(0.0, total)), 1)

    def calculate_resume_score(self, resume_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Computes composite resume score and breakdown.
        """
        profile = resume_data.get("profile", {}) if "profile" in resume_data else resume_data
        skills_data = resume_data.get("skills_analysis") or profile.get("skills")

        skills_score = self.calculate_skill_score(skills_data)
        projects_score = self.calculate_projects_score(profile.get("projects", []))
        experience_score = self.calculate_experience_score(profile.get("experience", []))
        education_score = self.calculate_education_score(profile.get("education", []))
        completeness_score = self.calculate_completeness_score(resume_data)

        # Weighted composite score
        # Skills: 30%, Experience: 25%, Projects: 20%, Education: 15%, Completeness: 10%
        # If student has 0 experience, redistribute weight to projects and skills
        if experience_score == 0:
            overall = (
                (0.40 * skills_score) +
                (0.30 * projects_score) +
                (0.18 * education_score) +
                (0.12 * completeness_score)
            )
        else:
            overall = (
                (0.30 * skills_score) +
                (0.25 * experience_score) +
                (0.20 * projects_score) +
                (0.15 * education_score) +
                (0.10 * completeness_score)
            )

        overall = round(min(100.0, max(0.0, overall)), 1)

        return {
            "overall": overall,
            "skills": skills_score,
            "projects": projects_score,
            "experience": experience_score,
            "education": education_score,
            "completeness": completeness_score
        }

    def get_improvement_suggestions(
        self,
        resume_data: Dict[str, Any],
        scores: Dict[str, float]
    ) -> List[Dict[str, str]]:
        """
        Generates actionable, prioritized improvement recommendations based on
        sectional score deficits and best-practice screening heuristics.
        """
        suggestions: List[Dict[str, str]] = []
        profile = resume_data.get("profile", {}) if "profile" in resume_data else resume_data

        # 1. Experience & Internships
        exp = profile.get("experience", [])
        if not exp or len(exp) == 0:
            suggestions.append({
                "category": "Work Experience",
                "priority": "High",
                "suggestion": "No formal work experience or internships detected. Add open-source contributions, research assistantships, or freelance projects formatted with clear role titles and date ranges to strengthen your profile."
            })
        elif len(exp) == 1:
            suggestions.append({
                "category": "Work Experience",
                "priority": "Medium",
                "suggestion": "Expand your experience descriptions with quantified impact metrics (e.g., 'Improved API latency by 25%' or 'Processed 50,000+ daily events') to make your contributions compelling to hiring managers."
            })

        # 2. Projects & Deliverables
        projects = profile.get("projects", [])
        if not projects or len(projects) == 0:
            suggestions.append({
                "category": "Projects",
                "priority": "High",
                "suggestion": "No technical projects found. Include at least 2 end-to-end projects with explicit technologies, architectural overviews, and live deployment links."
            })
        else:
            has_empty_tech = any(not p.get("technologies") for p in projects if isinstance(p, dict))
            if has_empty_tech:
                suggestions.append({
                    "category": "Projects",
                    "priority": "Medium",
                    "suggestion": "Specify an explicit 'Technologies Used' stack for all project entries so automated screening parsers can accurately index your hands-on competencies."
                })

        # 3. Technical Skills Breadth
        if scores.get("skills", 0) < 60:
            suggestions.append({
                "category": "Skills Breadth",
                "priority": "High",
                "suggestion": "Technical skills count is below competitive benchmarks. Categorize your proficiencies into Programming Languages, Frameworks, Databases, and Cloud/DevOps tools to pass keyword screening."
            })
        elif scores.get("skills", 0) < 80:
            suggestions.append({
                "category": "Skills Breadth",
                "priority": "Medium",
                "suggestion": "Diversify your skill set by adding modern deployment or storage technologies (e.g. Docker, PostgreSQL, or AWS) that complement your primary programming languages."
            })

        # 4. Certifications
        certs = profile.get("certifications", [])
        if not certs or len(certs) == 0:
            suggestions.append({
                "category": "Certifications",
                "priority": "Low",
                "suggestion": "Consider pursuing industry-recognized cloud or domain certifications (e.g. AWS Cloud Practitioner, Google Data Analytics, or Meta Frontend Developer) to validate your continuous learning."
            })

        # 5. Education & Academic Details
        edu = profile.get("education", [])
        if edu and isinstance(edu, list):
            first_edu = edu[0] if isinstance(edu[0], dict) else {}
            if not first_edu.get("cgpa"):
                suggestions.append({
                    "category": "Education",
                    "priority": "Low",
                    "suggestion": "Include your CGPA or academic percentage if it is above 7.0/10 (or 70%), as many enterprise campus recruitment filters utilize minimum grade cutoffs."
                })

        # 6. Top-tier candidate enhancement tip
        if not suggestions:
            suggestions.append({
                "category": "Portfolio & Impact",
                "priority": "Low",
                "suggestion": "Your profile meets high screening benchmarks across all sections. To further distinguish yourself for competitive roles, consider linking open-source repository contributions, technical blog posts, or live demo URLs."
            })

        return suggestions
