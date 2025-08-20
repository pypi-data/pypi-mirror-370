import io
import os
from typing import assert_never

from . import builder, util
from .builder import EndpointKey, EndpointSpecificPath, PathMapping
from .config import TypeScriptConfig
from .cross_output_links import get_path_links
from .emit_io_ts import emit_type_io_ts
from .emit_typescript_util import (
    MODIFY_NOTICE,
    EmitTypescriptContext,
    emit_constant_ts,
    emit_namespace_imports_ts,
    emit_type_ts,
    resolve_namespace_name,
    resolve_namespace_ref,
    ts_type_name,
)


def emit_typescript(builder: builder.SpecBuilder, config: TypeScriptConfig) -> None:
    _emit_types(builder, config)
    _emit_id_source(builder, config)


def _emit_types(builder: builder.SpecBuilder, config: TypeScriptConfig) -> None:
    index_out = io.StringIO()
    index_out.write(MODIFY_NOTICE)

    index_out_end = io.StringIO()

    for namespace in sorted(
        builder.namespaces.values(),
        key=lambda ns: resolve_namespace_name(ns),
    ):
        ctx = EmitTypescriptContext(
            out=io.StringIO(),
            namespace=namespace,
            cross_output_paths=builder.cross_output_paths,
            api_endpoints=builder.api_endpoints,
        )

        _emit_namespace(ctx, config, namespace)

        prepart = builder.preparts["typescript"].get(namespace.name)
        part = builder.parts["typescript"].get(namespace.name)

        # Don't emit an empty file
        if (
            prepart is None
            and part is None
            and len(namespace.types) == 0
            and len(namespace.constants) == 0
        ):
            # Try to capture some common incompleteness errors
            if namespace.endpoint is None or any(
                endpoint_specific_path.function is None
                for endpoint_specific_path in namespace.endpoint.path_per_api_endpoint.values()
            ):
                raise Exception(
                    f"Namespace {'/'.join(namespace.path)} is incomplete. It should have an endpoint with function, types, and/or constants"
                )
            continue

        full = io.StringIO()
        if prepart:
            full.write(MODIFY_NOTICE)
            full.write(f"// === START section from {namespace.name}.ts.prepart ===\n")
            full.write(prepart)
            full.write(f"// === END section from {namespace.name}.ts.prepart ===\n")
            full.write("\n")

        emit_namespace_imports_ts(ctx.namespaces, out=full, current_namespace=namespace)
        if namespace.emit_io_ts:
            full.write("import * as IO from 'io-ts';")
        full.write(ctx.out.getvalue())

        if part:
            full.write("\n")
            full.write(MODIFY_NOTICE)
            full.write(f"// === START section from {namespace.name}.ts.part ===\n")
            full.write("\n")
            full.write(part)
            full.write(f"// === END section from {namespace.name}.ts.part ===\n")

        full.write(MODIFY_NOTICE)

        basename = "/".join(namespace.path)
        filename = f"{config.types_output}/{basename}.ts"
        util.rewrite_file(filename, full.getvalue())

        if len(namespace.path) == 1:
            index_out.write(
                f"import * as {resolve_namespace_ref(namespace)} from './{resolve_namespace_name(namespace)}'\n"
            )  # noqa: E501
            index_out_end.write(f"export {{{resolve_namespace_ref(namespace)}}}\n")

    index_out.write("\n")
    index_out.write(MODIFY_NOTICE)
    index_out.write(index_out_end.getvalue())
    index_out.write(MODIFY_NOTICE)
    util.rewrite_file(f"{config.types_output}/index.ts", index_out.getvalue())


def _emit_namespace(
    ctx: EmitTypescriptContext,
    config: TypeScriptConfig,
    namespace: builder.SpecNamespace,
) -> None:
    for stype in namespace.types.values():
        if namespace.emit_io_ts:
            emit_type_io_ts(ctx, stype, namespace.derive_types_from_io_ts)
        if not namespace.emit_io_ts or not namespace.derive_types_from_io_ts:
            emit_type_ts(ctx, stype)

    for sconst in namespace.constants.values():
        emit_constant_ts(ctx, sconst)

    if namespace.endpoint is not None:
        _emit_endpoint(ctx, config, namespace, namespace.endpoint)


def _emit_endpoint(
    ctx: EmitTypescriptContext,
    config: TypeScriptConfig,
    namespace: builder.SpecNamespace,
    endpoint: builder.SpecEndpoint,
) -> None:
    if endpoint.suppress_ts:
        return

    assert namespace.path[0] == "api"
    has_arguments = "Arguments" in namespace.types
    has_data = "Data" in namespace.types
    has_deprecated_result = "DeprecatedResult" in namespace.types
    is_binary = endpoint.result_type == builder.ResultType.binary
    has_multiple_endpoints = len(endpoint.path_per_api_endpoint) > 1

    result_type_count = sum([has_data, has_deprecated_result, is_binary])
    assert result_type_count < 2

    # Don't emit interface for those with unsupported types
    if not has_arguments or result_type_count == 0:
        return

    if not is_binary:
        assert endpoint.result_type == builder.ResultType.json

    paths_string = get_path_links(
        ctx.cross_output_paths,
        namespace,
        current_path_type="TypeScript",
        endpoint=endpoint,
    )

    data_loader_head = ""
    data_loader_body = ""
    if endpoint.data_loader:
        # Don't support alternately named data for now
        assert has_data

        data_loader_head = (
            'import { argsKey, buildApiDataLoader } from "unc_base/data_manager"\n'
        )
        data_loader_body = (
            "\nexport const data = buildApiDataLoader(argsKey(), apiCall)\n"
        )

    method = endpoint.method.capitalize()
    if endpoint.has_attachment:
        assert endpoint.method == "post"
        method = f"{method}Attach"
    wrap_name = (
        f"buildWrappedBinary{method}Call" if is_binary else f"buildWrapped{method}Call"
    )
    wrap_call = (
        f"{wrap_name}<Arguments>" if is_binary else f"{wrap_name}<Arguments, Response>"
    )

    unc_base_api_imports = (
        f"appSpecificApiPath, {wrap_name}" if has_multiple_endpoints else wrap_name
    )
    path_mapping = ctx.api_endpoints[endpoint.default_endpoint_key].path_mapping

    match path_mapping:
        case PathMapping.NO_MAPPING:
            path_mapping_part = (
                "\n  { pathMapping: ApplicationT.APIPathMapping.noMapping },"
            )
        case PathMapping.DEFAULT_MAPPING:
            path_mapping_part = ""
        case _:
            assert_never(path_mapping)

    unc_types_imports = (
        'import { ApplicationT } from "unc_types"\n'
        if has_multiple_endpoints or path_mapping_part != ""
        else ""
    )

    type_path = f"unc_types/{'/'.join(namespace.path)}"

    if is_binary:
        tsx_response_head = f"""import {{ {unc_base_api_imports} }} from "unc_base/api"
"""
        tsx_response_part = f"""import type {{ Arguments }} from "{type_path}"

export type {{ Arguments }}
"""
    elif has_data and endpoint.has_attachment:
        tsx_response_head = f"""import {{ type AttachmentResponse, {unc_base_api_imports} }} from "unc_base/api"
"""
        tsx_response_part = f"""import type {{ Arguments, Data }} from "{type_path}"

export type {{ Arguments, Data }}
export type Response = AttachmentResponse<Data>
"""
    elif has_data:
        tsx_response_head = f"""import {{ {unc_base_api_imports}, type JsonResponse }} from "unc_base/api"
"""
        tsx_response_part = f"""import type {{ Arguments, Data }} from "{type_path}"

export type {{ Arguments, Data }}
export type Response = JsonResponse<Data>
"""

    else:
        assert has_deprecated_result
        tsx_response_head = f"""import {{ {unc_base_api_imports} }} from "unc_base/api"
"""
        tsx_response_part = f"""import type {{ Arguments, DeprecatedResult }} from "{type_path}"

export type {{ Arguments }}
export type Response = DeprecatedResult
"""

    """

    export const apiCall = buildWrappedGetCall<Arguments, Response>(
      appSpecificApiPath({
        [ApplicationT.FrontendApplication.materials]: "api/materials/common/list_id_source",
      }),
    )


    """

    if not has_multiple_endpoints:
        default_endpoint_path = endpoint.path_per_api_endpoint[
            endpoint.default_endpoint_key
        ]
        endpoint_path_part = f'"{default_endpoint_path.path_root}/{default_endpoint_path.path_dirname}/{default_endpoint_path.path_basename}",'
    else:
        path_lookup_map = ""
        api_endpoint_key: EndpointKey
        endpoint_specific_path: EndpointSpecificPath
        for (
            api_endpoint_key,
            endpoint_specific_path,
        ) in endpoint.path_per_api_endpoint.items():
            full_path = f"{endpoint_specific_path.path_root}/{endpoint_specific_path.path_dirname}/{endpoint_specific_path.path_basename}"
            frontend_app_value = config.endpoint_to_frontend_app_type[api_endpoint_key]

            path_lookup_map += (
                f'\n    [ApplicationT.{frontend_app_value}]: "{full_path}",'
            )

        endpoint_path_part = f"""appSpecificApiPath({{{path_lookup_map}
  }}),"""

    # tsx_api = f"""{MODIFY_NOTICE}
    tsx_api = f"""{MODIFY_NOTICE}{paths_string}
{tsx_response_head}{data_loader_head}{unc_types_imports}{tsx_response_part}
export const apiCall = {wrap_call}(
  {endpoint_path_part}{path_mapping_part}
)
{data_loader_body}"""

    output = f"{config.endpoint_to_routes_output[endpoint.default_endpoint_key]}/{'/'.join(namespace.path)}.tsx"
    util.rewrite_file(output, tsx_api)

    # Hacky index support, until enough is migrated to regen entirely
    # Emits the import into the UI API index file
    index_path = f"{config.endpoint_to_routes_output[endpoint.default_endpoint_key]}/{'/'.join(namespace.path[0:-1])}/index.tsx"
    api_name = f"Api{ts_type_name(namespace.path[0 - 1])}"
    if os.path.exists(index_path):
        with open(index_path) as index:
            index_data = index.read()
            need_index = index_data.find(api_name) == -1
    else:
        need_index = True

    if need_index:
        with open(index_path, "a") as index:
            print(f"Updated API Index {index_path}")
            index.write(f'import * as {api_name} from "./{namespace.path[-1]}"\n\n')
            index.write(f"export {{ {api_name} }}\n")


def _emit_id_source(builder: builder.SpecBuilder, config: TypeScriptConfig) -> None:
    id_source_output = config.id_source_output
    if id_source_output is None:
        return
    enum_out = io.StringIO()
    enum_out.write(MODIFY_NOTICE)

    enum_out.write("export type KnownEnumsType =\n")
    enum_map = {
        builder.resolve_proper_name(string_enum): string_enum
        for string_enum in builder.emit_id_source_enums
    }
    sorted_keys = sorted(enum_map.keys())
    for key in sorted_keys:
        enum_out.write(f'  | "{key}"\n')

    enum_out.write(f"\n{MODIFY_NOTICE}")
    enum_out.write("export const ENUM_NAME_MAPS = {\n")
    for key in sorted_keys:
        string_enum = enum_map[key]
        enum_out.write(f'  "{builder.resolve_proper_name(string_enum)}": {{\n')
        for entry in string_enum.values.values():
            if entry.label is not None:
                enum_out.write(f'    "{entry.value}": "{entry.label}",\n')
        enum_out.write("  },\n")
    enum_out.write("}\n")

    enum_out.write(f"\n{MODIFY_NOTICE}")
    util.rewrite_file(id_source_output, enum_out.getvalue())
