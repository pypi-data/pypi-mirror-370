import dataclasses
import typing

from .annotation import SerialBase, SerialInspector, get_serial_annotation

T = typing.TypeVar("T")


class IdentityHashWrapper(typing.Generic[T]):
    """This allows unhashable types to be used in the SerialUnion, like dict.
    Since we have only one copy of the types themselves, we rely on
    object identity for the hashing."""

    def __init__(self, inner: T) -> None:
        self.inner = inner

    def __hash__(self) -> int:
        return id(self.inner)


@dataclasses.dataclass(kw_only=True, frozen=True, eq=True)
class _SerialUnion(SerialBase):
    """
    This class is to be kept private, to provide flexibility in registration/lookup.
    Places that need the data should access it via help classes/methods.
    """

    # If specified, indicates the Union has a discriminator which should be used to
    # determine which type to parse.
    discriminator: str | None = None
    discriminator_map: IdentityHashWrapper[dict[str, type]] | None = None


def serial_union_annotation(
    *,
    discriminator: str | None = None,
    discriminator_map: dict[str, type] | None = None,
    named_type_path: str | None = None,
    is_dynamic_allowed: bool = False,
) -> _SerialUnion:
    return _SerialUnion(
        discriminator=discriminator,
        discriminator_map=IdentityHashWrapper(discriminator_map)
        if discriminator_map is not None
        else None,
        named_type_path=named_type_path,
        from_decorator=True,
        is_dynamic_allowed=is_dynamic_allowed,
    )


def _get_serial_union(parsed_type: type[T]) -> _SerialUnion | None:
    serial = get_serial_annotation(parsed_type)
    if not isinstance(serial, _SerialUnion):
        return None
    return serial


class SerialClassInspector(SerialInspector[T]):
    def __init__(self, parsed_type: type[T], serial_union: _SerialUnion) -> None:
        super().__init__(parsed_type, serial_union)
        self._parsed_type = parsed_type
        self._serial_union = serial_union

    def get_union_underlying(self) -> type[T]:
        return typing.get_args(self._parsed_type)[0]  # type:ignore[no-any-return]

    @property
    def discriminator(self) -> str | None:
        return self._serial_union.discriminator

    @property
    def discriminator_map(self) -> dict[str, type] | None:
        if self._serial_union.discriminator_map is None:
            return None
        return self._serial_union.discriminator_map.inner


def get_serial_union_data(parsed_type: type[T]) -> SerialClassInspector[T] | None:
    serial = _get_serial_union(parsed_type)
    if serial is None:
        return None

    return SerialClassInspector(parsed_type, serial)
