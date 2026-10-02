import re
from typing import Optional, List, Dict, Any
from app.ml.preprocessor import TextPreprocessor


# Broad set of bullet markers used in PDFs, Word documents, and text resumes
BULLET_CHARS = r'[\-•▪*–—+●▫‣⁃\uf0b7\ufffd]'
BULLET_REGEX = re.compile(rf'^\s*{BULLET_CHARS}+\s*')


class ResumeParser:
    """Parses resume text to extract structured information.
    
    Uses a combination of:
    - Regex patterns for contact info (email, phone)
    - Section header detection for resume structure
    - Heuristic parsing for education, experience, projects
    
    WHY NOT PURE ML FOR EVERYTHING?
    Resumes have predictable structures. Using regex + heuristics for 
    well-defined patterns (emails, phone numbers, section headers) is:
    - More reliable than ML for structured patterns
    - Faster (no model inference needed)
    - Explainable (you can show exactly why something was extracted)
    ML is better for understanding unstructured content (which we'll use later).
    """

    def __init__(self):
        self.preprocessor = TextPreprocessor()
        
        # Section header patterns mapping standardized names to common variants
        self.section_patterns = {
            'education': [
                r'education', r'academic background', r'academic qualifications',
                r'academic details', r'academics', r'qualification', r'qualifications',
                r'educational background'
            ],
            'experience': [
                r'work experience', r'professional experience', r'employment history',
                r'employment', r'work history', r'experience', r'industry experience'
            ],
            'skills': [
                r'technical skills', r'key skills', r'core competencies',
                r'technical proficiencies', r'skills & expertise', r'soft skills',
                r'skills', r'tools & technologies', r'technologies'
            ],
            'projects': [
                r'academic projects', r'personal projects', r'key projects',
                r'selected projects', r'hands-on projects', r'projects'
            ],
            'certifications': [
                r'certifications & licenses', r'certifications', r'certificates',
                r'awards & achievements', r'awards', r'honors', r'achievements'
            ],
            'internship': [
                r'internships', r'internship experience', r'internship',
                r'industrial training', r'practical training'
            ],
            'summary': [
                r'professional summary', r'career summary', r'career objective',
                r'executive summary', r'summary', r'objective', r'about me',
                r'about', r'profile'
            ],
            'strengths': [
                r'strengths & interests', r'strengths', r'core strengths',
                r'areas of interest', r'interests', r'hobbies'
            ],
            'activities': [
                r'extracurricular activities', r'extracurricular',
                r'leadership & activities', r'volunteer experience', r'volunteering'
            ],
            'publications': [
                r'publications', r'research papers', r'patents'
            ]
        }

    # Date range extraction patterns
    MONTHS = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
    NUM_MONTHS = r'(?:0?[1-9]|1[0-2])'
    YEAR = r'(?:19|20)\d{2}'
    DATE_POINT = rf'(?:{MONTHS}\.?,?\s+{YEAR}|{NUM_MONTHS}[\/\-]{YEAR}|{YEAR})'
    ONGOING = r'(?:Present|Current|Ongoing|Now|Till Date)'
    SEPARATOR = r'(?:\s*(?:[-–—\u2010-\u2015]|to|till|until)\s*)'
    DATE_RANGE_REGEX = re.compile(rf'\b({DATE_POINT}{SEPARATOR}(?:{DATE_POINT}|{ONGOING}))\b', re.IGNORECASE)

    # Technology knowledge base for robust extraction and canonical casing
    TECH_LIST = [
        'Python', 'Java', 'C++', 'C', 'C#', 'R', 'Go', 'Golang', 'Rust', 'Ruby',
        'PHP', 'Swift', 'Kotlin', 'TypeScript', 'JavaScript', 'Dart', 'Scala',
        'SQL', 'PL/SQL', 'HTML', 'HTML5', 'CSS', 'CSS3', 'Bash', 'Shell', 'PowerShell',
        'React', 'React.js', 'React Native', 'Angular', 'AngularJS', 'Vue', 'Vue.js',
        'Next.js', 'Node.js', 'Express', 'Express.js', 'Django', 'Flask', 'FastAPI',
        'Spring', 'Spring Boot', 'Hibernate', 'ASP.NET', '.NET', '.NET Core',
        'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch', 'Keras',
        'Matplotlib', 'Seaborn', 'OpenCV', 'NLTK', 'spaCy', 'SciPy', 'XGBoost', 'LightGBM',
        'Chart.js', 'D3.js', 'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 'Redis', 'Oracle',
        'Cassandra', 'DynamoDB', 'Elasticsearch', 'Firebase', 'Kafka', 'Spark', 'PySpark',
        'Hadoop', 'Tableau', 'Power BI', 'AWS', 'Azure', 'GCP', 'Google Cloud',
        'Docker', 'Kubernetes', 'Git', 'GitHub', 'GitLab', 'CI/CD', 'Linux', 'GraphQL',
        'REST', 'RESTful', 'REST API', 'Machine Learning', 'Deep Learning', 'NLP',
        'Artificial Intelligence', 'Computer Vision', 'VS Code', 'Visual Studio Code',
        'Postman', 'Tailwind CSS', 'Tailwind', 'Bootstrap'
    ]
    CANONICAL_MAP = {t.lower(): t for t in TECH_LIST}
    CANONICAL_MAP.update({
        'scikitlearn': 'Scikit-learn',
        'sklearn': 'Scikit-learn',
        'reactjs': 'React.js',
        'nodejs': 'Node.js',
        'springboot': 'Spring Boot',
        'postgres': 'PostgreSQL',
        'rest api': 'REST API',
        'golang': 'Go',
        'machine learning': 'Machine Learning',
        'ml': 'Machine Learning',
        'deep learning': 'Deep Learning',
        'nlp': 'NLP',
        'natural language processing': 'NLP',
        'ai': 'Artificial Intelligence',
        'artificial intelligence': 'Artificial Intelligence',
        'vs code': 'VS Code',
        'vscode': 'VS Code',
        'visual studio code': 'VS Code',
        'tailwind': 'Tailwind CSS',
        'tailwindcss': 'Tailwind CSS'
    })
    SORTED_TECHS = sorted(CANONICAL_MAP.keys(), key=lambda x: len(x), reverse=True)

    TECH_PREFIX_REGEX = re.compile(
        r'^(?:[-•▪*–—+●▫‣⁃\uf0b7\ufffd\s]*)(?:technologies(?:\s+used)?|tech(?:\s*stack)?|tools(?:\s+used)?|built\s+with|stack|environment)\s*[:\-]\s*(.*)$',
        re.IGNORECASE
    )

    def parse_resume(self, text: str) -> dict:
        """Master method that orchestrates all extraction."""
        sections = self.detect_sections(text)
        
        return {
            'name': self.extract_name(text),
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'education': self.parse_education(self._get_section_text(sections, ['education'])),
            'experience': self.parse_experience(
                self._get_section_text(sections, ['experience']) + "\n" + 
                self._get_section_text(sections, ['internship'])
            ),
            'projects': self.parse_projects(self._get_section_text(sections, ['projects'])),
            'skills': self._get_section_text(sections, ['skills']),
            'certifications': self.extract_certifications(self._get_section_text(sections, ['certifications'])),
        }

    def extract_name(self, text: str) -> Optional[str]:
        """
        Extracts candidate name from the top lines of the resume.
        Supports names with initials (e.g. 'PRAJWAL P.', 'A. B. Sharma', 'John D. Doe').
        """
        if not text:
            return None

        lines = [line.strip() for line in text.split('\n') if line.strip()]
        contact_keywords = {
            'email', 'phone', 'mobile', 'linkedin', 'github', 'portfolio',
            'website', 'curriculum', 'vitae', 'resume', 'address', 'http',
            'www', 'street', 'city', 'state', 'india', 'profile'
        }

        # The candidate name is almost universally within the first 6 non-empty lines
        candidate_pool = lines[:8]

        for line in candidate_pool:
            clean = line.strip(' \t,|;')
            if not clean:
                continue

            # Must contain letters, spaces, hyphens, and periods (for initials like 'P.')
            if re.match(r'^[A-Za-z.\-\s]{2,45}$', clean):
                words = clean.split()
                if 1 <= len(words) <= 5:
                    lower = clean.lower()

                    # Avoid section headers
                    is_header = any(
                        variant in lower
                        for variants in self.section_patterns.values()
                        for variant in variants
                    )
                    if is_header:
                        continue

                    # Avoid contact terms
                    if any(k in lower for k in contact_keywords):
                        continue

                    # Avoid phone numbers, emails, addresses, links
                    if any(c in line for c in ('@', '|', ':', '/', '+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                        continue

                    return clean

        return None

    def extract_email(self, text: str) -> Optional[str]:
        """Extracts email address using regex."""
        match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        return match.group(0) if match else None

    def extract_phone(self, text: str) -> Optional[str]:
        """Extracts phone number using regex."""
        match = re.search(r'(\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}|\+91[\s.-]?\d{10}|\d{10}', text)
        return match.group(0) if match else None

    def detect_sections(self, text: str) -> dict[str, str]:
        """Detects resume sections by their headers with high tolerance for formatting."""
        sections = {}
        if not text:
            return sections

        lines = text.split('\n')
        current_section = 'header'
        sections[current_section] = []

        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            # Strip leading/trailing decorative characters (e.g. '=== EDUCATION ===', 'PROJECTS:', '## SKILLS')
            candidate = re.sub(r'^[#*=_~-]+\s*|\s*[:#*=_~-]+$', '', line_clean).strip()
            candidate_lower = candidate.lower()
            words = candidate.split()

            is_section_header = False

            if 1 <= len(words) <= 5 and len(candidate) < 50:
                for section, variants in self.section_patterns.items():
                    for variant in variants:
                        if candidate_lower == variant or (
                            (candidate.isupper() or candidate.istitle()) and candidate_lower.startswith(variant)
                        ):
                            current_section = section
                            if current_section not in sections:
                                sections[current_section] = []
                            is_section_header = True
                            break
                    if is_section_header:
                        break

            if not is_section_header:
                sections[current_section].append(line_clean)

        return {k: '\n'.join(v) for k, v in sections.items() if v}

    def _get_section_text(self, sections: dict, keys: list[str]) -> str:
        """Helper to get text for a section."""
        for key in keys:
            if key in sections:
                return sections[key]
        return ""

    def parse_education(self, section_text: str) -> list[dict]:
        """Parse education section to extract degree, institution, graduation year, cgpa."""
        if not section_text:
            return []

        # Normalize special unicode dashes / replacement chars to standard hyphens
        cleaned_section = (
            section_text.replace('\ufffd', ' - ')
            .replace('\u2013', ' - ')
            .replace('\u2014', ' - ')
        )

        education_list = []
        lines = cleaned_section.split('\n')
        current_edu = {}

        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
            line_lower = line_clean.lower()

            # Degree
            if not current_edu.get('degree'):
                degree_match = re.search(
                    r'\b(b\.tech|b\.e\.|b\.sc|m\.tech|m\.sc|mba|phd|bachelor|master|diploma|associate)\b',
                    line_lower
                )
                if degree_match:
                    clean_degree = re.sub(r'\s*-\s*', ' - ', line_clean)
                    clean_degree = re.sub(r'\s+', ' ', clean_degree).strip()
                    current_edu['degree'] = clean_degree
                    continue

            # Graduation Year (if range like 2025 - 2029, pick the graduation end year 2029)
            year_range_match = re.search(r'(20[1-3][0-9])\s*[-–—]\s*(20[1-3][0-9])', line_clean)
            if year_range_match and not current_edu.get('graduation_year'):
                current_edu['graduation_year'] = year_range_match.group(2)
            else:
                year_match = re.search(r'\b(20[1-3][0-9])\b', line_clean)
                if year_match and not current_edu.get('graduation_year'):
                    current_edu['graduation_year'] = year_match.group(1)

            # CGPA / GPA / Percentage
            cgpa_match = re.search(r'(cgpa|gpa)[\s:]*([0-9]+\.?[0-9]*)|([0-9]+\.?[0-9]*)%', line_lower)
            if cgpa_match and not current_edu.get('cgpa'):
                current_edu['cgpa'] = cgpa_match.group(2) or cgpa_match.group(3)

            # Institution
            if not current_edu.get('institution'):
                inst_match = re.search(r'\b(institute|university|college|school|academy|polytechnic)\b', line_lower)
                if inst_match:
                    clean_inst = re.sub(r'\s+', ' ', line_clean).strip()
                    current_edu['institution'] = clean_inst

        if current_edu:
            education_list.append(current_edu)

        return education_list

    def extract_date_range(self, text: str) -> Optional[str]:
        """Extract a structured date range (e.g. 'June 2024 - August 2024', '2021 - 2023')."""
        if not text:
            return None
        match = self.DATE_RANGE_REGEX.search(text)
        return match.group(1).strip() if match else None

    def is_pure_date_line(self, line: str) -> bool:
        """Check if a line is exclusively a date range rather than a job role header."""
        d = self.extract_date_range(line)
        if not d:
            return False
        remainder = line.replace(d, '')
        remainder = re.sub(r'[\s\(\)\[\]\{\}\|,;:\-–—\u2010-\u2015*•▪+●▫‣⁃\uf0b7\ufffd]', '', remainder)
        return len(remainder) == 0

    def parse_experience(self, section_text: str) -> list[dict]:
        """
        Parse experience and internship sections.
        Correctly groups job headers, durations, and bulleted accomplishment descriptions.
        """
        if not section_text:
            return []

        experiences = []
        lines = section_text.split('\n')
        current_exp = None
        pending_date = None

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Check if this line is an accomplishment bullet
            is_bullet = bool(BULLET_REGEX.match(line_stripped))
            if is_bullet:
                desc_line = BULLET_REGEX.sub('', line_stripped).strip()
                if current_exp:
                    current_exp['description'] += (" " + desc_line if current_exp['description'] else desc_line)
                continue

            # Check if this line is purely a date duration line
            if self.is_pure_date_line(line_stripped):
                date_str = self.extract_date_range(line_stripped)
                if current_exp:
                    if not current_exp['duration']:
                        current_exp['duration'] = date_str
                else:
                    pending_date = date_str
                continue

            # Check if line contains a date range along with title/company
            date_str = self.extract_date_range(line_stripped)
            if date_str:
                role_text = line_stripped.replace(date_str, '').strip(" \t()[]{}|,-–—")
                duration = date_str
            else:
                role_text = line_stripped
                duration = pending_date or ""
                pending_date = None

            # Detect whether this line qualifies as a new role header
            is_separator_role = ('|' in role_text) or bool(re.search(r'\s+(?:at|@)\s+', role_text, re.IGNORECASE))
            has_title_keyword = bool(re.search(
                r'\b(?:intern|internship|engineer|developer|analyst|manager|lead|architect|consultant|specialist|scientist|administrator|associate|officer|director|vp|head|founder|co-founder|assistant)\b',
                role_text,
                re.IGNORECASE
            ))
            is_role_header = is_separator_role or has_title_keyword or (date_str is not None) or (current_exp is None)

            if is_role_header:
                if current_exp:
                    experiences.append(current_exp)

                if '|' in role_text:
                    parts = [p.strip() for p in role_text.split('|') if p.strip()]
                    title = parts[0]
                    company = parts[1] if len(parts) > 1 else ""
                elif re.search(r'\s+(?:at|@)\s+', role_text, re.IGNORECASE):
                    parts = re.split(r'\s+(?:at|@)\s+', role_text, maxsplit=1, flags=re.IGNORECASE)
                    title = parts[0].strip()
                    company = parts[1].strip() if len(parts) > 1 else ""
                elif ',' in role_text:
                    parts = [p.strip() for p in role_text.split(',', maxsplit=1) if p.strip()]
                    title = parts[0]
                    company = parts[1] if len(parts) > 1 else ""
                else:
                    title = role_text.strip()
                    company = ""

                current_exp = {
                    'title': title,
                    'company': company,
                    'duration': duration,
                    'description': ""
                }
            elif current_exp:
                clean_line = BULLET_REGEX.sub('', line_stripped).strip()
                current_exp['description'] += (" " + clean_line if current_exp['description'] else clean_line)

        if current_exp:
            experiences.append(current_exp)

        return experiences

    def _extract_technologies_from_line(self, line: str) -> list[str]:
        """Extract technology list from prefixed lines or bulleted skill lines."""
        # 1. Prefix pattern: e.g. "Technologies: Python, Flask", "Tech Stack: React, Node.js"
        prefix_match = self.TECH_PREFIX_REGEX.match(line)
        if prefix_match:
            raw = prefix_match.group(1)
            items = re.split(r'[,|/•▪*;]|\band\b', raw)
            res = []
            for it in items:
                clean_item = re.sub(r'^[\s\"\'\`\-•▪*–—+●▫‣⁃\uf0b7\ufffd]+|[\s\"\'\`.,;:–—]+$', '', it.strip())
                if not clean_item:
                    continue
                # Single letter languages C and R must be uppercase
                if clean_item.lower() in ('c', 'r') and clean_item not in ('C', 'R'):
                    continue
                canonical = self.CANONICAL_MAP.get(clean_item.lower(), clean_item)
                res.append(canonical)
            return res

        # 2. Bullet list pattern: e.g. "• Python, Pandas, NumPy", "- React.js, Node.js, MongoDB"
        clean = BULLET_REGEX.sub('', line).strip()
        items = [re.sub(r'^[\s\"\'\`\-•▪*–—+●▫‣⁃\uf0b7\ufffd]+|[\s\"\'\`.,;:–—]+$', '', it.strip())
                 for it in re.split(r'[,|/•▪*;]|\band\b', clean)]
        items = [it for it in items if it]
        matched = [
            self.CANONICAL_MAP.get(it.lower(), it)
            for it in items
            if it.lower() in self.CANONICAL_MAP and (it.lower() not in ('c', 'r') or it in ('C', 'R'))
        ]
        if len(items) >= 2 and len(matched) >= len(items) * 0.6:
            return matched

        return []

    def _add_technologies(self, proj: dict, new_techs: list[str]) -> None:
        """Add technologies to project while deduplicating case-insensitively and preserving order."""
        existing_lower = {t.lower() for t in proj['technologies']}
        for t in new_techs:
            t_clean = t.strip()
            if not t_clean:
                continue
            canonical = self.CANONICAL_MAP.get(t_clean.lower(), t_clean)
            if canonical.lower() in ('c', 'r') and t_clean not in ('C', 'R'):
                continue
            if canonical.lower() not in existing_lower:
                proj['technologies'].append(canonical)
                existing_lower.add(canonical.lower())

    def _enrich_project_tech_from_description(self, proj: dict) -> None:
        """Extract any technologies mentioned inside the project name or description text."""
        combined_text = f"{proj.get('name', '')} {proj.get('description', '')}".strip()
        if not combined_text:
            return

        desc_lower = combined_text.lower()
        found = []
        seen = {t.lower() for t in proj['technologies']}

        # Special bounded symbols
        if re.search(r'\bC\+\+\b', combined_text, re.IGNORECASE) or re.search(r'\bcpp\b', combined_text, re.IGNORECASE):
            if 'c++' not in seen:
                found.append('C++')
                seen.add('c++')

        if re.search(r'\bC\#\b', combined_text, re.IGNORECASE) or re.search(r'\bcsharp\b', combined_text, re.IGNORECASE):
            if 'c#' not in seen:
                found.append('C#')
                seen.add('c#')

        if re.search(r'(?:^|[\s,/|;(])C(?:$|[\s,/|;)])', combined_text):
            if 'c' not in seen:
                found.append('C')
                seen.add('c')

        if re.search(r'(?:^|[\s,/|;(])R(?:$|[\s,/|;)])', combined_text):
            if 'r' not in seen:
                found.append('R')
                seen.add('r')

        for t in self.SORTED_TECHS:
            if t in ('c', 'r', 'c++', 'c#'):
                continue
            pattern = r'\b' + re.escape(t) + r'\b'
            if re.search(pattern, desc_lower):
                canonical = self.CANONICAL_MAP[t]
                if canonical.lower() not in seen:
                    found.append(canonical)
                    seen.add(canonical.lower())

        self._add_technologies(proj, found)

    def parse_projects(self, section_text: str) -> list[dict]:
        """
        Parse projects section, accurately extracting both numbered and unnumbered project titles,
        descriptions, and technologies from explicit labels, bullets, or inline descriptions.
        """
        if not section_text:
            return []

        projects = []
        lines = section_text.split('\n')
        current_proj = None

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            is_bullet = bool(BULLET_REGEX.match(line_stripped))
            is_tech = bool(self.TECH_PREFIX_REGEX.match(line_stripped)) or bool(self._extract_technologies_from_line(line_stripped))
            is_numbered = bool(re.match(r'^\d+\.', line_stripped))
            is_prefixed = bool(re.match(r'^(?:Project\s*\d*|Title)\s*[:\-]\s*', line_stripped, re.IGNORECASE))
            is_pipe_header = ('|' in line_stripped) and not is_bullet and not is_tech

            # Standalone unnumbered header:
            # - Not a bullet line
            # - Not a technology prefix line
            # - Relatively concise (1-14 words, < 100 characters)
            # - Does not end with a period (avoiding normal narrative sentences)
            # - Either starting a new project or current project already has description/tech
            words = line_stripped.split()
            is_standalone_header = (
                not is_bullet and
                not is_tech and
                1 <= len(words) <= 14 and
                len(line_stripped) < 100 and
                not line_stripped.endswith('.') and
                (current_proj is None or len(current_proj['description']) > 0 or len(current_proj['technologies']) > 0)
            )

            is_project_header = (is_numbered or is_prefixed or is_pipe_header or is_standalone_header) and not is_tech

            if is_project_header:
                if current_proj:
                    self._enrich_project_tech_from_description(current_proj)
                    projects.append(current_proj)

                name = re.sub(r'^\d+\.\s*', '', line_stripped)
                name = re.sub(r'^(?:Project\s*\d*|Title)\s*[:\-]\s*', '', name, flags=re.IGNORECASE).strip()
                current_proj = {
                    'name': name,
                    'description': "",
                    'technologies': []
                }
            elif current_proj:
                if is_tech:
                    techs = self._extract_technologies_from_line(line_stripped)
                    if techs:
                        self._add_technologies(current_proj, techs)
                else:
                    clean_desc = BULLET_REGEX.sub('', line_stripped).strip()
                    if clean_desc:
                        current_proj['description'] += (" " + clean_desc if current_proj['description'] else clean_desc)

        if current_proj:
            self._enrich_project_tech_from_description(current_proj)
            projects.append(current_proj)

        return projects

    def extract_certifications(self, section_text: str) -> list[str]:
        """Extract list of certifications."""
        if not section_text:
            return []

        certs = []
        for line in section_text.split('\n'):
            line_clean = BULLET_REGEX.sub('', line.strip()).strip()
            if not line_clean or len(line_clean) <= 5:
                continue
            # Stop if another section header was included
            if line_clean.isupper() and len(line_clean.split()) <= 4:
                break
            certs.append(line_clean)

        return certs
