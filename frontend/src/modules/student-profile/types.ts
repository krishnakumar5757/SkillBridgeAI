/**
 * SkillBridge AI — Module 1: Student Intelligence Types
 *
 * TypeScript types for Module 1 entities, mirroring the backend Pydantic schemas.
 */

export interface StudentProfileCreateRequest {
  first_name: string;
  last_name: string;
  email: string;
}

export interface StudentProfileResponse {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  created_at: string; // ISO string
  updated_at: string; // ISO string
}

export interface AcademicInfoCreateRequest {
  institution: string;
  degree: string;
  major?: string | null;
  graduation_year?: number | null;
  gpa?: number | null;
}

export interface AcademicInfoResponse {
  id: string;
  student_id: string;
  institution: string;
  degree: string;
  major: string | null;
  graduation_year: number | null;
  gpa: number | null;
  created_at: string; // ISO string
  updated_at: string; // ISO string
}

export interface InterestCreateRequest {
  name: string;
}

export interface InterestResponse {
  id: string;
  student_id: string;
  name: string;
  created_at: string; // ISO string
  updated_at: string; // ISO string
}

export interface ProjectCreateRequest {
  title: string;
  description?: string | null;
  technologies?: string | null;
}

export interface ProjectResponse {
  id: string;
  student_id: string;
  title: string;
  description: string | null;
  technologies: string | null;
  created_at: string; // ISO string
  updated_at: string; // ISO string
}

export interface StudentSkillCreateRequest {
  skill_id: string;
  proficiency: 'beginner' | 'intermediate' | 'advanced';
}

export interface StudentSkillResponse {
  id: string;
  student_id: string;
  skill_id: string;
  proficiency: string;
  source: string;
  confidence: number;
  created_at: string; // ISO string
  updated_at: string; // ISO string
}

export interface ResumeUploadResponse {
  resume_id: string;
  file_name: string;
  status: string;
  message: string;
}
