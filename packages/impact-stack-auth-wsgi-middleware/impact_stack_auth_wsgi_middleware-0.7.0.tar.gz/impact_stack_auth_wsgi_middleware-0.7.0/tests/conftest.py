"""Define test fixtures."""

import datetime

import fakeredis
import flask
import flask_jwt_extended
import pytest
import requests_mock

from impact_stack.auth_wsgi_middleware import init_app

# Unused arguments may be used to declare dependencies of fixtures.
# pylint: disable=unused-argument


@pytest.fixture(name="block_requests", autouse=True)
def fixture_block_requests():
    """Don’t allow any remote HTTP requests."""
    with requests_mock.Mocker() as mocker:
        yield mocker


@pytest.fixture(name="jwt", scope="class")
def fixture_jwt():
    """Create a Flask-JWT object."""
    return flask_jwt_extended.JWTManager()


@pytest.fixture(name="app", scope="class")
def fixture_app(jwt):
    """Get the test app for wrapping."""
    app = flask.Flask(__name__)
    app.debug = True
    app.config["SECRET_KEY"] = "super-secret"
    app.config["JWT_SECRET_KEY"] = "super-secret"
    app.config["JWT_HEADER_TYPE"] = "JWT"
    app.config["AUTH_REDIS_URL"] = "redis://localhost:6379/0"
    app.config["AUTH_REDIS_CLIENT_CLASS"] = fakeredis.FakeStrictRedis
    app.config["IMPACT_STACK_API_URL"] = "https://impact-stack.net/api"
    app.config["IMPACT_STACK_API_KEY"] = "api-key"
    # Provide a simple config_getter for tests. moflask.flask.BaseApp providers a better one.
    app.config_getter = app.config.get

    jwt.init_app(app)

    @flask_jwt_extended.jwt_required()
    def protected():
        data = flask_jwt_extended.get_jwt()
        return flask.jsonify(data)

    app.route("/protected")(protected)
    with app.app_context():
        yield app


@pytest.fixture(name="auth_middleware", scope="class")
def fixture_auth_middleware(app, jwt):
    """Initialize the auth middleware."""
    middleware = init_app(app)
    expire_in = datetime.timedelta(days=1)
    # pylint: disable=protected-access
    middleware.token_store._client.set(
        "user1-uuid",
        flask_jwt_extended.create_access_token("user1", expires_delta=expire_in),
        ex=expire_in,
    )
    return middleware


@pytest.fixture(name="client")
def fixture_client(app):
    """Define a test client instance and context."""
    return app.test_client()
