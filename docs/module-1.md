# Module 1 — Student Intelligence

## Overview
Module 1 (Student Intelligence) builds a structured representation of the student's current skills and background. It handles student profile creation, academic information, areas of interest, projects, existing skills, resume upload and processing, NLP-based skill extraction and normalization, and generates the Student Skill Profile that serves as input to Module 2 (Career Intelligence).

## Responsibilities
- Student registration and profile management
- Academic information capture
- Areas of interest tracking
- Project management (title, description, technologies)
- Existing skills (self-reported) recording
- Resume upload and file handling
- Resume text extraction (PDF, DOCX, TXT)
- NLP-based text processing (spaCy + custom EntityRuler)
- Skill extraction from resume and profile
- Skill normalization (mapping variants to canonical names)
- Student skill profile generation (merging self-reported and resume-derived skills)

## Data Model
The following core entities are used (all inherit from BaseMixin for id, created_at, updated_at):

- **Student**: id, first_name, last_name, email
- **AcademicInfo**: student_id (FK), degree, major, institution, graduation_year, gpa
- **Interest**: student_id (FK), interest_category, interest_description
- **Project**: student_id (FK), name, description, technologies_used, start_date, end_date, url
- **Skill**: id, name, category, description (shared across modules)
- **StudentSkill**: id, student_id (FK), skill_id (FK), proficiency_level (beginner|intermediate|advanced), source (self-reported|resume|inferred), confidence (0.0-1.0), last_updated
- **Resume**: id, student_id (FK), file_path, upload_date, extracted_text (optional), processing_status

Relationships:
- One Student → many AcademicInfo, Interest, Project, StudentSkill, Resume
- Many StudentSkill → one Skill (canonical skill catalog)

## API / Service Interfaces
All endpoints are under `/api/v1` and require authentication.

### Profile Management
- `POST /profiles` – create student profile
  - Request: `{first_name, last_name, email}`
  - Response: `{student_id, first_name, last_name, email, created_at}`
- `GET /profiles/{student_id}` – retrieve profile
- `PUT /profiles/{student_id}` – update profile

### Academic Information
- `POST /academic-info` – add academic record
- `GET /academic-info/{student_id}` – list academic records
- `PUT /academic-info/{academic_id}` – update
- `DELETE /academic-info/{academic_id}` – delete

### Areas of Interest
- `POST /interests` – add interest
- `GET /interests/{student_id}` – list interests
- `PUT /interests/{interest_id}` – update
- `DELETE /interests/{interest_id}` – delete

### Projects
- `POST /projects` – add project
- `GET /projects/{student_id}` – list projects
- `PUT /projects/{project_id}` – update
- `DELETE /projects/{project_id}` – delete

### Existing Skills (Self-reported)
- `POST /skills/self-reported` – add self-reported skill
  - Request: `{skill_name, proficiency_level}`
  - Response: `{student_skill_id, skill_id, proficiency_level, source: "self_reported"}`
- `GET /skills/{student_id}` – list all skills (self-reported + resume-derived)

### Resume Upload & Processing
- `POST /resumes/upload` – upload and process resume
  - Request: multipart/form-data with `file`
  - Response: `{resume_id, status: "processing"}`
- `GET /resumes/{resume_id}` – get resume metadata
- `GET /resumes/{resume_id}/text` – get extracted text (if completed)
- `GET /resumes/{resume_id}/skills` – get skills extracted from this resume

### Student Skill Profile
- `GET /profiles/{student_id}/skill-profile` – get consolidated skill profile
  - Response: 
    ```json
    {
      "student_id": "...",
      "skills": [
        {
          "skill_id": "...",
          "name": "Python",
          "category": "Programming",
          "proficiency": "advanced",
          "sources": ["self_reported", "resume"],
          "confidence": 0.95
        }
      ],
      "last_updated": "2026-08-21T10:00:00Z"
    }
    ```

## NLP Processing Pipeline
1. **Text Extraction**: Format-specific extractors (pdfplumber, python-docx, plain text) produce raw string.
2. **Cleaning**: Remove extra whitespace, normalize line breaks.
3. **spaCy Processing**: Load `en_core_web_sm` model; apply tokenization, POS tagging, dependency parsing.
4. **Custom EntityRuler**: Pattern-based NER seeded from skill vocabulary (`data/skills/skills.json`).
5. **Context Analysis**: Use dependency patterns to filter entities that are likely skills (e.g., nouns modified by skill-related adjectives, verbs like "proficient in", "experienced with").
6. **Skill Candidate Output**: Raw list of skill mentions with context.

## Skill Extraction & Normalization
### Extraction (Two-Layer)
- **Layer 1 – Pattern-based (Deterministic)**:
  - Maintain canonical skill vocabulary (JSON) with `aliases` per skill.
  - Match extracted entities against aliases using exact match first, then fuzzy match (RapidFuzz, threshold ≥85).
  - Example: "JS", "Javascript", "JavaScript programming" → "JavaScript".
- **Layer 2 – Context-based (Supplementary)**:
  - Use spaCy noun chunks and dependency parsing to find skill-related phrases not caught by EntityRuler.
  - Match against skill vocabulary using same fuzzy logic.

### Normalization
- Input: raw skill string from extraction.
- Process:
  1. Exact alias lookup.
  2. Fuzzy lookup (RapidFuzz) against all aliases.
  3. If match ≥85%, return canonical skill ID, category, and confidence = similarity/100.
  4. If no match, discard (or optionally flag for LLM-assisted normalization if `ENABLE_LLM=true`).
- Output: `{skill_id, name, category, confidence}`.

## Student Skill Profile Generation
- Retrieve all `StudentSkill` records for a student (both `source=self_reported` and `source=resume`).
- Group by `skill_id`.
- For each skill:
  - Determine proficiency: if multiple sources, take the highest proficiency level (beginner < intermediate < advanced).
  - Sources: concatenate unique source values.
  - Confidence: average of confidences (weighted by source reliability if desired).
- Output sorted list by skill name or category.

## Testing Strategy
### Unit Tests
- **Models**: Validate field constraints, relationships, default values.
- **Services**:
  - Profile service: create, retrieve, update.
  - Academic/Interest/Project services: CRUD operations.
  - Resume service: file validation, storage, text extraction (mock files).
  - NLP service: tokenization, entity recognition, context filtering.
  - Skill extractor: alias matching, fuzzy thresholds, context extraction.
  - Skill normalizer: mapping variations, confidence scoring, edge cases.
  - Profile service: merge logic (conflict resolution, source tracking, proficiency resolution).
- **Utils**: Resume extractors for each file type using sample fixtures.

### Integration Tests
- **API Endpoints**:
  - Profile creation → retrieval.
  - Academic info CRUD.
  - Interest CRUD.
  - Project CRUD.
  - Self-reported skill addition → retrieval.
  - Resume upload → text extraction → skill extraction → normalization → skill profile retrieval.
- **Database**: Persistence and retrieval of all entities.
- **Service Layer**: Calls between services (e.g., profile service calling resume service for skills).

### Coverage Goals
- Minimum 80% line coverage for Module 1 code.
- Specific testing of edge cases: empty resumes, malformed files, conflicting skills, missing data.

## Out-of-Scope Confirmation
The following are explicitly **NOT** implemented in Module 1:
- A* Search algorithm (Module 3)
- Forward Chaining algorithm (Module 4)
- Career role selection or skill gap analysis (Module 2)
- Learning roadmap generation (Module 3)
- Career readiness scoring or classification (Module 4)
- AI Role-Specific Assessment (removed feature per PROJECT_SPEC.md §18)
- Any assessment generation, question papers, CSP/backtracking, or readiness scoring logic

All AI/NLP usage is limited to resume text extraction, skill identification, extraction, and normalization as permitted by PROJECT_SPEC.md §9.

---
*This document reflects the Module 1 architecture as planned for Week 1 implementation.*