import importlib
import os
import threading
import traceback
from http import HTTPStatus
from http.client import RemoteDisconnected
from importlib.metadata import PackageNotFoundError, version

from ddtrace import tracer
from flask import g, jsonify, request
from flask_limiter import Limiter
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.middleware.proxy_fix import ProxyFix

from .api_docs import public_docs
from .audit_log import audit_log_click_command
from .auth import (
    ApplicationUser,
    AuthenticationError,
    UnauthenticatedUser,
    authenticate_request,
    impersonation_header_key,
    role_required,
)
from .logging import (
    add_request_params_to_trace,
    configure_structured_logging,
    structured_logging_enabled,
)
from .platform_connection import PlatformConnectionError
from .queries_summary import get_database_queries_summary
from .skeema import skeema_click_command
from .utils.datadog import ErrorFilter


class DHPotluck:
    _app = None
    _db = None
    _app_tokens = None
    _structured_logging_enabled = False
    _rate_limiting_enabled = False
    _rate_limit = None
    _limiter = None
    _validate_token_func = None

    def __init__(self, app=None, db=None):
        """Initialize dh-potluck."""
        self._app = app
        self._db = db

        if app is not None:
            self.init_app(app, db)

    def init_app(self, app, db=None):
        self._app = app
        self._db = db
        self._app_tokens = []

        # Addresses issue with root span missing error details and breaking Datadog APM Error
        # Tracking. See https://ddtrace.readthedocs.io/en/stable/troubleshooting.html
        # #root-span-is-missing-error-details
        tracer.configure(settings={'FILTERS': [ErrorFilter()]})

        if 'DH_POTLUCK_APP_TOKEN' in app.config:
            self._app_tokens.append(app.config['DH_POTLUCK_APP_TOKEN'])

        if 'DH_POTLUCK_APP_TOKENS' in app.config:
            self._app_tokens.extend(app.config['DH_POTLUCK_APP_TOKENS'].split(','))

        self._structured_logging_enabled = structured_logging_enabled(app.config)
        self._rate_limiting_enabled = bool(app.config.get('RATELIMIT_ENABLED', 0))
        self._rate_limit = app.config.get('RATELIMIT_DEFAULT_PER_MINUTE', 1000)

        # Import function we use to authenticate incoming requests
        validate_func_name = app.config.get(
            'DH_POTLUCK_VALIDATE_TOKEN_FUNC', 'dh_potluck.auth.validate_token_using_api'
        )
        module_name, class_name = validate_func_name.rsplit('.', 1)
        self._validate_token_func = getattr(importlib.import_module(module_name), class_name)

        # Adjust the WSGI environ based on X-Forwarded- headers that proxies in front of the
        # application may set.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=app.config.get('DH_POTLUCK_NUM_PROXIES', 2))

        # Add potluck version to Datadog traces
        try:
            potluck_version = version('dh-potluck')
        except PackageNotFoundError:
            potluck_version = 'unknown'
        tracer.set_tags({'dh_potluck.version': potluck_version})

        self._limiter = self._configure_rate_limiting()
        app.extensions['dh-potluck-limiter'] = self._limiter

        app.before_request(self._process_request)
        app.after_request(self._process_response)
        self._register_error_handlers()

        configure_structured_logging(app.config)

        # Datadog Profiling - ddtrace 0.39.0 required
        if app.config.get('DD_PROFILING'):
            import ddtrace.profiling.auto  # noqa: F401

        self._configure_user_agent(app)

        # Install Click commands
        app.cli.add_command(audit_log_click_command)
        app.cli.add_command(skeema_click_command)

        app.extensions['dh-potluck'] = self

    def _get_rate_limit_key(self):
        """
        Extract a key from the request we can identify users by so we can rate limit appropriately.
        """
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
            impersonated_user_id = request.headers.get(impersonation_header_key) or ''
            return f'{token[:6]}...{token[-2:]}:{impersonated_user_id}'
        else:
            return request.remote_addr

    def _configure_rate_limiting(self):
        limiter = Limiter(
            key_func=self._get_rate_limit_key,
            default_limits=[f'{self._rate_limit} per minute'],
            default_limits_per_method=False,
            headers_enabled=True,
            swallow_errors=True,
            enabled=self._rate_limiting_enabled,
        )

        @limiter.request_filter
        def app_token_whitelist():
            return request.headers.get('Authorization', '') in [
                f'Application {t}' for t in self._app_tokens
            ]

        limiter.init_app(self._app)
        return limiter

    def _process_request(self):
        """
        Authenticate every incoming request.
        """
        # Allow any OPTIONS request so CORS works properly
        if request.method == 'OPTIONS':
            return

        # Add Domo session to Datadog traces if provided
        if 'domo-session' in request.headers:
            span = tracer.current_span()
            if span:
                span.set_tags({'dh_potluck.domo.session': request.headers.get('domo-session')})

        user, impersonator = authenticate_request(self._app_tokens, self._validate_token_func)
        g.user = user
        g.impersonator = impersonator

        user_tags = {}
        if user is not None and hasattr(user, 'id'):
            user_tags['dh_potluck.current_user'] = str(user.id)
        if isinstance(user, ApplicationUser) or isinstance(user, UnauthenticatedUser):
            user_tags['dh_potluck.current_user'] = type(user).__name__
        if impersonator is not None and hasattr(impersonator, 'id'):
            user_tags['dh_potluck.current_impersonator'] = str(impersonator.id)
        if isinstance(impersonator, ApplicationUser):
            user_tags['dh_potluck.current_impersonator'] = type(impersonator).__name__
        if user_tags:
            span = tracer.current_root_span()
            if span:
                span.set_tags(user_tags)

    def _process_response(self, response):
        """
        Capture SQL queries made during request and log info about them.
        """
        if os.environ.get('FLASK_DEBUG', 'false') == 'true':
            message = get_database_queries_summary(self._app)
            self._app.logger.info(message)

        return response

    def _register_error_handlers(self):
        # Catch flask-smorest validation errors and return them in JSON format
        @self._app.errorhandler(HTTPStatus.UNPROCESSABLE_ENTITY)
        def handle_unprocessable_entity(error):
            add_request_params_to_trace()
            response = {
                'description': 'Input failed validation.',
                'errors': error.exc.messages,
            }
            return jsonify(response), HTTPStatus.BAD_REQUEST

        # Catch marshmallow validation errors and return them in JSON format
        @self._app.errorhandler(ValidationError)
        def handle_validation_error(error):
            add_request_params_to_trace()
            response = {
                'description': 'Input failed validation.',
                'errors': error.messages,
            }
            return jsonify(response), HTTPStatus.BAD_REQUEST

        # Catch SQLAlchemy IntegrityErrors (usually unique constraint violations) and return them
        # in JSON format. TODO: Right now we return the database error as-is to the client. This
        # should be expanded to parse the integrity error and try to build a more structured,
        # user-friendly message about the error.
        @self._app.errorhandler(IntegrityError)
        def handle_integrity_errors(error):
            add_request_params_to_trace()
            return (
                jsonify({'description': f'Database integrity error: {error.orig.args[1]}'}),
                HTTPStatus.BAD_REQUEST,
            )

        # Ensure all other Flask HTTP exceptions are returned in JSON format
        @self._app.errorhandler(HTTPException)
        def handle_flask_exceptions(error):
            add_request_params_to_trace()
            return jsonify({'description': error.description}), error.code

        # Add extra context to Datadog traces for server errors
        @self._app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
        def handle_server_error(error):
            add_request_params_to_trace()
            error_response = (
                jsonify({'description': InternalServerError.description}),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return error_response

        # Add extra context to Datadog traces for rate limited requests
        @self._app.errorhandler(HTTPStatus.TOO_MANY_REQUESTS)
        def handle_too_many_requests(error):
            if 'Authorization' in request.headers:
                key = self._get_rate_limit_key()
                cleaned_key = f'{key[0:4]}...{key[-4:-1]}'
            else:
                cleaned_key = request.remote_addr

            tracer.set_tags({'rate_limit_key': cleaned_key})

            return (
                jsonify(
                    {
                        'description': (
                            'The user has sent too many requests in a given amount of time.'
                        )
                    }
                ),
                HTTPStatus.TOO_MANY_REQUESTS,
            )

        @self._app.errorhandler(RemoteDisconnected)
        def handle_remote_disconnected_exception(error):
            add_request_params_to_trace()
            return (
                jsonify(
                    {
                        'description': (
                            'Remote Disconnected: Remote end closed connection without response.'
                        )
                    }
                ),
                HTTPStatus.SERVICE_UNAVAILABLE,
            )

        @self._app.errorhandler(HTTPStatus.NOT_FOUND)
        def page_not_found(error):
            """Don't return 404 on OPTIONS calls"""
            if request and request.method == 'OPTIONS':
                return '', HTTPStatus.OK

            error_response = (
                jsonify({'description': error.description}),
                HTTPStatus.NOT_FOUND,
            )

            return error_response

        @self._app.errorhandler(PlatformConnectionError)
        def handle_platform_connection_error(error):
            return jsonify({'description': str(error)}), HTTPStatus.BAD_REQUEST

        @self._app.errorhandler(AuthenticationError)
        def handle_authentication_error(error):
            return jsonify({'description': error.description}), error.status

        @self._app.errorhandler(Exception)
        def handle_error(error):
            # log unhandled exceptions in JSON format
            if self._structured_logging_enabled:
                extra = {
                    'error.stack': traceback.format_exc(),
                    'error.kind': str(type(error)),
                    'logger.thread_name': threading.current_thread().name,
                }
                self._app.logger.error(str(error), extra=extra)
            else:
                traceback.print_exc()

            add_request_params_to_trace()
            return (
                jsonify({'description': InternalServerError.description}),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    def role_required(*args, **kwargs):
        return role_required(*args, **kwargs)

    @staticmethod
    def public_docs(*args, **kwargs):
        return public_docs(*args, **kwargs)

    @property
    def current_user(self):
        if hasattr(g, 'user'):
            return g.user
        return None

    @property
    def current_impersonator(self):
        if hasattr(g, 'impersonator'):
            return g.impersonator
        return None

    @property
    def limiter(self):
        return self._limiter

    @staticmethod
    def _configure_user_agent(app):
        from requests import utils

        user_agent = app.config.get('API_TITLE', 'Dash Hudson Unknown Backend Service')

        def get_user_agent():
            return user_agent

        utils.default_user_agent = get_user_agent
