"""
Tests for the PDF extraction service.

Tests cover:
- Text extraction from valid PDFs
- Handling of empty/scanned PDFs
- Multi-page extraction
- PDF validation
- Error handling for invalid files
- Text cleaning
"""

import os
import pytest
from app.services.pdf_service import PDFService

# Path to test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")

pdf_service = PDFService()


# ============================================================
# PDF Validation Tests
# ============================================================

class TestPDFValidation:
    """Tests for PDF validation."""

    def test_validate_valid_resume(self):
        """Valid resume PDF should pass validation."""
        path = os.path.join(TEST_DATA_DIR, "sample_resume.pdf")
        result = pdf_service.validate_pdf(path)
        assert result["is_valid"] is True
        assert result["error"] is None
        assert result["page_count"] >= 1
        assert result["has_text"] is True

    def test_validate_empty_pdf(self):
        """PDF with no text should fail validation."""
        path = os.path.join(TEST_DATA_DIR, "empty_resume.pdf")
        result = pdf_service.validate_pdf(path)
        assert result["is_valid"] is False
        assert result["has_text"] is False
        assert "scanned" in result["error"].lower() or "image" in result["error"].lower()

    def test_validate_nonexistent_file(self):
        """Non-existent file should fail validation."""
        result = pdf_service.validate_pdf("nonexistent_file.pdf")
        assert result["is_valid"] is False
        assert "not found" in result["error"].lower()

    def test_validate_multipage_resume(self):
        """Multi-page resume should pass validation."""
        path = os.path.join(TEST_DATA_DIR, "multipage_resume.pdf")
        result = pdf_service.validate_pdf(path)
        assert result["is_valid"] is True
        assert result["page_count"] == 2

    def test_validate_non_pdf_file(self, tmp_path):
        """Non-PDF file should fail validation."""
        fake_file = tmp_path / "resume.txt"
        fake_file.write_text("This is not a PDF")
        result = pdf_service.validate_pdf(str(fake_file))
        assert result["is_valid"] is False


# ============================================================
# Text Extraction Tests
# ============================================================

class TestTextExtraction:
    """Tests for PDF text extraction."""

    def test_extract_text_from_valid_resume(self):
        """Should extract meaningful text from a valid resume."""
        path = os.path.join(TEST_DATA_DIR, "sample_resume.pdf")
        text = pdf_service.extract_text(path)

        assert isinstance(text, str)
        assert len(text) > 100  # Should have substantial content

        # Verify key resume sections are extracted
        assert "RAHUL SHARMA" in text
        assert "rahul.sharma@email.com" in text
        assert "+91-9876543210" in text
        assert "Python" in text
        assert "EDUCATION" in text
        assert "TECHNICAL SKILLS" in text
        assert "PROJECTS" in text

    def test_extract_text_contains_skills(self):
        """Extracted text should contain technical skills."""
        path = os.path.join(TEST_DATA_DIR, "sample_resume.pdf")
        text = pdf_service.extract_text(path)

        skills_to_find = ["Python", "Java", "React", "Pandas", "NumPy", "Docker"]
        for skill in skills_to_find:
            assert skill in text, f"Skill '{skill}' not found in extracted text"

    def test_extract_text_contains_experience(self):
        """Extracted text should contain work experience details."""
        path = os.path.join(TEST_DATA_DIR, "sample_resume.pdf")
        text = pdf_service.extract_text(path)

        assert "Google" in text or "Intern" in text
        assert "WORK EXPERIENCE" in text

    def test_extract_text_from_empty_pdf_raises(self):
        """Should raise ValueError for empty/scanned PDF."""
        path = os.path.join(TEST_DATA_DIR, "empty_resume.pdf")
        with pytest.raises(ValueError, match="No text"):
            pdf_service.extract_text(path)

    def test_extract_text_nonexistent_file_raises(self):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            pdf_service.extract_text("nonexistent.pdf")

    def test_extract_text_multipage(self):
        """Should extract text from all pages."""
        path = os.path.join(TEST_DATA_DIR, "multipage_resume.pdf")
        text = pdf_service.extract_text(path)

        # Content from page 1
        assert "ANANYA PATEL" in text
        assert "EDUCATION" in text

        # Content from page 2
        assert "PROJECTS" in text or "WORK EXPERIENCE" in text

    def test_extract_text_by_page(self):
        """Should return text separated by page."""
        path = os.path.join(TEST_DATA_DIR, "multipage_resume.pdf")
        pages = pdf_service.extract_text_by_page(path)

        assert len(pages) == 2
        assert pages[0]["page_number"] == 1
        assert pages[1]["page_number"] == 2
        assert pages[0]["char_count"] > 0
        assert pages[1]["char_count"] > 0


# ============================================================
# Metadata Tests
# ============================================================

class TestPDFMetadata:
    """Tests for PDF metadata extraction."""

    def test_get_metadata(self):
        """Should return metadata dict with expected keys."""
        path = os.path.join(TEST_DATA_DIR, "sample_resume.pdf")
        metadata = pdf_service.get_metadata(path)

        assert "page_count" in metadata
        assert "file_size_kb" in metadata
        assert metadata["page_count"] >= 1
        assert metadata["file_size_kb"] > 0

    def test_metadata_nonexistent_file_raises(self):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            pdf_service.get_metadata("nonexistent.pdf")


# ============================================================
# Text Cleaning Tests
# ============================================================

class TestTextCleaning:
    """Tests for the internal text cleaning method."""

    def test_clean_multiple_spaces(self):
        """Should collapse multiple spaces into one."""
        result = pdf_service._clean_extracted_text("hello    world")
        assert result == "hello world"

    def test_clean_excessive_newlines(self):
        """Should collapse excessive empty lines."""
        result = pdf_service._clean_extracted_text("line1\n\n\n\n\nline2")
        # Should have at most 1 empty line between
        assert "\n\n\n" not in result
        assert "line1" in result
        assert "line2" in result

    def test_clean_ligatures(self):
        """Should replace ligature characters."""
        result = pdf_service._clean_extracted_text("of\ufb01ce")
        assert result == "office"

    def test_clean_empty_input(self):
        """Should handle empty string."""
        assert pdf_service._clean_extracted_text("") == ""

    def test_clean_preserves_content(self):
        """Should not remove meaningful content."""
        text = "Python, Java, C++\nEmail: test@email.com\nPhone: +91-9876543210"
        result = pdf_service._clean_extracted_text(text)
        assert "Python" in result
        assert "test@email.com" in result
        assert "+91-9876543210" in result
