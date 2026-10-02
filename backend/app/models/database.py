from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone
from app.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), index=True, nullable=False)
    company = Column(String(255), index=True, nullable=False)
    category = Column(String(100), index=True, nullable=False)
    description = Column(Text, nullable=False)
    responsibilities = Column(JSON, default=list)
    required_skills = Column(JSON, nullable=False)
    preferred_skills = Column(JSON, default=list)
    min_experience = Column(Integer, default=0)
    max_experience = Column(Integer, nullable=True)
    experience_level = Column(String(50), index=True, default="Entry-level")
    education = Column(String(255), default="Bachelor's in Computer Science or related field")
    employment_type = Column(String(50), default="Full-time")
    work_mode = Column(String(50), default="Hybrid")
    location = Column(String(100), default="Bengaluru, India")
    salary_range = Column(String(100), nullable=True)
    job_status = Column(String(20), default="Active")
    date_posted = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)
    original_filename = Column(String)
    extracted_text = Column(Text)
    skills_json = Column(JSON)
    analysis_json = Column(JSON)
    score = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

def safe_init_database():
    """Ensure database tables exist and perform safe column additions without losing data."""
    Base.metadata.create_all(bind=engine)
    
    # Check SQLite columns for safe non-destructive migration
    with engine.connect() as conn:
        try:
            result = conn.execute(text("PRAGMA table_info(jobs)"))
            existing_cols = {row[1] for row in result.fetchall()}
            
            if "responsibilities" not in existing_cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN responsibilities JSON"))
            if "date_posted" not in existing_cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN date_posted VARCHAR(50)"))
            conn.commit()
        except Exception as e:
            # Non-fatal if table doesn't exist yet or columns already exist
            pass

def create_tables():
    safe_init_database()

