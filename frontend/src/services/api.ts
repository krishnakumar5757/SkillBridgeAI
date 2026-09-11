/**
 * SkillBridge AI — API Communication Layer
 *
 * Provides a configured fetch wrapper for communicating with the
 * FastAPI backend. All API calls go through this module to ensure
 * consistent error handling and configuration.
 *
 * During development, Vite's dev-server proxy forwards /api and /health
 * requests to the backend at http://localhost:8000, so we use relative URLs.
 */

import type {
  CareerRoleSummary,
  CareerRoleDetail,
  SkillGapAnalysis,
  SkillGapReport,
  ErrorResponse,
  HealthResponse,
} from '../types';

/** Base URL for API requests. Uses relative paths in dev (proxied by Vite). */
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

/** Custom error class for API errors. */
export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number,
    public details?: Record<string, unknown>,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/** Generic fetch wrapper with error handling. */
export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path}`;

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorData: ErrorResponse;
    try {
      errorData = await response.json();
    } catch {
      errorData = {
        error: {
          code: 'UNKNOWN_ERROR',
          message: `Request failed with status ${response.status}`,
          details: {},
        },
      };
    }
    throw new ApiError(
      errorData.error.code,
      errorData.error.message,
      response.status,
      errorData.error.details,
    );
  }

  return response.json() as Promise<T>;
}

/** Check the backend health endpoint. */
export async function checkHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>('/health');
}

type CareerRolesResponse = {
  roles: CareerRoleSummary[];
  total: number;
};

/** List all available career roles. */
export async function listCareerRoles(): Promise<CareerRoleSummary[]> {
  const data = await apiFetch<CareerRolesResponse>('/api/v1/career-roles');
  return data.roles;
}

/** Get details for a specific career role. */
export async function getCareerRole(roleId: string): Promise<CareerRoleDetail> {
  return apiFetch<CareerRoleDetail>(`/api/v1/career-roles/${roleId}`);
}

/** Analyze skill gaps for a student against a career role. */
export async function analyzeSkillGap(
  studentId: string,
  roleId: string,
): Promise<SkillGapAnalysis> {
  return apiFetch<SkillGapAnalysis>(`/skill-gap/analyze?student_id=${studentId}&role_id=${roleId}`);
}

/** Generate a full skill gap report for a student against a career role. */
export async function generateSkillGapReport(
  studentId: string,
  roleId: string,
): Promise<SkillGapReport> {
  return apiFetch<SkillGapReport>(`/skill-gap/report?student_id=${studentId}&role_id=${roleId}`);
}

/** Analyze a student's career readiness for a target role. */
export async function analyzeCareerReadiness(
  studentId: string,
  roleId: string,
): Promise<{
  readiness_score: number;
  readiness_level: string;
  total_required_skills: number;
  skills_met: Array<{
    skill_id: string;
    skill_name: string;
    required_proficiency: string;
    current_proficiency: string | null;
    match_status: string;
    priority: string;
    is_core: boolean;
  }>;
  skills_missing: Array<{
    skill_id: string;
    skill_name: string;
    required_proficiency: string;
    current_proficiency: string | null;
    match_status: string;
    priority: string;
    is_core: boolean;
  }>;
  skills_below: Array<{
    skill_id: string;
    skill_name: string;
    required_proficiency: string;
    current_proficiency: string | null;
    match_status: string;
    priority: string;
    is_core: boolean;
  }>;
  coverage_percentage: number;
  proficiency_percentage: number;
  strengths: string[];
  priority_gaps: string[];
  recommendations: string[];
  roadmap_summary: string;
  summary: string;
  algorithm: string;
}> {
  return apiFetch<{
    readiness_score: number;
    readiness_level: string;
    total_required_skills: number;
    skills_met: any[];
    skills_missing: any[];
    skills_below: any[];
    coverage_percentage: number;
    proficiency_percentage: number;
    strengths: string[];
    priority_gaps: string[];
    recommendations: string[];
    roadmap_summary: string;
    summary: string;
    algorithm: string;
  }>(`/api/v1/career-readiness/analyze?student_id=${studentId}&role_id=${roleId}`);
}

/** Generate a personalized learning roadmap using A* Search. */
export async function generateLearningRoadmap(
  studentId: string,
  roleId: string,
): Promise<{
  target_role: string;
  goal_reached: boolean;
  roadmap: {
    learning_steps: Array<{
      skill_id: string;
      skill_name: string;
      current_proficiency: string;
      target_proficiency: string;
      estimated_cost: number;
      reason: string;
      priority: string;
      prerequisites?: string[];
    }>;
    total_estimated_cost: number;
    skills_acquired: number;
    skills_remaining: number;
    heuristic_used: string;
    algorithm: string;
  };
  nodes_expanded: number;
  search_depth: number;
  algorithm: string;
}> {
  return apiFetch<{
    target_role: string;
    goal_reached: boolean;
    roadmap: {
      learning_steps: Array<{
        skill_id: string;
        skill_name: string;
        current_proficiency: string;
        target_proficiency: string;
        estimated_cost: number;
        reason: string;
        priority: string;
        prerequisites?: string[];
      }>;
      total_estimated_cost: number;
      skills_acquired: number;
      skills_remaining: number;
      heuristic_used: string;
      algorithm: string;
    };
    nodes_expanded: number;
    search_depth: number;
    algorithm: string;
  }>(`/api/v1/learning-roadmap/generate?student_id=${studentId}&role_id=${roleId}`);
}

