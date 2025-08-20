from dataclasses import dataclass


@dataclass(kw_only=True)
class AuthDetailsApiKey:
    api_id: str
    api_secret_key: str


@dataclass(kw_only=True)
class AuthDetailsOAuth:
    refresh_token: str
    scope: str = "unc.rnd"


AuthDetails = AuthDetailsApiKey  # Legacy Mapping
AuthDetailsAll = AuthDetailsApiKey | AuthDetailsOAuth
