import base64
import datetime
import re
import typing
from dataclasses import dataclass
from datetime import UTC, timedelta
from enum import StrEnum
from io import BytesIO
from urllib.parse import unquote, urljoin
from uuid import uuid4

import requests
import simplejson as json
from opentelemetry.sdk.resources import Attributes
from requests.exceptions import JSONDecodeError

from pkgs.argument_parser import CachedParser
from pkgs.serialization_util import JsonValue, serialize_for_api
from uncountable.core.environment import get_version
from uncountable.integration.telemetry import Logger, push_scope_optional
from uncountable.types import download_file_t
from uncountable.types.client_base import APIRequest, ClientMethods
from uncountable.types.client_config import ClientConfigOptions

from .file_upload import FileUpload, FileUploader, UploadedFile
from .types import AuthDetailsAll, AuthDetailsApiKey, AuthDetailsOAuth

DT = typing.TypeVar("DT")
UNC_REQUEST_ID_HEADER = "X-UNC-REQUEST-ID"
UNC_SDK_VERSION_HEADER = "X-UNC-SDK-VERSION"


class EndpointMethod(StrEnum):
    POST = "POST"
    GET = "GET"


@dataclass(kw_only=True)
class HTTPRequestBase:
    method: EndpointMethod
    url: str
    headers: dict[str, str]


@dataclass(kw_only=True)
class HTTPGetRequest(HTTPRequestBase):
    method: EndpointMethod = EndpointMethod.GET
    query_params: dict[str, str]


@dataclass(kw_only=True)
class HTTPPostRequest(HTTPRequestBase):
    method: EndpointMethod = EndpointMethod.POST
    body: str | dict[str, str]


HTTPRequest = HTTPPostRequest | HTTPGetRequest


@dataclass(kw_only=True)
class ClientConfig(ClientConfigOptions):
    transform_request: typing.Callable[[requests.Request], requests.Request] | None = (
        None
    )
    logger: Logger | None = None


OAUTH_REFRESH_WINDOW_SECONDS = 60 * 5


class APIResponseError(Exception):
    status_code: int
    message: str
    extra_details: dict[str, JsonValue] | None

    def __init__(
        self,
        status_code: int,
        message: str,
        extra_details: dict[str, JsonValue] | None,
        request_id: str,
    ) -> None:
        super().__init__(status_code, message, extra_details)
        self.status_code = status_code
        self.message = message
        self.extra_details = extra_details
        self.request_id = request_id

    @classmethod
    def construct_error(
        cls,
        status_code: int,
        extra_details: dict[str, JsonValue] | None,
        request_id: str,
    ) -> "APIResponseError":
        message: str
        match status_code:
            case 403:
                message = "unexpected: unauthorized"
            case 410:
                message = "unexpected: not found"
            case 400:
                message = "unexpected: bad arguments"
            case 501:
                message = "unexpected: unimplemented"
            case 504:
                message = "unexpected: timeout"
            case 404:
                message = "not found"
            case 409:
                message = "bad arguments"
            case 422:
                message = "unprocessable"
            case _:
                message = "unknown error"
        return APIResponseError(
            status_code=status_code,
            message=message,
            extra_details=extra_details,
            request_id=request_id,
        )

    def __str__(self) -> str:
        details_obj = {
            "request_id": self.request_id,
            "status_code": self.status_code,
            "extra_details": self.extra_details,
        }
        details = json.dumps(details_obj)
        return f"API response error ({self.status_code}): '{self.message}'. Details: {details}"


class SDKError(Exception):
    message: str
    request_id: str

    def __init__(self, message: str, *, request_id: str) -> None:
        super().__init__(message)
        self.message = message
        self.request_id = request_id

    def __str__(self) -> str:
        return f"internal SDK error (request id {self.request_id}), please contact Uncountable support: {self.message}"


@dataclass(kw_only=True)
class OAuthBearerTokenCache:
    token: str
    expires_at: datetime.datetime


@dataclass(kw_only=True)
class GetOauthBearerTokenData:
    access_token: str
    expires_in: int
    token_type: str
    scope: str


oauth_bearer_token_data_parser = CachedParser(GetOauthBearerTokenData)


@dataclass
class DownloadedFile:
    name: str
    size: int
    data: BytesIO


DownloadedFiles = list[DownloadedFile]


class Client(ClientMethods):
    _parser_map: dict[type, CachedParser] = {}
    _auth_details: AuthDetailsAll
    _base_url: str
    _file_uploader: FileUploader
    _cfg: ClientConfig
    _oauth_bearer_token_cache: OAuthBearerTokenCache | None = None
    _session: requests.Session

    def __init__(
        self,
        *,
        base_url: str,
        auth_details: AuthDetailsAll,
        config: ClientConfig | None = None,
    ):
        self._auth_details = auth_details
        self._base_url = base_url
        self._cfg = config or ClientConfig()
        self._session = requests.Session()
        self._session.verify = not self._cfg.allow_insecure_tls
        self._file_uploader = FileUploader(
            self._base_url,
            self._auth_details,
            self._cfg.allow_insecure_tls,
            logger=self._cfg.logger,
        )

    @classmethod
    def _validate_response_status(
        cls, response: requests.Response, request_id: str
    ) -> None:
        if response.status_code < 200 or response.status_code > 299:
            extra_details: dict[str, JsonValue] | None = None
            try:
                data = response.json()
                extra_details = data
            except JSONDecodeError:
                extra_details = {
                    "body": response.text,
                }
            raise APIResponseError.construct_error(
                status_code=response.status_code,
                extra_details=extra_details,
                request_id=request_id,
            )

    def _get_response_json(
        self, response: requests.Response, request_id: str
    ) -> dict[str, JsonValue]:
        self._validate_response_status(response, request_id)
        try:
            return typing.cast(dict[str, JsonValue], response.json())
        except JSONDecodeError as e:
            raise SDKError("unable to process response", request_id=request_id) from e

    def _send_request(self, request: requests.Request) -> requests.Response:
        if self._cfg.extra_headers is not None:
            request.headers = {**request.headers, **self._cfg.extra_headers}
        if self._cfg.transform_request is not None:
            request = self._cfg.transform_request(request)
        prepared_request = request.prepare()
        response = self._session.send(prepared_request)
        return response

    def do_request(self, *, api_request: APIRequest, return_type: type[DT]) -> DT:
        request_id = str(uuid4())
        http_request = self._build_http_request(
            api_request=api_request, request_id=request_id
        )
        match http_request:
            case HTTPGetRequest():
                request = requests.Request("GET", http_request.url)
                request.params = http_request.query_params
            case HTTPPostRequest():
                request = requests.Request("POST", http_request.url)
                request.data = http_request.body
            case _:
                typing.assert_never(http_request)
        request.headers = http_request.headers
        attributes: Attributes = {
            "method": http_request.method,
            "endpoint": api_request.endpoint,
        }
        with push_scope_optional(self._cfg.logger, "api_call", attributes=attributes):
            if self._cfg.logger is not None:
                self._cfg.logger.log_info(api_request.endpoint, attributes=attributes)
            response = self._send_request(request)
        response_data = self._get_response_json(response, request_id=request_id)
        cached_parser = self._get_cached_parser(return_type)
        try:
            data = response_data["data"]
            return cached_parser.parse_api(data)
        except (ValueError, JSONDecodeError, KeyError) as e:
            raise SDKError("unable to process response", request_id=request_id) from e

    def _get_cached_parser(self, data_type: type[DT]) -> CachedParser[DT]:
        if data_type not in self._parser_map:
            self._parser_map[data_type] = CachedParser(data_type)
        return self._parser_map[data_type]

    def _get_oauth_bearer_token(self, *, oauth_details: AuthDetailsOAuth) -> str:
        if (
            self._oauth_bearer_token_cache is None
            or (
                self._oauth_bearer_token_cache.expires_at
                - datetime.datetime.now(tz=UTC)
            ).total_seconds()
            < OAUTH_REFRESH_WINDOW_SECONDS
        ):
            refresh_url = urljoin(self._base_url, "/token/get_bearer_token")
            request = requests.Request("POST", refresh_url)
            request.data = {
                "client_secret": oauth_details.refresh_token,
                "scope": oauth_details.scope,
                "grant_type": "client_credentials",
            }
            response = self._send_request(request)
            data = self._get_response_json(response, request_id=str(uuid4()))
            token_data = oauth_bearer_token_data_parser.parse_storage(data)
            self._oauth_bearer_token_cache = OAuthBearerTokenCache(
                token=token_data.access_token,
                expires_at=datetime.datetime.now(tz=UTC)
                + timedelta(seconds=token_data.expires_in),
            )

        return self._oauth_bearer_token_cache.token

    def _build_auth_headers(self) -> dict[str, str]:
        match self._auth_details:
            case AuthDetailsApiKey():
                encoded = base64.standard_b64encode(
                    f"{self._auth_details.api_id}:{self._auth_details.api_secret_key}".encode()
                ).decode("utf-8")
                return {"Authorization": f"Basic {encoded}"}
            case AuthDetailsOAuth():
                token = self._get_oauth_bearer_token(oauth_details=self._auth_details)
                return {"Authorization": f"Bearer {token}"}
        typing.assert_never(self._auth_details)

    def _build_http_request(
        self, *, api_request: APIRequest, request_id: str
    ) -> HTTPRequest:
        headers = self._build_auth_headers()
        headers[UNC_REQUEST_ID_HEADER] = request_id
        headers[UNC_SDK_VERSION_HEADER] = get_version()
        method = api_request.method.lower()
        data = {"data": json.dumps(serialize_for_api(api_request.args))}
        match method:
            case "get":
                return HTTPGetRequest(
                    method=EndpointMethod.GET,
                    url=urljoin(self._base_url, api_request.endpoint),
                    query_params=data,
                    headers=headers,
                )
            case "post":
                return HTTPPostRequest(
                    method=EndpointMethod.POST,
                    url=urljoin(self._base_url, api_request.endpoint),
                    body=data,
                    headers=headers,
                )
            case _:
                raise ValueError(f"unsupported request method: {method}")

    def _get_downloaded_filename(self, *, cd: str | None) -> str:
        if not cd:
            return "Unknown"

        fname = re.findall(r"filename\*=UTF-8''(.+)", cd)
        if fname:
            return unquote(fname[0])

        fname = re.findall(r'filename="?(.+)"?', cd)
        if fname:
            return str(fname[0].strip('"'))

        return "Unknown"

    def download_files(
        self, *, file_query: download_file_t.FileDownloadQuery
    ) -> DownloadedFiles:
        """Download a file from uncountable."""
        request_id = str(uuid4())
        api_request = APIRequest(
            method=download_file_t.ENDPOINT_METHOD,
            endpoint=download_file_t.ENDPOINT_PATH,
            args=download_file_t.Arguments(
                file_query=file_query,
            ),
        )
        http_request = self._build_http_request(
            api_request=api_request, request_id=request_id
        )
        request = requests.Request(http_request.method.value, http_request.url)
        request.headers = http_request.headers
        assert isinstance(http_request, HTTPGetRequest)
        request.params = http_request.query_params
        response = self._send_request(request)
        self._validate_response_status(response, request_id)

        content = response.content
        content_disposition = response.headers.get("Content-Disposition", None)
        return [
            DownloadedFile(
                name=self._get_downloaded_filename(cd=content_disposition),
                size=len(content),
                data=BytesIO(content),
            )
        ]

    def upload_files(
        self: typing.Self, *, file_uploads: list[FileUpload]
    ) -> list[UploadedFile]:
        """Upload files to uncountable, returning file ids that are usable with other SDK operations."""
        return self._file_uploader.upload_files(file_uploads=file_uploads)
