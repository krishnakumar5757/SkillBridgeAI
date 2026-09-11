/**
 * SkillBridge AI — Shared TypeScript Types
 *
 * Common types used across the frontend. Module-specific types will be
 * added in their respective module directories.
 */

/** Health check response from the backend. */
export interface HealthResponse {
  status: string;
  app: string;
  version: string;
  database: string;
}

/** Standard error response from the backend (Architecture Section 9.8). */
export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
  };
}

/** Career role summary from the roles data. */
export interface CareerRoleSummary {
  id: string;
  name: string;
  description: string;
  category: string;
  required_skill_count: number;
  critical_skills: number;
  core_skills: number;
}

/** Detailed career role information. */
export interface CareerRoleDetail {
  id: string;
  name: string;
  description: string;
  category: string;
  required_skills: Array<{
    skill_id: string;
    minimum_proficiency: string;
    priority: string;
    is_core: boolean;
    skill_name?: string;
  }>;
  priority_breakdown: Record<string, number>;
  total_required_skills: number;
  core_skill_count: number;
}

/** Skill gap analysis result types. */
export enum MatchStatus {
  STRONG = 'strong',
  WEAK = 'weak',
  MISSING = 'missing',
}

export interface SkillGapMatch {
  match_status: MatchStatus;
  skill_id: string;
  skill_name: string;
  required_proficiency: string;
  current_proficiency: string | null;
  gap_score: number;
  priority: string;
  is_core: boolean;
}

export interface SkillGapAnalysis {
  student_id: string;
  role_id: string;
  role_name: string;
  total_required_skills: number;
  matched_strong: SkillGapMatch[];
  matched_weak: SkillGapMatch[];
  matched_missing: SkillGapMatch[];
  prioritized_missing: SkillGapMatch[];
  prioritized_weak: SkillGapMatch[];
  skill_coverage_percent: number;
  core_skill_coverage_percent: number;
  critical_skill_coverage_percent: number;
  total_skills_acquired: number;
  total_skills_required: number;
  summary: {
    strong_count: number;
    weak_count: number;
    missing_count: number;
    total_gaps: number;
  };
}

/** Skill gap report types. */
export interface SkillGapReport {
  student_id: string;
  role_id: string;
  role_name: string;
  total_required_skills: number;
  skill_coverage_percent: number;
  core_skill_coverage_percent: number;
  critical_skill_coverage_percent: number;
  total_skills_acquired: number;
  total_skills_required: number;
  matched_strong: SkillGapMatch[];
  matched_weak: SkillGapMatch[];
  matched_missing: SkillGapMatch[];
  prioritized_missing: SkillGapMatch[];
  prioritized_weak: SkillGapMatch[];
  summary: {
    strong_count: number;
    weak_count: number;
    missing_count: number;
    total_gaps: number;
  };
}