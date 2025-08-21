from datetime import datetime, timezone
from typing import Optional, Union

from sqlalchemy import engine, types
from sqlalchemy.dialects.mysql import DATETIME

FRACTIONAL_SECONDS_PRECISION = 6


class UtcDateTime(types.TypeDecorator[datetime]):
    impl = types.DateTime
    cache_ok = True

    def __init__(self, use_microseconds=False):
        if use_microseconds:
            self.impl = DATETIME(fsp=FRACTIONAL_SECONDS_PRECISION)
            return

        super().__init__()

    # Ignoring return type awaiting dropbox/sqlalchemy-stubs#206
    def process_bind_param(  # type: ignore
        self, value: Optional[datetime], dialect: engine.Dialect
    ) -> Optional[Union[str, datetime]]:
        if value is None:
            return value

        if isinstance(value, str):
            return value

        return value.replace(tzinfo=timezone.utc)

    def process_result_value(
        self, value: Optional[datetime], dialect: engine.Dialect
    ) -> Optional[datetime]:
        if value is None:
            return value

        return value.replace(tzinfo=timezone.utc)
