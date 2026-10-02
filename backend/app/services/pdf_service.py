"""
PDF Service — Extracts and validates text from PDF resumes using PyMuPDF.

WHY PyMuPDF (fitz)?
- Fastest Python PDF parser (C-based bindings)
- Handles most PDF formats including those with complex layouts
- Returns text with layout preservation, which helps with section detection
- No external system dependencies (unlike poppler-based tools)
"""

import fitz  # PyMuPDF
import os
import re
from typing import Optional


class PDFService:
    """Handles PDF file validation and text extraction."""

    # Minimum characters expected from a valid resume
    MIN_TEXT_LENGTH = 50

    def validate_pdf(self, file_path: str) -> dict:
        """
        Validate that a file is a readable PDF with extractable text.

        Returns a dict with:
            - is_valid (bool): Whether the PDF is usable
            - error (str | None): Error message if invalid
            - page_count (int): Number of pages
            - has_text (bool): Whether text could be extracted
        """
        result = {
            "is_valid": False,
            "error": None,
            "page_count": 0,
            "has_text": False,
        }

        # Check file exists
        if not os.path.exists(file_path):
            result["error"] = "File not found"
            return result

        # Check file extension
        if not file_path.lower().endswith(".pdf"):
            result["error"] = "File is not a PDF"
            return result

        # Check file is not empty
        if os.path.getsize(file_path) == 0:
            result["error"] = "PDF file is empty"
            return result

        try:
            doc = fitz.open(file_path)
        except Exception:
            result["error"] = "File is corrupted or not a valid PDF"
            return result

        try:
            result["page_count"] = len(doc)

            if len(doc) == 0:
                result["error"] = "PDF has no pages"
                return result

            # Try extracting text from all pages
            full_text = ""
            for page in doc:
                full_text += page.get_text()

            text_stripped = full_text.strip()
            result["has_text"] = len(text_stripped) >= self.MIN_TEXT_LENGTH

            if not result["has_text"]:
                result["error"] = (
                    "PDF appears to be scanned or image-based. "
                    "Please upload a text-based PDF for best results."
                )
                return result

            result["is_valid"] = True
            return result

        finally:
            doc.close()

    def extract_text(self, file_path: str) -> str:
        """
        Extract all text from a PDF file.

        Uses PyMuPDF's text extraction which preserves basic layout.
        This is important because resume sections (Education, Experience, Skills)
        are often identified by their position and formatting.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text as a single string

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If PDF is invalid or has no extractable text
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            doc = fitz.open(file_path)
        except Exception as e:
            raise ValueError(f"Cannot open PDF: {str(e)}")

        try:
            pages_text = []

            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                if page_text.strip():
                    pages_text.append(page_text)

            if not pages_text:
                raise ValueError(
                    "No text could be extracted from this PDF. "
                    "It may be a scanned document or image-based PDF."
                )

            raw_text = "\n".join(pages_text)
            cleaned_text = self._clean_extracted_text(raw_text)
            return cleaned_text

        finally:
            doc.close()

    def extract_text_by_page(self, file_path: str) -> list[dict]:
        """
        Extract text from each page separately.

        Useful for multi-page resumes where we might want to know
        which page contains which sections.

        Returns:
            List of dicts with 'page_number' and 'text' keys
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            doc = fitz.open(file_path)
        except Exception as e:
            raise ValueError(f"Cannot open PDF: {str(e)}")

        try:
            pages = []
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                pages.append({
                    "page_number": page_num + 1,
                    "text": self._clean_extracted_text(page_text),
                    "char_count": len(page_text.strip()),
                })
            return pages
        finally:
            doc.close()

    def get_metadata(self, file_path: str) -> dict:
        """Extract PDF metadata (author, title, creation date, etc.)."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            doc = fitz.open(file_path)
        except Exception as e:
            raise ValueError(f"Cannot open PDF: {str(e)}")

        try:
            metadata = doc.metadata or {}
            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "page_count": len(doc),
                "file_size_kb": round(os.path.getsize(file_path) / 1024, 1),
            }
        finally:
            doc.close()

    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean raw text extracted from PDF.

        PDFs often have artifacts like:
        - Multiple consecutive spaces/tabs
        - Excessive newlines
        - Unicode control characters
        - Ligature characters (ﬁ, ﬂ, etc.)

        This method normalizes the text while preserving meaningful structure.
        """
        if not text:
            return ""

        # Replace common ligatures with standard characters
        ligature_map = {
            "\ufb01": "fi",
            "\ufb02": "fl",
            "\ufb03": "ffi",
            "\ufb04": "ffl",
        }
        for ligature, replacement in ligature_map.items():
            text = text.replace(ligature, replacement)

        # Remove null bytes and other control characters (keep newlines, tabs)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        # Normalize whitespace within lines (collapse multiple spaces/tabs)
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
            cleaned_lines.append(cleaned_line)

        # Collapse more than 2 consecutive empty lines into 1
        result_lines = []
        empty_count = 0
        for line in cleaned_lines:
            if line == "":
                empty_count += 1
                if empty_count <= 1:
                    result_lines.append(line)
            else:
                empty_count = 0
                result_lines.append(line)

        return "\n".join(result_lines).strip()
