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

type JsonObject = Record<string, unknown>;

export interface LearningRoadmapResponse {
  roadmap: {
    target_role: string;
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
    heuristic_used?: string;
    algorithm: string;
  };
  goal_reached: boolean;
  nodes_expanded: number;
  search_depth: number;
  algorithm: string;
}

export interface CareerReadinessSkill {
  skill_id: string;
  skill_name: string;
  required_proficiency: string;
  current_proficiency: number | null;
  match_status: string;
  priority: string;
  is_core: boolean;
}

export interface CareerReadinessResponse {
  readiness_score: number;
  readiness_level: string;
  total_required_skills: number;
  skills_met: CareerReadinessSkill[];
  skills_missing: CareerReadinessSkill[];
  skills_below: CareerReadinessSkill[];
  coverage_percentage: number;
  proficiency_percentage: number;
  strengths: string[];
  priority_gaps: string[];
  recommendations: string[];
  roadmap_summary: string;
  summary: string;
  algorithm: string;
}

function isJsonObject(value: unknown): value is JsonObject {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function errorMessage(value: unknown, fallback: string): string {
  if (typeof value === 'string' && value.length > 0) {
    return value;
  }

  if (value !== undefined && value !== null) {
    try {
      const serialized = JSON.stringify(value);
      if (serialized) {
        return serialized;
      }
    } catch {
      // Use the status-based fallback below for values that cannot be serialized.
    }
  }

  return fallback;
}

function parseApiError(payload: unknown, status: number): {
  code: string;
  message: string;
  details?: Record<string, unknown>;
} {
  const fallbackMessage = `Request failed with status ${status}`;

  if (isJsonObject(payload)) {
    const structuredError = payload.error;
    if (isJsonObject(structuredError)) {
      return {
        code: errorMessage(structuredError.code, 'UNKNOWN_ERROR'),
        message: errorMessage(structuredError.message, fallbackMessage),
        details: isJsonObject(structuredError.details) ? structuredError.details : undefined,
      };
    }

    if ('detail' in payload) {
      return {
        code: `HTTP_${status}`,
        message: errorMessage(payload.detail, fallbackMessage),
      };
    }
  }

  return {
    code: 'UNKNOWN_ERROR',
    message: fallbackMessage,
  };
}

/** Generic fetch wrapper with error handling. */
export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const isFormData = typeof FormData !== 'undefined' && options?.body instanceof FormData;

  const response = await fetch(url, {
    headers: isFormData ? options?.headers : {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorPayload: unknown;
    try {
      errorPayload = await response.json();
    } catch {
      errorPayload = undefined;
    }

    const errorData = parseApiError(errorPayload, response.status);
    throw new ApiError(
      errorData.code,
      errorData.message,
      response.status,
      errorData.details,
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
  return apiFetch<SkillGapAnalysis>(`/api/v1/skill-gap/analyze?student_id=${studentId}&role_id=${roleId}`, { method: 'POST' });
}

/** Generate a full skill gap report for a student against a career role. */
export async function generateSkillGapReport(
  studentId: string,
  roleId: string,
): Promise<SkillGapReport> {
  return apiFetch<SkillGapReport>(`/api/v1/skill-gap/report?student_id=${studentId}&role_id=${roleId}`, { method: 'POST' });
}

/** Analyze a student's career readiness for a target role. */
export async function analyzeCareerReadiness(
  studentId: string,
  roleId: string,
): Promise<CareerReadinessResponse> {
  return apiFetch<CareerReadinessResponse>(`/api/v1/career-readiness/analyze?student_id=${studentId}&role_id=${roleId}`, { method: 'POST' });
}

/** Generate a personalized learning roadmap using A* Search. */
export async function generateLearningRoadmap(
  studentId: string,
  roleId: string,
): Promise<LearningRoadmapResponse> {
  return apiFetch<LearningRoadmapResponse>(`/api/v1/learning-roadmap/generate?student_id=${studentId}&role_id=${roleId}`, { method: 'POST' });
}
