# AI Resume Screening & Job Recommendation System

An AI-powered web application that analyzes resumes, identifies relevant skills, and recommends suitable job opportunities based on a candidate's profile.

## 🌐 Live Demo

- **Frontend:** [AI Resume Screening System](https://ai-resume-screening-system-seven.vercel.app/)
- **Backend:** [Render API](https://ai-resume-screening-system-qsh7.onrender.com)

## ✨ Features

- **Resume Upload:** Upload a resume in PDF format for analysis.
- **Resume Parsing:** Extract text and relevant information from uploaded resumes.
- **Skill Extraction:** Identify technical skills and other relevant keywords.
- **Resume Scoring:** Evaluate resume content using defined scoring criteria.
- **Job Recommendations:** Find job opportunities relevant to the candidate's skills and profile.
- **Skill Gap Analysis:** Identify skills that may be missing for a particular job.
- **Dashboard:** View resume analysis results and job recommendations through a web interface.

## 🛠️ Tech Stack

### Frontend
- React
- JavaScript
- Vite
- Tailwind CSS

### Backend
- Python
- FastAPI
- Pydantic

### AI and NLP
- TF-IDF
- Cosine Similarity
- Natural Language Processing (NLP)
- Scikit-learn

### Database and Tools
- SQLite
- SQLAlchemy
- PyMuPDF for PDF text extraction
- Git and GitHub
- Vercel for frontend deployment
- Render for backend deployment

## ⚙️ How It Works

1. The user uploads a resume in PDF format.
2. The backend extracts text from the resume.
3. The system identifies relevant skills and keywords.
4. The extracted information is compared with available job descriptions.
5. TF-IDF and cosine similarity help measure the textual relevance between the resume and job descriptions.
6. The system presents resume analysis, relevant job recommendations, and potential skill gaps.

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or later
- Node.js and npm
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/prajwalppattanashetty-1810/AI-resume-screening-system.git
cd AI-resume-screening-system
```

### 2. Set Up the Backend

Open a terminal in the backend directory:

```bash
cd backend
python -m venv venv
```

Activate the virtual environment.

**Windows:**
```bash
venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the backend using the entry point configured in your project. For example, if the application is exposed as `app` in `main.py`:

```bash
uvicorn main:app --reload
```

### 3. Set Up the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your browser.

> Note: Verify the actual backend entry point, environment variables, and frontend API URL against the repository before following these commands.

## 🧪 Testing

Automated tests can help verify API responses, resume parsing, skill extraction, and recommendation logic.

Run the test command configured in the backend project. If Pytest is configured:

```bash
pytest
```

## 🔒 Privacy and Security

- Do not upload API keys, passwords, or private environment files to GitHub.
- Use environment variables for deployment-specific configuration.
- Use sample resumes without sensitive personal information when testing.
- Treat automated recommendations as decision-support suggestions, not guaranteed hiring outcomes.

## 🎯 Project Objective

The goal of this project is to simplify resume analysis and help job seekers discover opportunities that better match their skills and experience.

## 👨‍💻 Author

**Prajwal P Pattanashetty**

- GitHub: [prajwalppattanashetty-1810](https://github.com/prajwalppattanashetty-1810)

---

*This project is intended for educational and demonstration purposes. Recommendation quality depends on the available job data and the implemented matching logic.*
