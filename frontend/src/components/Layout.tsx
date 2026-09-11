import { NavLink, Outlet, useLocation } from 'react-router-dom';
import type { ReactElement } from 'react';

const items = [
  { to: '/dashboard', label: 'Overview', icon: 'grid' },
  { to: '/profile', label: 'My Profile', icon: 'user' },
  { to: '/skills', label: 'Skills', icon: 'spark' },
  { to: '/career', label: 'Career & Skill Gap', icon: 'target' },
  { to: '/roadmap', label: 'Learning Roadmap', icon: 'route' },
  { to: '/readiness', label: 'Career Readiness', icon: 'shield' },
];

function Icon({ name, size = 18 }: { name: string; size?: number }) {
  const common = { width: size, height: size, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const };
  const paths: Record<string, ReactElement> = {
    grid: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
    user: <><circle cx="12" cy="8" r="3.5"/><path d="M5 20c.8-3.5 3.1-5.2 7-5.2s6.2 1.7 7 5.2"/></>,
    spark: <><path d="m12 3 1.4 5.1L18 10l-4.6 1.9L12 17l-1.4-5.1L6 10l4.6-1.9L12 3Z"/><path d="m19 15 .6 2.2L22 18l-2.4.8L19 21l-.6-2.2L16 18l2.4-.8L19 15Z"/></>,
    target: <><circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><path d="m15.2 8.8 3-3"/><path d="M18 6h-2.8"/></>,
    route: <><circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="6" r="2.5"/><path d="M8.5 18H12a4 4 0 0 0 4-4V10"/><path d="m13 10 3-3 3 3"/></>,
    shield: <><path d="M12 3 20 6v5c0 5-3.1 8.3-8 10-4.9-1.7-8-5-8-10V6l8-3Z"/><path d="m8.5 12 2.2 2.2 4.8-5"/></>,
    bell: <><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/></>,
    arrow: <><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></>,
  };
  return <svg {...common}>{paths[name] ?? paths.spark}</svg>;
}

function Layout() {
  const location = useLocation();
  const current = items.find((item) => location.pathname.startsWith(item.to));
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Icon name="spark" size={19} /></div>
          <div><strong>SkillBridge</strong><span>AI</span></div>
        </div>
        <div className="sidebar-caption">CAREER INTELLIGENCE</div>
        <nav className="sidebar-nav" aria-label="Main navigation">
          {items.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <Icon name={item.icon} />
              <span>{item.label}</span>
              {current?.to === item.to && <span className="nav-dot" />}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="ai-status"><span className="status-pulse" /> AI engine ready</div>
          <div className="profile-mini">
            <div className="avatar">S</div>
            <div><strong>Student</strong><span>Career explorer</span></div>
          </div>
        </div>
      </aside>
      <main className="main-area">
        <header className="topbar">
          <div><span className="eyebrow">{current?.label ?? 'SkillBridge AI'}</span><h1>{current?.label === 'Overview' ? 'Your career command center' : current?.label}</h1></div>
          <div className="topbar-actions"><button className="icon-button" aria-label="Notifications"><Icon name="bell" /></button><div className="top-avatar">S</div></div>
        </header>
        <div className="page-container"><Outlet /></div>
        <footer className="app-footer">SkillBridge AI <span>•</span> Intelligent career readiness platform</footer>
      </main>
    </div>
  );
}

export { Icon };
export default Layout;
