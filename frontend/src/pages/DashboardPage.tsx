import { useEffect, useMemo, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { analyzeSkillGap, listCareerRoles } from '../services/api';
import type { CareerRoleSummary, SkillGapAnalysis } from '../types';
import { Icon } from '../components/Layout';

function DashboardPage() {
  const [roles, setRoles] = useState<CareerRoleSummary[]>([]);
  const [role, setRole] = useState<CareerRoleSummary | null>(null);
  const [roleSelectionInitialized, setRoleSelectionInitialized] = useState(false);
  const [gap, setGap] = useState<SkillGapAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState(false);
  const name = typeof window !== 'undefined' ? localStorage.getItem('skillbridge_student_name') : null;
  const studentId = typeof window !== 'undefined' ? localStorage.getItem('skillbridge_student_id') : null;
  const storedRoleId = typeof window !== 'undefined' ? localStorage.getItem('skillbridge_selected_role_id') : null;

  useEffect(() => {
    listCareerRoles().then((data) => setRoles(data)).catch(() => setApiError(true));
  }, []);
  useEffect(() => {
    let cancelled = false;

    if (!role || !studentId) { setGap(null); setLoading(false); return () => undefined; }
    setGap(null);
    setLoading(true);
    analyzeSkillGap(studentId, role.id)
      .then((data) => { if (!cancelled) setGap(data); })
      .catch(() => { if (!cancelled) { setGap(null); setApiError(true); } })
      .finally(() => { if (!cancelled) setLoading(false); });

    return () => { cancelled = true; };
  }, [role, studentId]);
  useEffect(() => {
    if (roles.length && !role && !roleSelectionInitialized) {
      setRole(roles.find((candidate) => candidate.id === storedRoleId) ?? roles[0]);
      setRoleSelectionInitialized(true);
    }
  }, [roles, role, roleSelectionInitialized, storedRoleId]);
  useEffect(() => {
    if (role && typeof window !== 'undefined') {
      localStorage.setItem('skillbridge_selected_role_id', role.id);
      window.dispatchEvent(new CustomEvent<string>('skillbridge-role-change', { detail: role.id }));
    }
  }, [role]);

  const coverage = gap?.skill_coverage_percent ?? 0;
  const circumference = 2 * Math.PI * 50;
  const dash = circumference - (coverage / 100) * circumference;
  const priority = useMemo(() => [...(gap?.prioritized_missing ?? []), ...(gap?.prioritized_weak ?? [])].slice(0, 4), [gap]);
  const handleRoleChange = (roleId: string) => {
    const selectedRole = roles.find((candidate) => candidate.id === roleId) ?? null;
    setRole(selectedRole);
    setRoleSelectionInitialized(true);
    if (!selectedRole && typeof window !== 'undefined') {
      localStorage.removeItem('skillbridge_selected_role_id');
      window.dispatchEvent(new CustomEvent<string>('skillbridge-role-change', { detail: '' }));
    }
  };

  return (
    <div className="dashboard page-enter">
      <section className="hero-panel">
        <div className="hero-glow glow-one" /><div className="hero-glow glow-two" />
        <div className="hero-copy">
          <div className="pill"><span className="live-dot" /> AI career intelligence</div>
          <h2>Welcome back<span>, {name || 'Student'}</span></h2>
          <p>Turn your current skills into a clear path toward the career you want.</p>
          <div className="hero-actions"><NavLink to="/career" className="primary-button">Explore careers <Icon name="arrow" size={16} /></NavLink><NavLink to="/profile" className="ghost-button">Complete profile</NavLink></div>
        </div>
        <div className="hero-orbit" aria-hidden="true">
          <div className="orbit orbit-a" /><div className="orbit orbit-b" />
          <div className="orbit orbit-c" />
          <div className="orbit-core"><Icon name="spark" size={30} /></div>
          <span className="orbit-node node-a" /><span className="orbit-node node-b" /><span className="orbit-node node-c" />
          <div className="hero-float-card float-a"><span className="float-icon"><Icon name="spark" size={13} /></span><div><b>Skill analysis</b><small>AI active</small></div></div>
          <div className="hero-float-card float-b"><span className="float-icon blue"><Icon name="route" size={13} /></span><div><b>Learning path</b><small>Optimized</small></div></div>
        </div>
      </section>

      {apiError && <div className="notice"><span>Backend data isn't available right now.</span><small> The interface is ready; start the backend to load your profile and skill analytics.</small></div>}

      <section className="metric-grid">
        <Metric label="Skill coverage" value={loading ? '—' : `${coverage}%`} icon="spark" tone="purple" sub={gap ? `${gap.total_skills_acquired}/${gap.total_skills_required} skills matched` : 'Awaiting assessment'} />
        <Metric label="Strong skills" value={gap?.summary.strong_count ?? '—'} icon="shield" tone="green" sub="Meeting role expectations" />
        <Metric label="Priority gaps" value={gap?.summary.total_gaps ?? '—'} icon="target" tone="orange" sub="Areas worth improving" />
        <Metric label="Target role" value={role?.name ?? 'Choose a role'} icon="route" tone="blue" sub="Your current career direction" compact />
      </section>

      <section className="dashboard-grid">
        <div className="glass-card coverage-card">
          <div className="card-head"><div><span className="section-kicker">SKILL PROFILE</span><h3>How close are you?</h3></div><span className="soft-badge">Live analysis</span></div>
          <div className="coverage-body">
            <div className="ring-wrap"><svg className="progress-ring" viewBox="0 0 120 120"><circle className="ring-bg" cx="60" cy="60" r="50"/><circle className="ring-value" cx="60" cy="60" r="50" strokeDasharray={circumference} strokeDashoffset={dash}/></svg><div className="ring-label"><strong>{loading ? '—' : `${coverage}%`}</strong><span>coverage</span></div></div>
            <div className="coverage-list"><CoverageLine label="Core skills" value={gap?.core_skill_coverage_percent ?? 0}/><CoverageLine label="Critical skills" value={gap?.critical_skill_coverage_percent ?? 0}/><div className="mini-note"><Icon name="spark" size={15}/><span>{role ? `Optimized for ${role.name}` : 'Select a role to begin'}</span></div></div>
          </div>
        </div>

        <div className="glass-card role-card">
          <div className="card-head"><div><span className="section-kicker">CAREER TARGET</span><h3>Where are you heading?</h3></div><Icon name="target" size={22}/></div>
          <div className="role-select-wrap"><select value={role?.id ?? ''} onChange={(e) => handleRoleChange(e.target.value)}><option value="">Select a career role</option>{roles.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}</select></div>
          {role ? <><p className="role-description">{role.description}</p><div className="role-meta"><span>{role.required_skill_count} required skills</span><span>{role.core_skills} core</span><span>{role.critical_skills} critical</span></div></> : <div className="empty-inline">Connect your profile to start personalized career analysis.</div>}
        </div>

        <div className="glass-card insight-card">
          <div className="card-head"><div><span className="section-kicker">AI INSIGHTS</span><h3>What needs attention?</h3></div><div className="ai-badge">AI</div></div>
          <div className="insight-list">{priority.length ? priority.map((skill) => <div className="insight-row" key={`${skill.skill_id}-${skill.match_status}`}><div className="insight-icon">!</div><div><strong>{skill.skill_name}</strong><span>{skill.match_status === 'missing' ? 'Missing from your profile' : `Needs ${skill.required_proficiency} proficiency`}</span></div><span className="priority">{skill.priority}</span></div>) : <div className="empty-inline">Complete a skill-gap analysis to unlock AI insights.</div>}</div>
        </div>

        <div className="glass-card journey-card">
          <div className="card-head"><div><span className="section-kicker">YOUR JOURNEY</span><h3>From skills to career readiness</h3></div><div>{role && <NavLink to={`/readiness/${role.id}`} className="text-link">Readiness <Icon name="arrow" size={14}/></NavLink>}<NavLink to={role ? `/roadmap/${role.id}` : '/career'} className="text-link">View roadmap <Icon name="arrow" size={14}/></NavLink></div></div>
          <div className="journey"><JourneyStep n="01" title="Profile" text="Build your student profile" active/><JourneyStep n="02" title="Skill Gap" text="Compare skills to a target role" active={!!gap}/><JourneyStep n="03" title="A* Roadmap" text="Find an efficient learning path"/><JourneyStep n="04" title="Readiness" text="Validate career preparedness"/></div>
        </div>
      </section>
    </div>
  );
}

function Metric({ label, value, sub, icon, tone, compact = false }: { label: string; value: string | number; sub: string; icon: string; tone: string; compact?: boolean }) { return <div className={`metric-card ${tone}`}><div className="metric-icon"><Icon name={icon} size={18}/></div><div className="metric-copy"><span>{label}</span><strong className={compact ? 'compact-value' : ''}>{value}</strong><small>{sub}</small></div></div>; }
function CoverageLine({ label, value }: { label: string; value: number }) { return <div className="coverage-line"><div><span>{label}</span><b>{value}%</b></div><div className="bar"><i style={{ width: `${Math.min(100, Math.max(0, value))}%` }}/></div></div>; }
function JourneyStep({ n, title, text, active }: { n: string; title: string; text: string; active?: boolean }) { return <div className={`journey-step ${active ? 'active' : ''}`}><div className="step-number">{active ? '✓' : n}</div><div><strong>{title}</strong><span>{text}</span></div></div>; }
export default DashboardPage;
