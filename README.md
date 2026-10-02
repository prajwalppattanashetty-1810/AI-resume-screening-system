# AI Resume Screening & Job Recommendation System

> An enterprise-grade, end-to-end Machine Learning and Natural Language Processing application that parses resumes from raw PDFs, extracts categorized technical skills with evidence-based proficiency, recommends matching job roles using TF-IDF and Cosine Similarity, performs multi-dimensional ATS resume strength scoring, identifies skill deficits, and generates personalized career learning roadmaps.

**Current Status:** ✅ **Phases 1–9 Fully Implemented, Integrated, Optimized & Production Ready**  
- **Pytest Test Suite:** 145 / 145 Tests Passing (100% Green, 0 warnings, 0 errors in 1.14s)
- **Phase 9 Production Readiness Suite:** 11 / 11 End-to-End System Assertions Passing (100% Green)
- **Phase 8 E2E Verification:** 11 / 11 System Verification Checks Passing
- **Phase 7 Deep Verification:** 12 / 12 Skill Gap Checks Passing
- **Phase 1–7 Pipeline Verification:** 23 / 23 Integration Steps Passing
- **Interactive API Documentation:** Swagger UI (`/docs`) and ReDoc (`/redoc`) 100% Operational
- **Frontend Production Build:** Vite v6.4.3 production bundle built cleanly (0 errors)
- **Containerization & Deployment:** Multi-stage Dockerfiles, Docker Compose, Nginx reverse proxy, and Procfile configured
- **Database Status:** 255 Verified Tech Job Records & 75+ Analyzed Resumes in SQLite

---

## 🚀 Quick Start Guide

### Option A: Docker Compose (Recommended for Production / Evaluation)

Run the entire full-stack application (FastAPI backend + React frontend + Nginx proxy + auto-seeded SQLite database) with a single command:

```bash
docker-compose up --build
```

- **Frontend Application**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Interactive Reference**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### Option B: Local Development Setup

#### Prerequisites
- Python 3.9+ (Tested on Python 3.11 & 3.12)
- Node.js 18+ & npm
- Git

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Note: On first startup, the database auto-seeds 255 verified jobs across 17 technology domains if empty.*

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

#### 3. Access Points
- **Web Application**: [http://localhost:5173](http://localhost:5173)
- **SaaS Telemetry Dashboard**: [http://localhost:5173/dashboard](http://localhost:5173/dashboard)
- **Job Explorer**: [http://localhost:5173/jobs](http://localhost:5173/jobs)
- **FastAPI Backend**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI 3.1 Specification**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 📁 System Architecture & Roadmap Overview

```
                      [ Raw PDF Resume ]
                              │
                              ▼
            ┌───────────────────────────────────┐
            │   Phase 2: PyMuPDF Text Extractor │  (Character normalization & metadata)
            └─────────────────┬─────────────────┘
                              │
                              ▼
            ┌───────────────────────────────────┐
            │   Phase 3: NLP Parser & Chunker   │  (Contact regex, section heuristic headers,
            └─────────────────┬─────────────────┘   education, work experience, projects)
                              │
                              ▼
            ┌───────────────────────────────────┐
            │ Phase 4: Skill Extraction Engine  │  (8-domain taxonomy, alias resolution,
            └─────────────────┬─────────────────┘   evidence counting, proficiency scoring)
                              │
             ┌────────────────┴────────────────┐
             ▼                                 ▼
┌───────────────────────────────┐ ┌───────────────────────────────────────┐
│ Phase 5 & 6: Recommender      │ │ Phase 8: Scoring & Improvement Engine │
│ 255 SQLite Jobs Dataset       │ │ 5-Dimensional Resume ATS Score       │
│ TF-IDF + Cosine Similarity    │ │ Prioritized Actionable Recommendations│
│ Composite Match (70% + 30%)   │ │ System SaaS Telemetry Dashboard       │
└────────────┬──────────────────┘ └───────────────────┬───────────────────┘
             │                                        │
             ▼                                        ▼
┌───────────────────────────────┐ ┌───────────────────────────────────────┐
│ Phase 7: Skill Gap Analysis   │ │ Production React 18 UI                │
│ Exact, Partial & Missing Gaps │ │ Dashboard, Explorer, Analysis,        │
│ Personalized Learning Roadmap │ │ Recommendations, Skill Matrix, Action │
└───────────────────────────────┘ └───────────────────────────────────────┘
                              │
                              ▼
            ┌───────────────────────────────────┐
            │ Phase 9: Testing, Optimization,   │  (145 pytests, Dockerization, ReDoc fix,
            │ Security & Deployment Readiness   │   Nginx proxy, hardened .gitignore)
            └───────────────────────────────────┘
```

| Phase | Milestone | Status | Key Deliverables |
| :--- | :--- | :---: | :--- |
| **Phase 1** | Architecture & Scaffolding | ✅ Complete | FastAPI + React 18 + Vite + Tailwind + SQLite setup |
| **Phase 2** | PDF Resume Extraction | ✅ Complete | PyMuPDF text & metadata extraction with ligature normalization |
| **Phase 3** | NLP Information Extraction | ✅ Complete | Section detection, contact info, education, experience, and projects |
| **Phase 4** | Skill Taxonomy & Competency | ✅ Complete | 8 technical domains, 120+ aliases, evidence-based proficiency |
| **Phase 5** | Job Dataset Management | ✅ Complete | 255 benchmark job records across 17 technology domains |
| **Phase 6** | AI Job Recommendation Engine | ✅ Complete | TF-IDF (12,000 features, sublinear TF) + Cosine Similarity (70%) + Skill Match (30%) |
| **Phase 7** | Skill Gap Analysis Engine | ✅ Complete | Gap classification, coverage metrics, and personalized learning roadmaps |
| **Phase 8** | Final System Integration & UI | ✅ Complete | Multi-dimensional scoring, prioritized improvement recommendations, SaaS dashboard |
| **Phase 9** | Testing, Optimization & Deployment | ✅ Complete | 145 pytests, 0 warnings, Docker Compose, Nginx proxy, ReDoc multi-CDN, hardened Git |

---

## 🌟 Key Functional Modules

### 1. Multi-Dimensional Resume Scoring Engine (`ScoringService`)
The resume scoring engine evaluates applicant quality across 5 dimensions on a 0–100 scale:

1. **Technical Skills Dimension (0–100%)**:
   - Skill Volume: 10 skills = 60 pts; up to 20 skills = 80 pts.
   - Domain Diversity: Each distinct technical category (Programming, Frameworks, Cloud, Databases) adds 5 pts (up to 20 pts for 4+ domains).
2. **Projects & Practical Implementation (0–100%)**:
   - Project Volume: 2 projects = 40 pts base.
   - Project Depth: Detailed technical descriptions (>50 chars) award +10 pts.
   - Tech Stack Attribution: Explicit technologies (+15 pts for 2+ labeled technologies).
3. **Work Experience & Professional Impact (0–100%)**:
   - Role Counts: 1 role = 40 pts, 2 roles = 60 pts, 3+ roles = 70 pts.
   - Duration & Dates: Valid date ranges award +8 pts.
   - Impact Descriptions: Action verbs and quantified impact metrics award +10 pts.
4. **Education & Academics (0–100%)**:
   - Degree title clarity (40 pts)
   - Institution identification (30 pts)
   - Graduation year (15 pts)
   - Academic metric / CGPA / percentage (15 pts)
5. **Structural Completeness (0–100%)**:
   - Evaluates coverage of essential resume sections: Name (10%), Email (15%), Phone (10%), Education (20%), Skills (20%), Projects (15%), Experience (5%), Certifications (5%).

#### Composite Weighted ATS Score Formula
For experienced candidates:
$$\text{Overall ATS Score} = 0.30 \times \text{Skills} + 0.25 \times \text{Experience} + 0.20 \times \text{Projects} + 0.15 \times \text{Education} + 0.10 \times \text{Completeness}$$

For freshman / early-career profiles with 0 experience, weights dynamically rebalance toward hands-on project deliverables:
$$\text{Overall ATS Score} = 0.40 \times \text{Skills} + 0.30 \times \text{Projects} + 0.18 \times \text{Education} + 0.12 \times \text{Completeness}$$

---

### 2. Prioritized Improvement Recommendations Engine
The scoring engine analyzes deficits and automatically generates prioritized, actionable advice:

- **Work Experience Gaps**: Identifies missing internships and suggests adding open-source contributions, research work, or freelance deliverables.
- **Project Detail Enhancements**: Flags projects lacking explicit "Technologies Used" tags so candidates can pass ATS keyword parsers.
- **Skill Breadth Expansion**: Alerts candidates when their skill count is below competitive benchmarks or lacks modern DevOps / Cloud tooling.
- **Academic Cutoff Advisory**: Suggests including CGPA or percentage for campus screening cutoffs.
- **High-Scorer Polish**: Guides competitive applicants on portfolio hosting, GitHub contribution links, and system design highlights.
- **Priority Labels**: Categorized into `High`, `Medium`, and `Low` priority badges.

---

### 3. SaaS Telemetry & Analytics Dashboard (`DashboardPage.jsx`)
A centralized management console delivering real-time database intelligence:

- **Key Performance Indicators (KPIs)**: Total Resumes Analyzed (real SQLite count), Active Job Listings (255), Average Resume Score, and Total Catalog Skills (115+ unique technologies).
- **Interactive Visualizations (Recharts)**:
  - Job Sector Distribution: BarChart breakdown of top hiring categories.
  - Resume Quality Distribution: Score bands (`Needs Work <60%`, `Fair 60–74%`, `Good 75–89%`, `Exceptional 90%+`).
  - Workplace Mode Breakdown: PieChart of Hybrid (35%), Remote (37%), and On-site (27%).
  - Seniority Breakdown: Experience levels (Entry, Junior, Mid, Senior).
- **Candidate Focus Spotlight**: Instant deep dive into any selected applicant, displaying candidate contact info, score breakdown gauges, and direct links.
- **Applicant History Table**: Paginated view of recent resume analyses with quick action buttons for Profile, Recommendations, and Improvements.

---

## 🧠 Core Machine Learning & NLP Methodologies

### 1. Hybrid Job Recommendation Engine
Combines content-based semantic matching with keyword precision:

$$\text{Composite Match Score} = 0.70 \times \text{TF-IDF Cosine Similarity} + 0.30 \times \text{Skill Match Ratio}$$

- **TF-IDF Feature Space**: 12,000 features, 1-to-3 n-grams, sublinear term frequency scaling ($1 + \log(\text{tf})$), smooth IDF weighting.
- **Cosine Similarity**: Computes directional cosine angle between the candidate vector and every job description vector in the SQLite database.
- **Skill Matching**: Calculates exact and partial intersection between candidate extracted skills and job required competencies.
- **Low Latency**: Inference executes in ~90ms across 255 job records without requiring GPU hardware.

### 2. Skill Gap Classification Heuristics
- **✓ Matched**: Direct presence in extracted profile with appropriate proficiency for role seniority.
- **▲ Partial Match**:
  - Proficiency deficit (Beginner level for Senior requirement).
  - Transferable domain cluster (e.g. `PyTorch` $\longleftrightarrow$ `TensorFlow`, `FastAPI` $\longleftrightarrow$ `Django`/`Flask`, `AWS` $\longleftrightarrow$ `GCP`/`Azure`).
- **✕ Missing**: Neither direct skill nor related mental model found in candidate profile.

---

## 🔒 Security, Privacy & Data Protection Safeguards

1. **UUID Pseudonymization**: Uploaded files are immediately renamed to cryptographically secure UUIDs (`uuid.uuid4()`), stripping original filenames to prevent path traversal attacks and information disclosure.
2. **File Validation**: Strict file inspection enforcing `.pdf` extension checks and 10MB maximum payload restrictions. Non-PDF files (e.g. `.txt`, `.exe`) return clean HTTP 400 Bad Request responses.
3. **Repository Cleanliness**: Hardened `.gitignore` guarantees that candidate resumes (`backend/uploads/*.pdf`), SQLite database files (`*.db`), virtual environments, and `.env` secrets are never committed to version control.
4. **Local Data Processing**: All NLP parsing, skill extraction, and machine learning inferences execute completely locally without calling external commercial third-party LLM APIs.

---

## 📡 API Reference Summary

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/resume/upload` | POST | Upload PDF resume, validate size/type, assign UUID, save to disk |
| `/api/resume/analyze` | POST | Full NLP parse, skill extraction, ATS score computation, and DB persistence |
| `/api/resume/dashboard-stats` | GET | Aggregated platform stats, distributions, and candidate spotlight |
| `/api/resume/improvements/{file_id}` | GET | Dimensional score breakdown and prioritized improvement tips |
| `/api/resume/history` | GET | List recently analyzed resumes with scores and metadata |
| `/api/jobs` | GET | Paginated jobs with category, location, and seniority filters |
| `/api/jobs/search` | GET | Fast keyword search across titles, skills, and descriptions |
| `/api/jobs/categories` | GET | List of 17 distinct industry domains with active opportunity counts |
| `/api/jobs/stats` | GET | Comprehensive job dataset statistics across categories and modes |
| `/api/jobs/recommend` | POST | Hybrid TF-IDF cosine recommendations |
| `/api/skill-gap/analyze` | POST | Skill gap analysis and personalized learning roadmap |
| `/api/skill-gap/analyze/{file_id}/{job_id}` | GET | Browser deep-linking endpoint for gap reports |
| `/health` | GET | Service liveness probe with version and UTC timestamp |
| `/docs` | GET | Interactive Swagger UI API documentation |
| `/redoc` | GET | High-reliability ReDoc technical reference with multi-CDN fallback |

---

## 🧪 Comprehensive Verification Suite

Execute the full suite of verification commands:

```bash
# 1. Run Complete Backend Pytest Suite (145 Tests — 100% Pass in ~1.1s)
cd backend
.\venv\Scripts\pytest -v

# 2. Run Phase 9 Comprehensive Production Readiness Suite (11 Checks)
.\venv\Scripts\python.exe scripts\verify_phase9_readiness.py

# 3. Run Phase 8 End-to-End System Verification (11 Checks)
.\venv\Scripts\python.exe scripts\verify_phase8_e2e.py

# 4. Run Phase 7 Deep Skill Gap Verification (12 Checks)
.\venv\Scripts\python.exe scripts\verify_phase7_deep.py

# 5. Run Phase 1–7 Pipeline Integration Verification (23 Checks)
.\venv\Scripts\python.exe scripts\verify_e2e_integration.py

# 6. Verify Swagger & ReDoc Documentation
.\venv\Scripts\python.exe scripts\verify_redoc_and_docs.py

# 7. Frontend Production Build Check
cd ..\frontend
npm run build
```

---

## 🌐 Production & Cloud Deployment Guide

### Deploying with Docker Compose
```bash
# Clone the repository
git clone <your-repo-url>
cd "ML PROJECT"

# Launch backend, frontend, and reverse proxy
docker-compose up -d --build

# View logs
docker-compose logs -f
```

### Deploying Backend to Render / Railway
1. **Repository**: Push the project to GitHub.
2. **Build Command**: `pip install -r backend/requirements.txt`
3. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   - `BACKEND_HOST=0.0.0.0`
   - `PORT=8000`
   - `FRONTEND_URL=https://your-frontend-domain.com`

### Deploying Frontend to Vercel / Netlify
1. **Root Directory**: `frontend`
2. **Build Command**: `npm run build`
3. **Output Directory**: `dist`
4. **Environment Variable**: `VITE_API_URL=https://your-backend-domain.com`

---

## 🎓 College Demonstration & Viva Walkthrough Guide

Use this scripted walkthrough for project reviews, placement interviews, and viva presentations:

### Step 1: System Overview & Architecture (1 Minute)
1. Open the **System Analytics Dashboard** at [http://localhost:5173/dashboard](http://localhost:5173/dashboard).
2. Point out real-time telemetry: 255 verified tech jobs, 75+ analyzed candidate resumes, and average ATS benchmark score.
3. Show the interactive Recharts distribution graphs (Job Categories, Score Quality brackets, Workplace Modes).

### Step 2: Resume Ingestion & NLP Parsing (2 Minutes)
1. Navigate to `/upload` and upload a tech resume PDF.
2. Click **Analyze Resume**.
3. Point out the extracted data in `/analysis/:fileId`:
   - Contact info parsed via regex.
   - Education and Work Experience presented as interactive visual timelines.
   - Projects parsed with automatic technology tagging.
   - NLP token counts and character metrics.

### Step 3: Skill Taxonomy & Evidence-Based Proficiency (2 Minutes)
1. Click **Inspect Skills Engine** or navigate to `/skills/:fileId`.
2. Explain how the rule engine normalizes aliases (e.g. `JS` $\rightarrow$ `JavaScript`, `K8s` $\rightarrow$ `Kubernetes`).
3. Highlight that proficiency is not self-declared; it is computed based on contextual evidence across project deliverables and work experience.

### Step 4: AI Job Recommendation Engine (2 Minutes)
1. Click **View Job Recommendations** (`/recommendations/:fileId`).
2. Explain the hybrid matching formula: 70% TF-IDF Cosine Similarity + 30% Skill Coverage.
3. Demonstrate live filtering by Job Category (e.g. Machine Learning Engineer) and Location.

### Step 5: Skill Gap Analysis & Learning Roadmap (2 Minutes)
1. Click **Analyze Skill Gap** on a recommended job card (`/skill-gap/:fileId/:jobId`).
2. Show the granular breakdown: Matched skills (green), Transferable skills (amber), and Missing skills (red).
3. Scroll down to the **Personalized Learning Roadmap** to show curated modules, estimated hours, and verified documentation links.

### Step 6: Resume Strength & Improvement Roadmap (1 Minute)
1. Click **Improvements** (`/improvements/:fileId`).
2. Show the overall ATS Score gauge and 5 dimensional score cards.
3. Show the prioritized recommendations that guide students on what to add to their resume to maximize hiring outcomes.

---

## 💡 Technical Viva & Interview Preparation Q&A

**Q1: Why did you use TF-IDF and Cosine Similarity instead of heavy Transformer models (like BERT or GPT) for job recommendations?**
> *Answer*: TF-IDF with sublinear term frequency scaling and 1-to-3 n-grams is deterministic, explainable, and computationally lightweight ($O(V)$ time complexity where $V$ is vocabulary size). It runs locally in sub-100 milliseconds without requiring GPU hardware, eliminating cold-start latency and inference costs while achieving high keyword-level precision. In enterprise recruiting, explainability is critical: candidates and recruiters need to see *why* a role was recommended (exact matched and missing terms).

**Q2: How does the system handle "transferable skills"?**
> *Answer*: The system groups technologies into semantic domain clusters. If a job requires `PyTorch` and the candidate possesses `TensorFlow` or `Keras`, the system marks it as a "Partial Match / Transferable Skill" awarding 50% credit. This acknowledges overlapping underlying mental models (tensors, backpropagation, neural architecture) rather than penalizing candidates for framework differences.

**Q3: How is proficiency determined without trusting self-reported ratings?**
> *Answer*: The system scans the entire resume for contextual occurrences. A skill mentioned only in the skills list receives `Beginner` status. A skill mentioned in 1 project or work experience receives `Intermediate` status. A skill mentioned across 2 or more distinct projects or work experiences with action verbs receives `Advanced` status.

**Q4: How does the scoring engine prevent penalizing freshers with zero work experience?**
> *Answer*: In `ScoringService`, when experience score is 0, the composite weighting automatically shifts from experience to practical project deliverables and technical skills ($40\%$ Skills + $30\%$ Projects + $18\%$ Education + $12\%$ Completeness). This ensures proactive students with strong portfolio projects receive competitive ATS evaluations.

---

## 📄 License
This project is open-source under the MIT License. Developed for educational, research, and placement interview demonstration purposes.
