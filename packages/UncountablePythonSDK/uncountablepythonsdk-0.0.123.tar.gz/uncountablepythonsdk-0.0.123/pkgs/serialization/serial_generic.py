import typing

from .annotation import SerialInspector, get_serial_annotation
from .serial_class import get_merged_serial_class_data

T = typing.TypeVar("T")


def get_serial_data(parsed_type: type[T]) -> SerialInspector[T] | None:
    serial = get_serial_annotation(parsed_type)
    if serial is None:
        serial = get_merged_serial_class_data(parsed_type)

    if serial is not None:
        return SerialInspector(parsed_type, serial)
    return None
