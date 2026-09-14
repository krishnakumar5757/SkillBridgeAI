import { beforeEach, describe, expect, it, vi } from 'vitest';
import { apiFetch } from '../../services/api';
import { uploadResume } from './service';

vi.mock('../../services/api', () => ({ apiFetch: vi.fn() }));

describe('uploadResume', () => {
  beforeEach(() => vi.clearAllMocks());

  it('sends the file as multipart FormData to the student endpoint', async () => {
    const file = new File(['resume'], 'resume.txt', { type: 'text/plain' });
    vi.mocked(apiFetch).mockResolvedValue({
      resume_id: 'resume-1', file_name: 'resume.txt', status: 'processed', message: 'Done',
    });

    await uploadResume('student-real-id', file);

    expect(apiFetch).toHaveBeenCalledWith(
      '/api/v1/students/student-real-id/resumes/upload',
      expect.objectContaining({ method: 'POST', body: expect.any(FormData) }),
    );
    const options = vi.mocked(apiFetch).mock.calls[0][1];
    expect((options?.body as FormData).get('file')).toBe(file);
  });
});
