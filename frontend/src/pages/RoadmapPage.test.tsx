import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import RoadmapPage from './RoadmapPage';
import { generateLearningRoadmap } from '../services/api';

vi.mock('../services/api', () => ({ generateLearningRoadmap: vi.fn() }));

describe('RoadmapPage response contract', () => {
  beforeEach(() => {
    localStorage.setItem('skillbridge_student_id', 'student-real-id');
    vi.mocked(generateLearningRoadmap).mockResolvedValue({
      roadmap: {
        target_role: 'software_engineer', learning_steps: [], total_estimated_cost: 0,
        skills_acquired: 7, skills_remaining: 0, algorithm: 'A* Search',
      },
      goal_reached: true, nodes_expanded: 0, search_depth: 0, algorithm: 'A* Search',
    });
  });

  it('reads target_role from the nested roadmap response', async () => {
    render(
      <MemoryRouter initialEntries={['/roadmap/software_engineer']}>
        <Routes><Route path="/roadmap/:roleId" element={<RoadmapPage />} /></Routes>
      </MemoryRouter>,
    );

    await waitFor(() => expect(generateLearningRoadmap).toHaveBeenCalledWith('student-real-id', 'software_engineer'));
    expect(await screen.findByText('Target: software_engineer')).toBeInTheDocument();
  });
});
