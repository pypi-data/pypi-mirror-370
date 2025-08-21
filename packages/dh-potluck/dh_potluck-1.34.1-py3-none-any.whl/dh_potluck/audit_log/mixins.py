import re
from datetime import datetime

import click
from flask import current_app, request
from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import DATETIME

from dh_potluck.auth import ApplicationUser, UnauthenticatedUser

# Take into account that not all backends use Celery
try:
    import celery
except ImportError:
    celery = None


# Currently all backends use alembic but we may be moving away from this
try:
    from alembic import op  # type: ignore
except ImportError:
    op = None


def get_alembic_context():
    try:
        return op.get_context()
    except Exception:
        return None


def get_potluck_current_user():
    try:
        return current_app.extensions['dh-potluck'].current_user
    except AttributeError:
        return None


def get_request_ip():
    try:
        return request.remote_addr
    except RuntimeError:
        return None


def get_request_user_agent():
    user_agent = request.headers.get('User-Agent', '')

    # Remove "Dash Hudson" from the beginning if it exists
    user_agent = user_agent.replace('Dash Hudson', '')

    # Convert the remaining string to kebab-case
    user_agent = re.sub(r'\s+', '-', user_agent.strip().lower())

    return user_agent


def get_updated_by():
    """
    Do our best to generate a string containing the details about who is making an update. Used
    by the audit logging triggers defined in ./commands.py.
    """
    updated_by_type = 'sqlalchemy'
    updated_by_id = None
    updated_by_ip = get_request_ip()
    potluck_current_user = get_potluck_current_user()

    if potluck_current_user:
        if hasattr(potluck_current_user, 'id'):
            updated_by_type = 'user'
            updated_by_id = potluck_current_user.id
        elif isinstance(potluck_current_user, UnauthenticatedUser):
            updated_by_type = 'user'
            updated_by_id = 'unauthenticated'
        elif isinstance(potluck_current_user, ApplicationUser):
            updated_by_type = 'service'
            updated_by_id = get_request_user_agent()
    elif celery and celery.current_task:
        updated_by_type = 'celery_task'
        updated_by_id = celery.current_task.name
    elif op and get_alembic_context():
        updated_by_type = 'alembic_migration'
        updated_by_id = get_alembic_context().get_current_revision()
    elif click.get_current_context(silent=True):
        updated_by_type = 'click_command'
        updated_by_id = click.get_current_context().command.name

    updated_by = {
        'updated_by_type': updated_by_type,
        'updated_by_id': updated_by_id,
        'updated_by_ip': updated_by_ip,
    }

    return updated_by


class UpdatedByMixin:
    updated_by_type = Column(
        String(255),
        default=lambda context: get_updated_by()['updated_by_type'],
        onupdate=lambda context: get_updated_by()['updated_by_type'],
    )
    updated_by_id = Column(
        String(255),
        default=lambda context: get_updated_by()['updated_by_id'],
        onupdate=lambda context: get_updated_by()['updated_by_id'],
    )
    updated_by_ip = Column(
        String(255),
        default=lambda context: get_updated_by()['updated_by_ip'],
        onupdate=lambda context: get_updated_by()['updated_by_ip'],
    )


class PreciseCreatedUpdatedMixin:
    """
    Created / updated timestamp fields with higher precision than the SQLAlchemy default which
    is just second-level precision.

    If you take a look at `./trigger_templates/audit_inserts.jinja2`,
    we're comparing OLD.updated_at = NEW.updated_at to determine if a query was executed by
    SQLAlchemy (i.e. updated_at value changed) or manually (i.e. updated_at unchanged). There is
    an edge case where two updates can happen very rapidly in quick succession within the same
    second and the trigger thinks the second one was manually executed. The increase in precision
    eliminates that edge case.
    """

    created_at = Column(
        DATETIME(fsp=6),
        nullable=False,
        default=lambda: datetime.utcnow(),
    )
    updated_at = Column(
        DATETIME(fsp=6),
        nullable=False,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
