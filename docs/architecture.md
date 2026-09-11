# SkillBridge AI — Technical Architecture

> **Version:** 2.2
> **Status:** Revised — Addresses architecture-verification.md finding F-NEW-1 (APPROVE WITH ONE REQUIRED FIX)
> **Author:** Architect Agent
> **Date:** 2026-08-20
> **Supersedes:** `docs/architecture.md` v2.1 (backed up as `docs/architecture.md.v2.1.bak`)
> **Review Verdict Addressed:** APPROVE WITH ONE REQUIRED FIX (1 HIGH: F-NEW-1)

---

## Table of Contents

1. [Technology Stack](#1-technology-stack)
2. [System Architecture](#2-system-architecture)
3. [Four Module Architecture](#3-four-module-architecture)
4. [Module 1 — Student Intelligence](#4-module-1--student-intelligence)
5. [Module 2 — Career Intelligence](#5-module-2--career-intelligence)
6. [Module 3 — Learning Intelligence (A* Search)](#6-module-3--learning-intelligence-a-search)
7. [Module 4 — Career Readiness (Forward Chaining)](#7-module-4--career-readiness-forward-chaining)
8. [Database Design](#8-database-design)
9. [API Architecture](#9-api-architecture)
10. [Data Flow](#10-data-flow)
11. [AI/NLP Boundary](#11-ainlp-boundary)
12. [Security Architecture](#12-security-architecture)
13. [Testing Architecture](#13-testing-architecture)
14. [Development Structure](#14-development-structure)
15. [Agent Boundaries](#15-agent-boundaries)
16. [Important Architectural Decisions](#16-important-architectural-decisions)
17. [Risks and Trade-offs](#17-risks-and-trade-offs)
18. [Recommended Project File Changes](#18-recommended-project-file-changes)
19. [Architecture Revision Summary](#19-architecture-revision-summary)
20. [Revision Summary (v2.2)](#20-revision-summary-v22)

---

## Conventions Used in This Document

Throughout this document, every significant recommendation is classified using the
following labels so that readers can distinguish evidence from opinion:

| Label | Meaning |
|-------|---------|
| **Requirement** | Explicitly mandated by `PROJECT_SPEC.md` or `AGENTS.md`. Non-negotiable. |
| **Observation** | Directly observed from the existing project files or directory structure. |
| **Assumption** | Inferred but not yet confirmed by the orchestrator or specification. |
| **Recommendation** | A proposed design choice based on evidence and project scope. |
| **Risk** | A plausible technical concern that should be verified or mitigated. |
| **Trade-off** | An accepted disadvantage in exchange for a chosen advantage. |

A dedicated **Revision Note** callout marks sections changed in response to the
formal architecture review (`docs/architecture-review.md`). Each note references
the finding ID it addresses (e.g., `F-ASTAR-1`).

---

## 1. Technology Stack

### 1.1 Frontend Framework

| Aspect | Value |
|--------|-------|
| **Choice** | React 18 + TypeScript + Vite |
| **Status** | Recommendation |

**Why it fits SkillBridge:**

- **Observation:** The existing `frontend/src/App.tsx` file and the `src/` directory
  structure (`components/`, `hooks/`, `pages/`, `modules/`, `services/`, `types/`,
  `utils/`, `layouts/`) confirm that a TypeScript/React project was intended. The
  `frontend/src/modules/` directory already contains subdirectories named
  `student-profile/`, `career-analysis/`, `learning-roadmap/`, and
  `career-readiness/` — one per SkillBridge module.
- **Advantages:** Component-based architecture maps cleanly to the four-module UI
  decomposition. TypeScript provides compile-time type safety for API contracts.
  Vite provides fast HMR and builds. Large ecosystem for file upload, forms, and
  progress visualization.
- **Disadvantages:** Requires Node.js toolchain and initial configuration.
- **Complexity introduced:** Low — standard React project, well within a 4-week
  timeline.
- **Necessity:** Recommended. The frontend scaffold already assumes this stack.

### 1.2 Backend Framework

| Aspect | Value |
|--------|-------|
| **Choice** | Python 3.11+ with FastAPI |
| **Status** | Recommendation |

**Why it fits SkillBridge:**

- **Observation:** The existing `backend/app/` directory has `core/`, `models/`,
  `routes/`, `schemas/`, `services/`, `utils/` — the standard FastAPI project
  structure with Pydantic schemas. Files `main.py`, `core/config.py`,
  `core/database.py`, `core/security.py` already exist (empty).
- **Advantages:** FastAPI provides automatic OpenAPI docs, async support, Pydantic
  v2 validation, and clean separation of routes/services/models. Python is the
  natural choice for NLP (spaCy) and algorithm implementation (A*, Forward
  Chaining). Type hints via Pydantic ensure data validation at API boundaries.
- **Disadvantages:** Synchronous NLP processing may block the async event loop
  (mitigated by running CPU-bound tasks in a thread pool via `run_in_executor`).
- **Complexity introduced:** Low — FastAPI is lightweight and the directory
  structure is already established.
- **Necessity:** Required. Python is essential for the NLP libraries and the two
  required syllabus algorithms.

### 1.3 Database

| Aspect | Value |
|--------|-------|
| **Choice** | SQLite (via SQLAlchemy 2.0 ORM) |
| **Status** | Recommendation |

**Why it fits SkillBridge:**

- **Advantages:** Zero configuration — no database server to install or manage.
  Single-file database is easy to back up, demo, and reset. SQLAlchemy ORM
  provides clean Python models and migrations (via Alembic). If needed later,
  switching to PostgreSQL requires only a connection string change.
- **Disadvantages:** Limited concurrent write performance (irrelevant for a
  single-student demo). No advanced features like full-text search (not required).
- **Complexity introduced:** Very low. SQLite is the simplest possible database
  choice.
- **Necessity:** Recommended. Proportional to an academic project with
  single-user or small-team demo usage.
- **Trade-off:** We deliberately choose SQLite over PostgreSQL to reduce
  deployment complexity. The SQLAlchemy abstraction allows migration to
  PostgreSQL later if the project scales.

### 1.4 Authentication

| Aspect | Value |
|--------|-------|
| **Choice** | JWT-based authentication with bcrypt password hashing |
| **Status** | Recommendation |

**Why it fits SkillBridge:**

- **Advantages:** Stateless authentication — no session storage needed. JWT
  works well with REST APIs. bcrypt provides secure password hashing. Simple to
  implement and demo.
- **Disadvantages:** No token revocation without additional logic (acceptable for
  this scope).
- **Complexity introduced:** Low. FastAPI has well-established JWT patterns.
- **Necessity:** Required. Student data (resumes, profiles) is sensitive;
  authentication is a security requirement.
- **Trade-off:** We choose JWT over session-based auth for API simplicity. We
  choose bcrypt over argon2 for wider library availability; both are secure.

### 1.5 File/Resume Storage

| Aspect | Value |
|--------|-------|
| **Choice** | Local filesystem with organized directory structure |
| **Status** | Recommendation |

**Why it fits SkillBridge:**

- **Advantages:** No cloud service dependency. Easy to demo offline. Simple
  implementation. Files stored at `uploads/resumes/{student_id}/`.
- **Disadvantages:** Not scalable to production. No backup/replication.
- **Complexity introduced:** Very low.
- **Necessity:** Sufficient for project scope. The architecture separates storage
  from processing, so cloud storage (S3) can be swapped in later by replacing the
  storage adapter.
- **Risk:** Local storage means files are lost if the server directory is deleted.
  Mitigated by treating this as a demo/academic project and adding `uploads/` to
  `.gitignore`.

### 1.6 NLP Libraries

| Aspect | Value |
|--------|-------|
| **Choice** | spaCy (core NLP) + RapidFuzz (fuzzy skill matching) + regex patterns |
| **Status** | Recommendation |

> **Revision Note (F-STACK-1, LOW):** The primary NLP contribution is
> tokenization + POS-based context analysis + a custom spaCy entity ruler seeded
> from the skill vocabulary. The default `en_core_web_sm` NER is weak for
> technology entities, so a custom `EntityRuler` (pattern-based NER) is the
> genuine NLP customization that makes skill extraction defensible. The `md`
> model is an optional upgrade if download size is acceptable.

**Why it fits SkillBridge:**

- **Advantages:** spaCy runs entirely offline — no API costs or network
  dependency. Provides tokenization, named entity recognition, part-of-speech
  tagging, and dependency parsing. RapidFuzz provides fast fuzzy string matching
  for skill alias resolution. Regex patterns provide deterministic skill matching
  against a known skill vocabulary.
- **Disadvantages:** spaCy models require download (~15 MB for `en_core_web_sm`,
  ~40 MB for `en_core_web_md`). Less flexible than LLMs for novel text
  interpretation.
- **Complexity introduced:** Medium. spaCy has a learning curve but is
  well-documented.
- **Necessity:** Required. NLP processing is a core requirement of Module 1.
- **Trade-off:** We use spaCy + a custom entity ruler + regex for NLP fundamentals
  rather than an LLM API. This keeps the system offline-capable and deterministic
  for skill extraction. An LLM can optionally enhance skill normalization later
  but must not replace the core pipeline.

### 1.7 AI/LLM Integration

| Aspect | Value |
|--------|-------|
| **Choice** | Optional — OpenAI API for enhanced explanations only |
| **Status** | Recommendation (optional, NOT required) |

**Why it fits SkillBridge:**

- **Recommendation:** The core system must work WITHOUT any LLM. If an LLM is
  used, it should be limited to:
  - Generating learning resource descriptions (Module 3)
  - Generating enhanced readiness explanations in natural language (Module 4)
  - Normalizing unusual skill names that fuzzy matching cannot resolve (Module 1)
- **Advantages:** Enhanced user experience for explanations.
- **Disadvantages:** Introduces API dependency, cost, and network requirement.
  Could mask the actual algorithms if overused.
- **Complexity introduced:** Low if optional; high risk if required.
- **Critical constraint:** The LLM must NEVER execute A* or Forward Chaining.
  These algorithms must be implemented as pure deterministic Python code. The LLM
  may only generate supplementary text content, never structural decisions.
- **Necessity:** NOT required. The system must be fully functional without any
  LLM. The LLM integration should be behind a feature flag that defaults to OFF.

### 1.8 API Communication

| Aspect | Value |
|--------|-------|
| **Choice** | REST (JSON) |
| **Status** | Recommendation |

**Why it fits SkillBridge:**

- **Advantages:** Simple, well-understood, sufficient for the 4-module data flow.
  FastAPI auto-generates OpenAPI docs. JSON is natively supported by both frontend
  and backend.
- **Disadvantages:** REST requires multiple round-trips for complex queries
  (acceptable for this scope).
- **Complexity introduced:** Low.
- **Necessity:** Sufficient. GraphQL would add unnecessary complexity.

### 1.9 Resume Parsing Libraries

| Aspect | Value |
|--------|-------|
| **Choice** | PyPDF2/pdfplumber (PDF) + python-docx (DOCX) + built-in (TXT) |
| **Status** | Recommendation |

**Why it fits SkillBridge:**

- **Advantages:** Each library handles one format well. All are pure-Python, no
  system dependencies. pdfplumber handles complex PDF layouts better than PyPDF2.
- **Disadvantages:** Some PDFs (scanned images) cannot be parsed without OCR
  (out of scope; return a clear error message).
- **Complexity introduced:** Low.
- **Necessity:** Required. Resume text extraction is a core Module 1 requirement.

### 1.10 Development Tooling

| Aspect | Value |
|--------|-------|
| **Choice** | pip + requirements.txt (backend), npm (frontend), pytest (testing), Alembic (migrations), ruff (backend lint/format), eslint + prettier (frontend lint/format) |
| **Status** | Recommendation |

> **Revision Note (F-STACK-2, LOW):** Added `ruff` for backend and
> `eslint` + `prettier` for frontend to improve cross-agent code consistency.
> These are zero-config and valuable for a multi-agent project. CI/CD remains
> excluded for scope, but a local `make lint` script is recommended.

**Why it fits SkillBridge:**

- **Advantages:** Standard Python and JavaScript package management. No additional
  tooling needed. pytest is the standard Python testing framework. Alembic
  provides database migrations for SQLAlchemy. ruff is a fast Python linter and
  formatter that replaces multiple tools (flake8, black, isort) with one.
- **Disadvantages:** None significant.
- **Complexity introduced:** Very low.
- **Necessity:** Required. The project currently has no dependency files.

### 1.11 Technology Stack Summary

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | React + TypeScript | React 18+, TS 5+ |
| Build Tool | Vite | Latest |
| Backend | Python + FastAPI | Python 3.11+, FastAPI 0.100+ |
| ORM | SQLAlchemy | 2.0+ |
| Migrations | Alembic | Latest |
| Database | SQLite | 3.x |
| NLP | spaCy | 3.7+ |
| Fuzzy Matching | RapidFuzz | Latest |
| Resume Parsing | pdfplumber / python-docx | Latest |
| Authentication | PyJWT + bcrypt | Latest |
| Validation | Pydantic | v2+ |
| Testing | pytest + pytest-asyncio | Latest |
| Frontend Testing | Vitest + Testing Library | Latest |
| Backend Lint/Format | ruff | Latest |
| Frontend Lint/Format | eslint + prettier | Latest |

---

## 2. System Architecture

### 2.1 Architecture Pattern

**Status:** Recommendation

The system uses a **layered modular monolith** with clear module boundaries.

A modular monolith is chosen over microservices because:

- **Observation:** The project is an academic system with a 4-week timeline and a
  single demo user.
- **Requirement:** Four modules with a strict linear dependency flow
  (Module 1 → 2 → 3 → 4).
- **Recommendation:** A monolith with internal module boundaries provides the
  separation of concerns needed for academic defensibility without the
  operational complexity of distributed services.

```
┌─────────────────────────────────────────────────────────────┐
│                       STUDENT USER                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                            │
│  React + TypeScript + Vite                                   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐ │
│  │ student-    │ │ career-    │ │ learning-  │ │ career-  │ │
│  │ profile     │ │ analysis   │ │ roadmap    │ │ readiness│ │
│  │ (Module 1)  │ │ (Module 2) │ │ (Module 3) │ │ (Module 4)│ │
│  └────────────┘ └────────────┘ └────────────┘ └──────────┘ │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Shared Components & Layouts              │   │
│  │  (Navigation, Auth, Common UI, Types, Utils)         │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API (JSON)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   API LAYER (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Authentication Middleware                  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Module 1 │ │ Module 2 │ │ Module 3 │ │ Module 4 │       │
│  │  Routes  │ │  Routes  │ │  Routes  │ │  Routes  │       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │
│       │            │            │            │               │
│       ▼            ▼            ▼            ▼               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Module 1 │ │ Module 2 │ │ Module 3 │ │ Module 4 │       │
│  │ Services │ │ Services │ │ Services │ │ Services │       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │
│       │            │            │            │               │
│       ▼            ▼            ▼            ▼               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Data Access Layer (SQLAlchemy ORM)       │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  SUPPORTING SERVICES                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  NLP Engine │  │ A* Algorithm│  │ Forward    │            │
│  │ (spaCy +   │  │ Engine      │  │ Chaining   │            │
│  │  regex)    │  │             │  │ Engine     │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                            │
│  SQLite + SQLAlchemy ORM                                     │
│  Students | Skills | Roles | Roadmaps | Progress | Readiness │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Layer Responsibilities

| Layer | Responsibility | Key Constraint |
|-------|---------------|----------------|
| **Frontend** | User interface, form handling, display of results | No business logic; delegates all processing to API |
| **API Routes** | Request parsing, validation, response formatting, authentication | Thin layer; delegates to services; no business logic |
| **Services** | Business logic, module orchestration, cross-module data contracts | Each module's services only access their own domain tables directly; cross-module access goes through the source module's service interface |
| **Algorithms** | A* Search, Forward Chaining, NLP processing | Pure computational logic; no HTTP or database access; takes structured data in, returns structured data out |
| **Data Access** | Data persistence, queries | Accessed only through SQLAlchemy ORM; no raw SQL in services |
| **Database** | Persistent storage | Single SQLite file; accessed only via ORM |

### 2.3 Module Boundary Enforcement

**Status:** Recommendation

Each module communicates with other modules through **well-defined data contracts**
(Pydantic schemas), not direct function calls into other modules' internals.

```
Module 1 ──[StudentSkillProfile]──► Module 2
Module 2 ──[SkillGapReport]───────► Module 3
Module 3 ──[LearningRoadmap]──────► Module 4
```

**Enforcement rules:**

1. Each module's services only access their own database tables directly.
2. Cross-module data access goes through the source module's service interface
   (e.g., Module 2 calls `Module1Service.get_skill_profile(student_id)` rather
   than querying `student_skills` directly).
3. Data contracts are defined as Pydantic schemas in a shared schemas package.
4. No circular dependencies: Module 4 may depend on Modules 1-3, but Modules 1-3
   never depend on Module 4.

> **Revision Note (F-MOD-1, MEDIUM):** The `SkillGapReport` contract (Section 5.6)
> now includes precomputed coverage percentages (`skill_coverage_percent`,
> `core_skill_coverage_percent`, `critical_skill_coverage_percent`). Module 4
> consumes these from the contract instead of recomputing them, keeping coverage
> logic in Module 2 as the single source of truth.

### 2.4 Dual Algorithm Location Strategy

**Status:** Recommendation

**Observation:** The project has two parallel locations for algorithm code:
- `modules/module-3-learning-intelligence/astar/` — top-level module directory
- `backend/app/services/module3/` — backend service directory

**Recommendation:** The algorithm logic (A* search, Forward Chaining engine) lives
in the `modules/` directory as pure, importable Python packages. The backend
services in `backend/app/services/moduleN/` import and orchestrate these
algorithms but do not contain the algorithm logic themselves.

```
modules/module-3-learning-intelligence/astar/
    ├── graph.py          ← SkillGraph data structure
    ├── algorithm.py      ← A* search implementation (pure)
    └── heuristic.py      ← Heuristic function (pure)

backend/app/services/module3/
    ├── skill_graph_builder.py   ← Builds graph from DB data
    ├── roadmap_generator.py     ← Calls A*, formats result
    └── roadmap_service.py       ← Orchestrates, persists
```

**Rationale:** This separation ensures the algorithms are testable in isolation
(without database or HTTP dependencies) and academically defensible as genuine
standalone implementations. The `modules/` directory is the "academic" location;
the `backend/app/services/` directory is the "application" location.

---

## 3. Four Module Architecture

### 3.1 Module Dependency Graph

```
Module 1: Student Intelligence
    │
    │ produces: Student Skill Profile
    ▼
Module 2: Career Intelligence
    │
    │ produces: Skill Gap Report
    ▼
Module 3: Learning Intelligence
    │
    │ produces: Personalized Learning Roadmap
    ▼
Module 4: Career Readiness
    │
    │ produces: Career Readiness Result
    ▼
[END]
```

**Status:** Requirement (from PROJECT_SPEC.md Section 7)

The dependency flow is strictly linear. No module may skip a predecessor:
- Module 2 requires Module 1's output (Student Skill Profile).
- Module 3 requires Module 2's output (Skill Gap Report) and Module 1's output
  (Student Skill Profile for start state).
- Module 4 requires Module 3's output (Learning Roadmap), Module 1's output
  (Student Skill Profile), and Module 2's output (Skill Gap Report with
  precomputed coverage metrics).

### 3.2 Module Summary Table

| Module | Name | Primary Input | Primary Output | Required Algorithm | Week |
|--------|------|---------------|----------------|-------------------|------|
| 1 | Student Intelligence | Student data + Resume | Student Skill Profile | None (NLP-based) | 1 |
| 2 | Career Intelligence | Student Skill Profile + Career Role | Skill Gap Report | None (deterministic matching) | 2 |
| 3 | Learning Intelligence | Skill Gap Report + Skill Profile | Personalized Learning Roadmap | A* Search | 3 |
| 4 | Career Readiness | Roadmap + Profile + Progress + Gap Report | Career Readiness Result | Forward Chaining | 4 |

### 3.3 Module 1 — Student Intelligence (Summary)

**Responsibilities:**
- Student registration and profile management
- Project management (title, description, technologies)
- Resume upload and file handling
- Resume text extraction (PDF, DOCX, TXT)
- NLP-based text processing
- Skill extraction from resume and profile
- Skill normalization (mapping variants to canonical names)
- Generating structured Student Skill Profile

**Inputs:** Student information (name, email, education, interests, projects), Resume file
**Outputs:** `StudentSkillProfile` — structured list of skills with proficiency levels
**Internal Components:** `ResumeTextExtractor`, `NLPEngine`, `SkillExtractor`, `SkillNormalizer`, `ProfileBuilder`
**Database Entities:** `Student`, `Resume`, `Project`, `Skill`, `StudentSkill`
**Dependencies:** None (first module in chain)

> **Revision Note (F-DB-2, MEDIUM):** Added `Project` to the database entities
> for Module 1. Projects are an explicit Module 1 input (PROJECT_SPEC.md Section 3)
> and are used by Module 4 facts (`has_projects`, `project_count`). See Section
> 8.2.3 for the `projects` table.

> Detailed architecture: [Section 4](#4-module-1--student-intelligence)

### 3.4 Module 2 — Career Intelligence (Summary)

**Responsibilities:**
- Career role selection and information display
- Role skill requirements lookup
- Skill matching against student profile
- Gap calculation (required proficiency − current proficiency)
- Strong/weak/missing skill identification
- Gap prioritization (prerequisite-aware)
- Coverage metric computation (skill, core, critical)

**Inputs:** `StudentSkillProfile` (from Module 1), Selected Career Role
**Outputs:** `SkillGapReport` — structured list of gaps with priorities AND precomputed coverage percentages
**Internal Components:** `RoleService`, `SkillMatcher`, `GapCalculator`, `GapPrioritizer`, `CoverageCalculator`
**Database Entities:** `CareerRole`, `RoleSkill`, `Skill`
**Dependencies:** Module 1 (consumes Student Skill Profile)

> **Revision Note (F-MOD-1, MEDIUM):** Module 2 now computes and exposes
> coverage percentages (`skill_coverage_percent`, `core_skill_coverage_percent`,
> `critical_skill_coverage_percent`) as part of the `SkillGapReport` contract.
> Module 4 consumes these rather than recomputing them.

> Detailed architecture: [Section 5](#5-module-2--career-intelligence)

### 3.5 Module 3 — Learning Intelligence (Summary)

**Responsibilities:**
- Skill dependency graph construction
- A* Search algorithm execution (genuine implementation)
- Personalized learning roadmap generation (for MISSING skills)
- Roadmap representation and storage

**Inputs:** `SkillGapReport` (from Module 2), `StudentSkillProfile` (from Module 1)
**Outputs:** `PersonalizedLearningRoadmap` — ordered list of learning steps
**Internal Components:** `SkillGraph`, `AStarSearch`, `HeuristicFunction`, `CostFunction`, `PathReconstructor`, `RoadmapGenerator`
**Database Entities:** `SkillDependency`, `LearningRoadmap`, `RoadmapItem`
**Dependencies:** Module 1 (skill profile for start state), Module 2 (gap report for target skills)

> **Revision Note (F-ASTAR-4, MEDIUM):** A* plans only MISSING skills (skills
> not in the student's current state). Weak skills (student has the skill but
> below required proficiency) are NOT planned by A*; they are addressed by
> Module 4's proficiency facts and readiness scoring. This is a deliberate
> design choice for the 4-week scope (Option A from the review). See Section
> 6.3 and 6.14 for details.

> Detailed architecture: [Section 6](#6-module-3--learning-intelligence-a-search)

### 3.6 Module 4 — Career Readiness (Summary)

**Responsibilities:**
- Learning progress tracking (via roadmap item status)
- Fact generation from student data (consuming Module 2's coverage metrics)
- Rule evaluation using Forward Chaining (genuine implementation)
- Readiness scoring (weighted factor formula — supporting evidence only)
- Readiness classification (SOLE authority: Forward Chaining)
- Explanation generation

**Inputs:** `StudentSkillProfile`, `LearningRoadmap`, `SkillGapReport` (with coverage metrics)
**Outputs:** `ReadinessResult` — classification (from FC) + score (supporting) + explanation
**Internal Components:** `FactGenerator`, `ForwardChainingEngine`, `RuleBase`, `ReadinessScorer`, `ExplanationGenerator`
**Database Entities:** `RoadmapItem` (progress source of truth), `ProgressAuditLog`, `ReadinessResult`
**Dependencies:** Modules 1, 2, and 3 (consumes their outputs)

> **Revision Note (F-FC-1, HIGH):** Forward Chaining is now the SOLE mechanism
> that determines the readiness classification (Role Ready / Nearly Ready /
> Needs Improvement). The readiness score (0–100) is a numeric measure
> displayed as supporting evidence; it does NOT independently classify the
> student. The score-threshold if/else classification has been removed.
>
> **Revision Note (F-FC-2, HIGH):** The `contributes_to_score` field has been
> removed from the rule schema. The weighted factor scoring formula (Section
> 7.9) is the single scoring model. No example sums rule contributions to
> compute the score.
>
> **Revision Note (F-NEW-1, HIGH):** The Forward Chaining engine now includes
> a classification-overwrite guard. Once `readiness_classification` has been
> asserted, no other rule may overwrite it. This prevents lower-priority
> classification rules from overwriting a higher-priority conclusion.
>
> **Revision Note (F-DB-1, MEDIUM):** `roadmap_items.status` is the authoritative
> progress state. The `learning_progress` table has been repurposed as an
> append-only `progress_audit_log` table. See Section 8.2.10.

> Detailed architecture: [Section 7](#7-module-4--career-readiness-forward-chaining)

### 3.7 Coupling Prevention

**Status:** Recommendation

Each module communicates through well-defined data contracts (Pydantic schemas),
not direct function calls into other modules' internals.

```
Module 1 ──[StudentSkillProfile schema]──► Module 2
Module 2 ──[SkillGapReport schema]──────► Module 3
Module 3 ──[LearningRoadmap schema]──────► Module 4
```

Each module's services only access their own database tables directly.
Cross-module data access goes through the source module's service interface.

---

## 4. Module 1 — Student Intelligence

### 4.1 Pipeline Overview

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Student  │───►│ Resume   │───►│ Text     │───►│ NLP +    │───►│ Student  │
│ Profile  │    │ Upload   │    │ Extract  │    │ Skill    │    │ Skill    │
│ + Skills │    │          │    │          │    │ Extract  │    │ Profile  │
│ +Projects│    └──────────┘    └──────────┘    └──────────┘    └──────────┘
└──────────┘
```

### 4.2 Student Profile Creation

**Status:** Recommendation

The student provides:
- Personal information (name, email)
- Education (institution, degree, year)
- Areas of interest
- Projects (title, description, technologies used) — stored in the `projects` table
- Existing skills (self-reported, with proficiency)

All fields are validated via Pydantic schemas. Self-reported skills are stored
with `source = "self_reported"` and serve as the proficiency baseline.

> **Revision Note (F-DB-2, MEDIUM):** Projects are now persisted in a dedicated
> `projects` table (Section 8.2.3) rather than as a JSON field. This supports
> Module 4's `has_projects` and `project_count` facts with structured,
> queryable data.

### 4.3 Resume Upload and Text Extraction

**Status:** Recommendation

```
Resume File Upload
       │
       ▼
┌──────────────┐
│ File Type    │──► PDF: use pdfplumber
│ Detection    │──► DOCX: use python-docx
│              │──► TXT: direct read
└──────────────┘
       │
       ▼
┌──────────────┐
│ Raw Text     │──► Cleaned, normalized text
│ Output       │
└──────────────┘
```

**Components:**
- `ResumeTextExtractor` class with methods for each format
- File validation: check MIME type, file size limit (5 MB max), allowed extensions
- Error handling for corrupted or unsupported files
- Extracted text stored in `resumes.extracted_text` column for reprocessing without re-upload

> **Revision Note (F-API-2, LOW):** Resume reprocessing semantics are now
> documented: Reprocessing a resume deletes prior `source = 'resume'` skills
> for that student and re-inserts fresh ones. Self-reported skills
> (`source = 'self_reported'`) are preserved. The `student_skills` table
> includes a `resume_id` foreign key to track which resume produced which
> skill, enabling clean re-extraction. See Section 8.2.5.

### 4.4 NLP Processing Pipeline

**Status:** Recommendation

```
Raw Resume Text
       │
       ▼
┌──────────────────┐
│ spaCy Processing │──► Tokenization, POS tagging, NER, dependency parsing
│ (en_core_web_sm  │
│  or _md)         │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ Custom Entity    │──► Pattern-based NER seeded from skill vocabulary
│ Ruler            │    (genuine NLP customization, more defensible than
│                  │     relying on default sm model NER)
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ Context Analysis │──► Use POS tags and dependency parsing to determine
│                  │    if extracted entities are skills vs. companies vs. roles
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ Extracted Skills │──► Raw list of identified skills from resume
│ (unnormalized)   │
└──────────────────┘
```

> **Revision Note (F-STACK-1, LOW):** Added a custom spaCy `EntityRuler`
> seeded from the skill vocabulary as the primary NER mechanism. This is
> genuine NLP customization and is more defensible than relying on the
> small model's default NER for technology entities.

### 4.5 Skill Extraction Strategy

**Status:** Recommendation

Two-layer extraction approach:

**Layer 1 — Pattern-based extraction (primary, deterministic):**
- Maintain a canonical skill vocabulary (JSON file at `data/skills/skills.json`)
- Each skill entry has: `id`, `name`, `category`, `aliases` (list of common
  names), `description`, `learning_cost_hours`
- Match extracted entities against skill aliases using fuzzy matching (RapidFuzz)
- Example: "JS", "Javascript", "JavaScript programming" all map to "JavaScript"

**Layer 2 — Context-based extraction (supplementary):**
- Use the custom spaCy EntityRuler (pattern-based NER) seeded from the skill
  vocabulary to detect technology-related named entities
- Filter entities by POS pattern: proper nouns and nouns in technology contexts
- Match against skill vocabulary

**Combination:** Merge results from both layers, deduplicate, and normalize.

### 4.6 Skill Normalization

**Status:** Recommendation

```
Raw Extracted Skill
       │
       ▼
┌──────────────────┐
│ Alias Matching   │──► Check against skill vocabulary aliases
│ (exact + fuzzy)  │    Exact match: "Python" → "Python"
└──────────────────┘    Fuzzy match: "Py" → "Python" (if in aliases, threshold ≥ 85)
       │
       ▼
┌──────────────────┐
│ Category Mapping │──► Assign skill to category (Programming, Framework,
│                  │    DevOps, Database, etc.)
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ Proficiency      │──► Infer from context clues:
│ Estimation       │    - Resume mentions "expert in X" → Advanced
│                  │    - Listed in projects → Intermediate+
│                  │    - Listed in skills section only → Beginner-Intermediate
│                  │    - Self-reported skill → Use student's reported level
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ Merged Profile   │──► Combine resume-derived + self-reported skills
│                  │    (resume adds new skills, self-reported provides
│                  │     proficiency baseline; if both sources mention a skill,
│                  │     take the higher proficiency)
└──────────────────┘
```

### 4.7 Student Skill Profile Structure

```python
class StudentSkillProfile:
    student_id: str
    skills: list[StudentSkill]
    last_updated: datetime

class StudentSkill:
    skill_id: str
    name: str
    category: str
    proficiency: str       # "beginner" | "intermediate" | "advanced"
    source: str            # "resume" | "self_reported" | "inferred"
    confidence: float      # 0.0 to 1.0
```

### 4.8 How Unstructured Resume Data Becomes Structured Skill Data

**Status:** Recommendation

The transformation pipeline:

1. **Unstructured input:** A PDF/DOCX/TXT file containing free-form text.
2. **Text extraction:** Format-specific extractors produce raw text string.
3. **NLP processing:** spaCy tokenizes, tags, and parses the text into linguistic
   structures.
4. **Entity extraction:** The custom EntityRuler (pattern-based NER) and named
   entities/noun phrases are extracted as candidate skill mentions.
5. **Vocabulary matching:** Each candidate is matched against the canonical skill
   vocabulary using exact alias matching first, then fuzzy matching (RapidFuzz
   with a similarity threshold).
6. **Normalization:** Matched candidates are mapped to canonical skill IDs.
   Unmatched candidates are discarded (or optionally sent to LLM for
   normalization if the feature flag is enabled).
7. **Proficiency inference:** Rule-based inference from context clues determines
   the proficiency level for each extracted skill.
8. **Profile merging:** Resume-derived skills are merged with self-reported
   skills. Self-reported proficiency is the baseline; resume evidence may upgrade
   proficiency.
9. **Structured output:** `StudentSkillProfile` — a list of `StudentSkill` objects
   with canonical skill IDs, proficiency levels, source attribution, and
   confidence scores.

### 4.9 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Skill vocabulary | Pre-defined JSON file (`data/skills/skills.json`) | Deterministic, testable, easily extensible without code changes |
| Proficiency inference | Rule-based from context | No LLM needed, explainable, deterministic |
| Resume parsing | Format-specific extractors | Robust handling of PDF/DOCX/TXT |
| Normalization | Alias dictionary + fuzzy matching (RapidFuzz) | Handles common name variations deterministically |
| Skill merging | Resume supplements self-reported; higher proficiency wins | Self-reported is baseline truth; resume evidence upgrades |
| Confidence scoring | 0.0-1.0 per skill | Allows downstream modules to weight skills |
| NER mechanism | Custom spaCy EntityRuler seeded from vocabulary | Genuine NLP customization, defensible for technology entities |
| Project storage | Dedicated `projects` table | Structured, queryable; supports Module 4 facts |

---

## 5. Module 2 — Career Intelligence

### 5.1 Career Role Data Model

**Status:** Recommendation

```python
class CareerRole:
    id: str
    name: str                    # e.g., "Backend Developer"
    description: str
    category: str                 # e.g., "Engineering"
    required_skills: list[RoleSkill]

class RoleSkill:
    skill_id: str                # FK to Skill
    skill_name: str              # Denormalized for display
    minimum_proficiency: str     # "beginner" | "intermediate" | "advanced"
    priority: str                # "critical" | "important" | "nice_to_have"
    is_core: bool                # Whether this is a core/non-negotiable skill
```

Career roles are seeded from `data/roles/roles.json`. The architecture supports
adding new roles by simply adding entries to this file — no code changes required.

### 5.2 How Module 1's Student Skill Profile Is Consumed

**Status:** Recommendation

Module 2 receives the `StudentSkillProfile` from Module 1 through the service
interface:

```python
# Module 2 service calls Module 1 service
skill_profile = module1_service.get_skill_profile(student_id)
```

The `StudentSkillProfile` provides:
- `student_id` — to identify the student
- `skills` — list of `StudentSkill` objects, each with `skill_id`, `proficiency`,
  `source`, `confidence`

Module 2 does NOT query the `student_skills` table directly. It goes through
Module 1's service interface to maintain module boundaries.

### 5.3 Skill Matching Algorithm

**Status:** Recommendation

```
For each required skill in Career Role:
    │
    ├── Does student have this skill?
    │       │
    │       ├── YES: Compare proficiency levels
    │       │       │
    │       │       ├── Student >= Required → STRONG
    │       │       ├── Student < Required by 1 level → WEAK
    │       │       └── Student < Required by 2+ levels → WEAK (priority gap)
    │       │
    │       └── NO → MISSING
    │
    └── Record match result
```

Proficiency levels map to numeric values for comparison:
- `beginner = 1`, `intermediate = 2`, `advanced = 3`

> **Revision Note (F-SCORE-2, LOW):** The proficiency-to-number mapping is
> defined as a named constant `MAX_PROFICIENCY_LEVEL = 3` in
> `backend/app/utils/constants.py` and referenced wherever the mapping is
> needed (Module 2 matching, Module 4 scoring). This avoids magic numbers.

### 5.4 Gap Calculation

**Status:** Recommendation

For each skill gap, calculate:

```python
gap_score = proficiency_level(required) - proficiency_level(student)
```

- `gap_score = 0` → Strong (student meets or exceeds requirement)
- `gap_score = 1` → Weak (student is one level below)
- `gap_score = 2` → Very Weak (student is two levels below)
- `gap_score = 3` → Missing (student does not have the skill at all)

### 5.5 Gap Prioritization

**Status:** Recommendation

Gaps are prioritized using dependency-aware ordering:

1. **Missing prerequisite skills** → Highest priority (skills that block other
   skills in the dependency graph)
2. **Critical role skills** → High priority (skills marked as `critical` in the
   role definition)
3. **Large proficiency gaps** → Medium priority (skills where student is far
   below required)
4. **Important role skills** → Medium priority
5. **Small proficiency gaps** → Lower priority
6. **Nice-to-have skills** → Lowest priority

### 5.6 Skill Gap Report Structure

> **Revision Note (F-MOD-1, MEDIUM):** The `SkillGapReport` contract now
> includes precomputed coverage percentages. Module 4 consumes these from the
> contract instead of recomputing them, keeping coverage logic in Module 2 as
> the single source of truth.

```python
class SkillGapReport:
    student_id: str
    career_role_id: str
    career_role_name: str
    total_required_skills: int
    matched_skills: list[SkillMatch]
    strong_skills: list[SkillMatch]     # Student meets or exceeds requirement
    weak_skills: list[SkillMatch]       # Student has skill but below required level
    missing_skills: list[SkillMatch]   # Student doesn't have the skill
    overall_gap_score: float            # 0.0 to 1.0 (0 = no gaps, 1 = all missing)
    prioritized_gaps: list[SkillGap]    # Ordered by priority

    # Coverage metrics (precomputed by Module 2, consumed by Module 4)
    skill_coverage_percent: float         # (acquired / required) * 100
    core_skill_coverage_percent: float    # Only core skills
    critical_skill_coverage_percent: float # Only critical skills
    total_skills_acquired: int            # Count of required skills student has
    total_skills_required: int            # Count of required skills for the role

class SkillMatch:
    skill_id: str
    skill_name: str
    required_proficiency: str
    current_proficiency: str | None     # None if missing
    match_status: str                   # "strong" | "weak" | "missing"
    gap_score: int                      # 0, 1, 2, or 3
    priority: str                       # "critical" | "important" | "nice_to_have"
    is_core: bool

class SkillGap:
    skill_id: str
    skill_name: str
    gap_score: int
    priority_rank: int                  # 1 = highest priority
    is_prerequisite: bool               # Whether this skill blocks others
    blocks: list[str]                   # Skill IDs that depend on this skill
```

**Coverage metric definitions (computed by Module 2):**

```python
# A skill is "acquired" if the student has it at ANY proficiency level
# (i.e., it appears in their StudentSkillProfile)
acquired = [s for s in required_skills if s.skill_id in student_skill_ids]
skill_coverage_percent = (len(acquired) / len(required_skills)) * 100

# Core skills only
core_required = [s for s in required_skills if s.is_core]
core_acquired = [s for s in core_required if s.skill_id in student_skill_ids]
core_skill_coverage_percent = (len(core_acquired) / len(core_required)) * 100

# Critical priority skills only
critical_required = [s for s in required_skills if s.priority == "critical"]
critical_acquired = [s for s in critical_required if s.skill_id in student_skill_ids]
critical_skill_coverage_percent = (len(critical_acquired) / len(critical_required)) * 100
```

### 5.7 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Role data source | JSON seed file (`data/roles/roles.json`) | Easy to add roles without code changes |
| Gap calculation | Level-based subtraction (numeric) | Simple, explainable, deterministic |
| Prioritization | Dependency + priority hybrid | Ensures prerequisites are learned first |
| Skill matching | Exact skill ID matching | After normalization in Module 1, skills use canonical IDs |
| Module 1 access | Via service interface, not direct DB query | Maintains module boundary |
| Coverage metrics | Computed by Module 2, exposed in SkillGapReport | Single source of truth; Module 4 consumes, not recomputes |
| Proficiency mapping | Named constant `MAX_PROFICIENCY_LEVEL = 3` | Avoids magic numbers; single definition point |

---

## 6. Module 3 — Learning Intelligence (A* Search)

### 6.1 CRITICAL: A* Must Be Genuine

**Status:** Requirement (from AGENTS.md Section 3 and PROJECT_SPEC.md Section 8)

The A* Search implementation must contain:
- Graph representation with nodes and edges
- Cost function g(n)
- Heuristic function h(n)
- f(n) = g(n) + h(n)
- Open list (priority queue)
- Closed list (visited set)
- Node expansion
- Path reconstruction

The implementation must NOT be a fake that returns pre-defined results. The
generated roadmap must depend on the student's current skill state and the target
role's required skills.

### 6.2 Skill Dependency Graph

**Status:** Recommendation

The skill dependency graph is a **weighted directed acyclic graph (DAG)**.

**Data Structure:**

```python
class SkillNode:
    skill_id: str
    name: str
    category: str
    learning_cost: float          # Estimated hours to learn (base cost)
    prerequisites: list[str]      # Skill IDs that must be learned first

class SkillEdge:
    from_skill: str               # Prerequisite skill ID
    to_skill: str                 # Dependent skill ID
    # Note: edge_cost is NOT used in the cost model.
    # The cost of learning a skill is its learning_cost (SkillNode.learning_cost).
    # Prerequisite relationships constrain ordering (successor function)
    # but do not add extra cost. This keeps the cost model simple and
    # the optimality claim precise (F-ASTAR-3).

class SkillGraph:
    nodes: dict[str, SkillNode]   # skill_id → SkillNode
    edges: dict[str, list[SkillEdge]]  # skill_id → list of outgoing edges
```

> **Revision Note (F-ASTAR-3, MEDIUM):** The `edge_cost` field has been removed
> from `SkillEdge`. Prerequisite relationships constrain ordering (via the
> successor function) but do not add extra cost. The cost model is a single
> scalar: the learning cost of each skill. This makes the optimality claim
> precise: A* finds the minimum-total-learning-cost path subject to prerequisite
> ordering constraints.

**Storage:** `data/skill-relationships/dependencies.json`

**Graph Construction:**
- Nodes = all skills in the skill vocabulary
- Edges = prerequisite relationships from `SkillDependency` data
- Costs = learning time estimates (from skill metadata or configurable defaults)

### 6.3 State Space Definition

**Status:** Recommendation

This is the most critical architectural decision for A*.

**Nodes in the search space** are NOT individual skills — they are **skill
states** (sets of skills the student has acquired).

```
State = frozenset of skill_ids the student currently knows
```

**Why states instead of skills?**
- A student can be in different "states" depending on which combination of skills
  they have.
- A* needs to search through states to find the optimal path from current state to
  goal state.
- This is analogous to how A* navigates through positions on a map — the state is
  the "position" and skills are the "moves."

> **Revision Note (F-ASTAR-4, MEDIUM):** The state representation is **binary**
> (skill present or absent). A* plans only for **MISSING** skills — skills not
> in the student's current state. **Weak skills** (student has the skill but
> below the required proficiency level) are NOT planned by A* because the
> binary state cannot represent proficiency levels. Weak skills are addressed
> by Module 4's proficiency facts and readiness scoring.
>
> This is a deliberate design choice (Option A from the review) appropriate for
> the 4-week academic scope. A proficiency-aware state representation (Option B)
> would increase state-space size and implementation effort without proportional
> benefit for the demo. The roadmap output still includes
> `current_proficiency` and `target_proficiency` for display purposes, but
> these are informational labels, not search-state components.

### 6.4 Start State

```python
start_state = frozenset(student_current_skill_ids)
```

**Example:** If the student knows Python, Git, and SQL:
```
start_state = frozenset({"python", "git", "sql"})
```

Note: The start state includes ALL skills the student has, regardless of
proficiency level. A student who "knows Python at beginner" still has "python"
in their start state.

### 6.5 Goal State

```python
# The goal is built ONLY from missing skills (skills not in the student's state).
# Weak skills are NOT included in the goal because the binary state already
# contains them (the student has the skill, just at a lower proficiency).
goal_required_skill_ids = set(missing_skill_ids from SkillGapReport)

goal_test = lambda state: goal_required_skill_ids.issubset(state)
```

The goal is reached when the student's state includes ALL **missing** required
skills. The goal is NOT a single state — it is ANY state that satisfies the
requirement (a goal test function).

> **Revision Note (F-ASTAR-4 / F-MOD-2, MEDIUM):** The goal is now built ONLY
> from `missing_skills` (skills the student does not have at all). Weak skills
> are excluded because their IDs are already in the start state (the student
> has them at some proficiency), so adding them to the goal would make the
> goal test pass immediately without generating any learning steps for them.
> Weak-skill proficiency upgrades are handled by Module 4's readiness scoring,
> not by the A* roadmap.

**Example:** If the role requires Python, SQL, Docker, REST APIs, System Design,
and the student knows Python, Git, SQL (SQL at beginner, below required
intermediate):
```
missing_skills = {"docker", "rest_apis", "system_design"}  # NOT in student's state
weak_skills = {"sql"}  # In student's state but below required proficiency

goal_required_skill_ids = {"docker", "rest_apis", "system_design"}  # Only missing
goal_test checks: {"docker", "rest_apis", "system_design"} ⊆ state
```

### 6.6 Neighbors / Successor Function

From any state S, the possible next states are:

```
For each skill X that:
    1. X is NOT already in S
    2. All prerequisites of X ARE in S
    3. X is needed (either a missing required skill, or is a prerequisite
       of a missing required skill)

    Successor state = S ∪ {X}
    Cost to reach successor = learning_cost(X)
```

**Key invariant:** Each skill is acquired **at most once** per path. The
successor function enforces `X not in S`, so a skill can never be "re-learned."
This invariant is essential for the consistency of g(n) (see Section 6.7).

**Example:** From state `{"python", "git", "sql"}`:
- "docker" becomes available if its prerequisites (e.g., "linux") are in the state
- "rest_apis" becomes available if its prerequisites are met
- Each generates a new state with cost = that skill's learning cost

### 6.7 Cost Function g(n)

> **Revision Note (F-ASTAR-2, MEDIUM):** g(n) is now explicitly defined as the
> **accumulated path cost** — the sum of learning costs for all skills learned
> along the path from the start state to the current state. The "learned at
> most once" invariant (enforced by the successor function) guarantees that
> the path-based definition and the state-based definition are mathematically
> equivalent.

**Status:** Recommendation

```python
def g(state, came_from) -> float:
    """
    Accumulated cost to reach this state from start_state along the path
    recorded in came_from.

    This is the sum of learning costs for all skills learned on the path.
    Because each skill is acquired at most once (successor function enforces
    X not in S), this equals the sum of learning costs of skills in
    (state - start_state).

    In the implementation, g is tracked incrementally via came_from:
        g(successor) = g(current) + cost(successor_skill)
    This is equivalent to recomputing from the state because of the
    "learned at most once" invariant.
    """
    # Incremental tracking (used in implementation):
    # g(successor_state) = came_from[current_state].g + learning_cost(new_skill)
    #
    # State-based equivalent (mathematically equal due to the invariant):
    # g(state) = sum(learning_cost(skill) for skill in (state - start_state))
```

- `g(start_state) = 0` (already know these skills)
- Each transition adds the learning cost of the newly acquired skill
- g accumulates monotonically along any path (learning costs are non-negative)
- The "learned at most once" invariant guarantees no skill's cost is counted twice

### 6.8 Heuristic Function h(n)

> **Revision Note (F-ASTAR-1, HIGH):** The heuristic definition and admissibility
> proof have been completely rewritten. The heuristic sums the base learning
> cost of each missing **required** skill. It does NOT include prerequisite
> costs. An explicit warning is added: do NOT add prerequisite costs to h,
> as this would risk double-counting and could make h inadmissible.

**Status:** Recommendation

```python
def h(state) -> float:
    """
    Admissible heuristic: estimates the minimum remaining cost to reach the goal.

    For each missing required skill (in goal_required_skill_ids but not in state):
        Add its base learning cost.

    This is a LOWER BOUND on the actual remaining cost because:
    - Each missing required skill MUST be learned at least once, costing at
      least its base learning cost.
    - The actual remaining cost may be HIGHER because non-required prerequisite
      skills may also need to be learned (their costs are NOT counted in h).
    - Therefore h(state) <= h*(state) (the true optimal remaining cost).

    WARNING: Do NOT add prerequisite costs to h. Doing so would risk
    double-counting (a prerequisite that is itself a required skill would
    be counted both as a required skill and as a prerequisite) and could
    make h INADMISSIBLE, voiding A*'s optimality guarantee.
    """
    remaining = goal_required_skill_ids - state
    if not remaining:
        return 0.0
    return sum(learning_cost(skill) for skill in remaining)
```

**Admissibility Proof:**

Let `h*(state)` denote the true minimum remaining cost to reach the goal from
`state`. We show `h(state) <= h*(state)`.

1. **Definition of h:** `h(state) = Σ learning_cost(s)` for each `s` in
   `remaining = goal_required_skill_ids - state`. These are the missing required
   skills.

2. **Any path to the goal must learn each missing required skill at least once.**
   The goal test requires `goal_required_skill_ids ⊆ state`. For each skill `s`
   in `remaining`, `s` is not in `state`, so it must be added to the state at
   some point along any path to the goal. The successor function enforces
   `X not in S`, so each skill is learned at most once. Therefore, each `s` in
   `remaining` contributes exactly `learning_cost(s)` to the path cost.

3. **The actual remaining cost may be higher.** The path to the goal may also
   need to learn **non-required prerequisite skills** (skills that are
   prerequisites of required skills but are not themselves in
   `goal_required_skill_ids`). These skills' costs are NOT included in `h(state)`
   but ARE included in the actual path cost. Therefore:
   ```
   h*(state) = Σ learning_cost(s) for s in remaining
             + Σ learning_cost(p) for non-required prerequisites p
             >= Σ learning_cost(s) for s in remaining
             = h(state)
   ```

4. **Conclusion:** `h(state) <= h*(state)` for all states. The heuristic is
   admissible. A* with an admissible heuristic guarantees finding the optimal
   (minimum-cost) path.

**Consistency (triangle inequality):**

The heuristic is also **consistent** (monotone). For any transition from state
`S` to successor `S'` (acquiring skill `X`):

- If `X` is a required skill: `h(S) = h(S') + learning_cost(X)`, because `X` is
  in `remaining` for `S` but not for `S'`. So `h(S) = cost(X) + h(S')`, which
  satisfies `h(S) <= cost(X) + h(S')` with equality.
- If `X` is a non-required prerequisite: `h(S) = h(S')`, because `X` was not in
  `remaining` for either state. So `h(S) = 0 + h(S') <= cost(X) + h(S')`.

In both cases, `h(S) <= cost(X) + h(S')`, which is the consistency condition.
A consistent heuristic is always admissible, and consistency guarantees that A*
never needs to re-expand a node (the closed set is safe).

**Trade-off acknowledged:** `h` is a relaxed lower bound — it ignores
prerequisite chains. This means `h` can be a loose lower bound when missing
required skills have many non-required prerequisites, making A* behave closer to
Dijkstra (less pruning). This is an acceptable trade-off for a small skill graph
(50-100 skills, pruned to role-relevant subset). A tighter heuristic (e.g.,
including prerequisite costs) risks inadmissibility and is not worth the
complexity for this scope.

### 6.9 f(n) = g(n) + h(n)

```python
def f(state) -> float:
    return g(state) + h(state)
```

A* expands the state with the lowest f(n) first.

### 6.10 A* Search Algorithm

**Status:** Recommendation (genuine implementation)

```python
import heapq

def a_star_search(graph, start_state, goal_test, g_func, h_func):
    """
    Genuine A* Search implementation.

    Args:
        graph: SkillGraph with nodes and edges
        start_state: frozenset of skill_ids the student currently knows
        goal_test: function(state) -> bool
        g_func: function(state) -> float (accumulated path cost)
        h_func: function(state) -> float (heuristic estimate)

    Returns:
        path: list of (skill_id, cost) tuples from start to goal, or None if no path
    """
    # Priority queue: (f_score, tie_breaker, state)
    # tie_breaker ensures deterministic ordering when f_scores are equal
    open_list = []
    counter = 0
    heapq.heappush(open_list, (h_func(start_state), counter, start_state))

    # Maps state → (g_score, parent_state, skill_learned)
    # g_score is the accumulated path cost to reach this state
    came_from = {start_state: (0.0, None, None)}

    # Set of fully explored states
    closed_set = set()

    while open_list:
        current_f, _, current_state = heapq.heappop(open_list)

        # Goal check
        if goal_test(current_state):
            return reconstruct_path(came_from, current_state)

        # Skip if already processed (handles duplicate entries in open list)
        if current_state in closed_set:
            continue
        closed_set.add(current_state)

        # Expand neighbors
        for skill_id, successor_state, cost in get_successors(graph, current_state):
            if successor_state in closed_set:
                continue

            # g is the accumulated path cost: g(current) + cost of new skill
            tentative_g = came_from[current_state][0] + cost

            if successor_state not in came_from or tentative_g < came_from[successor_state][0]:
                came_from[successor_state] = (tentative_g, current_state, skill_id)
                f_score = tentative_g + h_func(successor_state)
                counter += 1
                heapq.heappush(open_list, (f_score, counter, successor_state))

    return None  # No path found
```

### 6.11 Path Reconstruction

```python
def reconstruct_path(came_from, goal_state):
    """Trace back from goal to start to build the path."""
    path = []
    current = goal_state
    while came_from[current][1] is not None:
        g_score, parent, skill_learned = came_from[current]
        path.append({
            "skill_id": skill_learned,
            "skill_name": skill_name(skill_learned),
            "cost": g_score - came_from[parent][0],  # Cost of this step
            "cumulative_cost": g_score,                # Total cost so far
            "prerequisites": get_prerequisites(skill_learned),
        })
        current = parent
    path.reverse()
    return path
```

### 6.12 Roadmap Generation from A* Path

**Status:** Recommendation

The A* path (list of skills to learn in order) is converted to a user-friendly
roadmap:

```python
class LearningRoadmapItem:
    order: int                     # Step number (1, 2, 3, ...)
    skill_id: str
    skill_name: str
    category: str
    current_proficiency: str | None  # None for missing skills; the student's
                                      # current level for weak skills (display only)
    target_proficiency: str        # What they should achieve
    prerequisites: list[str]       # Skills that must be completed first
    estimated_hours: float         # Learning cost for this step
    cumulative_hours: float        # Total hours up to this step
    status: str                    # "not_started" | "in_progress" | "completed"
```

> **Revision Note (F-ASTAR-4, MEDIUM):** `current_proficiency` is `None` for
> missing skills (the student doesn't have them). For weak skills, the roadmap
> does NOT include a learning step (A* only plans missing skills). However,
> weak skills may appear in the roadmap as informational context (e.g., "You
> already know SQL at beginner; the role requires intermediate — consider
> improving"). This is display-only and not part of the A* path.

### 6.13 Worked Example

> **Revision Note (F-ASTAR-5, LOW):** The worked example now shows g, h, and f
> separately at each step, with correct computations.

**Student knows:** Python, Git
**Role requires:** Python, SQL, Docker, REST APIs, System Design
**Skill dependencies:** SQL → REST APIs, Linux → Docker, Docker → System Design
**Learning costs:** SQL=20h, REST APIs=15h, Linux=10h, Docker=15h, System Design=25h

**Missing required skills:** SQL, Docker, REST APIs, System Design (Linux is a
non-required prerequisite of Docker)

**Start state:** `{"python", "git"}`
**Goal:** `{"sql", "docker", "rest_apis", "system_design"} ⊆ state`

```
Initial: state = {"python", "git"}
  g = 0
  h = 20 + 15 + 15 + 25 = 75  (sum of missing required skills' costs)
  f = 0 + 75 = 75

Step 1: Learn SQL (cost 20h, no prerequisites needed)
  state = {"python", "git", "sql"}
  g = 0 + 20 = 20
  h = 15 + 15 + 25 = 55  (REST APIs, Docker, System Design still missing)
  f = 20 + 55 = 75

Step 2: Learn REST APIs (cost 15h, prereq: SQL ✓)
  state = {"python", "git", "sql", "rest_apis"}
  g = 20 + 15 = 35
  h = 15 + 25 = 40  (Docker, System Design still missing)
  f = 35 + 40 = 75

Step 3: Learn Linux (cost 10h, non-required prerequisite of Docker)
  state = {"python", "git", "sql", "rest_apis", "linux"}
  g = 35 + 10 = 45
  h = 15 + 25 = 40  (Linux is NOT a required skill, so h unchanged)
  f = 45 + 40 = 85

Step 4: Learn Docker (cost 15h, prereq: Linux ✓)
  state = {"python", "git", "sql", "rest_apis", "linux", "docker"}
  g = 45 + 15 = 60
  h = 25  (only System Design still missing)
  f = 60 + 25 = 85

Step 5: Learn System Design (cost 25h, prereq: Docker ✓)
  state = {"python", "git", "sql", "rest_apis", "linux", "docker", "system_design"}
  g = 60 + 25 = 85
  h = 0  (all required skills now in state)
  f = 85 + 0 = 85

Goal reached! Total learning cost = 85 hours.
```

**Note on optimality:** A* finds the minimum-total-learning-cost path (85 hours)
subject to prerequisite ordering constraints, given the configured cost model
(learning hours per skill). This is "optimal" with respect to the modeled
learning cost, NOT with respect to real-world educational value. See Section
6.15 for the precise optimality claim.

**Note on h at Step 3:** When Linux (a non-required prerequisite) is learned,
`h` does not decrease because Linux is not in `goal_required_skill_ids`. This
is correct — `h` only counts required skills. The actual cost of learning
Linux (10h) is captured in `g` but not anticipated by `h`, which is why `h`
remains a lower bound (admissible).

### 6.14 How A* Receives Its Input and Produces Its Output

**Status:** Recommendation

**Input assembly:**

1. **Start state:** Module 3 service calls Module 1 service to get the student's
   current skill IDs → `frozenset(skill_ids)`. This includes ALL skills the
   student has, regardless of proficiency level.

2. **Goal state:** Module 3 service calls Module 2 service to get the Skill Gap
   Report → extracts **only `missing_skills`** skill IDs → these form the set
   of skills the student needs to acquire.
   - **Weak skills are NOT included** in the goal. A weak skill's ID is already
     in the start state (the student has it at some proficiency), so adding it
     to the goal would make the goal test pass immediately without generating
     any learning step. Weak-skill proficiency upgrades are handled by Module 4.

3. **Graph:** Module 3 service loads `SkillDependency` data from the database
   (or `data/skill-relationships/dependencies.json`) → builds `SkillGraph` with
   nodes and edges.

4. **Costs:** Each skill's `learning_cost_hours` comes from the `Skill` table
   (seeded from `data/skills/skills.json`).

**A* execution:**

5. The `a_star_search()` function is called with `start_state`, `goal_test`,
   `g_func`, `h_func`, and the `SkillGraph`.
6. A* explores the state space using the priority queue, expanding states with
   the lowest f(n) first.
7. When the goal test passes, `reconstruct_path()` traces back from the goal
   state to the start state, producing an ordered list of (skill_id, cost) pairs.

**Output formatting:**

8. The `RoadmapGenerator` converts the A* path into `LearningRoadmapItem`
   objects with order numbers, prerequisites, estimated hours, and cumulative
   hours.
9. The roadmap is persisted to the `learning_roadmaps` and `roadmap_items`
   tables.
10. The roadmap is returned to the frontend as a `LearningRoadmap` response.

### 6.15 Optimality Claim (Precise Statement)

> **Revision Note (F-ASTAR-3, MEDIUM):** The optimality claim is now precisely
> stated. A* finds the minimum modeled learning cost, not "real-world learning
> optimality."

**Status:** Recommendation

A* with an admissible and consistent heuristic guarantees finding the
**minimum-total-learning-cost path** from the start state to the goal state,
where:

- **Cost** = sum of `learning_cost_hours` for each skill learned along the path.
- **Path** = an ordered sequence of skill acquisitions.
- **Constraints** = prerequisite ordering (a skill can only be learned after all
  its prerequisites are in the state).

This is "optimal" **with respect to the modeled learning cost** (configured
learning hours per skill). It is NOT a claim about:

- Real-world educational effectiveness of the learning order.
- Pedagogical optimality (some students may learn better with different orders).
- Time-to-completion in real life (actual learning time varies by student).

The optimality guarantee holds because:
1. The heuristic is admissible (never overestimates — see proof in Section 6.8).
2. The heuristic is consistent (satisfies the triangle inequality — see Section 6.8).
3. A* with a consistent heuristic is guaranteed to find the optimal path without
   re-expanding nodes.

### 6.16 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Graph representation | DAG with adjacency dict | Efficient neighbor lookup for A* |
| State representation | frozenset of skill_ids (binary) | Hashable, efficient set operations, immutable; sufficient for 4-week scope |
| Heuristic | Sum of missing required skills' base costs | Admissible, consistent, simple to compute; does not include prerequisite costs |
| Cost model | Configurable learning hours per skill (single scalar) | Transparent, adjustable, meaningful; no edge costs |
| Goal condition | Set inclusion test (missing skills only) | Flexible — any state superset of missing required skills qualifies |
| Open list | Min-heap (heapq) with tie-breaker counter | Standard priority queue for A*; deterministic ordering |
| Closed set | Python set | O(1) membership check |
| Algorithm location | `modules/module-3-learning-intelligence/astar/` | Pure, testable, academically defensible |
| Orchestration location | `backend/app/services/module3/` | Handles DB, persistence, API integration |
| Weak skills | NOT planned by A*; handled by Module 4 | Binary state cannot represent proficiency; keeps A* scope manageable |
| edge_cost | Removed from SkillEdge | Prerequisites constrain ordering only; no extra cost; keeps optimality claim precise |

---

## 7. Module 4 — Career Readiness (Forward Chaining)

### 7.1 CRITICAL: Forward Chaining Must Be Genuine

**Status:** Requirement (from AGENTS.md Section 3 and PROJECT_SPEC.md Section 8)

The Forward Chaining implementation must contain:
- Facts (structured representations)
- Rules (IF-THEN format)
- Working memory
- Rule matching and firing
- Iterative inference until no new rules fire
- Explainable conclusions (inference trace)

The implementation must NOT be a fake that simply checks thresholds with if/else
statements. It must be a genuine inference engine that loads facts into working
memory, matches rules against working memory, fires matching rules, adds
conclusions to working memory, and repeats until no more rules can fire.

> **Revision Note (F-FC-1, HIGH):** Forward Chaining is now the **SOLE
> mechanism** that determines the readiness classification (Role Ready / Nearly
> Ready / Needs Improvement). The readiness score (0-100) is a numeric measure
> displayed as supporting evidence; it does NOT independently classify the
> student. The score-threshold if/else classification (former Section 7.10)
> has been **removed entirely**. The rule thresholds are aligned with the
> PROJECT_SPEC.md Section 6 score ranges (80-100, 60-79, 0-59) so that the
> rules and the score agree in normal cases, but the rule is authoritative.

### 7.2 Fact Representation

**Status:** Recommendation

Facts are key-value pairs representing known information about the student.

```python
class Fact:
    key: str           # e.g., "skill_coverage_percent"
    value: Any          # e.g., 75.0
    source: str         # How this fact was derived (e.g., "computed", "student_profile")
    timestamp: datetime
```

**Fact Categories:**

```python
# Skill facts
Fact("python_proficiency", "advanced")
Fact("sql_proficiency", "intermediate")
Fact("docker_proficiency", "beginner")
Fact("total_skills_acquired", 8)
Fact("total_skills_required", 12)

# Coverage facts (consumed from SkillGapReport, NOT recomputed by Module 4)
Fact("skill_coverage_percent", 66.7)         # From Module 2's SkillGapReport
Fact("core_skill_coverage_percent", 75.0)    # From Module 2's SkillGapReport
Fact("critical_skill_coverage_percent", 80.0) # From Module 2's SkillGapReport

# Proficiency facts
Fact("average_proficiency", 2.1)             # 1-3 scale (MAX_PROFICIENCY_LEVEL = 3)
Fact("min_core_proficiency", 2)              # Lowest proficiency among core skills
Fact("advanced_skills_count", 3)

# Progress facts (from roadmap_items.status - the authoritative progress source)
Fact("learning_progress_percent", 60.0)      # (completed_items / total_items) * 100
Fact("skills_completed", 5)
Fact("skills_in_progress", 2)
Fact("skills_not_started", 5)

# Experience facts (from the projects table)
Fact("has_projects", True)
Fact("project_count", 3)
Fact("has_resume", True)

# Readiness score (computed by the weighted factor formula, exposed as a fact)
Fact("readiness_score", 72.5)               # Computed BEFORE Forward Chaining runs
```

> **Revision Note (F-MOD-1, MEDIUM):** Coverage facts
> (`skill_coverage_percent`, `core_skill_coverage_percent`,
> `critical_skill_coverage_percent`) are now **consumed from Module 2's
> `SkillGapReport`** contract rather than recomputed by Module 4. Module 4's
> fact generator reads these precomputed values from the contract.
>
> **Revision Note (F-DB-1, MEDIUM):** Progress facts are derived from
> `roadmap_items.status` (the authoritative progress state), not from a
> separate `learning_progress` table.
>
> **Revision Note (F-SCORE-1, MEDIUM):** The `has_projects` fact remains for
> rule conditions, but the scoring formula now uses a graded experience factor
> based on `project_count` (see Section 7.9).

### 7.3 Rule Representation

> **Revision Note (F-FC-2, HIGH):** The `contributes_to_score` field has been
> **removed** from the `Conclusion` schema. Rules assert facts into working
> memory; they do NOT contribute to the score. The score is computed solely by
> the weighted factor formula (Section 7.9). This eliminates the dual scoring
> model inconsistency.

**Status:** Recommendation

Rules use an IF-THEN structure with conditions on facts.

```python
class Rule:
    id: str
    name: str
    conditions: list[Condition]     # ALL must be true (AND logic)
    conclusion: Conclusion          # What to assert if conditions are met
    priority: int                   # Higher = evaluated first
    explanation_template: str       # Human-readable explanation

class Condition:
    fact_key: str
    operator: str                   # ">=" | "<=" | "==" | ">" | "<" | "!="
    value: Any

class Conclusion:
    fact_key: str
    fact_value: Any                 # What to assert into working memory
    # NOTE: contributes_to_score has been REMOVED (F-FC-2).
    # Rules assert facts; they do not contribute to the score.
    # The score is computed by the weighted factor formula (Section 7.9).
```

### 7.4 Rule Base (Configurable)

> **Revision Note (F-FC-3, MEDIUM):** The rule base now includes **genuine
> multi-step inference chains**. Intermediate rules derive facts (e.g.,
> `core_skills_satisfied`, `progress_on_track`) that enable downstream
> classification rules. This makes the Forward Chaining engine demonstrate
> real multi-step inference, not just single-step if/else classification.
>
> **Revision Note (F-FC-2, HIGH):** All `contributes_to_score` fields have been
> removed from the example rules.
>
> **Revision Note (F-FC-1, HIGH):** Rule thresholds are aligned with
> PROJECT_SPEC.md Section 6 score ranges (80-100 -> Role Ready, 60-79 ->
> Nearly Ready, 0-59 -> Needs Improvement) so that the rules and the score
> agree in normal cases. Forward Chaining is the sole classification authority.

**Status:** Recommendation

Rules are stored in `data/rules/readiness_rules.json` and can be modified without
code changes. This satisfies the PROJECT_SPEC requirement: "The exact thresholds
and rules must be configurable rather than hard-coded throughout the application."

```json
{
  "rules": [
    {
      "id": "rule_core_skills_satisfied",
      "name": "Core Skills Satisfied",
      "conditions": [
        {"fact_key": "core_skill_coverage_percent", "operator": ">=", "value": 90},
        {"fact_key": "min_core_proficiency", "operator": ">=", "value": 2}
      ],
      "conclusion": {
        "fact_key": "core_skills_satisfied",
        "fact_value": true
      },
      "priority": 100,
      "explanation_template": "Core skill coverage is {core_skill_coverage_percent}% with minimum proficiency {min_core_proficiency}, satisfying core skill requirements."
    },
    {
      "id": "rule_progress_on_track",
      "name": "Learning Progress On Track",
      "conditions": [
        {"fact_key": "learning_progress_percent", "operator": ">=", "value": 70}
      ],
      "conclusion": {
        "fact_key": "progress_on_track",
        "fact_value": true
      },
      "priority": 90,
      "explanation_template": "Learning progress is {learning_progress_percent}%, indicating the student is on track with their roadmap."
    },
    {
      "id": "rule_role_ready",
      "name": "Role Ready Classification",
      "conditions": [
        {"fact_key": "core_skills_satisfied", "operator": "==", "value": true},
        {"fact_key": "progress_on_track", "operator": "==", "value": true},
        {"fact_key": "skill_coverage_percent", "operator": ">=", "value": 80}
      ],
      "conclusion": {
        "fact_key": "readiness_classification",
        "fact_value": "role_ready"
      },
      "priority": 80,
      "explanation_template": "Core skills are satisfied, learning progress is on track, and overall skill coverage is {skill_coverage_percent}%, meeting all thresholds for Role Ready."
    },
    {
      "id": "rule_nearly_ready",
      "name": "Nearly Ready Classification",
      "conditions": [
        {"fact_key": "skill_coverage_percent", "operator": ">=", "value": 60},
        {"fact_key": "learning_progress_percent", "operator": ">=", "value": 50}
      ],
      "conclusion": {
        "fact_key": "readiness_classification",
        "fact_value": "nearly_ready"
      },
      "priority": 70,
      "explanation_template": "Skill coverage is {skill_coverage_percent}% and learning progress is {learning_progress_percent}%, meeting thresholds for Nearly Ready."
    },
    {
      "id": "rule_needs_improvement_default",
      "name": "Needs Improvement (Default)",
      "conditions": [],
      "conclusion": {
        "fact_key": "readiness_classification",
        "fact_value": "needs_improvement"
      },
      "priority": 10,
      "explanation_template": "Current skill coverage ({skill_coverage_percent}%) and learning progress ({learning_progress_percent}%) do not yet meet the thresholds for higher classifications."
    }
  ]
}
```

**Multi-step inference chain explanation (F-FC-3):**

The rule base now contains a genuine multi-step inference chain:

1. **Step 1:** `rule_core_skills_satisfied` fires if `core_skill_coverage_percent >= 90`
   AND `min_core_proficiency >= 2`. It asserts `core_skills_satisfied = true`
   into working memory.

2. **Step 2:** `rule_progress_on_track` fires if `learning_progress_percent >= 70`.
   It asserts `progress_on_track = true` into working memory.

3. **Step 3:** `rule_role_ready` fires if `core_skills_satisfied == true` (derived
   in Step 1) AND `progress_on_track == true` (derived in Step 2) AND
   `skill_coverage_percent >= 80`. It asserts
   `readiness_classification = "role_ready"`.

This is a genuine forward chain: `rule_role_ready`'s conditions depend on facts
**derived by inference** (`core_skills_satisfied`, `progress_on_track`), not just
on raw input facts. An examiner can verify that the engine performs multi-step
inference, not just single-step if/else.

> **Revision Note (F-FC-4, LOW):** The default rule
> (`rule_needs_improvement_default`) has **empty conditions** (`conditions: []`),
> which means it is **always applicable**. It must have the **lowest priority**
> (priority 10) so it only fires when no other classification rule fires. The
> engine fires the highest-priority applicable rule first and marks rules as
> fired, so the default rule will only fire after higher-priority classification
> rules have either fired or been found inapplicable. **Do not change the engine
> to fire-all-applicable without also changing this rule's semantics** - if all
> applicable rules fired per iteration, the default rule would fire alongside a
> higher classification, overwriting it.

**Note:** The `rule_needs_improvement_default` has NO conditions - it acts as a
default/fallback that fires when no other classification rule fires. This ensures
a classification is always produced.

### 7.5 Forward Chaining Engine

**Status:** Recommendation (genuine implementation)

```python
class ForwardChainingEngine:
    """
    Genuine Forward Chaining inference engine.

    Algorithm:
    1. Load all facts into working memory
    2. Load all rules from the rule base
    3. Repeat:
       a. Find all rules whose conditions are satisfied by current working memory
          AND that have not yet fired
       b. Among those, select the rule with highest priority
       c. If no rule can fire, stop
       d. Fire the rule: add its conclusion to working memory
       e. Record which rule fired and what it concluded
       f. Mark the rule as fired (each rule fires at most once)
    4. Return final working memory state and inference trace

    The engine supports multi-step inference: a rule's conclusion becomes
    a new fact in working memory, which may enable another rule's conditions
    in a subsequent iteration.
    """

    def __init__(self, facts: dict, rules: list[Rule]):
        self.working_memory = dict(facts)     # Copy of initial facts
        self.rules = rules
        self.fired_rules = []                  # Trace of fired rules
        self.inference_trace = []              # Step-by-step log

    def run(self) -> InferenceResult:
        fired_ids = set()

        while True:
            # Find all applicable rules (conditions met, not yet fired)
            applicable = []
            for rule in self.rules:
                if rule.id in fired_ids:
                    continue
                if self._conditions_met(rule):
                    applicable.append(rule)

            if not applicable:
                break  # No more rules can fire -> STOP

            # Select highest priority rule
            next_rule = max(applicable, key=lambda r: r.priority)

            # Fire the rule
            self._fire_rule(next_rule)
            fired_ids.add(next_rule.id)

        return InferenceResult(
            working_memory=self.working_memory,
            inference_trace=self.inference_trace,
            fired_rules=self.fired_rules
        )

    def _conditions_met(self, rule: Rule) -> bool:
        """Check if ALL conditions of a rule are satisfied."""
        # An empty conditions list returns True (always applicable).
        # This is used by the default rule (F-FC-4).
        for condition in rule.conditions:
            fact_value = self.working_memory.get(condition.fact_key)
            if fact_value is None:
                return False
            if not self._evaluate(fact_value, condition.operator, condition.value):
                return False
        return True

    def _evaluate(self, actual, operator, expected) -> bool:
        """Evaluate a single condition."""
        ops = {
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            ">":  lambda a, b: a > b,
            "<":  lambda a, b: a < b,
            "!=": lambda a, b: a != b,
        }
        return ops[operator](actual, expected)

    def _fire_rule(self, rule: Rule):
        """Fire a rule: add conclusion to working memory, record trace.
        
        CLASSIFICATION-OVERWRITE GUARD (F-NEW-1 fix):
        Once a readiness_classification has been asserted, no other rule
        may overwrite it. The first classification rule to fire is
        authoritative. This prevents lower-priority classification rules
        from overwriting a higher-priority classification.
        """
        # Guard: do not overwrite an already-asserted readiness classification
        if (rule.conclusion.fact_key == "readiness_classification"
                and "readiness_classification" in self.working_memory):
            return  # Classification already determined; skip this rule

        self.working_memory[rule.conclusion.fact_key] = rule.conclusion.fact_value
        self.fired_rules.append(rule)
        self.inference_trace.append({
            "rule_id": rule.id,
            "rule_name": rule.name,
            "conclusion": {rule.conclusion.fact_key: rule.conclusion.fact_value},
            "explanation": rule.explanation_template
        })
```

> **Revision Note (F-NEW-1, HIGH):** Added a classification-overwrite guard
> to `_fire_rule()`. Once `readiness_classification` has been asserted in
> working memory, any subsequent rule whose conclusion targets the same fact
> key is skipped. This ensures the first (highest-priority) classification
> rule to fire is authoritative. Without this guard, lower-priority
> classification rules would overwrite the higher-priority conclusion,
> always producing "needs_improvement" regardless of facts. The guard is
> engine-level (not rule-condition-level) because it is simpler, more
> robust, and does not require changes to every classification rule.

### 7.6 Forward Chaining Process Diagram

> **Revision Note (F-FC-2, HIGH):** The process diagram no longer shows the
> score being computed by summing rule contributions. The score is computed by
> the weighted factor formula (Section 7.9) BEFORE Forward Chaining runs, and
> is exposed as a fact (`readiness_score`) for potential use in rule conditions.
>
> **Revision Note (F-FC-3, MEDIUM):** The diagram now shows a genuine
> multi-step inference chain: intermediate rules derive facts that enable
> downstream classification rules.

```
+--------------------------------------------------+
|              INITIAL FACTS                        |
|  skill_coverage_percent = 85.0                   |
|  core_skill_coverage_percent = 92.0              |
|  critical_skill_coverage_percent = 88.0          |
|  min_core_proficiency = 2                        |
|  learning_progress_percent = 75.0                 |
|  has_projects = True                             |
|  project_count = 3                               |
|  readiness_score = 78.5  (computed by formula)   |
|  total_skills_acquired = 10                       |
|  total_skills_required = 12                       |
+----------------------+---------------------------+
                       |
                       v
+--------------------------------------------------+
|  ITERATION 1                                      |
|  EVALUATE: rule_core_skills_satisfied (pri 100)  |
|  core_skill_coverage >= 90?  92.0 >= 90 -> YES     |
|  min_core_proficiency >= 2?  2 >= 2 -> YES         |
|  ALL conditions met -> FIRE                        |
|                                                   |
|  Assert: core_skills_satisfied = true             |
|  Record explanation                               |
+----------------------+---------------------------+
                       |
                       v
+--------------------------------------------------+
|  ITERATION 2                                      |
|  EVALUATE: rule_progress_on_track (pri 90)        |
|  learning_progress >= 70?  75.0 >= 70 -> YES       |
|  ALL conditions met -> FIRE                        |
|                                                   |
|  Assert: progress_on_track = true                 |
|  Record explanation                               |
+----------------------+---------------------------+
                       |
                       v
+--------------------------------------------------+
|  ITERATION 3                                      |
|  EVALUATE: rule_role_ready (pri 80)               |
|  core_skills_satisfied == true?  YES (from iter 1)|
|  progress_on_track == true?  YES (from iter 2)    |
|  skill_coverage >= 80?  85.0 >= 80 -> YES          |
|  ALL conditions met -> FIRE                        |
|                                                   |
|  Assert: readiness_classification = "role_ready"  |
|  Record explanation                               |
+----------------------+---------------------------+
                       |
                       v
+--------------------------------------------------+
|  ITERATION 4                                      |
|  EVALUATE: rule_nearly_ready (pri 70)             |
|  skill_coverage >= 60?  85.0 >= 60 -> YES         |
|  learning_progress >= 50?  75.0 >= 50 -> YES      |
|  ALL conditions met -> BUT:                       |
|  GUARD: readiness_classification already set      |
|         ("role_ready" from iteration 3)           |
|  -> SKIP (F-NEW-1 guard: no overwrite)           |
|                                                   |
|  EVALUATE: rule_needs_improvement_default (pri 10)|
|  Conditions: empty (always applicable)            |
|  GUARD: readiness_classification already set      |
|         ("role_ready" from iteration 3)           |
|  -> SKIP (F-NEW-1 guard: no overwrite)           |
|                                                   |
|  No more NEW rules can fire -> STOP                |
|                                                   |
|  Final classification: "Role Ready" (from FC)    |
|  Score: 78.5/100 (supporting evidence, from       |
|          weighted factor formula)                 |
|  Explanation: generated from inference trace       |
+--------------------------------------------------+
```

**Note on the example:** In this example, the FC classification is "Role Ready"
while the score is 78.5 (which would fall in the "Nearly Ready" range if the
score were the classifier). This demonstrates that FC is the sole classification
authority - the score is supporting evidence only. In practice, the rule
thresholds are aligned with the score ranges so they usually agree, but FC is
authoritative when they diverge. The explanation must clearly state which rules
fired and why.

### 7.7 How Facts Enter the Forward Chaining Engine

> **Revision Note (F-MOD-1, MEDIUM):** The fact generator now **consumes**
> coverage metrics from Module 2's `SkillGapReport` contract instead of
> recomputing them. This keeps coverage logic in Module 2 as the single source
> of truth.
>
> **Revision Note (F-DB-1, MEDIUM):** Progress facts are derived from
> `roadmap_items.status` (the authoritative progress state), not from a
> separate `learning_progress` table.
>
> **Revision Note (F-DB-2, MEDIUM):** Experience facts (`has_projects`,
> `project_count`) are now derived from the `projects` table.

**Status:** Recommendation

The fact generation pipeline:

1. **Load student skill profile** (from Module 1 via service interface):
   - Student's current skills and proficiency levels.
   - Compute `average_proficiency` = mean proficiency level across all acquired
     skills (using `MAX_PROFICIENCY_LEVEL = 3` for normalization).
   - Compute `min_core_proficiency` = minimum proficiency among core skills.
   - Compute `advanced_skills_count` = count of skills at advanced level.
   - Generate per-skill proficiency facts (e.g., `python_proficiency = "advanced"`).

2. **Load skill gap report** (from Module 2 via service interface):
   - **Consume** precomputed coverage metrics from the `SkillGapReport` contract:
     - `skill_coverage_percent` (from contract, NOT recomputed)
     - `core_skill_coverage_percent` (from contract, NOT recomputed)
     - `critical_skill_coverage_percent` (from contract, NOT recomputed)
     - `total_skills_acquired` (from contract)
     - `total_skills_required` (from contract)

3. **Load learning roadmap and progress** (from Module 3 via service interface):
   - Load roadmap items and their `status` from `roadmap_items` table
     (authoritative progress source).
   - Compute `learning_progress_percent = (completed_items / total_items) * 100`.
   - Count `skills_completed`, `skills_in_progress`, `skills_not_started`
     from `roadmap_items.status`.

4. **Load projects** (from Module 1 via service interface):
   - Query the `projects` table for this student.
   - `has_projects` = True if student has any projects.
   - `project_count` = number of projects.
   - `has_resume` = True if student has uploaded a resume.

5. **Compute readiness score** (using the weighted factor formula, Section 7.9):
   - The score is computed BEFORE Forward Chaining runs.
   - The score is exposed as a fact (`readiness_score`) so that rules CAN
     reference it in conditions if desired (though the default rule base does
     not use the score in conditions - classification is based on coverage,
     proficiency, and progress facts).

6. **Assemble fact dictionary:**
   ```python
   facts = {
       # Coverage (from Module 2 contract)
       "skill_coverage_percent": 85.0,
       "core_skill_coverage_percent": 92.0,
       "critical_skill_coverage_percent": 88.0,
       "total_skills_acquired": 10,
       "total_skills_required": 12,

       # Proficiency (computed from Module 1 data)
       "average_proficiency": 2.1,
       "min_core_proficiency": 2,
       "advanced_skills_count": 3,

       # Progress (from roadmap_items.status)
       "learning_progress_percent": 75.0,
       "skills_completed": 6,
       "skills_in_progress": 2,
       "skills_not_started": 4,

       # Experience (from projects table)
       "has_projects": True,
       "project_count": 3,
       "has_resume": True,

       # Score (computed by weighted factor formula)
       "readiness_score": 78.5,

       # Per-skill proficiency
       "python_proficiency": "advanced",
       "sql_proficiency": "intermediate",
       "docker_proficiency": "beginner",
   }
   ```

7. **Pass facts to Forward Chaining engine:**
   ```python
   rules = load_rules_from_json("data/rules/readiness_rules.json")
   engine = ForwardChainingEngine(facts, rules)
   result = engine.run()
   ```

### 7.8 How the Final Classification Is Produced

> **Revision Note (F-FC-1, HIGH):** The classification is determined **SOLELY**
> by the Forward Chaining engine. The score is NOT used as a classifier. There
> is no score-threshold if/else. The score is displayed alongside the
> classification as supporting evidence.

**Status:** Recommendation

1. The readiness score is computed from the weighted factor formula (Section 7.9)
   and added to the facts dictionary as `readiness_score`.
2. The Forward Chaining engine runs until no more rules can fire.
3. The engine's working memory now contains the `readiness_classification` fact
   (asserted by whichever classification rule fired - or the default rule).
4. The classification from Forward Chaining is the **sole authoritative
   classification**.
5. The computed score is included as **supporting evidence** (displayed alongside
   the classification).
6. The explanation is generated from the inference trace and factor values.
7. The result is persisted to the `readiness_results` table.

**Important:** The classification is determined **SOLELY** by the Forward
Chaining engine (rule-based). The score provides a numeric measure displayed as
supporting evidence; it does NOT independently classify the student. There is no
score-threshold if/else classification. The rule thresholds are aligned with
the spec's score ranges (80-100, 60-79, 0-59) so they agree in normal cases, but
the rule is authoritative.

### 7.9 Readiness Scoring

> **Revision Note (F-FC-2, HIGH):** The weighted factor formula is the **single
> scoring model**. There is no alternative "sum of rule contributions" model.
> The `contributes_to_score` field has been removed from rules.
>
> **Revision Note (F-SCORE-1, MEDIUM):** The experience factor is now graded
> based on `project_count` instead of a binary `has_projects`. A student with
> more projects gets a higher experience score (capped at 100).
>
> **Revision Note (F-SCORE-2, LOW):** The proficiency normalization uses a
> named constant `MAX_PROFICIENCY_LEVEL = 3` instead of a magic number.

**Status:** Recommendation

The readiness score is computed from multiple measurable factors using a
weighted formula. The score is computed BEFORE Forward Chaining runs and is
exposed as a fact (`readiness_score`) for potential use in rule conditions.

```python
# Defined in backend/app/utils/constants.py
MAX_PROFICIENCY_LEVEL = 3  # beginner=1, intermediate=2, advanced=3

def compute_readiness_score(facts: dict) -> float:
    """
    Compute a 0-100 readiness score from measurable factors.

    This is the SINGLE scoring model. Rules do NOT contribute to the score.
    The score is supporting evidence displayed alongside the FC classification.

    Factors and weights:
    - skill_coverage (30%):       overall skill coverage percentage
    - core_skill_coverage (25%):  core skill coverage percentage
    - proficiency_level (20%):    average proficiency normalized to 0-100
    - learning_progress (15%):    roadmap completion percentage
    - experience (10%):           graded by project count (not binary)
    """
    weights = {
        "skill_coverage": 0.30,
        "core_skill_coverage": 0.25,
        "proficiency_level": 0.20,
        "learning_progress": 0.15,
        "experience": 0.10,
    }

    # Graded experience factor: 0 projects -> 0, 1 -> 33, 2 -> 67, 3+ -> 100
    # (capped at 100). This uses project_count meaningfully (F-SCORE-1).
    project_count = facts.get("project_count", 0)
    experience_score = min(100, project_count * 33)

    score = (
        weights["skill_coverage"] * facts["skill_coverage_percent"] +
        weights["core_skill_coverage"] * facts["core_skill_coverage_percent"] +
        weights["proficiency_level"] * (facts["average_proficiency"] / MAX_PROFICIENCY_LEVEL * 100) +
        weights["learning_progress"] * facts["learning_progress_percent"] +
        weights["experience"] * experience_score
    )

    return round(score, 1)
```

**How the score is exposed to Forward Chaining:**

The score is computed BEFORE the Forward Chaining engine runs and is added to
the facts dictionary:

```python
# In the fact generator (Section 7.7, step 5):
score = compute_readiness_score(facts)
facts["readiness_score"] = score

# Then pass facts (including readiness_score) to the FC engine:
engine = ForwardChainingEngine(facts, rules)
result = engine.run()
```

This allows rules to reference `readiness_score` in their conditions if desired
(e.g., a rule could check `readiness_score >= 80` as an additional condition).
However, the **default rule base** does NOT use the score in rule conditions -
classification is based on coverage, proficiency, and progress facts. The score
is displayed as supporting evidence alongside the classification.

The score is documented in `docs/algorithms.md` and applied consistently.

### 7.10 Classification (Forward Chaining is Sole Authority)

> **Revision Note (F-FC-1, HIGH):** This section replaces the former
> "Classification Thresholds" section (which contained the score-threshold
> if/else). The score-threshold if/else has been **removed**. Forward Chaining
> is the sole classification mechanism.

**Status:** Requirement (from PROJECT_SPEC.md Section 6 and AGENTS.md Section 3)

The readiness classification is determined **SOLELY** by the Forward Chaining
engine. The three classifications are:

```text
Role Ready        -> asserted by rule_role_ready
Nearly Ready      -> asserted by rule_nearly_ready
Needs Improvement -> asserted by rule_needs_improvement_default (fallback)
```

**Alignment with PROJECT_SPEC.md Section 6 score ranges:**

The PROJECT_SPEC defines classification by score ranges:
```text
80-100 -> Role Ready
60-79  -> Nearly Ready
0-59   -> Needs Improvement
```

The rule thresholds are aligned with these ranges:
- `rule_role_ready` requires `skill_coverage_percent >= 80` (aligned with 80-100)
- `rule_nearly_ready` requires `skill_coverage_percent >= 60` (aligned with 60-79)
- `rule_needs_improvement_default` catches everything else (aligned with 0-59)

In normal cases, the FC classification and the score range will agree. If they
diverge (due to rule configuration or additional conditions like
`core_skills_satisfied`), the **Forward Chaining classification is
authoritative**. The score is displayed as supporting evidence.

**Why FC is authoritative (not the score):**

The spec (Section 6) defines the score ranges, but the spec (Section 8) also
requires Forward Chaining as the primary algorithm for Module 4. Making FC the
sole classification authority satisfies both:
- The score ranges inform the rule threshold design (alignment).
- Forward Chaining performs the actual classification (algorithm requirement).
- The score is explainable supporting evidence (spec Section 13).

### 7.11 Explanation Generation

**Status:** Recommendation

The explanation is built from the inference trace:

```python
def generate_explanation(inference_result: InferenceResult, facts: dict) -> str:
    """
    Generate a human-readable explanation of the readiness classification.

    Includes:
    1. The final classification (from Forward Chaining) and score (supporting)
    2. Which factors contributed positively
    3. Which factors are weak
    4. Which rules fired and why (the inference trace)
    5. What the student should improve
    """
    lines = []

    # Classification (from Forward Chaining - sole authority)
    lines.append(f"Readiness Classification: {facts['readiness_classification']}")
    lines.append(f"Readiness Score: {facts['readiness_score']}/100 (supporting evidence)")
    lines.append("")

    # Factors
    lines.append("Factors:")
    lines.append(f"  - Skill Coverage: {facts['skill_coverage_percent']}%")
    lines.append(f"  - Core Skill Coverage: {facts['core_skill_coverage_percent']}%")
    lines.append(f"  - Learning Progress: {facts['learning_progress_percent']}%")
    lines.append(f"  - Average Proficiency: {facts['average_proficiency']}/{MAX_PROFICIENCY_LEVEL}")
    lines.append(f"  - Projects: {facts['project_count']}")
    lines.append("")

    # Inference trace (shows the multi-step reasoning chain)
    lines.append("Reasoning (Forward Chaining inference trace):")
    for step in inference_result.inference_trace:
        lines.append(f"  - Rule '{step['rule_name']}' fired: {step['explanation']}")
    lines.append("")

    # Recommendations
    lines.append("Recommendations:")
    if facts['readiness_classification'] == 'role_ready':
        lines.append("  You are ready for the target role. Consider exploring advanced topics.")
    elif facts['readiness_classification'] == 'nearly_ready':
        lines.append("  Focus on completing your remaining learning roadmap items.")
        lines.append("  Improve proficiency in weak skill areas.")
    else:
        lines.append("  Prioritize completing prerequisite skills.")
        lines.append("  Focus on core skills first.")
        lines.append("  Maintain consistent learning progress.")

    return "\n".join(lines)
```

### 7.12 Key Design Decisions

> **Revision Note (F-FC-1, F-FC-2, F-FC-3, F-SCORE-1):** The key design
> decisions table has been updated to reflect: FC as sole classification
> authority, removal of `contributes_to_score`, multi-step inference chains,
> and graded experience factor.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Fact format | Key-value pairs | Simple, flexible, easy to serialize |
| Rule format | IF-THEN with conditions (AND logic) | Standard production rule format |
| Rule storage | JSON file (`data/rules/readiness_rules.json`) | Configurable without code changes (PROJECT_SPEC requirement) |
| Engine | Priority-ordered forward chaining with multi-step inference | Deterministic, traceable, explainable, genuine inference |
| Default rule | Catch-all with no conditions, lowest priority | Ensures classification always produced; must not be overridden |
| Classification authority | Forward Chaining (SOLE) | Required algorithm; score is supporting evidence only |
| Classification-overwrite guard | Engine-level skip in _fire_rule() | Prevents lower-priority classification rules from overwriting an already-asserted readiness_classification; ensures highest-priority classification is authoritative |
| Scoring model | Weighted factor formula (SINGLE model) | Transparent, adjustable, explainable; no dual scoring model |
| Experience factor | Graded by project_count (0->0, 1->33, 2->67, 3+->100) | Uses project information meaningfully; not binary |
| Proficiency normalization | Named constant `MAX_PROFICIENCY_LEVEL = 3` | Avoids magic numbers; single definition point |
| Coverage metrics | Consumed from Module 2's SkillGapReport | Single source of truth; Module 4 does not recompute |
| Progress source | `roadmap_items.status` (authoritative) | Single source of truth; no duplication |
| Explanation | Template + inference trace | Shows multi-step reasoning chain and why classification was reached |
| Algorithm location | `modules/module-4-career-readiness/forward-chaining/` | Pure, testable, academically defensible |
| Orchestration location | `backend/app/services/module4/` | Handles DB, persistence, API integration |

---

## 8. Database Design

### 8.1 Database Choice

**Status:** Recommendation

SQLite via SQLAlchemy 2.0 ORM. The ORM abstraction allows migration to PostgreSQL
by changing only the connection string.

### 8.2 Entity Definitions

#### 8.2.1 Student

```sql
CREATE TABLE students (
    id TEXT PRIMARY KEY,              -- UUID
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    education_institution TEXT,
    education_degree TEXT,
    education_year INTEGER,
    interests TEXT,                   -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 8.2.2 Resume

```sql
CREATE TABLE resumes (
    id TEXT PRIMARY KEY,              -- UUID
    student_id TEXT NOT NULL,         -- FK -> students.id
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,          -- pdf, docx, txt
    file_size INTEGER,
    extracted_text TEXT,              -- Raw extracted text
    processing_status TEXT DEFAULT 'pending',  -- pending, processed, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id)
);
```

#### 8.2.3 Project

> **Revision Note (F-DB-2, MEDIUM):** Added the `projects` table. Projects are
> an explicit Module 1 input (PROJECT_SPEC.md Section 3) and are used by Module 4
> facts (`has_projects`, `project_count`). Previously, projects had no storage
> location in the schema.

```sql
CREATE TABLE projects (
    id TEXT PRIMARY KEY,              -- UUID
    student_id TEXT NOT NULL,         -- FK -> students.id
    title TEXT NOT NULL,
    description TEXT,
    technologies TEXT,                -- JSON array of skill IDs or names
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id)
);
```

#### 8.2.4 Skill

```sql
CREATE TABLE skills (
    id TEXT PRIMARY KEY,              -- Canonical skill ID (e.g., "python")
    name TEXT NOT NULL,
    category TEXT NOT NULL,           -- programming, framework, devops, database, etc.
    description TEXT,
    learning_cost_hours REAL,         -- Base learning cost for A*
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 8.2.5 StudentSkill

> **Revision Note (F-API-2, LOW):** Added `resume_id` foreign key to track
> which resume produced which skill, enabling clean re-extraction. Reprocessing
> a resume deletes prior `source = 'resume'` skills for that student and
> re-inserts fresh ones. Self-reported skills are preserved.

```sql
CREATE TABLE student_skills (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,         -- FK -> students.id
    skill_id TEXT NOT NULL,           -- FK -> skills.id
    proficiency TEXT NOT NULL,        -- beginner, intermediate, advanced
    source TEXT NOT NULL,             -- resume, self_reported, inferred
    confidence REAL,                  -- 0.0 to 1.0
    resume_id TEXT,                   -- FK -> resumes.id (nullable; set when source='resume')
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id),
    FOREIGN KEY (resume_id) REFERENCES resumes(id),
    UNIQUE(student_id, skill_id)
);
```

#### 8.2.6 CareerRole

```sql
CREATE TABLE career_roles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 8.2.7 RoleSkill

```sql
CREATE TABLE role_skills (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,            -- FK -> career_roles.id
    skill_id TEXT NOT NULL,           -- FK -> skills.id
    minimum_proficiency TEXT NOT NULL,
    priority TEXT NOT NULL,           -- critical, important, nice_to_have
    is_core BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (role_id) REFERENCES career_roles(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id),
    UNIQUE(role_id, skill_id)
);
```

#### 8.2.8 SkillDependency

```sql
CREATE TABLE skill_dependencies (
    id TEXT PRIMARY KEY,
    skill_id TEXT NOT NULL,           -- The skill that has a prerequisite
    prerequisite_id TEXT NOT NULL,    -- The prerequisite skill
    dependency_type TEXT DEFAULT 'hard',  -- hard (required) or soft (recommended)
    FOREIGN KEY (skill_id) REFERENCES skills(id),
    FOREIGN KEY (prerequisite_id) REFERENCES skills(id),
    UNIQUE(skill_id, prerequisite_id)
);
```

#### 8.2.9 GapReport

> **Revision Note (F-API-1, LOW):** Added the `gap_reports` table to persist
> gap analysis results. This resolves the ambiguity between the API
> (`GET /gap-analysis` implies persistence) and the schema (no table existed).
> Gap reports are now persisted and `GET /gap-analysis` reads the latest
> persisted report.

```sql
CREATE TABLE gap_reports (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,         -- FK -> students.id
    role_id TEXT NOT NULL,            -- FK -> career_roles.id
    report_data TEXT NOT NULL,        -- JSON: full SkillGapReport (including coverage metrics)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (role_id) REFERENCES career_roles(id)
);
```

#### 8.2.10 LearningRoadmap

> **Revision Note (F-DB-4, LOW):** Added a note on supersession semantics.
> Generating a new roadmap for the same student+role supersedes (deactivates)
> prior active roadmaps. This prevents multiple active roadmaps for the same
> student+role, which would make "the" roadmap ambiguous for Module 4.

```sql
CREATE TABLE learning_roadmaps (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,         -- FK -> students.id
    role_id TEXT NOT NULL,            -- FK -> career_roles.id
    total_estimated_hours REAL,
    total_items INTEGER,
    completed_items INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',     -- active, completed, abandoned, superseded
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (role_id) REFERENCES career_roles(id)
);

-- Supersession semantics: When a new roadmap is generated for a student+role,
-- all prior 'active' roadmaps for that student+role are set to 'superseded'.
-- This ensures only one active roadmap exists per student+role at a time.
-- Application-level enforcement (in the service layer) is recommended since
-- SQLite partial unique indexes have limited support.
```

#### 8.2.11 RoadmapItem

> **Revision Note (F-DB-1, MEDIUM):** `roadmap_items.status` is now the
> **authoritative progress state**. The `started_at` and `completed_at`
> fields support progress tracking. The separate `learning_progress` table
> has been repurposed as an append-only audit log (Section 8.2.12).

```sql
CREATE TABLE roadmap_items (
    id TEXT PRIMARY KEY,
    roadmap_id TEXT NOT NULL,         -- FK -> learning_roadmaps.id
    skill_id TEXT NOT NULL,           -- FK -> skills.id
    order_index INTEGER NOT NULL,     -- Step number in the roadmap
    current_proficiency TEXT,         -- Student's current level (display only)
    target_proficiency TEXT NOT NULL,
    estimated_hours REAL,
    cumulative_hours REAL,
    status TEXT DEFAULT 'not_started',  -- not_started, in_progress, completed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (roadmap_id) REFERENCES learning_roadmaps(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id)
);
```

#### 8.2.12 ProgressAuditLog

> **Revision Note (F-DB-1, MEDIUM):** The former `learning_progress` table has
> been repurposed as an **append-only audit log**. `roadmap_items.status` is
> the authoritative progress state. This table records progress update events
> for audit/history purposes, not as a second source of current progress.

```sql
CREATE TABLE progress_audit_log (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,         -- FK -> students.id
    roadmap_id TEXT NOT NULL,         -- FK -> learning_roadmaps.id
    roadmap_item_id TEXT NOT NULL,    -- FK -> roadmap_items.id
    skill_id TEXT NOT NULL,           -- FK -> skills.id
    previous_status TEXT,             -- not_started, in_progress, completed
    new_status TEXT NOT NULL,         -- not_started, in_progress, completed
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (roadmap_id) REFERENCES learning_roadmaps(id),
    FOREIGN KEY (roadmap_item_id) REFERENCES roadmap_items(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id)
);
```

#### 8.2.13 ReadinessResult

```sql
CREATE TABLE readiness_results (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    role_id TEXT NOT NULL,
    readiness_score REAL NOT NULL,           -- 0-100 (supporting evidence)
    classification TEXT NOT NULL,             -- role_ready, nearly_ready, needs_improvement
                                             -- (determined SOLELY by Forward Chaining)
    skill_coverage_percent REAL,
    core_skill_coverage_percent REAL,
    learning_progress_percent REAL,
    average_proficiency REAL,
    explanation TEXT,                         -- Full explanation text
    inference_trace TEXT,                     -- JSON trace of Forward Chaining steps
    fired_rules TEXT,                         -- JSON list of rules that fired
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (role_id) REFERENCES career_roles(id)
);
```

> **Revision Note (F-DB-3, LOW):** The `readiness_rules` table has been
> **removed** from the initial schema. Rules are loaded from the JSON file
> (`data/rules/readiness_rules.json`), which is the sole source of truth.
> A database table for rules can be added later if runtime rule editing is
> designed. This removes unused dead schema and eliminates ambiguity about
> which source the engine loads from.

### 8.3 Entity Relationship Diagram

> **Revision Note (F-DB-2, MEDIUM):** Added `Project` entity to the ER diagram.
> **Revision Note (F-DB-1, MEDIUM):** Replaced `LearningProgress` with
> `ProgressAuditLog` (append-only). **Revision Note (F-API-1, LOW):** Added
> `GapReport` entity. **Revision Note (F-DB-3, LOW):** Removed `ReadinessRule`
> entity.

```
Student --1:N--> Resume
Student --1:N--> Project
Student --1:N--> StudentSkill <--N:1-- Skill
CareerRole --1:N--> RoleSkill <--N:1-- Skill
Skill --1:N--> SkillDependency (self-referencing)
Student --1:N--> GapReport --N:1--> CareerRole
Student --1:N--> LearningRoadmap --1:N--> RoadmapItem <--N:1-- Skill
Student --1:N--> ProgressAuditLog
Student --1:N--> ReadinessResult --N:1--> CareerRole
```

### 8.4 Indexing Recommendations

| Table | Index | Reason |
|-------|-------|--------|
| student_skills | (student_id, skill_id) | Frequent lookups by student |
| role_skills | (role_id) | Load all skills for a role |
| skill_dependencies | (skill_id) | Load prerequisites for A* graph |
| roadmap_items | (roadmap_id, order_index) | Ordered roadmap display |
| roadmap_items | (roadmap_id, status) | Progress aggregation by status |
| progress_audit_log | (student_id, roadmap_id) | Audit log queries |
| gap_reports | (student_id, role_id, created_at) | Latest gap report lookup |
| readiness_results | (student_id, role_id, created_at) | Latest readiness check |
| projects | (student_id) | Project lookup for facts |

### 8.5 Key Design Decisions

> **Revision Note (F-DB-1, F-DB-2, F-DB-3, F-DB-4):** Updated to reflect:
> Project entity added, progress audit log replaces learning_progress,
> readiness_rules table removed, roadmap supersession semantics documented.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ORM | SQLAlchemy 2.0 | Python-native, migration-ready, well-tested |
| IDs | UUIDs (TEXT in SQLite) | Globally unique, safe for distributed future |
| Skill IDs | String slugs (e.g., "python") | Human-readable, used in JSON data files |
| Timestamps | created_at / updated_at | Audit trail |
| JSON fields | For conditions, interests, traces, report data | Flexible structured data without extra tables |
| Proficiency | String enum (beginner/intermediate/advanced) | Simple, matches PROJECT_SPEC examples |
| MAX_PROFICIENCY_LEVEL | Named constant = 3 | Avoids magic numbers in scoring formula |
| Progress source of truth | `roadmap_items.status` | Single authoritative source; audit log is append-only |
| Project storage | Dedicated `projects` table | Structured, queryable; supports Module 4 facts |
| Gap report storage | `gap_reports` table (JSON report_data) | Supports `GET /gap-analysis` persistence |
| Rule storage | JSON file only (no DB table) | Single source of truth; no dead schema |
| Roadmap uniqueness | Supersession semantics (app-level) | Only one active roadmap per student+role |

---

## 9. API Architecture

### 9.1 API Base Configuration

```
Base URL: /api/v1
Content-Type: application/json
Authentication: Bearer token (JWT) in Authorization header
```

### 9.2 Authentication Endpoints

| Method | Path | Purpose | Input | Output | Auth |
|--------|------|---------|-------|--------|------|
| POST | `/api/v1/auth/register` | Register new student | `{name, email, password}` | `{student_id, token}` | No |
| POST | `/api/v1/auth/login` | Login | `{email, password}` | `{token, student_id}` | No |
| GET | `/api/v1/auth/me` | Get current user | — | `{student_id, name, email}` | Yes |

### 9.3 Module 1 — Student Intelligence Endpoints

> **Revision Note (F-API-2, LOW):** Resume reprocessing semantics documented:
> `POST /resumes/{id}/process` deletes prior `source = 'resume'` skills for this
> student and re-inserts fresh ones. Self-reported skills are preserved. The
> `student_skills` table includes a `resume_id` FK to track which resume
> produced which skill.

| Method | Path | Purpose | Input | Output | Auth |
|--------|------|---------|-------|--------|------|
| PUT | `/api/v1/students/profile` | Update student profile | `{name, education, interests}` | `{student_id, profile}` | Yes |
| GET | `/api/v1/students/profile` | Get student profile | — | `{profile}` | Yes |
| POST | `/api/v1/projects` | Add a project | `{title, description, technologies}` | `{project}` | Yes |
| GET | `/api/v1/projects` | List student projects | — | `{projects[]}` | Yes |
| DELETE | `/api/v1/projects/{id}` | Remove a project | — | `{status}` | Yes |
| POST | `/api/v1/resumes/upload` | Upload resume | `multipart/form-data` (file) | `{resume_id, status}` | Yes |
| GET | `/api/v1/resumes` | List student resumes | — | `{resumes[]}` | Yes |
| POST | `/api/v1/resumes/{id}/process` | Process resume (NLP + skill extraction) | — | `{status, extracted_skills[]}` | Yes |
| GET | `/api/v1/skills/profile` | Get student skill profile | — | `{skills[]}` | Yes |
| POST | `/api/v1/skills` | Add self-reported skill | `{skill_name, proficiency}` | `{student_skill}` | Yes |
| DELETE | `/api/v1/skills/{id}` | Remove a skill | — | `{status}` | Yes |

### 9.4 Module 2 — Career Intelligence Endpoints

> **Revision Note (F-API-1, LOW):** Gap analysis is now **persisted** in the
> `gap_reports` table. `POST /gap-analysis` runs the analysis and persists the
> result. `GET /gap-analysis` reads the latest persisted report. This resolves
> the ambiguity between the API contract and the schema.

| Method | Path | Purpose | Input | Output | Auth |
|--------|------|---------|-------|--------|------|
| GET | `/api/v1/career-roles` | List available career roles | — | `{roles[]}` | Yes |
| GET | `/api/v1/career-roles/{id}` | Get role details + required skills | — | `{role, required_skills[]}` | Yes |
| POST | `/api/v1/gap-analysis` | Run skill gap analysis (persisted) | `{role_id}` | `{SkillGapReport}` | Yes |
| GET | `/api/v1/gap-analysis` | Get latest persisted gap analysis | — | `{SkillGapReport}` | Yes |
| GET | `/api/v1/gap-analysis/history` | Get gap analysis history | — | `{reports[]}` | Yes |

### 9.5 Module 3 — Learning Intelligence Endpoints

| Method | Path | Purpose | Input | Output | Auth |
|--------|------|---------|-------|--------|------|
| POST | `/api/v1/roadmaps/generate` | Generate personalized roadmap | `{role_id}` | `{LearningRoadmap}` | Yes |
| GET | `/api/v1/roadmaps` | List student roadmaps | — | `{roadmaps[]}` | Yes |
| GET | `/api/v1/roadmaps/{id}` | Get roadmap details | — | `{roadmap, items[]}` | Yes |
| PUT | `/api/v1/roadmaps/{id}/items/{item_id}/progress` | Update progress on a roadmap item | `{status, notes?}` | `{roadmap_item}` | Yes |

> **Revision Note (F-DB-1, MEDIUM):** The progress update endpoint updates
> `roadmap_items.status` (the authoritative progress state) and appends an
> entry to `progress_audit_log`. There is no separate `learning_progress`
> table to update.

### 9.6 Module 4 — Career Readiness Endpoints

| Method | Path | Purpose | Input | Output | Auth |
|--------|------|---------|-------|--------|------|
| POST | `/api/v1/readiness/evaluate` | Run readiness evaluation | `{role_id}` | `{ReadinessResult}` | Yes |
| GET | `/api/v1/readiness` | Get latest readiness result | — | `{ReadinessResult}` | Yes |
| GET | `/api/v1/readiness/history` | Get readiness evaluation history | — | `{results[]}` | Yes |

### 9.7 Reference Data Endpoints

| Method | Path | Purpose | Input | Output | Auth |
|--------|------|---------|-------|--------|------|
| GET | `/api/v1/skills` | List all available skills | — | `{skills[]}` | Yes |
| GET | `/api/v1/skills/{id}` | Get skill details + dependencies | — | `{skill, prerequisites[]}` | Yes |

### 9.8 Error Response Format

```json
{
    "error": {
        "code": "SKILL_NOT_FOUND",
        "message": "The specified skill does not exist.",
        "details": {}
    }
}
```

Standard HTTP status codes: 200, 201, 400, 401, 403, 404, 422, 500.

### 9.9 API Design Principles

**Status:** Recommendation

1. **Resource-oriented:** Endpoints are organized around resources (students,
   resumes, projects, skills, career-roles, roadmaps, readiness).
2. **Module-aligned:** Endpoints are grouped by module, with each module's router
   in a separate file.
3. **Thin controllers:** Route handlers only parse input, call services, and
   format output. All business logic is in services.
4. **Consistent pagination:** List endpoints support `?page=1&limit=20` query
   parameters (for future scalability).
5. **Versioned:** All endpoints are under `/api/v1/` to allow future API versions
   without breaking existing clients.

---

## 10. Data Flow

### 10.1 Complete End-to-End Data Flow

> **Revision Note:** Updated to reflect: coverage metrics computed by Module 2
> and consumed by Module 4 (F-MOD-1), progress from roadmap_items.status
> (F-DB-1), projects from projects table (F-DB-2), FC as sole classification
> (F-FC-1), score as supporting evidence (F-FC-1), gap reports persisted
> (F-API-1).

```
+---------------------------------------------------------------------+
|                         STUDENT ACTIONS                              |
|  1. Register/Login                                                  |
|  2. Create Profile (education, interests)                           |
|  3. Add Projects (title, description, technologies)                |
|  4. Upload Resume (PDF/DOCX/TXT)                                    |
|  5. Add Self-Reported Skills                                        |
|  6. Select Career Role                                              |
|  7. Update Learning Progress                                        |
+---------------------------+-----------------------------------------+
                            |
                            v
+--- MODULE 1: STUDENT INTELLIGENCE ---------------------------------+
|                                                                      |
|  Student Profile --> [Persisted in students table]                  |
|                                                                      |
|  Projects --> [Persisted in projects table]                          |
|                                                                      |
|  Resume Upload --> File Storage (uploads/resumes/{student_id}/)      |
|       |                                                              |
|       v                                                              |
|  Text Extraction --> pdfplumber / python-docx / plain read           |
|       |                                                              |
|       v                                                              |
|  NLP Processing --> spaCy (tokenization, custom EntityRuler, POS)    |
|       |                                                              |
|       v                                                              |
|  Skill Extraction --> Pattern matching + vocabulary lookup           |
|       |                                                              |
|       v                                                              |
|  Skill Normalization --> Alias mapping + fuzzy matching (RapidFuzz)   |
|       |                                                              |
|       v                                                              |
|  Profile Merging --> Resume skills + self-reported skills             |
|       |                                                              |
|       v                                                              |
|  Student Skill Profile --> [Persisted in student_skills table]        |
|                                                                      |
+---------------------------+-----------------------------------------+
                            |
                            v StudentSkillProfile (data contract)
+--- MODULE 2: CAREER INTELLIGENCE ---------------------------------+
|                                                                      |
|  Career Role Selection --> [Loaded from career_roles table]          |
|       |                                                              |
|       v                                                              |
|  Load Role Requirements --> [Loaded from role_skills table]         |
|       |                                                              |
|       v                                                              |
|  Skill Matching --> Compare StudentSkillProfile vs RoleRequirements  |
|       |                                                              |
|       v                                                              |
|  Gap Calculation --> For each required skill, compute gap             |
|       |                                                              |
|       v                                                              |
|  Coverage Calculation --> Compute skill/core/critical coverage %     |
|       |                                                              |
|       v                                                              |
|  Gap Prioritization --> Dependency-aware ordering                    |
|       |                                                              |
|       v                                                              |
|  Skill Gap Report (with coverage metrics) -->                       |
|       [Persisted in gap_reports table]                               |
|                                                                      |
+---------------------------+-----------------------------------------+
                            |
                            v SkillGapReport + StudentSkillProfile
+--- MODULE 3: LEARNING INTELLIGENCE --------------------------------+
|                                                                      |
|  Build Skill Dependency Graph --> From skill_dependencies table     |
|       |                                                              |
|       v                                                              |
|  Define Start State --> frozenset of student's current skills        |
|       |                                                              |
|       v                                                              |
|  Define Goal Test --> All MISSING required skills must be in state   |
|       (weak skills NOT included - handled by Module 4)              |
|       |                                                              |
|       v                                                              |
|  A* Search --> Genuine A* with g(n), h(n), open/closed lists         |
|       |  (h = sum of missing required skills' base costs;            |
|       |   admissible, consistent, no prerequisite costs in h)        |
|       v                                                              |
|  Path Reconstruction --> Ordered list of skills to learn             |
|       |                                                              |
|       v                                                              |
|  Roadmap Generation --> Convert A* path to LearningRoadmap           |
|       |                                                              |
|       v                                                              |
|  Personalized Learning Roadmap -->                                  |
|       [Persisted in learning_roadmaps + roadmap_items tables]        |
|                                                                      |
+---------------------------+-----------------------------------------+
                            |
                            v LearningRoadmap + StudentSkillProfile + GapReport
+--- MODULE 4: CAREER READINESS -------------------------------------+
|                                                                      |
|  Learning Progress --> [Loaded from roadmap_items.status]            |
|       |  (authoritative progress source; audit log is append-only)   |
|       v                                                              |
|  Fact Generation -->                                                 |
|       - Coverage metrics: CONSUMED from SkillGapReport (Module 2)    |
|       - Proficiency: computed from StudentSkillProfile               |
|       - Progress: computed from roadmap_items.status                |
|       - Experience: from projects table                             |
|       - Score: computed by weighted factor formula                  |
|       |                                                              |
|       v                                                              |
|  Load Rules --> [From JSON config: readiness_rules.json]             |
|       |                                                              |
|       v                                                              |
|  Forward Chaining --> Genuine inference engine (SOLE classifier)     |
|       |  - Match rules against facts in working memory               |
|       |  - Fire highest-priority matching rule                       |
|       |  - Add conclusion to working memory (enables new rules)      |
|       |  - Multi-step inference chain:                               |
|       |    core_skills_satisfied -> progress_on_track ->             |
|       |    readiness_classification                                 |
|       |  - Repeat until no new rules fire                            |
|       v                                                              |
|  Readiness Classification --> Role Ready / Nearly Ready / Needs Imp  |
|       (SOLE authority: Forward Chaining; score is supporting)       |
|       |                                                              |
|       v                                                              |
|  Readiness Score --> Weighted factor combination (0-100)             |
|       (supporting evidence; computed BEFORE FC runs)                 |
|       |                                                              |
|       v                                                              |
|  Explanation Generation --> From inference trace + templates          |
|       |                                                              |
|       v                                                              |
|  Career Readiness Result --> [Persisted in readiness_results table]  |
|                                                                      |
+---------------------------------------------------------------------+
```

### 10.2 Data Persistence Points

> **Revision Note:** Updated to reflect: gap reports persisted (F-API-1),
> projects persisted (F-DB-2), progress from roadmap_items (F-DB-1).

| Step | Data | Where Persisted |
|------|------|-----------------|
| Student registers | Account info | `students` table |
| Profile created | Education, interests | `students` table |
| Projects added | Title, description, technologies | `projects` table |
| Resume uploaded | File + extracted text | `resumes` table + filesystem |
| Skills extracted | Skills + proficiency | `student_skills` table (with `resume_id` FK) |
| Role selected | Role preference | Stored in session/request |
| Gap analysis run | Gap results + coverage metrics | `gap_reports` table |
| Roadmap generated | Roadmap + items | `learning_roadmaps` + `roadmap_items` tables |
| Progress updated | Skill progress (authoritative) | `roadmap_items.status` + `progress_audit_log` (append) |
| Readiness evaluated | Score + classification + explanation | `readiness_results` table |

### 10.3 Data Transformation Points

| Transformation | Input | Output | Module |
|----------------|-------|--------|--------|
| Resume -> Text | Binary file | Raw text string | Module 1 |
| Text -> Skills | Raw text | List of skill IDs + proficiency | Module 1 |
| Skills -> Profile | List of skills | Structured StudentSkillProfile | Module 1 |
| Profile -> Gap Report | StudentSkillProfile + Role requirements | SkillGapReport (with coverage metrics) | Module 2 |
| Gap Report -> Graph | Skill gaps + dependencies | SkillGraph (DAG) | Module 3 |
| Graph -> Roadmap | SkillGraph + start/goal states | LearningRoadmap (via A*) | Module 3 |
| Roadmap + Gap Report -> Facts | Roadmap + progress + profile + coverage | Fact dictionary | Module 4 |
| Facts -> Classification | Facts + rules | ReadinessResult (via Forward Chaining) | Module 4 |

---

## 11. AI/NLP Boundary

### 11.1 Boundary Definition

**Status:** Requirement (from AGENTS.md Section 13 and PROJECT_SPEC.md Section 9)

The architecture must clearly separate deterministic logic from NLP processing
and optional LLM-generated content. The two required algorithms (A* and Forward
Chaining) must NEVER be replaced by an LLM.

```
+-------------------------------------------------------------+
|                    DETERMINISTIC LOGIC                        |
|  (No AI/LLM involvement - pure Python code)                   |
|                                                               |
|  - A* Search Algorithm (Module 3)                            |
|  - Forward Chaining Engine (Module 4)                        |
|  - Gap Calculation (Module 2)                                |
|  - Coverage Metric Calculation (Module 2)                    |
|  - Skill Matching (Module 2)                                 |
|  - Roadmap Generation (Module 3)                             |
|  - Readiness Scoring Formula (Module 4)                      |
|  - Database Queries                                          |
|  - Authentication                                           |
|  - API Request Validation                                    |
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|                    NLP PROCESSING                             |
|  (spaCy + custom EntityRuler + regex - offline, deterministic)|
|                                                               |
|  - Resume Text Extraction (Module 1)                        |
|  - Tokenization (Module 1)                                   |
|  - Custom Entity Ruler (pattern-based NER, Module 1)         |
|  - POS Tagging (Module 1)                                    |
|  - Skill Extraction via Pattern Matching (Module 1)          |
|  - Skill Normalization via Alias Dictionary (Module 1)       |
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|               OPTIONAL LLM INTEGRATION                        |
|  (Only for non-critical enhancement - never replaces logic)   |
|  Behind a feature flag that defaults to OFF                   |
|                                                               |
|  - Learning resource descriptions (Module 3)                 |
|  - Enhanced readiness explanations (Module 4)                |
|  - Unusual skill name normalization (Module 1)               |
|  - Student-friendly summaries                                |
|                                                               |
|  CONSTRAINT: LLM output is NEVER used as input to            |
|  A*, Forward Chaining, or any deterministic algorithm.        |
+-------------------------------------------------------------+
```

### 11.2 Algorithm Protection Mechanisms

**Status:** Requirement

The architecture prevents LLM from replacing required algorithms by:

1. **A* and Forward Chaining are pure Python functions** - they take structured
   data in, return structured data out. No API calls, no network access, no LLM
   involvement.
2. **Module services call algorithms directly** - the A* engine is called by
   `Module3Service.generate_roadmap()`, not by any external API or LLM.
3. **Tests verify algorithm correctness** - unit tests check that A* produces
   valid paths and that Forward Chaining produces correct classifications. These
   tests would fail if the algorithm were replaced by an LLM.
4. **Code review checklist** - the reviewer agent specifically checks that A* and
   Forward Chaining are genuine implementations (AGENTS.md Section 7.3).
5. **Data flow separation** - NLP output (skill extraction) feeds INTO the
   deterministic pipeline as structured data but never replaces it.
6. **Feature flag for LLM** - any LLM integration is behind a feature flag
   (`ENABLE_LLM=false` by default). When disabled, the system uses deterministic
   fallbacks for all LLM-enhanced features.

### 11.3 What the LLM May and May Not Do

| LLM May | LLM May NOT |
|---------|-------------|
| Generate learning resource descriptions | Execute A* search |
| Generate enhanced natural language explanations | Execute Forward Chaining |
| Normalize unusual skill names (fallback only) | Determine skill gaps |
| Summarize readiness results | Compute readiness scores |
| Suggest learning resources | Classify readiness |
| | Make structural decisions about the roadmap |
| | Replace any deterministic algorithm |

---

## 12. Security Architecture

### 12.1 Authentication

**Status:** Recommendation

- JWT tokens with short expiry (24 hours)
- bcrypt password hashing (cost factor 12)
- Token sent in `Authorization: Bearer <token>` header
- No refresh tokens (proportional to project scope)
- Token contains `student_id` and `exp` (expiry timestamp)

### 12.2 Authorization

**Status:** Recommendation

- All endpoints except `register` and `login` require authentication.
- Students can only access their own data — authorization check in services:
  ```python
  if resume.student_id != current_user.id:
      raise HTTPException(403, "Not authorized to access this resource")
  ```
- No admin/role-based access control needed for this scope (single student role).

### 12.3 Resume Upload Security

**Status:** Recommendation

| Control | Implementation |
|---------|---------------|
| File type validation | Whitelist: `.pdf`, `.docx`, `.txt` only |
| MIME type check | Verify MIME type matches extension |
| File size limit | Maximum 5 MB per upload |
| Filename sanitization | Strip special characters, use UUID prefix |
| Storage isolation | Files stored in `{student_id}/` subdirectories |
| No execution | Upload directory is outside web root, no script execution |
| No path traversal | Use `os.path.join` and validate resolved path is within upload root |

### 12.4 Input Validation

**Status:** Recommendation

- All API inputs validated via Pydantic models (FastAPI native)
- String fields have max length limits
- Email format validation
- Proficiency values restricted to enum: `beginner`, `intermediate`, `advanced`
- Role IDs validated against database
- SQL injection prevented by SQLAlchemy ORM (parameterized queries)
- File content validation: check file magic bytes, not just extension

### 12.5 API Security

**Status:** Recommendation

- All endpoints except login/register require authentication
- Student can only access their own data (authorization check in services)
- CORS configured to allow only the frontend origin
- Rate limiting not required for academic demo (can be added later)
- HTTPS recommended for production (not required for local demo)

### 12.6 Secret Management

**Status:** Requirement (from AGENTS.md Section 18)

| Secret | Storage |
|--------|---------|
| Database path | Environment variable `DATABASE_URL` |
| JWT secret | Environment variable `JWT_SECRET` |
| LLM API key (if used) | Environment variable `OPENAI_API_KEY` |
| File storage path | Environment variable `UPLOAD_DIR` |

`.env.example` provides template. `.env` is in `.gitignore`. Secrets are never
committed to version control.

### 12.7 Student Data Protection

**Status:** Recommendation

- Resume files are student-specific (stored per student directory)
- Passwords are hashed with bcrypt, never stored in plain text
- API responses never include password hashes
- Student data is isolated — students cannot access other students' data
- No PII in logs (error messages should not include email or other PII)
- Resume extracted text is stored in the database but not exposed via API to
  other students
- `.gitignore` must include `uploads/`, `*.db`, `.env`

---

## 13. Testing Architecture

### 13.1 Testing Levels

```
tests/
├── unit/
│   ├── test_skill_extraction.py       # Module 1 NLP
│   ├── test_skill_normalization.py    # Module 1 normalization
│   ├── test_gap_calculation.py        # Module 2
│   ├── test_coverage_calculation.py   # Module 2 coverage metrics
│   ├── test_a_star.py                 # Module 3 A* Search
│   ├── test_forward_chaining.py       # Module 4 Forward Chaining
│   ├── test_readiness_scoring.py      # Module 4 scoring
│   └── test_fact_generation.py        # Module 4 facts
├── integration/
│   ├── test_module1_pipeline.py       # Profile -> Skill Profile
│   ├── test_module2_pipeline.py       # Skill Profile -> Gap Report
│   ├── test_module3_pipeline.py       # Gap Report -> Roadmap
│   ├── test_module4_pipeline.py       # Roadmap -> Readiness
│   └── test_full_pipeline.py          # End-to-end module integration
├── end-to-end/
│   └── test_e2e_workflow.py           # Full user workflow via API
└── test_data/
    ├── sample_resumes/                # Test PDF, DOCX, TXT files
    ├── sample_skills.json             # Test skill vocabulary
    └── sample_roles.json              # Test career roles
```

**Observation:** The project also has module-level test directories:
- `modules/module-1-student-intelligence/tests/`
- `modules/module-2-career-intelligence/tests/`
- `modules/module-3-learning-intelligence/tests/`
- `modules/module-3-learning-intelligence/astar/tests/`
- `modules/module-4-career-readiness/tests/`
- `modules/module-4-career-readiness/forward-chaining/tests/`
- `backend/tests/`

**Recommendation:** Algorithm-specific tests (A*, Forward Chaining) live in the
`modules/` test directories (co-located with the algorithm code). Application-level
tests (API, integration, end-to-end) live in the top-level `tests/` directory.
The `backend/tests/` directory can hold backend-specific integration tests.

### 13.2 A* Test Strategy

> **Revision Note (F-ASTAR-1, F-ASTAR-4, F-ASTAR-5):** Updated test strategy to
> verify heuristic admissibility (no prerequisite costs in h), weak-skill
> handling (A* plans only missing skills), and correct f(n) computation.

**Status:** Recommendation

```python
class TestAStar:
    """Comprehensive A* Search tests."""

    def test_simple_path(self):
        """Student knows A, role needs A->B->C. Verify path is [B, C]."""

    def test_multiple_paths(self):
        """Multiple valid paths exist. Verify A* finds the lowest-cost one."""

    def test_prerequisite_enforcement(self):
        """B requires A. Verify A is learned before B in the path."""

    def test_student_already_has_skills(self):
        """Student knows A and C, role needs A->B->C. Only B should be in path."""

    def test_no_path_possible(self):
        """Circular dependency or impossible requirement. Verify graceful handling (returns None)."""

    def test_heuristic_admissibility(self):
        """Verify h(n) never overestimates actual remaining cost.
        Specifically: h does NOT include prerequisite costs; h only sums
        missing required skills' base costs."""

    def test_heuristic_no_prerequisite_costs(self):
        """Verify that h does not include costs of non-required prerequisites.
        h should only count missing required skills, not their prerequisites."""

    def test_optimal_cost(self):
        """Verify the path found has the minimum total cost."""

    def test_empty_start_state(self):
        """Student knows nothing. Verify complete path is generated."""

    def test_goal_already_met(self):
        """Student already has all required skills. Verify empty path."""

    def test_complex_dependency_chain(self):
        """Diamond dependency graph: A->B, A->C, B->D, C->D. Verify correct ordering."""

    def test_different_starting_states(self):
        """Two students with different skills get different roadmaps for the same role."""

    def test_different_target_requirements(self):
        """Same student gets different roadmaps for different roles."""

    def test_cost_heuristic_behavior(self):
        """Verify that f(n) = g(n) + h(n) is computed correctly at each step.
        g = accumulated path cost; h = sum of missing required skills' base costs."""

    def test_weak_skills_not_in_goal(self):
        """Student has a skill at beginner (below required intermediate).
        Verify the skill is NOT in the goal set (A* plans only missing skills).
        The skill's ID is already in the start state."""

    def test_non_required_prerequisite_in_path(self):
        """A required skill has a non-required prerequisite.
        Verify the prerequisite appears in the path (needed to unlock the
        required skill) but is NOT counted in h (not a required skill)."""
```

**Location:** `modules/module-3-learning-intelligence/astar/tests/test_algorithm.py`
and `tests/unit/test_a_star.py` (the latter may import from the former).

### 13.3 Forward Chaining Test Strategy

> **Revision Note (F-FC-1, F-FC-2, F-FC-3):** Updated test strategy to verify:
> multi-step inference chains, FC as sole classification authority, no
> contributes_to_score, and score as supporting evidence only.

**Status:** Recommendation

```python
class TestForwardChaining:
    """Comprehensive Forward Chaining tests."""

    def test_single_rule_fires(self):
        """One rule matches. Verify it fires and conclusion is reached."""

    def test_multiple_rules_fire(self):
        """Multiple rules can fire. Verify correct priority ordering."""

    def test_rule_chain_multi_step(self):
        """Genuine multi-step inference chain:
        1. rule_core_skills_satisfied fires -> asserts core_skills_satisfied=true
        2. rule_progress_on_track fires -> asserts progress_on_track=true
        3. rule_role_ready fires (depends on facts from steps 1 and 2)
        Verify all three fire in order and the final classification is role_ready."""

    def test_intermediate_fact_enables_downstream_rule(self):
        """Verify that a fact derived by one rule enables another rule
        that could not fire before the intermediate fact was asserted."""

    def test_no_rules_fire_except_default(self):
        """No conditions met except default rule. Verify default classification."""

    def test_rule_priority(self):
        """Two rules match, different priorities. Higher priority fires first."""

    def test_classification_role_ready(self):
        """High coverage + progress + core skills satisfied.
        Verify 'Role Ready' classification from Forward Chaining (not from score)."""

    def test_classification_nearly_ready(self):
        """Moderate coverage + progress. Verify 'Nearly Ready' classification."""

    def test_classification_needs_improvement(self):
        """Low coverage + progress. Verify 'Needs Improvement' classification."""

    def test_fc_is_sole_classification_authority(self):
        """Verify that the classification comes from Forward Chaining,
        NOT from a score-threshold if/else. The score is supporting evidence."""

    def test_no_contributes_to_score(self):
        """Verify that rules do NOT have a contributes_to_score field.
        The score is computed solely by the weighted factor formula."""

    def test_score_computed_before_fc(self):
        """Verify that the readiness_score fact is computed by the weighted
        factor formula and added to facts BEFORE Forward Chaining runs."""

    def test_explanation_generation(self):
        """Verify explanation matches the classification and includes
        the multi-step reasoning trace."""

    def test_threshold_edge_cases(self):
        """Test exact boundary values (e.g., coverage = 80.0 exactly)."""

    def test_working_memory_accumulates(self):
        """Verify each fired rule's conclusion persists in working memory
        and can enable subsequent rules."""

    def test_fact_generation_from_student_data(self):
        """Verify facts are correctly computed from student profile + progress.
        Coverage metrics should come from SkillGapReport (not recomputed)."""

    def test_conflicting_non_triggering_conditions(self):
        """Rule with conditions that partially match but not all. Verify it does NOT fire."""

    def test_default_rule_lowest_priority(self):
        """Verify the default rule (empty conditions) has the lowest priority
        and only fires when no other classification rule fires."""

    def test_classification_not_overwritten(self):
        """F-NEW-1: Once a classification is asserted, lower-priority
        classification rules must NOT overwrite it.
        
        Setup: facts satisfy role_ready conditions (coverage >= 80,
        core_skills_satisfied, progress_on_track). rule_role_ready
        fires first (priority 80) and asserts role_ready.
        
        Verify: rule_nearly_ready (priority 70) does NOT fire even
        though its conditions (coverage >= 60, progress >= 50) are
        still met. The final classification remains "role_ready".
        
        This tests the engine-level classification-overwrite guard."""
```

**Location:** `modules/module-4-career-readiness/forward-chaining/tests/test_engine.py`
and `tests/unit/test_forward_chaining.py`.

### 13.4 Module-Level Testing

Each module can be tested independently by providing mock inputs:

| Module | Test Input | Test Output |
|--------|-----------|-------------|
| Module 1 | Sample resumes + profiles + projects | Extracted skills + proficiency |
| Module 2 | Mock StudentSkillProfile + role | SkillGapReport (with coverage metrics) |
| Module 3 | Mock SkillGapReport (missing skills only) + SkillGraph | A* path + roadmap |
| Module 4 | Mock facts (with coverage from contract) + rules | Forward Chaining result + classification |

Integration tests verify the modules work together end-to-end.

### 13.5 Test Data Strategy

**Status:** Recommendation

- **Sample resumes:** Create 3-5 sample resumes in `tests/test_data/sample_resumes/`
  (one PDF, one DOCX, one TXT, one edge case).
- **Sample skill vocabulary:** A subset of `data/skills/skills.json` for testing.
- **Sample roles:** A subset of `data/roles/roles.json` for testing.
- **Sample dependencies:** A small skill dependency graph for A* testing.
- **Sample rules:** A small rule set for Forward Chaining testing (including
  multi-step inference chains).

### 13.6 Testing Principles

1. **Algorithm tests are deterministic** — same input always produces same output.
2. **Algorithm tests do NOT require database or HTTP** — algorithms are pure
   functions tested in isolation.
3. **Integration tests use a test database** — separate SQLite file or in-memory
   SQLite (`sqlite:///:memory:`).
4. **End-to-end tests use FastAPI's TestClient** — no need for a running server.
5. **Tests are added alongside implementation** — not postponed to the end.

---

## 14. Development Structure

### 14.1 File Organization by Module

**Status:** Recommendation

The architecture is designed so each module can reach a demonstrable state at the
end of its respective week. The file organization maps to the weekly milestones.

```
backend/
├── app/
│   ├── main.py                           # FastAPI app initialization
│   ├── core/
│   │   ├── config.py                     # Settings, env vars
│   │   ├── database.py                   # SQLAlchemy engine, session
│   │   └── security.py                   # JWT, password hashing
│   ├── models/                           # SQLAlchemy ORM models
│   │   ├── student.py                    # Student, Resume, Project models
│   │   ├── skill.py                      # Skill, StudentSkill, SkillDependency
│   │   ├── career.py                     # CareerRole, RoleSkill
│   │   ├── roadmap.py                    # LearningRoadmap, RoadmapItem, ProgressAuditLog
│   │   └── readiness.py                  # GapReport, ReadinessResult
│   ├── schemas/                          # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── student.py
│   │   ├── skill.py
│   │   ├── career.py
│   │   ├── roadmap.py
│   │   └── readiness.py
│   ├── routes/                           # FastAPI routers
│   │   ├── auth.py                       # Week 1+ (auth needed from start)
│   │   ├── module1_student.py            # Week 1
│   │   ├── module2_career.py             # Week 2
│   │   ├── module3_learning.py           # Week 3
│   │   └── module4_readiness.py          # Week 4
│   ├── services/                         # Business logic
│   │   ├── module1/
│   │   │   ├── resume_parser.py          # Text extraction from files
│   │   │   ├── nlp_engine.py             # spaCy processing + custom EntityRuler
│   │   │   ├── skill_extractor.py         # Skill extraction logic
│   │   │   ├── skill_normalizer.py       # Alias mapping
│   │   │   └── profile_builder.py        # Assemble Student Skill Profile
│   │   ├── module2/
│   │   │   ├── role_service.py           # Career role management
│   │   │   ├── skill_matcher.py          # Match student to role skills
│   │   │   ├── gap_calculator.py         # Compute gaps
│   │   │   ├── coverage_calculator.py    # Compute coverage metrics
│   │   │   └── gap_prioritizer.py        # Priority ordering
│   │   ├── module3/
│   │   │   ├── skill_graph_builder.py    # Build graph from DB data
│   │   │   ├── roadmap_generator.py      # Calls A*, formats result
│   │   │   └── roadmap_service.py        # Orchestrates, persists
│   │   └── module4/
│   │       ├── fact_generator.py         # Compute facts from student data
│   │       ├── readiness_scorer.py       # Score computation (weighted formula)
│   │       ├── explanation_generator.py  # Human-readable explanation
│   │       └── readiness_service.py      # Orchestrates, persists
│   └── utils/                            # Shared utilities
│       ├── file_utils.py                 # File handling helpers
│       └── constants.py                  # Shared constants (MAX_PROFICIENCY_LEVEL, etc.)

modules/                                   # Pure algorithm packages
├── module-1-student-intelligence/
│   ├── nlp/                              # NLP processing (spaCy wrapper + EntityRuler)
│   ├── profile/                          # Profile data structures
│   ├── resume/                           # Resume text extraction
│   ├── skill-extraction/                 # Skill extraction logic
│   └── tests/
├── module-2-career-intelligence/
│   ├── roles/                            # Role data structures
│   ├── skill-gap/                        # Gap calculation logic
│   ├── skill-requirements/               # Requirement data structures
│   └── tests/
├── module-3-learning-intelligence/
│   ├── astar/
│   │   ├── graph.py                      # SkillGraph data structure
│   │   ├── algorithm.py                  # A* search (pure)
│   │   ├── heuristic.py                  # Heuristic function (pure)
│   │   └── tests/
│   ├── roadmap/                          # Roadmap data structures
│   ├── skill-graph/                      # Graph construction logic
│   └── tests/
└── module-4-career-readiness/
    ├── forward-chaining/
    │   ├── engine.py                     # Forward Chaining engine (pure)
    │   ├── facts.py                      # Fact data structures
    │   ├── rules.py                      # Rule data structures
    │   └── tests/
    ├── progress/                         # Progress data structures
    ├── readiness/                        # Readiness data structures
    ├── scoring/                          # Scoring logic (weighted formula)
    └── tests/

frontend/
├── src/
│   ├── App.tsx                           # Root component with routing
│   ├── main.tsx                          # Entry point
│   ├── components/                       # Shared UI components
│   │   ├── Layout.tsx
│   │   ├── Navbar.tsx
│   │   ├── ProtectedRoute.tsx
│   │   └── SkillBadge.tsx
│   ├── pages/                            # Page components
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   └── ProfilePage.tsx
│   ├── modules/                          # Module-specific UI components
│   │   ├── student-profile/              # Week 1
│   │   │   ├── ProfileForm.tsx
│   │   │   ├── ProjectForm.tsx
│   │   │   ├── ResumeUpload.tsx
│   │   │   └── SkillProfile.tsx
│   │   ├── career-analysis/             # Week 2
│   │   │   ├── RoleSelector.tsx
│   │   │   └── SkillGapReport.tsx
│   │   ├── learning-roadmap/            # Week 3
│   │   │   ├── RoadmapView.tsx
│   │   │   └── RoadmapItem.tsx
│   │   └── career-readiness/            # Week 4
│   │       ├── ReadinessResult.tsx
│   │       └── ReadinessExplanation.tsx
│   ├── services/                         # API client functions
│   │   ├── api.ts                        # Axios/fetch base configuration
│   │   ├── authApi.ts
│   │   ├── studentApi.ts
│   │   ├── careerApi.ts
│   │   ├── learningApi.ts
│   │   └── readinessApi.ts
│   ├── hooks/                            # Custom React hooks
│   │   ├── useAuth.ts
│   │   └── useApi.ts
│   ├── types/                            # TypeScript type definitions
│   │   └── index.ts
│   └── utils/                            # Frontend utilities

data/
├── skills/
│   └── skills.json                       # Canonical skill vocabulary
├── roles/
│   └── roles.json                        # Career role definitions
├── skill-relationships/
│   └── dependencies.json                 # Skill prerequisite graph
├── sample/
│   └── sample-resumes/                   # Sample resumes for testing
└── rules/
    └── readiness_rules.json              # Forward Chaining rules
```

### 14.2 Weekly Development Map

> **Revision Note (F-SCOPE-2, LOW):** Added an "Optional/Stretch" column to
> mark non-core features. Core deliverables must be complete for DEMO_READY.
> Optional features are pursued only if core is complete.

| Week | Module | Backend Files | Frontend Files | Data Files | Tests | Optional/Stretch |
|------|--------|--------------|----------------|------------|-------|------------------|
| 1 | Module 1 | config, database, security, models (student, skill, project), routes/module1, services/module1/* | auth pages, student-profile module, shared components | skills.json | unit: skill extraction, normalization | LLM skill normalization (if ENABLE_LLM) |
| 2 | Module 2 | routes/module2, services/module2/* (including coverage_calculator), models/career, models/gap_report | career-analysis module, role selector, gap report | roles.json | unit: gap calculation, coverage metrics, integration: module 1->2 | — |
| 3 | Module 3 | routes/module3, services/module3/*, models/roadmap, modules/.../astar/* | learning-roadmap module, roadmap view | dependencies.json | unit: A* (including admissibility, weak-skill tests), integration: module 2->3 | LLM resource descriptions, graph visualization |
| 4 | Module 4 | routes/module4, services/module4/*, models/readiness, modules/.../forward-chaining/* | career-readiness module, explanation view | readiness_rules.json | unit: forward chaining (including multi-step chain tests), integration: all modules, e2e | LLM enhanced explanations |

**Core vs. Optional:**
- **Core deliverables** must be complete for `DEMO_READY`.
- **Optional/Stretch features** are pursued only if core is complete and time
  allows. They are behind feature flags and must not block core functionality.

### 14.3 Module Completion Gate

**Status:** Requirement (from AGENTS.md Section 9)

Each module must pass through these states before the next module begins:

```
IMPLEMENTED
    ↓
TESTED
    ↓
REVIEWED
    ↓
SECURITY CHECKED
    ↓
INTEGRATED
    ↓
DOCUMENTED
    ↓
DEMO_READY
```

A module is `DEMO_READY` when a real user can execute its intended workflow
successfully. A module is NOT `DEMO_READY` if:
- Major features are placeholders
- Core logic is hard-coded
- Tests are missing for important functionality
- The module breaks previously completed modules
- The primary algorithm is only simulated
- The UI claims functionality that the backend does not implement
- Important errors are ignored

### 14.4 Weekly Demo Requirements

**Week 1 — Module 1 Demo:**
```
Enter Student Information -> Enter Academic Information -> Select Areas of Interest -> Add Projects -> Input Existing Skills -> Upload Resume -> Process Resume -> Extract Skills -> Normalize Skills -> Merge & Display Student Skill Profile
```

**Week 2 — Module 2 Demo:**
```
Select Career Role -> Load Role Requirements -> Compare Student Skills ->
Generate Skill Gap Report (with coverage metrics)
```
Must consume Module 1's output.

**Week 3 — Module 3 Demo:**
```
Skill Gap (missing skills only) -> Skill Dependency Graph -> A* Search ->
Personalized Learning Roadmap
```
A* must be demonstrable with test cases (including admissibility and weak-skill
handling).

**Week 4 — Module 4 Demo:**
```
Learning Progress + Skill Profile + Gap Report -> Facts ->
Forward Chaining (multi-step inference) -> Readiness Rules ->
Career Readiness Result (FC classification + score as supporting evidence +
explanation with inference trace)
```
Must integrate with Modules 1-3.

---

## 15. Agent Boundaries

### 15.1 Agent Roles and Architecture Interaction

**Status:** Requirement (from AGENTS.md Section 7)

The six development agents interact with the architecture as follows:

### 15.2 krishna-dev — Orchestrator

**Architecture interaction:**
- Reads `PROJECT_SPEC.md` and this architecture document before delegating work.
- Breaks work into module-sized tasks aligned with the weekly milestones.
- Assigns tasks to specialist agents based on their expertise.
- Maintains module boundaries — ensures agents do not cross module lines without
  coordination.
- Integrates completed work from multiple agents.
- Resolves conflicts between agent recommendations (e.g., architect vs. security
  on a design decision).
- Tracks module completion through the completion gate states.
- Ensures the project remains within the locked scope (4 modules, A*, Forward
  Chaining, no AI Assessment).

**What krishna-dev should NOT do:**
- Blindly delegate the entire project without coordination.
- Allow one agent to modify another module's core logic without coordination.
- Move to the next module before the current one reaches `DEMO_READY`.

### 15.3 architect — Architecture Specialist (this agent)

**Architecture interaction:**
- Produces and maintains this architecture document.
- Makes technology decisions (stack, database, API design).
- Defines module boundaries and data contracts.
- Designs database schema and entity relationships.
- Defines API endpoints and data flow.
- Documents significant architectural decisions (Section 16).
- Does NOT implement features or write application code.
- Does NOT modify project files except architecture documentation.

**What architect should NOT do:**
- Introduce enterprise-level complexity without evidence the project requires it.
- Rewrite working architecture merely because another pattern is fashionable.
- Add features not in `PROJECT_SPEC.md`.

### 15.4 reviewer — Code and Architecture Reviewer

**Architecture interaction:**
- Reviews code for correctness, maintainability, and architecture consistency.
- Verifies project-spec compliance.
- Detects unnecessary complexity and duplicated logic.
- For Module 3: verifies that A* is genuinely implemented (has graph, nodes,
  edges, cost function, heuristic, open/closed lists, path reconstruction).
  Verifies the heuristic is admissible (no prerequisite costs in h).
- For Module 4: verifies that Forward Chaining is genuinely implemented (has
  facts, rules, working memory, rule matching, inference loop, trace). Verifies
  multi-step inference chains exist. Verifies FC is the sole classification
  authority (no score-threshold if/else).
- Reviews API/interface contracts for consistency.
- Identifies problems rather than silently rewriting large parts of the project.

**What reviewer should NOT do:**
- Silently rewrite code instead of identifying issues.
- Reject code for stylistic preferences without meaningful benefit.
- Approve fake algorithm implementations.

### 15.5 security — Security Specialist

**Architecture interaction:**
- Reviews authentication and authorization implementation.
- Reviews resume/file-upload security (file type validation, size limits, path
  traversal prevention).
- Reviews input validation and API security.
- Reviews sensitive student data handling.
- Verifies secrets are not committed to source code.
- Reviews dependency security.
- Ensures security requirements are proportional to the actual application.

**What security should NOT do:**
- Over-engineer security for an academic demo (e.g., require OAuth2 with PKCE
  for a single-user demo).
- Introduce security measures that break the demo workflow without providing
  alternatives.

### 15.6 debugger — Debugging Specialist

**Architecture interaction:**
- Diagnoses bugs by reproducing, investigating, identifying root causes.
- Applies focused fixes — does not introduce unrelated changes.
- Verifies fixes do not introduce regressions.
- Works within the existing architecture — does not redesign to fix a bug.
- Reports which files were changed and why.

**What debugger should NOT do:**
- Hide errors merely to make tests pass.
- Make sweeping changes when a focused fix would suffice.
- Change architecture to work around a bug.

### 15.7 tester — Testing Specialist

**Architecture interaction:**
- Writes unit tests for core functionality (especially A* and Forward Chaining).
- Writes integration tests for module boundaries.
- Writes end-to-end tests for the full user workflow.
- Writes edge-case tests for algorithm boundary conditions.
- Writes regression tests for fixed bugs.
- Ensures algorithm tests are deterministic and do not require database/HTTP.

**What tester should NOT do:**
- Postpone all testing until the end of the project.
- Write tests that depend on external services or network access.
- Write tests that mask failures instead of verifying correctness.

### 15.8 Agent Interaction Flow

```
krishna-dev (orchestrator)
    |
    |---> architect: "Design module N architecture"
    |       \---> Produces/updates architecture docs
    |
    |---> [implementation agents]: "Implement module N per architecture"
    |       \---> Implement code within module boundaries
    |
    |---> reviewer: "Review module N implementation"
    |       \---> Verifies correctness, algorithm genuineness, spec compliance
    |
    |---> security: "Security-check module N"
    |       \---> Verifies auth, validation, data protection
    |
    |---> tester: "Test module N"
    |       \---> Writes and runs unit/integration/e2e tests
    |
    \---> debugger: "Fix bugs in module N"
            \---> Diagnoses and fixes issues with focused changes
```

### 15.9 Agent Boundaries Summary

| Agent | May Modify | May NOT Modify |
|-------|-----------|----------------|
| krishna-dev | Any file (orchestrator) | N/A (has final responsibility) |
| architect | `docs/architecture.md` only | Application source code, other docs |
| reviewer | None (identifies issues only) | Any source code (unless explicitly asked) |
| security | None (identifies issues only) | Any source code (unless explicitly asked) |
| debugger | Bug-related files only | Architecture, unrelated files |
| tester | Test files only | Application source code |

---

## 16. Important Architectural Decisions

### 16.1 Decision: Modular Monolith over Microservices

**Decision:** Use a layered modular monolith with internal module boundaries.

**Requirement:** Four modules with a strict linear dependency flow
(AGENTS.md Section 6).

**Evidence:** The project is an academic system with a 4-week timeline, a single
demo user, and a linear data flow. There is no evidence of a need for independent
deployment, scaling, or team boundaries that would justify microservices.

**Alternatives considered:**
- Microservices: Rejected — adds operational complexity (service discovery,
  inter-service communication, distributed transactions) without benefit for this
  scope.
- Single-layer monolith (no module boundaries): Rejected — would not provide the
  separation of concerns needed for academic defensibility and the four-module
  structure required by the spec.

**Trade-offs:**
- Advantage: Simpler deployment, easier debugging, no network overhead between
  modules.
- Disadvantage: Modules share a process; a crash in one module affects all. Not
  independently scalable. Acceptable for this scope.

**Risks:** Module boundaries may erode over time if developers bypass service
interfaces. Mitigated by code review and the reviewer agent's boundary checks.

**Verification:** Reviewer verifies that cross-module access goes through service
interfaces, not direct DB queries.

### 16.2 Decision: SQLite over PostgreSQL

**Decision:** Use SQLite via SQLAlchemy ORM for development and initial deployment.

**Requirement:** None explicitly — this is a recommendation.

**Evidence:** The project is a single-user academic demo. SQLite requires zero
configuration and no server process. The SQLAlchemy abstraction allows migration
to PostgreSQL by changing only the connection string.

**Alternatives considered:**
- PostgreSQL: Rejected for initial implementation — requires server setup,
  configuration, and management disproportionate to an academic demo. Can be
  adopted later if needed.

**Trade-offs:**
- Advantage: Zero configuration, single-file database, easy backup/reset.
- Disadvantage: Limited concurrent write performance, no full-text search. Not
  relevant for this scope.

**Risks:** If the project scales beyond a demo, SQLite's limitations may become
apparent. Mitigated by SQLAlchemy abstraction — migration is a connection string
change.

**Verification:** Test that all ORM operations work with SQLite. Test that
connection string change to PostgreSQL works (if attempted).

### 16.3 Decision: A* State Space as Frozensets of Skill IDs (Binary)

> **Revision Note (F-ASTAR-1, F-ASTAR-3, F-ASTAR-4):** Updated to reflect:
> binary state representation (no proficiency levels), heuristic admissibility
> proof (no prerequisite costs), precise optimality claim (minimum modeled
> learning cost), and weak-skill handling (A* plans only missing skills).

**Decision:** A* search nodes are skill states (frozensets of skill IDs), not
individual skills. The state representation is **binary** (skill present or
absent) — proficiency levels are NOT part of the state.

**Requirement:** A* must be a genuine implementation that depends on the
student's current skill state and the target role's required skills
(AGENTS.md Section 3).

**Evidence:** A* is a pathfinding algorithm that searches through states. In
SkillBridge, the "position" is the set of skills the student has acquired. The
"goal" is any state that includes all **missing** required skills. This is the
natural formulation of the learning path problem as a search problem.

**Alternatives considered:**
- Search over individual skills (not states): Rejected — would not correctly
  model the combinatorial nature of skill acquisition. A* needs to search through
  states to find the optimal path.
- Use a simple topological sort instead of A*: Rejected — would not satisfy the
  academic requirement for A* and would not optimize for cost.
- Proficiency-aware state (Option B from review): Considered but rejected for
  4-week scope — would increase state-space size and implementation effort without
  proportional benefit. Weak skills are handled by Module 4's readiness scoring.

**Trade-offs:**
- Advantage: Genuine A* formulation; finds minimum-total-learning-cost path
  subject to prerequisite ordering; academically defensible; simple state
  representation.
- Disadvantage: Cannot plan proficiency upgrades for weak skills (binary state).
  Weak skills are handled by Module 4 instead. State space can grow exponentially
  with the number of skills. Mitigated by limiting the graph to role-relevant
  skills only.

**Risks:**
- State space explosion for complex skill graphs. Mitigated by pruning the graph
  to only skills relevant to the target role and its prerequisites.
- Weak-skill proficiency upgrades not planned by A*. Mitigated by Module 4's
  readiness scoring which considers proficiency facts.

**Verification:** A* unit tests verify path correctness, optimality, prerequisite
enforcement, heuristic admissibility (no prerequisite costs in h), weak-skill
handling (not in goal), and edge cases (no path, goal already met, empty start
state).

### 16.4 Decision: Forward Chaining as Sole Classification Authority

> **Revision Note (F-FC-1, F-FC-2, F-FC-3):** Updated to reflect: FC as sole
> classification authority, removal of contributes_to_score, multi-step
> inference chains.

**Decision:** Implement Forward Chaining as a genuine inference engine with
facts, rules, working memory, rule matching, and iterative firing. Forward
Chaining is the **sole mechanism** that determines the readiness classification.
The readiness score is supporting evidence only.

**Requirement:** Forward Chaining must be implemented as a genuine inference
process (AGENTS.md Section 3, PROJECT_SPEC.md Section 8). The readiness
classification must be explainable (AGENTS.md Section 5).

**Evidence:** The spec requires facts, rules, rule evaluation, inference, and
final conclusions. A simple if/else threshold check would not satisfy this
requirement. The spec also defines score ranges (80-100, 60-79, 0-59) which
inform the rule threshold design.

**Alternatives considered:**
- Simple if/else threshold checks: Rejected — would not be a genuine Forward
  Chaining implementation and would fail the reviewer's algorithm verification.
- External rule engine library: Rejected — would not be academically defensible
  as a self-implemented algorithm.
- Score-threshold classification (score as classifier): Rejected — would
  undermine the role of Forward Chaining as the required algorithm. The score
  is supporting evidence, not the classifier.
- Dual classification (FC + score thresholds with precedence): Rejected —
  creates contradictions and confusion. FC is the sole authority.

**Trade-offs:**
- Advantage: Genuine inference engine; explainable via inference trace;
  academically defensible; single classification authority (no contradictions);
  multi-step inference chains demonstrate real forward chaining.
- Disadvantage: More code than simple if/else. Acceptable given the requirement.
  Rule thresholds must be aligned with spec score ranges for consistency.

**Risks:**
- Rule configuration errors may produce unexpected classifications. Mitigated by
  the default catch-all rule and comprehensive testing.
- FC classification and score may diverge in edge cases. This is by design — FC
  is authoritative. The explanation must clearly state which rules fired.

**Verification:** Forward Chaining unit tests verify rule firing, priority
ordering, multi-step inference chains, classification correctness, FC as sole
authority, and edge cases.

### 16.5 Decision: Algorithm Code in modules/ Directory, Orchestration in backend/app/services/

**Decision:** Pure algorithm logic (A*, Forward Chaining) lives in the
`modules/` directory as importable Python packages. Backend services in
`backend/app/services/moduleN/` import and orchestrate these algorithms.

**Requirement:** Algorithms must be genuine, testable, and academically
defensible (AGENTS.md Section 12).

**Evidence:** The `modules/` directory already exists with subdirectories for
each algorithm (`astar/`, `forward-chaining/`). Separating pure algorithm code
from application orchestration allows algorithms to be tested in isolation
without database or HTTP dependencies.

**Alternatives considered:**
- All code in `backend/app/services/`: Rejected — would mix algorithm logic with
  application concerns, making it harder to test algorithms in isolation and
  less academically defensible.
- All code in `modules/`: Rejected — algorithms need to be orchestrated with
  database access and API integration, which belongs in the backend.

**Trade-offs:**
- Advantage: Clean separation; algorithms testable in isolation; academically
  defensible as standalone implementations.
- Disadvantage: Two locations for related code. Mitigated by clear naming and
  import paths.

**Risks:** Import path complexity. Mitigated by using relative imports within
`modules/` and absolute imports from `backend/`.

**Verification:** Algorithm tests run without database or HTTP dependencies.

### 16.6 Decision: Configurable Rules via JSON File (No DB Table)

> **Revision Note (F-DB-3, LOW):** Updated to reflect removal of the
> `readiness_rules` table. JSON file is the sole source of truth.

**Decision:** Forward Chaining rules are stored in `data/rules/readiness_rules.json`
and can be modified without code changes. No database table mirrors the rules.

**Requirement:** "The exact thresholds and rules must be configurable rather than
hard-coded throughout the application" (PROJECT_SPEC.md Section 6).

**Evidence:** The spec explicitly requires configurability. JSON files provide a
human-readable, editable format that does not require code changes.

**Alternatives considered:**
- Rules in database: Considered — allows runtime editing via API. But adds
  complexity. JSON file is simpler and sufficient for this scope. A database
  table can be added later if runtime rule editing is designed.
- Rules hard-coded in Python: Rejected — violates the spec's configurability
  requirement.
- JSON file + DB mirror: Rejected — creates ambiguity about which source is
  authoritative and invites inconsistency.

**Trade-offs:**
- Advantage: Configurable without code changes; human-readable; version-controllable;
  single source of truth (no dead schema).
- Disadvantage: No runtime editing via API. Acceptable for this scope.

**Verification:** Test that changing rule thresholds in JSON changes the
classification output.

### 16.7 Decision: LLM Integration is Optional and Behind a Feature Flag

**Decision:** The core system works without any LLM. LLM integration is optional,
behind a feature flag (`ENABLE_LLM=false` by default).

**Requirement:** AI-generated content must not replace the actual A* or Forward
Chaining algorithms (PROJECT_SPEC.md Section 9, AGENTS.md Section 13).

**Evidence:** The spec allows AI for supplementary features (explanations,
resource descriptions) but explicitly prohibits it from replacing required
algorithms. A feature flag ensures the system is fully functional without an LLM.

**Alternatives considered:**
- LLM required: Rejected — would introduce API dependency, cost, and network
  requirement. Would risk masking the actual algorithms.
- No LLM at all: Considered — simplest approach. But the spec allows optional AI
  enhancement, so a feature flag provides flexibility without risk.

**Trade-offs:**
- Advantage: System works offline without LLM; LLM enhancement available when
  desired; algorithms protected.
- Disadvantage: Slightly more code for fallback paths. Acceptable.

**Risks:** LLM output could be incorrectly used as algorithm input. Mitigated by
the AI/NLP boundary (Section 11) and code review.

**Verification:** All tests pass with `ENABLE_LLM=false`. Algorithm tests never
invoke the LLM.

### 16.8 Decision: JWT Authentication with bcrypt

**Decision:** Use JWT tokens for authentication and bcrypt for password hashing.

**Requirement:** Student data is sensitive; authentication is a security
requirement (AGENTS.md Section 18).

**Evidence:** JWT is stateless and works well with REST APIs. bcrypt is a
well-established password hashing algorithm. Both are simple to implement with
FastAPI.

**Alternatives considered:**
- Session-based auth: Rejected — requires session storage, more complex for REST
  APIs.
- argon2: Considered — slightly more secure than bcrypt but less widely available.
  bcrypt is sufficient for this scope.

**Trade-offs:**
- Advantage: Stateless, simple, well-understood.
- Disadvantage: No token revocation without additional logic. Acceptable for
  this scope.

**Verification:** Security agent reviews authentication implementation. Tests
verify password hashing and token generation/verification.

### 16.9 Decision: Local Filesystem for Resume Storage

**Decision:** Store resume files on the local filesystem in
`uploads/resumes/{student_id}/`.

**Requirement:** Resume upload is a Module 1 requirement (PROJECT_SPEC.md
Section 3).

**Evidence:** The project is a local demo. Cloud storage (S3) would require
external service setup and credentials disproportionate to the scope.

**Alternatives considered:**
- Cloud storage (S3): Rejected — requires AWS account, credentials, network
  access. Not proportional to an academic demo.
- Database BLOB storage: Considered — but SQLite has performance issues with
  large BLOBs. Filesystem is simpler.

**Trade-offs:**
- Advantage: No external dependency; easy to demo offline; simple implementation.
- Disadvantage: Not scalable; files lost if server directory deleted. Acceptable
  for demo.

**Risks:** Files lost if server directory is deleted. Mitigated by treating as a
demo project and adding `uploads/` to `.gitignore`.

**Verification:** Security agent reviews file upload validation and storage
isolation.

### 16.10 Decision: Roadmap Items Status as Authoritative Progress Source

> **Revision Note (F-DB-1, MEDIUM):** New decision documenting
> `roadmap_items.status` as the single source of truth for progress, with
> `progress_audit_log` as an append-only audit trail.

**Decision:** `roadmap_items.status` is the authoritative progress state. The
`progress_audit_log` table records progress update events for audit/history
purposes only — it is NOT a second source of current progress.

**Requirement:** Learning progress must be tracked (PROJECT_SPEC.md Section 12).
Module 4 needs progress facts.

**Evidence:** Having two tables store overlapping progress state
(`roadmap_items.status` and `learning_progress.progress_percent`) creates
inconsistency risk. Designating one as authoritative eliminates this risk.

**Alternatives considered:**
- `learning_progress` as authoritative: Rejected — `roadmap_items` is already
  tied to the roadmap and simpler to use as the progress source.
- Both tables with synchronization: Rejected — adds complexity and
  synchronization bugs.

**Trade-offs:**
- Advantage: Single source of truth; no synchronization bugs; simpler progress
  queries.
- Disadvantage: No separate progress_percent field per skill (progress is
  derived from status: not_started=0%, in_progress=50%, completed=100%).

**Verification:** Tests verify that progress facts are derived from
`roadmap_items.status` and that the audit log is append-only.

---

## 17. Risks and Trade-offs

### 17.1 Key Risks

> **Revision Note:** Updated risks to reflect revised architecture.

| Risk | Severity | Mitigation |
|------|----------|------------|
| A* state space too large for complex skill graphs | Medium | Limit graph to role-relevant skills only; use pruning; limit skill vocabulary to 50-100 skills |
| A* heuristic is a loose lower bound (ignores prerequisite chains) | Low | Acceptable trade-off for small graph; adding prerequisite costs risks inadmissibility; documented in Section 6.8 |
| Weak skills not planned by A* (binary state) | Low | By design; weak-skill proficiency handled by Module 4 readiness scoring; documented in Section 6.3 |
| NLP skill extraction accuracy insufficient | Medium | Fallback to regex pattern matching; custom EntityRuler seeded from vocabulary; allow manual skill addition; fuzzy matching with threshold |
| 4-week timeline too tight for full implementation | High | Prioritize core flow; defer optional LLM integration; keep skill vocabulary small initially; optional features marked in weekly map |
| SQLite limitations for concurrent access | Low | Not a concern for single-student demo |
| Resume parsing fails on unusual formats (scanned PDFs) | Medium | Support PDF/DOCX/TXT; clear error messages for unsupported formats; do not attempt OCR |
| Forward Chaining rule misconfiguration produces wrong classification | Medium | Default catch-all rule ensures classification always produced; comprehensive rule tests; multi-step chain tests |
| FC classification and score diverge | Low | By design — FC is authoritative; explanation must state which rules fired; rule thresholds aligned with score ranges for normal agreement |
| Module boundary erosion over time | Medium | Code review checks for direct DB access across modules; service interface enforcement; coverage metrics consumed from contract |
| LLM output incorrectly used as algorithm input | High | Feature flag defaults to OFF; AI/NLP boundary documented; reviewer checks algorithm genuineness |
| spaCy model download fails in demo environment | Low | Document model download in setup instructions; provide fallback to regex-only extraction |
| Progress state inconsistency | Low | Eliminated by designating `roadmap_items.status` as sole authoritative source; audit log is append-only |

### 17.2 Deliberate Simplifications

| Simplification | Reason | Impact |
|----------------|--------|--------|
| SQLite instead of PostgreSQL | Proportional to project scope; no server setup needed | No concurrent access; acceptable for demo |
| No refresh tokens | Reduces auth complexity | Sessions expire; user must re-login (acceptable) |
| Local file storage instead of cloud | No external service dependency | Files lost if server directory deleted (demo only) |
| spaCy + custom EntityRuler instead of LLM for NLP | Offline, deterministic, no API cost | Less flexible than LLM for unusual text patterns |
| No WebSocket/real-time updates | REST is sufficient for the workflow | User must refresh to see updates (acceptable) |
| No Redis caching | Not needed for single-user demo | Slower repeated queries (acceptable) |
| No CI/CD pipeline | Not required for academic project | Manual testing (acceptable); local lint scripts recommended |
| Small initial skill vocabulary (50-100 skills) | Sufficient for demo; keeps A* state space manageable | May not cover all real-world skills (extensible via JSON) |
| 3-5 initial career roles | Sufficient for demo | Architecture supports adding more without code changes |
| Binary A* state (no proficiency levels) | Sufficient for 4-week scope; weak skills handled by Module 4 | A* plans only missing skills; proficiency upgrades not in roadmap |
| Readiness rules in JSON only (no DB table) | Single source of truth; no dead schema | No runtime rule editing via API (acceptable) |
| Gap reports persisted as JSON in DB | Simple; supports GET /gap-analysis | No relational querying of gap report internals (acceptable) |

### 17.3 Architectural Trade-offs

| Trade-off | Chosen | Alternative | Rationale |
|-----------|--------|-------------|-----------|
| Simplicity vs. Scalability | Simplicity | Scalable microservices | 4-week timeline; single demo user |
| Offline vs. Cloud NLP | Offline (spaCy + EntityRuler) | Cloud LLM | No API cost; deterministic; works in demo environment |
| Deterministic vs. AI-enhanced | Deterministic core | AI-enhanced | Required algorithms (A*, FC) must be deterministic |
| Configuration vs. Code | JSON config files | Hard-coded rules | Rules and skills must be configurable without code changes |
| Monolith vs. Modular monolith | Modular monolith | Microservices | Appropriate for project scope; modules have clear boundaries |
| Algorithm separation vs. colocation | Separated (modules/ + backend/) | All in backend/ | Algorithms testable in isolation; academically defensible |
| JWT vs. Session auth | JWT | Session-based | Stateless; simpler for REST APIs |
| Filesystem vs. Cloud storage | Local filesystem | S3/cloud | No external dependency; demo-friendly |
| Binary A* state vs. proficiency-aware | Binary (Option A) | Proficiency-aware (Option B) | 4-week scope; weak skills handled by Module 4 |
| FC sole classifier vs. dual classifier | FC sole authority | FC + score thresholds | Eliminates contradictions; FC is required algorithm |
| Single progress source vs. dual | roadmap_items.status only | roadmap_items + learning_progress | Eliminates inconsistency; audit log is append-only |

### 17.4 What Might Need Rearchitecting Later

| Area | Current Approach | Future Consideration |
|------|------------------|---------------------|
| Database | SQLite | Switch to PostgreSQL for production |
| File Storage | Local filesystem | Switch to S3/cloud storage |
| Authentication | Simple JWT | Add refresh tokens, OAuth |
| NLP | spaCy + custom EntityRuler + regex | Add LLM for enhanced extraction |
| Caching | None | Add Redis for repeated queries |
| Deployment | Local development | Docker containerization |
| Skill vocabulary | JSON file (50-100 skills) | Database-backed vocabulary with admin UI |
| Rule management | JSON file | Database-backed rules with admin UI |
| Real-time updates | REST polling | WebSocket for live progress updates |
| A* state representation | Binary (skill present/absent) | Proficiency-aware state (skill_id, proficiency_level) tuples |
| Gap report storage | JSON in DB | Relational decomposition for querying |

---

## 18. Recommended Project File Changes

### 18.1 Architecture Documentation (This Document)

| File | Action | Status |
|------|--------|--------|
| `docs/architecture.md` | **Updated** (v2.2, this document) | Done |

### 18.2 Files to Create (Implementation Phase — NOT by Architect)

**Note:** The architect does NOT create these files. This list is a recommendation
for the orchestrator and implementation agents.

| File | Purpose | Week |
|------|---------|------|
| `backend/requirements.txt` | Python dependencies (including ruff) | 1 |
| `frontend/package.json` | Frontend dependencies (including eslint, prettier) | 1 |
| `frontend/vite.config.ts` | Vite configuration | 1 |
| `frontend/tsconfig.json` | TypeScript config | 1 |
| `frontend/src/main.tsx` | Frontend entry point | 1 |
| `backend/app/main.py` | FastAPI app setup (populate) | 1 |
| `backend/app/core/config.py` | Settings class (populate) | 1 |
| `backend/app/core/database.py` | SQLAlchemy setup (populate) | 1 |
| `backend/app/core/security.py` | JWT + bcrypt (populate) | 1 |
| `backend/app/utils/constants.py` | Shared constants (MAX_PROFICIENCY_LEVEL, etc.) | 1 |
| `backend/app/models/*.py` | SQLAlchemy models (including Project, GapReport, ProgressAuditLog) | 1-4 |
| `backend/app/schemas/*.py` | Pydantic schemas | 1-4 |
| `backend/app/routes/*.py` | FastAPI routers | 1-4 |
| `backend/app/services/module1/*.py` | Module 1 services | 1 |
| `backend/app/services/module2/*.py` | Module 2 services (including coverage_calculator) | 2 |
| `backend/app/services/module3/*.py` | Module 3 services | 3 |
| `backend/app/services/module4/*.py` | Module 4 services | 4 |
| `backend/app/utils/file_utils.py` | File handling utilities | 1 |
| `modules/module-3-learning-intelligence/astar/graph.py` | SkillGraph (populate) | 3 |
| `modules/module-3-learning-intelligence/astar/algorithm.py` | A* search (populate) | 3 |
| `modules/module-3-learning-intelligence/astar/heuristic.py` | Heuristic (populate) | 3 |
| `modules/module-4-career-readiness/forward-chaining/engine.py` | FC engine (populate) | 4 |
| `modules/module-4-career-readiness/forward-chaining/facts.py` | Fact structures (populate) | 4 |
| `modules/module-4-career-readiness/forward-chaining/rules.py` | Rule structures (populate) | 4 |
| `data/skills/skills.json` | Skill vocabulary | 1 |
| `data/roles/roles.json` | Career role definitions | 2 |
| `data/skill-relationships/dependencies.json` | Skill dependency graph | 3 |
| `data/rules/readiness_rules.json` | Forward Chaining rules (with multi-step chains) | 4 |
| `database/migrations/` | Alembic migrations | 1 |
| `database/seed/` | Seed data scripts | 1 |

### 18.3 Files to Populate (Already Exist but Empty)

| File | Week | Content |
|------|------|---------|
| `backend/app/main.py` | 1 | FastAPI app initialization, CORS, router includes |
| `backend/app/core/config.py` | 1 | Pydantic Settings class with env vars |
| `backend/app/core/database.py` | 1 | SQLAlchemy engine, session maker, Base |
| `backend/app/core/security.py` | 1 | JWT creation/verification, password hashing |
| `frontend/src/App.tsx` | 1 | Root component with routing |
| `modules/module-3-learning-intelligence/astar/graph.py` | 3 | SkillGraph data structure |
| `modules/module-3-learning-intelligence/astar/algorithm.py` | 3 | A* search implementation |
| `modules/module-3-learning-intelligence/astar/heuristic.py` | 3 | Heuristic function |
| `modules/module-4-career-readiness/forward-chaining/engine.py` | 4 | Forward Chaining engine |
| `modules/module-4-career-readiness/forward-chaining/facts.py` | 4 | Fact data structures |
| `modules/module-4-career-readiness/forward-chaining/rules.py` | 4 | Rule data structures |

### 18.4 Documentation to Update (by Other Agents)

| File | Action | Responsible Agent | When |
|------|--------|-------------------|------|
| `docs/algorithms.md` | Populate with A* and Forward Chaining algorithm documentation | krishna-dev or architect | Week 3-4 |
| `docs/api-design.md` | Populate with detailed API documentation | krishna-dev | Week 1-4 |
| `docs/database-design.md` | Populate with database schema documentation | krishna-dev or architect | Week 1 |
| `docs/project-overview.md` | Populate with high-level project overview | krishna-dev | Week 1 |
| `docs/module-1.md` | Populate with Module 1 documentation | krishna-dev | Week 1 |
| `docs/module-2.md` | Populate with Module 2 documentation | krishna-dev | Week 2 |
| `docs/module-3.md` | Populate with Module 3 documentation | krishna-dev | Week 3 |
| `docs/module-4.md` | Populate with Module 4 documentation | krishna-dev | Week 4 |
| `docs/development-log/week-1.md` | Populate with Week 1 development log | krishna-dev | Week 1 |
| `docs/development-log/week-2.md` | Populate with Week 2 development log | krishna-dev | Week 2 |
| `docs/development-log/week-3.md` | Populate with Week 3 development log | krishna-dev | Week 3 |
| `docs/development-log/week-4.md` | Populate with Week 4 development log | krishna-dev | Week 4 |
| `.env.example` | Populate with environment variable template | security or krishna-dev | Week 1 |
| `.gitignore` | Populate with ignore patterns (uploads/, *.db, .env, node_modules/) | krishna-dev | Week 1 |
| `README.md` | Populate with project setup and run instructions | krishna-dev | Week 1 |

### 18.5 Required Structure of `docs/algorithms.md`

> **Revision Note (F-ACAD-2, LOW):** Added the required structure of
> `docs/algorithms.md` per AGENTS.md Section 12. This ensures the algorithm
> documentation satisfies the academic requirement.

`docs/algorithms.md` must contain the following sections for each algorithm
(A* Search and Forward Chaining):

```text
1. Problem being solved
2. Input
3. Output
4. Algorithm steps
5. Data structures
6. Complexity
7. Implementation (file locations)
8. Example (worked example with g, h, f for A*; inference trace for FC)
9. Test cases
10. How the algorithm contributes to SkillBridge
```

Additionally, `docs/algorithms.md` must include:

- **A* heuristic admissibility proof** (from Section 6.8 of this document)
- **A* optimality claim** (precise statement from Section 6.15)
- **A* weak-skill handling** (binary state; A* plans only missing skills)
- **Forward Chaining multi-step inference chain** (from Section 7.4)
- **Forward Chaining as sole classification authority** (from Section 7.10)
- **Readiness scoring formula** (from Section 7.9, per PROJECT_SPEC.md Section 13)
- **Experience factor formula** (graded by project_count)

### 18.6 Configuration Files to Create

| File | Purpose | Content |
|------|---------|---------|
| `.env.example` | Environment variable template | `DATABASE_URL`, `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_EXPIRY_HOURS`, `UPLOAD_DIR`, `SPACY_MODEL`, `ENABLE_LLM` (optional: `OPENAI_API_KEY`) |
| `.gitignore` | Git ignore patterns | `__pycache__/`, `*.pyc`, `.env`, `uploads/`, `*.db`, `node_modules/`, `dist/`, `.venv/` |
| `backend/requirements.txt` | Python dependencies | `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pydantic`, `pyjwt`, `bcrypt`, `spacy`, `rapidfuzz`, `pdfplumber`, `python-docx`, `pytest`, `pytest-asyncio`, `httpx`, `ruff` |
| `frontend/package.json` | Frontend dependencies | `react`, `react-dom`, `react-router-dom`, `axios`, `typescript`, `vite`, `vitest`, `@testing-library/react`, `eslint`, `prettier` |

---

## Appendix A: Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./skillbridge.db

# Authentication
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# File Storage
UPLOAD_DIR=./uploads

# NLP
SPACY_MODEL=en_core_web_sm
# Alternative: en_core_web_md (better NER, larger download)

# Optional: LLM (not required for core functionality)
ENABLE_LLM=false
# OPENAI_API_KEY=your-api-key-here
```

---

## Appendix B: Open Architectural Questions

These questions should be resolved during implementation by the orchestrator:

1. **Skill vocabulary size:** How many skills should the initial vocabulary contain?
   - **Recommendation:** 50-100 common skills across 5-7 categories (Programming,
     Frameworks, Databases, DevOps, Data Science, Web, Soft Skills).
   - **Risk:** Too few skills may make the demo unconvincing; too many may make
     the A* state space too large.

2. **Career roles:** How many roles to seed initially?
   - **Recommendation:** 3-5 roles for demo (e.g., Backend Developer, Frontend
     Developer, Data Analyst, Full-Stack Developer, DevOps Engineer).

3. **Proficiency inference:** How detailed should the resume context analysis be?
   - **Recommendation:** Start simple (keyword-based: "expert" -> advanced,
     "experience" -> intermediate, listed only -> beginner). Add complexity if
     time allows.

4. **Roadmap visualization:** How should the roadmap be displayed?
   - **Recommendation:** Linear list with progress indicators for Week 3. Consider
     graph visualization later if time allows (optional/stretch).

5. **LLM integration:** Include or exclude from initial implementation?
   - **Recommendation:** Exclude from Weeks 1-3. Consider optional enhancement in
     Week 4 only if time allows and core functionality is complete (optional/stretch).

6. **Skill merging conflict resolution:** When resume and self-reported skills
   disagree on proficiency, which wins?
   - **Recommendation:** Take the higher proficiency (optimistic). Document this
   decision in `docs/module-1.md`.

7. **FC classification and score divergence:** What if the FC classification
   says "Role Ready" but the score is 78.5 (which would be "Nearly Ready" by
   score range)?
   - **Resolution:** Forward Chaining classification is authoritative (F-FC-1).
   The score is supporting evidence. The explanation must clearly state which
   rules fired and why. Rule thresholds are aligned with score ranges for normal
   agreement, but FC is authoritative when they diverge. Document this in
   `docs/algorithms.md`.

---

## Appendix C: Algorithm Summary for Academic Defense

### A* Search (Module 3)

| Aspect | Value |
|--------|-------|
| **Problem** | Find the minimum-total-learning-cost path from current skill state to target role's missing required skills, subject to prerequisite ordering constraints |
| **Input** | Start state (frozenset of current skills), goal test (all missing required skills in state), skill dependency graph, cost function |
| **Output** | Ordered list of skills to learn (the optimal path) or None if no path |
| **Algorithm** | A* Search with f(n) = g(n) + h(n) |
| **Data structures** | Priority queue (open list), set (closed list), dict (came_from for path reconstruction) |
| **g(n)** | Accumulated path cost: sum of learning costs for skills learned along the path (each skill learned at most once) |
| **h(n)** | Sum of base learning costs for missing required skills (admissible, consistent; does NOT include prerequisite costs) |
| **Admissibility** | h(n) <= h*(n) because each missing required skill must be learned at least once at its base cost; actual cost may be higher due to non-required prerequisites |
| **Optimality** | A* finds the minimum-total-learning-cost path subject to prerequisite ordering, given the configured cost model. NOT a claim about real-world educational effectiveness. |
| **Weak skills** | NOT planned by A* (binary state). Handled by Module 4 readiness scoring. |
| **Complexity** | O(b^d) in worst case, where b = branching factor, d = depth of optimal solution. In practice, much better due to heuristic pruning. |
| **Implementation** | `modules/module-3-learning-intelligence/astar/algorithm.py` |
| **Contribution** | Generates personalized learning roadmaps that respect skill dependencies and minimize total modeled learning cost |

### Forward Chaining (Module 4)

| Aspect | Value |
|--------|-------|
| **Problem** | Determine career readiness classification from student facts using rule-based reasoning |
| **Input** | Fact dictionary (computed from student profile, skill gaps with coverage metrics, learning progress, projects), rule base (from JSON config) |
| **Output** | Readiness classification (Role Ready / Nearly Ready / Needs Improvement), inference trace, explanation |
| **Algorithm** | Forward Chaining (data-driven inference) |
| **Data structures** | Working memory (dict), rule list, fired rules list, inference trace |
| **Inference process** | Match rules against working memory -> fire highest-priority matching rule -> add conclusion to working memory (with classification-overwrite guard: skip if readiness_classification already set) -> repeat until no more rules fire |
| **Multi-step chaining** | Intermediate rules derive facts (core_skills_satisfied, progress_on_track) that enable downstream classification rules |
| **Classification authority** | Forward Chaining is the SOLE classification mechanism. Score is supporting evidence only. |
| **Scoring** | Weighted factor formula (single model; no contributes_to_score); computed before FC runs; exposed as readiness_score fact |
| **Complexity** | O(n x m x c) where n = number of inference iterations, m = number of rules, c = conditions per rule. Bounded by number of rules (each fires at most once). |
| **Implementation** | `modules/module-4-career-readiness/forward-chaining/engine.py` |
| **Contribution** | Produces explainable readiness classifications based on measurable student factors and configurable rules, with genuine multi-step inference |

---

## 19. Architecture Revision Summary

This section documents the revisions made in response to the formal architecture
review (`docs/architecture-review.md`), which issued the verdict
**APPROVE WITH CHANGES**.

### Review Findings Addressed

| Finding | Severity | Status | Description of Change |
|---------|----------|--------|----------------------|
| F-ASTAR-1 | HIGH | RESOLVED | Rewrote the A* heuristic definition and admissibility proof (Section 6.8). The heuristic now clearly sums only the base learning costs of missing **required** skills. The proof explicitly shows h(n) <= h*(n) because each required skill must be learned at least once at its base cost, and the actual cost may be higher due to non-required prerequisites. Added an explicit warning: "Do NOT add prerequisite costs to h, as this would risk double-counting and could make h inadmissible." Acknowledged that h is a relaxed lower bound (ignores prerequisite chains), which preserves optimality but may limit pruning. |
| F-FC-1 | HIGH | RESOLVED | Made Forward Chaining the **SOLE** classification mechanism (Section 7.10). Removed the score-threshold if/else classification entirely (former Section 7.10). The readiness score (0-100) is now explicitly a numeric measure displayed as supporting evidence; it does NOT independently classify the student. Rule thresholds are aligned with PROJECT_SPEC.md Section 6 score ranges (80-100, 60-79, 0-59) for normal agreement, but FC is authoritative. Updated Sections 7.1, 7.8, 7.10, 7.11, 16.4, and Appendix B Q7. |
| F-FC-2 | HIGH | RESOLVED | Removed the `contributes_to_score` field from the `Conclusion` schema (Section 7.3) and from all example rules (Section 7.4). The weighted factor scoring formula (Section 7.9) is now the **single** scoring model. Updated the Forward Chaining process diagram (Section 7.6) to show the score computed by the formula, not by summing rule contributions. Removed the "Score: 60 + 20 = 80 (from rule contributions)" line. Updated Section 7.12 key design decisions. |
| F-ASTAR-2 | MEDIUM | RESOLVED | Made g(n) consistently represent accumulated path cost (Section 6.7). Explicitly stated the "learned at most once" invariant (enforced by the successor function requiring X not in S). Explained that the path-based definition (incremental via came_from) and the state-based definition (sum of state - start_state) are mathematically equivalent due to this invariant. |
| F-ASTAR-3 | MEDIUM | RESOLVED | Qualified the "optimal path" claim precisely (Section 6.15). A* finds the minimum-total-learning-cost path subject to prerequisite ordering constraints, given the configured cost model. Explicitly stated this is NOT a claim about real-world educational effectiveness. Removed the `edge_cost` field from `SkillEdge` (Section 6.2) to avoid implying unused functionality. Prerequisites constrain ordering only; they do not add extra cost. |
| F-ASTAR-4 | MEDIUM | RESOLVED | Explicitly defined how weak skills are handled (Section 6.3, 6.5, 6.14). Chose Option A (binary state; A* plans only missing skills). Weak skills (student has the skill but below required proficiency) are NOT planned by A* because the binary state already contains them. Weak-skill proficiency is addressed by Module 4's readiness scoring. Documented this as a deliberate design choice for the 4-week scope. |
| F-FC-3 | MEDIUM | RESOLVED | Added genuine multi-step inference chains to the example rule base (Section 7.4). Intermediate rules (`rule_core_skills_satisfied`, `rule_progress_on_track`) derive facts that enable the downstream `rule_role_ready` classification rule. The Forward Chaining process diagram (Section 7.6) now shows the multi-step chain across iterations 1-3. Added a test case `test_rule_chain_multi_step` (Section 13.3). |
| F-SCORE-1 | MEDIUM | RESOLVED | Replaced the binary `has_projects` scoring factor with a graded experience factor based on `project_count` (Section 7.9). Formula: `experience_score = min(100, project_count * 33)` — 0 projects -> 0, 1 -> 33, 2 -> 67, 3+ -> 100. Uses project information meaningfully without adding unnecessary complexity. |
| F-MOD-1 | MEDIUM | RESOLVED | Extended the `SkillGapReport` data contract (Section 5.6) to include precomputed `skill_coverage_percent`, `core_skill_coverage_percent`, `critical_skill_coverage_percent`, `total_skills_acquired`, and `total_skills_required`. Module 4's fact generator (Section 7.7) now consumes these from the contract instead of recomputing them. Added `CoverageCalculator` to Module 2's internal components. Updated Section 2.3 module boundary enforcement note. |
| F-MOD-2 | MEDIUM | RESOLVED | Resolved the weak-skill goal construction inconsistency (Section 6.5, 6.14). The A* goal is now built ONLY from missing_skills (skills not in the student's state). Weak skills are excluded because their IDs are already in the start state (the student has them at some proficiency), so adding them to the goal would make the goal test pass immediately without generating any learning steps. Weak-skill proficiency upgrades are handled by Module 4's readiness scoring, not by the A* roadmap. This was addressed together with F-ASTAR-4 as part of the binary state design choice (Option A). |
| F-DB-1 | MEDIUM | RESOLVED | Designated `roadmap_items.status` as the authoritative progress state (Section 8.2.11). Repurposed the former `learning_progress` table as an append-only `progress_audit_log` table (Section 8.2.12). Documented the single source of truth for `learning_progress_percent` in the fact generator (Section 7.7, step 3). Added Decision 16.10. Updated API endpoint (Section 9.5) and data flow (Section 10.1). |
| F-DB-2 | MEDIUM | RESOLVED | Added the `projects` table (Section 8.2.3) because projects are explicitly part of the student information (PROJECT_SPEC.md Section 3) and are used by Module 4 facts (`has_projects`, `project_count`). Updated the ER diagram (Section 8.3), fact generator (Section 7.7, step 4), API endpoints (Section 9.3), and file organization (Section 14.1). |
| F-ASTAR-5 | LOW | RESOLVED | Fixed the worked example (Section 6.13) to show g, h, and f separately at each step with correct computations. Example now correctly shows: Step 1: g=20, h=55, f=75 (not f=20). Added a note explaining why h does not decrease when a non-required prerequisite (Linux) is learned. |
| F-FC-4 | LOW | RESOLVED | Documented the default rule's priority dependency (Section 7.4). Added a note explaining that the default rule has empty conditions (always applicable) and must have the lowest priority. Added a warning: "Do not change the engine to fire-all-applicable without also changing this rule's semantics." Added test case `test_default_rule_lowest_priority` (Section 13.3). |
| F-SCORE-2 | LOW | RESOLVED | Defined a named constant `MAX_PROFICIENCY_LEVEL = 3` in `backend/app/utils/constants.py` (Section 7.9). Used this constant in the scoring formula instead of the magic number 3. Documented the proficiency-to-number mapping in one place (Section 5.3) and referenced it. |
| F-STACK-1 | LOW | RESOLVED | Added a custom spaCy `EntityRuler` seeded from the skill vocabulary as the primary NER mechanism (Section 4.4, 4.5). This is genuine NLP customization and is more defensible than relying on the small model's default NER for technology entities. Noted `en_core_web_md` as an optional upgrade. |
| F-STACK-2 | LOW | RESOLVED | Added `ruff` for backend and `eslint` + `prettier` for frontend to the development tooling (Section 1.10, 1.11). These are zero-config and improve cross-agent code consistency. CI/CD remains excluded for scope. |
| F-DB-3 | LOW | RESOLVED | Removed the `readiness_rules` table from the initial schema (Section 8.2). Rules are loaded from the JSON file (`data/rules/readiness_rules.json`), which is the sole source of truth. Updated Decision 16.6. Removed the table from the ER diagram (Section 8.3). |
| F-DB-4 | LOW | RESOLVED | Documented supersession semantics for active roadmaps (Section 8.2.10). Generating a new roadmap for the same student+role supersedes (deactivates) prior active roadmaps. Application-level enforcement in the service layer is recommended. |
| F-API-1 | LOW | RESOLVED | Resolved gap analysis persistence ambiguity (Section 9.4, 8.2.9). Added the `gap_reports` table to persist gap analysis results (including coverage metrics as JSON). `POST /gap-analysis` runs and persists; `GET /gap-analysis` reads the latest persisted report. Added `GET /gap-analysis/history` endpoint. Updated data flow (Section 10.2). |
| F-API-2 | LOW | RESOLVED | Documented resume reprocessing semantics (Section 4.3, 8.2.5). Reprocessing a resume deletes prior `source = 'resume'` skills for that student and re-inserts fresh ones. Self-reported skills are preserved. Added `resume_id` FK to `student_skills` table to track which resume produced which skill. |
| F-SCOPE-2 | LOW | RESOLVED | Added an "Optional/Stretch" column to the weekly development map (Section 14.2). Marked LLM integration, graph visualization, and LLM resource descriptions as optional/stretch. Stated: "Core deliverables must be complete for DEMO_READY. Optional features are pursued only if core is complete." |
| F-ACAD-2 | LOW | RESOLVED | Specified the required structure of `docs/algorithms.md` (Section 18.5) per AGENTS.md Section 12. Listed all required sections (problem, input, output, algorithm steps, data structures, complexity, implementation, example, test cases, contribution). Added required content: A* heuristic admissibility proof, optimality claim, weak-skill handling, FC multi-step inference chain, FC as sole classification authority, readiness scoring formula, experience factor formula. |
| F-NEW-1 | HIGH | RESOLVED | Added a classification-overwrite guard to the Forward Chaining engine's `_fire_rule()` method (Section 7.5). Once `readiness_classification` has been asserted in working memory, any subsequent rule whose conclusion targets the same fact key is skipped. This ensures the first (highest-priority) classification rule to fire is authoritative, and lower-priority classification rules cannot overwrite it. Updated the process diagram (Section 7.6, iteration 4) to show the guard in action. Added test case `test_classification_not_overwritten` (Section 13.3). Updated Module 4 summary (Section 3.6), key design decisions (Section 7.12), and Appendix C (Forward Chaining summary). |
| F-SCOPE-1 | INFO | CONFIRMED | AI Role-Specific Assessment correctly excluded. No action needed. |
| F-ACAD-1 | INFO | CONFIRMED | A* and Forward Chaining are genuinely designed. Caveats (F-ASTAR-1, F-FC-1, F-FC-2, F-FC-3, F-ASTAR-5) have been resolved in this revision. |

### Intentionally Rejected Recommendations

| Finding | Recommendation | Reason for Rejection |
|---------|----------------|---------------------|
| F-ASTAR-4 | Option B: Proficiency-aware state representation (frozenset of (skill_id, proficiency_level) tuples) | Rejected for 4-week scope. Option B would increase state-space size and implementation effort without proportional benefit for the demo. Weak skills are adequately handled by Module 4's readiness scoring. Option A (binary state) is simpler and sufficient. Documented as a deliberate design choice. Can be reconsidered if the project scope is extended. |
| F-STACK-1 | Use `en_core_web_md` instead of `en_core_web_sm` | Partially rejected. The `md` model is noted as an optional upgrade (Appendix A), but the default remains `sm` with a custom EntityRuler. The custom EntityRuler (pattern-based NER seeded from the skill vocabulary) is the primary NER mechanism and is more defensible than relying on a larger model's default NER. Download size for `md` (~40 MB) may be a concern in demo environments. |
| F-DB-3 (alternative) | Keep `readiness_rules` table and document load precedence | Rejected. Having both a JSON file (authoritative) and a database table (mirror) for the same data invites inconsistency. The JSON file is the sole source of truth. A database table can be added later if runtime rule editing is designed. Removing the table eliminates ambiguity. |

### Remaining Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| A* heuristic is a loose lower bound (ignores prerequisite chains) | A* may behave closer to Dijkstra (less pruning) for graphs with many non-required prerequisites | Acceptable trade-off for a small skill graph (50-100 skills, pruned to role-relevant subset). A tighter heuristic risks inadmissibility. Documented in Section 6.8. |
| Weak skills not planned by A* (binary state) | Students with weak skills do not receive proficiency-upgrade steps in their roadmap | By design. Weak-skill proficiency is addressed by Module 4's readiness scoring (proficiency facts, average_proficiency, min_core_proficiency). The roadmap focuses on acquiring missing skills. Documented in Section 6.3. Can be reconsidered with Option B if scope extends. |
| FC classification and score may diverge in edge cases | User sees a classification that doesn't match the score range (e.g., "Role Ready" with score 78.5) | By design — FC is authoritative. The explanation must clearly state which rules fired and why. Rule thresholds are aligned with score ranges for normal agreement. Documented in Section 7.10 and Appendix B Q7. |
| Gap reports stored as JSON (not relationally decomposed) | Cannot perform relational queries on gap report internals | Acceptable for demo scope. The full SkillGapReport (including coverage metrics) is stored as JSON in the `gap_reports` table. If relational querying is needed later, the table can be decomposed. |
| Roadmap supersession is application-level (not DB constraint) | Race condition could theoretically create two active roadmaps | Acceptable for single-user demo. Application-level enforcement in the service layer is recommended. A partial unique index could be added if concurrent access becomes a concern. |
| Experience factor formula (project_count * 33) is a simple linear model | Does not account for project complexity, relevance, or quality | Acceptable for demo scope. The formula is explainable and uses project_count meaningfully. A more complex model (e.g., weighting by project relevance to the role) would add complexity without proportional benefit for the 4-week timeline. |

---

## 20. Revision Summary (v2.2)

### F-NEW-1 — Forward Chaining Classification Overwrite (HIGH)

**Problem:** The Forward Chaining engine would overwrite an already-asserted
`readiness_classification` with lower-priority classification rules. After
`rule_role_ready` (priority 80) fired and asserted `"role_ready"`, the
lower-priority `rule_nearly_ready` (priority 70) would fire next (its
conditions `skill_coverage >= 60` and `learning_progress >= 50` were still
satisfied) and overwrite the classification to `"nearly_ready"`. Then the
default rule (priority 10) would overwrite again to `"needs_improvement"`.
The engine always produced "needs_improvement" regardless of facts.

**Root cause:** The engine's `_fire_rule()` method had no guard against
overwriting an already-asserted classification fact. The `fired_ids` set
only prevented the same rule from firing twice — it did not prevent different
rules from overwriting the same fact key.

**Fix:** Added a classification-overwrite guard in `_fire_rule()`. Before
firing any rule whose conclusion targets `readiness_classification`, the
engine checks whether `readiness_classification` is already present in
working memory. If so, the rule is skipped. This ensures the first
(highest-priority) classification rule to fire is authoritative.

**Why engine-level (not rule-condition-level):** An engine-level guard is
simpler, more robust, and does not require changes to every classification
rule. Rule-condition approaches (e.g., adding `readiness_classification != X`
to every lower-priority rule) are fragile: adding a new classification rule
requires remembering to add the negation to all lower-priority rules.

**Sections modified:** 3.6, 7.5, 7.6, 7.12, 13.3, 19, Appendix C.

**Verification:** The worked example (Section 7.6) now correctly produces
"Role Ready" with the guard in place. Test case `test_classification_not_overwritten`
(Section 13.3) verifies the guard behavior.

---

*This architecture document (v2.2) is the authoritative technical reference for
SkillBridge AI. All agents should review this document before making implementation
decisions. Updates to this document should be documented in `docs/development-log/`.*

*End of document.*
