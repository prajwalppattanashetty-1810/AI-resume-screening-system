"""
Script to create sample test PDF files for testing the PDF extraction service.

Creates:
1. A realistic sample resume PDF
2. An empty PDF (no text)
3. A multi-page resume PDF
"""

import fitz  # PyMuPDF
import os


def create_sample_resume(output_path: str):
    """Create a realistic sample resume PDF for testing."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 size

    # Resume content
    resume_text = """RAHUL SHARMA
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
   - Reduced customer response time by 40%

2. E-Commerce Analytics Dashboard
   - Developed a real-time analytics dashboard
   - Technologies: React, Node.js, MongoDB, Chart.js
   - Processed 100K+ transactions for insights
   - Implemented user segmentation using K-means clustering

3. Stock Price Prediction System
   - Built LSTM-based stock prediction model
   - Technologies: Python, Pandas, TensorFlow, Matplotlib
   - Achieved RMSE of 2.3% on test data

WORK EXPERIENCE

Software Engineering Intern | Google India
June 2024 - August 2024
- Developed microservices for search optimization
- Improved API response time by 25%
- Collaborated with a team of 8 engineers

Data Science Intern | Flipkart
January 2024 - March 2024
- Analyzed customer purchase patterns using Python and SQL
- Built recommendation models using collaborative filtering
- Created automated reporting dashboards with Tableau

CERTIFICATIONS

- AWS Certified Cloud Practitioner
- Google Data Analytics Professional Certificate
- Deep Learning Specialization - Coursera

SOFT SKILLS

Communication, Team Leadership, Problem Solving, Critical Thinking, Adaptability
"""

    # Write text to PDF page
    text_rect = fitz.Rect(50, 40, 545, 800)
    page.insert_textbox(
        text_rect,
        resume_text,
        fontsize=9,
        fontname="helv",
        align=fitz.TEXT_ALIGN_LEFT,
    )

    doc.save(output_path)
    doc.close()
    print(f"Created: {output_path}")


def create_empty_pdf(output_path: str):
    """Create a PDF with a page but no text (simulates scanned/image PDF)."""
    doc = fitz.open()
    doc.new_page(width=595, height=842)
    doc.save(output_path)
    doc.close()
    print(f"Created: {output_path}")


def create_multipage_resume(output_path: str):
    """Create a multi-page resume PDF."""
    doc = fitz.open()

    # Page 1
    page1 = doc.new_page(width=595, height=842)
    page1_text = """ANANYA PATEL
Email: ananya.patel@email.com | Phone: +91-9123456789

EDUCATION
Master of Science in Data Science
Indian Institute of Science, Bangalore
Graduation Year: 2025 | CGPA: 9.1/10

Bachelor of Engineering in Computer Science
BITS Pilani
Graduation Year: 2023 | CGPA: 8.9/10

TECHNICAL SKILLS
Programming: Python, R, SQL, Java, Scala
ML/AI: Scikit-learn, TensorFlow, PyTorch, XGBoost
Data: Pandas, NumPy, Spark, Hadoop
Visualization: Matplotlib, Seaborn, Tableau, Power BI
Cloud: AWS, Azure, GCP
Databases: PostgreSQL, MongoDB, Cassandra, Redis
"""
    page1.insert_textbox(
        fitz.Rect(50, 40, 545, 800),
        page1_text, fontsize=10, fontname="helv",
    )

    # Page 2
    page2 = doc.new_page(width=595, height=842)
    page2_text = """PROJECTS

1. Real-time Fraud Detection System
   Built an ML pipeline for detecting fraudulent transactions
   Technologies: Python, Spark, XGBoost, Kafka
   Achieved 96.5% accuracy with 0.2% false positive rate

2. Natural Language Processing for Legal Documents
   Developed NER and text classification for legal texts
   Technologies: Python, spaCy, BERT, FastAPI
   Processed 50K+ legal documents with 92% accuracy

WORK EXPERIENCE

Machine Learning Engineer Intern | Microsoft
May 2024 - August 2024
- Built NLP models for document understanding
- Deployed models using Azure ML and Docker
- Published internal research paper on transfer learning

Data Analyst Intern | Amazon
December 2023 - February 2024
- Analyzed supply chain data for optimization
- Reduced delivery delays by 15% through predictive modeling
- Built automated SQL pipelines for daily reporting

CERTIFICATIONS
- TensorFlow Developer Certificate
- AWS Machine Learning Specialty
- Stanford Machine Learning (Coursera)
"""
    page2.insert_textbox(
        fitz.Rect(50, 40, 545, 800),
        page2_text, fontsize=10, fontname="helv",
    )

    doc.save(output_path)
    doc.close()
    print(f"Created: {output_path}")


if __name__ == "__main__":
    test_dir = os.path.join(os.path.dirname(__file__), "..", "tests", "test_data")
    os.makedirs(test_dir, exist_ok=True)

    create_sample_resume(os.path.join(test_dir, "sample_resume.pdf"))
    create_empty_pdf(os.path.join(test_dir, "empty_resume.pdf"))
    create_multipage_resume(os.path.join(test_dir, "multipage_resume.pdf"))

    print("\nAll test PDFs created successfully!")
