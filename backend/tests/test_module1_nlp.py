"""
SkillBridge AI — Module 1 NLP and Skill Extraction Unit Tests

Tests for resume text extraction, NLP processing, skill normalization, and skill extraction.
"""
from __future__ import annotations

import os
import tempfile
from unittest.mock import Mock, patch

from app.nlp.nlp_engine import NlpEngine
from app.skill_extraction.skill_extractor import SkillExtractor
from app.skill_extraction.skill_normalizer import SkillNormalizer
from app.utils.resume_extractor import (
    extract_resume_text,
    extract_text_from_docx,
    extract_text_from_pdf,
    extract_text_from_txt,
)

# Sample text for testing
SAMPLE_TXT = """
Experienced software engineer with expertise in Python, Java, and SQL.
Proficient in React and Docker. Familiar with Git and REST APIs.
"""

SAMPLE_EXPECTED_SKILLS = [
    {"skill": "Python", "confidence": 1.0},
    {"skill": "Java", "confidence": 1.0},
    {"skill": "SQL", "confidence": 1.0},
    {"skill": "React", "confidence": 1.0},
    {"skill": "Docker", "confidence": 1.0},
    {"skill": "Git", "confidence": 1.0},
    {"skill": "REST APIs", "confidence": 1.0},
]


def test_extract_text_from_txt():
    """Test extracting text from a TXT file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(SAMPLE_TXT)
        temp_path = f.name

    try:
        text = extract_text_from_txt(temp_path)
        assert SAMPLE_TXT.strip() == text.strip()
    finally:
        os.unlink(temp_path)


def test_extract_text_from_pdf():
    """Test extracting text from a PDF file (mocked)."""
    # We'll mock pdfplumber to avoid needing a real PDF
    with patch("app.utils.resume_extractor.pdfplumber") as mock_pdfplumber:
        # Mock the pdfplumber.open context manager
        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample PDF text"
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

        text = extract_text_from_pdf("dummy.pdf")
        assert text == "Sample PDF text\n"


def test_extract_text_from_docx():
    """Test extracting text from a DOCX file (mocked)."""
    with patch("app.utils.resume_extractor.docx") as mock_docx:
        mock_document = Mock()
        mock_paragraph = Mock()
        mock_paragraph.text = "Sample DOCX text"
        mock_document.paragraphs = [mock_paragraph]
        mock_docx.Document.return_value = mock_document

        text = extract_text_from_docx("dummy.docx")
        assert text == "Sample DOCX text\n"


def test_extract_resume_text_txt():
    """Test extracting text from a TXT file via the main function."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(SAMPLE_TXT)
        temp_path = f.name

    try:
        text = extract_resume_text(temp_path, mime_type="text/plain")
        assert SAMPLE_TXT.strip() == text.strip()
    finally:
        os.unlink(temp_path)


def test_nlp_engine_loads():
    """Test that the NlpEngine loads without error."""
    nlp = NlpEngine()
    assert nlp.nlp is not None
    # Check that the entity_ruler is in the pipeline
    pipe_names = [pipe[0] for pipe in nlp.nlp.pipeline]
    assert "entity_ruler" in pipe_names


def test_nlp_engine_process_text():
    """Test processing text with the NLP engine."""
    nlp = NlpEngine()
    doc = nlp.process_text(SAMPLE_TXT)
    assert doc is not None
    assert len(doc) > 0


def test_nlp_engine_extract_skill_entities():
    """Test extracting skill entities from processed text."""
    nlp = NlpEngine()
    doc = nlp.process_text(SAMPLE_TXT)
    entities = nlp.extract_skill_entities(doc)
    # We expect at least some entities to be labeled as SKILL
    # Note: the EntityRuler was built from the skill vocabulary with aliases
    assert len(entities) > 0
    for ent in entities:
        assert ent.label_ == "SKILL"


def test_skill_normalizer_exact_match():
    """Test exact matching of skill aliases."""
    normalizer = SkillNormalizer()
    # Test exact match for Python
    result = normalizer.normalize("Python")
    assert result is not None
    assert result["skill_id"] == "Python"  # skill_id is the name if no id in JSON
    assert result["name"] == "Python"
    assert result["category"] == "Programming"
    assert result["confidence"] == 1.0
    assert result["match_method"] == "exact"

    # Test case-insensitive
    result = normalizer.normalize("python")
    assert result is not None
    assert result["confidence"] == 1.0
    assert result["match_method"] == "exact"

    # Test alias
    result = normalizer.normalize("JS")  # but we don't have JS in our vocab, so skip
    # Instead, test an alias we added: "Python programming"
    result = normalizer.normalize("Python programming")
    assert result is not None
    assert result["confidence"] == 1.0
    assert result["match_method"] == "exact"


def test_skill_normalizer_fuzzy_match():
    """Test fuzzy matching for skill aliases."""
    normalizer = SkillNormalizer(fuzzy_threshold=80)
    # Test a close match
    result = normalizer.normalize("Pythn")  # missing 'o'
    assert result is not None
    assert result["skill_id"] == "Python"
    assert result["confidence"] < 1.0
    assert result["confidence"] >= 0.8  # because threshold is 80
    assert result["match_method"] == "fuzzy"

    # Test a poor match (should return None)
    result = normalizer.normalize("xyz")
    assert result is None


def test_skill_normalizer_no_match():
    """Test that non-skill text returns None."""
    normalizer = SkillNormalizer()
    result = normalizer.normalize("This is not a skill")
    assert result is None


def test_skill_extractor_from_text():
    """Test extracting skills from raw text."""
    extractor = SkillExtractor()
    skills = extractor.extract_skills_from_text(SAMPLE_TXT)

    # We expect to find the skills in the sample text
    assert len(skills) >= len(SAMPLE_EXPECTED_SKILLS)

    # Build a map of skill name to skill for easy checking
    skill_map = {s["name"]: s for s in skills}

    for expected in SAMPLE_EXPECTED_SKILLS:
        skill_name = expected["skill"]
        assert skill_name in skill_map, f"Expected skill {skill_name} not found in extracted skills"
        skill = skill_map[skill_name]
        assert skill["confidence"] > 0.0
        # The skill_id should match the name (since we don't have explicit IDs)
        assert skill["skill_id"] == skill_name
        # Category should be present
        assert skill["category"] is not None


def test_skill_extractor_duplicate_handling():
    """Test that duplicate skills are deduplicated."""
    text = "Python Python Python"
    extractor = SkillExtractor()
    skills = extractor.extract_skills_from_text(text)
    # Should only have one Python skill
    python_skills = [s for s in skills if s["name"] == "Python"]
    assert len(python_skills) == 1


def test_skill_extractor_empty_text():
    """Test extracting skills from empty text."""
    extractor = SkillExtractor()
    skills = extractor.extract_skills_from_text("")
    assert skills == []


def test_skill_extractor_unknown_text():
    """Test extracting skills from text with no known skills."""
    text = "The quick brown fox jumps over the lazy dog."
    extractor = SkillExtractor()
    skills = extractor.extract_skills_from_text(text)
    # Should be empty or very low confidence (but our normalizer returns None for no match)
    assert skills == []


# Optional: test the resume service logic without hitting the database
# We'll test the skill extraction from a resume file using the extractor
def test_skill_extractor_from_resume_mock():
    """Test extracting skills from a resume file (mocked)."""
    # We'll mock the resume extractor to return sample text
    with patch("app.skill_extraction.skill_extractor.extract_resume_text") as mock_extract:
        mock_extract.return_value = SAMPLE_TXT
        extractor = SkillExtractor()
        skills = extractor.extract_skills_from_resume("dummy.pdf")
        # Should have extracted the skills
        assert len(skills) > 0
        skill_names = {s["name"] for s in skills}
        assert "Python" in skill_names
        assert "Java" in skill_names
