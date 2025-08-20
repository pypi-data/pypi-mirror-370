"""
The syntax tree as well as the parser to create it.
"""

from __future__ import annotations

import abc
import os
import re
from collections import defaultdict
from dataclasses import MISSING, dataclass
from enum import Enum, StrEnum, auto
from typing import Any, Self

from . import util
from .cross_output_links import CrossOutputPaths
from .non_discriminated_union_exceptions import NON_DISCRIMINATED_UNION_EXCEPTIONS
from .util import parse_type_str

RawDict = dict[Any, Any]
EndpointKey = str


class PathMapping(StrEnum):
    NO_MAPPING = "no_mapping"
    DEFAULT_MAPPING = "default_mapping"


@dataclass(kw_only=True)
class APIEndpointInfo:
    root_path: str
    path_mapping: PathMapping


class StabilityLevel(StrEnum):
    """These are currently used for open api,
    see: https://github.com/Tufin/oasdiff/blob/main/docs/STABILITY.md
    """

    draft = "draft"
    beta = "beta"
    stable = "stable"


class PropertyExtant(StrEnum):
    required = "required"
    optional = "optional"
    missing = "missing"


class PropertyConvertValue(StrEnum):
    # Base conversion on underlying types
    auto = "auto"
    # Always convert the value (Not needed yet, thus not supported)
    # convert = 'convert'
    # Do not convert the value
    no_convert = "no_convert"


@dataclass
class SpecProperty:
    name: str
    label: str | None
    spec_type: SpecType
    extant: PropertyExtant
    convert_value: PropertyConvertValue
    # Conversion of this property's name
    name_case: NameCase
    default: Any = None
    has_default: bool = False
    # Requires this value in parsing, even if it has a default
    parse_require: bool = False
    desc: str | None = None
    # Holds extra information that will be emitted along with type_info. The builder knows nothing
    # about the contents of this information.
    ext_info: Any = None
    explicit_default: bool = False


class NameCase(StrEnum):
    convert = "convert"
    preserve = "preserve"
    # Upper-case in JavaScript, convert otherwise. This is a compatibilty
    # setting.
    js_upper = "js_upper"


class BaseTypeName(StrEnum):
    """
    Base types that are supported.
    """

    # Simple types
    s_boolean = "Boolean"
    s_date = "Date"
    s_date_time = "DateTime"
    s_decimal = "Decimal"
    s_dict = "Dict"
    s_integer = "Integer"
    s_json_value = "JsonValue"
    s_list = "List"
    s_lossy_decimal = "LossyDecimal"
    # The explicit None type is useful in certain discriminating unions and aliases
    # None was chose over "null" as our primary input is YAML files where null
    # has special meaning
    s_none = "None"
    # IMPROVE: Remove OpaqueKey and provide a way to not
    # convert dictionary keys.
    s_opaque_key = "OpaqueKey"
    s_literal = "Literal"
    s_optional = "Optional"
    s_string = "String"
    s_tuple = "Tuple"
    s_readonly_array = "ReadonlyArray"
    s_union = "Union"

    # For a root class that defines properties
    s_object = "Object"


class DefnTypeName(StrEnum):
    # Type is a named alias of another type
    s_alias = "Alias"
    # Type is imported from an external source (opaque to type_spec)
    s_external = "External"
    # An enum based on strings
    s_string_enum = "StringEnum"
    # a particular literal value
    s_string_literal = "_StringLiteral"
    # A union of several other types
    s_union = "Union"


base_namespace_name = "base"


class SpecTypeForm(Enum):
    """Using word Form to avoid a SpecTypeType and related confusion"""

    instance = auto()
    defn = auto()


class SpecType(abc.ABC):
    name: str

    @abc.abstractmethod
    def is_value_converted(self) -> bool:
        """
        On to-JSON serialization should this value undergo standard name/value
        processing.
        """
        ...

    @abc.abstractmethod
    def is_value_to_string(self) -> bool:
        """
        On to-JSON conversion this type should be force converted to a string.
        Only makes sense for simple types like Decimal/int
        """
        ...

    @abc.abstractmethod
    def is_valid_parameter(self) -> bool:
        """
        Is this type allowed to be used as a parameter to a parametric type.
        Meant only to catch unsupported situations now.
        """
        ...

    @abc.abstractmethod
    def is_base_type(self, type_: BaseTypeName) -> bool:
        """
        Is this the provided base type.
        """
        ...

    @abc.abstractmethod
    def get_referenced_types(self) -> list[SpecType]:
        """
        Returns a list of directly referenced types.
        For indirectly reference types call this method recursively
        """
        ...


class SpecTypeInstance(SpecType):
    def __init__(
        self,
        defn_type: SpecTypeDefn,
        parameters: list[SpecType],
    ) -> None:
        self.defn_type = defn_type
        self.parameters = parameters
        for parameter in parameters:
            assert parameter.is_valid_parameter()

    def is_value_converted(self) -> bool:
        return self.defn_type.is_value_converted()

    def is_value_to_string(self) -> bool:
        return self.defn_type.is_value_to_string()

    def is_valid_parameter(self) -> bool:
        return self.defn_type.is_valid_parameter()

    def is_base_type(self, type_: BaseTypeName) -> bool:
        return False

    def get_referenced_types(self) -> list[SpecType]:
        defn_type: list[SpecType] = [self.defn_type]
        return defn_type + self.parameters


@dataclass(kw_only=True)
class SpecEndpointExample:
    summary: str
    description: str
    arguments: dict[str, object]
    data: dict[str, object]


@dataclass(kw_only=True)
class SpecGuide:
    ref_name: str
    title: str
    markdown_content: str
    html_content: str


@dataclass(kw_only=True, frozen=True)
class RootGuideKey:
    pass


@dataclass(kw_only=True, frozen=True)
class EndpointGuideKey:
    path: str


SpecGuideKey = RootGuideKey | EndpointGuideKey


class SpecTypeLiteralWrapper(SpecType):
    def __init__(
        self,
        value: util.LiteralTypeValue,
        value_type: SpecType,
    ) -> None:
        self.value = value
        self.value_type = value_type

    def is_value_converted(self) -> bool:
        return True

    def is_value_to_string(self) -> bool:
        return True

    def is_valid_parameter(self) -> bool:
        # this isn't always a valid parameter,
        # but it can't be constructed directly by a user
        # trust that the builder code only inserts it in the right place
        return True

    def is_base_type(self, type_: BaseTypeName) -> bool:
        return True

    def get_referenced_types(self) -> list[SpecType]:
        return [self.value_type]


def unwrap_literal_type(stype: SpecType) -> SpecTypeLiteralWrapper | None:
    if isinstance(stype, SpecTypeInstance) and stype.defn_type.is_base_type(
        BaseTypeName.s_literal
    ):
        param_0 = stype.parameters[0]
        assert isinstance(param_0, SpecTypeLiteralWrapper)
        return param_0

    return None


class SpecTypeDefn(SpecType):
    """
    Base for type definitions. Do not instantiate this directly, use a derived class.
    """

    def __init__(
        self,
        namespace: SpecNamespace,
        name: str,
        *,
        is_predefined: bool = False,
        _is_value_converted: bool = True,
        is_base: bool = False,
        is_exported: bool = True,
    ) -> None:
        self.namespace = namespace
        self.name = name
        self.label: str | None = None

        self.is_predefined = is_predefined
        self.name_case = NameCase.convert
        self.is_base = is_base
        self.is_exported = is_exported

        self._is_value_converted = _is_value_converted
        self._is_value_to_string = False
        self._is_valid_parameter = True
        self._is_dynamic_allowed = False
        self.ext_info: Any = None

    def is_value_converted(self) -> bool:
        return self._is_value_converted

    def is_value_to_string(self) -> bool:
        return self._is_value_to_string

    def is_valid_parameter(self) -> bool:
        return self._is_valid_parameter

    def is_dynamic_allowed(self) -> bool:
        return self._is_dynamic_allowed

    def is_base_type(self, type_: BaseTypeName) -> bool:
        return self.is_base and self.name == type_

    def can_process(self, builder: SpecBuilder, data: RawDict) -> bool:
        return True

    @abc.abstractmethod
    def process(self, builder: SpecBuilder, data: RawDict) -> None: ...

    def base_process(
        self, builder: SpecBuilder, data: RawDict, extra_names: list[str]
    ) -> None:
        util.check_fields(
            data,
            [
                "ext_info",
                "label",
                "is_dynamic_allowed",
            ]
            + extra_names,
        )

        self.ext_info = data.get("ext_info")
        self.label = data.get("label")

        is_dynamic_allowed = data.get("is_dynamic_allowed", False)
        assert isinstance(is_dynamic_allowed, bool)
        self._is_dynamic_allowed = is_dynamic_allowed

    def _process_property(
        self, builder: SpecBuilder, spec_name: str, data: RawDict
    ) -> SpecProperty:
        builder.push_where(spec_name)
        util.check_fields(
            data,
            [
                "convert_value",
                "default",
                "desc",
                "ext_info",
                "extant",
                "label",
                "name_case",
                "type",
            ],
        )
        try:
            extant_type = data.get("extant")
            if spec_name.endswith("?"):
                if extant_type is not None:
                    raise Exception("cannot specify extant with ?")
                extant = PropertyExtant.optional
                name = spec_name[:-1]
            else:
                extant = (
                    PropertyExtant.required
                    if extant_type is None
                    else PropertyExtant(extant_type)
                )
                name = spec_name

            property_name_case = self.name_case
            name_case_raw = data.get("name_case")
            if name_case_raw is not None:
                property_name_case = NameCase(name_case_raw)

            if property_name_case != NameCase.preserve:
                assert util.is_valid_property_name(name), (
                    f"{name} is not a valid property name"
                )

            data_type = data.get("type")
            builder.ensure(data_type is not None, "missing `type` entry")
            assert data_type is not None

            convert_value = PropertyConvertValue(data.get("convert_value", "auto"))

            ptype = builder.parse_type(self.namespace, data_type, scope=self)

            default_spec = data.get("default", MISSING)
            explicit_default = default_spec != MISSING
            if default_spec == MISSING:
                has_default = False
                default = None
            else:
                has_default = True
                # IMPROVE: check the type against the ptype
                default = default_spec
            if extant == PropertyExtant.missing and explicit_default:
                raise Exception(
                    f"cannot have extant missing and default for property {name}"
                )
            parse_require = False
            literal = unwrap_literal_type(ptype)
            if literal is not None:
                default = literal.value
                has_default = True
                parse_require = True

            ext_info = data.get("ext_info")
            label = data.get("label")

            return SpecProperty(
                name=name,
                label=label,
                extant=extant,
                spec_type=ptype,
                convert_value=convert_value,
                name_case=property_name_case,
                has_default=has_default,
                default=default,
                parse_require=parse_require,
                desc=data.get("desc", None),
                ext_info=ext_info,
                explicit_default=explicit_default,
            )
        finally:
            builder.pop_where()

    def __repr__(self) -> str:
        return f"<SpecType {self.name}>"

    def get_referenced_types(self) -> list[SpecType]:
        return []


class SpecTypeGenericParameter(SpecType):
    def __init__(
        self,
        spec_type_definition: SpecTypeDefnObject,
        name: str,
    ) -> None:
        self.spec_type_definition = spec_type_definition
        self.name = name

    def is_value_converted(self) -> bool:
        return True

    def is_value_to_string(self) -> bool:
        return True

    def is_valid_parameter(self) -> bool:
        return True

    def is_base_type(self, type_: BaseTypeName) -> bool:
        return True

    def get_referenced_types(self) -> list[SpecType]:
        return []


class SpecTypeDefnObject(SpecTypeDefn):
    base: SpecTypeDefnObject | None
    parameters: list[str]

    def __init__(
        self,
        namespace: SpecNamespace,
        name: str,
        *,
        parameters: list[str] | None = None,
        is_base: bool = False,
        is_predefined: bool = False,
        is_hashable: bool = False,
        _is_value_converted: bool = True,
    ) -> None:
        super().__init__(
            namespace,
            name,
            is_predefined=is_predefined,
            _is_value_converted=_is_value_converted,
            is_base=is_base,
            is_exported=not is_base,
        )
        self.parameters = parameters if parameters is not None else []
        self.is_hashable = is_hashable
        self.base = None
        self.properties: dict[str, SpecProperty] | None = None
        self._kw_only: bool = True
        self.desc: str | None = None

    def is_value_converted(self) -> bool:
        if self.base and not self.base.is_value_converted():
            return False
        return super().is_value_converted()

    def is_value_to_string(self) -> bool:
        if self.base and self.base.is_value_to_string():
            return True
        return super().is_value_to_string()

    def is_valid_parameter(self) -> bool:
        if self.base and not self.base.is_valid_parameter():
            return False
        return super().is_valid_parameter()

    def resolve_ultimate_base(self) -> SpecTypeDefnObject:
        if self.base is None:
            return self
        return self.base.resolve_ultimate_base()

    def process(self, builder: SpecBuilder, data: RawDict) -> None:
        super().base_process(
            builder,
            data,
            ["type", "desc", "properties", "name_case", "hashable", "kw_only"],
        )
        type_base = builder.parse_type(self.namespace, data["type"], scope=self)
        builder.ensure(
            isinstance(type_base, SpecTypeDefnObject),
            "unsupported base type: not an Object",
        )
        assert isinstance(type_base, SpecTypeDefnObject)
        self.base = type_base
        self.name_case = NameCase(data.get("name_case", "convert"))
        ultimate = self.base.resolve_ultimate_base()
        builder.ensure(ultimate.is_base, "unsupported base type: not a base")

        if ultimate.name != BaseTypeName.s_object:
            raise Exception("unsupported base type: unknown", self.base)

        props = data.get("properties")
        if props is not None:
            self.properties = {}
            for name, prop_data in data["properties"].items():
                prop = self._process_property(builder, name, prop_data)
                self.properties[prop.name] = prop

        hashable = data.get("hashable")
        if hashable is not None:
            assert isinstance(hashable, bool)
            self.is_hashable = hashable

        self._kw_only = data.get("kw_only", True)
        self.desc = data.get("desc", None)

    def is_kw_only(self) -> bool:
        return self._kw_only

    def get_referenced_types(self) -> list[SpecType]:
        prop_types: list[SpecType] = (
            [prop.spec_type for prop in self.properties.values()]
            if self.properties is not None
            else []
        )
        base_type: list[SpecType] = [self.base] if self.base is not None else []
        return base_type + prop_types

    def get_generics(self) -> list[str]:
        return self.parameters


class SpecTypeDefnAlias(SpecTypeDefn):
    alias: SpecType

    def __init__(
        self,
        namespace: SpecNamespace,
        name: str,
    ) -> None:
        super().__init__(
            namespace,
            name,
        )
        self.desc: str | None = None
        self.discriminator: str | None = None

    def process(self, builder: SpecBuilder, data: RawDict) -> None:
        super().base_process(builder, data, ["type", "desc", "alias", "discriminator"])
        self.alias = builder.parse_type(self.namespace, data["alias"])
        self.desc = data.get("desc", None)
        self.discriminator = data.get("discriminator", None)

    def get_referenced_types(self) -> list[SpecType]:
        return [self.alias]


class SpecTypeDefnUnion(SpecTypeDefn):
    def __init__(self, namespace: SpecNamespace, name: str) -> None:
        super().__init__(namespace, name)
        self.discriminator: str | None = None
        self.types: list[SpecType] = []
        self._alias_type: SpecType | None = None
        self.discriminator_map: dict[str, SpecType] | None = None
        self.desc: str | None = None

    def process(self, builder: SpecBuilder, data: RawDict) -> None:
        super().base_process(builder, data, ["type", "desc", "types", "discriminator"])

        self.desc = data.get("desc", None)
        self.discriminator = data.get("discriminator", None)

        for sub_type_str in data["types"]:
            sub_type = builder.parse_type(self.namespace, sub_type_str)
            self.types.append(sub_type)

        base_type = builder.namespaces[base_namespace_name].types[BaseTypeName.s_union]
        self._backing_type = SpecTypeInstance(base_type, self.types)

        if self.discriminator is not None:
            self.discriminator_map = {}
            for sub_type in self.types:
                builder.push_where(sub_type.name)
                assert isinstance(sub_type, SpecTypeDefnObject), (
                    "union-type-must-be-object"
                )
                assert sub_type.properties is not None
                discriminator_type = sub_type.properties.get(self.discriminator)
                assert discriminator_type is not None, (
                    f"missing-discriminator-field: {sub_type}"
                )
                prop_type = unwrap_literal_type(discriminator_type.spec_type)
                assert prop_type is not None
                assert prop_type.is_value_to_string()
                value_type = prop_type.value_type
                if isinstance(value_type, SpecTypeDefnStringEnum):
                    assert isinstance(prop_type.value, str)
                    discriminant = value_type.values[prop_type.value].value
                else:
                    discriminant = str(prop_type.value)
                assert discriminant not in self.discriminator_map, (
                    f"duplicated-discriminant, {discriminant} in {sub_type}"
                )
                self.discriminator_map[discriminant] = sub_type

                builder.pop_where()
        elif (
            f"{self.namespace.name}.{self.name}"
            not in NON_DISCRIMINATED_UNION_EXCEPTIONS
        ):
            raise Exception(f"union requires a discriminator: {self.name}")

    def get_referenced_types(self) -> list[SpecType]:
        return self.types

    def get_backing_type(self) -> SpecType:
        assert self._backing_type is not None
        return self._backing_type


class SpecTypeDefnExternal(SpecTypeDefn):
    external_map: dict[str, str]

    def __init__(
        self,
        namespace: SpecNamespace,
        name: str,
    ) -> None:
        super().__init__(
            namespace,
            name,
            # Usually meant for internal use to the file
            is_exported=False,
        )

    def process(self, builder: SpecBuilder, data: RawDict) -> None:
        # IMPROVE: Add a test of external, since our only use case was
        # removed and it's uncertain that externals still work
        super().base_process(builder, data, ["type", "import"])
        self.external_map = data["import"]

    def get_referenced_types(self) -> list[SpecType]:
        return []


@dataclass(kw_only=True)
class StringEnumEntry:
    name: str
    value: str
    label: str | None = None
    deprecated: bool = False


class SpecTypeDefnStringEnum(SpecTypeDefn):
    def __init__(
        self,
        namespace: SpecNamespace,
        name: str,
    ) -> None:
        super().__init__(
            namespace,
            name,
        )
        self.values: dict[str, StringEnumEntry] = {}
        self.desc: str | None = None
        self.sql_type_name: str | None = None
        self.emit_id_source = False
        self.source_enums: list[SpecType] = []

    def can_process(self, builder: SpecBuilder, data: dict[Any, Any]) -> bool:
        source_enums = data.get("source_enums")
        try:
            for sub_type_str in source_enums or []:
                sub_type = builder.parse_type(self.namespace, sub_type_str)
                assert isinstance(sub_type, SpecTypeDefnStringEnum)
                assert len(sub_type.values) > 0
        except AssertionError:
            return False
        return super().can_process(builder, data)

    def process(self, builder: SpecBuilder, data: RawDict) -> None:
        super().base_process(
            builder,
            data,
            ["type", "desc", "values", "name_case", "sql", "emit", "source_enums"],
        )
        self.name_case = NameCase(data.get("name_case", "convert"))
        self.values = {}
        data_values = data.get("values")
        self.desc = data.get("desc", None)
        source_enums = data.get("source_enums", None)
        if isinstance(data_values, dict):
            for name, value in data_values.items():
                builder.push_where(name)
                if isinstance(value, str):
                    self.values[name] = StringEnumEntry(name=name, value=value)
                elif isinstance(value, dict):
                    util.check_fields(value, ["value", "desc", "label", "deprecated"])

                    enum_value = value.get("value", name)
                    builder.ensure(
                        isinstance(enum_value, str), "enum value should be string"
                    )
                    assert isinstance(enum_value, str)

                    deprecated = value.get("deprecated", False)
                    builder.ensure(
                        isinstance(deprecated, bool),
                        "deprecated value should be a bool",
                    )

                    label = value.get("label")
                    builder.ensure(
                        label is None or isinstance(label, str),
                        "label should be a string",
                    )

                    self.values[name] = StringEnumEntry(
                        name=name,
                        value=enum_value,
                        label=label,
                        deprecated=deprecated,
                    )
                else:
                    raise Exception(f"unsupported-value-type:{name}:{value}")
                builder.pop_where()

        elif isinstance(data_values, list):
            for value in data_values:
                if value in self.values:
                    raise Exception(
                        "duplicate value in typespec enum", self.name, value
                    )
                self.values[value] = StringEnumEntry(name=value, value=value)
        else:
            if source_enums is None or data_values is not None:
                raise Exception("unsupported values type")

        sql_data = data.get("sql")
        if sql_data is not None:
            util.check_fields(sql_data, ["type_name"])
            self.sql_type_name = sql_data.get("type_name")

        emit_data = data.get("emit")
        if emit_data is not None:
            util.check_fields(emit_data, ["id_source"])
            emit_id_source = emit_data.get("id_source", False)
            assert isinstance(emit_id_source, bool)
            self.emit_id_source = emit_id_source
            if emit_id_source:
                builder.emit_id_source_enums.add(self)

        if self.emit_id_source:
            assert len(self.namespace.path) == 1
            for entry in self.values.values():
                builder.ensure(
                    entry.label is not None, f"need-label-for-id-source:{entry.name}"
                )
        for sub_type_str in source_enums or []:
            sub_type = builder.parse_type(self.namespace, sub_type_str)
            self.source_enums.append(sub_type)

        for sub_type in self.source_enums:
            builder.push_where(sub_type.name)
            if isinstance(sub_type, SpecTypeDefnStringEnum):
                self.values.update(sub_type.values)
            builder.pop_where()

    def get_referenced_types(self) -> list[SpecType]:
        return self.source_enums


TOKEN_ENDPOINT = "$endpoint"
TOKEN_EMIT_IO_TS = "$emit_io_ts"
TOKEN_EMIT_TYPE_INFO = "$emit_type_info"
TOKEN_EMIT_TYPE_INFO_PYTHON = "$emit_type_info_python"
# The import token is only for explicit ordering of the files, to process constants
# and enums correctly. It does not impact the final generation of files, or the
# language imports. Those are still auto-resolved.
TOKEN_IMPORT = "$import"


class RouteMethod(StrEnum):
    post = "post"
    get = "get"
    delete = "delete"
    patch = "patch"
    put = "put"


class ResultType(StrEnum):
    json = "json"
    binary = "binary"


RE_ENDPOINT_ROOT = re.compile(r"\${([_a-z]+)}")


@dataclass(kw_only=True, frozen=True)
class _EndpointPathDetails:
    root: EndpointKey
    root_path: str
    resolved_path: str


def _resolve_endpoint_path(
    path: str, api_endpoints: dict[EndpointKey, APIEndpointInfo]
) -> _EndpointPathDetails:
    root_path_source = path.split("/")[0]
    root_match = RE_ENDPOINT_ROOT.fullmatch(root_path_source)
    if root_match is None:
        raise Exception(f"invalid-api-path-root:{root_path_source}")

    root_var = root_match.group(1)
    root_path = api_endpoints[root_var].root_path

    _, *rest_path = path.split("/", 1)
    resolved_path = "/".join([root_path] + rest_path)

    return _EndpointPathDetails(
        root=root_var, root_path=root_path, resolved_path=resolved_path
    )


class EndpointEmitType(StrEnum):
    EMIT_ENDPOINT = "emit_endpoint"
    EMIT_TYPES = "emit_types"
    EMIT_NOTHING = "emit_nothing"


@dataclass(kw_only=True, frozen=True)
class EndpointSpecificPath:
    root: EndpointKey
    path_root: str
    path_dirname: str
    path_basename: str
    function: str | None


def parse_endpoint_specific_path(
    builder: SpecBuilder,
    data_per_endpoint: RawDict | None,
) -> EndpointSpecificPath | None:
    if data_per_endpoint is None:
        return None
    util.check_fields(
        data_per_endpoint,
        [
            "path",
            "function",
        ],
    )

    if "path" not in data_per_endpoint or data_per_endpoint["path"] is None:
        return None

    path = data_per_endpoint["path"].split("/")

    assert len(path) > 1, "invalid-endpoint-path"

    path_details = _resolve_endpoint_path(
        data_per_endpoint["path"], builder.api_endpoints
    )

    result = EndpointSpecificPath(
        function=data_per_endpoint.get("function"),
        path_dirname="/".join(path[1:-1]),
        path_basename=path[-1],
        root=path_details.root,
        path_root=path_details.root_path,
    )

    return result


class SpecEndpoint:
    method: RouteMethod
    data_loader: bool
    is_sdk: EndpointEmitType
    stability_level: StabilityLevel | None
    # Don't emit TypeScript endpoint code
    suppress_ts: bool
    deprecated: bool = False
    async_batch_path: str | None = None
    result_type: ResultType = ResultType.json
    has_attachment: bool = False
    desc: str | None = None
    account_type: str | None
    route_group: str | None

    # function, path details per api endpoint
    path_per_api_endpoint: dict[str, EndpointSpecificPath]
    default_endpoint_key: EndpointKey

    is_external: bool = False

    def __init__(self) -> None:
        pass

    def process(self, builder: SpecBuilder, data: RawDict) -> None:
        util.check_fields(
            data,
            [
                "method",
                "path",
                "data_loader",
                "deprecated",
                "is_sdk",
                "stability_level",
                "async_batch_path",
                "function",
                "suppress_ts",
                "desc",
                "deprecated",
                "result_type",
                "has_attachment",
                "account_type",
                "route_group",
            ]
            + list(builder.api_endpoints.keys()),
        )
        self.method = RouteMethod(data["method"])

        data_loader = data.get("data_loader", False)
        assert isinstance(data_loader, bool)
        self.data_loader = data_loader
        self.deprecated = data.get("deprecated", False)

        is_sdk = data.get("is_sdk", EndpointEmitType.EMIT_NOTHING)

        # backwards compatibility
        if isinstance(is_sdk, bool):
            if is_sdk is True:
                is_sdk = EndpointEmitType.EMIT_ENDPOINT
            else:
                is_sdk = EndpointEmitType.EMIT_NOTHING
        elif isinstance(is_sdk, str):
            try:
                is_sdk = EndpointEmitType(is_sdk)
            except ValueError as e:
                raise ValueError(f"Invalid value for is_sdk: {is_sdk}") from e

        assert isinstance(is_sdk, EndpointEmitType)

        self.is_sdk = is_sdk

        route_group = data.get("route_group")
        assert route_group is None or isinstance(route_group, str)
        self.route_group = route_group

        account_type = data.get("account_type")
        assert account_type is None or isinstance(account_type, str)
        self.account_type = account_type

        stability_level_raw = data.get("stability_level")
        assert stability_level_raw is None or isinstance(stability_level_raw, str)
        self.stability_level = (
            StabilityLevel(stability_level_raw)
            if stability_level_raw is not None
            else None
        )

        async_batch_path = data.get("async_batch_path")
        if async_batch_path is not None:
            assert isinstance(async_batch_path, str)
            self.async_batch_path = async_batch_path

        suppress_ts = data.get("suppress_ts", False)
        assert isinstance(suppress_ts, bool)
        self.suppress_ts = suppress_ts

        self.result_type = ResultType(data.get("result_type", ResultType.json.value))
        self.has_attachment = data.get("has_attachment", False)
        self.desc = data.get("desc")

        # compatibility with single-endpoint files
        default_endpoint_path = parse_endpoint_specific_path(
            builder,
            {"path": data.get("path"), "function": data.get("function")},
        )
        if default_endpoint_path is not None:
            assert default_endpoint_path.root in builder.api_endpoints, (
                "Default endpoint is not a valid API endpoint"
            )
            self.default_endpoint_key = default_endpoint_path.root
            self.path_per_api_endpoint = {
                self.default_endpoint_key: default_endpoint_path,
            }
        else:
            self.path_per_api_endpoint = {}
            shared_function_name = None
            for endpoint_key in builder.api_endpoints:
                endpoint_specific_path = parse_endpoint_specific_path(
                    builder,
                    data.get(endpoint_key),
                )
                if endpoint_specific_path is not None:
                    self.path_per_api_endpoint[endpoint_key] = endpoint_specific_path
                    if endpoint_specific_path.function is not None:
                        fn_name = endpoint_specific_path.function.split(".")[-1]
                        if shared_function_name is None:
                            shared_function_name = fn_name
                        assert shared_function_name == fn_name

            if builder.top_namespace in self.path_per_api_endpoint:
                self.default_endpoint_key = builder.top_namespace
            elif len(self.path_per_api_endpoint) == 1:
                self.default_endpoint_key = next(
                    iter(self.path_per_api_endpoint.keys())
                )
            else:
                raise RuntimeError("no clear default endpoint")

        assert len(self.path_per_api_endpoint) > 0, (
            "Missing API endpoint path and function definitions for API call"
        )

        # IMPROVE: remove need for is_external flag
        self.is_external = (
            self.path_per_api_endpoint[self.default_endpoint_key].path_root
            == "api/external"
        )

        assert self.is_sdk != EndpointEmitType.EMIT_ENDPOINT or self.desc is not None, (
            f"Endpoint description required for SDK endpoints, missing: {self.resolved_path}"
        )

    @property
    def resolved_path(self: Self) -> str:
        default_endpoint_path = self.path_per_api_endpoint[self.default_endpoint_key]
        return f"{default_endpoint_path.path_root}/{default_endpoint_path.path_dirname}/{default_endpoint_path.path_basename}"


def _parse_const(
    builder: SpecBuilder,
    namespace: SpecNamespace,
    const_type: SpecType,
    value: object,
) -> object:
    if isinstance(const_type, SpecTypeInstance):
        if const_type.defn_type.name == BaseTypeName.s_list:
            assert isinstance(value, list)
            builder.ensure(
                len(const_type.parameters) == 1,
                "constant-list-expects-one-type",
            )
            param_type = const_type.parameters[0]
            builder.ensure(isinstance(value, list), "constant-list-is-list")
            return [_parse_const(builder, namespace, param_type, x) for x in value]

        elif const_type.defn_type.name == BaseTypeName.s_dict:
            assert isinstance(value, dict)
            builder.ensure(
                len(const_type.parameters) == 2, "constant-dict-expects-one-type"
            )
            key_type = const_type.parameters[0]
            value_type = const_type.parameters[1]
            builder.ensure(isinstance(value, dict), "constant-dict-is-dict")
            return {
                _parse_const(builder, namespace, key_type, dict_key): _parse_const(
                    builder, namespace, value_type, dict_value
                )
                for dict_key, dict_value in value.items()
            }

        elif const_type.defn_type.name == BaseTypeName.s_optional:
            builder.ensure(
                len(const_type.parameters) == 1, "constant-optional-expects-one-type"
            )
            if value is None:
                return None
            return _parse_const(builder, namespace, const_type.parameters[0], value)

        else:
            raise Exception("unsupported-constant-collection-type")

    if isinstance(const_type, SpecTypeDefnStringEnum):
        assert isinstance(value, str)
        *parsed_type, parsed_value = util.parse_type_str(value)
        lookup_type = builder._convert_parsed_type(parsed_type, namespace, top=True)
        assert lookup_type == const_type
        builder.ensure(
            parsed_value.name in const_type.values,
            f"{parsed_value.name}:not-found-in:{parsed_type}",
        )
        return parsed_value.name

    if isinstance(const_type, SpecTypeDefnObject):
        if const_type.name == BaseTypeName.s_string:
            builder.ensure(isinstance(value, str), "invalid value for string constant")
            return str(value)

        if const_type.name == BaseTypeName.s_integer:
            builder.ensure(isinstance(value, int), "invalid value for integer constant")
            return value

        if const_type.name == BaseTypeName.s_boolean:
            builder.ensure(
                isinstance(value, bool), "invalid value for boolean constant"
            )
            return value

    raise Exception("unsupported-const-scalar-type", const_type)


class SpecConstant:
    value: object = None
    value_type: SpecType
    desc: str | None = None

    def __init__(self, namespace: SpecNamespace, name: str):
        self.name = name
        self.namespace = namespace

    def process(self, builder: SpecBuilder, data: RawDict) -> None:
        util.check_fields(data, ["type", "value", "desc", "complete"])
        self.value_type = builder.parse_type(self.namespace, data["type"])
        value = data["value"]

        self.desc = data.get("desc", None)
        self.value = _parse_const(builder, self.namespace, self.value_type, value)

        complete = data.get("complete", False)
        assert isinstance(complete, bool)
        if complete:
            assert isinstance(self.value_type, SpecTypeInstance)
            key_type = self.value_type.parameters[0]
            assert isinstance(key_type, SpecTypeDefnStringEnum)
            assert isinstance(self.value, dict)
            # the parsing checks that the values are correct, so a simple length check
            # should be enough to check completeness
            builder.ensure(
                len(key_type.values) == len(self.value), "incomplete-enum-map"
            )


class SpecNamespace:
    def __init__(
        self,
        name: str,
    ):
        self.types: dict[str, SpecTypeDefn] = {}
        self.constants: dict[str, SpecConstant] = {}
        self.endpoint: SpecEndpoint | None = None
        self.emit_io_ts = False
        self.emit_type_info = False
        self.emit_type_info_python = False
        self.derive_types_from_io_ts = False
        self._imports: list[str] | None = None
        self.path = name.split(".")
        self.name = self.path[-1]
        self._order: int | None = None

    def _update_order(self, builder: SpecBuilder, recurse: int = 0) -> int:
        if self._order is not None:
            return self._order

        # simple stop to infinite loops
        assert recurse < 50

        # subdirectories get included later, this forces them to have a higher value
        # but doesn't preclude importing in those directories
        order = len(self.path) * 100
        for import_name in self._imports or []:
            # assume simple single names for now
            ns = builder.namespaces[import_name]
            ns_order = ns._update_order(builder, recurse + 1)
            order = max(ns_order + 1, order)

        self._order = order
        return order

    def _sort_key(self) -> tuple[int, str]:
        return self._order or 0, self.name

    def prescan(self, data: RawDict) -> None:
        """
        Create placeholders for all types. This allows types to be defined in
        any order and refer to types later in the file. This is also the reason
        why all the Spec classes are only partially defined at construction.
        """
        for full_name, defn in data.items():
            parsed_name = parse_type_str(full_name)[0]
            name = parsed_name.name

            if name == TOKEN_ENDPOINT:
                assert self.endpoint is None
                self.endpoint = SpecEndpoint()
                continue

            if name == TOKEN_EMIT_IO_TS:
                assert defn in (True, False)
                self.emit_io_ts = defn
                self.derive_types_from_io_ts = defn
                continue

            if name == TOKEN_EMIT_TYPE_INFO:
                assert defn in (True, False)
                self.emit_type_info = defn
                continue

            if name == TOKEN_EMIT_TYPE_INFO_PYTHON:
                assert defn in (True, False)
                self.emit_type_info_python = defn
                continue

            if name == TOKEN_IMPORT:
                assert self._imports is None
                imports = [defn] if isinstance(defn, str) else defn
                assert isinstance(imports, list)
                self._imports = imports
                continue

            if "value" in defn:
                assert util.is_valid_property_name(name), (
                    f"{name} is not a valid constant name"
                )
                spec_constant = SpecConstant(self, name)
                self.constants[name] = spec_constant
                continue

            assert util.is_valid_type_name(name), f"{name} is not a valid type name"
            assert name not in self.types, f"{name} is duplicate"
            defn_type = defn["type"]
            spec_type: SpecTypeDefn
            if defn_type == DefnTypeName.s_alias:
                spec_type = SpecTypeDefnAlias(self, name)
            elif defn_type == DefnTypeName.s_union:
                spec_type = SpecTypeDefnUnion(self, name)
            elif defn_type == DefnTypeName.s_external:
                spec_type = SpecTypeDefnExternal(self, name)
            elif defn_type == DefnTypeName.s_string_enum:
                spec_type = SpecTypeDefnStringEnum(self, name)
            else:
                parameters = (
                    [
                        parameter.name
                        for name_parameters in parsed_name.parameters
                        for parameter in name_parameters
                    ]
                    if parsed_name.parameters is not None
                    else None
                )
                spec_type = SpecTypeDefnObject(
                    self,
                    name,
                    parameters=parameters,
                )
            self.types[name] = spec_type

    def process(self, builder: SpecBuilder, data: RawDict) -> None:
        """
        Complete the definition of each type.
        """
        builder.push_where(self.name)
        items_to_process: list[NameDataPair] = [
            NameDataPair(full_name=full_name, data=defn)
            for full_name, defn in data.items()
        ]
        while len(items_to_process) > 0:
            deferred_items: list[NameDataPair] = []
            for item in items_to_process:
                full_name = item.full_name
                defn = item.data
                parsed_name = parse_type_str(full_name)[0]
                name = parsed_name.name

                if name in [
                    TOKEN_EMIT_IO_TS,
                    TOKEN_EMIT_TYPE_INFO,
                    TOKEN_IMPORT,
                    TOKEN_EMIT_TYPE_INFO_PYTHON,
                ]:
                    continue

                builder.push_where(name)

                if "value" in defn:
                    spec_constant = self.constants[name]
                    spec_constant.process(builder, defn)

                elif name == TOKEN_ENDPOINT:
                    assert self.endpoint
                    self.endpoint.process(builder, defn)

                else:
                    spec_type = self.types[name]
                    if spec_type.can_process(builder, defn):
                        spec_type.process(builder, defn)
                    else:
                        deferred_items.append(item)

                builder.pop_where()
            assert len(deferred_items) < len(items_to_process)
            items_to_process = [deferred for deferred in deferred_items]

        builder.pop_where()


class BuilderException(Exception):
    pass


@dataclass(kw_only=True)
class NamespaceDataPair:
    namespace: SpecNamespace
    data: RawDict


@dataclass(kw_only=True)
class NameDataPair:
    full_name: str
    data: RawDict


class SpecBuilder:
    def __init__(
        self,
        *,
        api_endpoints: dict[EndpointKey, APIEndpointInfo],
        top_namespace: str,
        cross_output_paths: CrossOutputPaths | None,
    ) -> None:
        self.top_namespace = top_namespace
        self.where: list[str] = []
        self.namespaces = {}
        self.pending: list[NamespaceDataPair] = []
        self.parts: dict[str, dict[str, str]] = defaultdict(dict)
        self.preparts: dict[str, dict[str, str]] = defaultdict(dict)
        self.examples: dict[str, list[SpecEndpointExample]] = defaultdict(list)
        self.guides: dict[SpecGuideKey, list[SpecGuide]] = defaultdict(list)
        self.api_endpoints = api_endpoints
        self.cross_output_paths = cross_output_paths
        base_namespace = SpecNamespace(name=base_namespace_name)
        for base_type in BaseTypeName:
            defn = SpecTypeDefnObject(base_namespace, base_type, is_base=True)
            # Hacky approach, but still simpler than a table of all core type defns
            if base_type == BaseTypeName.s_decimal:
                defn._is_value_to_string = True
                # Not allowed now as we cannot serialization this correctly at the
                # moment. Only a problem for built-in parametrics, but we
                # don't support custom parametrics yet, so the distinction isn't needed
                defn._is_valid_parameter = False
            base_namespace.types[base_type] = defn

        self.namespaces[base_namespace_name] = base_namespace

        self.emit_id_source_enums: set[SpecTypeDefnStringEnum] = set()

        this_dir = os.path.dirname(os.path.realpath(__file__))
        with open(f"{this_dir}/parts/base.py.prepart") as py_base_part:
            self.preparts["python"][base_namespace_name] = py_base_part.read()
        with open(f"{this_dir}/parts/base.ts.prepart") as ts_base_part:
            self.preparts["typescript"][base_namespace_name] = ts_base_part.read()

        base_namespace.types["ObjectId"] = SpecTypeDefnObject(
            base_namespace,
            "ObjectId",
            is_predefined=True,
        )
        base_namespace.types["JsonValue"] = SpecTypeDefnObject(
            base_namespace,
            "JsonValue",
            is_predefined=True,
            _is_value_converted=False,
        )
        base_namespace.types["JsonScalar"] = SpecTypeDefnObject(
            base_namespace,
            "JsonScalar",
            is_predefined=True,
        )

    def push_where(self, msg: str) -> None:
        self.where.append(msg)

    def pop_where(self) -> None:
        self.where.pop()

    def ensure(self, condition: bool, msg: str) -> None:
        if not condition:
            print(self.where)
            print(msg)
            raise BuilderException()

    def prescan(self, namespace_path: str, data: RawDict) -> None:
        assert namespace_path not in self.namespaces
        namespace = SpecNamespace(namespace_path)
        namespace.prescan(data)
        self.namespaces[namespace_path] = namespace
        self.pending.append(NamespaceDataPair(namespace=namespace, data=data))

    def process(self) -> bool:
        self.where = []
        try:
            for item in self.pending:
                item.namespace._update_order(self)

            # Use a consistent sorting order to ensure stable builds
            sorted_pending = sorted(self.pending, key=lambda x: x.namespace._sort_key())
            for item in sorted_pending:
                item.namespace.process(self, item.data)
        except BuilderException:
            return False
        except Exception:
            print(self.where)
            raise

        return True

    def get_type_of_literal(self, value: util.LiteralTypeValue) -> SpecType:
        if isinstance(value, str):
            return self.namespaces[base_namespace_name].types[BaseTypeName.s_string]
        if isinstance(value, bool):
            return self.namespaces[base_namespace_name].types[BaseTypeName.s_boolean]

        raise BuilderException("invalid-literal", value)

    def _convert_parsed_type(
        self,
        path: util.ParsedTypePath,
        namespace: SpecNamespace,
        scope: SpecTypeDefn | None = None,
        top: bool = False,
    ) -> SpecType:
        """
        WARNING: support is limited to what is used right now, in particular
        with regards to parametric types and literals
        """
        assert len(path) > 0
        # Consider namespaces only if in top, as we don't support a hierarchy of namespaces yet
        if top:
            sub_namespace = self.namespaces.get(path[0].name)
            if sub_namespace is not None:
                return self._convert_parsed_type(path[1:], sub_namespace, scope=scope)

        literal_value: util.LiteralTypeValue
        if path[0].name == DefnTypeName.s_string_literal:
            assert path[0].literal_value is not None
            assert len(path) == 1, path
            literal_value = path[0].literal_value
            assert literal_value is not None
            return SpecTypeLiteralWrapper(
                value=literal_value,
                value_type=self.get_type_of_literal(literal_value),
            )
        if path[0].name in ("true", "false"):
            assert path[0].name is not None
            assert len(path) == 1, path
            literal_value = {"true": True, "false": False}[path[0].name]

            return SpecTypeLiteralWrapper(
                value=literal_value,
                value_type=self.get_type_of_literal(literal_value),
            )

        # Always resolve in base namespace first, making those types essentially reserved words
        defn_type = self.namespaces[base_namespace_name].types.get(path[0].name)

        if defn_type is None:
            defn_type = namespace.types.get(path[0].name)

        if (
            defn_type is None
            and scope is not None
            and isinstance(scope, SpecTypeDefnObject)
        ):
            if path[0].name in (scope.parameters or []):
                return SpecTypeGenericParameter(
                    spec_type_definition=scope,
                    name=path[0].name,
                )

        self.ensure(defn_type is not None, f"unknown-type: {path[0].name} in {path}")
        assert defn_type is not None

        # We might be resolving to a literal enum value
        if len(path) == 2:
            if isinstance(defn_type, SpecTypeDefnStringEnum):
                assert path[1].parameters is None
                statement = f"$import: [{defn_type.namespace.name}]"
                self.ensure(
                    path[1].name in defn_type.values,
                    f"missing-enum-value: {path} have you specified the dependency in an import statement: {statement}",
                )
                return SpecTypeLiteralWrapper(
                    value=path[1].name,
                    value_type=defn_type,
                )
            else:
                self.ensure(False, f"unknown-type-path-resolution: {path}")

        assert len(path) == 1, path
        if path[0].parameters is None:
            return defn_type

        return SpecTypeInstance(
            defn_type,
            [
                self._convert_parsed_type(p, namespace, top=True, scope=scope)
                for p in path[0].parameters
            ],
        )

    def parse_type(
        self, namespace: SpecNamespace, spec: str, scope: SpecTypeDefn | None = None
    ) -> SpecType:
        self.push_where(spec)
        parsed_type = util.parse_type_str(spec)
        result = self._convert_parsed_type(
            parsed_type, namespace, top=True, scope=scope
        )
        self.pop_where()
        return result

    def add_part_file(self, target: str, name: str, data: str) -> None:
        self.parts[target][name] = data

    def add_prepart_file(self, target: str, name: str, data: str) -> None:
        self.preparts[target][name] = data

    def add_example_file(self, data: dict[str, object]) -> None:
        path_details = _resolve_endpoint_path(str(data["path"]), self.api_endpoints)

        examples_data = data["examples"]
        if not isinstance(examples_data, list):
            raise Exception(
                f"'examples' in example files are expected to be a list, endpoint_path={path_details.resolved_path}"
            )
        for example in examples_data:
            arguments = example["arguments"]
            data_example = example["data"]
            if not isinstance(arguments, dict) or not isinstance(data_example, dict):
                raise Exception(
                    f"'arguments' and 'data' fields must be dictionaries for each endpoint example, endpoint={path_details.resolved_path}"
                )
            self.examples[path_details.resolved_path].append(
                SpecEndpointExample(
                    summary=str(example["summary"]),
                    description=str(example["description"]),
                    arguments=arguments,
                    data=data_example,
                )
            )

    def add_guide_file(self, file_content: str) -> None:
        import markdown

        md = markdown.Markdown(extensions=["meta"])
        html = md.convert(file_content)
        meta: dict[str, list[str]] = md.Meta  # type: ignore[attr-defined]
        title_meta: list[str] | None = meta.get("title")
        if title_meta is None:
            raise Exception("guides require a title in the meta section")
        id_meta: list[str] | None = meta.get("id")
        if id_meta is None:
            raise Exception("guides require an id in the meta section")

        path_meta: list[str] | None = meta.get("path")
        guide_key: SpecGuideKey = RootGuideKey()
        if path_meta is not None:
            path_details = _resolve_endpoint_path(
                "".join(path_meta), self.api_endpoints
            )
            guide_key = EndpointGuideKey(path=path_details.resolved_path)

        self.guides[guide_key].append(
            SpecGuide(
                ref_name="".join(id_meta),
                title="".join(title_meta),
                html_content=html,
                markdown_content=file_content,
            )
        )

    def resolve_proper_name(self, stype: SpecTypeDefn) -> str:
        return f"{'.'.join(stype.namespace.path)}.{stype.name}"
