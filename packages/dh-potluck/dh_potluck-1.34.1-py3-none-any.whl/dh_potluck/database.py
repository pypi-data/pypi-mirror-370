import functools

import sqlalchemy
from packaging import version
from sqlalchemy import text


class disable_autocommit:
    """
    A context manager and decorator that temporarily disables autocommit behaviour. It automatically
    restores the original isolation level when the block or decorated function ends, and rollbacks
    any changes if they fail or are otherwise uncommitted.

    Parameters:
    - session (sqlalchemy.orm.session.Session): The database session to disable autocommit for.
    - isolation_level (str, optional): The transaction isolation level to be used for this context.
    Defaults to 'READ COMMITTED'.

    Examples:
    ```python
    with disable_autocommit(db.session):
        db.session.add(new_record)
        # More database operations...
        db.session.commit()
    ```

    ```python
    @disable_autocommit(db.session)
    def my_func():
        db.session.add(new_record)
        # More database operations...
        db.session.commit()
    ```
    """

    def __init__(self, session, isolation_level='READ COMMITTED'):
        self.session = session
        self.isolation_level = isolation_level
        self.original_isolation_level = None

    def __enter__(self):
        if version.parse(sqlalchemy.__version__) < version.parse('2.0.20'):
            raise Exception('This context manager / decorator requires SQLAlchemy >= 2.0.20')

        connection = self.session.connection()
        is_autocommit = connection._is_autocommit_isolation()
        self.original_isolation_level = connection.default_isolation_level

        if not is_autocommit:
            raise Exception(
                'Isolation level must be AUTOCOMMIT in order to use `disable_autocommit()`.'
            )

        # Ensure the current transaction is closed
        self.session.rollback()

        # Disable autocommit and set isolation level to the provided value
        self.session.connection(execution_options={'isolation_level': self.isolation_level})

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Re-enable autocommit and discard anything not explicitly committed in the context manager
        self.session.rollback()

        # Restore the original isolation level if necessary. This is necessary because while
        # SQLAlchemy treats autocommit as an isolation level, it's not one in the DB. In theory,
        # the DB isolation level shouldn't matter much when autocommit is enabled, but to be safe
        # we set it back to the original value here.
        if self.isolation_level != self.original_isolation_level:
            self.session.execute(
                text(f'SET SESSION TRANSACTION ISOLATION LEVEL {self.original_isolation_level}')
            )

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper
