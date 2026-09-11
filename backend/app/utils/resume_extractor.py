"""
SkillBridge AI — Resume Text Extraction Utility

Handles text extraction from PDF, DOCX, and TXT resume files.
"""
from __future__ import annotations

import logging
import os

# Optional imports - handle missing dependencies gracefully
try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None

try:
    import docx
except ImportError:  # pragma: no cover
    docx = None

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file using pdfplumber."""
    if pdfplumber is None:
        raise ImportError("pdfplumber is not installed. Install it to process PDF resumes.")

    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file using python-docx."""
    if docx is None:
        raise ImportError("python-docx is not installed. Install it to process DOCX resumes.")

    document = docx.Document(file_path)
    text = ""
    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"
    return text


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from a plain text file."""
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_resume_text(file_path: str, mime_type: str | None = None) -> str:
    """
    Extract text from a resume file based on its MIME type or file extension.
    Args:
        file_path: Path to the resume file.
        mime_type: MIME type of the file (optional). If not provided, inferred from extension.
    Returns:
        Extracted text as a string.
    Raises:
        ValueError: If the file type is not supported.
        ImportError: If required dependencies are missing.
    """
    # Determine file type from mime_type or extension
    file_type = None
    if mime_type:
        if mime_type == "application/pdf":
            file_type = "pdf"
        elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            file_type = "docx"
        elif mime_type == "text/plain":
            file_type = "txt"

    # Fallback to file extension
    if not file_type:
        _, ext = os.path.splitext(file_path.lower())
        if ext == ".pdf":
            file_type = "pdf"
        elif ext == ".docx":
            file_type = "docx"
        elif ext == ".txt":
            file_type = "txt"
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    # Extract text based on file type
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_type == "docx":
        return extract_text_from_docx(file_path)
    elif file_type == "txt":
        return extract_text_from_txt(file_path)
    else:  # pragma: no cover
        raise ValueError(f"Unsupported file type: {file_type}")
