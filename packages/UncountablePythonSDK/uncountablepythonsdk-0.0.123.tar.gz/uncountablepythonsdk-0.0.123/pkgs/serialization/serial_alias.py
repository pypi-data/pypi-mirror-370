import dataclasses
import typing

from .annotation import SerialBase, SerialInspector, get_serial_annotation

T = typing.TypeVar("T")


@dataclasses.dataclass(kw_only=True, frozen=True, eq=True)
class _SerialAlias(SerialBase):
    """
    This class is to be kept private, to provide flexibility in registration/lookup.
    Places that need the data should access it via help classes/methods.
    """


def serial_alias_annotation(
    *,
    named_type_path: str | None = None,
    is_dynamic_allowed: bool = False,
) -> _SerialAlias:
    return _SerialAlias(
        named_type_path=named_type_path,
        from_decorator=True,
        is_dynamic_allowed=is_dynamic_allowed,
    )


def _get_serial_alias(parsed_type: type[T]) -> _SerialAlias | None:
    serial = get_serial_annotation(parsed_type)
    if not isinstance(serial, _SerialAlias):
        return None
    return serial


class SerialAliasInspector(SerialInspector[T]):
    def __init__(self, parsed_type: type[T], serial_alias: _SerialAlias) -> None:
        super().__init__(parsed_type, serial_alias)
        self._serial_alias = serial_alias


def get_serial_alias_data(parsed_type: type[T]) -> SerialAliasInspector[T] | None:
    serial = _get_serial_alias(parsed_type)
    if serial is None:
        return None

    return SerialAliasInspector(parsed_type, serial)
