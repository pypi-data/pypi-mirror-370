from os import environ
from typing import List, Optional


def is_var_truthy(name: str, default: bool) -> bool:
    return environ.get(name, str(default)) in ['true', 'True', 'TRUE', '1']


def parse_list(name: str, default: Optional[str] = None, *, sep: str = ',') -> List[str]:
    raw_value = environ.get(name, default)
    return list(v.strip() for v in raw_value.split(sep)) if raw_value else []
