import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import StudentProfilePage from './StudentProfilePage';
import { getProfile, uploadResume } from './service';

vi.mock('./service', async () => {
  const actual = await vi.importActual<typeof import('./service')>('./service');
  return { ...actual, getProfile: vi.fn(), uploadResume: vi.fn() };
});

const mockedGetProfile = vi.mocked(getProfile);
const mockedUploadResume = vi.mocked(uploadResume);

function selectResume() {
  if (!screen.queryByRole('heading', { name: 'Student Profile' })) {
    render(<StudentProfilePage />);
  }
  const file = new File(['resume text'], 'resume.txt', { type: 'text/plain' });
  fireEvent.change(screen.getByLabelText('Resume file:'), { target: { files: [file] } });
  return file;
}

describe('StudentProfilePage resume upload', () => {
  beforeEach(() => {
    localStorage.clear();
    mockedGetProfile.mockReset();
    mockedGetProfile.mockResolvedValue({
      id: 'student-real-id', first_name: 'Saved', last_name: 'Student', email: 'saved@example.com',
      created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z',
    });
    mockedUploadResume.mockReset();
  });

  it('hydrates the saved profile using the stored student ID', async () => {
    localStorage.setItem('skillbridge_student_id', 'student-real-id');
    mockedGetProfile.mockResolvedValue({
      id: 'student-real-id', first_name: 'Saved', last_name: 'Student', email: 'saved@example.com',
      created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z',
    });

    render(<StudentProfilePage />);

    await waitFor(() => expect(mockedGetProfile).toHaveBeenCalledWith('student-real-id'));
    expect(await screen.findByText('Saved Student')).toBeInTheDocument();
    expect(screen.getByLabelText('First Name:')).toHaveValue('Saved');
    expect(screen.getByLabelText('Email:')).toHaveValue('saved@example.com');
  });

  it('uploads using the real student ID stored in localStorage', async () => {
    localStorage.setItem('skillbridge_student_id', 'student-real-id');
    const file = selectResume();
    mockedUploadResume.mockResolvedValue({
      resume_id: 'resume-1', file_name: 'resume.txt', status: 'processed', message: 'Resume processed successfully.',
    });

    fireEvent.click(screen.getByRole('button', { name: 'Upload Resume' }));

    await waitFor(() => expect(mockedUploadResume).toHaveBeenCalledWith('student-real-id', file));
  });

  it('shows a successful processing message', async () => {
    localStorage.setItem('skillbridge_student_id', 'student-real-id');
    selectResume();
    mockedUploadResume.mockResolvedValue({
      resume_id: 'resume-1', file_name: 'resume.txt', status: 'processed', message: 'Resume processed successfully.',
    });

    fireEvent.click(screen.getByRole('button', { name: 'Upload Resume' }));

    expect(await screen.findByRole('status')).toHaveTextContent('Resume processed successfully.');
  });

  it('shows backend errors without crashing', async () => {
    localStorage.setItem('skillbridge_student_id', 'student-real-id');
    selectResume();
    mockedUploadResume.mockRejectedValue(new Error('Unsupported file type'));

    fireEvent.click(screen.getByRole('button', { name: 'Upload Resume' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('Unsupported file type');
  });

  it('does not request an upload when the student ID is missing', async () => {
    selectResume();

    fireEvent.click(screen.getByRole('button', { name: 'Upload Resume' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('create a student profile');
    expect(mockedUploadResume).not.toHaveBeenCalled();
  });

  it('prevents duplicate submissions while processing', async () => {
    localStorage.setItem('skillbridge_student_id', 'student-real-id');
    selectResume();
    let resolveUpload: (value: Awaited<ReturnType<typeof uploadResume>>) => void = () => undefined;
    mockedUploadResume.mockReturnValue(new Promise((resolve) => { resolveUpload = resolve; }));

    const button = screen.getByRole('button', { name: 'Upload Resume' });
    fireEvent.click(button);
    fireEvent.click(button);

    expect(mockedUploadResume).toHaveBeenCalledTimes(1);
    resolveUpload({
      resume_id: 'resume-1', file_name: 'resume.txt', status: 'processed', message: 'Done',
    });
    await screen.findByRole('status');
  });
});
