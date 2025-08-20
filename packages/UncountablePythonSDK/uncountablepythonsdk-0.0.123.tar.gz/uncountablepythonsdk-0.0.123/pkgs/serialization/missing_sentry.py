from typing import Optional, TypeVar, Union

ClassT = TypeVar("ClassT")


class MissingSentryType:
    """
    A unique type for the MISSING_SENTRY to avoid clashes with any other
    type.
    """

    _instance: Optional["MissingSentryType"] = None

    def __new__(cls) -> "MissingSentryType":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __bool__(self) -> bool:
        raise ValueError("Bool check on missing type")


MISSING_SENTRY = MissingSentryType()

# The MissingSentryType is expected to come first for serialization parsing
MissingType = Union[MissingSentryType, ClassT]


def coalesce_missing_sentry(value: MissingType[ClassT]) -> ClassT | None:
    return None if isinstance(value, MissingSentryType) else value
