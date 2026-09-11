import { NavLink, useParams } from 'react-router-dom';
import { Icon } from '../components/Layout';
import { useEffect, useState } from 'react';
import { analyzeCareerReadiness } from '../services/api';

function ReadinessPage() {
  const { roleId } = useParams<{ roleId: string }>();
  const [readiness, setReadiness] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const studentId = typeof window !== 'undefined' ? localStorage.getItem('skillbridge_student_id') : null;

  useEffect(() => {
    let cancelled = false;

    async function loadReadiness() {
      if (!roleId) {
        setError('No career role selected');
        setLoading(false);
        return;
      }

      if (!studentId) {
        setError('No student profile found');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data: any = await analyzeCareerReadiness(studentId, roleId);

        if (!cancelled && data) {
          setReadiness(data);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.message || 'Failed to analyze career readiness');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadReadiness();

    return () => {
      cancelled = true;
    };
  }, [roleId, studentId]);

  if (loading) {
    return (
      <div className="page-enter">
        <div className="page-heading">
          <div>
            <span className="section-kicker">CAREER READINESS</span>
            <h2>Career Readiness Assessment</h2>
            <p>Evaluating your skills against the target role...</p>
          </div>
        </div>
        <section className="roadmap-hero glass-card">
          <div className="roadmap-visual">
            <div className="roadmap-orbit r1"/>
            <div className="roadmap-orbit r2"/>
            <div className="roadmap-core"><Icon name="route" size={28}/></div>
          </div>
          <div className="roadmap-copy">
            <span className="soft-badge">READY</span>
            <h3>Assessing career preparedness</h3>
            <p>The career readiness engine evaluates skill coverage, proficiency match, and core skill importance to produce a deterministic 0–100 readiness score.</p>
          </div>
        </section>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-enter">
        <div className="page-heading">
          <div>
            <span className="section-kicker">CAREER READINESS</span>
            <h2>Career Readiness Assessment</h2>
          </div>
        </div>
        <section className="roadmap-hero glass-card">
          <div className="roadmap-visual">
            <div className="roadmap-orbit r1"/>
            <div className="roadmap-orbit r2"/>
            <div className="roadmap-core"><Icon name="error" size={28}/></div>
          </div>
          <div className="roadmap-copy">
            <span className="soft-badge">ERROR</span>
            <h3>Failed to load readiness assessment</h3>
            <p>{error}</p>
            <NavLink to="/career" className="primary-button">Back to Career Analysis</NavLink>
          </div>
        </section>
      </div>
    );
  }

  // Readiness data is loaded - display it
  const score = readiness.readiness_score;
  const level = readiness.readiness_level;
  const coverage = readiness.coverage_percentage;
  const proficiency = readiness.proficiency_percentage;
  const strengths = readiness.strengths;
  const priorityGaps = readiness.priority_gaps;
  const recommendations = readiness.recommendations;
  const roadmapSummary = readiness.roadmap_summary;
  const totalRequired = readiness.total_required_skills;
  const skillsMet = readiness.skills_met.length;
  const skillsMissing = readiness.skills_missing.length;
  const skillsBelow = readiness.skills_below.length;

  // Determine level styling
  let levelClass = 'level-ready';
  let levelText = 'Ready';
  if (level === 'Nearly Ready') {
    levelClass = 'level-nearly-ready';
    levelText = 'Nearly Ready';
  } else if (level === 'Developing') {
    levelClass = 'level-developing';
    levelText = 'Developing';
  } else {
    levelClass = 'level-not-ready';
    levelText = 'Not Ready';
  }

  return (
    <div className="page-enter">
      <div className="page-heading">
        <div>
          <span className="section-kicker">CAREER READINESS</span>
          <h2>Career Readiness Assessment</h2>
        </div>
      </div>

      <section className="readiness-container glass-card">
        <div className="readiness-header">
          <div className="readiness-score">
            <strong>{score}/100</strong>
            <span className={levelClass}>{levelText}</span>
          </div>
          <div className="readiness-details">
            <span className="coverage-percent">{coverage}%</span>
            <span className="proficiency-percent">{proficiency}% proficient</span>
          </div>
        </div>

        <div className="readiness-summary">
          <p>{readiness.summary}</p>
        </div>

        <div className="readiness-breakdown">
          <div className="breakdown-item">
            <strong>{skillsMet} of {totalRequired} skills met</strong>
            <span>{coverage}% skill coverage</span>
          </div>
          <div className="breakdown-item">
            <strong>{proficiency}% proficiency match</strong>
            <span>{skillsMet} of {skillsMet + skillsMissing + skillsBelow} skills evaluated</span>
          </div>
          <div className="breakdown-item">
            <strong>{skillsMissing} skills missing</strong>
            <span>Required but not in your profile</span>
          </div>
          <div className="breakdown-item">
            <strong>{skillsBelow} skills below requirement</strong>
            <span>Have some proficiency, but below required level</span>
          </div>
        </div>

        {strengths.length > 0 && (
          <div className="readiness-strengths">
            <strong>Strengths:</strong>
            <ul>
              {strengths.map((s: string, i: number) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
        )}

        {priorityGaps.length > 0 && (
          <div className="readiness-gaps">
            <strong>Priority gaps:</strong>
            <ul>
              {priorityGaps.map((g: string, i: number) => (
                <li key={i}>{g}</li>
              ))}
            </ul>
          </div>
        )}

        {recommendations.length > 0 && (
          <div className="readiness-recommendations">
            <strong>Recommendations:</strong>
            <ol>
              {recommendations.map((r: string, i: number) => (
                <li key={i}>{r}</li>
              ))}
            </ol>
          </div>
        )}

        {roadmapSummary && (
          <div className="roadmap-summary">
            <strong>Learning path:</strong> {roadmapSummary}
          </div>
        )}

        <div className="readiness-actions">
          {skillsMissing > 0 || skillsBelow > 0 ? (
            <NavLink to="/career" className="primary-button">
              Review skill gaps <Icon name="arrow" size={15}/>
            </NavLink>
          ) : (
            <NavLink to="/roadmap" className="primary-button">
              View learning roadmap <Icon name="arrow" size={15}/>
            </NavLink>
          )}
          <NavLink to="/profile" className="ghost-button">
            Update profile <Icon name="arrow" size={15}/>
          </NavLink>
        </div>
      </section>
    </div>
  );
}

export default ReadinessPage;