"""Test code for auto-refreshing tokens."""

from impact_stack.auth_wsgi_middleware import AuthMiddleware


def test_refresher_gets_http_error(auth_middleware: AuthMiddleware, requests_mock, caplog):
    """Test that the refresher handles HTTP errors."""
    requests_mock.post("https://impact-stack.net/api/auth/v1/refresh", status_code=500)
    assert auth_middleware.token_refresher(0, {"HTTP_AUTHORIZATION": "Bearer token"}) is None
    assert caplog.records[0].message == "Error when trying to refresh a token."
