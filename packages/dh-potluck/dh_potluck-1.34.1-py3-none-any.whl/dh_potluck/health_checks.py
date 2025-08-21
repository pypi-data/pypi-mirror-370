from http import HTTPStatus

from flask import Blueprint, abort

healthz = Blueprint('healthz', __name__)


class HealthChecks:
    callback = lambda: True  # noqa: E731

    def init_app(self, app, callback=None):
        if callback:
            HealthChecks.callback = callback
        app.register_blueprint(healthz, url_prefix='/healthz')


@healthz.route('/liveness')
def liveness():
    return 'OK'


@healthz.route('/readiness')
def readiness():
    try:
        if not HealthChecks.callback():
            abort(HTTPStatus.SERVICE_UNAVAILABLE, 'Pod unready to service requests.')
    except Exception as e:
        abort(HTTPStatus.SERVICE_UNAVAILABLE, str(e))
    return 'OK'
