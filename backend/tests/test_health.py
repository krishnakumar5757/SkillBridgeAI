"""
SkillBridge AI — Health Endpoint Tests

Verifies that the health check endpoint returns the correct response
structure and that the database connectivity check works.
"""

from app.core.config import settings


class TestHealthEndpoint:
    """Tests for the GET /health endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint should return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client):
        """Health response should contain all required fields."""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert "app" in data
        assert "version" in data
        assert "database" in data

    def test_health_status_healthy(self, client):
        """Health status should be 'healthy' when the database is connected."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_database_connected(self, client):
        """Database status should be 'connected' when the DB is reachable."""
        response = client.get("/health")
        data = response.json()
        assert data["database"] == "connected"

    def test_health_app_name(self, client):
        """Health response should include the application name."""
        response = client.get("/health")
        data = response.json()
        assert data["app"] == settings.APP_NAME

    def test_health_version(self, client):
        """Health response should include the application version."""
        response = client.get("/health")
        data = response.json()
        assert data["version"] == settings.APP_VERSION
