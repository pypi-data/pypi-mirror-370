from datetime import datetime, timezone
from typing import Optional

from marshmallow.fields import AwareDateTime, DateTime, Field


class EnumField(Field):
    """
    This replacement for EnumField is used to resolve an issue where the default marshmallow enum
    did not work to properly serialize allowed values and the property, missing, for the API spec.
    """

    default_error_messages = {
        'invalid': 'Invalid enum value {input}',
    }

    def __init__(self, enum_type, *args, **kwargs):
        self.enum = enum_type

        super().__init__(*args, **kwargs)

        # Detect type of enum and make it available to apispec
        values = [e.value for e in self.enum if e.value is not None]
        if all(isinstance(v, int) for v in values):
            self.metadata['type'] = 'integer'
        elif all(isinstance(v, (float, int)) for v in values):
            self.metadata['type'] = 'number'
        elif all(isinstance(v, bool) for v in values):
            self.metadata['type'] = 'boolean'
        elif all(isinstance(v, str) for v in values):
            self.metadata['type'] = 'string'

        # Ensure all enum values are made available to apispec
        self.metadata['enum'] = sorted([e.value for e in self.enum])

    # These template methods are not invoked when constructing the apispec
    # but they are used by the routes
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.value

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        try:
            return self.enum(value)
        except ValueError as error:
            raise self.make_error('invalid', input=value, value=value) from error

    def make_error(self, key, **kwargs):
        kwargs['values'] = ', '.join([str(mem.value) for mem in self.enum])
        return super().make_error(key, **kwargs)


class UTCDateTime(DateTime):
    """
    This replacement for Marshmallow's DateTime field replicates Marshmallow 2.x's behaviour of
    adding explicit timezone data to naive datetimes on serialization, which was changed in 3.x.

    Deprecated; please use AwareDateTimeField below.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        if type(value) is datetime:
            # Assume no timezone means UTC to keep in line with Marshmallow 2.x behaviour
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            else:
                value = value.astimezone(timezone.utc)
        dt = super()._serialize(value, attr, obj, **kwargs)
        return dt


class UTCAwareDateTime(AwareDateTime):
    """Uses Marshmallow 3's AwareDateTime field to handle datetimes assumed to be
    already aware. Subclassed to convert timezone to default TZ (UTC) on serialization.

    Use with UtcDateTime sqlalchemy decorator."""

    def __init__(self, *args, default_timezone: timezone = timezone.utc, **kwargs) -> None:
        super().__init__(*args, default_timezone=default_timezone, **kwargs)

    def _serialize(self, value: Optional[datetime], attr, obj, **kwargs) -> str:
        return super()._serialize(
            value.astimezone(timezone.utc) if value else None, attr, obj, **kwargs
        )

    def _deserialize(self, value: Optional[str], attr, data, **kwargs) -> datetime:
        datetime = super()._deserialize(value, attr, data, **kwargs)
        return datetime.astimezone(timezone.utc) if datetime else None
