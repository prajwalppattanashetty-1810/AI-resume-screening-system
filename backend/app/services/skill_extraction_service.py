"""
Skill Extraction Service — Identifies, normalizes, categorizes, and scores technical skills.

Part of Phase 4: Skill Extraction Engine for AI Resume Screening System.
"""

import re
from typing import Dict, List, Optional, Any, Set, Tuple


# ============================================================================
# 1. STRUCTURED SKILL TAXONOMY
# Organized into 8 distinct categories as specified in Phase 4 requirements.
# ============================================================================

SKILL_TAXONOMY: Dict[str, List[str]] = {
    "programming_languages": [
        "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript",
        "R", "PHP", "Go", "Ruby", "Rust", "Kotlin", "Swift", "Scala",
        "Dart", "SQL", "PL/SQL", "Bash", "Shell", "PowerShell", "Perl"
    ],
    "frontend": [
        "HTML", "CSS", "React", "Angular", "Vue.js", "Next.js",
        "Bootstrap", "Tailwind CSS", "Sass", "SCSS", "jQuery", "Redux",
        "Svelte", "Nuxt.js", "HTML5", "CSS3"
    ],
    "backend": [
        "Node.js", "Express.js", "Django", "Flask", "FastAPI",
        "Spring Boot", "ASP.NET", ".NET", "Hibernate", "Laravel",
        "GraphQL", "REST API", "NestJS", "Fastify", "Ruby on Rails"
    ],
    "databases": [
        "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Oracle",
        "Cassandra", "DynamoDB", "Elasticsearch", "Firebase", "MariaDB",
        "SQL Server", "Supabase", "Neo4j"
    ],
    "machine_learning": [
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "Scikit-learn", "TensorFlow", "PyTorch", "Pandas", "NumPy",
        "Matplotlib", "Seaborn", "Keras", "OpenCV", "NLTK", "spaCy",
        "SciPy", "XGBoost", "LightGBM", "CatBoost", "Transformers",
        "Hugging Face", "BERT", "LLM", "Tableau", "Power BI"
    ],
    "cloud_devops": [
        "AWS", "Microsoft Azure", "Google Cloud", "Docker", "Kubernetes",
        "Jenkins", "GitHub Actions", "CI/CD", "Linux", "Terraform",
        "Ansible", "Nginx", "Apache", "Kafka", "Airflow"
    ],
    "development_tools": [
        "Git", "GitHub", "VS Code", "Jupyter Notebook", "Postman",
        "GitLab", "Jira", "Bitbucket", "Linux", "IntelliJ IDEA", "Eclipse"
    ],
    "soft_skills": [
        "Communication", "Leadership", "Teamwork", "Problem Solving",
        "Time Management", "Critical Thinking", "Adaptability", "Collaboration",
        "Work Ethic", "Creativity"
    ]
}

# ============================================================================
# 2. CONFIGURABLE ALIAS MAP
# Maps variations, acronyms, and common typos to their canonical taxonomy name.
# ============================================================================

ALIAS_MAP: Dict[str, str] = {
    # Languages
    "js": "JavaScript",
    "ts": "TypeScript",
    "golang": "Go",
    "py": "Python",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "c-sharp": "C#",
    "plsql": "PL/SQL",
    "pl-sql": "PL/SQL",

    # Frontend
    "reactjs": "React",
    "react.js": "React",
    "react native": "React",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "angularjs": "Angular",
    "nextjs": "Next.js",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",

    # Backend
    "nodejs": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "springboot": "Spring Boot",
    "spring": "Spring Boot",
    "rest": "REST API",
    "restful": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",
    "rails": "Ruby on Rails",
    "dotnet": ".NET",
    "asp.net core": "ASP.NET",

    # Databases
    "postgres": "PostgreSQL",
    "postgre": "PostgreSQL",
    "mongo": "MongoDB",
    "mssql": "SQL Server",

    # Machine Learning / Data Science
    "sklearn": "Scikit-learn",
    "scikitlearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "tf": "TensorFlow",
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "natural language processing": "NLP",
    "computer vision": "Computer Vision",
    "powerbi": "Power BI",

    # Cloud & DevOps
    "azure": "Microsoft Azure",
    "gcp": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "k8s": "Kubernetes",
    "cicd": "CI/CD",
    "ci / cd": "CI/CD",
    "github action": "GitHub Actions",

    # Development Tools
    "vscode": "VS Code",
    "visual studio code": "VS Code",
    "jupyter": "Jupyter Notebook",
    "jupyter notebooks": "Jupyter Notebook"
}


# ============================================================================
# 3. SKILL EXTRACTION ENGINE CLASS
# ============================================================================

class SkillExtractionService:
    """
    Identifies, normalizes, categorizes, and computes evidence-based
    proficiency for skills extracted from resumes.
    """

    def __init__(self, taxonomy: Optional[Dict[str, List[str]]] = None, alias_map: Optional[Dict[str, str]] = None):
        self.taxonomy = taxonomy or SKILL_TAXONOMY
        self.alias_map = {k.lower(): v for k, v in (alias_map or ALIAS_MAP).items()}

        # Build reverse lookup: canonical_lower -> (canonical_name, category)
        self.canonical_lookup: Dict[str, Tuple[str, str]] = {}
        for cat, skills in self.taxonomy.items():
            for skill in skills:
                skill_lower = skill.lower()
                # If a skill exists in multiple categories (e.g. Linux in tools and devops),
                # keep the first or most specific category.
                if skill_lower not in self.canonical_lookup:
                    self.canonical_lookup[skill_lower] = (skill, cat)

        # Pre-compile multi-word skills for greedy matching (longest first)
        all_match_keys = set(self.canonical_lookup.keys()).union(self.alias_map.keys())
        self.sorted_phrases = sorted(
            [k for k in all_match_keys if len(k.split()) > 1 or '-' in k or '.' in k],
            key=lambda x: len(x),
            reverse=True
        )
        self.single_word_keys = {
            k for k in all_match_keys
            if len(k.split()) == 1 and '-' not in k and '.' not in k and k not in ('c', 'r', 'go')
        }

    def normalize_skill(self, raw_name: str) -> Optional[str]:
        """
        Convert a raw or aliased skill name into its canonical taxonomy form.
        Returns None if not recognized in the taxonomy.
        """
        if not raw_name:
            return None
        cleaned = raw_name.strip()
        cleaned_lower = cleaned.lower()

        # 1. Direct alias match
        if cleaned_lower in self.alias_map:
            return self.alias_map[cleaned_lower]

        # 2. Canonical taxonomy match
        if cleaned_lower in self.canonical_lookup:
            return self.canonical_lookup[cleaned_lower][0]

        # 3. Special case for single-letter languages (case-sensitive)
        if cleaned in ("C", "R"):
            return cleaned

        return None

    def get_skill_category(self, canonical_name: str) -> str:
        """Get category name for a canonical skill."""
        lower = canonical_name.lower()
        if lower in self.canonical_lookup:
            return self.canonical_lookup[lower][1]
        return "other"

    def extract_skills_from_text(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract recognizable taxonomy skills from a raw block of text.
        Returns a list of tuples: (canonical_name, matched_text_snippet).
        """
        if not text:
            return []

        results: List[Tuple[str, str]] = []
        seen_canonical: Set[str] = set()
        text_lower = text.lower()

        # 1. Special Handling for Short and Symbol-bearing Programming Languages
        # C++ and C# must be checked with non-word boundaries because '+' and '#' are non-word characters.
        if re.search(r'(?:\bC\+\+(?:$|[\s,/|;)\]\.])|\bcpp\b)', text, re.IGNORECASE):
            results.append(("C++", "C++"))
            seen_canonical.add("C++")

        if re.search(r'(?:\bC\#(?:$|[\s,/|;)\]\.])|\bcsharp\b)', text, re.IGNORECASE):
            results.append(("C#", "C#"))
            seen_canonical.add("C#")

        # Match single-letter C only if uppercase and NOT followed by '+' or '#'
        if re.search(r'(?:^|[\s,/|;(\[])C(?![+#])(?:$|[\s,/|;)\]\.])', text):
            results.append(("C", "C"))
            seen_canonical.add("C")

        # Match single-letter R only if uppercase
        if re.search(r'(?:^|[\s,/|;(\[])R(?:$|[\s,/|;)\]\.])', text):
            results.append(("R", "R"))
            seen_canonical.add("R")

        # Match Go only if uppercase or written as golang
        if re.search(r'\bGo\b', text) or re.search(r'\bgolang\b', text_lower):
            results.append(("Go", "Go"))
            seen_canonical.add("Go")

        # Match .NET
        if re.search(r'(?:^|[\s,/|;(\[])\.NET(?:\s+Core)?(?:$|[\s,/|;)\]\.])', text, re.IGNORECASE):
            results.append((".NET", ".NET"))
            seen_canonical.add(".NET")

        # 2. Multi-word phrases and hyphenated terms (e.g. "Spring Boot", "Machine Learning", "Scikit-learn")
        for phrase in self.sorted_phrases:
            pattern = r'\b' + re.escape(phrase) + r'\b'
            for match in re.finditer(pattern, text_lower):
                canonical = self.normalize_skill(phrase)
                if canonical and canonical not in seen_canonical:
                    snippet = text[max(0, match.start() - 25):min(len(text), match.end() + 25)].strip()
                    results.append((canonical, snippet))
                    seen_canonical.add(canonical)

        # 3. Single-word technical skills (e.g. Python, Docker, PostgreSQL, React)
        for word in self.single_word_keys:
            pattern = r'\b' + re.escape(word) + r'\b'
            for match in re.finditer(pattern, text_lower):
                canonical = self.normalize_skill(word)
                if canonical and canonical not in seen_canonical:
                    snippet = text[max(0, match.start() - 25):min(len(text), match.end() + 25)].strip()
                    results.append((canonical, snippet))
                    seen_canonical.add(canonical)

        return results

    def determine_proficiency(self, sources: List[str], occurrences: int, evidence: List[str]) -> Tuple[str, str]:
        """
        Compute an evidence-based proficiency indicator (Beginner, Intermediate, Advanced, Unknown).

        Heuristics:
        - Advanced: Used in work experience, or across multiple sections (work + projects/certifications)
                    with 3+ occurrences.
        - Intermediate: Used in projects (practical application) or in both skills and projects.
        - Beginner: Listed in skills section only, without practical project or work experience demonstration.
        - Unknown: Insufficient evidence.
        """
        has_experience = "experience" in sources
        has_projects = "projects" in sources
        has_skills_section = "skills_section" in sources

        if has_experience and (has_projects or occurrences >= 2):
            return (
                "Advanced",
                "Demonstrated professional usage across work experience and technical projects."
            )
        elif has_experience:
            return (
                "Advanced",
                "Applied in formal work experience and workplace responsibilities."
            )
        elif has_projects:
            return (
                "Intermediate",
                "Demonstrated in practical project implementations and technical deliverables."
            )
        elif has_skills_section:
            return (
                "Beginner",
                "Listed in resume skills section without documented project or job implementation."
            )

        return ("Unknown", "Mentioned in resume context without documented project or workplace implementation.")

    def extract_skills_from_profile(self, profile: Dict[str, Any], full_text: str = "") -> Dict[str, Any]:
        """
        Comprehensive skill extraction that scans all structured profile components
        (skills section, projects, experience, certifications) and aggregates them.
        """
        # skill_records: canonical_name -> {category, sources: set(), occurrences: int, evidence: list}
        skill_records: Dict[str, Dict[str, Any]] = {}

        def record_skill(canonical: str, source: str, snippet: str = ""):
            category = self.get_skill_category(canonical)
            if canonical not in skill_records:
                skill_records[canonical] = {
                    "name": canonical,
                    "category": category,
                    "sources": set(),
                    "occurrences": 0,
                    "evidence": []
                }
            skill_records[canonical]["sources"].add(source)
            skill_records[canonical]["occurrences"] += 1
            if snippet and len(skill_records[canonical]["evidence"]) < 3:
                clean_snippet = snippet.replace('\n', ' ').strip()
                if clean_snippet and clean_snippet not in skill_records[canonical]["evidence"]:
                    skill_records[canonical]["evidence"].append(clean_snippet)

        # 1. Extract from Skills Section
        raw_skills_text = profile.get("skills", "")
        if isinstance(raw_skills_text, dict):
            # If skills section was pre-categorized or structured
            combined_skills = " ".join([" ".join(v) if isinstance(v, list) else str(v) for v in raw_skills_text.values()])
            for skill, snippet in self.extract_skills_from_text(combined_skills):
                record_skill(skill, "skills_section", snippet)
        elif isinstance(raw_skills_text, str) and raw_skills_text:
            for skill, snippet in self.extract_skills_from_text(raw_skills_text):
                record_skill(skill, "skills_section", snippet)

        # 2. Extract from Projects (Technologies, Names, and Descriptions)
        projects = profile.get("projects", [])
        if isinstance(projects, list):
            for proj in projects:
                proj_name = proj.get("name", "Project")

                # Direct technology stack items
                for tech in proj.get("technologies", []):
                    canonical = self.normalize_skill(tech)
                    if canonical:
                        record_skill(canonical, "projects", f"Project '{proj_name}' tech: {tech}")
                    else:
                        # Fallback text search if tech contains multiple items
                        for sub_skill, sub_snip in self.extract_skills_from_text(str(tech)):
                            record_skill(sub_skill, "projects", f"Project '{proj_name}' tech: {tech}")

                # Project title and narrative descriptions
                proj_desc = proj.get("description", "")
                combined_proj_text = f"{proj_name} {proj_desc}".strip()
                if combined_proj_text:
                    for skill, snippet in self.extract_skills_from_text(combined_proj_text):
                        evidence_str = f"Project '{proj_name}': {snippet}" if snippet else f"Project: {proj_name}"
                        record_skill(skill, "projects", evidence_str)

        # 3. Extract from Experience
        experiences = profile.get("experience", [])
        if isinstance(experiences, list):
            for exp in experiences:
                exp_text = f"{exp.get('title', '')} {exp.get('company', '')} {exp.get('description', '')}"
                for skill, snippet in self.extract_skills_from_text(exp_text):
                    record_skill(skill, "experience", snippet)

        # 4. Extract from Certifications
        certifications = profile.get("certifications", [])
        if isinstance(certifications, list):
            for cert in certifications:
                for skill, snippet in self.extract_skills_from_text(cert):
                    record_skill(skill, "certifications", f"Certified in: {cert}")

        # 5. Extract from Full Text if profile sections were incomplete
        if full_text and len(skill_records) < 3:
            for skill, snippet in self.extract_skills_from_text(full_text):
                record_skill(skill, "full_text", snippet)

        # Assemble Output
        categorized_skills: Dict[str, List[str]] = {cat: [] for cat in self.taxonomy.keys()}
        skill_items: List[Dict[str, Any]] = []

        for canonical_name in sorted(skill_records.keys()):
            data = skill_records[canonical_name]
            sources_list = sorted(list(data["sources"]))
            proficiency, reason = self.determine_proficiency(
                sources=sources_list,
                occurrences=data["occurrences"],
                evidence=data["evidence"]
            )

            category = data["category"]
            if category in categorized_skills:
                categorized_skills[category].append(canonical_name)
            else:
                if "other" not in categorized_skills:
                    categorized_skills["other"] = []
                categorized_skills["other"].append(canonical_name)

            skill_items.append({
                "name": canonical_name,
                "category": category,
                "proficiency": proficiency,
                "proficiency_reason": reason,
                "sources": sources_list,
                "occurrences": data["occurrences"],
                "evidence": data["evidence"]
            })

        return {
            "total_skills": len(skill_items),
            "categorized_skills": categorized_skills,
            "skills": skill_items
        }
