# SkillBridge AI Foundation Documentation

## Overview

The Foundation of SkillBridge AI consists of the backend setup, configuration, security, database initialization, and shared utilities that enable the four modules to function. It provides:

- Application configuration via Pydantic Settings
- Secure JWT authentication with secret guard
- Database engine and session management (SQLAlchemy 2.0)
- Safe logging utilities (including database URL redaction)
- Base ORM model mixin (BaseMixin) for common fields
- Health check endpoint
- Exception handling framework

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher (for frontend)
- Git

### Backend Setup

1. Clone the repository
2. Navigate to the backend directory: cd backend
3. Create a virtual environment: python -m venv .venv
4. Activate the virtual environment:
   - Windows: .venv\Scripts\activate
   - Unix/MacOS: source .venv/bin/activate
5. Install dependencies: pip install -r requirements.txt
6. Copy the environment template: copy ..\.env.example .\.env (Windows) or cp ../.env.example .env (Unix/MacOS)
7. Edit .env to adjust settings as needed (see below)

### Environment Variables

The .env file (based on .env.example) contains:

- DATABASE_URL: SQLite database URL (default: sqlite:///./skillbridge.db)
- JWT_SECRET: Secret for signing JWT tokens (default: placeholder; must be changed to a strong secret for non-debug use)
- JWT_ALGORITHM: Algorithm for JWT signing (default: HS256)
- JWT_EXPIRY_HOURS: Token expiration time (default: 24)
- UPLOAD_DIR: Directory for uploaded files (default: ./uploads)
- SPACY_MODEL: spaCy language model for NLP (default: en_core_web_sm)
- CORS_ORIGINS: Comma-separated list of allowed frontend origins (default: http://localhost:5173)
- ENABLE_LLM: Enable experimental LLM features (default: false)
- OPENAI_API_KEY: API key for OpenAI (if LLM enabled)
- DEBUG: Enable debug mode (default: true in template; set to false for production/shared demos)

**Important**: The application refuses to start with an insecure JWT secret (placeholder or too short) when DEBUG=false. Generate a strong secret using:
python -c "import secrets; print(secrets.token_urlsafe(32))"

### Running the Backend

1. Ensure the virtual environment is activated
2. Start the application: uvicorn app.main:app --reload
3. The API will be available at http://localhost:8000
4. API documentation: http://localhost:8000/docs

### Frontend Setup

1. Navigate to the frontend directory: cd frontend
2. Install dependencies: npm install
3. Copy environment template: copy .env.example .env.local (Windows) or cp .env.example .env.local (Unix/MacOS)
4. Edit .env.local if needed (typically leave VITE_API_URL empty for proxy)

### Running the Frontend

1. Ensure you are in the frontend directory
2. Start the development server: npm run dev
3. The frontend will be available at http://localhost:5173

### Running Tests

#### Backend Tests

1. Ensure the backend virtual environment is activated
2. Run the test suite: pytest
3. Specific test files: pytest backend/tests/test_database.py

#### Frontend Tests

1. Ensure you are in the frontend directory
2. Run the test suite: npm test
3. Run tests in watch mode: npm run test:watch

## Foundation Components

### Configuration (app/core/config.py)

- Uses Pydantic Settings for type-safe environment variable parsing
- Provides default values suitable for local development
- Includes JWT secret guard constants (JWT_SECRET_PLACEHOLDER, JWT_SECRET_MIN_LENGTH)
- Settings instance is a singleton imported throughout the application

### JWT Secret Guard (app/main.py lifespan)

- On application startup, checks if DEBUG=False and the JWT secret is insecure (placeholder or too short)
- If insecure and DEBUG=False: raises RuntimeError to prevent startup
- If insecure and DEBUG=True: logs a warning (acceptable for local development)
- Logs the redacted database URL at startup for observability

### Database (app/core/database.py)

- SQLAlchemy 2.0 engine with SQLite default (configurable via DATABASE_URL)
- Session factory via get_db dependency
- Base declarative base for ORM models
- BaseMixin (imported from app.models.base) provides id, created_at, updated_at columns
- redact_db_url function safely redacts credentials from database URLs for logging
- check_db_connection function verifies database connectivity with safe error logging
- init_db function creates tables (used in development; migrations via Alembic for production)

### Safe Logging (app/core/logging.py)

- setup_logging configures structured logging to stdout
- Log level: DEBUG when debug=True, otherwise INFO
- Reduces noise from third-party libraries (sqlalchemy, httpx)
- get_logger returns a logger for the given name

### Base Mixin (app/models/base.py)

- Provides common columns for all entity models:
  - id: UUID4 string primary key
  - created_at: timezone-aware datetime set on creation
  - updated_at: timezone-aware datetime updated on modification
- Decorated with @declarative_mixin for correct SQLAlchemy 2.0 behavior
- Models inherit from both Base and BaseMixin:
  class Student(Base, BaseMixin):
      __tablename__ = "students"
      # ... model-specific columns

### Health Check (app/routes/health.py)

- Endpoint: GET /health
- Returns:
  - status: healthy if database connected, otherwise unhealthy
  - database: boolean indicating database connectivity
  - app_name: from settings
  - version: from settings
  - timestamp: ISO 8601 UTC timestamp

### Exception Handling (app/core/exceptions.py)

- Provides consistent error response format
- Handles HTTP exceptions and general exceptions
- Returns JSON with error (type) and message fields

## Security Considerations

- JWT secret is never logged in plaintext (only checked for insecurity)
- Database URLs are redacted before logging (credentials replaced with ***)
- Debug mode should be disabled (DEBUG=false) in production or shared demos
- The application refuses to start with an insecure JWT secret when DEBUG=false
- No hard-coded secrets in the source code (secrets must be provided via environment variables)
- CORS is restricted to configured origins
- Input validation is handled by Pydantic models in the schemas directory

## Development Workflow

1. Make changes to the backend
2. Run backend tests: pytest
3. Run frontend tests (if applicable): npm test
4. Check for linting errors: ruff check (backend)
5. Verify the application starts and health endpoint passes
6. Update documentation as needed

## Notes

- The foundation is intentionally minimal and focused on enabling the four modules.
- Module-specific code (student intelligence, career intelligence, etc.) resides in the modules directory and is imported as those modules are implemented.
- The foundation does not include resume processing, NLP skill extraction, A* search, or forward chaining — those are implemented in their respective modules.
- All foundation components are tested and verified to work together.

---

*This document reflects the foundation as implemented after completing the Foundation fixes.*
