from dataclasses import fields
from typing import TYPE_CHECKING, Any, Iterator

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


def iterate_fields(d: "DataclassInstance") -> Iterator[tuple[str, Any]]:
    for field in fields(d):
        yield field.name, getattr(d, field.name)


def dict_fields(d: "DataclassInstance") -> dict[str, Any]:
    return dict(iterate_fields(d))
