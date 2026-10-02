"""
Phase 9: Comprehensive System Verification and Production Readiness Test Runner.
Executes automated end-to-end assertions against the running FastAPI service,
validating code quality, ML inference, API endpoints, security, and performance.
"""

import sys
import os
import json
import time
import urllib.request
import urllib.error

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"


def http_get(url):
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return resp.status, json.loads(content.decode("utf-8")), resp.headers
            return resp.status, content.decode("utf-8", errors="replace"), resp.headers
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(err_body), e.headers
        except Exception:
            return e.code, err_body, e.headers
    except Exception as e:
        return 0, str(e), {}


def http_post_json(url, payload):
    req = urllib.request.Request(url, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    data = json.dumps(payload).encode("utf-8")
    req.data = data
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, json.loads(content)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"error": err_body}
    except Exception as e:
        return 0, {"error": str(e)}


def http_post_multipart(url, filename, file_bytes, content_type="application/pdf"):
    boundary = "----WebKitFormBoundary" + str(int(time.time() * 1000))
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode(
            "utf-8"
        )
    )
    body.extend(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
    body.extend(file_bytes)
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, json.loads(content)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"error": err_body}
    except Exception as e:
        return 0, {"error": str(e)}


def run_phase9_tests():
    print("=" * 70)
    print("PHASE 9: COMPREHENSIVE TESTING, OPTIMIZATION & DEPLOYMENT READINESS")
    print("=" * 70)

    results = []

    # -------------------------------------------------------------
    # Test 1: Service Liveness & Documentation Endpoints
    # -------------------------------------------------------------
    try:
        status, health, _ = http_get(f"{BACKEND_URL}/health")
        assert status == 200 and health.get("status") == "ok", f"Health status: {health}"

        status_root, root, _ = http_get(f"{BACKEND_URL}/")
        assert status_root == 200 and root.get("docs") == "/docs", f"Root: {root}"

        status_openapi, openapi, _ = http_get(f"{BACKEND_URL}/openapi.json")
        assert status_openapi == 200, "OpenAPI failed"
        paths_count = len(openapi.get("paths", {}))
        assert paths_count >= 20, f"Expected >= 20 API routes, found {paths_count}"

        status_docs, _, _ = http_get(f"{BACKEND_URL}/docs")
        assert status_docs == 200, "Swagger /docs failed"

        status_redoc, redoc_html, _ = http_get(f"{BACKEND_URL}/redoc")
        assert status_redoc == 200 and "Redoc.init" in redoc_html, "ReDoc failed"

        results.append(("1. Service Liveness & Documentation (Health, OpenAPI, Docs, ReDoc)", True, f"{paths_count} routes registered"))
        print("[PASS] 1. Service Liveness & Documentation OK")
    except Exception as e:
        results.append(("1. Service Liveness & Documentation", False, str(e)))
        print(f"[FAIL] 1. Service Liveness & Documentation: {e}")

    # -------------------------------------------------------------
    # Test 2: Upload Validation & Security Handling
    # -------------------------------------------------------------
    try:
        # Rejection of invalid file extension
        status_txt, _ = http_post_multipart(
            f"{BACKEND_URL}/api/resume/upload",
            "fake_resume.txt",
            b"Hello I am a text resume",
            content_type="text/plain",
        )
        assert status_txt == 400, f"Expected 400 for .txt file, got {status_txt}"

        # Rejection of fake binary
        status_exe, _ = http_post_multipart(
            f"{BACKEND_URL}/api/resume/upload",
            "malicious.exe",
            b"MZ\x90\x00\x03\x00\x00\x00",
            content_type="application/octet-stream",
        )
        assert status_exe == 400, f"Expected 400 for .exe file, got {status_exe}"

        results.append(("2. Upload File Validation & Type Restrictions", True, "Successfully rejected .txt and .exe"))
        print("[PASS] 2. Upload File Validation OK")
    except Exception as e:
        results.append(("2. Upload File Validation", False, str(e)))
        print(f"[FAIL] 2. Upload File Validation: {e}")

    # -------------------------------------------------------------
    # Test 3: Resume PDF Upload & Deep NLP Parsing
    # -------------------------------------------------------------
    uploaded_file_id = None
    analysis_data = {}
    try:
        sample_pdf_path = os.path.join(
            os.path.dirname(__file__), "..", "tests", "test_data", "sample_resume.pdf"
        )
        assert os.path.exists(sample_pdf_path), "sample_resume.pdf missing"
        with open(sample_pdf_path, "rb") as f:
            pdf_bytes = f.read()

        status_upload, upload_data = http_post_multipart(
            f"{BACKEND_URL}/api/resume/upload", "prajwal_ai_resume.pdf", pdf_bytes
        )
        assert status_upload == 200, f"Upload error: {upload_data}"
        uploaded_file_id = upload_data.get("file_id")
        assert uploaded_file_id, "Missing file_id"

        # Trigger analysis
        status_analyze, analysis_data = http_post_json(
            f"{BACKEND_URL}/api/resume/analyze", {"file_id": uploaded_file_id}
        )
        assert status_analyze == 200, f"Analysis error: {analysis_data}"
        profile = analysis_data.get("profile", {})
        assert profile.get("name"), "Name was not extracted"
        assert profile.get("email"), "Email was not extracted"
        assert len(profile.get("education", [])) > 0, "Education empty"

        skills_analysis = analysis_data.get("skills_analysis", {})
        extracted_skills = skills_analysis.get("skills", [])
        tech_skills_count = len(extracted_skills)
        assert tech_skills_count >= 5, f"Expected >= 5 extracted skills, got {tech_skills_count}"

        results.append(("3. Resume PDF Parsing & NLP Information Extraction", True, f"Extracted {tech_skills_count} skills, name: {profile.get('name')}"))
        print(f"[PASS] 3. Resume PDF Upload & NLP Extraction OK ({tech_skills_count} skills)")
    except Exception as e:
        results.append(("3. Resume PDF Parsing & NLP Extraction", False, str(e)))
        print(f"[FAIL] 3. Resume PDF Parsing: {e}")

    # -------------------------------------------------------------
    # Test 4: Multi-Dimensional Scoring Engine
    # -------------------------------------------------------------
    try:
        scores = analysis_data.get("scores", {})
        overall = scores.get("overall", 0)
        skills_score = scores.get("skills", 0)
        projects_score = scores.get("projects", 0)
        experience_score = scores.get("experience", 0)
        education_score = scores.get("education", 0)
        completeness = scores.get("completeness", 0)

        for s in [overall, skills_score, projects_score, experience_score, education_score, completeness]:
            assert 0 <= s <= 100, f"Score out of bounds (0-100): {s}"

        suggestions = analysis_data.get("improvement_suggestions", [])
        assert len(suggestions) > 0, "No improvement suggestions generated"

        results.append(("4. Multi-Dimensional Scoring Engine", True, f"Overall: {overall}/100, {len(suggestions)} suggestions"))
        print(f"[PASS] 4. Multi-Dimensional Scoring OK (Score: {overall}/100)")
    except Exception as e:
        results.append(("4. Multi-Dimensional Scoring Engine", False, str(e)))
        print(f"[FAIL] 4. Multi-Dimensional Scoring: {e}")

    # -------------------------------------------------------------
    # Test 5: Job Dataset, Search & Filtering
    # -------------------------------------------------------------
    try:
        status_jobs, jobs_resp, _ = http_get(f"{BACKEND_URL}/api/jobs?limit=5")
        assert status_jobs == 200, f"Job list error: {jobs_resp}"
        total_jobs = jobs_resp.get("total", 0)
        assert total_jobs >= 250, f"Expected >= 250 jobs, found {total_jobs}"

        status_cats, cats_resp, _ = http_get(f"{BACKEND_URL}/api/jobs/categories")
        assert status_cats == 200 and isinstance(cats_resp, list) and len(cats_resp) >= 10, "Categories error"

        status_stats, stats_resp, _ = http_get(f"{BACKEND_URL}/api/jobs/stats")
        assert status_stats == 200 and stats_resp.get("total_jobs") == total_jobs, "Stats error"

        # Search query check
        status_search, search_resp, _ = http_get(f"{BACKEND_URL}/api/jobs?search=Machine+Learning&limit=5")
        assert status_search == 200 and len(search_resp.get("jobs", [])) > 0, "Job search failed"

        results.append(("5. Job Dataset, Explorer & Search API", True, f"{total_jobs} jobs across {len(cats_resp)} categories"))
        print(f"[PASS] 5. Job Dataset & Search OK ({total_jobs} jobs)")
    except Exception as e:
        results.append(("5. Job Dataset & Search", False, str(e)))
        print(f"[FAIL] 5. Job Dataset & Search: {e}")

    # -------------------------------------------------------------
    # Test 6: ML Recommendation Engine (TF-IDF + Cosine Similarity) & Latency
    # -------------------------------------------------------------
    target_job_id = None
    try:
        resume_text = (
            "Experienced Machine Learning Engineer with expertise in Python, PyTorch, "
            "Scikit-learn, TensorFlow, Natural Language Processing, and SQL. "
            "Built NLP recommender systems and deep learning models for classification."
        )
        skills_list = ["Python", "Machine Learning", "NLP", "Scikit-Learn", "SQL", "PyTorch"]

        latencies = []
        rec_data = None
        for _ in range(5):
            t0 = time.perf_counter()
            status_rec, rec_data = http_post_json(
                f"{BACKEND_URL}/api/jobs/recommend",
                {"resume_text": resume_text, "skills": skills_list, "top_n": 5},
            )
            latencies.append((time.perf_counter() - t0) * 1000)

        assert status_rec == 200, f"Recommendation error: {rec_data}"
        recs = rec_data.get("recommendations", [])
        assert len(recs) == 5, f"Expected 5 recommendations, got {len(recs)}"

        avg_latency = sum(latencies) / len(latencies)
        top_rec = recs[0]
        assert top_rec.get("match_score", 0) > 0, "Top recommendation match score is 0"
        assert "skill_match" in top_rec, "Missing skill_match details"
        assert len(top_rec.get("skill_match", {}).get("matched", [])) > 0, "No matched skills"

        target_job_id = top_rec["job"]["job_id"]

        results.append(("6. TF-IDF + Cosine Similarity Recommendation Engine", True, f"Top match: {top_rec['job']['title']} ({top_rec['match_score']}%), Latency: {avg_latency:.1f}ms"))
        print(f"[PASS] 6. ML Recommendation Engine OK (Mean Latency: {avg_latency:.1f}ms)")
    except Exception as e:
        results.append(("6. ML Recommendation Engine", False, str(e)))
        print(f"[FAIL] 6. ML Recommendation Engine: {e}")

    # -------------------------------------------------------------
    # Test 7: Skill Gap Analysis & Learning Roadmap
    # -------------------------------------------------------------
    try:
        assert uploaded_file_id and target_job_id, "Missing resume file_id or job_id"
        gap_url = f"{BACKEND_URL}/api/skill-gap/analyze/{uploaded_file_id}/{target_job_id}"
        status_gap, gap_data, _ = http_get(gap_url)
        assert status_gap == 200, f"Skill gap error: {gap_data}"

        metrics = gap_data.get("metrics", {})
        overall_match = metrics.get("overall_coverage_percentage", metrics.get("overall_match_percentage", 0))
        assert "overall_coverage_percentage" in metrics or "overall_match_percentage" in metrics, "Missing coverage percentage"
        assert "matched_skills" in gap_data, "Missing matched_skills"
        assert "missing_skills" in gap_data, "Missing missing_skills"
        assert "learning_recommendations" in gap_data, "Missing learning_recommendations"

        roadmap = gap_data.get("learning_recommendations", [])

        results.append(("7. Skill Gap Analysis & Personalized Learning Roadmap", True, f"Skill match: {overall_match}%, {len(roadmap)} recommendations"))
        print(f"[PASS] 7. Skill Gap & Learning Roadmap OK ({overall_match}% coverage)")
    except Exception as e:
        results.append(("7. Skill Gap & Learning Roadmap", False, str(e)))
        print(f"[FAIL] 7. Skill Gap Analysis: {e}")

    # -------------------------------------------------------------
    # Test 8: Error Handling & Security Boundary Tests
    # -------------------------------------------------------------
    try:
        # Invalid resume ID for skill gap
        status_bad_resume, _, _ = http_get(f"{BACKEND_URL}/api/skill-gap/analyze/invalid-non-existent-uuid/{target_job_id}")
        assert status_bad_resume == 404, f"Expected 404 for invalid resume ID, got {status_bad_resume}"

        # Invalid job ID for skill gap
        status_bad_job, _, _ = http_get(f"{BACKEND_URL}/api/skill-gap/analyze/{uploaded_file_id}/INVALID-JOB-99999")
        assert status_bad_job == 404, f"Expected 404 for invalid job ID, got {status_bad_job}"

        # Invalid resume ID for analyze
        status_bad_analyze, _ = http_post_json(f"{BACKEND_URL}/api/resume/analyze", {"file_id": "non-existent-file-id"})
        assert status_bad_analyze == 404, f"Expected 404 for analyze on missing file, got {status_bad_analyze}"

        results.append(("8. Error Handling & Exception Management (404/400)", True, "Verified 404 on invalid file IDs and job IDs"))
        print("[PASS] 8. Error Handling & Boundary Tests OK")
    except Exception as e:
        results.append(("8. Error Handling & Boundary Tests", False, str(e)))
        print(f"[FAIL] 8. Error Handling: {e}")

    # -------------------------------------------------------------
    # Test 9: Dashboard Aggregation & Resume History
    # -------------------------------------------------------------
    try:
        status_dash, dash_stats, _ = http_get(f"{BACKEND_URL}/api/resume/dashboard-stats")
        assert status_dash == 200, f"Dashboard stats error: {dash_stats}"
        assert dash_stats.get("total_resumes", 0) > 0, "No resumes in dashboard stats"

        status_hist, hist_data, _ = http_get(f"{BACKEND_URL}/api/resume/history?limit=10")
        assert status_hist == 200 and len(hist_data.get("resumes", [])) > 0, "History error"

        status_imp, imp_data, _ = http_get(f"{BACKEND_URL}/api/resume/improvements/{uploaded_file_id}")
        assert status_imp == 200 and "suggestions" in imp_data, "Improvements endpoint error"

        results.append(("9. Dashboard Aggregation & Resume History APIs", True, f"{dash_stats['total_resumes']} total resumes processed in system"))
        print(f"[PASS] 9. Dashboard Aggregation OK ({dash_stats['total_resumes']} resumes tracked)")
    except Exception as e:
        results.append(("9. Dashboard Aggregation", False, str(e)))
        print(f"[FAIL] 9. Dashboard Aggregation: {e}")

    # -------------------------------------------------------------
    # Test 10: Git Hygiene & Sensitive Data Protection
    # -------------------------------------------------------------
    try:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        gitignore_path = os.path.join(repo_root, ".gitignore")
        assert os.path.exists(gitignore_path), ".gitignore missing"
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gi_content = f.read()

        assert "*.db" in gi_content, "*.db rule missing in .gitignore"
        assert ".env" in gi_content, ".env rule missing in .gitignore"
        assert "backend/uploads/*" in gi_content, "backend/uploads/* missing in .gitignore"
        assert "!backend/uploads/.gitkeep" in gi_content, "!backend/uploads/.gitkeep missing"

        results.append(("10. Git Hygiene & Sensitive Data Protection", True, ".gitignore rules verified"))
        print("[PASS] 10. Git Hygiene & Security OK")
    except Exception as e:
        results.append(("10. Git Hygiene & Security", False, str(e)))
        print(f"[FAIL] 10. Git Hygiene: {e}")

    # -------------------------------------------------------------
    # Test 11: Frontend Production Asset Verification
    # -------------------------------------------------------------
    try:
        frontend_dist_index = os.path.join(
            os.path.dirname(__file__), "..", "..", "frontend", "dist", "index.html"
        )
        assert os.path.exists(frontend_dist_index), "frontend/dist/index.html missing — run 'npm run build'"

        # Verify frontend live dev server is also responsive
        status_front, _, _ = http_get(FRONTEND_URL)
        assert status_front == 200, f"Frontend dev server returned {status_front}"

        results.append(("11. Frontend Production Build & Live Server", True, "dist/index.html verified, dev server 200 OK"))
        print("[PASS] 11. Frontend Production Assets & Dev Server OK")
    except Exception as e:
        results.append(("11. Frontend Production Build", False, str(e)))
        print(f"[FAIL] 11. Frontend Production Build: {e}")

    # -------------------------------------------------------------
    # Summary Report
    # -------------------------------------------------------------
    print("=" * 70)
    print("PHASE 9 VERIFICATION SUMMARY")
    print("=" * 70)
    passed_count = sum(1 for _, ok, _ in results if ok)
    total_count = len(results)

    for name, ok, detail in results:
        status_tag = "[PASS]" if ok else "[FAIL]"
        print(f"{status_tag} {name} - {detail}")

    print("-" * 70)
    print(f"Total Passed: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")
    print("=" * 70)

    return passed_count == total_count


if __name__ == "__main__":
    success = run_phase9_tests()
    sys.exit(0 if success else 1)
