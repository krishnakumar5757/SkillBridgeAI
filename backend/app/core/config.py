"""
SkillBridge AI — Application Configuration

Loads configuration from environment variables using Pydantic Settings.
The .env file is expected at the project root (one directory above backend/).
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# ---------------------------------------------------------------------------
# Path to the project root .env file
# backend/app/core/config.py -> backend/app/core/ -> backend/app/ -> backend/ -> root
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "backend" / "skillbridge.db"


def resolve_database_url(url: str) -> str:
    """Resolve relative SQLite URLs from the backend project directory."""
    if not url.startswith("sqlite:///") or ":memory:" in url:
        return url

    raw_path = url.removeprefix("sqlite:///")
    path = Path(raw_path)
    if path.is_absolute():
        return url
    resolved = (PROJECT_ROOT / "backend" / path).resolve()
    return f"sqlite:///{resolved.as_posix()}"

# ---------------------------------------------------------------------------
# JWT secret guard constants
# ---------------------------------------------------------------------------
# Module-level constants (NOT settings fields) so they cannot be overridden
# via environment variables and are not treated as Pydantic private attrs.
# The placeholder is the known insecure default; the app refuses to start
# with this value (or any secret shorter than the minimum length) when not
# in DEBUG mode. See app.main lifespan for the guard.
JWT_SECRET_PLACEHOLDER = "change-me-to-a-strong-random-secret"
JWT_SECRET_MIN_LENGTH = 32


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All values have sensible defaults for local development.
    Override by setting environment variables or editing .env.
    """

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    # Default is the known placeholder. The lifespan guard refuses to start
    # the app with this value (or any secret < JWT_SECRET_MIN_LENGTH) when
    # DEBUG is False. Generate a strong secret for any non-local run.
    JWT_SECRET: str = JWT_SECRET_PLACEHOLDER
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24

    # ------------------------------------------------------------------
    # File Storage
    # ------------------------------------------------------------------
    UPLOAD_DIR: str = "./uploads"

    # ------------------------------------------------------------------
    # NLP Configuration
    # ------------------------------------------------------------------
    SPACY_MODEL: str = "en_core_web_sm"

    # ------------------------------------------------------------------
    # CORS Configuration
    # ------------------------------------------------------------------
    CORS_ORIGINS: str = "http://localhost:5173"

    # ------------------------------------------------------------------
    # Optional LLM Integration
    # ------------------------------------------------------------------
    ENABLE_LLM: bool = False
    OPENAI_API_KEY: str = ""

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    APP_NAME: str = "SkillBridge AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse the comma-separated CORS_ORIGINS string into a list."""
        if not self.CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_jwt_secret_insecure(self) -> bool:
        """Check if the JWT secret is the known placeholder or too short.

        The lifespan guard uses this to refuse starting the app in non-debug
        mode with an insecure secret (architecture Section 12.6).
        """
        return (
            self.JWT_SECRET == JWT_SECRET_PLACEHOLDER
            or len(self.JWT_SECRET) < JWT_SECRET_MIN_LENGTH
        )


# Singleton settings instance
settings = Settings()
