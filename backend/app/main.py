from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from app.config import get_settings
from app.api.routes import health, resume, jobs, skills, skill_gap

from app.models.database import create_tables

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events for the application."""
    # Startup: create upload directory and initialize database tables
    os.makedirs(settings.upload_dir, exist_ok=True)
    create_tables()
    # Auto-seed jobs dataset if database has 0 jobs (cold-start / Docker ready)
    try:
        from app.models.database import SessionLocal, Job
        from app.services.job_service import JobService
        db = SessionLocal()
        try:
            if db.query(Job).count() == 0:
                JobService().seed_dataset(db)
        finally:
            db.close()
    except Exception as e:
        pass
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title='AI Resume Screening & Job Recommendation System',
    description='Backend API for Resume Screening and Job Recommendation',
    version='1.0.0',
    lifespan=lifespan,
    redoc_url=None  # Custom reliable ReDoc handler configured below
)

# Build resilient CORS origins list supporting local Vite, Docker Nginx, and comma-separated production domains
cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if settings.frontend_url:
    for origin in settings.frontend_url.split(","):
        clean_origin = origin.strip().rstrip("/")
        if clean_origin and clean_origin not in cors_origins:
            cors_origins.append(clean_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
app.include_router(skill_gap.router, prefix="/api/skill-gap", tags=["Skill Gap"])


@app.get("/")
def root():
    return {"message": "API is running", "version": "1.0.0", "docs": "/docs", "redoc": "/redoc"}


@app.get("/redoc", include_in_schema=False, response_class=HTMLResponse)
def redoc_documentation():
    """
    Renders high-reliability ReDoc API documentation with multi-CDN fallback
    and explicit Redoc.init mounting to resolve the blank page issue caused by
    unstable redoc@next packages or intermittent CDN throttling.
    """
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{app.title} - ReDoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Roboto, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #fafafa;
        }}
        #loading {{
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            color: #475569;
            font-size: 16px;
            font-weight: 500;
        }}
        #error-banner {{
            display: none;
            margin: 40px auto;
            max-width: 600px;
            padding: 24px;
            border: 1px solid #f87171;
            background: #fef2f2;
            border-radius: 12px;
            color: #991b1b;
        }}
    </style>
</head>
<body>
    <div id="loading">Loading ReDoc API Documentation...</div>
    <div id="error-banner">
        <h3 style="margin-top:0;">Unable to load ReDoc documentation bundle</h3>
        <p>Your network or firewall may be restricting external CDN scripts. You can use the interactive Swagger UI documentation instead:</p>
        <p><a href="/docs" style="color: #2563eb; font-weight: bold; text-decoration: underline;">Go to Interactive Swagger UI (/docs) &rarr;</a></p>
    </div>
    <div id="redoc-container"></div>
    <script>
        var initialized = false;
        function initRedoc() {{
            if (initialized) return;
            var loader = document.getElementById('loading');
            if (loader) loader.style.display = 'none';
            if (window.Redoc) {{
                initialized = true;
                Redoc.init('/openapi.json', {{
                    scrollYOffset: 50,
                    hideDownloadButton: false,
                    expandResponses: '200,201',
                    theme: {{
                        colors: {{
                            primary: {{ main: '#2563eb' }}
                        }},
                        typography: {{
                            fontFamily: 'Roboto, sans-serif',
                            headings: {{
                                fontFamily: 'Montserrat, sans-serif'
                            }}
                        }}
                    }}
                }}, document.getElementById('redoc-container'));
            }} else {{
                showError();
            }}
        }}

        function showError() {{
            var loader = document.getElementById('loading');
            if (loader) loader.style.display = 'none';
            var err = document.getElementById('error-banner');
            if (err) err.style.display = 'block';
        }}

        function loadScript(url, fallbackUrl) {{
            var script = document.createElement('script');
            script.src = url;
            script.onload = initRedoc;
            script.onerror = function() {{
                if (fallbackUrl) {{
                    console.warn('Primary ReDoc CDN failed, trying fallback CDN:', fallbackUrl);
                    loadScript(fallbackUrl, 'https://unpkg.com/redoc@latest/bundles/redoc.standalone.js');
                }} else {{
                    showError();
                }}
            }};
            document.body.appendChild(script);
        }}

        // Load primary official Redocly CDN (v2.5.4 stable), with jsdelivr and unpkg fallbacks
        loadScript(
            'https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js',
            'https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js'
        );
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


if __name__ == '__main__':
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug
    )
