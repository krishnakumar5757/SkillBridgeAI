"""
SkillBridge AI — Skill Normalizer

Normalizes raw skill strings to canonical skill IDs using alias dictionary and fuzzy matching.
"""
from __future__ import annotations

import json
import os
from typing import Any

from rapidfuzz import fuzz, process
from rapidfuzz.utils import default_process

# Load skill vocabulary for matching
SKILL_VOCAB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "skills", "skills.json"
)


def load_skill_vocab() -> list[dict[str, Any]]:
    """Load the skill vocabulary from the JSON file."""
    with open(SKILL_VOCAB_PATH, encoding="utf-8") as f:
        return json.load(f)


def build_alias_map(skill_vocab: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Build a mapping from alias (lowercase) to skill information.

    Returns:
        dict: alias_lower -> {skill_id, name, category, aliases}
    """
    alias_map = {}
    for skill in skill_vocab:
        skill_id = skill.get("id", skill["name"])  # fallback to name if no id
        for alias in skill["aliases"]:
            alias_map[alias.lower()] = {
                "skill_id": skill_id,
                "name": skill["name"],
                "category": skill["category"],
                "aliases": skill["aliases"],
            }
    return alias_map


class SkillNormalizer:
    """
    Normalizes raw skill strings to canonical skill IDs.
    """

    def __init__(self, fuzzy_threshold: int = 85):
        """
        Initialize the skill normalizer.

        Args:
            fuzzy_threshold: Minimum similarity score (0-100) for fuzzy matching.
        """
        self.skill_vocab = load_skill_vocab()
        self.alias_map = build_alias_map(self.skill_vocab)
        self.fuzzy_threshold = fuzzy_threshold

    def normalize(self, raw_skill: str) -> dict[str, Any] | None:
        """
        Normalize a raw skill string to a canonical skill.

        Args:
            raw_skill: The raw skill string extracted from text.

        Returns:
            Dictionary with keys:
                - skill_id: canonical skill ID
                - name: canonical skill name
                - category: skill category
                - confidence: confidence score (0.0-1.0)
                - match_method: "exact" or "fuzzy"
            Returns None if no match found above the fuzzy threshold.
        """
        if not raw_skill or not raw_skill.strip():
            return None

        raw_skill = raw_skill.strip()
        # Try exact match first (case-insensitive)
        exact_match = self.alias_map.get(raw_skill.lower())
        if exact_match:
            return {
                "skill_id": exact_match["skill_id"],
                "name": exact_match["name"],
                "category": exact_match["category"],
                "confidence": 1.0,
                "match_method": "exact",
            }

        # Try fuzzy match against all aliases
        match_result = process.extractOne(
            raw_skill,
            list(self.alias_map.keys()),
            scorer=fuzz.WRatio,
            score_cutoff=self.fuzzy_threshold,
            processor=default_process,
        )
        if match_result:
            matched_alias, score, _ = match_result
            skill_info = self.alias_map[matched_alias]
            return {
                "skill_id": skill_info["skill_id"],
                "name": skill_info["name"],
                "category": skill_info["category"],
                "confidence": score / 100.0,
                "match_method": "fuzzy",
            }
        return None
