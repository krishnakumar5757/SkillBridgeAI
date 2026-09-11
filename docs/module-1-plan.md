# Module 1 — Student Intelligence Implementation Plan

This document maps each requirement from `PROJECT_SPEC.md` (Section 3) to concrete implementation components, ensuring traceability and testability.

## Requirement Mapping

| PROJECT_SPEC.md Requirement | Frontend Component | API/Data Contract | Backend Service | Module Implementation | Tests |
|-----------------------------|--------------------|-------------------|-----------------|-----------------------|-------|
| Student registration/profile | `StudentProfileForm` (React) | `StudentProfileCreateRequest`, `StudentProfileResponse` (Pydantic) | `ProfileService.create_profile()` | `models/profile.py`, `services/profile_service.py` | Unit: form validation, service create; Integration: API endpoint |
| Academic information | `AcademicInfoForm` (React) | `AcademicInfoCreateRequest`, `AcademicInfoResponse` | `AcademicInfoService.create_academic_info()` | `models/academic_info.py`, `services/academic_info_service.py` | Unit: model fields, service logic; Integration: API CRUD |
| Areas of interest | `InterestsForm` (React) | `InterestCreateRequest`, `InterestResponse` | `InterestService.create_interest()` | `models/interest.py`, `services/interest_service.py` | Unit: validation, service; Integration: API |
| Projects | `ProjectForm` (React) | `ProjectCreateRequest`, `ProjectResponse` | `ProjectService.create_project()` | `models/project.py`, `services/project_service.py` | Unit: model, service; Integration: API |
| Existing skills | `ExistingSkillsForm` (React) | `StudentSkillCreateRequest`, `StudentSkillResponse` | `StudentSkillService.add_self_reported_skill()` | `models/student_skill.py`, `services/student_skill_service.py` | Unit: source tracking, proficiency; Integration: API |
| Resume upload | `ResumeUpload` (React) | `ResumeUploadRequest`, `ResumeUploadResponse` | `ResumeService.upload_resume()` | `models/resume.py`, `services/resume_service.py` | Unit: file validation, storage; Integration: endpoint |
| Resume text extraction | (Handled by backend) | `ResumeTextExtractResponse` | `ResumeService.extract_text()` | `utils/resume_extractor.py` (PDF/DOCX/TXT) | Unit: each extractor with sample files; Integration: upload→extract |
| NLP-based information extraction | (Handled by backend) | `NlpAnalysisResponse` | `NlpService.analyze_text()` | `nlp/nlp_engine.py` (spaCy + EntityRuler) | Unit: tokenization, entity recognition; Integration: text→analysis |
| Skill extraction from resume | (Handled by backend) | `SkillExtractionResponse` | `SkillExtractor.extract_skills()` | `skill_extraction/skill_extractor.py` (pattern + context) | Unit: alias matching, context inference; Integration: NLP→skills |
| Skill normalization | (Handled by backend) | `SkillNormalizationResponse` | `SkillNormalizer.normalize()` | `skill_extraction/skill_normalizer.py` (alias dict, fuzzy match) | Unit: mapping variations, confidence scoring; Integration: extraction→normalization |
| Student skill profile generation | `StudentSkillProfileView` (React) | `StudentSkillProfileResponse` | `ProfileService.get_skill_profile()` | `services/profile_service.py` (merge logic) | Unit: merging self-reported & resume skills, proficiency resolution; Integration: API returns profile |

## Explicitly Included Components

### Academic Information
- **Frontend**: Form for degree, major, institution, graduation year, GPA.
- **API**: `POST /api/v1/academic-info`, `GET /api/v1/academic-info/{student_id}`.
- **Backend**: `AcademicInfo` model linked to `Student`; service for CRUD.
- **Tests**: Validation of fields, service logic, API endpoint tests.

### Areas of Interest
- **Frontend**: Multi-select or text input for interests.
- **API**: `POST /api/v1/interests`, `GET /api/v1/interests/{student_id}`.
- **Backend**: `Interest` model; service.
- **Tests**: Similar to academic info.

### Existing Skills
- **Frontend**: Form to add skills with proficiency (self-reported).
- **API**: `POST /api/v1/skills/self-reported`, `GET /api/v1/skills/{student_id}`.
- **Backend**: `StudentSkill` with `source='self_reported'`; service to add/update.
- **Tests**: Source tracking, proficiency enforcement, merge logic.

### Resume Input
- **Frontend**: File upload component (PDF, DOCX, TXT) with drag-and-drop.
- **API**: `POST /api/v1/resumes/upload`.
- **Backend**: `Resume` model; service handles file storage and text extraction.
- **Tests**: File type validation, size limits, storage path.

### Resume Text Extraction
- **Backend**: Utility using `pdfplumber` (PDF), `python-docx` (DOCX), direct read (TXT).
- **Tests**: Sample files for each format; assert text length > 0.

### NLP Processing
- **Backend**: spaCy pipeline with custom `EntityRuler` seeded from skill vocabulary.
- **Steps**: Tokenization → POS → Dependency → EntityRuler → Context filtering.
- **Tests**: Unit tests for each pipeline component; integration test: raw text → extracted entities.

### Skill Extraction
- **Backend**: Two-layer approach:
  1. Pattern-based: fuzzy match (RapidFuzz) against skill aliases.
  2. Context-based: noun phrase chunking around skill verbs.
- **Tests**: Alias mapping, fuzzy thresholds, context extraction (e.g., "proficient in Python").

### Skill Normalization
- **Backend**: Alias dictionary (from `data/skills/skills.json`) + fuzzy fallback.
- **Output**: Canonical skill ID, category, confidence score.
- **Tests**: Mapping variations (JS→JavaScript), confidence scoring, category assignment.

### Student Skill Profile
- **Backend**: Merge self-reported and resume-derived skills:
  - Match by skill ID.
  - Proficiency: take higher of sources; track sources.
  - Output list of `StudentSkill` with `source` array and `confidence`.
- **Tests**: Merge scenarios (conflict, single source, both sources), proficiency resolution.

## Out-of-Scope Items (Explicitly Excluded from Module 1)

The following are **NOT** part of Module 1 implementation:
- A* Search (Algorithm) → Module 3
- Forward Chaining (Algorithm) → Module 4
- Career-role matching / Skill-gap analysis → Module 2
- Learning roadmap generation → Module 3
- Career-readiness scoring / Forward Chaining reasoning → Module 4
- AI Role-Specific Assessment (removed feature) → Not in any module
- Assessment generation, question papers, CSP/backtracking → Removed
- Any functionality that computes readiness, gaps, or learning paths

## Updated Week-1 Demo Definition

The Week-1 demonstration will now show the complete Module 1 flow:

```
Enter Student Information (name, email)
    ↓
Enter Academic Information (degree, major, institution, year, GPA)
    ↓
Select Areas of Interest (multiple)
    ↓
Add Projects (title, description, technologies)
    ↓
Input Existing Skills (with proficiency levels)
    ↓
Upload Resume (PDF/DOCX/TXT)
    ↓
System extracts resume text
    ↓
NLP processing identifies skill entities
    ↓
Skill extraction matches against skill vocabulary
    ↓
Skill normalization maps variants to canonical skills
    ↓
Resume-derived skills merged with self-reported skills
    ↓
Display final Student Skill Profile (table of skill → proficiency)
```

This demonstrates all required inputs and the core output: Student Skill Profile.

## Documentation Updates

See `docs/module-1.md` for:
- Module overview and responsibilities
- Data model diagrams (ERD)
- API/service interface specifications (endpoints, request/response schemas)
- NLP processing pipeline diagram
- Skill extraction and normalization algorithms
- Testing strategy (unit, integration, coverage goals)

## Compliance Notes

- No A* or Forward Chaining logic appears in any Module 1 component.
- All AI/NLP usage is confined to resume text extraction, skill identification, extraction, and normalization (permitted per PROJECT_SPEC.md §9).
- The plan adheres to the locked project scope (only Module 1).
- Foundation and approved architecture remain unchanged.