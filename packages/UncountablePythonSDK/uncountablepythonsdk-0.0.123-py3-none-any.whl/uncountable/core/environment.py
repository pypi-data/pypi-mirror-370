import functools
import os
from importlib.metadata import PackageNotFoundError, version

from uncountable.types import integration_server_t


@functools.cache
def get_version() -> str:
    try:
        version_str = version("UncountablePythonSDK")
    except PackageNotFoundError:
        version_str = "unknown"
    return version_str


def get_server_env() -> str | None:
    return os.environ.get("UNC_SERVER_ENV")


def get_http_server_port() -> int:
    return int(os.environ.get("UNC_WEBHOOK_SERVER_PORT", "5001"))


def get_local_admin_server_port() -> int:
    return int(os.environ.get("UNC_ADMIN_SERVER_PORT", "50051"))


def get_otel_enabled() -> bool:
    return os.environ.get("UNC_OTEL_ENABLED") == "true"


def get_profiles_module() -> str:
    return os.environ["UNC_PROFILES_MODULE"]


def get_integration_envs() -> list[integration_server_t.IntegrationEnvironment]:
    return [
        integration_server_t.IntegrationEnvironment(env)
        for env in os.environ.get("UNC_INTEGRATION_ENVS", "prod").split(",")
    ]
