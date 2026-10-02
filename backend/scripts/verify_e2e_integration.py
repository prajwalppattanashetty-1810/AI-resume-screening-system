"""
End-to-end integration verification script for Phase 1-3.

Tests:
1. Backend health & root endpoints
2. Frontend server responsiveness
3. PDF resume upload via /api/resume/upload
4. PDF text extraction & validation
5. NLP preprocessing (cleaning, tokenization)
6. NLP Information Extraction via /api/resume/analyze
   - Candidate Name
   - Email & Phone
   - Education
   - Work Experience & Employment Dates
   - Projects & Project Technologies
   - Certifications & Skills
"""

import urllib.request
import urllib.parse
import json
import os
import mimetypes
import uuid

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"
SAMPLE_PDF = os.path.join(os.path.dirname(__file__), "..", "tests", "test_data", "sample_resume.pdf")


def log(step, msg, status="INFO"):
    symbol = "PASS" if status == "PASS" else ("FAIL" if status == "FAIL" else "INFO")
    print(f"[{symbol:4}] Step {step}: {msg}")


def test_backend_health():
    url = f"{BACKEND_URL}/health/"
    req = urllib.request.urlopen(url, timeout=5)
    data = json.loads(req.read().decode())
    assert req.status == 200 and data.get("status") == "ok", f"Health check failed: {data}"
    log(1, f"FastAPI Backend running at {BACKEND_URL} - Health check OK", "PASS")


def test_frontend_server():
    req = urllib.request.urlopen(FRONTEND_URL, timeout=5)
    content = req.read().decode()
    assert req.status == 200 and ("Vite" in content or "html" in content), "Frontend didn't return HTML"
    log(2, f"React Frontend running at {FRONTEND_URL} - Loads successfully", "PASS")


def upload_multipart(url, file_path, field_name="file"):
    boundary = uuid.uuid4().hex
    filename = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    lines = []
    lines.append(f"--{boundary}".encode("utf-8"))
    lines.append(f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"'.encode("utf-8"))
    lines.append(f"Content-Type: {mime_type}".encode("utf-8"))
    lines.append(b"")
    lines.append(file_bytes)
    lines.append(f"--{boundary}--".encode("utf-8"))
    lines.append(b"")

    body = b"\r\n".join(lines)
    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Content-Length", str(len(body)))

    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def test_upload():
    url = f"{BACKEND_URL}/api/resume/upload"
    result = upload_multipart(url, SAMPLE_PDF)
    assert "file_id" in result, f"Upload response missing file_id: {result}"
    log(3, f"Resume Upload API accepted PDF -> file_id={result['file_id']}", "PASS")
    return result["file_id"]


def test_analyze(file_id):
    url = f"{BACKEND_URL}/api/resume/analyze"
    payload = json.dumps({"file_id": file_id}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())

    # 4. Verify PDF Text Extraction
    assert "extracted_text" in data and len(data["extracted_text"]) > 100
    log(4, f"PDF Text Extraction verified: {data['text_length']} characters extracted", "PASS")

    # 5. Verify NLP Preprocessing
    assert "cleaned_text" in data and "tokens" in data and data["token_count"] > 0
    log(5, f"NLP Preprocessing verified: {data['token_count']} normalized tokens created", "PASS")

    # 6. Verify NLP Parser Information Extraction
    profile = data.get("profile", {})

    # Name, Email, Phone
    assert profile.get("name") and "RAHUL" in profile["name"].upper(), f"Name mismatch: {profile.get('name')}"
    assert profile.get("email") == "rahul.sharma@email.com", f"Email mismatch: {profile.get('email')}"
    assert profile.get("phone") and "9876543210" in profile["phone"], f"Phone mismatch: {profile.get('phone')}"
    log(6, f"Contact details extracted: Name='{profile['name']}', Email='{profile['email']}', Phone='{profile['phone']}'", "PASS")

    # Education
    edu = profile.get("education", [])
    assert len(edu) >= 1 and "Bachelor of Technology" in edu[0].get("degree", "")
    log(7, f"Education extracted: {len(edu)} degree(s) found -> '{edu[0].get('degree')}' at '{edu[0].get('institution')}'", "PASS")

    # Experience & Employment Dates
    exp = profile.get("experience", [])
    assert len(exp) == 2, f"Expected 2 experiences, got {len(exp)}"
    assert exp[0].get("duration") == "June 2024 - August 2024"
    assert exp[1].get("duration") == "January 2024 - March 2024"
    log(8, f"Work Experience & Dates extracted: {len(exp)} roles found with valid durations ({exp[0]['duration']}, {exp[1]['duration']})", "PASS")

    # Projects & Project Technologies
    proj = profile.get("projects", [])
    assert len(proj) == 3, f"Expected 3 projects in sample_resume.pdf, got {len(proj)}"
    assert "Python" in proj[0].get("technologies", [])
    assert "React" in proj[1].get("technologies", [])
    assert "Pandas" in proj[2].get("technologies", [])
    log(9, f"Projects & Technologies extracted: {len(proj)} projects found with tech stacks (Proj 1: {proj[0]['technologies']}, Proj 2: {proj[1]['technologies']}, Proj 3: {proj[2]['technologies']})", "PASS")

    # Certifications & Skills
    certs = profile.get("certifications", [])
    assert len(certs) == 3, f"Expected 3 certifications, got {len(certs)}"
    log(10, f"Certifications & Skills extracted: {len(certs)} certifications found ({certs[0]})", "PASS")

    # 7. Phase 4: Verify Skills Analysis in /api/resume/analyze
    assert "skills_analysis" in data, "Response missing skills_analysis"
    s_analysis = data["skills_analysis"]
    assert s_analysis["total_skills"] > 0, f"Expected skills, got {s_analysis['total_skills']}"
    log(11, f"Skills Analysis present in analyze response: {s_analysis['total_skills']} skills detected", "PASS")

    return data, file_id


def test_extract_skills_api(file_id):
    url = f"{BACKEND_URL}/api/resume/extract-skills"
    payload = json.dumps({"file_id": file_id}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())

    assert "total_skills" in data and data["total_skills"] >= 10, f"Expected >= 10 skills, got {data.get('total_skills')}"
    assert "categorized_skills" in data, "Missing categorized_skills"
    cats = data["categorized_skills"]

    # Verify key domains
    assert len(cats.get("programming_languages", [])) > 0, "Missing programming_languages"
    assert len(cats.get("machine_learning", [])) > 0, "Missing machine_learning"
    assert len(cats.get("databases", [])) > 0, "Missing databases"
    log(12, f"Skill Categories verified: {len(cats)} categories present (Prog: {cats['programming_languages']}, ML: {cats['machine_learning']})", "PASS")

    # Verify proficiency levels and evidence
    skills_list = data.get("skills", [])
    has_advanced = any(s["proficiency"] == "Advanced" for s in skills_list)
    has_intermediate = any(s["proficiency"] == "Intermediate" for s in skills_list)
    has_beginner = any(s["proficiency"] == "Beginner" for s in skills_list)
    assert has_advanced, "No Advanced skills found from work experience"
    assert has_intermediate, "No Intermediate skills found from projects"

    python_skill = next((s for s in skills_list if s["name"] == "Python"), None)
    assert python_skill is not None, "Python not found in extracted skills"
    assert python_skill["proficiency"] == "Advanced", f"Python should be Advanced, got {python_skill['proficiency']}"
    assert len(python_skill["evidence"]) > 0, "Python missing evidence snippet"

    log(13, f"Skill Proficiency & Evidence verified: Python='{python_skill['proficiency']}' with {len(python_skill['evidence'])} evidence snippet(s)", "PASS")
    return data


def test_jobs_api():
    # 14. GET /api/jobs
    url = f"{BACKEND_URL}/api/jobs?page=1&limit=10"
    req = urllib.request.urlopen(url, timeout=10)
    data = json.loads(req.read().decode())
    assert req.status == 200, "GET /api/jobs failed"
    assert data["total"] >= 200, f"Expected >= 200 jobs, got {data['total']}"
    assert len(data["jobs"]) == 10, f"Expected 10 jobs per page, got {len(data['jobs'])}"
    first_job = data["jobs"][0]
    log(14, f"Jobs List API verified: total={data['total']}, page=1, limit=10, first='{first_job['title']}' ({first_job['company']})", "PASS")

    # 15. GET /api/jobs/categories
    cat_url = f"{BACKEND_URL}/api/jobs/categories"
    req = urllib.request.urlopen(cat_url, timeout=10)
    cats = json.loads(req.read().decode())
    assert len(cats) >= 14, f"Expected >= 14 job categories, got {len(cats)}"
    log(15, f"Job Categories API verified: {len(cats)} categories present (e.g. {cats[0]['category']}: {cats[0]['count']} jobs)", "PASS")

    # 16. GET /api/jobs/search & filters
    search_url = f"{BACKEND_URL}/api/jobs/search?q=Machine+Learning&limit=5"
    req = urllib.request.urlopen(search_url, timeout=10)
    search_data = json.loads(req.read().decode())
    assert isinstance(search_data, list) and len(search_data) > 0, "Search for 'Machine Learning' returned 0 jobs"
    log(16, f"Job Search API verified: query='Machine Learning' returned {len(search_data)} matches (e.g. '{search_data[0]['title']}')", "PASS")

    # 17. GET /api/jobs/{job_id}
    job_id = first_job["id"]
    job_code = first_job["job_id"]
    detail_url = f"{BACKEND_URL}/api/jobs/{job_code}"
    req = urllib.request.urlopen(detail_url, timeout=10)
    detail_data = json.loads(req.read().decode())
    assert detail_data["job_id"] == job_code, f"Expected job_id {job_code}, got {detail_data.get('job_id')}"
    assert "responsibilities" in detail_data and len(detail_data["responsibilities"]) > 0, "Responsibilities missing in detail"
    assert "date_posted" in detail_data and detail_data["date_posted"], "Date posted missing in detail"
    log(17, f"Job Detail API verified: fetched '{detail_data['title']}' with {len(detail_data['responsibilities'])} responsibilities, posted {detail_data['date_posted']}", "PASS")

    # 18. GET /api/jobs/stats
    stats_url = f"{BACKEND_URL}/api/jobs/stats"
    req = urllib.request.urlopen(stats_url, timeout=10)
    stats_data = json.loads(req.read().decode())
    assert stats_data["total_jobs"] >= 200, f"Expected >= 200 jobs in stats, got {stats_data['total_jobs']}"
    assert stats_data["total_categories"] >= 15, f"Expected >= 15 categories, got {stats_data['total_categories']}"
    log(18, f"Job Stats API verified: total={stats_data['total_jobs']}, categories={stats_data['total_categories']}, remote={stats_data['work_modes'].get('Remote', 0)}", "PASS")

    # 19. POST /api/jobs/seed
    seed_url = f"{BACKEND_URL}/api/jobs/seed"
    req = urllib.request.Request(seed_url, data=b"", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        seed_data = json.loads(resp.read().decode())
    assert "Job dataset successfully synchronized" in seed_data["message"]
    assert seed_data["total_in_db"] >= 200
    log(19, f"Job Seed API verified: safe re-sync returned {seed_data['total_in_db']} jobs in DB ({seed_data['inserted']} inserted, {seed_data['updated']} updated)", "PASS")


def test_recommendation_api(file_id):
    # 20. POST /api/jobs/recommend
    url = f"{BACKEND_URL}/api/jobs/recommend"
    payload = json.dumps({
        "file_id": file_id,
        "top_n": 5,
        "tfidf_weight": 0.7,
        "skill_weight": 0.3
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())

    assert "recommendations" in data and len(data["recommendations"]) == 5, f"Expected 5 recommendations, got {len(data.get('recommendations', []))}"
    assert data["total_jobs_analyzed"] >= 200, "Expected >= 200 analyzed jobs"
    assert len(data.get("candidate_skills_used", [])) > 0, "No candidate skills listed"

    top = data["recommendations"][0]
    assert "job_id" in top and "title" in top and "match_score" in top
    assert top["match_score"] > 0, "Match score should be > 0"
    assert "tfidf_similarity" in top and "skill_match_percentage" in top
    assert len(top.get("matched_skills", [])) > 0, "Expected some matched skills"
    assert "explanation" in top and len(top["explanation"]) > 10, "Missing explanation"

    # Verify descending score order
    scores = [r["match_score"] for r in data["recommendations"]]
    assert scores == sorted(scores, reverse=True), "Recommendations not sorted descending"

    log(20, f"Recommendation API verified: Top Match = '{top['title']}' at '{top['company']}' with {top['match_score']}% match (TF-IDF: {top['tfidf_similarity']:.2f}, Skills: {top['skill_match_percentage']}%)", "PASS")

    # 21. POST /api/jobs/recommend with Category Filter
    filtered_payload = json.dumps({
        "file_id": file_id,
        "category": "Machine Learning Engineer",
        "top_n": 3
    }).encode("utf-8")
    req = urllib.request.Request(url, data=filtered_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        filt_data = json.loads(resp.read().decode())

    assert len(filt_data["recommendations"]) > 0
    for r in filt_data["recommendations"]:
        assert r["category"] == "Machine Learning Engineer"

    log(21, f"Filtered Recommendations verified: returned {len(filt_data['recommendations'])} ML Engineer positions exclusively", "PASS")
    return top["job_id"]


def test_skill_gap_api(file_id: str, job_id: str):
    # 22. POST /api/skill-gap/analyze
    url = f"{BACKEND_URL}/api/skill-gap/analyze"
    payload = json.dumps({
        "file_id": file_id,
        "job_id": job_id
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())

    assert data["job_id"] == job_id, f"Expected job_id={job_id}, got {data.get('job_id')}"
    assert "metrics" in data, "Missing metrics in response"
    metrics = data["metrics"]
    assert "required_match_percentage" in metrics
    assert "overall_coverage_percentage" in metrics
    assert "learning_recommendations" in data
    assert isinstance(data["learning_recommendations"], list)
    assert len(data["learning_recommendations"]) > 0

    first_rec = data["learning_recommendations"][0]
    assert "skill_name" in first_rec and "priority" in first_rec and "learning_topics" in first_rec
    assert "project_ideas" in first_rec and "estimated_duration" in first_rec

    log(22, f"Skill Gap API verified: Job='{data['job_title']}' ({data['job_id']}), Overall Coverage={metrics['overall_coverage_percentage']}%, Matched={metrics['matched_required']}, Partial={metrics['partial_required']}, Missing={metrics['missing_required']}, Roadmap={len(data['learning_recommendations'])} skills", "PASS")

    # 23. GET /api/skill-gap/analyze/{file_id}/{job_id}
    get_url = f"{BACKEND_URL}/api/skill-gap/analyze/{file_id}/{job_id}"
    req_get = urllib.request.Request(get_url)
    with urllib.request.urlopen(req_get, timeout=15) as resp:
        get_data = json.loads(resp.read().decode())
    assert get_data["job_id"] == job_id
    assert get_data["metrics"]["overall_coverage_percentage"] == metrics["overall_coverage_percentage"]

    log(23, f"Skill Gap GET endpoint verified for browser deep-linking: /api/skill-gap/analyze/{file_id[:8]}.../{job_id}", "PASS")


if __name__ == "__main__":
    print("==================================================")
    print("PHASE 1-7 END-TO-END INTEGRATION VERIFICATION")
    print("==================================================")
    try:
        test_backend_health()
        test_frontend_server()
        fid = test_upload()
        _, file_id = test_analyze(fid)
        test_extract_skills_api(file_id)
        test_jobs_api()
        top_job_id = test_recommendation_api(file_id)
        test_skill_gap_api(file_id, top_job_id)
        print("==================================================")
        print("ALL 23 VERIFICATION CHECKS PASSED SUCCESSFULLY! [OK]")
        print("==================================================")
    except Exception as e:
        print(f"\n[FAIL] Verification failed: {e}")
        import traceback
        traceback.print_exc()



