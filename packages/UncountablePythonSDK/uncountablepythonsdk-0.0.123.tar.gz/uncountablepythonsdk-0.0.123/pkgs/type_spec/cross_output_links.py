from __future__ import annotations

import os
from dataclasses import dataclass

from pkgs.type_spec import builder


def get_python_stub_file_path(
    function_name: str | None,
) -> str | None:
    if function_name is None:
        return None
    module_dir, file_name, _func_name = function_name.rsplit(".", 2)
    module_path = os.path.relpath(module_dir.replace(".", "/"))
    api_stub_file = f"{module_path}/{file_name}.py"
    return api_stub_file


@dataclass(kw_only=True, frozen=True)
class CrossOutputPaths:
    python_types_output: str
    typescript_types_output: str
    typescript_routes_output_by_endpoint: dict[str, str]
    typespec_files_input: list[str]


def get_python_api_file_path(
    cross_output_paths: CrossOutputPaths,
    namespace: builder.SpecNamespace,
) -> str:
    return f"{cross_output_paths.python_types_output}/{'/'.join(namespace.path)}{'' if len(namespace.path) > 1 else '_t'}.py"


def get_typescript_api_file_path(
    cross_output_paths: CrossOutputPaths,
    namespace: builder.SpecNamespace,
    endpoint_key: builder.EndpointKey,
) -> str:
    return f"{cross_output_paths.typescript_routes_output_by_endpoint[endpoint_key]}/{'/'.join(namespace.path)}.tsx"


def get_yaml_api_file_path(
    cross_output_paths: CrossOutputPaths,
    namespace: builder.SpecNamespace,
) -> str:
    abs_path = next(
        (
            path
            for path in cross_output_paths.typespec_files_input
            if (
                namespace.endpoint is None
                or namespace.endpoint.default_endpoint_key in path
            )
        ),
        cross_output_paths.typespec_files_input[0],
    )
    return f"{os.path.relpath(abs_path)}/{'/'.join(namespace.path)}.yaml"


def get_return_to_root_path(path: str) -> str:
    return "../" * (path.count("/"))


def get_path_links(
    cross_output_paths: CrossOutputPaths | None,
    namespace: builder.SpecNamespace,
    *,
    current_path_type: str,
    endpoint: builder.SpecEndpoint,
) -> str:
    if cross_output_paths is None:
        return ""

    api_paths = {
        "Python": get_python_api_file_path(cross_output_paths, namespace),
        "TypeScript": get_typescript_api_file_path(
            cross_output_paths, namespace, endpoint.default_endpoint_key
        ),
        "YAML": get_yaml_api_file_path(cross_output_paths, namespace),
    }

    assert current_path_type in api_paths

    comment_prefix = "#"
    if current_path_type == "TypeScript":
        comment_prefix = "//"

    return_to_root_path = get_return_to_root_path(api_paths[current_path_type])
    del api_paths[current_path_type]

    paths_string = ""
    for path_name, path in api_paths.items():
        paths_string += (
            f"{comment_prefix} {path_name}: file://./{return_to_root_path}{path}\n"
        )

    if namespace.endpoint is not None:
        for (
            endpoint_key,
            path_specific_endpoint,
        ) in namespace.endpoint.path_per_api_endpoint.items():
            path_from_root = get_python_stub_file_path(path_specific_endpoint.function)
            if path_from_root is None:
                continue
            paths_string += f"{comment_prefix} Implementation for {endpoint_key}: file://./{return_to_root_path}{path_from_root}\n"
    return paths_string
