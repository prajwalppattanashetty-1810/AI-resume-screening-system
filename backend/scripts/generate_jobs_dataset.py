"""
Generate structured, realistic synthetic job records for Phase 5.
Covers 14 categories, distributed across Entry-level, Junior, Intermediate, and Senior tiers.
Saves to backend/data/jobs.json and provides an idempotent database seeder.
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta

# 17 Categories (including all 15 required categories from Phase 5 specification)
CATEGORIES = [
    "Machine Learning Engineer",
    "AI Engineer",
    "Data Scientist",
    "Data Analyst",
    "Data Engineer",
    "Python Developer",
    "Full Stack Developer",
    "Frontend Developer",
    "Backend Developer",
    "Java Developer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Cybersecurity Analyst",
    "Database Administrator",
    "UI/UX Designer",
    "Software Developer",
    "Software Engineer"
]

EXPERIENCE_TIERS = [
    {"level": "Entry-level", "min_exp": 0, "max_exp": 1, "ratio": 0.30},
    {"level": "Junior", "min_exp": 1, "max_exp": 3, "ratio": 0.30},
    {"level": "Intermediate", "min_exp": 3, "max_exp": 5, "ratio": 0.25},
    {"level": "Senior", "min_exp": 5, "max_exp": 9, "ratio": 0.15}
]

WORK_MODES = ["Remote", "Hybrid", "On-site"]
EMPLOYMENT_TYPES = ["Full-time", "Full-time", "Full-time", "Internship", "Contract"]

LOCATIONS = [
    "Bengaluru, Karnataka",
    "Hyderabad, Telangana",
    "Pune, Maharashtra",
    "Gurugram, Haryana",
    "Noida, Uttar Pradesh",
    "Chennai, Tamil Nadu",
    "Mumbai, Maharashtra",
    "Mysuru, Karnataka",
    "Remote - India",
    "Remote - Global"
]

# Clearly identify sample / demo companies as per project requirements
COMPANIES = [
    "Nexora Cloud Technologies (Demo)", "DataPulse AI Systems (Sample)", "Vanguard Software Labs (Demo)",
    "Aegis Cyber Defense (Sample)", "HyperScale Data Corp (Demo)", "Cognitive Wave Infotech (Demo)",
    "InfiniTech Digital Solutions (Sample)", "StrataFlow Analytics (Demo)", "QuantumLeap Software (Sample)",
    "Apex Global Engineering (Demo)", "Crestline Mobility Systems (Sample)", "Novus FinTech Solutions (Demo)",
    "Orion HealthTech Labs (Sample)", "Zenith Retail Platforms (Demo)", "Acuity Distributed Systems (Sample)",
    "Skyline Cybernetics (Demo)", "BluePrint Automation (Sample)", "Solstice Enterprise Tech (Demo)",
    "Krypton Security Works (Sample)", "Terraformic Cloud Labs (Demo)", "OmniData Solutions (Sample)",
    "PixelCraft Design Studios (Demo)", "RelationalCore Systems (Sample)", "Veritas Data Platforms (Demo)",
    "Catalyst Intelligent Systems (Sample)", "OmniTech Global (Demo)", "Pinnacle Software Group (Sample)",
    "Elevate Cloud Solutions (Demo)", "Prism AI Analytics (Sample)", "Syntropic Software (Demo)",
    "Frontier Data Networks (Sample)", "Beacon CyberTech (Demo)", "Matrix Enterprise Systems (Sample)"
]

CATEGORY_TEMPLATES = {
    "Machine Learning Engineer": {
        "titles": [
            "Machine Learning Engineer", "Junior ML Engineer", "MLOps Engineer",
            "Applied Machine Learning Engineer", "Machine Learning Intern", "Senior ML Platform Engineer"
        ],
        "core_required": ["Python", "Machine Learning", "Scikit-learn", "Pandas", "NumPy", "Git"],
        "pool_required": ["TensorFlow", "PyTorch", "Docker", "SQL", "Linux", "FastAPI"],
        "pool_preferred": ["NLP", "Computer Vision", "AWS", "Kubernetes", "CI/CD", "MLflow", "PostgreSQL"],
        "duty_templates": [
            "Design and deploy production-ready machine learning models for predictive ranking, classification, and time-series forecasting.",
            "Build automated data preprocessing pipelines and feature engineering modules using Python, Pandas, and Scikit-learn.",
            "Collaborate with backend engineering teams to serve ML models via high-performance REST APIs built with FastAPI.",
            "Monitor model performance in production, detect data drift, and automate continuous model retraining pipelines."
        ]
    },
    "AI Engineer": {
        "titles": [
            "AI Engineer", "Generative AI Engineer", "AI Solutions Developer",
            "Junior AI Engineer", "AI Research Intern", "Lead AI Engineer"
        ],
        "core_required": ["Python", "Deep Learning", "TensorFlow", "PyTorch", "NLP", "Git"],
        "pool_required": ["Transformers", "Hugging Face", "Machine Learning", "FastAPI", "Docker"],
        "pool_preferred": ["Computer Vision", "OpenCV", "AWS", "Azure", "LangChain", "Vector DB", "Linux"],
        "duty_templates": [
            "Architect and fine-tune large language models and neural networks for conversational agents and intelligent document understanding.",
            "Implement multimodal AI pipelines utilizing PyTorch, Transformers, and custom embedding search vectors.",
            "Optimize neural network inference latency and memory footprints for containerized deployment on cloud GPUs.",
            "Work alongside product teams to translate complex business problems into production AI capabilities."
        ]
    },
    "Data Scientist": {
        "titles": [
            "Data Scientist", "Associate Data Scientist", "Data Science Intern",
            "Applied Data Scientist", "Senior Data Scientist", "Decision Scientist"
        ],
        "core_required": ["Python", "SQL", "Machine Learning", "Pandas", "NumPy", "Scikit-learn"],
        "pool_required": ["Matplotlib", "Seaborn", "Statistics", "Tableau", "Git"],
        "pool_preferred": ["Deep Learning", "AWS", "Power BI", "PySpark", "MongoDB", "R", "Communication"],
        "duty_templates": [
            "Formulate predictive algorithms and statistical hypothesis tests to derive actionable business intelligence from multi-terabyte datasets.",
            "Develop comprehensive exploratory data analysis (EDA) workflows and interactive executive dashboards.",
            "Partner with domain experts to build customer lifetime value, churn risk, and recommendation engines.",
            "Communicate quantitative insights, model limitations, and strategic recommendations to cross-functional stakeholders."
        ]
    },
    "Data Analyst": {
        "titles": [
            "Data Analyst", "Business Intelligence Analyst", "Junior Data Analyst",
            "Product Data Analyst", "Data Analytics Intern", "Senior BI Analyst"
        ],
        "core_required": ["SQL", "Excel", "Tableau", "Power BI", "Data Analysis", "Communication"],
        "pool_required": ["Python", "Pandas", "Matplotlib", "PostgreSQL", "Problem Solving"],
        "pool_preferred": ["MySQL", "Git", "Google Cloud", "Statistics", "AWS", "Seaborn"],
        "duty_templates": [
            "Write complex SQL queries, window functions, and views to extract transactional records and cohort data from relational databases.",
            "Design, build, and maintain executive Tableau and Power BI dashboards tracking core business performance KPIs.",
            "Perform root-cause variance analysis on quarterly metrics to assist strategic decision-making.",
            "Clean and validate incoming telemetry data to guarantee data integrity across enterprise reporting systems."
        ]
    },
    "Data Engineer": {
        "titles": [
            "Data Engineer", "Big Data Engineer", "Junior Data Engineer",
            "Data Platform Engineer", "Data Pipeline Engineer", "Lead Data Engineer"
        ],
        "core_required": ["Python", "SQL", "PostgreSQL", "Kafka", "Docker", "Git"],
        "pool_required": ["PySpark", "Spark", "AWS", "Airflow", "MongoDB", "Linux"],
        "pool_preferred": ["GCP", "Kubernetes", "Redis", "Elasticsearch", "Snowflake", "Terraform"],
        "duty_templates": [
            "Construct robust, high-throughput ETL/ELT pipelines ingesting millions of daily events into centralized data warehouses.",
            "Maintain scalable distributed processing infrastructure using Apache Spark, Kafka streams, and relational data lakes.",
            "Optimize SQL queries, indexing, table partitioning, and database storage schemas for query efficiency.",
            "Implement automated pipeline monitoring, anomaly detection, and schema migration procedures."
        ]
    },
    "Python Developer": {
        "titles": [
            "Python Developer", "Python Backend Developer", "Junior Python Developer",
            "Software Engineer - Python", "Python Developer Intern", "Senior Python Engineer"
        ],
        "core_required": ["Python", "FastAPI", "Flask", "Django", "SQL", "Git"],
        "pool_required": ["PostgreSQL", "Docker", "REST API", "Linux", "PyTest"],
        "pool_preferred": ["Redis", "Celery", "AWS", "MongoDB", "CI/CD", "HTML", "JavaScript"],
        "duty_templates": [
            "Develop modular, clean, and maintainable backend microservices and APIs using modern Python and FastAPI/Django frameworks.",
            "Design relational database schemas, write optimized ORM models, and perform database migrations with Alembic.",
            "Integrate third-party RESTful services, payment gateways, and asynchronous background worker queues using Celery and Redis.",
            "Write unit and integration tests using PyTest to maintain strict test coverage and code quality standards."
        ]
    },
    "Full Stack Developer": {
        "titles": [
            "Full Stack Developer", "Full Stack Engineer", "Junior Full Stack Developer",
            "Full Stack Web Developer", "Software Engineer - Full Stack", "Senior Full Stack Engineer"
        ],
        "core_required": ["JavaScript", "React", "Node.js", "HTML", "CSS", "SQL", "Git"],
        "pool_required": ["TypeScript", "Express.js", "MongoDB", "PostgreSQL", "Tailwind CSS", "REST API"],
        "pool_preferred": ["Next.js", "Docker", "AWS", "Redis", "GraphQL", "CI/CD"],
        "duty_templates": [
            "Build responsive client-facing interfaces with React and Tailwind CSS coupled with resilient Node.js / Express backend services.",
            "Implement secure authentication, role-based access control (RBAC), and session management protocols.",
            "Manage end-to-end web architecture from relational database schema design down to interactive DOM components.",
            "Collaborate in Agile sprint cycles, conducting code reviews and maintaining continuous integration pipelines."
        ]
    },
    "Frontend Developer": {
        "titles": [
            "Frontend Developer", "React Developer", "UI/UX Frontend Engineer",
            "Junior Frontend Developer", "Frontend Engineering Intern", "Senior Frontend Engineer"
        ],
        "core_required": ["JavaScript", "HTML", "CSS", "React", "Git"],
        "pool_required": ["TypeScript", "Tailwind CSS", "Next.js", "Redux", "Bootstrap"],
        "pool_preferred": ["Vue.js", "Angular", "Jest", "GraphQL", "Figma", "Webpack"],
        "duty_templates": [
            "Translate UI/UX wireframes and Figma specifications into responsive, pixel-perfect, accessible web interfaces.",
            "Manage client-side state efficiently with modern React hooks, context APIs, and Redux Toolkit stores.",
            "Profile and optimize browser rendering speed, bundle payloads, and Core Web Vitals performance.",
            "Ensure cross-browser compatibility and responsive screen adaptations across mobile, tablet, and desktop devices."
        ]
    },
    "Backend Developer": {
        "titles": [
            "Backend Developer", "Backend Engineer", "API Developer",
            "Junior Backend Developer", "Systems Backend Engineer", "Lead Backend Architect"
        ],
        "core_required": ["Node.js", "Python", "FastAPI", "SQL", "PostgreSQL", "Git"],
        "pool_required": ["Docker", "REST API", "Express.js", "MongoDB", "Linux", "Redis"],
        "pool_preferred": ["Spring Boot", "Kubernetes", "AWS", "GraphQL", "CI/CD", "Kafka"],
        "duty_templates": [
            "Design, code, and deploy resilient distributed backend services, RPC endpoints, and RESTful APIs.",
            "Implement high-performance caching layers, connection pooling, and asynchronous messaging architectures.",
            "Maintain relational integrity, enforce data validation constraints, and optimize database indexing strategies.",
            "Write comprehensive API documentation with Swagger/OpenAPI and enforce automated testing workflows."
        ]
    },
    "Java Developer": {
        "titles": [
            "Java Developer", "Java Backend Developer", "Junior Java Engineer",
            "Software Engineer - Java", "Enterprise Java Developer", "Senior Java Engineer"
        ],
        "core_required": ["Java", "Spring Boot", "SQL", "Git", "REST API"],
        "pool_required": ["Hibernate", "MySQL", "PostgreSQL", "Docker", "Maven", "Linux"],
        "pool_preferred": ["Kafka", "Microservices", "AWS", "Kubernetes", "Redis", "JUnit"],
        "duty_templates": [
            "Develop mission-critical enterprise applications and microservices using modern Java and Spring Boot ecosystems.",
            "Implement persistence logic and transactional boundaries with Hibernate ORM and Spring Data JPA.",
            "Collaborate with solution architects to design secure, stateless API architectures capable of high concurrency.",
            "Conduct automated unit and integration testing with JUnit and Mockito to enforce enterprise reliability."
        ]
    },
    "DevOps Engineer": {
        "titles": [
            "DevOps Engineer", "Site Reliability Engineer (SRE)", "Junior DevOps Engineer",
            "Cloud DevOps Specialist", "Infrastructure Automation Engineer", "Senior DevOps Engineer"
        ],
        "core_required": ["Docker", "Kubernetes", "Linux", "Git", "CI/CD", "Bash"],
        "pool_required": ["AWS", "Terraform", "GitHub Actions", "Python", "Ansible"],
        "pool_preferred": ["Azure", "GCP", "Prometheus", "Grafana", "Nginx", "Jenkins"],
        "duty_templates": [
            "Build and maintain automated continuous integration and continuous deployment (CI/CD) pipelines.",
            "Manage containerized microservices deployments across production Kubernetes clusters with zero downtime.",
            "Automate cloud infrastructure provisioning using Infrastructure as Code (IaC) principles with Terraform.",
            "Implement comprehensive telemetry, distributed tracing, alerting, and automated incident recovery policies."
        ]
    },
    "Cloud Engineer": {
        "titles": [
            "Cloud Engineer", "Cloud Solutions Architect", "Junior Cloud Engineer",
            "AWS Cloud Developer", "Cloud Infrastructure Specialist", "Senior Cloud Engineer"
        ],
        "core_required": ["AWS", "Linux", "Docker", "Git", "Networking", "Python"],
        "pool_required": ["Azure", "GCP", "Terraform", "CI/CD", "Kubernetes"],
        "pool_preferred": ["SQL", "Security", "Ansible", "CloudFormation", "Serverless"],
        "duty_templates": [
            "Design and implement scalable, fault-tolerant cloud architectures across AWS, Azure, and Google Cloud environments.",
            "Configure virtual private clouds (VPCs), subnets, routing tables, security groups, and load balancers.",
            "Optimize cloud infrastructure expenditure through rightsizing, reserved instances, and serverless compute models.",
            "Enforce strict identity and access management (IAM) policies, encryption standards, and compliance frameworks."
        ]
    },
    "Cybersecurity Analyst": {
        "titles": [
            "Cybersecurity Analyst", "Information Security Specialist", "Junior Security Analyst",
            "SOC Analyst", "Vulnerability Assessment Analyst", "Senior Cyber Defense Engineer"
        ],
        "core_required": ["Linux", "Networking", "Security", "Python", "Problem Solving"],
        "pool_required": ["Bash", "Git", "SIEM", "Firewalls", "Docker"],
        "pool_preferred": ["Wireshark", "Metasploit", "AWS", "Cryptography", "SQL", "OWASP"],
        "duty_templates": [
            "Monitor enterprise security information and event management (SIEM) consoles for anomalous traffic and threat indicators.",
            "Perform vulnerability assessments, penetration testing, and code audits following OWASP Top 10 guidelines.",
            "Implement automated incident response playbooks using Python and shell scripts to isolate compromised assets.",
            "Collaborate with systems engineers to ensure data protection, key management, and regulatory compliance standards."
        ]
    },
    "Database Administrator": {
        "titles": [
            "Database Administrator", "Junior Database Administrator", "Senior PostgreSQL DBA",
            "Cloud Database Administrator", "Database Reliability Engineer", "Associate DBA"
        ],
        "core_required": ["SQL", "PostgreSQL", "MySQL", "Database Administration", "Linux"],
        "pool_required": ["Performance Tuning", "Backup & Recovery", "Bash", "Redis", "High Availability"],
        "pool_preferred": ["Oracle", "MongoDB", "AWS RDS", "Docker", "Data Replication", "Security"],
        "duty_templates": [
            "Design, provision, configure, and maintain high-availability PostgreSQL and MySQL database clusters.",
            "Execute routine query optimization, index tuning, vacuuming, and database performance profiling.",
            "Implement automated daily backups, disaster recovery drills, point-in-time recovery, and replication monitoring.",
            "Enforce database role-based access control (RBAC), auditing standards, and data encryption at rest and in transit."
        ]
    },
    "UI/UX Designer": {
        "titles": [
            "UI/UX Designer", "Product Designer", "Junior UI/UX Designer",
            "Senior Product Designer", "UX Researcher & Designer", "Design Systems Specialist"
        ],
        "core_required": ["Figma", "UI/UX Design", "Wireframing", "Prototyping", "User Research"],
        "pool_required": ["Design Systems", "Usability Testing", "Interaction Design", "Visual Design", "Information Architecture"],
        "pool_preferred": ["Adobe XD", "HTML", "CSS", "Tailwind CSS", "Design Thinking", "Responsive Design"],
        "duty_templates": [
            "Create user flows, wireframes, high-fidelity prototypes, and interactive UI specifications using Figma.",
            "Conduct qualitative user interviews, usability testing sessions, and journey mapping to uncover UX friction.",
            "Maintain and evolve comprehensive design systems, component libraries, typography scales, and design tokens.",
            "Collaborate closely with product managers and frontend developers to ensure design integrity and seamless user experience."
        ]
    },
    "Software Developer": {
        "titles": [
            "Software Developer", "Junior Software Developer", "Associate Software Developer",
            "Senior Software Developer", "Full Cycle Software Developer", "Software Development Engineer"
        ],
        "core_required": ["Python", "Java", "JavaScript", "SQL", "Git", "Data Structures"],
        "pool_required": ["Algorithms", "REST API", "Docker", "Problem Solving", "Linux"],
        "pool_preferred": ["PostgreSQL", "React", "FastAPI", "CI/CD", "AWS", "TypeScript"],
        "duty_templates": [
            "Design, build, and maintain robust, scalable software features across backend and application layers.",
            "Write comprehensive unit, integration, and regression tests to guarantee high code reliability.",
            "Participate in agile sprints, code reviews, and architectural design discussions to ensure best practices.",
            "Identify bottlenecks, troubleshoot bugs, and refactor codebases for long-term maintainability and performance."
        ]
    },
    "Software Engineer": {
        "titles": [
            "Software Engineer", "Associate Software Engineer", "Software Development Engineer (SDE-1)",
            "Junior Software Engineer", "Graduate Software Trainee", "Senior Software Engineer"
        ],
        "core_required": ["Python", "Java", "C++", "SQL", "Git", "Data Structures"],
        "pool_required": ["Algorithms", "Linux", "Docker", "REST API", "Problem Solving"],
        "pool_preferred": ["FastAPI", "React", "PostgreSQL", "AWS", "CI/CD", "JavaScript"],
        "duty_templates": [
            "Architect and write clean, modular, and performant code to solve complex engineering and algorithmic challenges.",
            "Participate actively in full software development lifecycles (SDLC) from technical design through deployment.",
            "Diagnose, debug, and resolve performance bottlenecks, memory leaks, and distributed concurrency issues.",
            "Write thorough unit tests and documentation to ensure long-term code quality, scalability, and maintainability."
        ]
    }
}


def generate_salary_range(level: str, emp_type: str) -> str:
    if emp_type == "Internship":
        stipend = random.choice([25000, 30000, 35000, 45000, 50000])
        return f"₹{stipend:,} - ₹{stipend + 15000:,} / month (Stipend)"

    if level == "Entry-level":
        base = random.choice([450000, 600000, 750000, 900000])
        return f"₹{base//100000}.{(base%100000)//10000} - ₹{(base + 300000)//100000}.{((base + 300000)%100000)//10000} LPA"
    elif level == "Junior":
        base = random.choice([800000, 1000000, 1200000])
        return f"₹{base//100000} - ₹{(base + 400000)//100000} LPA"
    elif level == "Intermediate":
        base = random.choice([1400000, 1600000, 2000000])
        return f"₹{base//100000} - ₹{(base + 600000)//100000} LPA"
    else:  # Senior
        base = random.choice([2400000, 2800000, 3200000])
        return f"₹{base//100000} - ₹{(base + 1000000)//100000} LPA"


def generate_jobs_dataset(target_count: int = 255) -> list:
    """Generate target_count unique, realistic synthetic job records."""
    jobs = []
    base_date = datetime.now() - timedelta(days=60)
    per_category = max(1, target_count // len(CATEGORIES))

    job_counter = 1

    for cat_idx, category in enumerate(CATEGORIES):
        config = CATEGORY_TEMPLATES[category]

        for i in range(per_category):
            tier_info = random.choices(
                EXPERIENCE_TIERS,
                weights=[t["ratio"] for t in EXPERIENCE_TIERS]
            )[0]

            level = tier_info["level"]
            min_exp = tier_info["min_exp"]
            max_exp = tier_info["max_exp"]

            emp_type = "Internship" if level == "Entry-level" and random.random() < 0.35 else random.choice(["Full-time", "Full-time", "Full-time", "Contract"])
            work_mode = random.choice(WORK_MODES)
            location = random.choice(LOCATIONS)
            company = random.choice(COMPANIES)

            # Title matching level
            title_pool = config["titles"]
            if level == "Entry-level":
                title_candidates = [t for t in title_pool if "Junior" in t or "Intern" in t or "Associate" in t or "Trainee" in t or "SDE-1" in t]
                title = random.choice(title_candidates) if title_candidates else f"Junior {category}"
            elif level == "Senior":
                title_candidates = [t for t in title_pool if "Senior" in t or "Lead" in t or "Architect" in t]
                title = random.choice(title_candidates) if title_candidates else f"Senior {category}"
            else:
                title = random.choice(title_pool)

            # Skills assembly
            core = list(config["core_required"])
            pool_req = random.sample(config["pool_required"], k=min(len(config["pool_required"]), random.randint(2, 4)))
            required_skills = list(dict.fromkeys(core + pool_req))

            pref_pool = [s for s in config["pool_preferred"] if s not in required_skills]
            preferred_skills = random.sample(pref_pool, k=min(len(pref_pool), random.randint(2, 4)))

            # Construct rich, meaningful description for TF-IDF feature extraction
            duties = random.sample(config["duty_templates"], k=random.randint(3, 4))
            duty_bullets = "\n".join([f"• {d}" for d in duties])

            description = (
                f"### Role Overview: {title}\n"
                f"{company} is looking for a talented and driven {title} ({level}) to join our engineering and technology team in {location}. "
                f"In this role, you will collaborate with seasoned software engineers, data specialists, and product managers to develop, "
                f"scale, and support enterprise applications and cutting-edge software solutions.\n\n"
                f"### Core Responsibilities:\n{duty_bullets}\n\n"
                f"### Qualifications & Experience:\n"
                f"• Experience: {min_exp} to {max_exp} year(s) in {category} or related technical domain.\n"
                f"• Education: Bachelor's or Master's degree in Computer Science, Data Science, Information Technology, Design, or relevant engineering field.\n"
                f"• Demonstrated competency with core technical stack: {', '.join(required_skills[:5])}.\n"
                f"• Familiarity with modern version control (Git), collaborative agile development, and clean coding principles.\n\n"
                f"### Employment Details:\n"
                f"• Employment Type: {emp_type}\n"
                f"• Work Environment: {work_mode}\n"
                f"• Location: {location}\n\n"
                f"*(Note: Verified synthetic demonstration dataset for AI Resume Screening & Job Recommendation System. Company names and positions are demo records.)*"
            )

            category_prefix = category.split()[0][:3].upper()
            job_code = f"JOB-{category_prefix}-{job_counter:04d}"
            created_date = (base_date + timedelta(days=random.randint(1, 55))).strftime("%Y-%m-%d")

            salary_range = generate_salary_range(level, emp_type)

            job_record = {
                "id": job_counter,
                "job_id": job_code,
                "title": title,
                "company": company,
                "category": category,
                "description": description,
                "responsibilities": duties,
                "required_skills": required_skills,
                "preferred_skills": preferred_skills,
                "min_experience": min_exp,
                "max_experience": max_exp,
                "experience_level": level,
                "education": "Bachelor's in Computer Science, Information Technology, Design, or equivalent",
                "employment_type": emp_type,
                "work_mode": work_mode,
                "location": location,
                "salary_range": salary_range,
                "job_status": "Active",
                "date_posted": created_date,
                "created_date": created_date
            }

            jobs.append(job_record)
            job_counter += 1

    return jobs


def save_jobs_dataset(filepath: str, jobs: list):
    """Save generated jobs to a JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved {len(jobs)} jobs to {filepath}")


if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "jobs.json")
    generated = generate_jobs_dataset(target_count=255)
    save_jobs_dataset(out_path, generated)

