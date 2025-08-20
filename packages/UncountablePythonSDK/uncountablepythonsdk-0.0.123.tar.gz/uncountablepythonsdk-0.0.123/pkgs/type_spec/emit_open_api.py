"""
Generates an OpenAPI specification based on the type_spec definitions

WORK-IN-PROGRESS, DON'T USE!
"""

import dataclasses
import json
import re
from enum import StrEnum
from typing import Collection, assert_never, cast

from pkgs.serialization import yaml
from pkgs.serialization_util import serialize_for_api

from . import builder, util
from .builder import EndpointGuideKey, RootGuideKey
from .config import OpenAPIConfig
from .emit_open_api_util import (
    MODIFY_NOTICE,
    EmitOpenAPIContext,
    EmitOpenAPIEndpoint,
    EmitOpenAPIEndpointExample,
    EmitOpenAPIGlobalContext,
    EmitOpenAPIGuide,
    EmitOpenAPIPath,
    EmitOpenAPIServer,
    EmitOpenAPIStabilityLevel,
    EmitOpenAPITag,
    GlobalContextInfo,
    TagGroupToNamedTags,
    TagPathsToRef,
    resolve_namespace_ref,
)
from .emit_typescript_util import ts_name
from .open_api_util import (
    OpenAPIArrayType,
    OpenAPIBooleanT,
    OpenAPIEmptyType,
    OpenAPIEnumType,
    OpenAPIFreeFormObjectType,
    OpenAPIIntegerT,
    OpenAPIIntersectionType,
    OpenAPINumberT,
    OpenAPIObjectType,
    OpenAPIRefType,
    OpenAPIStringT,
    OpenAPIType,
    OpenAPIUnionType,
)

base_name_map = {
    builder.BaseTypeName.s_boolean: OpenAPIBooleanT,
    builder.BaseTypeName.s_date: OpenAPIStringT,  # IMPROVE: Aliased DateStr
    builder.BaseTypeName.s_date_time: OpenAPIStringT,  # IMPROVE: Aliased DateTimeStr
    # Decimal's are marked as to_string_values thus are strings in the front-end
    builder.BaseTypeName.s_decimal: OpenAPIStringT,
    builder.BaseTypeName.s_integer: OpenAPIIntegerT,
    builder.BaseTypeName.s_lossy_decimal: OpenAPINumberT,
    builder.BaseTypeName.s_opaque_key: OpenAPIStringT,
    builder.BaseTypeName.s_string: OpenAPIStringT,
    # UNC: global types
}


class OpenAPIDefaultBehavior(StrEnum):
    OPTIONAL_WITH_DEFAULT = "optional_with_default"


def _rewrite_with_notice(
    file_path: str, file_content: str, *, notice: str = MODIFY_NOTICE
) -> bool:
    pattern = re.compile(r"^\S", re.MULTILINE)

    file_lines = file_content.split("\n")
    comment_lines = []
    for line_number, line in enumerate(file_lines):
        match = pattern.match(line)
        if match is not None and match.group() != "-" and line_number > 0:
            comment_lines.append(f"{notice}")
        comment_lines.append(line)

    modified_file_content = "\n".join(comment_lines)

    return util.rewrite_file(file_path, f"{notice}\n{modified_file_content}")


def _write_guide_as_html(guide: EmitOpenAPIGuide, *, is_open: bool) -> str:
    return f"""
        <details id="{guide.ref_name}" {"open" if is_open else ""}>
        <summary>{guide.title}</summary>
        {guide.html_content}
        </details>"""


def _open_api_info(
    config: OpenAPIConfig, guides: list[EmitOpenAPIGuide]
) -> GlobalContextInfo:
    full_guides = "<br/>".join([
        _write_guide_as_html(guide, is_open=True)
        for guide in sorted(guides, key=lambda g: g.ref_name)
    ])
    full_description = f"{config.description}<br/>{full_guides}"
    info: GlobalContextInfo = dict()
    info["version"] = "1.0.0"
    info["title"] = "Uncountable API Documentation"
    info["description"] = full_description
    info["x-logo"] = {"url": "../static/images/logo_blue.png", "altText": "Logo"}
    return info


def _open_api_servers(config: OpenAPIConfig) -> list[EmitOpenAPIServer]:
    server_url = config.server_url
    return [EmitOpenAPIServer(url=server_url)] if server_url is not None else []


def emit_open_api(builder: builder.SpecBuilder, *, config: OpenAPIConfig) -> None:
    root_guides = builder.guides.get(RootGuideKey(), [])
    openapi_guides = [
        EmitOpenAPIGuide(
            ref_name=guide.ref_name, title=guide.title, html_content=guide.html_content
        )
        for guide in root_guides
    ]
    gctx = EmitOpenAPIGlobalContext(
        version="3.0.0",
        info=_open_api_info(config, openapi_guides),
        servers=_open_api_servers(config),
    )

    for namespace in sorted(builder.namespaces.values(), key=lambda ns: ns.name):
        ctx = EmitOpenAPIContext(namespace=namespace)

        if (
            ctx.namespace.endpoint is not None
            and ctx.namespace.endpoint.stability_level
            == EmitOpenAPIStabilityLevel.draft
        ):
            continue

        if ctx.namespace.name == "base":
            # TODO: add additional base defintions here
            ctx.types["ObjectId"] = OpenAPIIntegerT()
            ctx.types["JsonValue"] = OpenAPIStringT()

        _emit_namespace(
            gctx,
            ctx,
            namespace=namespace,
            config=config,
            examples=builder.examples,
            guides=builder.guides,
        )

    _rewrite_with_notice(
        f"{config.types_output}/openapi.yaml", _serialize_global_context(gctx)
    )


def _serialize_global_context(ctx: EmitOpenAPIGlobalContext) -> str:
    oa_root: dict[str, object] = dict()

    oa_root["openapi"] = ctx.version
    oa_root["info"] = ctx.info
    oa_root["servers"] = [*map(dataclasses.asdict, ctx.servers)]

    sorted_tags = sorted(ctx.tags, key=lambda tag: tag.name)
    oa_root["tags"] = [dataclasses.asdict(tag) for tag in sorted_tags]

    oa_tag_groups: list[TagGroupToNamedTags] = []
    for tag_group in sorted(ctx.tag_groups.keys()):
        sub_tags = ctx.tag_groups[tag_group]
        oa_tag_groups.append({"name": tag_group, "tags": sorted(sub_tags)})
    oa_root["x-tagGroups"] = oa_tag_groups

    oa_paths: TagPathsToRef = dict()
    for path in ctx.paths:
        # assert path.path not in oa_paths
        oa_paths[path.path] = {"$ref": path.ref}
    oa_root["paths"] = oa_paths

    return yaml.dumps(oa_root, sort_keys=False)


def _is_empty_object_type(typ: OpenAPIType) -> bool:
    if not isinstance(typ, OpenAPIObjectType):
        return False
    return len(typ.properties) == 0


_QUERY_PARM_METHODS = ("get", "head", "options")
_REQUEST_BODY_METHODS = ("put", "post", "patch", "delete")

ApiSchema = dict[str, "ApiSchema"] | Collection["ApiSchema"] | str | bool
DictApiSchema = dict[str, ApiSchema]


def _emit_endpoint_argument_examples(
    examples: list[EmitOpenAPIEndpointExample],
) -> DictApiSchema:
    if len(examples) == 0:
        return {}

    response_examples = {}
    for example in examples:
        response_examples[example.ref_name] = {
            "summary": example.summary,
            "description": example.description,
            "value": example.arguments,
        }
    return {"examples": response_examples}


def _emit_endpoint_parameter_examples(
    examples: list[EmitOpenAPIEndpointExample],
) -> DictApiSchema:
    if len(examples) == 0:
        return {}

    paramater_examples = []
    comment_new_line = "\n// "
    new_line = "\n"
    for example in examples:
        javascript_description = (
            f"// {comment_new_line.join(example.description.split(new_line))}"
        )
        javascript_json_payload = f"{json.dumps(example.arguments, indent=2)}"
        paramater_examples.append({
            "lang": "JavaScript",
            "label": f"Payload - {example.summary}",
            "source": f"{javascript_description}\n{javascript_json_payload}",
        })
    return {"x-codeSamples": paramater_examples}


def _emit_endpoint_parameters(
    endpoint: EmitOpenAPIEndpoint,
    argument_type: OpenAPIType | None,
    examples: list[EmitOpenAPIEndpointExample],
) -> DictApiSchema:
    if (
        endpoint.method.lower() not in _QUERY_PARM_METHODS
        or argument_type is None
        or _is_empty_object_type(argument_type)
    ):
        return {}

    return {
        "parameters": [
            {
                "name": "data",
                "required": True,
                "in": "query",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schema/Arguments"}
                    }
                },
            }
        ]
    } | _emit_endpoint_parameter_examples(examples)


def _emit_endpoint_deprecated(deprecated: bool) -> DictApiSchema:
    return {"deprecated": True} if deprecated else {}


def _emit_stability_level(
    stability_level: EmitOpenAPIStabilityLevel | None,
) -> DictApiSchema:
    stability_info: dict[str, ApiSchema] = {}
    resolved_stability_level = (
        stability_level
        if stability_level is not None
        else EmitOpenAPIStabilityLevel.stable
    )
    stability_info["x-stability-level"] = str(resolved_stability_level)
    match resolved_stability_level:
        case EmitOpenAPIStabilityLevel.draft:
            stability_info["x-beta"] = True
        case EmitOpenAPIStabilityLevel.beta:
            stability_info["x-badges"] = [
                {
                    "name": "Beta",
                    "color": "DarkOrange",
                }
            ]
        case EmitOpenAPIStabilityLevel.stable:
            pass
        case _:
            assert_never(stability_level)
    return stability_info


def _emit_endpoint_request_body(
    endpoint: EmitOpenAPIEndpoint,
    arguments_type: OpenAPIType | None,
    examples: list[EmitOpenAPIEndpointExample],
) -> DictApiSchema:
    if (
        endpoint.method.lower() not in _REQUEST_BODY_METHODS
        or arguments_type is None
        or _is_empty_object_type(arguments_type)
    ):
        return {}

    return {
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "title": "Body",
                        "required": ["data"],
                        "properties": {
                            "data": {"$ref": "#/components/schema/Arguments"}
                        },
                    }
                }
                | _emit_endpoint_argument_examples(examples)
            },
        }
    }


def _emit_endpoint_response_examples(
    examples: list[EmitOpenAPIEndpointExample],
) -> dict[str, dict[str, object]]:
    if len(examples) == 0:
        return {}

    response_examples: dict[str, object] = {}
    for example in examples:
        response_examples[example.ref_name] = {
            "summary": example.summary,
            "description": example.description,
            "value": example.data,
        }
    return {"examples": response_examples}


def _create_warning_banner(api_type: str, message: str) -> str:
    return (
        f'<div style="background-color: #fff3cd; border: 1px solid #ffeaa7; '
        f'border-radius: 4px; padding: 12px; margin-bottom: 16px;">'
        f"<strong>⚠️ {api_type} API:</strong> {message}"
        f"</div>"
    )


def _get_stability_warning(
    stability_level: EmitOpenAPIStabilityLevel | None,
) -> str:
    resolved_stability_level = (
        stability_level
        if stability_level is not None
        else EmitOpenAPIStabilityLevel.stable
    )

    match resolved_stability_level:
        case EmitOpenAPIStabilityLevel.draft:
            return _create_warning_banner(
                "Draft",
                "This endpoint is in draft status and may change significantly. Not recommended for production use.",
            )
        case EmitOpenAPIStabilityLevel.beta:
            return _create_warning_banner(
                "Beta",
                "This endpoint is in beta and its required parameters may change. Use with caution in production environments.",
            )
        case EmitOpenAPIStabilityLevel.stable:
            return ""


def _emit_endpoint_description(
    description: str,
    guides: list[EmitOpenAPIGuide],
    stability_level: EmitOpenAPIStabilityLevel | None = None,
) -> dict[str, str]:
    stability_warning = _get_stability_warning(stability_level)

    full_guides = "<br/>".join([
        _write_guide_as_html(guide, is_open=False)
        for guide in sorted(guides, key=lambda g: g.ref_name)
    ])

    full_description_parts = [
        part for part in [stability_warning, description, full_guides] if part
    ]
    full_description = "<br/>".join(full_description_parts)

    return {"description": full_description}


def _emit_namespace(
    gctx: EmitOpenAPIGlobalContext,
    ctx: EmitOpenAPIContext,
    namespace: builder.SpecNamespace,
    *,
    config: OpenAPIConfig,
    examples: dict[str, list[builder.SpecEndpointExample]],
    guides: dict[builder.SpecGuideKey, list[builder.SpecGuide]],
) -> None:
    for stype in namespace.types.values():
        _emit_type(ctx, stype, config=config)

    if namespace.endpoint is not None:
        endpoint_examples = examples.get(namespace.endpoint.resolved_path, [])
        endpoint_guides = guides.get(
            EndpointGuideKey(path=namespace.endpoint.resolved_path), []
        )
        _emit_endpoint(
            gctx, ctx, namespace, namespace.endpoint, endpoint_examples, endpoint_guides
        )

    oa_components: dict[str, object] = dict()

    if ctx.endpoint is not None:
        endpoint = ctx.endpoint
        argument_type = ctx.types.get("Arguments")
        oa_endpoint = dict()
        oa_endpoint[endpoint.method] = (
            {
                "tags": endpoint.tags,
                "summary": endpoint.summary,
            }
            | _emit_endpoint_deprecated(endpoint.deprecated)
            | _emit_endpoint_description(
                endpoint.description, ctx.endpoint.guides, endpoint.stability_level
            )
            | _emit_stability_level(endpoint.stability_level)
            | _emit_endpoint_parameters(endpoint, argument_type, ctx.endpoint.examples)
            | _emit_endpoint_request_body(
                endpoint, argument_type, ctx.endpoint.examples
            )
            | {
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schema/Data"}
                            }
                            | _emit_endpoint_response_examples(ctx.endpoint.examples)
                        },
                    }
                },
            }
        )
        oa_components["endpoint"] = oa_endpoint

    types = ctx.types
    if ctx.endpoint is not None:
        # OpenAPI always expected Arguments and Data create
        # them here if they were not already created
        if "Arguments" not in types:
            types["Arguments"] = OpenAPIObjectType({})
        if "Data" not in types:
            types["Data"] = OpenAPIObjectType({})

    if ctx.endpoint is not None and "Data" in ctx.types:
        # IMPROVE: Handle the general case here: wrap result in data object
        types["Data"] = OpenAPIObjectType({"data": types["Data"]})

    if ctx.endpoint is not None and "Arguments" in ctx.types:
        # OpenAPI Expects a different format for arguments
        # then for regular types; do conversion here
        raw_type = types["Arguments"]
        if isinstance(
            raw_type, (OpenAPIIntersectionType, OpenAPIUnionType, OpenAPIRefType)
        ):
            print(
                f"[Warning] Skipping Documentation Generation for Endpoint {ctx.namespace.name} due to unsupported 'Argument' structure"
            )
            # TODO handle inheritence (allOf and refs); need to inline here...
            # for now skip this endpoint
            return

        assert isinstance(raw_type, (OpenAPIObjectType, OpenAPIFreeFormObjectType))

    oa_components["schema"] = cast(
        object,
        {name: value.asdict() for name, value in types.items()},
    )

    path = f"{config.types_output}/common/{'/'.join(namespace.path)}.yaml"
    oa_namespace = {"components": oa_components}
    _rewrite_with_notice(path, yaml.dumps(oa_namespace, sort_keys=False))


def _get_openapi_default_behavior(
    prop: builder.SpecProperty,
) -> OpenAPIDefaultBehavior | None:
    if prop.ext_info is None or prop.ext_info.get("open_api") is None:
        return None
    value_passed = prop.ext_info["open_api"].get("default_required_behavior")
    if value_passed is None:
        return None
    assert isinstance(value_passed, str)
    return OpenAPIDefaultBehavior(value_passed)


def _emit_type(
    ctx: EmitOpenAPIContext,
    stype: builder.SpecType,
    *,
    config: OpenAPIConfig,
) -> None:
    if not isinstance(stype, builder.SpecTypeDefn):
        return
    if stype.is_base or stype.is_predefined:
        return

    if isinstance(stype, builder.SpecTypeDefnExternal):
        # IMPROVE: handle external definitions better (for now map to any)
        ctx.types[stype.name] = OpenAPIEmptyType(
            nullable=True,
            description=f"External Type Definition ({stype.name})",
        )
        return

    assert stype.is_exported, "expecting exported names"
    if isinstance(stype, builder.SpecTypeDefnAlias):
        ctx.types[stype.name] = open_api_type(ctx, stype.alias, config=config)
        return

    if isinstance(stype, builder.SpecTypeDefnUnion):
        converted_discriminator_map: dict[str, OpenAPIRefType] = dict()
        if stype.discriminator_map is not None:
            for discriminator_value, base_type in stype.discriminator_map.items():
                converted_base_type = open_api_type(ctx, base_type, config=config)
                assert isinstance(converted_base_type, OpenAPIRefType)
                converted_discriminator_map[discriminator_value] = converted_base_type
        ctx.types[stype.name] = OpenAPIUnionType(
            [open_api_type(ctx, p, config=config) for p in stype.types],
            discriminator=stype.discriminator,
            discriminator_map=converted_discriminator_map
            if stype.discriminator_map is not None
            else None,
        )
        return

    if isinstance(stype, builder.SpecTypeDefnStringEnum):
        # TODO: check that these are always string enums
        # IMPROVE: reflect the enum names in the description

        # we just use the values here as that is what is being sent...
        values = [entry.value for entry in stype.values.values()]
        ctx.types[stype.name] = OpenAPIEnumType(values)
        return

    assert isinstance(stype, builder.SpecTypeDefnObject)
    assert stype.base is not None

    if stype.properties is None and stype.base.is_base:
        ctx.types[stype.name] = OpenAPIObjectType({})
        return
    elif stype.properties is None:
        # TODO: check if these are actually equivalent
        ctx.types[stype.name] = open_api_type(ctx, stype.base, config=config)
        return
    else:
        properties: dict[str, OpenAPIType] = dict()
        property_desc: dict[str, str] = dict()

        for prop in stype.properties.values():
            ref_type = open_api_type(ctx, prop.spec_type, config=config)
            prop_name = ts_name(prop.name, prop.name_case or stype.name_case)
            if prop.desc:
                property_desc[prop_name] = prop.desc
            if prop.has_default and not prop.parse_require:
                # For now, we'll assume the generated types with defaults are meant as
                # arguments, thus treat like extant==missing
                # IMPROVE: if we can decide they are meant as output instead, then
                # they should be marked as required
                openapi_default_beahvior = _get_openapi_default_behavior(prop)
                match openapi_default_beahvior:
                    case None:
                        pass
                    case OpenAPIDefaultBehavior.OPTIONAL_WITH_DEFAULT:
                        ref_type.nullable = True
                        assert prop.default is not None, (
                            "optional_with_default requires default"
                        )
                        ref_type.default = prop.default
                properties[prop_name] = ref_type
            elif prop.extant == builder.PropertyExtant.missing:
                # Unlike optional below, missing does not imply null is possible. They
                # treated distinctly.
                properties[prop_name] = ref_type
            elif prop.extant == builder.PropertyExtant.optional:
                # Need to add in |null since Python side can produce null's right now
                # IMPROVE: It would be better if the serializer could instead omit the None's
                # Dropping the null should be forward compatible
                ref_type.nullable = True
                properties[prop_name] = ref_type
            else:
                properties[prop_name] = ref_type
        final_type: OpenAPIType = OpenAPIObjectType(
            properties, property_desc=property_desc
        )

    if not stype.base.is_base:
        # support inheritance via allOf
        final_type = OpenAPIIntersectionType([
            open_api_type(ctx, stype.base, config=config),
            final_type,
        ])

    ctx.types[stype.name] = final_type


def _emit_constant(ctx: EmitOpenAPIContext, sconst: builder.SpecConstant) -> None:
    if sconst.value_type.is_base_type(builder.BaseTypeName.s_string):
        value = util.encode_common_string(cast(str, sconst.value))
    elif sconst.value_type.is_base_type(builder.BaseTypeName.s_integer):
        value = str(sconst.value)
    else:
        raise Exception("invalid constant type", sconst.name)

    const_name = sconst.name.upper()
    print("_emit_constant", value, const_name)


def _emit_endpoint(
    gctx: EmitOpenAPIGlobalContext,
    ctx: EmitOpenAPIContext,
    namespace: builder.SpecNamespace,
    endpoint: builder.SpecEndpoint,
    endpoint_examples: list[builder.SpecEndpointExample],
    endpoint_guides: list[builder.SpecGuide],
) -> None:
    assert namespace.endpoint is not None
    assert namespace.path[0] == "api"

    has_arguments = "Arguments" in namespace.types
    has_data = "Data" in namespace.types
    has_deprecated_result = "DeprecatedResult" in namespace.types
    is_binary = endpoint.result_type == builder.ResultType.binary

    result_type_count = sum([has_data, has_deprecated_result, is_binary])

    assert result_type_count < 2
    is_binary = endpoint.result_type == builder.ResultType.binary

    # Don't emit interface for those with unsupported types
    if not has_arguments or result_type_count == 0:
        return
    if not is_binary and endpoint.result_type != builder.ResultType.json:
        return

    assert len(namespace.path) > 1
    tag_group = namespace.path[1]
    tag_subgroup = namespace.path[2] if len(namespace.path) > 2 else "General"

    tag_name = f"{tag_group}/{tag_subgroup}"
    # IMPROVE Add Per Tag Descriptions via type_spec index files
    gctx.tags.add(EmitOpenAPITag(name=tag_name, description=""))
    gctx.tag_groups[tag_group].add(tag_name)

    ref_path = f"common/{'/'.join(namespace.path)}.yaml#/components/endpoint"
    ep = namespace.endpoint
    gctx.paths.append(
        EmitOpenAPIPath(
            path=f"/{ep.resolved_path}",
            ref=ref_path,
        )
    )

    description = namespace.endpoint.desc if namespace.endpoint.desc is not None else ""
    if endpoint.is_external:
        description = f"**[External API-Endpoint]** <br/> {description}"

    path_cutoff = min(3, len(namespace.path) - 1)

    ctx.endpoint = EmitOpenAPIEndpoint(
        method=namespace.endpoint.method.lower(),
        tags=[tag_name],
        summary=f"{'/'.join(namespace.path[path_cutoff:])}",
        description=description,
        deprecated=namespace.endpoint.deprecated,
        stability_level=namespace.endpoint.stability_level,
        examples=[
            EmitOpenAPIEndpointExample(
                ref_name=f"ex_{i}",
                summary=example.summary,
                description=example.description,
                arguments=serialize_for_api(example.arguments),
                data=serialize_for_api(example.data),
            )
            for i, example in enumerate(endpoint_examples)
        ],
        guides=[
            EmitOpenAPIGuide(
                ref_name=guide.ref_name,
                title=guide.title,
                html_content=guide.html_content,
            )
            for guide in endpoint_guides
        ],
    )


def _enum_name(name: str, name_case: builder.NameCase) -> str:
    if name_case == builder.NameCase.js_upper:
        return name.upper()
    return ts_name(name, name_case)


def _emit_value(stype: builder.SpecType, value: object) -> str:
    """Mimics emit_python even if not all types are used in OpenAPI yet"""
    literal = builder.unwrap_literal_type(stype)
    if literal is not None:
        return _emit_value(literal.value_type, literal.value)

    if stype.is_base_type(builder.BaseTypeName.s_string):
        assert isinstance(value, str)
        return util.encode_common_string(value)
    elif stype.is_base_type(builder.BaseTypeName.s_integer):
        assert isinstance(value, int)
        return str(value)
    elif stype.is_base_type(builder.BaseTypeName.s_boolean):
        assert isinstance(value, bool)
        return "true" if value else "false"
    elif stype.is_base_type(builder.BaseTypeName.s_lossy_decimal):
        return str(value)
    elif stype.is_base_type(builder.BaseTypeName.s_decimal):
        return f"'{value}'"
    elif isinstance(stype, builder.SpecTypeDefnStringEnum):
        return f"{stype.name}.{_enum_name(str(value), stype.name_case)}"
    else:
        raise Exception("invalid constant type", value, stype)


def open_api_type(
    ctx: EmitOpenAPIContext,
    stype: builder.SpecType,
    *,
    config: OpenAPIConfig,
) -> OpenAPIType:
    if isinstance(stype, builder.SpecTypeInstance):
        if stype.defn_type.name == builder.BaseTypeName.s_list:
            return OpenAPIArrayType(
                open_api_type(ctx, stype.parameters[0], config=config)
            )
        if stype.defn_type.name == builder.BaseTypeName.s_union:
            return OpenAPIUnionType([
                open_api_type(ctx, p, config=config) for p in stype.parameters
            ])
        if stype.defn_type.name == builder.BaseTypeName.s_literal:
            # IMPROVE relax the string constraint for literals (for now treat as string)
            parts = []
            for parameter in stype.parameters:
                assert isinstance(parameter, builder.SpecTypeLiteralWrapper)
                parts.append(parameter.value)

            return OpenAPIEnumType([str(x) for x in parts])
        if stype.defn_type.name == builder.BaseTypeName.s_optional:
            ref_type = open_api_type(ctx, stype.parameters[0], config=config)
            ref_type.nullable = True
            return ref_type
        if stype.defn_type.name == builder.BaseTypeName.s_tuple:
            # IMPROVE potentially handle tuples better: for now map tupples to arrays of those types
            return OpenAPIArrayType(
                [open_api_type(ctx, p, config=config) for p in stype.parameters],
                description="TupleType",
            )
        if stype.defn_type.name == builder.BaseTypeName.s_readonly_array:
            return OpenAPIArrayType(
                open_api_type(ctx, stype.parameters[0], config=config)
            )

        # TODO: generics are not supported by OpenAPI
        # map to Free-Form Object and add description
        # IMPROVE: Create a better description for this
        return OpenAPIFreeFormObjectType(description=f"({stype.defn_type.name})")

    if isinstance(stype, builder.SpecTypeLiteralWrapper):
        # TODO: relax the string constraint for literals (for now treat as string)
        # i.e. convert from stype.value_type
        return OpenAPIEnumType([_emit_value(stype.value_type, stype.value)])

    assert isinstance(stype, builder.SpecTypeDefn)
    if stype.is_base:  # assume correct namespace
        if stype.name == builder.BaseTypeName.s_list:
            return OpenAPIArrayType([])  # TODO: generic type
        return base_name_map[builder.BaseTypeName(stype.name)]()

    if stype.namespace == ctx.namespace:
        # internal namespace resolution
        return OpenAPIRefType(source=f"#/components/schema/{stype.name}")

    ctx.namespaces.add(stype.namespace)
    # external namespace resolution
    return OpenAPIRefType(
        source=f"{resolve_namespace_ref(source_path=ctx.namespace.path, ref_path=stype.namespace.path, ref='/components/schema')}/{stype.name}"
    )
