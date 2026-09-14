import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import ReadinessPage from './ReadinessPage';
import { analyzeCareerReadiness } from '../services/api';

vi.mock('../services/api', () => ({ analyzeCareerReadiness: vi.fn() }));

describe('ReadinessPage numeric proficiency contract', () => {
  beforeEach(() => {
    localStorage.setItem('skillbridge_student_id', 'student-real-id');
    vi.mocked(analyzeCareerReadiness).mockResolvedValue({
      readiness_score: 80, readiness_level: 'Ready', total_required_skills: 1,
      skills_met: [{ skill_id: 'skill-1', skill_name: 'Python', required_proficiency: 'advanced', current_proficiency: 3, match_status: 'Strong', priority: 'critical', is_core: true }],
      skills_missing: [], skills_below: [], coverage_percentage: 100,
      proficiency_percentage: 100, strengths: [], priority_gaps: [], recommendations: [],
      roadmap_summary: '', summary: 'Ready', algorithm: 'Career Readiness Analysis',
    });
  });

  it('accepts and renders a backend response with numeric proficiency', async () => {
    render(
      <MemoryRouter initialEntries={['/readiness/software_engineer']}>
        <Routes><Route path="/readiness/:roleId" element={<ReadinessPage />} /></Routes>
      </MemoryRouter>,
    );

    await waitFor(() => expect(analyzeCareerReadiness).toHaveBeenCalledWith('student-real-id', 'software_engineer'));
    expect(await screen.findByText('80/100')).toBeInTheDocument();
    expect(screen.getByText('100% proficient')).toBeInTheDocument();
  });
});
