"""Flywheel HTTP API Client."""
# ruff: noqa: F405

import dataclasses
import email
import io
import json
import os
import typing as t
import warnings
from collections.abc import AsyncIterator, Iterator

import httpx
from fw_utils import attrify
from httpx import *  # noqa F403
from httpx import _content as httpx_content
from httpx._client import BaseClient

from . import errors
from .client import KILOBYTE, MEGABYTE, FWClient
from .errors import (
    ClientError,
    Conflict,
    InvalidJSONError,
    JSONDecodeError,
    NotFound,
    ServerError,
    ValidationError,
)

__all__ = httpx.__all__ + [
    "ClientError",
    "Conflict",
    "Event",
    "FWClient",
    "InvalidJSONError",
    "JSONDecodeError",
    "NotFound",
    "Part",
    "ServerError",
    "ValidationError",
]


class ProxyBaseClient:
    """Custom base client to enable sharing the base client between multiple clients."""

    def __init__(self, *args, **kwargs):
        self._base = BaseClient(*args, **kwargs)

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self._base, name)
        except AttributeError:  # pragma: no cover
            msg = f"{self.__class__.__name__!r} object has no attribute {name!r}"
            raise AttributeError(msg) from None

    def __setattr__(self, name, value):
        try:
            _base = object.__getattribute__(self, "_base")
            attr = object.__getattribute__(_base.__class__, name)
        except AttributeError:
            attr = None
        if attr and isinstance(attr, property) and attr.fset:
            attr.fset(self._base, value)
        else:
            object.__setattr__(self, name, value)


_orig_json = httpx.Response.json
_orig_raise_for_status = httpx.Response.raise_for_status
_orig_iter_bytes = httpx.Response.iter_bytes
_orig_iter_text = httpx.Response.iter_text
_orig_iter_raw = httpx.Response.iter_raw
_orig_aiter_bytes = httpx.Response.aiter_bytes
_orig_aiter_text = httpx.Response.aiter_text
_orig_aiter_raw = httpx.Response.aiter_raw


def iter_jsonl(self) -> t.Iterator[t.Any]:
    """Yield individual JSON objects from each line of the response stream."""
    with self:
        for line in self.iter_lines():
            yield json.loads(line)


async def aiter_jsonl(self) -> t.AsyncIterator[t.Any]:
    """Yield individual JSON objects from each line of the response stream."""
    async with self:
        async for line in self.aiter_lines():
            yield json.loads(line)


def iter_parts(self, chunk_size: int = MEGABYTE) -> t.Iterator["Part"]:
    """Yield individual message parts from a multipart response stream."""
    content_type = self.headers["content-type"]
    ctype, *ct_info = [ct.strip() for ct in content_type.split(";")]
    if not ctype.lower().startswith("multipart"):
        raise ValueError(f"Content-Type is not multipart: {ctype}")
    for item in ct_info:
        attr, _, value = item.partition("=")
        if attr.lower() == "boundary":
            boundary = value.strip('"')
            break
    else:
        # Some servers set the media type to multipart but don't provide a
        # boundary and just send a single frame in the body - yield as is.
        yield Part(self.read(), split_header=False)
        return
    message = b""
    delimiter = f"\r\n--{boundary}".encode()
    preamble = True
    with self:
        for chunk in self.iter_raw(chunk_size=chunk_size):
            message += chunk
            if preamble and delimiter[2:] in message:
                _, message = message.split(delimiter[2:], maxsplit=1)
                preamble = False
            while delimiter in message:
                content, message = message.split(delimiter, maxsplit=1)
                yield Part(content)
    if not message.startswith(b"--"):
        warnings.warn("Last boundary is not a closing delimiter")


async def aiter_parts(self, chunk_size: int = MEGABYTE) -> t.AsyncIterator["Part"]:
    """Yield individual message parts from a multipart response stream."""
    content_type = self.headers["content-type"]
    ctype, *ct_info = [ct.strip() for ct in content_type.split(";")]
    if not ctype.lower().startswith("multipart"):
        raise ValueError(f"Content-Type is not multipart: {ctype}")
    for item in ct_info:
        attr, _, value = item.partition("=")
        if attr.lower() == "boundary":
            boundary = value.strip('"')
            break
    else:
        # Some servers set the media type to multipart but don't provide a
        # boundary and just send a single frame in the body - yield as is.
        yield Part(await self.aread(), split_header=False)
        return
    message = b""
    delimiter = f"\r\n--{boundary}".encode()
    preamble = True
    async with self:
        async for chunk in self.aiter_raw(chunk_size=chunk_size):
            message += chunk
            if preamble and delimiter[2:] in message:
                _, message = message.split(delimiter[2:], maxsplit=1)
                preamble = False
            while delimiter in message:
                content, message = message.split(delimiter, maxsplit=1)
                yield Part(content)
    if not message.startswith(b"--"):
        warnings.warn("Last boundary is not a closing delimiter")


def iter_events(self, chunk_size: int = KILOBYTE) -> t.Iterator["Event"]:
    """Yield individual events from a Server-Sent Event response stream."""
    content_type = self.headers["content-type"]
    ctype = content_type.split(";")[0].strip()
    if ctype.lower() != "text/event-stream":
        raise ValueError(f"Content-Type is not text/event-stream: {ctype}")

    def iter_sse_lines():
        """Yield lines from the response delimited by either CRLF, LF or CR."""
        buffer = ""
        eols = "\r\n", "\n", "\r"
        for chunk in self.iter_raw(chunk_size=chunk_size):
            buffer += chunk.decode() if isinstance(chunk, bytes) else chunk
            while eol := next((eol for eol in eols if eol in buffer), None):
                # found a CR as the last char - read more in case it's a CRLF
                if eol == "\r" and buffer.index(eol) == len(buffer) - 1:
                    break
                line, buffer = buffer.split(eol, maxsplit=1)
                yield line
        if buffer:
            yield buffer.rstrip("\r")

    with self:
        # TODO retry from last_id if connection lost
        event = Event()
        retry = last_id = None
        for line in iter_sse_lines():
            if line:
                event.parse_line(line)
                retry = event.retry or retry
            elif event.data:
                if event.data.endswith("\n"):
                    event.data = event.data[:-1]
                yield event
                last_id = event.id or last_id
                event = Event()


async def aiter_events(self, chunk_size: int = KILOBYTE) -> t.AsyncIterator["Event"]:
    """Yield individual events from a Server-Sent Event response stream."""
    content_type = self.headers["content-type"]
    ctype = content_type.split(";")[0].strip()
    if ctype.lower() != "text/event-stream":
        raise ValueError(f"Content-Type is not text/event-stream: {ctype}")

    async def iter_sse_lines():
        """Yield lines from the response delimited by either CRLF, LF or CR."""
        buffer = ""
        eols = "\r\n", "\n", "\r"
        async for chunk in self.aiter_raw(chunk_size=chunk_size):
            buffer += chunk.decode() if isinstance(chunk, bytes) else chunk
            while eol := next((eol for eol in eols if eol in buffer), None):
                # found a CR as the last char - read more in case it's a CRLF
                if eol == "\r" and buffer.index(eol) == len(buffer) - 1:
                    break
                line, buffer = buffer.split(eol, maxsplit=1)
                yield line
        if buffer:
            yield buffer.rstrip("\r")

    async with self:
        # TODO retry from last_id if connection lost
        event = Event()
        retry = last_id = None
        async for line in iter_sse_lines():
            if line:
                event.parse_line(line)
                retry = event.retry or retry
            elif event.data:
                if event.data.endswith("\n"):
                    event.data = event.data[:-1]
                yield event
                last_id = event.id or last_id
                event = Event()


def iter_bytes(self, chunk_size: int = MEGABYTE) -> t.Iterator[bytes]:
    return _orig_iter_bytes(self, chunk_size=chunk_size)


async def aiter_bytes(self, chunk_size: int = MEGABYTE) -> t.AsyncIterator[bytes]:
    async for chunk in _orig_aiter_bytes(self, chunk_size=chunk_size):
        yield chunk


def iter_raw(self, chunk_size: int = MEGABYTE) -> t.Iterator[bytes]:
    return _orig_iter_raw(self, chunk_size=chunk_size)


async def aiter_raw(self, chunk_size: int = MEGABYTE) -> t.AsyncIterator[bytes]:
    async for chunk in _orig_aiter_raw(self, chunk_size=chunk_size):
        yield chunk


def iter_text(self, chunk_size: int = MEGABYTE) -> t.Iterator[str]:
    return _orig_iter_text(self, chunk_size=chunk_size)


async def aiter_text(self, chunk_size: int = MEGABYTE) -> t.AsyncIterator[str]:
    async for chunk in _orig_aiter_text(self, chunk_size=chunk_size):
        yield chunk


def raw_prop(self) -> t.BinaryIO:
    if not hasattr(self, "_raw"):
        self._raw = StreamReader(self.stream)
    return self._raw


def _json(self, **kwargs):
    """Return loaded JSON response with attribute access enabled."""
    try:
        return attrify(_orig_json(self, **kwargs))
    except json.JSONDecodeError as exc:
        raise JSONDecodeError(str(exc), request=self.request, response=self) from exc


def _raise_for_status(self) -> httpx.Response:
    """Raise ClientError for 4xx / ServerError for 5xx responses."""
    try:
        return _orig_raise_for_status(self)
    except httpx.HTTPStatusError as exc:
        if self.status_code == 404:
            exc.__class__ = NotFound  # pragma: no cover
        elif self.status_code == 409:
            exc.__class__ = Conflict  # pragma: no cover
        elif self.status_code < 500:
            exc.__class__ = ClientError
        else:
            exc.__class__ = ServerError
        raise


def resp__enter__(self) -> httpx.Response:
    return self


def resp__exit__(self, exc, value, tb) -> None:
    self.close()


async def resp__aenter__(self) -> httpx.Response:
    return self


async def resp__aexit__(self, exc, value, tb) -> None:
    await self.aclose()


class StreamReader(io.IOBase):
    def __init__(self, stream: httpx.SyncByteStream | httpx.AsyncByteStream):
        if isinstance(stream, httpx.SyncByteStream):
            self._stream = iter(stream)
        else:
            self._stream = aiter(stream)
        self._buffer = bytearray()
        self._read_bytes = 0

    def readable(self):
        return True

    def tell(self):
        return self._read_bytes

    def read(self, size=-1):
        if not isinstance(self._stream, Iterator):
            raise RuntimeError("Attempted to call a sync iterator on an async stream.")
        if size == -1:
            for chunk in self._stream:
                self._buffer.extend(chunk)
            result = bytes(self._buffer)
            self._buffer.clear()
            self._read_bytes += len(result)
            return result

        while len(self._buffer) < size:
            try:
                chunk = next(self._stream)
                self._buffer.extend(chunk)
            except StopIteration:
                break
        result = bytes(self._buffer[:size])
        del self._buffer[:size]
        self._read_bytes += len(result)
        return result

    async def aread(self, size=-1):
        if not isinstance(self._stream, AsyncIterator):
            raise RuntimeError("Attempted to call an async iterator on a sync stream.")
        if size == -1:
            async for chunk in self._stream:
                self._buffer.extend(chunk)
            result = bytes(self._buffer)
            self._buffer.clear()
            self._read_bytes += len(result)
            return result

        while len(self._buffer) < size:
            try:
                chunk = await anext(self._stream)
                self._buffer.extend(chunk)
            except StopAsyncIteration:
                break
        result = bytes(self._buffer[:size])
        del self._buffer[:size]
        self._read_bytes += len(result)
        return result


@dataclasses.dataclass
class Part:
    """Single part of a multipart message with it's own headers and content."""

    headers: httpx.Headers
    content: bytes

    def __init__(self, content: bytes, split_header: bool = True):
        """Return message part with it's own headers and content."""
        if not split_header:
            headers = None
        elif b"\r\n\r\n" not in content:
            raise ValueError("Message part does not contain CRLF CRLF")
        else:
            header, content = content.split(b"\r\n\r\n", maxsplit=1)
            headers = email.parser.HeaderParser().parsestr(header.decode()).items()
        self.headers = httpx.Headers(headers or {})
        self.content = content


@dataclasses.dataclass
class Event:
    """Single event from a Server-Sent Event stream."""

    id: t.Optional[str] = None
    type: str = "message"
    data: str = ""
    retry: t.Optional[int] = None

    def parse_line(self, line: str) -> None:
        """Parse non-empty SSE line and incrementally update event attributes."""
        if line.startswith(":"):
            return
        if ":" not in line:
            line += ":"
        field, value = line.split(":", maxsplit=1)
        value = value[1:] if value.startswith(" ") else value
        if field == "id" and "\0" not in value:
            self.id = value
        elif field == "event":
            self.type = value
        elif field == "data":
            self.data += f"{value}\n"
        elif field == "retry" and value.isdigit():
            self.retry = int(value)
        return


def peek_filelike_length(stream: t.Any) -> int | None:
    """Return length of file-like object if possible."""
    try:
        fd = stream.fileno()
        offset = stream.tell()
        length = os.fstat(fd).st_size
    except (AttributeError, OSError):
        try:
            offset = stream.tell()
            length = stream.seek(0, os.SEEK_END)
            stream.seek(offset)
        except (AttributeError, OSError):
            return None
    return length - offset


Client.__bases__ = (ProxyBaseClient,)
AsyncClient.__bases__ = (ProxyBaseClient,)
Response.json = _json
Response.raise_for_status = _raise_for_status
Response.__enter__ = resp__enter__
Response.__exit__ = resp__exit__
Response.__aenter__ = resp__aenter__
Response.__aexit__ = resp__aexit__
Response.raw = property(raw_prop)
Response.iter_bytes = iter_bytes
Response.iter_raw = iter_raw
Response.iter_text = iter_text
Response.iter_jsonl = iter_jsonl
Response.iter_parts = iter_parts
Response.iter_events = iter_events
Response.iter_content = Response.iter_bytes
Response.aiter_bytes = aiter_bytes
Response.aiter_raw = aiter_raw
Response.aiter_text = aiter_text
Response.aiter_jsonl = aiter_jsonl
Response.aiter_parts = aiter_parts
Response.aiter_events = aiter_events
# patch the exceptions for more useful default error messages
HTTPError.__getattr__ = errors.http_error_getattr
HTTPError.__str__ = errors.http_error_str
ConnectError.__str__ = errors.connection_error_str
HTTPStatusError.__str__ = errors.http_status_error_str
InvalidJSONError.__str__ = errors.json_error_str
# patch utils
httpx_content.peek_filelike_length = peek_filelike_length
