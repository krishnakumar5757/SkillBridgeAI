"""
SkillBridge AI — Shared Constants

Application-wide constants used across modules.
These avoid magic numbers and provide a single definition point.
"""

# ---------------------------------------------------------------------------
# Proficiency Levels
# ---------------------------------------------------------------------------
# Maps proficiency names to numeric values for comparison and scoring.
# Used by Module 2 (skill matching) and Module 4 (readiness scoring).
PROFICIENCY_BEGINNER = 1
PROFICIENCY_INTERMEDIATE = 2
PROFICIENCY_ADVANCED = 3

PROFICIENCY_LEVELS: dict[str, int] = {
    "beginner": PROFICIENCY_BEGINNER,
    "intermediate": PROFICIENCY_INTERMEDIATE,
    "advanced": PROFICIENCY_ADVANCED,
}

PROFICIENCY_NAMES: dict[int, str] = {
    v: k for k, v in PROFICIENCY_LEVELS.items()
}

# The maximum proficiency level — used for normalization in scoring formulas.
# (Architecture Section 7.9, F-SCORE-2)
MAX_PROFICIENCY_LEVEL = 3


# ---------------------------------------------------------------------------
# Skill Source
# ---------------------------------------------------------------------------
SKILL_SOURCE_RESUME = "resume"
SKILL_SOURCE_SELF_REPORTED = "self_reported"
SKILL_SOURCE_INFERRED = "inferred"

VALID_SKILL_SOURCES = {
    SKILL_SOURCE_RESUME,
    SKILL_SOURCE_SELF_REPORTED,
    SKILL_SOURCE_INFERRED,
}


# ---------------------------------------------------------------------------
# Skill Priority (Module 2)
# ---------------------------------------------------------------------------
PRIORITY_CRITICAL = "critical"
PRIORITY_IMPORTANT = "important"
PRIORITY_NICE_TO_HAVE = "nice_to_have"

VALID_PRIORITIES = {
    PRIORITY_CRITICAL,
    PRIORITY_IMPORTANT,
    PRIORITY_NICE_TO_HAVE,
}


# ---------------------------------------------------------------------------
# Match Status (Module 2)
# ---------------------------------------------------------------------------
MATCH_STRONG = "strong"
MATCH_WEAK = "weak"
MATCH_MISSING = "missing"

VALID_MATCH_STATUSES = {MATCH_STRONG, MATCH_WEAK, MATCH_MISSING}


# ---------------------------------------------------------------------------
# Roadmap Item Status (Module 3/4)
# ---------------------------------------------------------------------------
STATUS_NOT_STARTED = "not_started"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"

VALID_ROADMAP_STATUSES = {
    STATUS_NOT_STARTED,
    STATUS_IN_PROGRESS,
    STATUS_COMPLETED,
}


# ---------------------------------------------------------------------------
# Readiness Classification (Module 4)
# ---------------------------------------------------------------------------
READINESS_ROLE_READY = "role_ready"
READINESS_NEARLY_READY = "nearly_ready"
READINESS_NEEDS_IMPROVEMENT = "needs_improvement"

VALID_READINESS_CLASSIFICATIONS = {
    READINESS_ROLE_READY,
    READINESS_NEARLY_READY,
    READINESS_NEEDS_IMPROVEMENT,
}


# ---------------------------------------------------------------------------
# Resume Processing Status (Module 1)
# ---------------------------------------------------------------------------
RESUME_PENDING = "pending"
RESUME_PROCESSED = "processed"
RESUME_FAILED = "failed"

VALID_RESUME_STATUSES = {
    RESUME_PENDING,
    RESUME_PROCESSED,
    RESUME_FAILED,
}


# ---------------------------------------------------------------------------
# File Upload Limits (Module 1)
# ---------------------------------------------------------------------------
MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".docx", ".txt"}
