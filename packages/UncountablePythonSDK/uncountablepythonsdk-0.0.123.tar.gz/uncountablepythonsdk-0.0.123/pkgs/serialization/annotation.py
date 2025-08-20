import dataclasses
import typing

T = typing.TypeVar("T")


@dataclasses.dataclass(kw_only=True, frozen=True, eq=True)
class SerialBase:
    named_type_path: str | None = None
    # Indicates this type is allowed in dynamic lookups, such as via a named_type_path
    # This isn't meant to be limting, but to catalog all the types where we need it
    is_dynamic_allowed: bool = False
    # Tracks if this data was provided as a decorator to the type.
    # This is used to track "proper types" which are appropriate
    # for serialization and/or dynamic discovery
    from_decorator: bool = False


def get_serial_annotation(parsed_type: type[T]) -> SerialBase | None:
    if not hasattr(parsed_type, "__metadata__"):
        return None
    metadata = parsed_type.__metadata__  # type:ignore[attr-defined]
    if not isinstance(metadata, tuple) or len(metadata) != 1:
        return None
    serial = metadata[0]
    if not isinstance(serial, SerialBase):
        return None
    return serial


class SerialInspector(typing.Generic[T]):
    def __init__(self, parsed_type: type[T], serial_base: SerialBase) -> None:
        self._parsed_type = parsed_type
        self._serial_base = serial_base

    @property
    def named_type_path(self) -> str | None:
        return self._serial_base.named_type_path

    @property
    def from_decorator(self) -> bool:
        return self._serial_base.from_decorator

    @property
    def is_field_proper(self) -> bool:
        return (
            self._serial_base.from_decorator
            and self._serial_base.named_type_path is not None
        )

    @property
    def is_dynamic_allowed(self) -> bool:
        return self._serial_base.is_dynamic_allowed


def unwrap_annotated(parsed_type: type[T]) -> type[T]:
    """
    If the type is an annotated type then return the origin of it.
    Otherwise return the original type.
    """
    if typing.get_origin(parsed_type) is typing.Annotated:
        # It's unclear if there's anyway to type this correctly
        return parsed_type.__origin__  # type:ignore[attr-defined, no-any-return]
    return parsed_type
