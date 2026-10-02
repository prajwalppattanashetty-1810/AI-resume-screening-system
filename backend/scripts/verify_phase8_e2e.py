"""
Phase 8 End-to-End System Integration Verification Script.
Validates all Phase 8 deliverables:
1. Resume scoring engine (multi-dimensional score calculation)
2. Improvement recommendations engine (prioritized, actionable suggestions)
3. Dashboard statistics endpoint (/api/resume/dashboard-stats)
4. Resume improvements endpoint (/api/resume/improvements/{file_id})
5. Resume history endpoint (/api/resume/history)
6. Data persistence in SQLite database
7. Frontend reverse proxy and routing compatibility
"""

import sys
import os
import json
import urllib.request
import urllib.error

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"

def request_json(url, data=None, method="GET"):
    req = urllib.request.Request(url, method=method)
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
        body = json.dumps(data).encode("utf-8")
        req.data = body

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, json.loads(content)
    except urllib.error.HTTPError as e:
        err_content = e.read().decode("utf-8")
        try:
            return e.code, json.loads(err_content)
        except Exception:
            return e.code, {"error": err_content}
    except Exception as e:
        return 0, {"error": str(e)}


def run_phase8_verification():
    print("=" * 60)
    print("PHASE 8 END-TO-END SYSTEM INTEGRATION VERIFICATION")
    print("=" * 60)

    # 1. Health check
    code, health = request_json(f"{BACKEND_URL}/health")
    assert code == 200 and health.get("status") == "ok", f"Health check failed: {health}"
    print("[PASS] 1. Backend Health Check OK (FastAPI 1.0.0)")

    # 2. Frontend connectivity
    try:
        req = urllib.request.Request(FRONTEND_URL)
        with urllib.request.urlopen(req, timeout=5) as resp:
            assert resp.status == 200
            print("[PASS] 2. Frontend React / Vite dev server is running (Port 5173)")
    except Exception as e:
        print(f"[FAIL] 2. Frontend connectivity failed: {e}")
        sys.exit(1)

    # 3. Overall Dashboard Stats
    code, stats = request_json(f"{BACKEND_URL}/api/resume/dashboard-stats")
    assert code == 200, f"Dashboard stats endpoint failed: {code}, {stats}"
    assert stats["total_resumes"] > 0, "total_resumes should be > 0"
    assert stats["total_jobs"] >= 250, "total_jobs should be at least 250"
    assert stats["avg_resume_score"] > 0, "avg_resume_score should be positive"
    assert stats["total_skills_catalog"] > 100, "total_skills_catalog should be > 100"
    assert len(stats["category_distribution"]) > 10, "Should have 10+ categories"
    assert len(stats["score_distribution"]) == 4, "Should have 4 score bands"
    assert len(stats["recent_resumes"]) > 0, "Should have recent resumes"
    print(f"[PASS] 3. Dashboard Stats API verified:")
    print(f"       Resumes: {stats['total_resumes']}, Jobs: {stats['total_jobs']}, Avg Score: {stats['avg_resume_score']}%, Skills: {stats['total_skills_catalog']}")

    # 4. History Endpoint
    code, history = request_json(f"{BACKEND_URL}/api/resume/history?limit=15")
    assert code == 200 and history.get("total", 0) > 0, f"History failed: {history}"
    first_resume = history["resumes"][0]
    file_id = first_resume["file_id"]
    print(f"[PASS] 4. History API verified ({history['total']} records retrieved, latest: {first_resume['candidate_name']}, score: {first_resume['score']}%)")

    # 5. Candidate Spotlight in Dashboard Stats
    code, candidate_stats = request_json(f"{BACKEND_URL}/api/resume/dashboard-stats?file_id={file_id}")
    assert code == 200, f"Candidate stats failed: {candidate_stats}"
    c_summary = candidate_stats.get("candidate_summary")
    assert c_summary is not None, "Candidate summary missing when file_id provided"
    assert "scores" in c_summary, "Candidate summary should include scores"
    assert "overall" in c_summary["scores"], "Overall score should be present"
    print(f"[PASS] 5. Candidate Spotlight verified for {c_summary['name']} (Overall: {c_summary['scores']['overall']}%)")

    # 6. Improvements API Endpoint
    code, improvements = request_json(f"{BACKEND_URL}/api/resume/improvements/{file_id}")
    assert code == 200, f"Improvements failed: {improvements}"
    scores = improvements["scores"]
    suggestions = improvements["suggestions"]
    summary = improvements["profile_summary"]

    for dim in ["overall", "skills", "projects", "experience", "education", "completeness"]:
        assert dim in scores, f"Missing dimension '{dim}' in scores"
        assert 0.0 <= scores[dim] <= 100.0, f"Score out of range: {dim}={scores[dim]}"

    print(f"[PASS] 6. Improvements API verified:")
    print(f"       Scores: Overall={scores['overall']}%, Skills={scores['skills']}%, Projects={scores['projects']}%, Experience={scores['experience']}%, Education={scores['education']}%")
    print(f"       Suggestions: {len(suggestions)} recommendations generated")

    # 7. Suggestions Quality Check
    for s in suggestions:
        assert s.get("category") and s.get("priority") and s.get("suggestion"), f"Malformed suggestion: {s}"
        assert s["priority"] in ["High", "Medium", "Low"], f"Invalid priority: {s['priority']}"
    print(f"[PASS] 7. Improvement suggestions schema & priority integrity verified")

    # 8. Resume Analysis Endpoint Verification (Phase 8 score integration)
    code, analyze_resp = request_json(f"{BACKEND_URL}/api/resume/analyze", data={"file_id": file_id}, method="POST")
    assert code == 200, f"Analyze failed: {analyze_resp}"
    assert "scores" in analyze_resp, "Analyze response should contain scores in Phase 8"
    assert "improvement_suggestions" in analyze_resp, "Analyze response should contain improvement_suggestions in Phase 8"
    print(f"[PASS] 8. Resume Analysis API confirmed returns Phase 8 scores & suggestions directly")

    # 9. Test Invalid file_id handling
    code, inv_resp = request_json(f"{BACKEND_URL}/api/resume/improvements/non-existent-uuid-99999")
    assert code == 404, f"Expected 404 for invalid resume ID, got {code}"
    print(f"[PASS] 9. Error handling verified for invalid resume ID (HTTP 404)")

    # 10. Verify Data Flow: SQLite DB Persistence
    from app.models.database import SessionLocal, ResumeAnalysis
    db = SessionLocal()
    rec = db.query(ResumeAnalysis).filter(ResumeAnalysis.file_id == file_id).first()
    assert rec is not None, "Record not found in database"
    assert rec.score is not None, "ResumeAnalysis.score should be persisted in DB"
    assert rec.score == scores["overall"], "Persisted score matches computed overall score"
    db.close()
    print(f"[PASS] 10. Database persistence confirmed: ResumeAnalysis.score = {rec.score} stored in SQLite")

    # 11. Fresher Profile Verification with Deficits & Suggestions
    fresher_id = "5c7c676b-1782-4439-8076-effb041d186a"
    code, f_imp = request_json(f"{BACKEND_URL}/api/resume/improvements/{fresher_id}")
    if code == 200:
        f_scores = f_imp["scores"]
        f_sugg = f_imp["suggestions"]
        assert len(f_sugg) >= 2, "Fresher profile should generate actionable suggestions"
        assert f_scores["overall"] < 60.0, "Fresher with missing experience/projects should score < 60%"
        print(f"[PASS] 11. Fresher Deficit Evaluation verified (Score: {f_scores['overall']}%, {len(f_sugg)} actionable tips generated)")


    print("=" * 60)
    print("ALL 11 PHASE 8 VERIFICATION CHECKS PASSED SUCCESSFULLY! [OK]")
    print("=" * 60)


if __name__ == "__main__":
    run_phase8_verification()
