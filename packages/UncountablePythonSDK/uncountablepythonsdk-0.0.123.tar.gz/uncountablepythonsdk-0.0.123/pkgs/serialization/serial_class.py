from __future__ import annotations

import dataclasses
from collections.abc import Callable
from enum import StrEnum
from typing import Any, TypeVar, cast

from .annotation import SerialBase, SerialInspector

ClassT = TypeVar("ClassT")


@dataclasses.dataclass(kw_only=True, frozen=True, eq=True)
class _SerialClassData(SerialBase):
    unconverted_keys: set[str] = dataclasses.field(default_factory=set)
    unconverted_values: set[str] = dataclasses.field(default_factory=set)
    to_string_values: set[str] = dataclasses.field(default_factory=set)
    parse_require: set[str] = dataclasses.field(default_factory=set)
    named_type_path: str | None = None


EMPTY_SERIAL_CLASS_DATA = _SerialClassData()


def serial_class(
    *,
    unconverted_keys: set[str] | None = None,
    unconverted_values: set[str] | None = None,
    to_string_values: set[str] | None = None,
    parse_require: set[str] | None = None,
    named_type_path: str | None = None,
    is_dynamic_allowed: bool = False,
) -> Callable[[ClassT], ClassT]:
    """
    An additional decorator to a dataclass that specifies serialization options.

    @param unconverted_keys
        The keys of these items will not be case converted (they will be
        left as-is)
    @param unconverted_values
        The values of these items (referred to by field name) will not undergo
        conversion beyond normal json serialization. They should generally
        contain only json compatible types, otherwise the resulting format is
        undefined.
    @param to_string_values
        For the values of these items (referred to by field name) to be strings.
        This is only useful for types where the string conversion makes sense,
        such as Decimal or int.
    @param parse_require
        This field is always required while parsing, even if it has a default in the definition.
        This allows supporting literal type defaults for Python instantiation, but
        requiring them for the API input.
    @param named_type_path
        The type_spec type-path to this type. This applies only to named types.
    """

    def decorate(orig_class: ClassT) -> ClassT:
        cast(Any, orig_class).__unc_serial_data = _SerialClassData(
            unconverted_keys=unconverted_keys or set(),
            unconverted_values=unconverted_values or set(),
            to_string_values=to_string_values or set(),
            parse_require=parse_require or set(),
            named_type_path=named_type_path,
            from_decorator=True,
            is_dynamic_allowed=is_dynamic_allowed,
        )
        return orig_class

    return decorate


class SerialClassDataInspector(SerialInspector[ClassT]):
    def __init__(
        self,
        parsed_type: type[ClassT],
        current: _SerialClassData,
    ) -> None:
        super().__init__(parsed_type, current)
        self.current = current

    def has_unconverted_key(self, key: str) -> bool:
        return key in self.current.unconverted_keys

    def has_unconverted_value(self, key: str) -> bool:
        return key in self.current.unconverted_values

    def has_to_string_value(self, key: str) -> bool:
        return key in self.current.to_string_values

    def has_parse_require(self, key: str) -> bool:
        return key in self.current.parse_require


def get_merged_serial_class_data(type_class: type[Any]) -> _SerialClassData | None:
    base_class_data = (
        cast(_SerialClassData, type_class.__unc_serial_data)
        if hasattr(type_class, "__unc_serial_data")
        else None
    )
    if base_class_data is None:
        return None

    # IMPROVE: We should cache this result on the type
    if type_class.__bases__ is not None:
        for base in type_class.__bases__:
            curr_base_class_data = get_merged_serial_class_data(base)
            if curr_base_class_data is not None:
                base_class_data = dataclasses.replace(
                    base_class_data,
                    unconverted_keys=base_class_data.unconverted_keys
                    | curr_base_class_data.unconverted_keys,
                    unconverted_values=base_class_data.unconverted_values
                    | curr_base_class_data.unconverted_values,
                    to_string_values=base_class_data.to_string_values
                    | curr_base_class_data.to_string_values,
                    parse_require=base_class_data.parse_require
                    | curr_base_class_data.parse_require,
                )
    return base_class_data


def get_serial_class_data(
    type_class: type[ClassT],
) -> SerialClassDataInspector[ClassT]:
    return SerialClassDataInspector(
        type_class, get_merged_serial_class_data(type_class) or EMPTY_SERIAL_CLASS_DATA
    )


@dataclasses.dataclass(kw_only=True)
class _SerialStringEnumData:
    labels: dict[str, str] = dataclasses.field(default_factory=dict)
    deprecated: set[str] = dataclasses.field(default_factory=set)


def serial_string_enum(
    *, labels: dict[str, str] | None = None, deprecated: set[str] | None = None
) -> Callable[[ClassT], ClassT]:
    """
    A decorator for enums to provide serialization data, including labels.
    """

    def decorate(orig_class: ClassT) -> ClassT:
        cast(Any, orig_class).__unc_serial_string_enum_data = _SerialStringEnumData(
            labels=labels or {}, deprecated=deprecated or set()
        )
        return orig_class

    return decorate


class SerialStringEnumInspector:
    def __init__(self, current: _SerialStringEnumData) -> None:
        self.current = current

    def get_label(self, value: str) -> str | None:
        return self.current.labels.get(value)

    def get_deprecated(self, value: str) -> bool:
        return value in self.current.deprecated


def get_serial_string_enum_data(type_class: type[StrEnum]) -> SerialStringEnumInspector:
    return SerialStringEnumInspector(
        cast(_SerialStringEnumData, type_class.__unc_serial_string_enum_data)
        if hasattr(type_class, "__unc_serial_string_enum_data")
        else _SerialStringEnumData(),
    )
