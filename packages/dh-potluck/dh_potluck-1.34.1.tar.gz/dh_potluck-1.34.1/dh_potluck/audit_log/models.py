import enum
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Type

from sqlalchemy import JSON, Column, Enum, Index, Integer, String
from sqlalchemy.dialects import mysql
from sqlalchemy.ext.declarative import declared_attr

from dh_potluck.utils import get_db

logger = logging.getLogger(__name__)


class Operation(enum.Enum):
    insert = 'insert'
    update = 'update'
    delete = 'delete'


class AuditLog:
    """
    This table is populated via MySQL triggers. See ./trigger_templates for the
    implementation of these triggers.
    """

    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True)
    timestamp = Column(mysql.DATETIME(fsp=6), nullable=False)
    # Represents the method or entity that made the change. Typical values are:
    #   * `user` - A Flask user, authenticated or unauthenticated
    #   * `service` - An internal service using an `Application` token
    #   * `celery_task`
    #   * `alembic_migration`
    #   * `click_command`
    #   * `sqlalchemy` - A change made via SQLAlchemy ORM but not in the context of a request or
    #      one of the above methods
    #   * `mysql` - A change made via a raw MySQL command either via `conn.execute()` or via a SQL
    #      client
    updated_by_type = Column(String(255))

    # Values for each of the above types are:
    #   * `user` - The user id or 'unauthenticated'
    #   * `service` - Empty (until we can individually identify services making requests)
    #   * `celery_task` - The Celery task name
    #   * `alembic_migration` - The Alembic migration revision number
    #   * `click_command` - The Click command name
    #   * `sqlalchemy` - Empty
    #   * `mysql` - The MySQL user
    updated_by_id = Column(String(255))

    # The IP or hostname of the user making the request
    updated_by_ip = Column(String(255))
    table_name = Column(String(64), nullable=False)
    object_id = Column(String(64), nullable=False)
    operation = Column(Enum(Operation), nullable=False)
    old_data = Column(JSON)
    changed_data = Column(JSON)

    """
    Using the regular __table_args__ class attribute caused unit test failures.
    'sqlalchemy.exc.ArgumentError: Index 'ix_table_name_object_id' is against table 'audit_log',
    and cannot be associated with table 'audit_log'.'
    """

    @declared_attr
    def __table_args__(cls):
        table_args = (
            Index('ix_table_name_object_id', 'table_name', 'object_id'),
            Index('ix_timestamp', 'timestamp'),
        )
        return table_args


def delete_audit_logs_older_than(
    audit_log_model: Type[AuditLog],
    timestamp: Optional[datetime] = None,
    table_names: Optional[list[str]] = None,
) -> None:
    if timestamp is None:
        timestamp = datetime.now(tz=timezone.utc) - timedelta(days=30)

    logger.info(f'Deleting audit log history for tables {table_names} older than {timestamp}')

    current_db = get_db()
    logs_to_delete = current_db.session.query(audit_log_model).filter(
        audit_log_model.timestamp < timestamp
    )
    if table_names is not None:
        logs_to_delete = logs_to_delete.filter(audit_log_model.table_name.in_(table_names))

    logs_to_delete.delete(synchronize_session=False)
    current_db.session.commit()
