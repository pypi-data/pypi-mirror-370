"""Flywheel client errors."""

import io
import json
import re
import typing as t

from httpx import Request, Response
from httpx._exceptions import (
    CloseError,
    ConnectError,
    ConnectTimeout,
    CookieConflict,
    DecodingError,
    HTTPError,
    HTTPStatusError,
    InvalidURL,
    LocalProtocolError,
    NetworkError,
    PoolTimeout,
    ProtocolError,
    ProxyError,
    ReadError,
    ReadTimeout,
    RemoteProtocolError,
    RequestError,
    RequestNotRead,
    ResponseNotRead,
    StreamClosed,
    StreamConsumed,
    StreamError,
    TimeoutException,
    TooManyRedirects,
    TransportError,
    UnsupportedProtocol,
    WriteError,
    WriteTimeout,
)

__all__ = [
    # httpx errors
    "CloseError",
    "ConnectError",
    "ConnectTimeout",
    "CookieConflict",
    "DecodingError",
    "HTTPError",
    "HTTPStatusError",
    "InvalidURL",
    "LocalProtocolError",
    "NetworkError",
    "PoolTimeout",
    "ProtocolError",
    "ProxyError",
    "ReadError",
    "ReadTimeout",
    "RemoteProtocolError",
    "RequestError",
    "RequestNotRead",
    "ResponseNotRead",
    "StreamClosed",
    "StreamConsumed",
    "StreamError",
    "TimeoutException",
    "TooManyRedirects",
    "TransportError",
    "UnsupportedProtocol",
    "WriteError",
    "WriteTimeout",
    # extra types
    "ClientError",
    "Conflict",
    "InvalidJSONError",
    "JSONDecodeError",
    "NotFound",
    "ServerError",
]


class ClientError(HTTPStatusError):
    """The server returned a response with a 4xx status code."""


class NotFound(ClientError):
    """The server returned a response with a 404 status code."""


class Conflict(ClientError):
    """The server returned a response with a 409 status code."""


class ServerError(HTTPStatusError):
    """The server returned a response with a 5xx status code."""


class ValidationError(Exception):
    """Raised when client configuration is not valid."""


class InvalidJSONError(Exception):
    """A JSON error occurred."""

    def __init__(self, message: str, *, request: Request, response: Response) -> None:
        """Initialize the InvalidJSONError."""
        super().__init__(message)
        self.request = request
        self.response = response


class JSONDecodeError(InvalidJSONError):
    """Couldn't decode the text into json."""


def http_error_getattr(self, name: str):
    """Proxy the response and the request attributes for convenience."""
    # TODO try to subclass requests exceptions in order to enable type-hinting
    # eg. add py.typed after refact so that downstream users can mypy .status_code
    try:
        response = object.__getattribute__(self, "response")
        return getattr(response, name)
    except AttributeError:
        pass
    try:
        request = object.__getattribute__(self, "request")
        return getattr(request, name)
    except AttributeError:
        pass
    raise AttributeError(f"{type(self).__name__} has no attribute {name!r}")


def http_error_str(self) -> str:  # pragma: no cover
    """Return the string representation of a HTTPError."""
    request = self.request or self.response.request
    return f"{request.method} {request.url} - {self.args[0]}"


def connection_error_str(self) -> str:
    """Return the string representation of a ConnectError."""
    request = self.request or self.response.request
    msg = str(self.args[0])
    if "Errno" in msg:
        msg = re.sub(r".*(\[[^']*).*", r"\1", msg)
    if "read timeout" in msg:
        msg = re.sub(r'.*: ([^"]*).*', r"\1", msg)  # pragma: no cover
    if "Connection aborted" in msg:  # TODO investigate: raised locally, not in ci
        msg = re.sub(r".*'([^']*)'.*", r"\1", msg)  # pragma: no cover
    return f"{request.method} {request.url} - {msg}"


def http_status_error_str(self) -> str:
    """Return the string representation of an HTTPStatusError."""
    request = self.request or self.response.request
    msg = (
        f"{request.method} {self.response.url} - "
        f"{self.response.status_code} {self.response.reason_phrase}"
    )
    if self.response.history:
        redirects = "\n".join(
            f"{request.method} {redirect.url} - "
            f"{redirect.status_code} {redirect.reason_phrase}"
            for redirect in self.response.history
        )
        msg = f"{redirects}\n{msg}"
    if not hasattr(self.response, "_content"):
        return msg
    if error_message := get_error_message(stringify(self.response.content)):
        msg += f"\nResponse: {error_message}"
    return msg


def json_error_str(self) -> str:
    """Return the string representation of an InvalidJSONError."""
    request = self.request or self.response.request
    msg = f"{request.method} {self.response.url} - invalid JSON"
    if self.response.content:
        msg += f" response: {truncate(stringify(self.response.content))}"
    return msg


def truncate(
    string: str, max_length_binary: int = 100, max_length_text: int = 1000
) -> str:
    """Return string truncated to be at most 'max_length' characters."""
    if string.startswith("b'") and len(string) > max_length_binary:
        string = string[: max_length_binary - 3].rstrip() + "..."
    elif len(string) > max_length_text:
        string = string[: max_length_text - 3].rstrip() + "..."
    return string.rstrip()


def get_error_message(message: str) -> str:
    """Return human-readable error message from a (possibly JSON) response."""
    try:
        if json_message := json.loads(message).get("message"):
            return json_message  # pragma: no cover
    except Exception:
        pass
    return truncate(message)


def stringify(data: t.Union[t.IO, bytes, str, None]) -> str:
    """Return string representation of a request- or response body."""
    if not data:
        return ""
    # requests.post(url, data=open(file))
    name = getattr(data, "name", None)
    if name:  # pragma: no cover
        return f"file://{name}"
    # requests.post(url, data=BytesIO(b"foo"))
    if isinstance(data, io.BytesIO):  # pragma: no cover
        data = data.getvalue()
    try:
        return data.decode()  # type: ignore
    except (AttributeError, UnicodeDecodeError):  # pragma: no cover
        return str(data)
