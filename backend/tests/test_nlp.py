import pytest
from app.ml.preprocessor import TextPreprocessor
from app.services.nlp_service import ResumeParser

SAMPLE_RESUME_TEXT = """
RAHUL SHARMA
Email: rahul.sharma@email.com | Phone: +91-9876543210
LinkedIn: linkedin.com/in/rahulsharma | GitHub: github.com/rahulsharma

EDUCATION

Bachelor of Technology in Computer Science
Indian Institute of Technology, Delhi
Graduation Year: 2025 | CGPA: 8.7/10

TECHNICAL SKILLS

Programming Languages: Python, Java, C++, JavaScript
Frameworks: React, Flask, FastAPI, Django
Libraries: Pandas, NumPy, Scikit-learn, TensorFlow, Matplotlib
Databases: MySQL, PostgreSQL, MongoDB, SQLite
Cloud: AWS (EC2, S3), Google Cloud Platform
Tools: Git, Docker, VS Code, Jupyter Notebook, Linux

PROJECTS

1. AI Chatbot for Customer Support
   - Built a chatbot using NLP and machine learning
   - Technologies: Python, NLTK, Flask, TensorFlow
   - Achieved 87% accuracy on intent classification

2. E-Commerce Analytics Dashboard
   - Developed a real-time analytics dashboard
   - Technologies: React, Node.js, MongoDB, Chart.js

WORK EXPERIENCE

Software Engineering Intern | Google India
June 2024 - August 2024
- Developed microservices for search optimization
- Improved API response time by 25%

Data Science Intern | Flipkart
January 2024 - March 2024
- Analyzed customer purchase patterns using Python and SQL

CERTIFICATIONS

- AWS Certified Cloud Practitioner
- Google Data Analytics Professional Certificate
- Deep Learning Specialization - Coursera
"""

class TestTextPreprocessor:
    @pytest.fixture
    def preprocessor(self):
        return TextPreprocessor()

    def test_clean_text_removes_urls(self, preprocessor):
        text = "Check out https://example.com and www.test.com"
        cleaned = preprocessor.clean_text(text)
        assert "http" not in cleaned
        assert "www" not in cleaned

    def test_clean_text_lowercase(self, preprocessor):
        text = "PYTHON AND JAVA"
        assert preprocessor.clean_text(text) == "python and java"

    def test_clean_text_normalizes_whitespace(self, preprocessor):
        text = "too    much\t\nwhitespace"
        assert preprocessor.clean_text(text) == "too much whitespace"

    def test_tokenize_returns_list(self, preprocessor):
        tokens = preprocessor.tokenize("python java c++")
        assert isinstance(tokens, list)
        assert len(tokens) > 0

    def test_tokenize_filters_punctuation(self, preprocessor):
        tokens = preprocessor.tokenize("hello, world! this is a test.")
        for token in tokens:
            assert token not in (',', '!', '.')

    def test_remove_stopwords(self, preprocessor):
        tokens = ["the", "quick", "brown", "fox", "is", "resume"]
        filtered = preprocessor.remove_stopwords(tokens)
        assert "the" not in filtered
        assert "is" not in filtered
        assert "resume" not in filtered
        assert "quick" in filtered

    def test_remove_stopwords_keeps_c_r(self, preprocessor):
        tokens = ["c", "r", "python"]
        filtered = preprocessor.remove_stopwords(tokens)
        assert "c" in filtered
        assert "r" in filtered

    def test_lemmatize(self, preprocessor):
        tokens = ["running", "cats", "better"]
        lemmatized = preprocessor.lemmatize(tokens)
        assert isinstance(lemmatized, list)
        assert len(lemmatized) == 3

    def test_full_pipeline(self, preprocessor):
        text = "The QUICK brown fox jumped over the lazy dogs! My resume is here."
        result = preprocessor.preprocess_pipeline(text)
        assert isinstance(result, str)
        assert "the" not in result
        assert "resume" not in result

    def test_get_tokens(self, preprocessor):
        tokens = preprocessor.get_tokens("The QUICK brown fox!")
        assert isinstance(tokens, list)

class TestResumeParser:
    @pytest.fixture
    def parser(self):
        return ResumeParser()

    def test_extract_name(self, parser):
        name = parser.extract_name(SAMPLE_RESUME_TEXT)
        assert name.upper() == "RAHUL SHARMA"

    def test_extract_email(self, parser):
        email = parser.extract_email(SAMPLE_RESUME_TEXT)
        assert email == "rahul.sharma@email.com"

    def test_extract_phone(self, parser):
        phone = parser.extract_phone(SAMPLE_RESUME_TEXT)
        assert "+91-9876543210" in phone or "9876543210" in phone

    def test_detect_sections(self, parser):
        sections = parser.detect_sections(SAMPLE_RESUME_TEXT)
        assert 'education' in sections
        assert 'skills' in sections
        assert 'projects' in sections
        assert 'experience' in sections
        assert 'certifications' in sections

    def test_parse_education(self, parser):
        sections = parser.detect_sections(SAMPLE_RESUME_TEXT)
        edu_text = sections.get('education', '')
        edu_list = parser.parse_education(edu_text)
        assert len(edu_list) >= 1
        edu = edu_list[0]
        assert "Bachelor of Technology" in edu.get('degree', '')
        assert "Indian Institute of Technology" in edu.get('institution', '')
        assert "2025" in edu.get('graduation_year', '')
        assert "8.7" in edu.get('cgpa', '')

    def test_parse_experience(self, parser):
        sections = parser.detect_sections(SAMPLE_RESUME_TEXT)
        exp_text = sections.get('experience', '')
        exp_list = parser.parse_experience(exp_text)
        assert len(exp_list) >= 2
        titles = [e['title'] for e in exp_list]
        assert "Software Engineering Intern" in titles[0] or "Software Engineering Intern" in titles[1]

    def test_parse_projects(self, parser):
        sections = parser.detect_sections(SAMPLE_RESUME_TEXT)
        proj_text = sections.get('projects', '')
        proj_list = parser.parse_projects(proj_text)
        assert len(proj_list) >= 2
        names = [p['name'] for p in proj_list]
        assert "AI Chatbot for Customer Support" in names
        techs = proj_list[0]['technologies']
        assert "Python" in techs
        
    def test_extract_certifications(self, parser):
        sections = parser.detect_sections(SAMPLE_RESUME_TEXT)
        cert_text = sections.get('certifications', '')
        certs = parser.extract_certifications(cert_text)
        assert len(certs) == 3
        assert "AWS Certified Cloud Practitioner" in certs

    def test_full_parse(self, parser):
        profile = parser.parse_resume(SAMPLE_RESUME_TEXT)
        assert profile['name'].upper() == "RAHUL SHARMA"
        assert profile['email'] == "rahul.sharma@email.com"
        assert len(profile['education']) > 0
        assert len(profile['experience']) == 2
        assert len(profile['projects']) == 2
        assert len(profile['certifications']) == 3

class TestEdgeCases:
    @pytest.fixture
    def parser(self):
        return ResumeParser()
        
    def test_empty_text(self, parser):
        profile = parser.parse_resume("")
        assert profile['name'] is None
        assert profile['email'] is None
        assert len(profile['education']) == 0
        
    def test_no_sections(self, parser):
        text = "Just a bunch of random text\nwith no clear headers\nor anything useful."
        profile = parser.parse_resume(text)
        assert len(profile['education']) == 0
        
    def test_unusual_formatting(self, parser):
        text = "John Doe\njohn@test.com\n\nEdUcAtIoN\nBS CS 2020\n\nPrOjEcTs\n1. Test Project"
        profile = parser.parse_resume(text)
        assert "education" in profile


class TestTechnologyExtraction:
    @pytest.fixture
    def parser(self):
        return ResumeParser()

    def test_prefixed_tech_stack_formats(self, parser):
        text = """
1. Web App
Tech Stack: Python, React, SQL

2. API Service
Technologies Used: Python | Flask | MySQL
"""
        projects = parser.parse_projects(text)
        assert len(projects) == 2
        assert projects[0]['technologies'] == ['Python', 'React', 'SQL']
        assert projects[1]['technologies'] == ['Python', 'Flask', 'MySQL']

    def test_bullet_tech_stack_formats(self, parser):
        text = """
1. Data Pipeline
• Python, Pandas, NumPy

2. Full Stack App
- React.js, Node.js, MongoDB

3. Backend Service
* Java, Spring Boot, PostgreSQL
"""
        projects = parser.parse_projects(text)
        assert len(projects) == 3
        assert "Pandas" in projects[0]['technologies']
        assert "React.js" in projects[1]['technologies']
        assert "Spring Boot" in projects[2]['technologies']

    def test_single_letter_languages_and_deduplication(self, parser):
        text = """
1. Systems Software
Tech Stack: C, C++, Python, R, python, C
"""
        projects = parser.parse_projects(text)
        assert len(projects) == 1
        techs = projects[0]['technologies']
        assert techs == ['C', 'C++', 'Python', 'R']

    def test_tech_in_project_description(self, parser):
        text = """
1. E-Commerce
Developed an application using React and PostgreSQL with Docker deployment.
"""
        projects = parser.parse_projects(text)
        assert len(projects) == 1
        techs = projects[0]['technologies']
        assert "React" in techs
        assert "PostgreSQL" in techs
        assert "Docker" in techs


class TestDateParsingFormats:
    @pytest.fixture
    def parser(self):
        return ResumeParser()

    def test_date_range_formats(self, parser):
        date_samples = [
            ('Jan 2023 - Dec 2024', 'Jan 2023 - Dec 2024'),
            ('January 2022 \u2013 Present', 'January 2022 \u2013 Present'),
            ('2021 - 2023', '2021 - 2023'),
            ('06/2022 - 08/2024', '06/2022 - 08/2024'),
            ('2022 \u2013 Present', '2022 \u2013 Present'),
            ('May 2023 to July 2024', 'May 2023 to July 2024'),
            ('2023 - Current', '2023 - Current'),
        ]
        for sample, expected in date_samples:
            extracted = parser.extract_date_range(sample)
            assert extracted == expected, f"Failed on {sample}"

    def test_non_dates_not_extracted(self, parser):
        non_dates = [
            'Graduation Year: 2025 | CGPA: 8.7/10',
            '+91-9876543210',
            'Software Engineering Intern | Google India'
        ]
        for sample in non_dates:
            assert parser.extract_date_range(sample) is None or not parser.is_pure_date_line(sample)

    def test_experience_with_various_date_formats(self, parser):
        text = """
Software Engineer | Amazon
May 2023 to July 2024
- Built distributed backend systems

Data Analyst at Meta (06/2022 - 08/2024)
- Designed telemetry dashboards
"""
        exp = parser.parse_experience(text)
        assert len(exp) == 2
        assert exp[0]['duration'] == 'May 2023 to July 2024'
        assert exp[0]['title'] == 'Software Engineer'
        assert exp[0]['company'] == 'Amazon'
        assert exp[1]['duration'] == '06/2022 - 08/2024'
        assert exp[1]['title'] == 'Data Analyst'
        assert exp[1]['company'] == 'Meta'

