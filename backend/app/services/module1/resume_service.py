"""
SkillBridge AI — Resume Service

Handles resume upload, text extraction, skill extraction, and storage.
"""
from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.skill import Skill
from app.models.student import Resume, Student
from app.nlp.nlp_engine import NlpEngine
from app.services.module1 import student_skill_service
from app.skill_extraction.skill_extractor import SkillExtractor
from app.utils import get_skill_id_by_name


class ResumeService:
    """Service for handling resume uploads and processing."""

    def __init__(self):
        """Initialize the resume service."""
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.resume_dir = self.upload_dir / "resumes"
        self.resume_dir.mkdir(parents=True, exist_ok=True)
        self.skill_extractor = SkillExtractor()
        self.nlp_engine = NlpEngine()

    def _validate_file(self, file: UploadFile) -> None:
        """Validate the uploaded file.
        Checks file size and MIME type.
        Raises ValueError if validation fails.
        """
        # Check file size (limit to 5 MB)
        max_size = 5 * 1024 * 1024  # 5 MB
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)  # reset pointer
        if file_size > max_size:
            raise ValueError(
                f"File size {file_size} bytes exceeds maximum allowed size of {max_size} bytes"
            )

        # Check MIME type
        allowed_mime_types = {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
        }
        if file.content_type not in allowed_mime_types:
            raise ValueError(
                f"Unsupported file type: {file.content_type}. "
                f"Allowed types: {', '.join(allowed_mime_types)}"
            )

    def _save_file(self, file: UploadFile, student_id: str) -> tuple[str, str]:
        """Save the uploaded file to disk.
        Returns:
            tuple: (file_path, file_name) where file_path is the absolute path
                   and file_name is the original filename.
        """
        # Create student-specific directory
        student_dir = self.resume_dir / student_id
        student_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename to prevent path traversal attacks
        # Keep only the basename of the file to prevent directory traversal
        file_name = os.path.basename(file.filename)
        # If the filename becomes empty after sanitization, use a default
        if not file_name:
            file_name = "uploaded_file"

        # Generate a unique filename to avoid collisions
        # Use UUID to ensure uniqueness and prevent overwriting
        file_uuid = uuid.uuid4()
        # Keep the original file extension if it exists
        _, ext = os.path.splitext(file_name)
        unique_filename = f"{file_uuid}{ext}"
        file_path = student_dir / unique_filename

        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return str(file_path), file_name

    def upload_resume(
        self, db: Session, student_id: str, file: UploadFile
    ) -> Resume:
        """Upload and process a resume for a student.
        Steps:
        1. Validate the file.
        2. Save the file to disk.
        3. Extract text from the file.
        4. Extract skills from the text.
        5. Delete any existing resume-derived skills for the student.
        6. Add the extracted skills as resume-derived skills.
        7. Save the Resume record with extracted text.
        8. Return the Resume object.
        """
        # Verify student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student with id {student_id} not found")

        # Validate the uploaded file
        self._validate_file(file)

        # Save the file
        file_path, file_name = self._save_file(file, student_id)

        # Extract text from the file
        extracted_text = self._extract_text(file_path, file.content_type)

        # Extract skills from the text
        extracted_skills = self._extract_skills(extracted_text)

        # Delete existing resume-derived skills for this student (to avoid duplicates on re-upload)
        student_skill_service.delete_resume_skills_for_student(db, student_id)

        # Add the extracted skills as resume-derived skills
        for skill in extracted_skills:
            # The extractor uses the vocabulary's canonical name as the
            # fallback identifier, while StudentSkill requires the database
            # UUID. Resolve the name at this integration boundary and retain
            # support for vocabularies that already provide database IDs.
            extracted_skill_id = skill["skill_id"]
            database_skill = db.query(Skill).filter(Skill.id == extracted_skill_id).first()
            resolved_skill_id = (
                extracted_skill_id
                if database_skill is not None
                else get_skill_id_by_name(db, skill.get("name"))
            )
            if resolved_skill_id is None:
                raise ValueError(
                    f"Extracted skill '{skill.get('name', extracted_skill_id)}' "
                    "is not present in the skills table"
                )
            student_skill_service.add_resume_skill(
                db,
                student_id=student_id,
                skill_id=resolved_skill_id,
                proficiency=skill.get("proficiency", "beginner"),  # default if not inferred
                confidence=skill["confidence"],
            )

        # Create or update the Resume record
        # Check if a resume already exists for this student
        existing_resume = db.query(Resume).filter(Resume.student_id == student_id).first()
        if existing_resume:
            # Update existing record
            existing_resume.file_name = file_name
            existing_resume.file_path = file_path
            existing_resume.file_size = os.path.getsize(file_path)
            existing_resume.mime_type = file.content_type
            existing_resume.extracted_text = extracted_text
            db.commit()
            db.refresh(existing_resume)
            return existing_resume
        else:
            # Create new record
            db_resume = Resume(
                student_id=student_id,
                file_name=file_name,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                mime_type=file.content_type,
                extracted_text=extracted_text,
            )
            db.add(db_resume)
            db.commit()
            db.refresh(db_resume)
            return db_resume

    def _extract_text(self, file_path: str, mime_type: str | None) -> str:
        """Extract text from a resume file.
        Delegates to the resume extractor utility.
        """
        from app.utils.resume_extractor import extract_resume_text

        return extract_resume_text(file_path, mime_type)

    def _extract_skills(self, text: str) -> list[dict]:
        """Extract skills from resume text.
        Returns a list of dictionaries, each containing:
            - skill_id: canonical skill ID
            - name: skill name
            - category: skill category
            - confidence: confidence score (0.0-1.0)
            - proficiency: inferred proficiency (beginner, intermediate, advanced)
        """
        # Use the skill extractor to get skills with confidence
        raw_skills = self.skill_extractor.extract_skills_from_text(text)

        # Process text with NLP engine to get sentences
        doc = self.nlp_engine.process_text(text)

        # Build a list of sentences with their start and end positions
        sentences = []
        for sent in doc.sents:
            sentences.append({
                "text": sent.text,
                "start": sent.start_char,
                "end": sent.end_char,
            })

        # For each raw skill, infer proficiency from the sentence it appears in
        skills = []
        for skill in raw_skills:
            skill_start = skill["start"]
            skill_end = skill["end"]
            # Find the sentence that contains this skill
            sentence_text = ""
            for sent in sentences:
                if sent["start"] <= skill_start and sent["end"] >= skill_end:
                    sentence_text = sent["text"]
                    break
            # If no sentence found, use the whole text as fallback
            if not sentence_text:
                sentence_text = text

            # Infer proficiency from sentence_text
            proficiency = self._infer_proficiency(sentence_text)

            skills.append(
                {
                    "skill_id": skill["skill_id"],
                    "name": skill["name"],
                    "category": skill["category"],
                    "confidence": skill["confidence"],
                    "proficiency": proficiency,
                }
            )
        return skills

    def _infer_proficiency(self, sentence: str) -> str:
        """Infer proficiency level from a sentence.
        Returns one of: "beginner", "intermediate", "advanced".
        """
        sentence_lower = sentence.lower()
        # Check for advanced indicators
        if any(
            keyword in sentence_lower
            for keyword in [
                "expert",
                "expertise",
                "advanced",
                "highly proficient",
                "extensive experience",
            ]
        ):
            return "advanced"
        # Check for intermediate indicators
        if any(
            keyword in sentence_lower
            for keyword in [
                "proficient",
                "intermediate",
                "solid experience",
                "working knowledge",
            ]
        ):
            return "intermediate"
        # Default to beginner
        return "beginner"

    def get_resume(self, db: Session, student_id: str) -> Resume | None:
        """Get the resume record for a student."""
        return db.query(Resume).filter(Resume.student_id == student_id).first()

    def get_resume_text(self, db: Session, student_id: str) -> str | None:
        """Get the extracted text for a student's resume."""
        resume = self.get_resume(db, student_id)
        return resume.extracted_text if resume else None
