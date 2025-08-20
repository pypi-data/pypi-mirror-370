from uncountable.core import AuthDetailsApiKey, Client
from uncountable.core.client import ClientConfig
from uncountable.core.types import AuthDetailsAll, AuthDetailsOAuth
from uncountable.integration.secret_retrieval.retrieve_secret import retrieve_secret
from uncountable.integration.telemetry import JobLogger
from uncountable.types import auth_retrieval_t
from uncountable.types.job_definition_t import (
    ProfileMetadata,
)


def _construct_auth_details(profile_meta: ProfileMetadata) -> AuthDetailsAll:
    match profile_meta.auth_retrieval:
        case auth_retrieval_t.AuthRetrievalOAuth():
            refresh_token = retrieve_secret(
                profile_meta.auth_retrieval.refresh_token_secret,
                profile_metadata=profile_meta,
            )
            return AuthDetailsOAuth(refresh_token=refresh_token)
        case auth_retrieval_t.AuthRetrievalBasic():
            api_id = retrieve_secret(
                profile_meta.auth_retrieval.api_id_secret, profile_metadata=profile_meta
            )
            api_key = retrieve_secret(
                profile_meta.auth_retrieval.api_key_secret,
                profile_metadata=profile_meta,
            )

            return AuthDetailsApiKey(api_id=api_id, api_secret_key=api_key)


def _construct_client_config(
    profile_meta: ProfileMetadata, job_logger: JobLogger
) -> ClientConfig | None:
    if profile_meta.client_options is None:
        return None
    return ClientConfig(
        allow_insecure_tls=profile_meta.client_options.allow_insecure_tls,
        extra_headers=profile_meta.client_options.extra_headers,
        logger=job_logger,
    )


def construct_uncountable_client(
    profile_meta: ProfileMetadata, logger: JobLogger
) -> Client:
    return Client(
        base_url=profile_meta.base_url,
        auth_details=_construct_auth_details(profile_meta),
        config=_construct_client_config(profile_meta, logger),
    )
