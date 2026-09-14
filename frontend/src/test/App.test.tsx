import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import App from '../App';

// Mock the API module so tests don't make real network calls
vi.mock('../services/api', () => ({
  checkHealth: vi.fn(),
  listCareerRoles: vi.fn().mockResolvedValue([]),
  ApiError: class ApiError extends Error {
    constructor(
      public code: string,
      message: string,
      public status: number,
      public details?: Record<string, unknown>,
    ) {
      super(message);
      this.name = 'ApiError';
    }
  },
}));

import { checkHealth } from '../services/api';

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', async () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );
    await waitFor(() => expect(screen.getByText('SkillBridge')).toBeInTheDocument());
  });

  it('renders the dashboard by default', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    );
    await waitFor(() => expect(screen.getByText(/Welcome back/)).toBeInTheDocument());
  });

  it('renders the health page at /health', async () => {
    // Mock a successful health response
    vi.mocked(checkHealth).mockResolvedValue({
      status: 'healthy',
      app: 'SkillBridge AI',
      version: '0.1.0',
      database: 'connected',
    });

    render(
      <MemoryRouter initialEntries={['/health']}>
        <App />
      </MemoryRouter>,
    );

    // Wait for the async health check to complete and the heading to appear
    await waitFor(() => {
      expect(screen.getByText('Backend Health')).toBeInTheDocument();
    });
  });
});
