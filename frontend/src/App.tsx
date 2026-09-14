import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import HealthPage from './pages/HealthPage';
import DashboardPage from './pages/DashboardPage';
import StudentProfilePage from './modules/student-profile/StudentProfilePage';
import CareerPage from './pages/CareerPage';
import SkillsPage from './pages/SkillsPage';
import RoadmapPage from './pages/RoadmapPage';
import ReadinessPage from './pages/ReadinessPage';

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/profile" element={<StudentProfilePage />} />
        <Route path="/skills" element={<SkillsPage />} />
        <Route path="/career" element={<CareerPage />} />
        <Route path="/roadmap" element={<RoadmapPage />} />
        <Route path="/roadmap/:roleId" element={<RoadmapPage />} />
        <Route path="/readiness" element={<ReadinessPage />} />
        <Route path="/readiness/:roleId" element={<ReadinessPage />} />
        <Route path="/health" element={<HealthPage />} />
      </Route>
    </Routes>
  );
}

export default App;
