# Phase 4: Skill Extraction Engine — Architecture & Developer Guide

## 1. Overview & Architectural Motivation

In modern Applicant Tracking Systems (ATS) and resume recommenders, extracting skills accurately is crucial. While generative LLMs can be used, pure black-box approaches suffer from:
1. **Hallucinations** (inventing skills not in the resume).
2. **High Latency & Cost** (seconds per resume, expensive token costs).
3. **Lack of Explainability** (cannot show exact line/bullet evidence to the recruiter or candidate).

The **Phase 4 Skill Extraction Engine** solves this by using a deterministic, highly optimized, explainable NLP pipeline that combines:
- A curated **8-domain skill taxonomy** with 100+ industry-standard skills.
- An extensible **canonical alias normalization dictionary**.
- **Context-aware regex tokenizers** with boundary safety for short symbols (`C`, `R`, `C++`, `C#`).
- **Evidence-based heuristic proficiency scoring** linking skills to work experience and projects.
- Full SQLite database persistence and a reactive React frontend UI.

---

## 2. Taxonomy Categories

The taxonomy is organized across 8 technical and professional domains:

| Category Key | Category Label | Representative Skills |
| :--- | :--- | :--- |
| `programming_languages` | Programming Languages | Python, Java, C++, C, C#, JavaScript, TypeScript, Go, Rust, Ruby, PHP, Swift, Kotlin, SQL, R, Dart, Scala |
| `frontend` | Frontend Development | React, Angular, Vue.js, HTML, CSS, Tailwind CSS, Next.js, Redux, Svelte, Bootstrap, jQuery |
| `backend` | Backend Frameworks | FastAPI, Flask, Django, Node.js, Express.js, Spring Boot, ASP.NET, NestJS, Ruby on Rails, GraphQL, REST API |
| `databases` | Databases & Storage | PostgreSQL, MySQL, MongoDB, SQLite, Redis, Oracle, Microsoft SQL Server, Cassandra, DynamoDB, Elasticsearch |
| `machine_learning` | Machine Learning & AI | Scikit-learn, TensorFlow, PyTorch, Keras, Pandas, NumPy, NLP, Computer Vision, OpenCV, NLTK, Transformers, Deep Learning, Matplotlib, Seaborn, Tableau, Power BI |
| `cloud_devops` | Cloud & DevOps | AWS, Microsoft Azure, Google Cloud Platform (GCP), Docker, Kubernetes, Jenkins, Terraform, CI/CD, Git, Linux |
| `development_tools` | Development Tools | Git, GitHub, GitLab, VS Code, Postman, JIRA, Docker, Figma, Jupyter Notebook, Linux |
| `soft_skills` | Soft Skills & Leadership | Leadership, Communication, Problem Solving, Teamwork, Critical Thinking, Time Management, Agile, Scrum |

---

## 3. Canonical Normalization & Alias Mapping

Candidates write technical terms in many variations. The engine normalizes every variant to a canonical name before saving or matching:

```python
ALIAS_MAP = {
    # JavaScript variations
    "js": "JavaScript",
    "javascript": "JavaScript",
    
    # React variations
    "react.js": "React",
    "reactjs": "React",
    
    # Machine Learning / Data Science
    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "tf": "TensorFlow",
    "nlp": "Natural Language Processing",
    "cv": "Computer Vision",
    
    # Cloud / Backend / Languages
    "golang": "Go",
    "k8s": "Kubernetes",
    "gcp": "Google Cloud Platform",
    "aws": "AWS",
    "postgres": "PostgreSQL",
    "node": "Node.js",
    "nodejs": "Node.js",
    "cpp": "C++",
    "cplusplus": "C++",
    "csharp": "C#",
    ".net": ".NET",
    "dotnet": ".NET",
}
```

---

## 4. Boundary Safety & False-Positive Prevention

### The Regex Trap with Symbols (`+`, `#`, `.`)
In standard regular expressions, `\b` (word boundary) matches between a word character (`\w`: `[a-zA-Z0-9_]`) and a non-word character (`\W`).
However, in `C++` or `C#`, the `+` and `#` symbols are non-word characters!
If you write `r'\bC\+\+\b'`, the pattern **fails to match** `"C++,"` or `"C++\n"` because `+` followed by `,` is two non-word characters, so no `\b` boundary exists!

**The Solution:**
```python
# Custom symbol lookaround pattern for C++
r'(?:\bC\+\+(?:$|[\s,/|;)\]\.])|\bcpp\b)'

# Custom symbol lookaround pattern for C#
r'(?:\bC#(?:$|[\s,/|;)\]\.])|\bcsharp\b)'
```

### The Single-Letter Trap (`C` and `R`)
Single letters like `C` and `R` frequently trigger false positives:
- English words like `"car"`, `"cat"` or the letter `"c"` in `"e.g."`.
- Words like `"Vitamin C"` or `"Section C"`.
- `C++` getting erroneously parsed as `C`.

**The Solution:**
1. Require uppercase `C` or `R`.
2. Ensure strict non-word lookbehinds and lookaheads.
3. Use negative lookahead `(?![+#])` so `"C++"` or `"C#"` does not match as `"C"`:
```python
# Boundary-safe single-letter C extractor
pattern = r'(?:^|[\s,/|;(\[])C(?![+#])(?:$|[\s,/|;)\]\.])'
```

### Greedy Multi-Word Matching
Multi-word terms must always take precedence over their constituent words (e.g., `"Machine Learning"` before `"Learning"`, `"Spring Boot"` before `"Boot"`). The extractor searches for multi-word phrases first, collects matched spans, and ensures subsequent single-word tokens do not double-count overlapping spans.

---

## 5. Evidence-Based Heuristic Proficiency Scoring

Resumes typically show a skill in multiple places with differing degrees of credibility:
1. **Work Experience Records**: Highest credibility. If a skill was used in an employment role (e.g. `"Software Engineering Intern: Developed services using Python and SQL"`), the candidate has demonstrated real-world production competence.
   - Proficiency: **`Advanced`**
   - Reason: `"Demonstrated through professional employment experience."`
2. **Projects & Technical Stacks**: Hands-on practical implementation.
   - Proficiency: **`Intermediate`**
   - Reason: `"Demonstrated through hands-on project implementation."`
3. **Skills Section / Profile Summary**: Self-declared list without detailed narrative.
   - Proficiency: **`Beginner`**
   - Reason: `"Identified in resume skills section."`
4. **General Keyword Mention**:
   - Proficiency: **`Unknown`**

For every extracted skill, the engine preserves:
- **`sources`**: `["skills_section", "projects", "experience"]`
- **`occurrences`**: Count of mentions across the entire document
- **`evidence`**: Contextual excerpts from the resume (bullet points, descriptions)

---

## 6. API Specifications

### `POST /api/resume/extract-skills`
Accepts `file_id`, structured `profile` (from Phase 3 NLP Parser), or raw `resume_text`.

#### Request Schema:
```json
{
  "file_id": "55bbf530-e0be-41fc-99dd-19947a52c212"
}
```

#### Response Schema:
```json
{
  "file_id": "55bbf530-e0be-41fc-99dd-19947a52c212",
  "total_skills": 32,
  "categorized_skills": {
    "programming_languages": ["C", "C++", "Java", "JavaScript", "Python", "SQL"],
    "frontend": ["React"],
    "backend": ["FastAPI", "Flask", "Node.js"],
    "databases": ["MongoDB", "MySQL", "PostgreSQL", "SQLite"],
    "machine_learning": [
      "Deep Learning",
      "Machine Learning",
      "Matplotlib",
      "NLP",
      "NLTK",
      "NumPy",
      "Pandas",
      "Scikit-learn",
      "Tableau",
      "TensorFlow"
    ],
    "cloud_devops": ["AWS", "Docker", "Google Cloud Platform", "Linux"],
    "development_tools": ["Docker", "Git", "Jupyter Notebook", "Linux", "VS Code"],
    "soft_skills": []
  },
  "skills": [
    {
      "name": "Python",
      "category": "programming_languages",
      "proficiency": "Advanced",
      "proficiency_reason": "Demonstrated through professional employment experience.",
      "sources": ["skills_section", "projects", "experience"],
      "occurrences": 3,
      "evidence": [
        "Software Engineering Intern | Google India ... Developed microservices using Python",
        "Data Science Intern | Flipkart ... Analyzed customer purchase patterns using Python and SQL"
      ]
    }
  ],
  "message": "Skills extracted and categorized successfully."
}
```

---

## 7. Database Persistence

In `backend/app/models/database.py`, the `ResumeAnalysis` model contains the `skills_json` column:
```python
class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(50), unique=True, index=True, nullable=False)
    original_filename = Column(String(255), nullable=False)
    extracted_text = Column(Text, nullable=True)
    skills_json = Column(JSON, nullable=True)    # Stores the full categorized skills payload
    analysis_json = Column(JSON, nullable=True)  # Stores NLP profile & metadata
    created_at = Column(DateTime, default=datetime.utcnow)
```
Whenever `/api/resume/analyze` or `/api/resume/extract-skills` runs, the normalized skill output is committed to SQLite.

---

## 8. Frontend Interface (`SkillsPage.jsx`)

The React frontend presents:
1. **Hero & Domain Metrics**: Total skills count, Active Domains counter (e.g. 7/8), and counts for Advanced, Intermediate, and Beginner tiers.
2. **Domain Group Cards**: Visual layout grouping skills by domain with color-coded badges and icons.
3. **Filter & Search Bar**: Real-time search by skill name or domain, level filters (`Advanced`, `Intermediate`, `Beginner`), and domain tabs.
4. **Evidence & Details Inspector**: Right-hand sticky panel showing:
   - Canonical name & category badge
   - Evaluated proficiency level & explanatory rationale
   - Identified sections (`experience`, `projects`, `skills_section`)
   - Mention frequency
   - Exact highlighted evidence snippets from the resume
5. **Seamless Navigation**: Integrated links connecting `UploadPage` → `AnalysisPage` → `SkillsPage` → `Dashboard`.

---

## 9. Test Suite & Verification Results

### Unit Tests
Located at `backend/tests/test_skill_extraction.py`:
- `test_skill_taxonomy_categories`: Verifies all 8 categories exist and have valid canonical items.
- `test_extract_from_text_basic`: Validates extraction of Python, React, Docker, and AWS from raw text.
- `test_alias_normalization`: Tests `JS` -> `JavaScript`, `sklearn` -> `Scikit-learn`, `react.js` -> `React`.
- `test_short_and_single_letter_skills`: Confirms `C`, `C++`, `C#`, `R`, and `Go` are extracted without edge-case false positives.
- `test_single_letter_false_positive_prevention`: Ensures words like `"cat"`, `"car"`, or `"vitamin c"` are not flagged as `C`.
- `test_proficiency_heuristic_experience`: Validates `Advanced` rating when skill is in work experience.
- `test_proficiency_heuristic_projects`: Validates `Intermediate` rating when skill is in projects.
- `test_proficiency_heuristic_skills_list`: Validates `Beginner` rating when skill only appears in skills section.
- `test_extract_skills_from_profile`: End-to-end profile extraction verifying deduplication, category mapping, and evidence attribution.
- `test_api_extract_skills_endpoint`: FastAPI TestClient validation of `POST /api/resume/extract-skills`.
- `test_analyze_resume_includes_skills`: Ensures `/api/resume/analyze` payload includes Phase 4 skill extraction data.

**Current Test Result:** **80 / 80 Passing** (100%) in 0.51s.

### End-to-End Integration
Executed via `backend/scripts/verify_e2e_integration.py`:
- 13/13 E2E integration verification checks passing against live FastAPI (`127.0.0.1:8000`) and Vite (`127.0.0.1:5173`).
