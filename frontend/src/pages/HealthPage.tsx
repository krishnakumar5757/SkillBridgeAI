import { useEffect, useState } from 'react';
import { checkHealth, ApiError } from '../services/api';
import type { HealthResponse } from '../types';

/**
 * SkillBridge AI — Health Page
 *
 * Displays the backend health status, demonstrating that the
 * frontend can communicate with the backend API.
 */
function HealthPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkHealth()
      .then((data) => {
        setHealth(data);
        setError(null);
      })
      .catch((err: unknown) => {
        if (err instanceof ApiError) {
          setError(`${err.code}: ${err.message}`);
        } else if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('An unknown error occurred');
        }
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="health-page">Checking backend health...</div>;
  }

  if (error) {
    return (
      <div className="health-page">
        <h2>Backend Health</h2>
        <div className="health-error">
          <p>Failed to connect to the backend.</p>
          <p className="error-detail">{error}</p>
          <p className="error-hint">
            Make sure the backend is running: uvicorn app.main:app --reload --port 8000
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="health-page">
      <h2>Backend Health</h2>
      {health && (
        <div className="health-status">
          <div className="health-row">
            <span className="health-label">Status:</span>
            <span className={`health-value health-${health.status}`}>
              {health.status}
            </span>
          </div>
          <div className="health-row">
            <span className="health-label">Application:</span>
            <span className="health-value">{health.app}</span>
          </div>
          <div className="health-row">
            <span className="health-label">Version:</span>
            <span className="health-value">{health.version}</span>
          </div>
          <div className="health-row">
            <span className="health-label">Database:</span>
            <span className={`health-value health-${health.database}`}>
              {health.database}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default HealthPage;
