"""
API endpoint tests for resume upload and analysis.

Tests the full HTTP request/response cycle through FastAPI's TestClient.
"""

import os

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")


# ============================================================
# Root & Health Endpoints
# ============================================================

def test_root_endpoint(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["message"] == "API is running"

def test_health_endpoint(test_client):
    response = test_client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ============================================================
# Resume Upload Endpoint
# ============================================================

def test_upload_no_file(test_client):
    """Should return 422 when no file is provided."""
    response = test_client.post("/api/resume/upload")
    assert response.status_code == 422

def test_upload_invalid_file_type(test_client):
    """Should reject non-PDF files."""
    files = {"file": ("test.txt", b"Hello world", "text/plain")}
    response = test_client.post("/api/resume/upload", files=files)
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]

def test_upload_empty_file(test_client):
    """Should reject empty files."""
    files = {"file": ("empty.pdf", b"", "application/pdf")}
    response = test_client.post("/api/resume/upload", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

def test_upload_valid_resume(test_client):
    """Should accept a valid PDF resume and return file_id."""
    pdf_path = os.path.join(TEST_DATA_DIR, "sample_resume.pdf")
    with open(pdf_path, "rb") as f:
        files = {"file": ("sample_resume.pdf", f, "application/pdf")}
        response = test_client.post("/api/resume/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert "filename" in data
    assert data["filename"] == "sample_resume.pdf"
    assert len(data["file_id"]) > 0

def test_upload_empty_pdf_rejected(test_client):
    """Should reject a PDF that has no extractable text."""
    pdf_path = os.path.join(TEST_DATA_DIR, "empty_resume.pdf")
    with open(pdf_path, "rb") as f:
        files = {"file": ("empty_resume.pdf", f, "application/pdf")}
        response = test_client.post("/api/resume/upload", files=files)

    assert response.status_code == 400
    assert "scanned" in response.json()["detail"].lower() or "image" in response.json()["detail"].lower()


# ============================================================
# Resume Analysis Endpoint
# ============================================================

def test_analyze_nonexistent_resume(test_client):
    """Should return 404 for non-existent file_id."""
    response = test_client.post(
        "/api/resume/analyze",
        json={"file_id": "nonexistent-id-12345"}
    )
    assert response.status_code == 404

def test_analyze_uploaded_resume(test_client):
    """Should successfully analyze an uploaded resume."""
    # First upload
    pdf_path = os.path.join(TEST_DATA_DIR, "sample_resume.pdf")
    with open(pdf_path, "rb") as f:
        files = {"file": ("sample_resume.pdf", f, "application/pdf")}
        upload_response = test_client.post("/api/resume/upload", files=files)

    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]

    # Then analyze
    analyze_response = test_client.post(
        "/api/resume/analyze",
        json={"file_id": file_id}
    )

    assert analyze_response.status_code == 200
    data = analyze_response.json()
    assert data["file_id"] == file_id
    assert "extracted_text" in data
    assert len(data["extracted_text"]) > 100
    assert "RAHUL SHARMA" in data["extracted_text"]
    assert data["text_length"] > 0


# ============================================================
# Resume Status Endpoint
# ============================================================

def test_status_nonexistent(test_client):
    """Should return 404 for non-existent file."""
    response = test_client.get("/api/resume/status/nonexistent-id")
    assert response.status_code == 404

def test_status_uploaded_file(test_client):
    """Should return metadata for uploaded file."""
    # Upload first
    pdf_path = os.path.join(TEST_DATA_DIR, "sample_resume.pdf")
    with open(pdf_path, "rb") as f:
        files = {"file": ("sample_resume.pdf", f, "application/pdf")}
        upload_response = test_client.post("/api/resume/upload", files=files)

    file_id = upload_response.json()["file_id"]

    # Check status
    response = test_client.get(f"/api/resume/status/{file_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] is True
    assert "metadata" in data
    assert data["metadata"]["page_count"] >= 1
