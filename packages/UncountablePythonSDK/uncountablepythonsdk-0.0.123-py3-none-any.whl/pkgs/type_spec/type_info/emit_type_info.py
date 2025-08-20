import copy
import dataclasses
import decimal
import io
import json
from enum import Enum
from typing import Any, cast

import yaml

from main.base.types import data_t, type_info_t
from main.base.types.base_t import PureJsonValue
from pkgs.argument_parser import CachedParser
from pkgs.serialization_util import serialize_for_api, serialize_for_storage

from .. import builder, util
from ..emit_typescript_util import MODIFY_NOTICE, ts_name
from ..value_spec import convert_to_value_spec_type

ext_info_parser = CachedParser(type_info_t.ExtInfo, strict_property_parsing=True)


def type_path_of(stype: builder.SpecType) -> object:  # NamePath
    """
    Returns a type path for a given type. The output syntax, below, is chosen for storage
    in JSON with relatively easy understanding, and hopefully forward compatible with
    extended scopes, generics, and enum literal values.
    - Scoped Type: [ (namespace-string)..., type-string ]
    - Instance Type: [ "$instance", Scoped-Type-Base, [TypePath-Parameters...] ]
    - Literal Type: [ "$literal", [ "$value", value, value-type-string ]... ]

    @return (string-specific, multiple-types)
    """
    if isinstance(stype, builder.SpecTypeDefn):
        if stype.is_base:  # assume correct namespace
            return [stype.name]
        return [stype.namespace.name, stype.name]

    if isinstance(stype, builder.SpecTypeInstance):
        if stype.defn_type.name == builder.BaseTypeName.s_literal:
            parts: list[object] = ["$literal"]
            for parameter in stype.parameters:
                assert isinstance(parameter, builder.SpecTypeLiteralWrapper)
                # This allows expansion to enum literal values later
                parts.append([
                    "$value",
                    parameter.value,
                    type_path_of(parameter.value_type),
                ])
            return parts

        return [
            # this allows the front-end to not have to know if something is a generic by name
            "$instance",
            type_path_of(stype.defn_type),
            [type_path_of(parameter) for parameter in stype.parameters],
        ]

    raise Exception("unhandled-SpecType")


def _dict_null_strip(data: dict[str, object]) -> dict[str, object]:
    """
    We know the output supports missing fields in place of nulls for the
    dictionary keys. This will not look inside lists ensuring any eventual
    complex data literals/constants will be preserved.
    This is strictly to compact the output, as there will be many nulls.
    """
    return {
        key: (_dict_null_strip(value) if isinstance(value, dict) else value)
        for key, value in data.items()
        if value is not None
    }


class JsonEncoder(json.JSONEncoder):
    """We have some defaults of special types that we need to emit"""

    def default(self, obj: object) -> object:
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def emit_type_info(build: builder.SpecBuilder, output: str) -> None:
    type_map = _build_map_all(build)

    # sort for stability, indent for smaller diffs
    stripped = _dict_null_strip(dataclasses.asdict(type_map))
    serial = json.dumps(stripped, sort_keys=True, indent=2, cls=JsonEncoder)
    type_map_out = io.StringIO()
    type_map_out.write(MODIFY_NOTICE)
    type_map_out.write(f"export const TYPE_MAP = {serial}")

    util.rewrite_file(f"{output}/type_map.ts", type_map_out.getvalue())


def _convert_value_for_yaml_dump(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    elif isinstance(value, list):
        return [_convert_value_for_yaml_dump(item) for item in value]
    elif isinstance(value, dict):
        return {k: _convert_value_for_yaml_dump(v) for k, v in value.items()}
    elif isinstance(value, decimal.Decimal):
        return str(value)
    else:
        return value


def asdict_for_yaml_dump(dataclass_instance: Any) -> Any:
    return {
        k: _convert_value_for_yaml_dump(v)
        for k, v in dataclasses.asdict(dataclass_instance).items()
    }


def emit_type_info_python(build: builder.SpecBuilder, output: str) -> None:
    type_map = _build_map_all(build, python=True)

    stripped = _dict_null_strip(asdict_for_yaml_dump(type_map))

    yaml_content = yaml.dump(stripped, default_flow_style=False, sort_keys=True)
    util.rewrite_file(f"{output}/type_map.yaml", yaml_content)


@dataclasses.dataclass
class MapProperty:
    api_name: str
    type_name: str
    label: str | None
    type_path: object
    extant: str
    ext_info: PureJsonValue | None
    desc: str | None
    # We don't have typing on defaults yet, relying on emitters to check it. Limit
    # use of this field, as it'll necessarily change when adding type info
    default: PureJsonValue


@dataclasses.dataclass
class MapTypeBase:
    type_name: str
    label: str | None
    desc: str | None
    ext_info: PureJsonValue | None


@dataclasses.dataclass
class MapTypeObject(MapTypeBase):
    base_type_path: object
    properties: dict[str, MapProperty]


@dataclasses.dataclass
class MapTypeAlias(MapTypeBase):
    alias_type_path: object
    discriminator: str | None


@dataclasses.dataclass
class MapStringEnum(MapTypeBase):
    values: dict[str, str]


MapType = MapTypeObject | MapTypeAlias | MapStringEnum


@dataclasses.dataclass
class MapNamespace:
    types: dict[str, MapType]


@dataclasses.dataclass
class MapAll:
    namespaces: dict[str, MapNamespace]


def _build_map_all(build: builder.SpecBuilder, *, python: bool = False) -> MapAll:
    map_all = MapAll(namespaces={})

    for namespace in build.namespaces.values():
        if not python and not namespace.emit_type_info:
            continue

        if python and not namespace.emit_type_info_python:
            continue

        map_namespace = MapNamespace(types={})
        map_all.namespaces[namespace.name] = map_namespace

        for type_ in namespace.types.values():
            map_type = _build_map_type(build, type_)
            if map_type is not None:
                map_namespace.types[type_.name] = map_type

    return map_all


@dataclasses.dataclass(kw_only=True)
class InheritablePropertyParts:
    """This uses only the "soft" information for now, things that aren't relevant
    to the language emitted types. There are some fields that should be inherited
    at that level, but that needs to be done in builder. When that is done, the
    "label" and "desc" could probably be removed from this list."""

    label: str | None = None
    desc: str | None = None
    ext_info: type_info_t.ExtInfo | None = None


def _extract_inheritable_property_parts(
    stype: builder.SpecTypeDefnObject,
    prop: builder.SpecProperty,
) -> InheritablePropertyParts:
    if not stype.is_base and isinstance(stype.base, builder.SpecTypeDefn):
        base_prop = (stype.base.properties or {}).get(prop.name)
        if base_prop is None:
            base_parts = InheritablePropertyParts()
        else:
            base_parts = _extract_inheritable_property_parts(stype.base, base_prop)
            # Layout should not be inherited, as it'd end up hiding properties in the derived type
            if base_parts.ext_info is not None:
                base_parts.ext_info.layout = None
    else:
        base_parts = InheritablePropertyParts()

    label = prop.label or base_parts.label
    desc = prop.desc or base_parts.desc
    local_ext_info = _parse_ext_info(prop.ext_info)
    if local_ext_info is None:
        ext_info = base_parts.ext_info
    elif base_parts.ext_info is None:
        ext_info = local_ext_info
    else:
        ext_info = dataclasses.replace(
            local_ext_info,
            **{
                field.name: getattr(base_parts.ext_info, field.name)
                for field in dataclasses.fields(type_info_t.ExtInfo)
                if getattr(base_parts.ext_info, field.name) is not None
            },
        )

    return InheritablePropertyParts(label=label, desc=desc, ext_info=ext_info)


ExtInfoLayout = dict[str, set[str]]
ALL_FIELDS_GROUP = "*all_fields"


def _extract_and_validate_layout(
    stype: builder.SpecTypeDefnObject,
    ext_info: type_info_t.ExtInfo,
    base_layout: ExtInfoLayout | None,
) -> ExtInfoLayout:
    """
    Produce a map of groups to fields, for validation.
    """
    if ext_info.layout is None:
        return {}
    assert stype.properties is not None

    all_fields_group: set[str] = set()
    layout: ExtInfoLayout = {ALL_FIELDS_GROUP: all_fields_group}

    for group in ext_info.layout.groups:
        fields = set(group.fields or [])
        for field in fields:
            assert field in stype.properties or field == DISCRIMINATOR_COMMON_NAME, (
                f"layout-refers-to-missing-field:{field}"
            )

        local_ref_name = None
        if group.ref_name is not None:
            assert base_layout is None or base_layout.get(group.ref_name) is None, (
                f"group-name-duplicate-in-base:{group.ref_name}"
            )
            local_ref_name = group.ref_name

        if group.extends:
            assert base_layout is not None, "missing-base-layout"
            base_group = base_layout.get(group.extends)
            assert base_group is not None, f"missing-base-group:{group.extends}"
            fields.update(base_group)
            local_ref_name = group.extends

        assert local_ref_name not in layout, f"duplicate-group:{local_ref_name}"
        if local_ref_name is not None:
            layout[local_ref_name] = fields
        all_fields_group.update(fields)

    for group_ref_name in base_layout or {}:
        assert group_ref_name in layout, f"missing-base-group:{group_ref_name}"

    for prop_ref_name in stype.properties:
        assert prop_ref_name in all_fields_group, (
            f"layout-missing-field:{prop_ref_name}"
        )

    return layout


def _pull_property_from_type_recursively(
    stype: builder.SpecTypeDefnObject,
    property_name: str,
) -> builder.SpecProperty | None:
    assert stype.properties is not None
    prop = stype.properties.get(property_name)
    if prop is not None:
        return prop

    if stype.base is None:
        return None

    return _pull_property_from_type_recursively(stype.base, property_name)


DISCRIMINATOR_COMMON_NAME = "type"


def _validate_type_ext_info(
    stype: builder.SpecTypeDefnObject,
) -> tuple[ExtInfoLayout | None, type_info_t.ExtInfo | None]:
    ext_info = _parse_ext_info(stype.ext_info)
    if ext_info is None:
        return None, None

    if ext_info.label_fields is not None:
        assert stype.properties is not None
        for name in ext_info.label_fields:
            if name == DISCRIMINATOR_COMMON_NAME:
                continue
            prop = _pull_property_from_type_recursively(stype, name)
            assert prop is not None, f"missing-label-field:{name}"

    if ext_info.actions is not None:
        assert stype.properties is not None
        for action in ext_info.actions:
            if action.property == DISCRIMINATOR_COMMON_NAME:
                continue
            prop = _pull_property_from_type_recursively(stype, action.property)
            assert prop is not None, f"missing-action-field:{action.property}"

    if not stype.is_base and isinstance(stype.base, builder.SpecTypeDefnObject):
        base_layout, _ = _validate_type_ext_info(stype.base)
    else:
        base_layout = None

    return _extract_and_validate_layout(stype, ext_info, base_layout), ext_info


def _build_map_type(
    build: builder.SpecBuilder, stype: builder.SpecTypeDefn
) -> MapType | None:
    # limited support for now
    if (
        isinstance(stype, builder.SpecTypeDefnObject)
        and len(stype.parameters) == 0
        and not stype.is_base
        and stype.base is not None
    ):
        _, ext_info = _validate_type_ext_info(stype)

        properties: dict[str, MapProperty] = {}
        map_type = MapTypeObject(
            type_name=stype.name,
            label=stype.label,
            properties=properties,
            desc=stype.desc,
            base_type_path=type_path_of(stype.base),
            ext_info=serialize_for_api(ext_info),  # type: ignore[arg-type]
        )

        if stype.properties is not None:
            for prop in stype.properties.values():
                parts = _extract_inheritable_property_parts(stype, prop)
                # Propertis can't have layouts
                assert parts.ext_info is None or parts.ext_info.layout is None
                map_property = MapProperty(
                    type_name=prop.name,
                    label=parts.label,
                    api_name=ts_name(prop.name, prop.name_case),
                    extant=prop.extant,
                    type_path=type_path_of(prop.spec_type),
                    ext_info=serialize_for_api(parts.ext_info),  # type: ignore[arg-type]
                    desc=parts.desc,
                    default=prop.default,
                )
                map_type.properties[prop.name] = map_property

        return map_type

    if isinstance(stype, builder.SpecTypeDefnAlias):
        return MapTypeAlias(
            type_name=stype.name,
            label=stype.label,
            desc=stype.desc,
            alias_type_path=type_path_of(stype.alias),
            ext_info=_convert_ext_info(stype.ext_info),
            discriminator=stype.discriminator,
        )

    if isinstance(stype, builder.SpecTypeDefnUnion):
        # Emit as a basic alias for now, as the front-end supports only those for now
        # IMPROVE: We should emit a proper union type and support that
        backing = stype.get_backing_type()
        return MapTypeAlias(
            type_name=stype.name,
            label=stype.label,
            desc=stype.desc,
            alias_type_path=type_path_of(backing),
            ext_info=_convert_ext_info(stype.ext_info),
            discriminator=stype.discriminator,
        )

    if isinstance(stype, builder.SpecTypeDefnStringEnum):
        return MapStringEnum(
            type_name=stype.name,
            label=stype.label,
            desc=stype.desc,
            ext_info=_convert_ext_info(stype.ext_info),
            # IMPROVE: We probably want the label here, but this requires a change
            # to the front-end type-info and form code to handle
            values={
                entry.value: (entry.label or entry.name)
                for entry in stype.values.values()
            },
        )

    return None


def _parse_ext_info(in_ext: Any) -> type_info_t.ExtInfo | None:
    if in_ext is None:
        return None
    assert isinstance(in_ext, dict)
    mod_ext = copy.deepcopy(in_ext)

    df = mod_ext.get("data_format")
    if df is not None:
        df_type = df.get("type")
        assert df_type is not None

        # Do some patch-ups before parsing to get better syntax on types
        if df_type == data_t.DataFormatType.VALUE_SPEC and "result_type" in df:
            result_type_path = util.parse_type_str(df["result_type"])
            converted = convert_to_value_spec_type(result_type_path)
            df["result_type"] = serialize_for_storage(converted)
            mod_ext["data_format"] = df

    if "open_api" in mod_ext:
        del mod_ext["open_api"]
    return ext_info_parser.parse_storage(mod_ext)


def _convert_ext_info(in_ext: Any) -> PureJsonValue | None:
    # we need to convert this to API storage since it'll be used as-is in the UI
    parsed = _parse_ext_info(in_ext)
    return cast(PureJsonValue, serialize_for_api(parsed))
