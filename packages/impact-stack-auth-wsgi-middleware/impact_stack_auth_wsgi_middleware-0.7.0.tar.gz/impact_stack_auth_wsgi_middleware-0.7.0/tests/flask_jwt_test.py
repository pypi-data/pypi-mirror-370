"""Test the middleware by wrapping a Flask app that accepts JWT tokens."""

import datetime
import json

import pytest

from impact_stack.auth_wsgi_middleware import AuthMiddleware, from_config


@pytest.mark.usefixtures("auth_middleware")
class TestMiddleware:
    """Test the middleware."""

    def test_access_denied_without_cookie(self, client):
        """Test that a request without session ID gets a 401."""
        response = client.get("/protected")
        assert response.status_code == 401

    def test_access_denied_with_unsigned_cookie(self, client):
        """Test that a request with an unsigned session ID gets a 401."""
        client.set_cookie("session_uuid", "user1-uuid")
        response = client.get("/protected")
        assert response.status_code == 401

    def test_access_denied_with_invalid_signature(self, auth_middleware, client):
        """Test that a request with an invalid signature gets a 401."""
        invalid_uuid = "user1-uuid.invalid-signature"
        client.set_cookie(auth_middleware.cookie_handler.cookie_name, invalid_uuid)
        response = client.get("/protected")
        assert response.status_code == 401

    def test_authorization_headers_not_modified(self, auth_middleware: AuthMiddleware, client):
        """Test that the middleware doesn’t override existing Authorization headers."""
        signed_uuid = auth_middleware.cookie_handler.signer.sign("user1-uuid").decode()
        cookie_name = auth_middleware.cookie_handler.cookie_name
        client.set_cookie(cookie_name, signed_uuid)
        response = client.get("/protected", headers={"Authorization": "Other method"})
        assert response.status_code == 401

    def test_get_current_identity(self, auth_middleware: AuthMiddleware, client, requests_mock):
        """Test that a request with a valid signed session ID gets a 200."""
        signed_uuid = auth_middleware.cookie_handler.signer.sign("user1-uuid").decode()
        cookie_name = auth_middleware.cookie_handler.cookie_name
        client.set_cookie(cookie_name, signed_uuid)
        response = client.get("/protected")
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert "sub" in data and data["sub"] == "user1"

        # Force a token refresh
        auth_middleware.token_refresher.minimum_life_time = (
            datetime.timedelta(days=1).total_seconds() + 1
        )
        # Due to https://github.com/jamielennox/requests-mock/issues/17 we have to generate the
        # Set-Cookie header here manually instead of using requests-mock to do it.
        headers = {"Set-Cookie": f"{cookie_name}={signed_uuid}; Max-Age=86400"}
        requests_mock.post("http://localhost/api/auth/v1/refresh", json={}, headers=headers)
        response = client.get("/protected")
        # The flask app response is returned.
        assert response.status_code == 200
        assert response.json["sub"] == "user1"
        # A new token is generated.
        assert len(requests_mock.request_history) == 1
        assert "Authorization" in requests_mock.request_history[0].headers
        # The cookie header is forwarded.
        assert "Set-Cookie" in response.headers
        assert response.headers["Set-Cookie"] == headers["Set-Cookie"]


def test_secret_key_precedence(app):
    """Test precedence of the secret key config variables."""
    del app.config["JWT_SECRET_KEY"]
    app.config["SECRET_KEY"] = "secret-key"
    assert from_config(app.config_getter).cookie_handler.signer.secret_keys == [b"secret-key"]
    app.config["JWT_SECRET_KEY"] = "jwt-secret-key"
    assert from_config(app.config_getter).cookie_handler.signer.secret_keys == [b"jwt-secret-key"]
    app.config["AUTH_SECRET_KEY"] = "auth-secret-key"
    assert from_config(app.config_getter).cookie_handler.signer.secret_keys == [b"auth-secret-key"]
