"""
Skill Gap Analysis and Personalized Learning Recommendation Engine.

Part of Phase 7: Skill Gap Analysis & Personalized Learning Recommendations.
Compares candidate skills against job required and preferred skills, performs
proficiency analysis, computes skill coverage metrics, and generates targeted
learning roadmaps with verified resources.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from app.services.skill_extraction_service import SkillExtractionService

logger = logging.getLogger(__name__)


# ============================================================================
# 1. VERIFIED OFFICIAL LEARNING RESOURCES
# Only verified, permanent, official documentation and tutorial URLs are included.
# No unverified or placeholder URLs.
# ============================================================================
VERIFIED_RESOURCES: Dict[str, Dict[str, str]] = {
    # Programming Languages
    "Python": {
        "title": "Python Official Tutorial & Docs",
        "url": "https://docs.python.org/3/tutorial/"
    },
    "Java": {
        "title": "Oracle Java Documentation & Tutorials",
        "url": "https://docs.oracle.com/javase/tutorial/"
    },
    "C++": {
        "title": "cppreference.com C++ Reference",
        "url": "https://en.cppreference.com/w/"
    },
    "C": {
        "title": "cppreference.com C Reference",
        "url": "https://en.cppreference.com/w/c"
    },
    "C#": {
        "title": "Microsoft C# Documentation",
        "url": "https://learn.microsoft.com/en-us/dotnet/csharp/"
    },
    "JavaScript": {
        "title": "MDN Web Docs: JavaScript Guide",
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript"
    },
    "TypeScript": {
        "title": "TypeScript Official Handbook",
        "url": "https://www.typescriptlang.org/docs/"
    },
    "Go": {
        "title": "Go Documentation & Tour",
        "url": "https://go.dev/doc/"
    },
    "Rust": {
        "title": "The Rust Programming Language Book",
        "url": "https://www.rust-lang.org/learn"
    },
    "SQL": {
        "title": "W3Schools SQL Tutorial & Certification Guide",
        "url": "https://www.w3schools.com/sql/"
    },
    "Bash": {
        "title": "GNU Bash Reference Manual",
        "url": "https://www.gnu.org/software/bash/manual/"
    },

    # Frontend
    "React": {
        "title": "React Official Documentation & Guides",
        "url": "https://react.dev/learn"
    },
    "Next.js": {
        "title": "Next.js Documentation by Vercel",
        "url": "https://nextjs.org/docs"
    },
    "Angular": {
        "title": "Angular Documentation",
        "url": "https://angular.dev/"
    },
    "Vue.js": {
        "title": "Vue.js Official Guide",
        "url": "https://vuejs.org/guide/introduction.html"
    },
    "HTML": {
        "title": "MDN Web Docs: HTML Guide",
        "url": "https://developer.mozilla.org/en-US/docs/Web/HTML"
    },
    "CSS": {
        "title": "MDN Web Docs: CSS Guide",
        "url": "https://developer.mozilla.org/en-US/docs/Web/CSS"
    },
    "Tailwind CSS": {
        "title": "Tailwind CSS Documentation",
        "url": "https://tailwindcss.com/docs"
    },
    "Redux": {
        "title": "Redux Toolkit Official Tutorials",
        "url": "https://redux.js.org/tutorials/fundamentals/part-1-overview"
    },

    # Backend
    "Node.js": {
        "title": "Node.js Official Documentation",
        "url": "https://nodejs.org/en/docs"
    },
    "Express.js": {
        "title": "Express.js Getting Started Guide",
        "url": "https://expressjs.com/"
    },
    "FastAPI": {
        "title": "FastAPI Official Documentation & Tutorial",
        "url": "https://fastapi.tiangolo.com/"
    },
    "Flask": {
        "title": "Flask Documentation (Pallets Projects)",
        "url": "https://flask.palletsprojects.com/"
    },
    "Django": {
        "title": "Django Documentation & Getting Started",
        "url": "https://docs.djangoproject.com/"
    },
    "Spring Boot": {
        "title": "Spring Boot Reference Documentation",
        "url": "https://spring.io/projects/spring-boot"
    },
    "REST API": {
        "title": "RESTful API Architectural Guidelines",
        "url": "https://restfulapi.net/"
    },
    "GraphQL": {
        "title": "GraphQL Official Introduction & Docs",
        "url": "https://graphql.org/learn/"
    },

    # Databases
    "PostgreSQL": {
        "title": "PostgreSQL Official Documentation",
        "url": "https://www.postgresql.org/docs/"
    },
    "MySQL": {
        "title": "MySQL Reference Manual",
        "url": "https://dev.mysql.com/doc/"
    },
    "MongoDB": {
        "title": "MongoDB Manual & Getting Started",
        "url": "https://www.mongodb.com/docs/"
    },
    "SQLite": {
        "title": "SQLite Official Documentation",
        "url": "https://www.sqlite.org/docs.html"
    },
    "Redis": {
        "title": "Redis Documentation & Data Structures",
        "url": "https://redis.io/docs/"
    },

    # Machine Learning & AI
    "Machine Learning": {
        "title": "Scikit-Learn Machine Learning Tutorials",
        "url": "https://scikit-learn.org/stable/tutorial/"
    },
    "Deep Learning": {
        "title": "DeepLearning.AI Learning Pathways",
        "url": "https://www.deeplearning.ai/"
    },
    "PyTorch": {
        "title": "PyTorch Official Tutorials & Recipes",
        "url": "https://pytorch.org/tutorials/"
    },
    "TensorFlow": {
        "title": "TensorFlow Official Guides and Tutorials",
        "url": "https://www.tensorflow.org/tutorials"
    },
    "Scikit-learn": {
        "title": "Scikit-learn User Guide & API Docs",
        "url": "https://scikit-learn.org/stable/"
    },
    "Pandas": {
        "title": "Pandas Data Analysis Documentation",
        "url": "https://pandas.pydata.org/docs/"
    },
    "NumPy": {
        "title": "NumPy Fundamental Library Guide",
        "url": "https://numpy.org/doc/"
    },
    "NLP": {
        "title": "NLTK Python Natural Language Processing",
        "url": "https://www.nltk.org/"
    },
    "Computer Vision": {
        "title": "OpenCV Official Tutorials",
        "url": "https://docs.opencv.org/"
    },
    "Tableau": {
        "title": "Tableau Desktop Official Help",
        "url": "https://help.tableau.com/"
    },
    "Power BI": {
        "title": "Microsoft Power BI Documentation",
        "url": "https://learn.microsoft.com/en-us/power-bi/"
    },

    # Cloud & DevOps
    "Docker": {
        "title": "Docker Get Started Guide",
        "url": "https://docs.docker.com/get-started/"
    },
    "Kubernetes": {
        "title": "Kubernetes Official Documentation",
        "url": "https://kubernetes.io/docs/home/"
    },
    "AWS": {
        "title": "AWS Getting Started Tutorials & Resource Center",
        "url": "https://aws.amazon.com/getting-started/"
    },
    "Google Cloud": {
        "title": "Google Cloud Documentation",
        "url": "https://cloud.google.com/docs"
    },
    "Microsoft Azure": {
        "title": "Microsoft Azure Fundamentals & Documentation",
        "url": "https://learn.microsoft.com/en-us/azure/"
    },
    "Linux": {
        "title": "Linux Kernel & System Documentation",
        "url": "https://www.kernel.org/doc/html/latest/"
    },
    "CI/CD": {
        "title": "GitHub Actions Continuous Integration Guide",
        "url": "https://docs.github.com/en/actions"
    },
    "Terraform": {
        "title": "HashiCorp Terraform Tutorials",
        "url": "https://developer.hashicorp.com/terraform/tutorials"
    },

    # Development Tools
    "Git": {
        "title": "Pro Git Book & Official Reference",
        "url": "https://git-scm.com/doc"
    },
    "Postman": {
        "title": "Postman API Platform Learning Center",
        "url": "https://learning.postman.com/"
    }
}


# ============================================================================
# 2. TRANSFERABLE SKILL CLUSTERS
# When candidate lacks skill X, these related skills provide partial credit
# because their core mental models and paradigms are closely aligned.
# ============================================================================
TRANSFERABLE_SKILLS: Dict[str, List[str]] = {
    "PyTorch": ["TensorFlow", "Keras", "Deep Learning"],
    "TensorFlow": ["PyTorch", "Keras", "Deep Learning"],
    "Keras": ["TensorFlow", "PyTorch", "Deep Learning"],
    "Scikit-learn": ["Machine Learning", "Pandas", "NumPy"],
    "Pandas": ["NumPy", "SQL", "Scikit-learn"],
    "NumPy": ["Pandas", "SciPy"],
    "FastAPI": ["Flask", "Django", "REST API", "Python"],
    "Flask": ["FastAPI", "Django", "REST API", "Python"],
    "Django": ["Flask", "FastAPI", "REST API", "Python"],
    "React": ["Next.js", "Vue.js", "Angular", "JavaScript", "TypeScript"],
    "Next.js": ["React", "TypeScript", "JavaScript"],
    "Vue.js": ["React", "Angular", "JavaScript"],
    "Angular": ["React", "TypeScript", "JavaScript"],
    "TypeScript": ["JavaScript"],
    "JavaScript": ["TypeScript"],
    "PostgreSQL": ["MySQL", "SQLite", "SQL", "Oracle"],
    "MySQL": ["PostgreSQL", "SQLite", "SQL", "MariaDB"],
    "MongoDB": ["DynamoDB", "Cassandra", "NoSQL"],
    "SQLite": ["PostgreSQL", "MySQL", "SQL"],
    "AWS": ["Google Cloud", "Microsoft Azure"],
    "Google Cloud": ["AWS", "Microsoft Azure"],
    "Microsoft Azure": ["AWS", "Google Cloud"],
    "Docker": ["Kubernetes", "CI/CD", "Linux"],
    "Kubernetes": ["Docker", "Linux"],
    "C++": ["C", "Java"],
    "C": ["C++"],
    "Tailwind CSS": ["Bootstrap", "CSS", "SCSS"],
    "Bootstrap": ["Tailwind CSS", "CSS"],
    "Tableau": ["Power BI"],
    "Power BI": ["Tableau"],
}


# ============================================================================
# 3. CURATED LEARNING CURRICULUM BANK
# Structured learning topics, project ideas, and realistic durations.
# ============================================================================
LEARNING_BANK: Dict[str, Dict[str, Any]] = {
    "PyTorch": {
        "topics": [
            "Tensors, Autograd & Computational Graphs",
            "Building custom neural networks with torch.nn",
            "Datasets, DataLoaders, and custom transformations",
            "Training loops, loss functions, and optimizers (Adam, SGD)",
            "Model checkpointing, GPU acceleration with CUDA, and evaluation metrics"
        ],
        "projects": [
            "Build and train a Convolutional Neural Network (CNN) for image classification with CIFAR-10",
            "Implement a Transformer or LSTM sequence model for sentiment classification from scratch"
        ],
        "duration": "3-4 weeks"
    },
    "TensorFlow": {
        "topics": [
            "Keras Sequential and Functional API architectures",
            "Data pipelines with tf.data.Dataset",
            "Transfer learning with pre-trained vision models (ResNet, MobileNet)",
            "Model export, TensorBoard visualization, and quantization"
        ],
        "projects": [
            "Build an end-to-end multi-class computer vision pipeline with data augmentation and transfer learning",
            "Develop a deep neural network regression model for predictive analytics"
        ],
        "duration": "3-4 weeks"
    },
    "Docker": {
        "topics": [
            "Containerization fundamentals, namespaces, and cgroups",
            "Writing production-ready, multi-stage Dockerfiles",
            "Docker Compose multi-container application architecture",
            "Persistent volume management, networking, and security best practices"
        ],
        "projects": [
            "Containerize a full-stack web application (React frontend, FastAPI backend, PostgreSQL database) using Docker Compose",
            "Build an ultra-lightweight production container using Alpine Linux and non-root security principles"
        ],
        "duration": "1-2 weeks"
    },
    "Kubernetes": {
        "topics": [
            "Cluster architecture: Control Plane, Nodes, Kubelet, and etcd",
            "Core primitives: Pods, Deployments, Services (ClusterIP, NodePort, LoadBalancer)",
            "ConfigMaps, Secrets, and persistent storage with PVCs",
            "Ingress controllers, horizontal pod autoscaling (HPA), and rollout strategies"
        ],
        "projects": [
            "Deploy a resilient microservices application to a local Minikube cluster with rolling updates and health probes",
            "Implement automated horizontal scaling based on CPU and memory thresholds"
        ],
        "duration": "3-5 weeks"
    },
    "AWS": {
        "topics": [
            "Cloud architecture foundations, IAM roles, policies, and least-privilege access",
            "Compute & Containers: EC2 instances, security groups, ECS, and AWS Lambda",
            "Storage & Databases: S3 buckets, lifecycle policies, RDS (PostgreSQL/MySQL), and DynamoDB",
            "Networking: VPCs, subnets, route tables, and CloudFront CDN distribution"
        ],
        "projects": [
            "Deploy a containerized API onto AWS ECS/Fargate with RDS PostgreSQL and automated S3 file storage",
            "Build a serverless image processing pipeline using AWS Lambda triggered by S3 uploads"
        ],
        "duration": "3-5 weeks"
    },
    "PostgreSQL": {
        "topics": [
            "Relational database design, normalization, foreign keys, and constraint integrity",
            "Complex queries: multi-table joins, subqueries, Common Table Expressions (CTEs), and Window Functions",
            "Indexing strategies: B-tree, GIN indexes, EXPLAIN ANALYZE query optimization",
            "Transactions, ACID guarantees, isolation levels, and concurrency control"
        ],
        "projects": [
            "Design an e-commerce transactional database schema with optimized indexing and complex analytics queries",
            "Write stored procedures and database triggers to maintain audit logs and integrity checks"
        ],
        "duration": "2-3 weeks"
    },
    "FastAPI": {
        "topics": [
            "Asynchronous request handling, event loops, and coroutines in Python",
            "Pydantic data validation, type hints, and automatic OpenAPI schema generation",
            "Dependency injection system for database sessions and authentication",
            "JWT bearer token authentication, rate limiting, and background tasks"
        ],
        "projects": [
            "Build a production-ready asynchronous REST API with JWT authentication, SQLAlchemy ORM, and automated tests",
            "Create a real-time WebSocket communication service with background task execution"
        ],
        "duration": "1-2 weeks"
    },
    "React": {
        "topics": [
            "Component lifecycle, JSX, props, and conditional rendering",
            "Hooks in depth: useState, useEffect, useMemo, useCallback, and useRef",
            "Global state management: Context API and modern Redux Toolkit",
            "Routing with React Router, code splitting, and performance profiling"
        ],
        "projects": [
            "Build a responsive enterprise analytics dashboard with interactive charts and dynamic filtering",
            "Create an e-commerce shopping platform with persistent cart state and asynchronous checkout"
        ],
        "duration": "2-4 weeks"
    },
    "TypeScript": {
        "topics": [
            "Static typing, type inference, union types, and type narrowing",
            "Interfaces vs Type Aliases, utility types (Partial, Pick, Omit, Record)",
            "Generics in functions, classes, and interfaces",
            "Configuring tsconfig.json, module resolution, and strict null checking"
        ],
        "projects": [
            "Migrate an existing JavaScript codebase to strict TypeScript with comprehensive type coverage",
            "Build a strongly-typed API client library with runtime schema validation"
        ],
        "duration": "1-2 weeks"
    },
    "Machine Learning": {
        "topics": [
            "Supervised learning: linear/logistic regression, decision trees, random forests, and gradient boosting",
            "Unsupervised learning: K-Means clustering, PCA dimensionality reduction",
            "Data preprocessing, feature engineering, imputation, and categorical encoding",
            "Cross-validation, hyperparameter tuning (GridSearchCV), and evaluation metrics (ROC-AUC, F1-score)"
        ],
        "projects": [
            "Build a customer churn prediction model with comprehensive feature engineering and model interpretation",
            "Develop an end-to-end ML pipeline with Scikit-learn for automated data transformation and prediction"
        ],
        "duration": "4-6 weeks"
    },
    "Scikit-learn": {
        "topics": [
            "Estimator, Transformer, and Predictor interfaces",
            "Building robust composite Pipelines and ColumnTransformers",
            "Model selection, K-Fold cross-validation, and GridSearchCV/RandomizedSearchCV",
            "Feature selection techniques, PCA, and metrics calculation"
        ],
        "projects": [
            "Create a clean Scikit-learn Pipeline that handles numerical scaling and categorical encoding seamlessly",
            "Build a predictive pricing model and evaluate using RMSE, MAE, and R-squared metrics"
        ],
        "duration": "2-3 weeks"
    },
    "Deep Learning": {
        "topics": [
            "Multilayer Perceptrons, activation functions (ReLU, Sigmoid, Softmax), and backpropagation",
            "Convolutional Neural Networks (CNNs) for spatial pattern recognition",
            "Recurrent Neural Networks (RNNs, LSTMs, GRUs) for sequential data",
            "Regularization: Dropout, Batch Normalization, Weight Decay, and Early Stopping"
        ],
        "projects": [
            "Train a deep neural network for medical image classification using transfer learning",
            "Construct a sequential time-series forecasting model for financial or demand metrics"
        ],
        "duration": "4-6 weeks"
    },
    "NLP": {
        "topics": [
            "Text tokenization, lemmatization, stopword filtering, and POS tagging",
            "TF-IDF vectorization, Word2Vec, GloVe word embeddings",
            "Transformer architectures, self-attention mechanisms, and BERT fine-tuning",
            "Named Entity Recognition (NER), text classification, and sentiment analysis"
        ],
        "projects": [
            "Build an automated resume classification engine using TF-IDF and supervised classifiers",
            "Fine-tune a Hugging Face Transformer for domain-specific customer query intent detection"
        ],
        "duration": "3-4 weeks"
    },
    "CI/CD": {
        "topics": [
            "Continuous Integration principles, automated linting, and unit testing",
            "Continuous Delivery & Deployment pipelines using GitHub Actions",
            "Branch protection rules, automated test gating, and semantic versioning",
            "Secure secret management, artifact caching, and environment deployments"
        ],
        "projects": [
            "Implement a complete GitHub Actions workflow that runs pytest, builds a Docker image, and triggers automated deployment",
            "Create a reusable pipeline for automated dependency scanning and code coverage reporting"
        ],
        "duration": "1-2 weeks"
    }
}


class SkillGapService:
    """
    Intelligent Skill Gap Analysis & Personalized Learning Recommendation Service.
    
    Responsibilities:
    - Compare candidate profile skills against required & preferred job skills.
    - Classify skills into Matched, Partial Match, or Missing based on canonical taxonomy,
      transferable domain knowledge, and Phase 4 extracted proficiency levels.
    - Compute transparent coverage metrics (Required match %, Preferred coverage %, Overall coverage %).
    - Generate structured, high-value learning roadmaps prioritized by requirement criticality.
    """

    def __init__(self):
        self.extractor = SkillExtractionService()

    def _canonicalize_skill(self, skill_name: str) -> str:
        """Normalize a skill name to its canonical taxonomy form."""
        if not skill_name:
            return ""
        norm = self.extractor.normalize_skill(str(skill_name).strip())
        return norm if norm else str(skill_name).strip().title()

    def _build_candidate_skill_map(self, candidate_skills: Any) -> Dict[str, Dict[str, Any]]:
        """
        Builds a canonical, lowercase-indexed dictionary of candidate skills
        preserving extracted proficiency and evidence from Phase 4.
        """
        skill_map: Dict[str, Dict[str, Any]] = {}

        if not candidate_skills:
            return skill_map

        # Case 1: List of strings or dicts
        items = candidate_skills if isinstance(candidate_skills, list) else [candidate_skills]
        for item in items:
            if isinstance(item, dict):
                raw_name = item.get("name") or item.get("skill") or ""
                proficiency = item.get("proficiency") or "Beginner"
                evidence = item.get("evidence") or []
                sources = item.get("sources") or []
            elif isinstance(item, str):
                raw_name = item
                proficiency = "Beginner"
                evidence = []
                sources = []
            else:
                continue

            canonical = self._canonicalize_skill(raw_name)
            if not canonical:
                continue

            key = canonical.lower()
            category = self.extractor.get_skill_category(canonical)

            if key not in skill_map:
                skill_map[key] = {
                    "canonical_name": canonical,
                    "category": category,
                    "proficiency": proficiency,
                    "evidence": evidence,
                    "sources": sources
                }
            else:
                # Merge evidence & escalate proficiency if higher
                existing_prof = skill_map[key]["proficiency"]
                prof_rank = {"Advanced": 3, "Intermediate": 2, "Beginner": 1, "Unknown": 0}
                if prof_rank.get(proficiency, 0) > prof_rank.get(existing_prof, 0):
                    skill_map[key]["proficiency"] = proficiency
                if evidence:
                    for ev in evidence:
                        if ev not in skill_map[key]["evidence"]:
                            skill_map[key]["evidence"].append(ev)

        return skill_map

    def _evaluate_skill(
        self,
        skill_name: str,
        requirement_type: str,
        candidate_map: Dict[str, Dict[str, Any]],
        job_exp_level: str = "Entry-level"
    ) -> Dict[str, Any]:
        """
        Evaluates a single job skill against candidate skills.
        Classifies into 'matched', 'partial', or 'missing'.
        """
        canonical = self._canonicalize_skill(skill_name)
        category = self.extractor.get_skill_category(canonical)
        key = canonical.lower()

        is_senior_role = job_exp_level.lower() in ["senior", "lead", "principal", "manager", "mid-level", "intermediate"]

        # 1. Exact or canonical alias match in candidate skills
        if key in candidate_map:
            cand_info = candidate_map[key]
            prof = cand_info.get("proficiency", "Beginner")
            evidence = cand_info.get("evidence", [])

            # Check for proficiency gap:
            # If the job is Mid/Senior-level, and the candidate is Beginner (e.g. only in skills section without projects)
            if is_senior_role and prof == "Beginner" and requirement_type == "required":
                return {
                    "name": canonical,
                    "status": "partial",
                    "requirement_type": requirement_type,
                    "category": category,
                    "current_proficiency": prof,
                    "proficiency_evidence": evidence,
                    "reason": f"Possesses foundational knowledge ({prof}), but {job_exp_level} role requires intermediate/advanced production experience.",
                    "transferable_from": None
                }
            else:
                return {
                    "name": canonical,
                    "status": "matched",
                    "requirement_type": requirement_type,
                    "category": category,
                    "current_proficiency": prof,
                    "proficiency_evidence": evidence,
                    "reason": f"Directly matched in resume with {prof} proficiency.",
                    "transferable_from": None
                }

        # 2. Check for transferable domain skills
        transferable_options = TRANSFERABLE_SKILLS.get(canonical, [])
        found_transferable = []
        for opt in transferable_options:
            if opt.lower() in candidate_map:
                found_transferable.append(candidate_map[opt.lower()]["canonical_name"])

        if found_transferable:
            primary_transfer = found_transferable[0]
            cand_transfer_prof = candidate_map[primary_transfer.lower()].get("proficiency", "Intermediate")
            transfer_str = ", ".join(found_transferable[:2])
            return {
                "name": canonical,
                "status": "partial",
                "requirement_type": requirement_type,
                "category": category,
                "current_proficiency": f"Transferable ({cand_transfer_prof})",
                "proficiency_evidence": [f"Transferable domain knowledge demonstrated via {transfer_str}"],
                "reason": f"Transferable domain competency identified via {transfer_str}. Core concepts are directly applicable.",
                "transferable_from": primary_transfer
            }

        # 3. Completely missing
        return {
            "name": canonical,
            "status": "missing",
            "requirement_type": requirement_type,
            "category": category,
            "current_proficiency": None,
            "proficiency_evidence": [],
            "reason": f"Skill not detected in candidate profile or projects.",
            "transferable_from": None
        }

    def _generate_learning_recommendation(
        self,
        skill_item: Dict[str, Any],
        job_title: str,
        job_category: str,
        job_exp_level: str
    ) -> Dict[str, Any]:
        """
        Creates a personalized learning recommendation for a missing or partial skill.
        """
        skill_name = skill_item["name"]
        category = skill_item["category"]
        status = skill_item["status"]
        req_type = skill_item["requirement_type"]
        current_prof = skill_item["current_proficiency"]

        is_senior = job_exp_level.lower() in ["senior", "lead", "principal", "mid-level"]
        target_prof = "Advanced" if is_senior else "Intermediate"

        # Priority rules:
        # High: Required skills that are missing
        # Medium: Required skills with partial proficiency
        # Low: Preferred skills that are missing or partial
        if req_type == "required":
            priority = "High" if status == "missing" else "Medium"
        else:
            priority = "Low"

        # Tailored dynamic reason
        if status == "missing" and req_type == "required":
            reason = f"Essential required core competency for {job_title}. Closing this gap directly improves qualification eligibility."
        elif status == "partial" and req_type == "required":
            if skill_item.get("transferable_from"):
                reason = f"Leverage your existing background in {skill_item['transferable_from']} to transition into {skill_name}."
            else:
                reason = f"Candidate has foundational awareness; elevating to {target_prof} proficiency satisfies {job_title} production requirements."
        else:
            reason = f"Valuable preferred qualification for {job_category}. Gives a distinctive competitive advantage during technical interviews."

        # Fetch curated topics or generate robust defaults
        bank_entry = LEARNING_BANK.get(skill_name)
        if bank_entry:
            topics = bank_entry["topics"]
            projects = bank_entry["projects"]
            duration = bank_entry["duration"]
        else:
            # High-quality fallback curriculum generated by domain category
            topics = [
                f"{skill_name} core syntax, architecture, and foundational primitives",
                f"Idiomatic design patterns, testing strategies, and debugging with {skill_name}",
                f"Integration of {skill_name} into end-to-end production application workflows",
                f"Performance optimization, security best practices, and error handling"
            ]
            projects = [
                f"Build a production-grade module implementing {skill_name} with automated unit tests",
                f"Integrate {skill_name} into a full-stack portfolio project demonstrating practical utility"
            ]
            duration = "2-3 weeks" if status == "partial" else "3-4 weeks"

        # Verified resources only
        resources = []
        if skill_name in VERIFIED_RESOURCES:
            res_meta = VERIFIED_RESOURCES[skill_name]
            resources.append({
                "title": res_meta["title"],
                "url": res_meta["url"],
                "resource_type": "Official Documentation"
            })
        else:
            # Topic without invented link
            resources.append({
                "title": f"Official {skill_name} Documentation and Reference Guide",
                "url": None,
                "resource_type": "Curriculum Reference"
            })

        return {
            "skill_name": skill_name,
            "category": category,
            "current_proficiency": current_prof,
            "target_proficiency": target_prof,
            "priority": priority,
            "reason": reason,
            "learning_topics": topics,
            "project_ideas": projects,
            "estimated_duration": duration,
            "resources": resources
        }

    def analyze_skill_gap(
        self,
        candidate_skills: Any,
        required_skills: List[str],
        preferred_skills: Optional[List[str]] = None,
        job_title: str = "Software Position",
        job_category: str = "Technology",
        job_exp_level: str = "Entry-level"
    ) -> Dict[str, Any]:
        """
        Executes full skill comparison, computes metrics, and builds prioritized recommendations.
        """
        pref_list = preferred_skills if isinstance(preferred_skills, list) else []
        req_list = required_skills if isinstance(required_skills, list) else []

        candidate_map = self._build_candidate_skill_map(candidate_skills)

        # 1. Analyze Required Skills (Deduplicated canonical order)
        req_analysis: List[Dict[str, Any]] = []
        seen_req: Set[str] = set()
        for s in req_list:
            if not s or not str(s).strip():
                continue
            canonical = self._canonicalize_skill(str(s))
            if canonical.lower() in seen_req:
                continue
            seen_req.add(canonical.lower())
            item = self._evaluate_skill(canonical, "required", candidate_map, job_exp_level)
            req_analysis.append(item)

        # 2. Analyze Preferred Skills (Deduplicated canonical order, exclude skills already in required)
        pref_analysis: List[Dict[str, Any]] = []
        seen_pref: Set[str] = set()
        for s in pref_list:
            if not s or not str(s).strip():
                continue
            canonical = self._canonicalize_skill(str(s))
            c_lower = canonical.lower()
            if c_lower in seen_req or c_lower in seen_pref:
                continue
            seen_pref.add(c_lower)
            item = self._evaluate_skill(canonical, "preferred", candidate_map, job_exp_level)
            pref_analysis.append(item)

        # 3. Categorize matched, partial, missing
        matched_skills = [
            it["name"] for it in req_analysis + pref_analysis if it["status"] == "matched"
        ]
        partial_skills = [
            it["name"] for it in req_analysis + pref_analysis if it["status"] == "partial"
        ]
        missing_skills = [
            it["name"] for it in req_analysis + pref_analysis if it["status"] == "missing"
        ]

        # 4. Compute Metrics
        tot_req = len(req_analysis)
        matched_req = len([it for it in req_analysis if it["status"] == "matched"])
        partial_req = len([it for it in req_analysis if it["status"] == "partial"])
        missing_req = len([it for it in req_analysis if it["status"] == "missing"])

        tot_pref = len(pref_analysis)
        matched_pref = len([it for it in pref_analysis if it["status"] == "matched"])
        partial_pref = len([it for it in pref_analysis if it["status"] == "partial"])
        missing_pref = len([it for it in pref_analysis if it["status"] == "missing"])

        # Required match formula: (matched + 0.5 * partial) / total * 100
        if tot_req == 0:
            req_match_pct = 100.0
        else:
            req_match_pct = round(((matched_req + (0.5 * partial_req)) / tot_req) * 100.0, 1)

        # Preferred coverage formula: (matched + 0.5 * partial) / total * 100
        if tot_pref == 0:
            pref_cov_pct = 100.0
        else:
            pref_cov_pct = round(((matched_pref + (0.5 * partial_pref)) / tot_pref) * 100.0, 1)

        # Overall coverage: 75% weight on required, 25% on preferred
        if tot_pref > 0 and tot_req > 0:
            overall_pct = round((0.75 * req_match_pct) + (0.25 * pref_cov_pct), 1)
        elif tot_req > 0:
            overall_pct = req_match_pct
        else:
            overall_pct = 100.0

        metrics = {
            "total_required": tot_req,
            "matched_required": matched_req,
            "partial_required": partial_req,
            "missing_required": missing_req,
            "total_preferred": tot_pref,
            "matched_preferred": matched_pref,
            "partial_preferred": partial_pref,
            "missing_preferred": missing_pref,
            "required_match_percentage": req_match_pct,
            "preferred_coverage_percentage": pref_cov_pct,
            "overall_coverage_percentage": overall_pct
        }

        # 5. Build Personalized Learning Recommendations
        learning_recs: List[Dict[str, Any]] = []

        # High priority: Missing required skills
        for item in req_analysis:
            if item["status"] == "missing":
                rec = self._generate_learning_recommendation(item, job_title, job_category, job_exp_level)
                learning_recs.append(rec)

        # Medium priority: Partial required skills
        for item in req_analysis:
            if item["status"] == "partial":
                rec = self._generate_learning_recommendation(item, job_title, job_category, job_exp_level)
                learning_recs.append(rec)

        # Low priority: Missing / partial preferred skills
        for item in pref_analysis:
            if item["status"] in ["missing", "partial"]:
                rec = self._generate_learning_recommendation(item, job_title, job_category, job_exp_level)
                learning_recs.append(rec)

        # Summary Generation
        if overall_pct >= 80.0:
            summary = f"Strong qualification match ({overall_pct}% overall coverage). You possess the majority of core required competencies for {job_title}."
        elif overall_pct >= 50.0:
            summary = f"Moderate qualification match ({overall_pct}% overall coverage). Key foundational proficiencies align, with {missing_req} required and {missing_pref} preferred skills identified for targeted upskilling."
        else:
            summary = f"Significant skill gap detected ({overall_pct}% overall coverage). Focused learning on the {missing_req} missing required competencies will substantially improve compatibility for {job_title}."

        return {
            "metrics": metrics,
            "matched_skills": matched_skills,
            "partial_skills": partial_skills,
            "missing_skills": missing_skills,
            "required_skills_analysis": req_analysis,
            "preferred_skills_analysis": pref_analysis,
            "learning_recommendations": learning_recs,
            "summary": summary
        }
