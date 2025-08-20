from typing import (
    Any,
)

from pkgs.argument_parser import camel_to_snake_case
from pkgs.serialization import (
    MISSING_SENTRY,
    OpaqueKey,
)


def _key_convert_to_snake_case(o: Any) -> Any:
    if isinstance(o, OpaqueKey):
        return o
    if isinstance(o, str):
        return camel_to_snake_case(o)
    return o


def convert_dict_to_snake_case(data: Any) -> Any:
    return {
        _key_convert_to_snake_case(k): convert_dict_to_snake_case(v)
        if isinstance(v, dict)
        else v
        for k, v in data.items()
        if v != MISSING_SENTRY
    }
