import base64
import functools
from dataclasses import dataclass

from flask.wrappers import Response


class HttpException(Exception):
    error_code: int
    message: str

    def __init__(self, *, error_code: int, message: str) -> None:
        self.error_code = error_code
        self.message = message

    @staticmethod
    def payload_failed_signature() -> "HttpException":
        return HttpException(
            error_code=401, message="webhook payload did not match signature"
        )

    @staticmethod
    def no_signature_passed() -> "HttpException":
        return HttpException(error_code=400, message="missing signature")

    @staticmethod
    def body_parse_error() -> "HttpException":
        return HttpException(error_code=400, message="body parse error")

    @staticmethod
    def unknown_error() -> "HttpException":
        return HttpException(error_code=500, message="internal server error")

    @staticmethod
    def configuration_error(
        message: str = "internal configuration error",
    ) -> "HttpException":
        return HttpException(error_code=500, message=message)

    def __str__(self) -> str:
        return f"[{self.error_code}]: {self.message}"

    def make_error_response(self) -> Response:
        return Response(
            status=self.error_code, response={"error": {"message": str(self)}}
        )


@dataclass(kw_only=True, frozen=True)
class GenericHttpRequest:
    body_base64: str
    headers: dict[str, str]

    @functools.cached_property
    def body_bytes(self) -> bytes:
        return base64.b64decode(self.body_base64)

    @functools.cached_property
    def body_text(self) -> str:
        return self.body_bytes.decode()


@dataclass(kw_only=True)
class GenericHttpResponse:
    response: str
    status_code: int
    headers: dict[str, str] | None = None
