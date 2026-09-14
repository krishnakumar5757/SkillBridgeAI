import { useEffect, useState } from 'react';
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
import {
  createProfile,
  getProfile,
  createAcademicInfo,
  getAcademicInfo,
  createInterest,
  getInterests,
  createProject,
  getProjects,
  addSelfReportedSkill,
  getSkills,
  uploadResume,
} from './service';

/**
 * SkillBridge AI — Module 1 Student Profile Page
 *
 * Page for creating and viewing a student's profile, academic information,
 * interests, projects, and self-reported skills.
 */
function StudentProfilePage() {
  // State for student profile
  const [profile, setProfile] = useState<StudentProfileResponse | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState<string | null>(null);

  // State for academic information
  const [academicInfos, setAcademicInfos] = useState<AcademicInfoResponse[]>([]);
  const [academicLoading, setAcademicLoading] = useState(false);
  const [academicError, setAcademicError] = useState<string | null>(null);
  const [academicForm, setAcademicForm] = useState<AcademicInfoCreateRequest>({
    institution: '',
    degree: '',
    major: '',
    graduation_year: undefined,
    gpa: undefined,
  });

  // State for interests
  const [interests, setInterests] = useState<InterestResponse[]>([]);
  const [interestLoading, setInterestLoading] = useState(false);
  const [interestError, setInterestError] = useState<string | null>(null);
  const [interestForm, setInterestForm] = useState<InterestCreateRequest>({
    name: '',
  });

  // State for projects
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [projectLoading, setProjectLoading] = useState(false);
  const [projectError, setProjectError] = useState<string | null>(null);
  const [projectForm, setProjectForm] = useState<ProjectCreateRequest>({
    title: '',
    description: '',
    technologies: '',
  });

  // State for skills
  const [skills, setSkills] = useState<StudentSkillResponse[]>([]);
  const [skillLoading, setSkillLoading] = useState(false);
  const [skillError, setSkillError] = useState<string | null>(null);
  const [skillForm, setSkillForm] = useState<StudentSkillCreateRequest>({
    skill_id: '',
    proficiency: 'beginner',
  });

  // State for resume upload
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeLoading, setResumeLoading] = useState(false);
  const [resumeError, setResumeError] = useState<string | null>(null);
  const [resumeResult, setResumeResult] = useState<ResumeUploadResponse | null>(null);

  // Helper to reset form states
  const resetAcademicForm = () => {
    setAcademicForm({
      institution: '',
      degree: '',
      major: '',
      graduation_year: undefined,
      gpa: undefined,
    });
  };

  const resetInterestForm = () => {
    setInterestForm({ name: '' });
  };

  const resetProjectForm = () => {
    setProjectForm({ title: '', description: '', technologies: '' });
  };

  const resetSkillForm = () => {
    setSkillForm({ skill_id: '', proficiency: 'beginner' });
  };

  // Effect to fetch profile data when we have a student ID from URL or state
  // Restore the existing profile after a browser refresh when an ID is stored.
  useEffect(() => {
    const studentId = typeof window !== 'undefined'
      ? localStorage.getItem('skillbridge_student_id')
      : null;
    if (!studentId) return;

    let cancelled = false;
    setProfileLoading(true);
    setProfileError(null);
    getProfile(studentId)
      .then((data) => {
        if (!cancelled) {
          setProfile(data);
          setProfileForm((current) => (
            current.first_name || current.last_name || current.email
              ? current
              : {
                  first_name: data.first_name,
                  last_name: data.last_name,
                  email: data.email,
                }
          ));
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setProfileError(err instanceof Error ? err.message : 'Unable to load the saved student profile');
        }
      })
      .finally(() => {
        if (!cancelled) setProfileLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Fetch academic information when student ID changes
  useEffect(() => {
    if (profile?.id) {
      fetchAcademicInfo();
    }
  }, [profile?.id]);

  // Fetch interests when student ID changes
  useEffect(() => {
    if (profile?.id) {
      fetchInterests();
    }
  }, [profile?.id]);

  // Fetch projects when student ID changes
  useEffect(() => {
    if (profile?.id) {
      fetchProjects();
    }
  }, [profile?.id]);

  // Fetch skills when student ID changes
  useEffect(() => {
    if (profile?.id) {
      fetchSkills();
    }
  }, [profile?.id]);

  // Async functions to fetch data
  const fetchAcademicInfo = async () => {
    if (!profile?.id) return;
    setAcademicLoading(true);
    setAcademicError(null);
    try {
      const data = await getAcademicInfo(profile.id);
      setAcademicInfos(data);
    } catch (err) {
      if (err instanceof Error) {
        setAcademicError(err.message);
      } else {
        setAcademicError('An unknown error occurred');
      }
    } finally {
      setAcademicLoading(false);
    }
  };

  const fetchInterests = async () => {
    if (!profile?.id) return;
    setInterestLoading(true);
    setInterestError(null);
    try {
      const data = await getInterests(profile.id);
      setInterests(data);
    } catch (err) {
      if (err instanceof Error) {
        setInterestError(err.message);
      } else {
        setInterestError('An unknown error occurred');
      }
    } finally {
      setInterestLoading(false);
    }
  };

  const fetchProjects = async () => {
    if (!profile?.id) return;
    setProjectLoading(true);
    setProjectError(null);
    try {
      const data = await getProjects(profile.id);
      setProjects(data);
    } catch (err) {
      if (err instanceof Error) {
        setProjectError(err.message);
      } else {
        setProjectError('An unknown error occurred');
      }
    } finally {
      setProjectLoading(false);
    }
  };

  const fetchSkills = async () => {
    if (!profile?.id) return;
    setSkillLoading(true);
    setSkillError(null);
    try {
      const data = await getSkills(profile.id);
      setSkills(data);
    } catch (err) {
      if (err instanceof Error) {
        setSkillError(err.message);
      } else {
        setSkillError('An unknown error occurred');
      }
    } finally {
      setSkillLoading(false);
    }
  };

  // Form submission handlers
  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileLoading(true);
    setProfileError(null);
    try {
      const data = await createProfile({
        first_name: profileForm.first_name,
        last_name: profileForm.last_name,
        email: profileForm.email,
      });
      setProfile(data);
      // Persist student ID and name to localStorage for other frontend parts
      if (typeof window !== 'undefined') {
        localStorage.setItem('skillbridge_student_id', data.id);
        localStorage.setItem('skillbridge_student_name', `${data.first_name} ${data.last_name}`);
      }
      // After creating profile, we will fetch the lists in the useEffects above
    } catch (err) {
      if (err instanceof Error) {
        setProfileError(err.message);
      } else {
        setProfileError('An unknown error occurred');
      }
    } finally {
      setProfileLoading(false);
    }
  };

  const handleAcademicSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile?.id) {
      setAcademicError('Please create a student profile first');
      return;
    }
    setAcademicLoading(true);
    setAcademicError(null);
    try {
      const data = await createAcademicInfo(profile.id, academicForm);
      setAcademicInfos([...academicInfos, data]);
      resetAcademicForm();
    } catch (err) {
      if (err instanceof Error) {
        setAcademicError(err.message);
      } else {
        setAcademicError('An unknown error occurred');
      }
    } finally {
      setAcademicLoading(false);
    }
  };

  const handleInterestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile?.id) {
      setInterestError('Please create a student profile first');
      return;
    }
    setInterestLoading(true);
    setInterestError(null);
    try {
      const data = await createInterest(profile.id, interestForm);
      setInterests([...interests, data]);
      resetInterestForm();
    } catch (err) {
      if (err instanceof Error) {
        setInterestError(err.message);
      } else {
        setInterestError('An unknown error occurred');
      }
    } finally {
      setInterestLoading(false);
    }
  };

  const handleProjectSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile?.id) {
      setProjectError('Please create a student profile first');
      return;
    }
    setProjectLoading(true);
    setProjectError(null);
    try {
      const data = await createProject(profile.id, projectForm);
      setProjects([...projects, data]);
      resetProjectForm();
    } catch (err) {
      if (err instanceof Error) {
        setProjectError(err.message);
      } else {
        setProjectError('An unknown error occurred');
      }
    } finally {
      setProjectLoading(false);
    }
  };

  const handleSkillSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile?.id) {
      setSkillError('Please create a student profile first');
      return;
    }
    setSkillLoading(true);
    setSkillError(null);
    try {
      const data = await addSelfReportedSkill(profile.id, skillForm);
      setSkills([...skills, data]);
      resetSkillForm();
    } catch (err) {
      if (err instanceof Error) {
        setSkillError(err.message);
      } else {
        setSkillError('An unknown error occurred');
      }
    } finally {
      setSkillLoading(false);
    }
  };

  const handleResumeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setResumeError(null);
    setResumeResult(null);

    if (!resumeFile) {
      setResumeError('Please select a resume file first');
      return;
    }

    const studentId = typeof window !== 'undefined'
      ? localStorage.getItem('skillbridge_student_id')
      : null;
    if (!studentId) {
      setResumeError('Please create a student profile before uploading a resume');
      return;
    }

    setResumeLoading(true);
    try {
      const result = await uploadResume(studentId, resumeFile);
      setResumeResult(result);
      setResumeFile(null);
    } catch (err) {
      setResumeError(err instanceof Error ? err.message : 'Unable to upload and process the resume');
    } finally {
      setResumeLoading(false);
    }
  };

  // Profile form state
  const [profileForm, setProfileForm] = useState<StudentProfileCreateRequest>({
    first_name: '',
    last_name: '',
    email: '',
  });

  return (
    <div className="student-profile-page">
      <h1>Student Profile</h1>

      {/* Student Profile Form */}
      <section className="profile-form-section">
        <h2>Student Information</h2>
        <form onSubmit={handleProfileSubmit}>
          <div>
            <label>
              First Name:
              <input
                type="text"
                value={profileForm.first_name}
                onChange={(e) => setProfileForm({ ...profileForm, first_name: e.target.value })}
                required
                disabled={profileLoading}
              />
            </label>
          </div>
          <div>
            <label>
              Last Name:
              <input
                type="text"
                value={profileForm.last_name}
                onChange={(e) => setProfileForm({ ...profileForm, last_name: e.target.value })}
                required
                disabled={profileLoading}
              />
            </label>
          </div>
          <div>
            <label>
              Email:
              <input
                type="email"
                value={profileForm.email}
                onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                required
                disabled={profileLoading}
              />
            </label>
          </div>
          <button type="submit" disabled={profileLoading}>
            {profileLoading ? 'Creating...' : 'Create Profile'}
          </button>
          {profileError && <p className="error">{profileError}</p>}
        </form>

        {profile && (
          <div className="profile-display">
            <h3>Created Profile</h3>
            <p>
              <strong>ID:</strong> {profile.id}
            </p>
            <p>
              <strong>Name:</strong> {profile.first_name} {profile.last_name}
            </p>
            <p>
              <strong>Email:</strong> {profile.email}
            </p>
          </div>
        )}
      </section>

      {/* Resume Upload */}
      <section className="resume-form-section">
        <h2>Resume</h2>
        <form onSubmit={handleResumeSubmit}>
          <label>
            Resume file:
            <input
              type="file"
              accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
              onChange={(e) => setResumeFile(e.target.files?.[0] ?? null)}
              disabled={resumeLoading}
            />
          </label>
          <button type="submit" disabled={resumeLoading}>
            {resumeLoading ? 'Uploading and processing...' : 'Upload Resume'}
          </button>
          {resumeError && <p className="error" role="alert">{resumeError}</p>}
          {resumeResult && (
            <p className="success" role="status">
              {resumeResult.message || 'Resume processed successfully.'}
              {resumeResult.file_name ? ` (${resumeResult.file_name})` : ''}
            </p>
          )}
        </form>
      </section>

      {/* Academic Information Form */}
      {profile && (
        <>
          <section className="academic-form-section">
            <h2>Academic Information</h2>
            <form onSubmit={handleAcademicSubmit}>
              <div>
                <label>
                  Institution:
                  <input
                    type="text"
                    value={academicForm.institution}
                    onChange={(e) => setAcademicForm({ ...academicForm, institution: e.target.value })}
                    required
                    disabled={academicLoading}
                  />
                </label>
              </div>
              <div>
                <label>
                  Degree:
                  <input
                    type="text"
                    value={academicForm.degree}
                    onChange={(e) => setAcademicForm({ ...academicForm, degree: e.target.value })}
                    required
                    disabled={academicLoading}
                  />
                </label>
              </div>
              <div>
                <label>
                  Major:
                  <input
                    type="text"
                    value={academicForm.major ?? ''}
                    onChange={(e) => setAcademicForm({ ...academicForm, major: e.target.value || undefined })}
                    disabled={academicLoading}
                  />
                </label>
              </div>
              <div>
                <label>
                  Graduation Year:
                  <input
                    type="number"
                    value={academicForm.graduation_year ?? 0}
                    onChange={(e) => {
                      const val = e.target.value;
                      setAcademicForm({ ...academicForm, graduation_year: val ? parseInt(val, 10) : undefined });
                    }}
                    disabled={academicLoading}
                  />
                </label>
              </div>
              <div>
                <label>
                  GPA:
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="4"
                    value={academicForm.gpa ?? 0}
                    onChange={(e) => {
                      const val = e.target.value;
                      setAcademicForm({ ...academicForm, gpa: val ? parseFloat(val) : undefined });
                    }}
                    disabled={academicLoading}
                  />
                </label>
              </div>
              <button type="submit" disabled={academicLoading}>
                {academicLoading ? 'Adding...' : 'Add Academic Info'}
              </button>
              {academicError && <p className="error">{academicError}</p>}
            </form>

            {academicInfos.length > 0 && (
              <div className="academic-list">
                <h3>Saved Academic Information</h3>
                <ul>
                  {academicInfos.map((info) => (
                    <li key={info.id}>
                      <strong>{info.institution}</strong> - {info.degree}{info.major ? ` (${info.major})` : ''}
                      {info.graduation_year ? `, ${info.graduation_year}` : ''}
                      {info.gpa !== null && info.gpa !== undefined ? `, GPA: ${info.gpa}` : ''}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        </>
      )}

      {/* Interests Form */}
      {profile && (
        <>
          <section className="interest-form-section">
            <h2>Areas of Interest</h2>
            <form onSubmit={handleInterestSubmit}>
              <div>
                <label>
                  Interest:
                  <input
                    type="text"
                    value={interestForm.name}
                    onChange={(e) => setInterestForm({ ...interestForm, name: e.target.value })}
                    required
                    disabled={interestLoading}
                  />
                </label>
              </div>
              <button type="submit" disabled={interestLoading}>
                {interestLoading ? 'Adding...' : 'Add Interest'}
              </button>
              {interestError && <p className="error">{interestError}</p>}
            </form>

            {interests.length > 0 && (
              <div className="interest-list">
                <h3>Saved Interests</h3>
                <ul>
                  {interests.map((interest) => (
                    <li key={interest.id}>
                      {interest.name}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        </>
      )}

      {/* Projects Form */}
      {profile && (
        <>
          <section className="project-form-section">
            <h2>Projects</h2>
            <form onSubmit={handleProjectSubmit}>
              <div>
                <label>
                  Title:
                  <input
                    type="text"
                    value={projectForm.title}
                    onChange={(e) => setProjectForm({ ...projectForm, title: e.target.value })}
                    required
                    disabled={projectLoading}
                  />
                </label>
              </div>
              <div>
                <label>
                  Description:
                  <textarea
                    value={projectForm.description ?? ''}
                    onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value || undefined })}
                    disabled={projectLoading}
                  />
                </label>
              </div>
              <div>
                <label>
                  Technologies:
                  <input
                    type="text"
                    value={projectForm.technologies ?? ''}
                    onChange={(e) => setProjectForm({ ...projectForm, technologies: e.target.value || undefined })}
                    disabled={projectLoading}
                  />
                </label>
              </div>
              <button type="submit" disabled={projectLoading}>
                {projectLoading ? 'Adding...' : 'Add Project'}
              </button>
              {projectError && <p className="error">{projectError}</p>}
            </form>

            {projects.length > 0 && (
              <div className="project-list">
                <h3>Saved Projects</h3>
                <ul>
                  {projects.map((project) => (
                    <li key={project.id}>
                      <strong>{project.title}</strong>
                      {project.description ? ` - ${project.description}` : ''}
                      {project.technologies ? ` (${project.technologies})` : ''}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        </>
      )}

      {/* Skills Form */}
      {profile && (
        <>
          <section className="skill-form-section">
            <h2>Existing Skills (Self-reported)</h2>
            <form onSubmit={handleSkillSubmit}>
              <div>
                <label>
                  Skill ID:
                  <input
                    type="text"
                    value={skillForm.skill_id}
                    onChange={(e) => setSkillForm({ ...skillForm, skill_id: e.target.value })}
                    required
                    disabled={skillLoading}
                  />
                </label>
              </div>
              <div>
                <label>
                  Proficiency:
                  <select
                    value={skillForm.proficiency}
                    onChange={(e) => setSkillForm({ ...skillForm, proficiency: e.target.value as 'beginner' | 'intermediate' | 'advanced' })}
                    disabled={skillLoading}
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </label>
              </div>
              <button type="submit" disabled={skillLoading}>
                {skillLoading ? 'Adding...' : 'Add Skill'}
              </button>
              {skillError && <p className="error">{skillError}</p>}
            </form>

            {skills.length > 0 && (
              <div className="skill-list">
                <h3>Saved Skills</h3>
                <ul>
                  {skills.map((skill) => (
                    <li key={skill.id}>
                      <strong>{skill.skill_id}</strong> - {skill.proficiency} (Source: {skill.source})
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}

export default StudentProfilePage;
