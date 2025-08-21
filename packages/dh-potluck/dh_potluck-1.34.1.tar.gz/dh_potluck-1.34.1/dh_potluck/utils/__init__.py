import inspect
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from flask import current_app


def get_db():
    return current_app.extensions['dh-potluck']._db


def is_truthy(value):
    if isinstance(value, str):
        return value.lower() in ['true', '1']
    return bool(value)


def ensure_charset_in_uri(db_uri: str, *, charset: str = 'utf8mb4') -> str:
    parts = urlparse(db_uri)
    query = parse_qs(parts.query)
    query['charset'] = [charset]
    return urlunparse(parts._replace(query=urlencode(query, doseq=True)))


def get_config_value(config, key, default=None):
    if isinstance(config, dict):
        return config.get(key, default)
    else:
        return getattr(config, key, default)


def get_arg_names(f: Callable[..., Any]) -> list[str]:
    """Return arguments of function"""
    if not callable(f):
        return []
    return [
        parameter.name
        for parameter in inspect.signature(f).parameters.values()
        if parameter.kind in (parameter.POSITIONAL_OR_KEYWORD, parameter.POSITIONAL_ONLY)
    ]
