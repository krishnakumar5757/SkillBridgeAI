# SkillBridge AI

**Intelligent Skill Gap and Career Readiness Assessment System**

SkillBridge AI analyzes a student's current skills, compares them against a
selected career role, identifies skill gaps, generates a personalized learning
roadmap, tracks learning progress, and determines career readiness.

## Project Structure

```
Skillbridge/
├── backend/          # FastAPI backend (Python)
├── frontend/         # React + TypeScript frontend (Vite)
├── modules/          # Pure algorithm packages (A*, Forward Chaining)
├── data/             # Configuration data (skills, roles, rules)
├── database/         # Database scripts and migrations
├── docs/             # Project documentation
├── tests/            # Top-level test suite
└── scripts/          # Utility scripts
```

## Technology Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Frontend    | React 18 + TypeScript + Vite       |
| Backend     | Python 3.11+ + FastAPI              |
| Database    | SQLite via SQLAlchemy 2.0          |
| Auth        | JWT + bcrypt                        |
| Testing     | pytest (backend), Vitest (frontend) |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm 9+

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Environment Configuration

```bash
# From the project root
cp .env.example .env
# Edit .env and set JWT_SECRET to a strong random value
```

### Running the Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.
API docs (Swagger UI) at `http://localhost:8000/docs`.
Health check at `http://localhost:8000/health`.

### Running the Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`.

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Architecture

The approved architecture is documented in `docs/architecture.md` (v2.2).

The project consists of four major modules:

1. **Student Intelligence** — Profile, resume, NLP, skill extraction
2. **Career Intelligence** — Role matching, skill gap analysis
3. **Learning Intelligence** — A* Search, personalized roadmap
4. **Career Readiness** — Forward Chaining, readiness classification

## Documentation

- `PROJECT_SPEC.md` — Functional specification (source of truth)
- `AGENTS.md` — Agent engineering standards
- `docs/architecture.md` — Technical architecture (v2.2, approved)
