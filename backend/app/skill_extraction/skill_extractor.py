"""
SkillBridge AI — Skill Extractor

Extracts skills from resume text using a two-layer approach:
1. Pattern-based extraction (via spaCy EntityRuler)
2. Context-based extraction (noun chunks and dependency parsing)

Uses SkillNormalizer to map extracted strings to canonical skills.
"""
from __future__ import annotations

import json
import os
from typing import Any

from app.nlp.nlp_engine import NlpEngine
from app.skill_extraction.skill_normalizer import SkillNormalizer
from app.utils.resume_extractor import extract_resume_text

# Load skill vocabulary for matching (if needed elsewhere)
SKILL_VOCAB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "skills", "skills.json"
)


def load_skill_vocab() -> list[dict[str, Any]]:
    """Load the skill vocabulary from the JSON file."""
    with open(SKILL_VOCAB_PATH, encoding="utf-8") as f:
        return json.load(f)


class SkillExtractor:
    """
    Extracts skills from text using NLP and normalizes them via SkillNormalizer.
    """

    def __init__(self):
        """Initialize the skill extractor."""
        self.nlp_engine = NlpEngine()
        self.skill_normalizer = SkillNormalizer()

    def _extract_raw_skill_strings(self, doc) -> list[dict[str, Any]]:
        """
        Extract raw skill strings from a spaCy Doc.

        Returns:
            List of dictionaries with keys:
                - text: the raw skill text
                - start: start character offset
                - end: end character offset
                - source: either "entity_ruler" or "noun_chunk"
        """
        raw_skills = []
        seen_spans: set[tuple[int, int]] = set()

        # Extract from EntityRuler (SKILL entities)
        for ent in doc.ents:
            if ent.label_ == "SKILL":
                span_key = (ent.start_char, ent.end_char)
                if span_key not in seen_spans:
                    seen_spans.add(span_key)
                    raw_skills.append(
                        {
                            "text": ent.text,
                            "start": ent.start_char,
                            "end": ent.end_char,
                            "source": "entity_ruler",
                        }
                    )

        # Extract from noun chunks (context-based)
        for chunk in doc.noun_chunks:
            span_key = (chunk.start_char, chunk.end_char)
            if span_key not in seen_spans:
                seen_spans.add(span_key)
                # Only consider noun chunks that are not too short and not stopwords-only
                if len(chunk.text.strip()) >= 2 and not all(
                    token.is_stop for token in chunk
                ):
                    raw_skills.append(
                        {
                            "text": chunk.text,
                            "start": chunk.start_char,
                            "end": chunk.end_char,
                            "source": "noun_chunk",
                        }
                    )
        return raw_skills

    def extract_skills_from_text(self, text: str) -> list[dict[str, Any]]:
        """
        Extract skills from raw resume text.

        Args:
            text: Raw resume text.

        Returns:
            List of dictionaries representing extracted skills, each with:
                - skill_text: the raw extracted text
                - skill_id: canonical skill ID (if matched)
                - name: canonical skill name
                - category: skill category
                - confidence: confidence score (0.0-1.0)
                - match_method: "exact" or "fuzzy"
                - start: start character offset
                - end: end character offset
        """
        # Process text with NLP engine
        doc = self.nlp_engine.process_text(text)

        # Get raw skill strings from entities and noun chunks
        raw_skills = self._extract_raw_skill_strings(doc)

        # Normalize each raw skill string
        normalized_skills = []
        for raw in raw_skills:
            normalized = self.skill_normalizer.normalize(raw["text"])
            if normalized:
                normalized_skills.append(
                    {
                        "skill_text": raw["text"],
                        "skill_id": normalized["skill_id"],
                        "name": normalized["name"],
                        "category": normalized["category"],
                        "confidence": normalized["confidence"],
                        "match_method": normalized["match_method"],
                        "start": raw["start"],
                        "end": raw["end"],
                    }
                )

        # Deduplicate by skill_id: keep the highest confidence for each skill
        best_by_skill: dict[str, dict[str, Any]] = {}
        for skill in normalized_skills:
            skill_id = skill["skill_id"]
            if (
                skill_id not in best_by_skill
                or skill["confidence"] > best_by_skill[skill_id]["confidence"]
            ):
                best_by_skill[skill_id] = skill

        return list(best_by_skill.values())

    def extract_skills_from_resume(
        self, file_path: str, mime_type: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Extract skills from a resume file.

        Args:
            file_path: Path to the resume file.
            mime_type: MIME type of the file (optional).

        Returns:
            List of extracted skills (same format as extract_skills_from_text).
        """
        text = extract_resume_text(file_path, mime_type)
        return self.extract_skills_from_text(text)
