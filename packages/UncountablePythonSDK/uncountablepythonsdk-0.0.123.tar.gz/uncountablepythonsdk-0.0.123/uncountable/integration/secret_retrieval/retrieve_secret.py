import base64
import functools
import json
import os

import boto3

from pkgs.argument_parser import CachedParser
from uncountable.types import overrides_t
from uncountable.types.job_definition_t import ProfileMetadata
from uncountable.types.secret_retrieval_t import (
    SecretRetrieval,
    SecretRetrievalAWS,
    SecretRetrievalEnv,
)


class SecretRetrievalError(Exception):
    def __init__(
        self, secret_retrieval: SecretRetrieval, message: str | None = None
    ) -> None:
        self.secret_retrieval = secret_retrieval
        self.message = message

    def __str__(self) -> str:
        append_message = ""
        if self.message is not None:
            append_message = f": {self.message}"
        return f"{self.secret_retrieval.type} secret retrieval failed{append_message}"


@functools.cache
def _get_aws_secret(*, secret_name: str, region_name: str, sub_key: str | None) -> str:
    client = boto3.client("secretsmanager", region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in response:
        secret = response["SecretString"]
    else:
        secret = base64.b64decode(response["SecretBinary"])

    value = json.loads(secret)

    if sub_key is not None:
        assert isinstance(value, dict)
        return str(value[sub_key])
    else:
        return str(value)


@functools.cache
def _load_secret_overrides(profile_name: str) -> dict[SecretRetrieval, str]:
    overrides_parser = CachedParser(overrides_t.Overrides)
    profiles_module = os.environ["UNC_PROFILES_MODULE"]
    try:
        overrides = overrides_parser.parse_yaml_resource(
            package=f"{profiles_module}.{profile_name}",
            resource="local_overrides.yaml",
        )
        return {
            override.secret_retrieval: override.value for override in overrides.secrets
        }
    except FileNotFoundError:
        return {}


def retrieve_secret(
    secret_retrieval: SecretRetrieval, profile_metadata: ProfileMetadata
) -> str:
    value_from_override = _load_secret_overrides(profile_metadata.name).get(
        secret_retrieval
    )
    if value_from_override is not None:
        return value_from_override

    match secret_retrieval:
        case SecretRetrievalEnv():
            env_name = f"UNC_{profile_metadata.name.upper()}_{secret_retrieval.env_key.upper()}"
            secret = os.environ.get(env_name)
            if secret is None:
                raise SecretRetrievalError(
                    secret_retrieval, f"environment variable {env_name} missing"
                )
            return secret
        case SecretRetrievalAWS():
            try:
                return _get_aws_secret(
                    secret_name=secret_retrieval.secret_name,
                    region_name=secret_retrieval.region,
                    sub_key=secret_retrieval.sub_key,
                )
            except Exception as e:
                raise SecretRetrievalError(secret_retrieval) from e
