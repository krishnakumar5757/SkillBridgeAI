"""
SkillBridge AI — NLP Engine (spaCy + Custom EntityRuler)

Provides NLP processing for resume text: tokenization, POS tagging, dependency parsing,
and custom entity recognition for skills using a pattern-based EntityRuler seeded from
the skill vocabulary.
"""
from __future__ import annotations

import json
import os
from typing import Any

import spacy
from spacy.matcher import Matcher
from spacy.tokens import Doc, Span

# Load the skill vocabulary from the JSON file
SKILL_VOCAB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "skills", "skills.json"
)


def load_skill_vocab() -> list[dict[str, Any]]:
    """Load the skill vocabulary from the JSON file."""
    with open(SKILL_VOCAB_PATH, encoding="utf-8") as f:
        return json.load(f)


class NlpEngine:
    """
    spaCy-based NLP pipeline with custom EntityRuler for skill extraction.
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the NLP engine.

        Args:
            model_name: The spaCy model to load.
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError as e:
            raise OSError(
                f"spaCy model '{model_name}' not found. Please install it using: "
                f"python -m spacy download {model_name}"
            ) from e

        # Add custom EntityRuler for skill recognition
        self._add_skill_entity_ruler()

        # Initialize matcher for context-based skill extraction (optional)
        self.matcher = Matcher(self.nlp.vocab)
        self._add_context_patterns()

    def _add_skill_entity_ruler(self) -> None:
        """
        Add an EntityRuler to the pipeline with patterns from the skill vocabulary.
        Each skill's aliases are added as patterns labeled "SKILL".
        """
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        skill_vocab = load_skill_vocab()
        patterns = []
        for skill in skill_vocab:
            for alias in skill["aliases"]:
                # Pattern: exact lowercase match of the alias
                patterns.append({"label": "SKILL", "pattern": [{"LOWER": alias.lower()}]})
        ruler.add_patterns(patterns)

    def _add_context_patterns(self) -> None:
        """
        Add matcher patterns for context-based skill extraction.
        For example, verbs like "proficient in", "experienced with", "skilled at"
        followed by a skill name.
        """
        # Pattern: verb + preposition + skill (we'll catch the skill as an entity later)
        # We'll use this to boost confidence or extract noun chunks around these verbs.
        # For simplicity, we'll just note that we can use dependency parsing.
        # We'll implement context analysis in the skill extractor.
        pass

    def process_text(self, text: str) -> Doc:
        """
        Process raw text with the spaCy pipeline.

        Args:
            text: Raw resume text.

        Returns:
            A spaCy Doc object.
        """
        return self.nlp(text)

    def extract_skill_entities(self, doc: Doc) -> list[Span]:
        """
        Extract entities labeled as "SKILL" from the doc.

        Args:
            doc: Processed spaCy Doc.

        Returns:
            List of Span objects representing skill entities.
        """
        return [ent for ent in doc.ents if ent.label_ == "SKILL"]

    def get_skill_candidates(self, doc: Doc) -> list[dict[str, Any]]:
        """
        Get skill candidates from the doc, including context information.

        Args:
            doc: Processed spaCy Doc.

        Returns:
            List of dictionaries with keys:
                - text: the extracted skill text
                - start: start character offset
                - end: end character offset
                - sent: the sentence containing the skill
                - root: the root token of the skill entity (if available)
        """
        candidates = []
        for ent in self.extract_skill_entities(doc):
            candidates.append(
                {
                    "text": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "sent": ent.sent,
                    "root": ent.root,
                }
            )
        return candidates
