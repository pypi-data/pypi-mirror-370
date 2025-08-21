import hashlib
import logging
import re
from functools import wraps
from http import HTTPStatus
from pickle import loads
from typing import Optional

import requests
from flask import current_app, g, jsonify, request
from flask_redis import FlaskRedis
from redis.exceptions import ConnectionError, TimeoutError

logger = logging.getLogger(__name__)


auth_cookie_key = 'dashhudson-api-token'
impersonation_header_key = 'X-On-Behalf-Of'
auth_header_key = 'Authorization'
user_auth_header_value_prefix = 'Bearer'
app_auth_header_value_prefix = 'Application'


class AuthenticationError(Exception):
    description = 'Unknown Authentication Error'
    status = HTTPStatus.UNAUTHORIZED


class InvalidTokenError(AuthenticationError):
    description = 'Authentication token missing or invalid.'
    status = HTTPStatus.UNAUTHORIZED


class ImpersonationInvalidError(AuthenticationError):
    description = f'Invalid {impersonation_header_key} header provided.'
    status = HTTPStatus.FORBIDDEN


class ImpersonationUserNotFoundError(AuthenticationError):
    description = 'Unable to find user for impersonation.'
    status = HTTPStatus.FORBIDDEN


class PermissionDeniedError(AuthenticationError):
    description = 'You do not have access to this resource.'
    status = HTTPStatus.FORBIDDEN


class UnauthenticatedUser:
    role = None
    is_active = True


class AuthenticatedUser:
    id = None
    email = None
    first_name = None
    last_name = None
    default_time_zone = None
    time_zone_name = None
    password_reset_expires = None
    password_reset_url = None
    has_device = None
    status = None
    brandpanel_id = None
    is_superadmin = None
    is_pending = None
    job_title = None
    avatar_url = None
    organization = None
    brands = None
    accessible_brands = None
    permissions = None
    updated_at = None
    created_at = None

    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @property
    def role(self):
        if self.is_superadmin:
            return 'superadmin'
        return 'user'

    @property
    def is_active(self):
        return self.status == 0


class ApplicationUser:
    role = 'app'
    is_active = True


def authenticate_request(app_tokens, validate_token_func):
    user, valid_token = _handle_auth_header(app_tokens, validate_token_func)

    if not user:
        user, valid_token = _handle_auth_cookie(user, valid_token, validate_token_func)

    if not user or not user.is_active:
        user = UnauthenticatedUser()

    user, impersonator = _handle_impersonation(user, valid_token, validate_token_func)

    return user, impersonator


def _handle_auth_header(app_tokens, validate_token_func):
    user = None
    valid_token = None
    # handle header authentication
    auth_header = request.headers.get(auth_header_key)
    if auth_header is not None:
        match = re.match(
            rf'^({app_auth_header_value_prefix}|{user_auth_header_value_prefix}):? (\S+)$',
            auth_header,
        )
        if match:
            method = match.group(1)
            token = match.group(2)

            # Application token
            if method == app_auth_header_value_prefix:
                if token in app_tokens:
                    valid_token = token
                    user = ApplicationUser()

            # Bearer token
            elif method == user_auth_header_value_prefix:
                potential_user = validate_token_func(token)
                if potential_user:
                    valid_token = token
                    user = potential_user
    return user, valid_token


def _handle_auth_cookie(user, valid_token, validate_token_func):
    # handle cookie authentication
    auth_cookie = request.cookies.get(auth_cookie_key)
    if auth_cookie:
        potential_user = validate_token_func(auth_cookie)
        if potential_user:
            valid_token = auth_cookie
            user = potential_user
    return user, valid_token


def _handle_impersonation(user, valid_token, validate_token_func):
    impersonator = None
    on_behalf_of_user_id_str = request.headers.get(impersonation_header_key)
    if on_behalf_of_user_id_str:
        if valid_token and user_has_role(user, 'superadmin'):
            try:
                on_behalf_of_user_id = int(on_behalf_of_user_id_str)
            except ValueError:
                raise ImpersonationInvalidError()
            user_to_impersonate = validate_token_func(
                valid_token,
                (
                    app_auth_header_value_prefix
                    if isinstance(user, ApplicationUser)
                    else user_auth_header_value_prefix
                ),
                on_behalf_of_user_id,
            )
            if user_to_impersonate:
                impersonator = user
                user = user_to_impersonate
            else:
                raise ImpersonationUserNotFoundError()
        else:
            raise ImpersonationInvalidError()
    return user, impersonator


roles = {
    'user': 0,
    'brand_admin': 1,
    'superadmin': 2,
    'app': 3,
}


def user_has_role(user, role):
    if not user.role:
        return False
    return roles[user.role] >= roles[role]


def role_required(role):
    """
    Currently, the supported roles are:

    1. user
    2. brand_admin
    3. superadmin
    4. app

    Roles are ordered from least to most privilege. Each role receives the permissions of the roles
    before it. Example:

    If role='user', users with 'user', 'superadmin', or 'app' roles will be granted access.
    If role='superadmin', only users with 'superadmin' or 'app' roles will be granted access.
    """

    def decorator(func):
        # finds the role within a brand of the current user
        def get_brand_role():
            # extract the brand_id from the path
            brand_id = request.view_args.get('brand_id')
            if not brand_id:
                return None

            # use the brand_id to find the specific brand_role from the list of brand_roles
            brs = g.user.permissions.get('brand_roles', [])
            br = next((br.get('role') for br in brs if br.get('brand_id') == brand_id), None)

            # br.value will exist if g.user is assigned a user model (called from auth)
            # otherwise, br alone is the value we want
            return getattr(br, 'value', br)

        @wraps(func)
        def wrapper(*args, **kwargs):
            if isinstance(g.user, UnauthenticatedUser):
                raise InvalidTokenError()

            if user_has_role(g.user, role):
                return func(*args, **kwargs)

            # a check for the brand_admin role is needed as it isn't stored in the user instance
            if role == 'brand_admin' and g.user.brands and get_brand_role() == 'admin':
                return func(*args, **kwargs)

            raise PermissionDeniedError()

        return wrapper

    return decorator


class AuthCache(object):
    cache = None

    @classmethod
    def get_cache(cls):
        if not current_app.config.get('DH_POTLUCK_AUTH_REDIS_URL'):
            logger.debug('Identity cache url (DH_POTLUCK_AUTH_REDIS_URL) not configured')
            return None
        if not cls.cache:
            cls.cache = FlaskRedis(
                app=current_app, config_prefix='DH_POTLUCK_AUTH_REDIS', socket_timeout=0.4
            )
        return cls.cache


def _get_from_cache(token):
    logger.debug('Get identity from cache')
    cache = AuthCache.get_cache()
    if not cache:
        return None
    try:
        cached_identity = cache.get(get_auth_cache_key(token))
        if cached_identity:
            logger.debug('Identity found!')
            return jsonify(loads(cached_identity)).json
    except (ConnectionError, TimeoutError) as e:
        logger.exception(f'Error getting identity from cache: {e}')
        return None


def get_auth_cache_key(token):
    hash_object = hashlib.sha256(token.encode('utf-8'))
    token_hash = hash_object.hexdigest()
    return f'auth:token#{token_hash}'


def validate_token_using_api(
    token: str,
    token_prefix: str = user_auth_header_value_prefix,
    on_behalf_of_user_id: Optional[int] = None,
) -> Optional[AuthenticatedUser]:
    if current_app.config.get('DH_POTLUCK_ENABLE_AUTH_CACHE') and not on_behalf_of_user_id:
        identity = _get_from_cache(token)
        if identity:
            return AuthenticatedUser(identity)

    logger.debug(
        f'Get {"impersonating" if on_behalf_of_user_id else ""} identity from auth service'
    )

    headers = {
        'Authorization': f'{token_prefix} {token}',
        'content-type': 'application/json',
    }
    if on_behalf_of_user_id:
        headers[impersonation_header_key] = str(on_behalf_of_user_id)
        if token_prefix == app_auth_header_value_prefix:
            token = current_app.config['DH_POTLUCK_AUTH_API_TOKEN']
            headers['Authorization'] = f'{token_prefix} {token}'

    auth_api_url = current_app.config['DH_POTLUCK_AUTH_API_URL']
    res = requests.get(auth_api_url + 'self', headers=headers)
    if res.status_code == HTTPStatus.OK:
        identity = res.json()
        return AuthenticatedUser(identity)

    return None
