"""
Deep Verification Script for Phase 7: Skill Gap Analysis & Learning Recommendations.

Validates:
1. Valid/invalid resume and job ID handling
2. Matched, partial, missing skill accuracy
3. Math verification for coverage formulas
4. Learning recommendations priority & structure
5. End-to-end integration and data integrity
"""

import sys
import json
import urllib.request
import urllib.error

BACKEND_URL = "http://127.0.0.1:8000"


def request_json(url, method="GET", data=None):
    headers = {"Content-Type": "application/json"}
    payload = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return e.code, parsed


def run_deep_verification():
    print("==================================================")
    print("PHASE 7 DEEP VERIFICATION: SKILL GAP & LEARNING")
    print("==================================================")

    # 1. Fetch any valid resume and job from database via existing APIs
    status, jobs_data = request_json(f"{BACKEND_URL}/api/jobs?limit=5")
    assert status == 200, f"Jobs API failed: {status}"
    assert len(jobs_data["jobs"]) > 0, "No jobs in DB"
    test_job = jobs_data["jobs"][0]
    valid_job_id = test_job["job_id"]
    valid_job_numeric_id = test_job["id"]
    print(f"[OK] Fetched valid Job: '{test_job['title']}' (job_id='{valid_job_id}', id={valid_job_numeric_id})")

    import os
    import mimetypes
    import uuid

    sample_pdf_path = os.path.join(os.path.dirname(__file__), "..", "tests", "test_data", "sample_resume.pdf")
    boundary = uuid.uuid4().hex
    filename = os.path.basename(sample_pdf_path)
    mime_type = mimetypes.guess_type(sample_pdf_path)[0] or "application/pdf"

    with open(sample_pdf_path, "rb") as f:
        file_bytes = f.read()

    lines = []
    lines.append(f"--{boundary}".encode("utf-8"))
    lines.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode("utf-8"))
    lines.append(f"Content-Type: {mime_type}".encode("utf-8"))
    lines.append(b"")
    lines.append(file_bytes)
    lines.append(f"--{boundary}--".encode("utf-8"))
    lines.append(b"")
    body = b"\r\n".join(lines)

    up_req = urllib.request.Request(f"{BACKEND_URL}/api/resume/upload", data=body)
    up_req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    up_req.add_header("Content-Length", str(len(body)))
    with urllib.request.urlopen(up_req, timeout=10) as up_resp:
        up_data = json.loads(up_resp.read().decode())
    valid_file_id = up_data["file_id"]
    print(f"[OK] Uploaded test resume -> file_id='{valid_file_id}'")

    # Analyze resume
    status, ana_data = request_json(f"{BACKEND_URL}/api/resume/analyze", method="POST", data={"file_id": valid_file_id})
    assert status == 200, f"Analyze resume failed: {status}"
    cand_name = ana_data.get("profile", {}).get("name", "RAHUL SHARMA")
    print(f"[OK] Analyzed resume -> Candidate: '{cand_name}', extracted text length: {len(ana_data['extracted_text'])}")

    # 3. Test Valid Resume ID + Valid Job ID (String code e.g. JOB-MAC-0001)
    status, gap_res = request_json(
        f"{BACKEND_URL}/api/skill-gap/analyze",
        method="POST",
        data={"file_id": valid_file_id, "job_id": valid_job_id}
    )
    assert status == 200, f"Valid POST /api/skill-gap/analyze failed: {status}, {gap_res}"
    assert gap_res["job_id"] == valid_job_id
    assert gap_res["candidate_name"] == cand_name
    print(f"[OK] Valid Combination (String code): {valid_job_id} + {valid_file_id} -> HTTP 200 OK")

    # 4. Test Valid Resume ID + Valid Job ID (Numeric ID e.g. '1')
    status, gap_num = request_json(
        f"{BACKEND_URL}/api/skill-gap/analyze",
        method="POST",
        data={"file_id": valid_file_id, "job_id": str(valid_job_numeric_id)}
    )
    assert status == 200, f"Valid POST with numeric job ID failed: {status}"
    assert gap_num["job_numeric_id"] == valid_job_numeric_id
    print(f"[OK] Valid Combination (Numeric ID): id={valid_job_numeric_id} -> HTTP 200 OK")

    # 5. Test Invalid Resume ID + Valid Job ID -> HTTP 404
    status, err_resp = request_json(
        f"{BACKEND_URL}/api/skill-gap/analyze",
        method="POST",
        data={"file_id": "invalid-uuid-00000000-0000", "job_id": valid_job_id}
    )
    assert status == 404, f"Expected 404 for invalid file_id, got {status}"
    assert "not found" in err_resp.get("detail", "").lower()
    print(f"[OK] Invalid Resume ID test -> HTTP 404 Not Found ('{err_resp.get('detail')}')")

    # 6. Test Valid Resume ID + Invalid Job ID -> HTTP 404
    status, err_resp = request_json(
        f"{BACKEND_URL}/api/skill-gap/analyze",
        method="POST",
        data={"file_id": valid_file_id, "job_id": "NON-EXISTENT-JOB-9999"}
    )
    assert status == 404, f"Expected 404 for invalid job_id, got {status}"
    assert "not found" in err_resp.get("detail", "").lower()
    print(f"[OK] Invalid Job ID test -> HTTP 404 Not Found ('{err_resp.get('detail')}')")

    # 7. Test Missing Identifiers -> HTTP 400
    status, err_resp = request_json(
        f"{BACKEND_URL}/api/skill-gap/analyze",
        method="POST",
        data={"job_id": valid_job_id}
    )
    assert status == 400, f"Expected 400 for missing candidate identifiers, got {status}"
    print(f"[OK] Missing Candidate Identifiers test -> HTTP 400 Bad Request ('{err_resp.get('detail')}')")

    # 8. Test Mathematical Coverage Formulas on Response
    metrics = gap_res["metrics"]
    tot_req = metrics["total_required"]
    m_req = metrics["matched_required"]
    p_req = metrics["partial_required"]
    tot_pref = metrics["total_preferred"]
    m_pref = metrics["matched_preferred"]
    p_pref = metrics["partial_preferred"]

    expected_req_pct = round(((m_req + 0.5 * p_req) / tot_req) * 100.0, 1) if tot_req > 0 else 100.0
    expected_pref_pct = round(((m_pref + 0.5 * p_pref) / tot_pref) * 100.0, 1) if tot_pref > 0 else 100.0
    if tot_pref > 0 and tot_req > 0:
        expected_overall_pct = round((0.75 * expected_req_pct) + (0.25 * expected_pref_pct), 1)
    else:
        expected_overall_pct = expected_req_pct

    assert metrics["required_match_percentage"] == expected_req_pct, f"Req % mismatch: {metrics['required_match_percentage']} != {expected_req_pct}"
    assert metrics["preferred_coverage_percentage"] == expected_pref_pct, f"Pref % mismatch: {metrics['preferred_coverage_percentage']} != {expected_pref_pct}"
    assert metrics["overall_coverage_percentage"] == expected_overall_pct, f"Overall % mismatch: {metrics['overall_coverage_percentage']} != {expected_overall_pct}"
    print(f"[OK] Coverage Formula Verification:")
    print(f"     Required Match: ({m_req} + 0.5*{p_req})/{tot_req}*100 = {metrics['required_match_percentage']}%")
    print(f"     Preferred Coverage: ({m_pref} + 0.5*{p_pref})/{tot_pref}*100 = {metrics['preferred_coverage_percentage']}%")
    print(f"     Overall Fit: 0.75*{expected_req_pct} + 0.25*{expected_pref_pct} = {metrics['overall_coverage_percentage']}%")

    # 9. Verify Matched, Partial, Missing Items Breakdown
    req_analysis = gap_res["required_skills_analysis"]
    for item in req_analysis:
        assert item["status"] in ["matched", "partial", "missing"], f"Invalid status {item['status']}"
        assert item["requirement_type"] == "required"
        assert len(item["name"]) > 0
        assert len(item["reason"]) > 0

    pref_analysis = gap_res["preferred_skills_analysis"]
    for item in pref_analysis:
        assert item["status"] in ["matched", "partial", "missing"]
        assert item["requirement_type"] == "preferred"

    print(f"[OK] Skill Item Integrity: {len(req_analysis)} required and {len(pref_analysis)} preferred items inspected and valid")

    # 10. Verify Learning Recommendations Priority & Verified URLs
    recs = gap_res["learning_recommendations"]
    print(f"[OK] Learning Recommendations Generated: {len(recs)} total")
    priorities = [r["priority"] for r in recs]
    # Check priorities are ordered High -> Medium -> Low
    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    num_priorities = [priority_order.get(p, 99) for p in priorities]
    assert num_priorities == sorted(num_priorities), "Recommendations not sorted by priority"

    for r in recs:
        assert len(r["learning_topics"]) >= 2, f"Too few topics for {r['skill_name']}"
        assert len(r["project_ideas"]) >= 1, f"No project idea for {r['skill_name']}"
        assert len(r["estimated_duration"]) > 0
        for res in r["resources"]:
            if res["url"] is not None:
                assert res["url"].startswith("http://") or res["url"].startswith("https://"), f"Invalid resource URL: {res['url']}"

    print(f"[OK] Priority Sorting and URL Verification passed for all {len(recs)} roadmap items")

    # 11. GET deep-linking endpoint test
    status, get_res = request_json(f"{BACKEND_URL}/api/skill-gap/analyze/{valid_file_id}/{valid_job_id}")
    assert status == 200
    assert get_res["metrics"] == metrics
    print(f"[OK] GET /api/skill-gap/analyze/{valid_file_id[:8]}.../{valid_job_id} deep-link verified")

    # 12. Frontend Vite Proxy Connectivity Test (http://127.0.0.1:5173/api/skill-gap/analyze)
    vite_status, vite_res = request_json(
        "http://127.0.0.1:5173/api/skill-gap/analyze",
        method="POST",
        data={"file_id": valid_file_id, "job_id": valid_job_id}
    )
    assert vite_status == 200, f"Vite proxy request failed: {vite_status}"
    assert vite_res["candidate_name"] == cand_name
    assert vite_res["job_id"] == valid_job_id
    print(f"[OK] Frontend Vite Proxy -> FastAPI connectivity verified: HTTP 200 (Candidate: '{cand_name}')")

    print("==================================================")
    print("ALL DEEP VERIFICATION CHECKS PASSED SUCCESSFULLY! [OK]")
    print("==================================================")


if __name__ == "__main__":
    run_deep_verification()
