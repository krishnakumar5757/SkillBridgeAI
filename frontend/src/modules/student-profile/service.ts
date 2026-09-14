import { apiFetch } from '../../services/api';
import type {
  StudentProfileCreateRequest,
  StudentProfileResponse,
  AcademicInfoCreateRequest,
  AcademicInfoResponse,
  InterestCreateRequest,
  InterestResponse,
  ProjectCreateRequest,
  ProjectResponse,
  StudentSkillCreateRequest,
  StudentSkillResponse,
  ResumeUploadResponse,
} from './types';

/**
 * Module 1 Service — Student Intelligence
 *
 * Wrapper around the backend API for Module 1 endpoints.
 */

/**
 * Create a student profile.
 */
export async function createProfile(
  profile: StudentProfileCreateRequest
): Promise<StudentProfileResponse> {
  return apiFetch<StudentProfileResponse>('/api/v1/profile', {
    method: 'POST',
    body: JSON.stringify(profile),
  });
}

/**
 * Get a student profile by ID.
 */
export async function getProfile(studentId: string): Promise<StudentProfileResponse> {
  return apiFetch<StudentProfileResponse>(`/api/v1/profile/${studentId}`);
}

/**
 * Create academic information for a student.
 */
export async function createAcademicInfo(
  studentId: string,
  academicInfo: AcademicInfoCreateRequest
): Promise<AcademicInfoResponse> {
  return apiFetch<AcademicInfoResponse>(`/api/v1/academic-info?student_id=${studentId}`, {
    method: 'POST',
    body: JSON.stringify(academicInfo),
  });
}

/**
 * Get all academic information records for a student.
 */
export async function getAcademicInfo(studentId: string): Promise<AcademicInfoResponse[]> {
  return apiFetch<AcademicInfoResponse[]>(`/api/v1/academic-info/${studentId}`);
}

/**
 * Create an interest for a student.
 */
export async function createInterest(
  studentId: string,
  interest: InterestCreateRequest
): Promise<InterestResponse> {
  return apiFetch<InterestResponse>(`/api/v1/interests?student_id=${studentId}`, {
    method: 'POST',
    body: JSON.stringify(interest),
  });
}

/**
 * Get all interests for a student.
 */
export async function getInterests(studentId: string): Promise<InterestResponse[]> {
  return apiFetch<InterestResponse[]>(`/api/v1/interests/${studentId}`);
}

/**
 * Create a project for a student.
 */
export async function createProject(
  studentId: string,
  project: ProjectCreateRequest
): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(`/api/v1/projects?student_id=${studentId}`, {
    method: 'POST',
    body: JSON.stringify(project),
  });
}

/**
 * Get all projects for a student.
 */
export async function getProjects(studentId: string): Promise<ProjectResponse[]> {
  return apiFetch<ProjectResponse[]>(`/api/v1/projects/${studentId}`);
}

/**
 * Add a self-reported skill for a student.
 */
export async function addSelfReportedSkill(
  studentId: string,
  skill: StudentSkillCreateRequest
): Promise<StudentSkillResponse> {
  return apiFetch<StudentSkillResponse>(`/api/v1/skills/self-reported?student_id=${encodeURIComponent(studentId)}`, {
    method: 'POST',
    body: JSON.stringify(skill),
  });
}

/**
 * Get all skills for a student.
 */
export async function getSkills(studentId: string): Promise<StudentSkillResponse[]> {
  return apiFetch<StudentSkillResponse[]>(`/api/v1/skills/${studentId}`);
}

/** Upload and process a resume for a student. */
export async function uploadResume(studentId: string, file: File): Promise<ResumeUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  return apiFetch<ResumeUploadResponse>(
    `/api/v1/students/${encodeURIComponent(studentId)}/resumes/upload`,
    { method: 'POST', body: formData },
  );
}
