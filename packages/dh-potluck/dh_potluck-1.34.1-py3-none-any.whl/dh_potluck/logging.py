import json
import logging
import re
from urllib.parse import urlencode

import json_log_formatter
from boltons.iterutils import remap
from ddtrace import tracer
from flask import request

from dh_potluck.utils import get_config_value, is_truthy

SENSITIVE_KEYS = re.compile(r'password|token|secret|key', flags=re.I)
MAX_BODY_SIZE = 50000


def set_log_levels(config_object):
    general_log_level = get_config_value(config_object, 'DH_POTLUCK_LOG_LEVEL', 'INFO')
    if general_log_level:
        try:
            numeric_level = _get_numeric_log_level(general_log_level.upper())
        except ValueError as e:
            raise ValueError(f'General logging configuration error: {e}')
        logging.basicConfig(level=numeric_level)

    module_log_levels = get_config_value(config_object, 'DH_POTLUCK_MODULE_LOG_LEVELS', None)
    if module_log_levels:
        module_configs = dict(
            module_config.split(':')
            for module_config in module_log_levels.split(',')
            if module_config and len(module_config.split(':')) == 2
        )
        for module, log_level in module_configs.items():
            module = module.strip()
            log_level = log_level.strip().upper()
            try:
                numeric_level = _get_numeric_log_level(log_level)
            except ValueError as e:
                raise ValueError(f'Module "{module}" logging configuration error: {e}')
            logging.getLogger(module).setLevel(numeric_level)


def _get_numeric_log_level(log_level: str):
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    return numeric_level


def add_request_params_to_trace():
    """
    Add additional details about the current request (query string, body, request size) to
    the current Datadog trace. Useful for error handlers.
    """
    span = tracer.current_root_span()
    if not span:
        return

    # Log query string (if present) for all request methods
    query_params = request.args
    if query_params:
        clean = remap(query_params.copy(), visit=scrub_keys)
        span.set_tag('http.query_string', urlencode(clean))

    # Skip body logging if not POST, PATCH or PUT
    if request.method not in ['POST', 'PATCH', 'PUT']:
        return

    # Skip body logging if it's empty
    if not request.content_length:
        return

    span.set_tag('http.content_length', str(request.content_length))

    if request.content_length > MAX_BODY_SIZE:
        span.set_tag('http.body', 'Body too large, content could not be logged.')
        return

    # Try to parse body as JSON, and scrub sensitive values
    body = request.get_json(silent=True)
    if body:
        clean = remap(body, visit=scrub_keys)
        span.set_tag('http.body', json.dumps(clean))
    else:
        # If we can't parse as JSON, log the raw body
        body = request.get_data(as_text=True)
        span.set_tag('http.body', body)


def scrub_keys(path, key, value):
    if isinstance(key, str) and SENSITIVE_KEYS.search(key):
        return key, '-' * 5
    return key, value


class DHJSONFormatter(json_log_formatter.JSONFormatter):
    def json_record(self, message, extra, record):
        extra['funcName'] = record.funcName
        extra['level'] = record.levelname
        extra['lineno'] = record.lineno
        extra['pathname'] = record.pathname
        extra['module'] = record.module
        return super(DHJSONFormatter, self).json_record(message, extra, record)


def structure_logger(logger):
    # Assign JSON formatter to handler
    json_handler = logging.StreamHandler()
    json_handler.setFormatter(DHJSONFormatter())
    logger.handlers = [json_handler]
    # This looks to have been added to prevent celery from messing up logging configuration
    # TODO: Investigate if this is still needed, or if we can just rely on using
    #  `@celery.signals.setup_logging.connect` signal in applications is enough to prevent that
    logger.propagate = False


def structured_logging_enabled(config_object):
    structured_logging_config = get_config_value(config_object, 'STRUCTURED_LOGGING')
    if structured_logging_config is None:
        return True
    else:
        return is_truthy(structured_logging_config)


def configure_structured_logging(config_object):
    if structured_logging_enabled(config_object):
        # Configure root logger
        structure_logger(logging.getLogger())

        # Set all others
        for logger in (logging.getLogger(name) for name in logging.root.manager.loggerDict):
            structure_logger(logger)

        # Allow for Celery logs to report log level to Datadog
        # TODO - remove this once Celery log configuration hooks are sorted
        patch_celery_get_logger()


def patch_celery_get_logger():
    # This has the opportunity of being a patch closer to the source (kombu)
    # Imports safely hidden behind structured_logging flag for now
    try:
        from celery.utils import log

        def _patch_func(name):
            l = log._get_logger(name)  # noqa: E741
            if logging.root not in (l, l.parent) and l is not log.base_logger:
                l = log._using_logger_parent(log.base_logger, l)  # noqa: E741
            structure_logger(l)
            return l

        log.get_logger = _patch_func
    except ModuleNotFoundError:
        return
