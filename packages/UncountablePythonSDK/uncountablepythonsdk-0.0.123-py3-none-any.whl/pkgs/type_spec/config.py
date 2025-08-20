import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Self, TypeVar

from pkgs.serialization import yaml
from pkgs.type_spec.builder import APIEndpointInfo, EndpointKey

ConfigValueType = str | None | Mapping[str, str | None] | list[str]


def _parse_string_lookup(
    key: str, raw_value: ConfigValueType, conv_func: Callable[[str], str]
) -> dict[str, str]:
    assert isinstance(raw_value, dict), f"{key} must be key/values"
    return {
        k: conv_func(v)
        for k, v in raw_value.items()
        if v is not None and isinstance(v, str)
    }


VT = TypeVar("VT")


def _parse_data_lookup(
    key: str,
    raw_value: ConfigValueType,
    conv_func: type[VT],
) -> dict[str, VT]:
    assert isinstance(raw_value, dict), f"{key} must be key/values"
    return {
        k: conv_func(**v)
        for k, v in raw_value.items()
        if v is not None and isinstance(v, dict)
    }


@dataclass(kw_only=True)
class BaseLanguageConfig:
    types_output: (
        str  # folder where the generated type files will be emitted for this language.
    )

    def __post_init__(self: Self) -> None:
        self.types_output = os.path.abspath(self.types_output)


@dataclass(kw_only=True)
class TypeScriptConfig(BaseLanguageConfig):
    endpoint_to_routes_output: dict[
        EndpointKey, str
    ]  # folder for generate route files will be located.
    type_info_output: str  # folder for generated type info files
    id_source_output: str | None = None  # folder for emitted id source maps.
    endpoint_to_frontend_app_type: dict[
        str, str
    ]  # map from api_endpoint to frontend app type

    def __post_init__(self: Self) -> None:
        self.endpoint_to_routes_output = self.endpoint_to_routes_output
        self.type_info_output = os.path.abspath(self.type_info_output)
        self.id_source_output = (
            os.path.abspath(self.id_source_output)
            if self.id_source_output is not None
            else None
        )
        self.endpoint_to_frontend_app_type = _parse_string_lookup(
            "typescript_endpoint_to_frontend_app_type",
            self.endpoint_to_frontend_app_type,
            lambda x: x,
        )


@dataclass(kw_only=True)
class PythonConfig(BaseLanguageConfig):
    types_package: str  # package for the python types
    routes_output: dict[
        str, str
    ]  # folder for generate route files will be located, keyed by the base api endpoint
    id_source_output: str | None = None  # folder for emitted id source maps.
    emit_api_argument_lookup: bool = (
        False  # emit a lookup for api endpoint path to argument type.
    )
    emit_async_batch_processor: bool = False  # emit the async batch wrapping functions
    emit_client_class: bool = False  # emit the base class for the api client
    all_named_type_exports: bool = False  # emit __all__ for all named type exports
    sdk_endpoints_only: bool = False  # only emit is_sdk endpoints
    type_info_output: str | None = None  # folder for generated type info files

    def __post_init__(self: Self) -> None:
        self.routes_output = _parse_string_lookup(
            "python_routes_output", self.routes_output, os.path.abspath
        )
        self.id_source_output = (
            os.path.abspath(self.id_source_output)
            if self.id_source_output is not None
            else None
        )

        if self.type_info_output is not None:
            self.type_info_output = os.path.abspath(self.type_info_output)


@dataclass(kw_only=True)
class OpenAPIConfig(BaseLanguageConfig):
    types_output: str  # The folder to put generated openapi api yaml
    description: str  # Description of api documentation
    static_url_path: (
        str  # the base path where the generated yaml are hosted, e.g. /static/docs
    )
    server_url: str | None = None

    def __post_init__(self: Self) -> None:
        self.types_output = os.path.abspath(self.types_output)


@dataclass(kw_only=True)
class Config:
    top_namespace: str
    type_spec_types: list[str]  # folders containing the yaml type spec definitions
    api_endpoint: dict[str, APIEndpointInfo]
    # languages
    typescript: TypeScriptConfig | None
    python: PythonConfig
    open_api: OpenAPIConfig | None


T = TypeVar("T")


def _parse_language(config_class: type[T], raw_value: ConfigValueType) -> T:
    assert isinstance(raw_value, dict), "expecting language config to have key/values."
    return config_class(**raw_value)


def parse_yaml_config(config_file: str) -> Config:
    with open(config_file, encoding="utf-8") as input:
        raw_config: dict[str, ConfigValueType] = yaml.safe_load(input)

    raw_type_spec_types = raw_config["type_spec_types"]
    assert isinstance(raw_type_spec_types, list), (
        "type_spec_types, must be a list of folders"
    )
    type_spec_types = [os.path.abspath(folder) for folder in raw_type_spec_types]

    api_endpoint = _parse_data_lookup(
        "api_endpoint",
        raw_config.get("api_endpoint", {}),
        APIEndpointInfo,
    )

    raw_typescript = raw_config.get("typescript")
    typescript = (
        _parse_language(TypeScriptConfig, raw_typescript)
        if raw_typescript is not None
        else None
    )
    python = _parse_language(PythonConfig, raw_config["python"])
    raw_open_api = raw_config.get("open_api")
    open_api = (
        _parse_language(OpenAPIConfig, raw_open_api)
        if raw_open_api is not None
        else None
    )

    top_namespace = raw_config["top_namespace"]
    assert isinstance(top_namespace, str)

    return Config(
        top_namespace=top_namespace,
        type_spec_types=type_spec_types,
        api_endpoint=api_endpoint,
        typescript=typescript,
        python=python,
        open_api=open_api,
    )
