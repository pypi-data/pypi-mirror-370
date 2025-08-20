from decimal import Decimal
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from _typeshed import SupportsRead as SupportsReadT
    from _typeshed import SupportsWrite as SupportsWriteT

    SupportsRead = SupportsReadT[Any]
    SupportsWrite = SupportsWriteT[Any]
else:
    SupportsRead = object
    SupportsWrite = object


def _decimal_constructor(loader, node):  # type:ignore
    value = loader.construct_scalar(node)
    return Decimal(value)


# A semi-acceptable patch to force a number to be parsed as a decimal, since pyyaml
# parses them as lossy floats otherwise. Though a bit ugly, at least this way we have
# support for decimal constants
yaml.SafeLoader.add_constructor("!decimal", _decimal_constructor)


class YAMLError(BaseException):
    pass


def dumps(obj: Any, sort_keys: bool = False) -> str:
    return yaml.dump(obj, sort_keys=sort_keys)


def dump(obj: Any, f: SupportsWrite, sort_keys: bool = False) -> None:
    yaml.dump(obj, f, sort_keys=sort_keys)


def safe_load(src: str | bytes | SupportsRead) -> Any:
    try:
        return yaml.safe_load(src)
    except yaml.YAMLError as e:
        raise YAMLError() from e


def safe_dump(
    obj: Any,
    sort_keys: bool = False,
    indent: int | None = None,
    width: int | None = None,
) -> str:
    return yaml.safe_dump(obj, sort_keys=sort_keys, indent=indent, width=width)


def c_load(f: SupportsRead) -> Any:
    return yaml.load(f, Loader=yaml.CLoader)
