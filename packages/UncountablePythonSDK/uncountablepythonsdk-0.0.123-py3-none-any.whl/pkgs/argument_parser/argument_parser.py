from __future__ import annotations

import dataclasses
import datetime
import math
import types
import typing
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import date
from decimal import Decimal
from enum import Enum, auto
from importlib import resources

import dateutil.parser
import msgspec.yaml

from pkgs.serialization import (
    MissingSentryType,
    OpaqueKey,
    get_serial_class_data,
    get_serial_union_data,
)

from ._is_enum import is_string_enum_class
from ._is_namedtuple import is_namedtuple_type
from .case_convert import camel_to_snake_case, snake_to_camel_case

T = typing.TypeVar("T")
ParserFunction = typing.Callable[[typing.Any], T]
ParserCache = dict[type[typing.Any], ParserFunction[typing.Any]]


class SourceEncoding(Enum):
    API = auto()
    STORAGE = auto()


@dataclasses.dataclass(frozen=True, eq=True)
class ParserOptions:
    encoding: SourceEncoding
    strict_property_parsing: bool = False

    @staticmethod
    def Api(*, strict_property_parsing: bool = False) -> ParserOptions:
        return ParserOptions(
            encoding=SourceEncoding.API, strict_property_parsing=strict_property_parsing
        )

    @staticmethod
    def Storage(*, strict_property_parsing: bool = False) -> ParserOptions:
        return ParserOptions(
            encoding=SourceEncoding.STORAGE,
            strict_property_parsing=strict_property_parsing,
        )

    @property
    def from_camel_case(self) -> bool:
        return self.encoding == SourceEncoding.API

    @property
    def allow_direct_type(self) -> bool:
        """This allows parsing from a DB column without having to check whether it's
        the native format of the type, a JSON column, or a string encoding."""
        return self.encoding == SourceEncoding.STORAGE


@dataclasses.dataclass(frozen=True)
class ParserContext:
    options: ParserOptions
    cache: ParserCache


class ParserError(BaseException): ...


class ParserExtraFieldsError(ParserError):
    extra_fields: set[str]

    def __init__(self, extra_fields: set[str]) -> None:
        self.extra_fields = extra_fields

    def __str__(self) -> str:
        return f"extra fields were provided: {', '.join(self.extra_fields)}"


def is_union(field_type: typing.Any) -> bool:
    origin = typing.get_origin(field_type)
    return origin is typing.Union or origin is types.UnionType


def is_optional(field_type: typing.Any) -> bool:
    return is_union(field_type) and type(None) in typing.get_args(field_type)


def is_missing(field_type: typing.Any) -> bool:
    if not is_union(field_type):
        return False
    args = typing.get_args(field_type)
    return not (len(args) == 0 or args[0] is not MissingSentryType)


def _has_field_default(field: dataclasses.Field[typing.Any]) -> bool:
    return (
        field.default != dataclasses.MISSING
        and not isinstance(field.default, MissingSentryType)
    ) or field.default_factory != dataclasses.MISSING


def _get_field_default(
    field: dataclasses.Field[typing.Any],
) -> typing.Any:
    if field.default != dataclasses.MISSING:
        return field.default
    assert field.default_factory != dataclasses.MISSING
    return field.default_factory()


def _invoke_tuple_parsers(
    tuple_type: type[T],
    arg_parsers: typing.Sequence[typing.Callable[[typing.Any], object]],
    has_ellipsis: bool,
    value: typing.Any,
) -> T:
    if has_ellipsis:
        assert len(arg_parsers) == 1
        arg_parser = arg_parsers[0]
        output = (arg_parser(subvalue) for subvalue in value)
    else:
        assert len(value) == len(arg_parsers)
        output = (
            arg_parser(subvalue) for arg_parser, subvalue in zip(arg_parsers, value)
        )

    return typing.cast(T, tuple(output))


def _invoke_fallback_parsers(
    original_type: type[T],
    arg_parsers: typing.Sequence[typing.Callable[[typing.Any], T]],
    value: typing.Any,
) -> T:
    exceptions = []

    for parser in arg_parsers:
        try:
            return parser(value)
        except Exception as e:
            exceptions.append(e)
            continue
    raise ValueError(
        f"Unhandled value {value} cannot be cast to a member of {original_type}"
    ) from ExceptionGroup("Fallback Parser Exception", exceptions)


def _invoke_membership_parser(
    expected_values: set[T],
    value: typing.Any,
) -> T:
    """
    Look for the expected_value that matches the provided value. We return the expected_value
    since it may not be the same type as the input (for example, with an enum)
    """
    for test_value in expected_values:
        if value == test_value:
            return test_value

    raise ValueError(f"Expected value from {expected_values} but got value {value}")


def _build_parser_discriminated_union(
    context: ParserContext,
    discriminator_raw: str,
    discriminator_map: dict[str, ParserFunction[T]],
) -> ParserFunction[T]:
    discriminator = (
        snake_to_camel_case(discriminator_raw)
        if context.options.from_camel_case
        else discriminator_raw
    )

    def parse(value: typing.Any) -> typing.Any:
        if context.options.allow_direct_type and dataclasses.is_dataclass(value):
            discriminant = getattr(value, discriminator)
        else:
            discriminant = value.get(discriminator)
        if discriminant is None:
            raise ValueError("missing-union-discriminant")
        if not isinstance(discriminant, str):
            raise ValueError("union-discriminant-is-not-string")
        parser = discriminator_map.get(discriminant)
        if parser is None:
            raise ValueError("missing-type-for-union-discriminant", discriminant)
        return parser(value)

    return parse


def _build_parser_inner(
    parsed_type: type[T],
    context: ParserContext,
) -> ParserFunction[T]:
    """
    IMPROVE: We can now cache at this level, to avoid producing redundant
    internal parsers.
    """

    serial_union = get_serial_union_data(parsed_type)
    if serial_union is not None:
        discriminator = serial_union.discriminator
        discriminator_map = serial_union.discriminator_map
        if discriminator is None or discriminator_map is None:
            # fallback to standard union parsing
            parsed_type = serial_union.get_union_underlying()
        else:
            return _build_parser_discriminated_union(
                context,
                discriminator,
                {
                    key: _build_parser_inner(value, context)
                    for key, value in discriminator_map.items()
                },
            )

    if dataclasses.is_dataclass(parsed_type):
        return _build_parser_dataclass(parsed_type, context)

    # namedtuple support
    if is_namedtuple_type(parsed_type):
        type_hints = typing.get_type_hints(parsed_type)
        field_parsers = [
            (field_name, _build_parser_inner(type_hints[field_name], context))
            for field_name in parsed_type.__annotations__
        ]
        return lambda value: parsed_type(**{
            field_name: field_parser(
                value.get(
                    snake_to_camel_case(field_name)
                    if context.options.from_camel_case
                    else field_name
                )
            )
            for field_name, field_parser in field_parsers
        })

    if parsed_type == type(None):  # noqa: E721
        return lambda value: _invoke_membership_parser({None}, value)

    origin = typing.get_origin(parsed_type)
    if origin is tuple:
        args = typing.get_args(parsed_type)
        element_parsers: list[typing.Callable[[typing.Any], object]] = []
        has_ellipsis = False
        for arg in args:
            assert not has_ellipsis
            if arg is Ellipsis:
                assert len(element_parsers) == 1
                has_ellipsis = True
            else:
                element_parsers.append(_build_parser_inner(arg, context))
        return lambda value: _invoke_tuple_parsers(
            parsed_type, element_parsers, has_ellipsis, value
        )

    if origin is typing.Union or isinstance(parsed_type, types.UnionType):
        args = typing.get_args(parsed_type)
        sorted_args = sorted(
            args,
            key=lambda subtype: (0 if subtype == type(None) else 1),  # noqa: E721
        )
        arg_parsers = [_build_parser_inner(arg, context) for arg in sorted_args]
        return lambda value: _invoke_fallback_parsers(parsed_type, arg_parsers, value)

    if parsed_type is typing.Any:
        return lambda value: value

    if origin in (list, set):
        args = typing.get_args(parsed_type)
        if len(args) != 1:
            raise ValueError("List types only support one argument")
        arg_parser = _build_parser_inner(args[0], context)

        def parse_element(value: typing.Any) -> typing.Any:
            try:
                return arg_parser(value)
            except Exception as e:
                raise ValueError("Failed to parse element", value) from e

        def parse(value: typing.Any) -> typing.Any:
            if not isinstance(value, list):
                raise ValueError("value is not a list", parsed_type)
            return origin(parse_element(x) for x in value)

        return parse

    if origin is dict:
        args = typing.get_args(parsed_type)
        if len(args) != 2:
            raise ValueError("Dict types only support two arguments for now")
        k_inner_parser = _build_parser_inner(
            args[0],
            context,
        )

        def key_parser(value: typing.Any) -> object:
            inner = k_inner_parser(value)
            if (
                isinstance(inner, str)
                # enum keys and OpaqueData's would also have string value types,
                # but their explicit type is not a string, thus shouldn't be converted
                and args[0] is str
                and context.options.from_camel_case
            ):
                return camel_to_snake_case(value)
            return inner

        v_parser = _build_parser_inner(args[1], context)
        return lambda value: origin(
            (key_parser(k), v_parser(v)) for k, v in value.items()
        )

    if origin == typing.Literal:
        valid_values: set[T] = set(typing.get_args(parsed_type))
        return lambda value: _invoke_membership_parser(valid_values, value)

    if parsed_type is int:
        # first parse ints to decimal to allow scientific notation and decimals
        # e.g. (1) 1e4 => 1000, (2) 3.0 => 3

        def parse_int(value: typing.Any) -> T:
            if isinstance(value, str):
                assert "_" not in value, (
                    "numbers with underscores not considered integers"
                )

            dec_value = Decimal(value)
            int_value = int(dec_value)
            assert int_value == dec_value, (
                f"value ({value}) cannot be parsed to int without discarding precision"
            )
            return int_value  # type: ignore

        return parse_int

    if parsed_type is datetime.datetime:

        def parse_datetime(value: typing.Any) -> T:
            if context.options.allow_direct_type and isinstance(
                value, datetime.datetime
            ):
                return value  # type: ignore
            return dateutil.parser.isoparse(value)  # type:ignore

        return parse_datetime

    if parsed_type is date:

        def parse_date(value: typing.Any) -> T:
            if context.options.allow_direct_type and isinstance(value, date):
                return value  # type:ignore
            return date.fromisoformat(value)  # type:ignore

        return parse_date

    # MyPy: It's unclear why `parsed_type in (str, OpaqueKey)` is flagged as invalid
    # Thus an or statement is used instead, which isn't flagged as invalid.
    if parsed_type is str or parsed_type is OpaqueKey:

        def parse_str(value: typing.Any) -> T:
            if isinstance(value, str):
                return value  # type: ignore
            if isinstance(value, (float, int)):
                return str(value)  # type: ignore
            raise ValueError(f"Invalid string value: {type(value)}: {value}")

        return parse_str

    if parsed_type in (float, Decimal):

        def parse_as_numeric_type(value: typing.Any) -> T:
            numeric_value: Decimal | float = parsed_type(value)  # type: ignore
            if math.isnan(numeric_value):
                raise ValueError(f"Invalid numeric value: {numeric_value}")

            return numeric_value  # type: ignore

        return parse_as_numeric_type

    if parsed_type in (dict, bool) or is_string_enum_class(parsed_type):
        return lambda value: parsed_type(value)  # type: ignore

    if parsed_type is MissingSentryType:

        def error(value: typing.Any) -> T:
            raise ValueError("Missing type cannot be parsed directly")

        return error

    # Check last for generic annotated types and process them unwrapped
    # this must be last, since some of the expected types, like Unions,
    # will also be annotated, but have a special form
    if typing.get_origin(parsed_type) is typing.Annotated:
        return _build_parser_inner(
            parsed_type.__origin__,  # type: ignore[attr-defined]
            context,
        )

    raise ValueError(f"Unhandled type {parsed_type}/{origin}")


def _build_parser_dataclass(
    parsed_type: type[T],
    context: ParserContext,
) -> ParserFunction[T]:
    """
    Use the cache so that recursion involve dataclasses is supported. This
    requires the build order is a bit inverted: the dataclass parser is added
    to the cache prior to building it's field parsers.
    """
    cur_parser = context.cache.get(parsed_type)
    if cur_parser is not None:
        return cur_parser
    type_hints = typing.get_type_hints(parsed_type, include_extras=True)
    dc_field_parsers: list[
        tuple[
            dataclasses.Field[typing.Any],
            type[typing.Any],
            ParserFunction[typing.Any],
        ]
    ] = []

    serial_class_data = get_serial_class_data(parsed_type)

    def resolve_serialized_field_name(*, field_name: str) -> str:
        return (
            snake_to_camel_case(field_name)
            if (
                context.options.from_camel_case
                and not serial_class_data.has_unconverted_key(field_name)
            )
            else field_name
        )

    def parse(value: typing.Any) -> typing.Any:
        # Use an exact type match to prevent base/derived class mismatches
        if context.options.allow_direct_type and type(value) is parsed_type:
            return value

        data: dict[typing.Any, typing.Any] = {}
        for field, field_type, field_parser in dc_field_parsers:
            field_raw_value = None
            try:
                field_raw_value = value.get(
                    resolve_serialized_field_name(field_name=field.name),
                    dataclasses.MISSING,
                )
                field_value: typing.Any
                if field_raw_value == dataclasses.MISSING:
                    if serial_class_data.has_parse_require(field.name):
                        raise ValueError("missing-required-field", field.name)
                    if _has_field_default(field):
                        field_value = _get_field_default(field)
                    elif is_missing(field_type):
                        field_value = MissingSentryType()
                    elif is_optional(field_type):
                        # Backwards compatibilty to dataclasses that didn't set a default value
                        # IMPROVE: should we deprecate this?
                        field_value = None
                    elif field_type is bool:
                        # Backwards compatibilty to dataclasses that didn't set a default value
                        field_value = False
                    else:
                        raise ValueError("missing-value-for-field", field.name)
                elif (
                    field_raw_value is None
                    and not is_optional(field_type)
                    and _has_field_default(field)
                    and not serial_class_data.has_parse_require(field.name)
                ):
                    field_value = _get_field_default(field)
                elif serial_class_data.has_unconverted_value(field.name):
                    field_value = field_raw_value
                else:
                    field_value = field_parser(field_raw_value)

                data[field.name] = field_value

            except Exception as e:
                raise ValueError(
                    f"unable-to-parse-field:{field.name}", field_raw_value
                ) from e

        if context.options.strict_property_parsing:
            all_allowed_field_names = set(
                resolve_serialized_field_name(field_name=field.name)
                for (field, _, _) in dc_field_parsers
            )
            passed_field_names = set(value.keys())
            disallowed_field_names = passed_field_names.difference(
                all_allowed_field_names
            )
            if len(disallowed_field_names) > 0:
                raise ParserExtraFieldsError(disallowed_field_names)

        return parsed_type(**data)

    # Add to cache before building inner types, to support recursion
    parser_function = parse
    context.cache[parsed_type] = parser_function

    dc_field_parsers = [
        (
            field,
            type_hints[field.name],
            _build_parser_inner(type_hints[field.name], context),
        )
        for field in dataclasses.fields(parsed_type)  # type:ignore[arg-type]
    ]

    return parser_function


_CACHE_MAP: dict[ParserOptions, ParserCache] = defaultdict(ParserCache)


def build_parser(
    parsed_type: type[T],
    options: ParserOptions,
) -> ParserFunction[T]:
    """
    Consider using CachedParser to provide a cleaner API for storage and API
    data parsing.
    """

    # Keep a cache per ParserOptions type, as they produce distinct parsers
    cache = _CACHE_MAP[options]

    cur_parser = cache.get(parsed_type)
    if cur_parser is not None:
        return cur_parser

    context = ParserContext(options=options, cache=cache)
    built_parser = _build_parser_inner(parsed_type, context)
    cache[parsed_type] = built_parser
    return built_parser


class ParserBase(ABC, typing.Generic[T]):
    def parse_from_encoding(
        self,
        args: typing.Any,
        *,
        source_encoding: SourceEncoding,
    ) -> T:
        match source_encoding:
            case SourceEncoding.API:
                return self.parse_api(args)
            case SourceEncoding.STORAGE:
                return self.parse_storage(args)
            case _:
                typing.assert_never(source_encoding)

    # IMPROVE: Args would be better typed as "object"
    @abstractmethod
    def parse_storage(self, args: typing.Any) -> T: ...

    @abstractmethod
    def parse_api(self, args: typing.Any) -> T: ...

    def parse_yaml_file(self, path: str) -> T:
        with open(path, encoding="utf-8") as data_in:
            return self.parse_storage(msgspec.yaml.decode(data_in.read()))

    def parse_yaml_resource(self, package: resources.Package, resource: str) -> T:
        with resources.open_text(package, resource) as fp:
            return self.parse_storage(msgspec.yaml.decode(fp.read()))


class CachedParser(ParserBase[T], typing.Generic[T]):
    def __init__(
        self,
        args: type[T],
        strict_property_parsing: bool = False,
    ):
        self.arguments = args
        self.parser_api: ParserFunction[T] | None = None
        self.parser_storage: ParserFunction[T] | None = None
        self.strict_property_parsing = strict_property_parsing

    def parse_api(self, args: typing.Any) -> T:
        """
        Parses data coming from an API/Endpoint

        NOTE: Some places use this to parse storage data due to backwards
        compatibility. If your data is coming from the DB or a file, it is
        preferred to use parse_storage.
        """
        if self.parser_api is None:
            self.parser_api = build_parser(
                self.arguments,
                ParserOptions.Api(
                    strict_property_parsing=self.strict_property_parsing,
                ),
            )
        assert self.parser_api is not None
        return self.parser_api(args)

    def parse_storage(self, args: typing.Any) -> T:
        """
        Parses data coming from the database or file.
        """
        if self.parser_storage is None:
            self.parser_storage = build_parser(
                self.arguments,
                ParserOptions.Storage(
                    strict_property_parsing=self.strict_property_parsing,
                ),
            )
        assert self.parser_storage is not None
        return self.parser_storage(args)
