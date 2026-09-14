import { NavLink, useParams } from 'react-router-dom';
import { Icon } from '../components/Layout';
import { useEffect, useState } from 'react';
import { generateLearningRoadmap, type LearningRoadmapResponse } from '../services/api';

function RoadmapPage() {
  const { roleId } = useParams<{ roleId: string }>();
  const [roadmap, setRoadmap] = useState<LearningRoadmapResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const studentId = typeof window !== 'undefined' ? localStorage.getItem('skillbridge_student_id') : null;

  useEffect(() => {
    let cancelled = false;

    async function loadRoadmap() {
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
        const data = await generateLearningRoadmap(studentId, roleId);
        
        if (!cancelled && data) {
          setRoadmap(data);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.message || 'Failed to generate learning roadmap');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadRoadmap();

    return () => {
      cancelled = true;
    };
  }, [roleId, studentId]);

  if (loading) {
    return (
      <div className="page-enter">
        <div className="page-heading">
          <div>
            <span className="section-kicker">LEARNING INTELLIGENCE</span>
            <h2>Personalized Learning Roadmap</h2>
            <p>A* search will turn your skill gaps into an efficient sequence of learning steps.</p>
          </div>
        </div>
        <section className="roadmap-hero glass-card">
          <div className="roadmap-visual">
            <div className="roadmap-orbit r1"/>
            <div className="roadmap-orbit r2"/>
            <div className="roadmap-core"><Icon name="route" size={28}/></div>
          </div>
          <div className="roadmap-copy">
            <span className="soft-badge">A* READY</span>
            <h3>Your shortest path to the target role</h3>
            <p>Once a career target and skill-gap analysis are available, the A* engine will prioritize prerequisites and learning cost to generate a personalized roadmap.</p>
            <NavLink to="/career" className="primary-button">Start with Career Analysis <Icon name="arrow" size={15}/></NavLink>
          </div>
        </section>
        <section className="timeline-preview">
          <Step n="01" title="Current skill state" text="Your existing strengths become the starting node." active/>
          <Step n="02" title="Skill prerequisites" text="Dependencies shape the possible learning paths."/>
          <Step n="03" title="A* optimization" text="Heuristic search selects an efficient route."/>
          <Step n="04" title="Career-ready state" text="The final path reaches the required skill set."/>
        </section>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-enter">
        <div className="page-heading">
          <div>
            <span className="section-kicker">LEARNING INTELLIGENCE</span>
            <h2>Personalized Learning Roadmap</h2>
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
            <h3>Failed to load roadmap</h3>
            <p>{error}</p>
            <NavLink to="/career" className="primary-button">Start with Career Analysis</NavLink>
          </div>
        </section>
        <section className="timeline-preview">
          <Step n="01" title="Current skill state" text="Your existing strengths become the starting node." active/>
          <Step n="02" title="Skill prerequisites" text="Dependencies shape the possible learning paths."/>
          <Step n="03" title="A* optimization" text="Heuristic search selects an efficient route."/>
          <Step n="04" title="Career-ready state" text="The final path reaches the required skill set."/>
        </section>
      </div>
    );
  }

  if (!roadmap) {
    return (
      <div className="page-enter">
        <div className="page-heading">
          <div>
            <span className="section-kicker">LEARNING INTELLIGENCE</span>
            <h2>Personalized Learning Roadmap</h2>
          </div>
        </div>
        <section className="roadmap-hero glass-card">
          <div className="roadmap-visual">
            <div className="roadmap-orbit r1"/>
            <div className="roadmap-orbit r2"/>
            <div className="roadmap-core"><Icon name="route" size={28}/></div>
          </div>
          <div className="roadmap-copy">
            <span className="soft-badge">A* READY</span>
            <h3>Your shortest path to the target role</h3>
            <p>Once a career target and skill-gap analysis are available, the A* engine will prioritize prerequisites and learning cost to generate a personalized roadmap.</p>
            <NavLink to="/career" className="primary-button">Start with Career Analysis <Icon name="arrow" size={15}/></NavLink>
          </div>
        </section>
        <section className="timeline-preview">
          <Step n="01" title="Current skill state" text="Your existing strengths become the starting node." active/>
          <Step n="02" title="Skill prerequisites" text="Dependencies shape the possible learning paths."/>
          <Step n="03" title="A* optimization" text="Heuristic search selects an efficient route."/>
          <Step n="04" title="Career-ready state" text="The final path reaches the required skill set."/>
        </section>
      </div>
    );
  }

  // Roadmap is loaded - display it
  const steps = roadmap.roadmap.learning_steps;
  const totalCost = roadmap.roadmap.total_estimated_cost;
  const goalReached = roadmap.goal_reached;
  const algorithm = roadmap.algorithm;

  return (
    <div className="page-enter">
      <div className="page-heading">
        <div>
          <span className="section-kicker">LEARNING INTELLIGENCE</span>
          <h2>Personalized Learning Roadmap</h2>
        </div>
      </div>

      <section className="roadmap-hero glass-card">
        <div className="roadmap-visual">
          <div className="roadmap-orbit r1"/>
          <div className="roadmap-orbit r2"/>
          <div className="roadmap-core">
            <Icon name="route" size={28}/>
          </div>
        </div>
        <div className="roadmap-copy">
          <span className="soft-badge">A* GENERATED</span>
          <h3>Target: {roadmap.roadmap.target_role}</h3>
          <p>Personalized learning roadmap generated by A* Search</p>
        </div>
      </section>

      {goalReached ? (
        <p className="success-text">Congratulations! You already have all the skills required for this role.</p>
      ) : (
        <div className="roadmap-details">
          <h3>Learning Path</h3>
          <ol className="learning-steps-list">
            {steps.map((step, index) => (
              <li key={step.skill_id} className="learning-step-item">
                <div className="step-info">
                  <span className="step-number">{index + 1}</span>
                  <span className="skill-name">{step.skill_name}</span>
                  <div className="proficiency-bar">
                    <span className="current-prof">{step.current_proficiency}</span>
                    <span className="target-prof">{step.target_proficiency}</span>
                  </div>
                </div>
                <div className="step-details">
                  <span className="estimated-cost">{step.estimated_cost}</span>
                  <span className="reason">{step.reason}</span>
                  {step.prerequisites && step.prerequisites.length > 0 && (
                    <span className="prerequisites">
                      Prerequisites: {step.prerequisites.join(', ')}
                    </span>
                  )}
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}

      <div className="roadmap-footer">
        <div className="total-cost">
          Total estimated learning cost: {totalCost}
        </div>
        <div className="algorithm-info">
          Algorithm: {algorithm}
        </div>
        <NavLink to="/career" className="primary-button">
          Back to Career Analysis <Icon name="arrow" size={15}/>
        </NavLink>
      </div>
    </div>
  );
}

function Step({n, title, text, active}: {n: string; title: string; text: string; active?: boolean}) {
  return (
    <div className={`timeline-step ${active ? 'active' : ''}`}>
      <div className="timeline-number">{n}</div>
      <div>
        <strong>{title}</strong>
        <p>{text}</p>
      </div>
    </div>
  );
}

export default RoadmapPage;
