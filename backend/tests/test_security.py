"""
SkillBridge AI — Security Foundation Tests

Verifies that the JWT and bcrypt utilities work correctly, and that the
JWT secret guard (lifespan startup check) behaves correctly. These are
foundation-level tests for the authentication infrastructure.
"""

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import (
    JWT_SECRET_MIN_LENGTH,
    JWT_SECRET_PLACEHOLDER,
    Settings,
    settings,
)
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """Tests for bcrypt password hashing."""

    def test_hash_password_returns_string(self):
        """hash_password should return a string."""
        hashed = hash_password("testpassword123")
        assert isinstance(hashed, str)

    def test_hash_password_is_not_plain_text(self):
        """hash_password should not return the plain-text password."""
        password = "testpassword123"
        hashed = hash_password(password)
        assert hashed != password

    def test_verify_correct_password(self):
        """verify_password should return True for the correct password."""
        password = "mySecretPassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """verify_password should return False for an incorrect password."""
        hashed = hash_password("correctPassword")
        assert verify_password("wrongPassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Each hash should be unique due to random salt."""
        password = "samePassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestJWTTokens:
    """Tests for JWT token creation and verification."""

    def test_create_token_returns_string(self):
        """create_access_token should return a string."""
        token = create_access_token(subject="student-123")
        assert isinstance(token, str)

    def test_decode_token_returns_payload(self):
        """decode_access_token should return the token payload."""
        token = create_access_token(subject="student-123")
        payload = decode_access_token(token)
        assert payload["sub"] == "student-123"

    def test_token_contains_iat_and_exp(self):
        """Token payload should include issued-at and expiry timestamps."""
        token = create_access_token(subject="student-123")
        payload = decode_access_token(token)
        assert "iat" in payload
        assert "exp" in payload

    def test_token_with_extra_claims(self):
        """Token should include extra claims when provided."""
        token = create_access_token(
            subject="student-123",
            extra_claims={"name": "Test Student", "email": "test@example.com"},
        )
        payload = decode_access_token(token)
        assert payload["name"] == "Test Student"
        assert payload["email"] == "test@example.com"

    def test_invalid_token_raises_error(self):
        """decode_access_token should raise for an invalid token."""
        with pytest.raises(jwt.InvalidTokenError):
            decode_access_token("invalid.token.here")

    def test_token_uses_configured_secret(self):
        """Token should be signed with the configured JWT secret."""
        token = create_access_token(subject="student-123")
        # Should decode successfully with the configured secret
        payload = decode_access_token(token)
        assert payload["sub"] == "student-123"

        # Should fail with a different secret
        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode(
                token,
                "wrong-secret",
                algorithms=[settings.JWT_ALGORITHM],
            )


class TestJWTSecretGuard:
    """Tests for the JWT secret insecurity check and lifespan guard.

    The lifespan guard (app.main) refuses to start the application when
    DEBUG is False and the JWT secret is the known placeholder or shorter
    than the minimum length. These tests verify the guard's logic
    (is_jwt_secret_insecure) and the lifespan integration.
    """

    def test_placeholder_secret_is_insecure(self):
        """The known placeholder secret should be flagged as insecure."""
        s = Settings(JWT_SECRET=JWT_SECRET_PLACEHOLDER)
        assert s.is_jwt_secret_insecure is True

    def test_short_secret_is_insecure(self):
        """A secret shorter than the minimum length should be insecure."""
        s = Settings(JWT_SECRET="short")
        assert s.is_jwt_secret_insecure is True

    def test_strong_secret_is_secure(self):
        """A long, non-placeholder secret should be considered secure."""
        strong = "a-very-strong-and-long-random-secret-value-32chars"
        assert len(strong) >= JWT_SECRET_MIN_LENGTH
        s = Settings(JWT_SECRET=strong)
        assert s.is_jwt_secret_insecure is False

    def test_app_refuses_to_start_with_insecure_secret_in_production(
        self, monkeypatch
    ):
        """Lifespan should raise RuntimeError when DEBUG=False + insecure secret.

        This verifies the startup guard actually refuses to boot the app in
        non-debug mode with an insecure JWT secret.
        """
        from app.core import config
        from app.main import create_app

        monkeypatch.setattr(config.settings, "DEBUG", False)
        monkeypatch.setattr(config.settings, "JWT_SECRET", "short")

        app = create_app()
        with pytest.raises(RuntimeError, match="JWT_SECRET is insecure"), TestClient(app):
            pass
