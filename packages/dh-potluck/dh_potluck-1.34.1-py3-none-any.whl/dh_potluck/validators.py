import re
from typing import List
from urllib.parse import urlparse

from marshmallow import ValidationError, validate


class AllowedDomain(validate.Validator):
    default_message = 'URL is not from an approved domain.'

    def __init__(
        self,
        *,
        allowed_domain_regexes: List[str],
        error: str | None = None,
    ):
        self.allowed_domain_regexes = [
            re.compile(allowed_domain_regex) for allowed_domain_regex in allowed_domain_regexes
        ]
        self.error: str = error or self.default_message

    def _format_error(self, value: str) -> str:
        return self.error.format(input=value)

    def __call__(self, value: str) -> str:
        message = self._format_error(value)
        if not value:
            raise ValidationError(message)

        domain = urlparse(value).netloc
        if not any(regex.match(domain) for regex in self.allowed_domain_regexes):
            raise ValidationError(message)

        return value
