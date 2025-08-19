"""HTTP API clients for generic JSON APIs and Flywheel services."""

import os
import platform
import random
import re
import time
import typing as t
from contextlib import asynccontextmanager, contextmanager
from functools import cached_property, partial
from importlib.metadata import version as pkg_version

import backoff
import httpx
from httpx._auth import FunctionAuth
from packaging import version

from .errors import TransportError, ValidationError

# retry http errors for methods and response statuses
RETRY_METHODS = ("DELETE", "GET", "HEAD", "OPTIONS", "POST", "PUT")
RETRY_STATUSES = (429, 502, 503, 504)
RETRY_BACKOFF = 0.5
RETRY_TOTAL = 4


class APIClient(httpx.Client):
    """Generic HTTP API base client."""

    def __init__(  # noqa: PLR0913, PLR0915
        self,
        *,
        client_name: str | None = None,
        client_version: str | None = None,
        client_info: dict[str, str] | None = None,
        services: dict[str, dict] | None = None,
        retry_methods: t.Sequence[str] = RETRY_METHODS,
        retry_statuses: t.Sequence[int] = RETRY_STATUSES,
        retry_backoff: float = RETRY_BACKOFF,
        retry_total: int = RETRY_TOTAL,
        **kwargs,
    ):
        """Initialize HTTP JSON API client."""
        # store some custom attrs on self
        client_info = client_info or {}
        if client_name and client_version:  # pragma: no cover
            client_info[client_name] = client_version
        self.client_name = client_name
        self.client_version = client_version
        self.client_info = client_info
        self.services = services or {}
        self.retry_backoff = retry_backoff
        self.retry_methods = retry_methods
        self.retry_statuses = retry_statuses
        self.retry_total = retry_total
        # setup the sync client
        user_agent = dump_useragent(**client_info)
        kwargs.setdefault("follow_redirects", True)
        kwargs.setdefault("headers", {}).setdefault("user-agent", user_agent)
        kwargs.setdefault("timeout", (10, 30))
        sync_transport = kwargs.pop("transport", None)
        async_transport = kwargs.pop("async_transport", None)
        super().__init__(**kwargs, transport=sync_transport)
        # setup the async client
        self._async = httpx.AsyncClient(**kwargs, transport=async_transport)
        self._async._base = self._base

        # patch request() and stream()
        def prep_request(method, url, **kwargs):
            headers = kwargs.get("headers") or {}
            headers = {key.lower(): value for key, value in headers.items()}
            kwargs["headers"] = headers
            # apply prefix based, service specific kwargs
            if prefixes := [p for p in self.services if url.startswith(p)]:
                prefixes.sort(key=len, reverse=True)
                service = self.services[prefixes[0]].copy()
                url = service.pop("base_url", "") + url
                headers |= service.pop("headers", None) or {}
                kwargs.update(service)
            # support headers['authorization']:None for anonymous requests
            if kwargs.get("auth") is None and headers.get("authorization", ...) is None:
                kwargs["auth"] = httpx_anon
                headers.pop("authorization")  # httpx raises on None
            # support auth:str for setting the authorization header
            if isinstance(kwargs.get("auth"), str):
                headers["authorization"] = kwargs.pop("auth")
            # pop and gather kwargs for retry
            retry_keys = ["backoff", "methods", "statuses", "total"]
            retry_kwargs = {
                key: kwargs.pop(key, getattr(self, key, None))
                for key in [f"retry_{key}" for key in retry_keys]
            }
            # pop and gather kwargs for retry
            send_kwargs = {
                key: kwargs.pop(key, getattr(self, key, None))
                for key in ["auth", "follow_redirects"]
            }
            # build the request and pass it along w/ the split kwargs
            request = self.build_request(method, url, **kwargs)
            return request, retry_kwargs, send_kwargs

        def retry_send(send, request, **kwargs):
            offset = seakable = None
            if stream := getattr(request.stream, "_stream", None):
                try:
                    offset = stream.tell()
                    seakable = stream.seekable()
                except AttributeError:
                    pass

            def retry_when(response: httpx.Response):
                # byte streams can be safely retried
                can_retry = isinstance(response.request.stream, httpx.ByteStream)
                # or seakable file like objects
                if stream and seakable:
                    can_retry = True
                    stream.seek(offset)
                can_retry &= response.request.method in kwargs["retry_methods"]
                can_retry &= response.status_code in kwargs["retry_statuses"]
                return can_retry

            # backoff's max_tries includes the initial request, so add 1
            retry_kw = {
                "max_tries": kwargs["retry_total"] + 1,
                "factor": kwargs["retry_backoff"],
            }
            retry_http = backoff.on_predicate(backoff.expo, retry_when, **retry_kw)
            retry_tfer = backoff.on_exception(backoff.expo, TransportError, **retry_kw)
            return retry_http(retry_tfer(send))

        def prep_response(response: httpx.Response, raw: bool, stream: bool = False):
            if not raw:
                response.raise_for_status()
            if raw or stream:
                return response
            if not response.content:
                return None
            return response.json()

        def request(*args, raw: bool = False, **kwargs):
            request, retry_kwargs, send_kwargs = prep_request(*args, **kwargs)
            send = retry_send(self.send, request, **retry_kwargs)
            response = send(request, **send_kwargs)
            return prep_response(response, raw)

        async def arequest(*args, raw: bool = False, **kwargs):
            request, retry_kwargs, send_kwargs = prep_request(*args, **kwargs)
            send = retry_send(self._async.send, request, **retry_kwargs)
            response = await send(request, **send_kwargs)
            return prep_response(response, raw)

        @contextmanager
        def stream(*args, raw: bool = False, **kwargs):
            request, retry_kwargs, send_kwargs = prep_request(*args, **kwargs)
            send = retry_send(self.send, request, **retry_kwargs)
            response = send(request, stream=True, **send_kwargs)
            try:
                yield prep_response(response, raw, stream=True)
            finally:
                response.close()

        @asynccontextmanager
        async def astream(*args, raw: bool = False, **kwargs):
            request, retry_kwargs, send_kwargs = prep_request(*args, **kwargs)
            send = retry_send(self._async.send, request, **retry_kwargs)
            response = await send(request, stream=True, **send_kwargs)
            try:
                yield prep_response(response, raw, stream=True)
            finally:
                await response.aclose()

        self.request = request
        self.stream = stream
        self._async.request = arequest
        self._async.stream = astream
        for method in ["delete", "get", "head", "options", "patch", "post", "put"]:
            setattr(self, method, partial(request, method))
            setattr(self._async, method, partial(arequest, method))

    def __getattr__(self, name):
        """Proxy 'a' prefixed attributes to the async client."""
        try:
            if name.startswith("a"):
                aname = name[1:] if name != "aclose" else name
                return object.__getattribute__(self._async, aname)
            return object.__getattribute__(self._base, name)
        except AttributeError:  # pragma: no cover
            msg = f"{self.__class__.__name__!r} object has no attribute {name!r}"
            raise AttributeError(msg) from None


# chunk size helpers
KILOBYTE = 1 << 10
MEGABYTE = 1 << 20
# regex to match api keys with (to extract the host if it's embedded)
API_KEY_RE = re.compile(
    r"(?i)"
    r"((?P<api_key_type>bearer|scitran-user) )?"
    r"((?P<scheme>https?://)?(?P<host>[^:]+)(?P<port>:\d+)?:)?"
    r"(?P<api_key>.+)"
)
# global cache of drone keys (device api keys acquired via drone secret)
DRONE_DEVICE_KEYS = {}
# x-accept-feature header sent by default to core-api
CORE_FEATURES = (
    "multipart_signed_url",
    "pagination",
    "safe-redirect",
    "subject-container",
)


class FWClient(APIClient):
    """Flywheel HTTP API base client."""

    def __init__(  # noqa: PLR0912, PLR0913, PLR0915
        self,
        api_key: str | None = None,
        *,
        drone_secret: str | None = None,
        device_type: str | None = None,
        device_label: str | None = None,
        defer_auth: bool = False,
        core_features: t.Sequence[str] = CORE_FEATURES,
        **kwargs,
    ):
        """Initialize FW client."""
        self.api_key = api_key
        self.drone_secret = drone_secret
        self.device_type = device_type or kwargs.get("client_name")
        self.device_label = device_label or self.device_type
        self.defer_auth = defer_auth
        self.core_features = core_features
        # support url/base_url for backwards-compat
        base_url = kwargs.get("base_url") or kwargs.pop("url", None)
        # set the x-accept-feature header on core-api requests
        core_hdr = {"x-accept-feature": ", ".join(core_features)}
        services = kwargs.setdefault("services", {})
        services.setdefault("/api", {}).setdefault("headers", {}).update(core_hdr)
        # TODO default cluster-internal urls - opt in? opt out? env?
        # support io_proxy_url/snapshot_url/xfer_url for backwards-compat
        for svc in ["io_proxy", "snapshot", "xfer"]:
            if svc_url := kwargs.pop(f"{svc}_url", None):
                prefix = f"/{svc}".replace("_", "-")
                services.setdefault(prefix, {})["base_url"] = svc_url
        # extract additional api key info "[type ][scheme://]host[:port]:key"
        if api_key:
            if not (match := API_KEY_RE.match(api_key)):  # pragma: no cover
                raise ValidationError(f"invalid api_key: {api_key!r}")
            info = match.groupdict()
            # clean the key of extras (enhanced keys don't allow any)
            api_key = info["api_key"]
            # use site url prefixed on the key if otherwise not provided
            if not base_url and info["host"]:
                scheme = info["scheme"] or "https://"
                host = info["host"]
                port = info["port"] or ""
                base_url = f"{scheme}{host}{port}"
        # raise if we don't have the base_url passed directly or from api_key
        if not base_url:
            raise ValidationError("api_key with domain or base_url required")
        # default to https:// when passing a domain to base_url
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"
        # strip base_url /api path suffix if present to accommodate other apis
        base_url = re.sub(r"(/api)?/?$", "", base_url)
        kwargs["base_url"] = base_url
        super().__init__(**kwargs)
        # require auth (unless it's deferred via defer_auth)
        creds = api_key or self.drone_secret
        if self.defer_auth and creds:
            msg = "api_key and drone_secret not allowed with defer_auth"
            raise ValidationError(msg)
        elif not self.defer_auth and not creds:
            raise ValidationError("api_key or drone_secret required")
        if api_key:
            # careful, core-api is case-sensitively testing for Bearer...
            key_type = "Bearer" if len(api_key) == 57 else "scitran-user"
            self.headers["authorization"] = f"{key_type} {api_key}"
        # require device_type and device_label if drone
        elif not api_key and self.drone_secret:
            if not self.device_type:  # pragma: no cover
                raise ValidationError("device_type required")
            if not self.device_label:  # pragma: no cover
                raise ValidationError("device_label required")
            api_key = self._get_device_key()
            key_type = "Bearer" if len(api_key) == 57 else "scitran-user"
            self.headers["authorization"] = f"{key_type} {api_key}"

    def _get_device_key(self) -> str:
        """Return device API key for the given drone_secret (cached)."""
        drone = (self.base_url, self.device_type, self.device_label)
        if drone not in DRONE_DEVICE_KEYS:
            # limit the use of the secret only for acquiring a device api key
            assert self.drone_secret and self.device_type and self.device_label
            headers = {
                "X-Scitran-Auth": self.drone_secret,
                "X-Scitran-Method": self.device_type,
                "X-Scitran-Name": self.device_label,
            }
            kwargs: t.Any = {"headers": headers, "auth": None}
            # core-api auto-creates new device entries based on type and label
            # however, it may create conflicting ones for parallel requests...
            # FLYW-17258 intended to fix and guard against that, to no avail
            # to mitigate, add some (0-1s) jitter before the 1st connection
            if "PYTEST_CURRENT_TEST" not in os.environ:
                time.sleep(random.random())  # pragma: no cover
            # furthermore, delete redundant device entries, leaving only the 1st
            # ie. try to enforce type/label uniqueness from the client side
            type_filter = f"type={self.device_type}"
            label_filter = f"label={self.device_label}"
            query = f"filter={type_filter}&filter={label_filter}"
            url = "/api/devices"
            devices = self.get(f"{url}?{query}", **kwargs)
            for device in devices[1:]:  # type: ignore
                self.delete(f"{url}/{device['_id']}", **kwargs)
            # legacy api keys are auto-generated and returned on the response
            # TODO generate key if not exposed after devices get enhanced keys
            # NOTE caching will need rework and move to self due to expiration
            device = self.get(f"{url}/self", **kwargs)
            DRONE_DEVICE_KEYS[drone] = device["key"]
        return DRONE_DEVICE_KEYS[drone]

    @cached_property
    def core_version(self) -> str:
        """Return the Flywheel release version."""
        return self.get("/api/version").get("flywheel_release")

    @cached_property
    def core_config(self) -> dict:
        """Return the Core-API config."""
        return self.get("/api/config")

    @cached_property
    def auth_status(self) -> dict:
        """Return the client's auth status."""
        status = self.get("/api/auth/status")
        resource = "devices" if status.is_device else "users"
        status["info"] = self.get(f"/api/{resource}/self")
        return status

    def check_feature(self, feature: str) -> bool:
        """Return True if Core-API has the given feature enabled."""
        return bool(self.core_config["features"].get(feature))  # type: ignore

    def check_version(self, min_ver: str) -> bool:
        """Return True if release version is greater or equal to 'min_ver'."""
        return version.parse(self.core_version) >= version.parse(min_ver)

    def upload_device_file(
        self,
        project_id: str,
        file: t.BinaryIO,
        origin: dict | None = None,
        content_encoding: str | None = None,
    ) -> str:
        """Upload a single file using the /api/storage/files endpoint (device only)."""
        assert self.auth_status.is_device, "device authentication required"
        url = "/api/storage/files"
        origin = origin or self.auth_status.origin
        params = {
            "project_id": project_id,
            "origin_type": origin["type"],
            "origin_id": origin["id"],
            "signed_url": True,
        }
        headers = {"content-encoding": content_encoding} if content_encoding else {}
        response = self.post(url, params=params, headers=headers, raw=True)
        if response.is_success:
            upload = response.json()
            headers = upload.get("upload_headers") or {}
            if hasattr(file, "getbuffer"):
                headers["content-length"] = str(file.getbuffer().nbytes)
            else:
                headers["content-length"] = str(os.fstat(file.fileno()).st_size)
            try:

                def stream():
                    while chunk := file.read(MEGABYTE):
                        yield chunk

                self.put(
                    url=upload["upload_url"],
                    auth=httpx_anon,
                    headers=headers,
                    content=stream(),
                )
            # make sure we clean up any residue on failure
            except httpx.HTTPError:
                del_url = f"{url}/{upload['storage_file_id']}"
                self.delete(del_url, params={"ignore_storage_errors": True})
                raise
        # core's 409 means no signed url support - upload directly instead
        elif response.status_code == 409:
            del params["signed_url"]
            files = {"file": file}
            upload = self.post(url, params=params, headers=headers, files=files)
        else:
            response.raise_for_status()
        return upload["storage_file_id"]

    async def aupload_device_file(
        self,
        project_id: str,
        file: t.BinaryIO,
        origin: dict | None = None,
        content_encoding: str | None = None,
    ) -> str:
        """Upload a single file using the /api/storage/files endpoint (device only)."""
        assert self.auth_status.is_device, "device authentication required"
        url = "/api/storage/files"
        origin = origin or self.auth_status.origin
        params = {
            "project_id": project_id,
            "origin_type": origin["type"],
            "origin_id": origin["id"],
            "signed_url": True,
        }
        headers = {"content-encoding": content_encoding} if content_encoding else {}
        response = await self.apost(url, params=params, headers=headers, raw=True)
        if response.is_success:
            upload = response.json()
            headers = upload.get("upload_headers") or {}
            if hasattr(file, "getbuffer"):
                headers["content-length"] = str(file.getbuffer().nbytes)
            else:
                headers["content-length"] = str(os.fstat(file.fileno()).st_size)
            try:

                async def stream():
                    while chunk := file.read(MEGABYTE):
                        yield chunk

                await self.aput(
                    url=upload["upload_url"],
                    auth=httpx_anon,
                    headers=headers,
                    content=stream(),
                )
            # make sure we clean up any residue on failure
            except httpx.HTTPError:
                del_url = f"{url}/{upload['storage_file_id']}"
                await self.adelete(del_url, params={"ignore_storage_errors": True})
                raise
        # core's 409 means no signed url support - upload directly instead
        elif response.status_code == 409:
            del params["signed_url"]
            files = {"file": file}
            upload = await self.apost(url, params=params, headers=headers, files=files)
        else:
            response.raise_for_status()
        return upload["storage_file_id"]


def dump_useragent(*args: str, **kwargs: str) -> str:
    """Return parsable UA string for the given agent info."""
    useragent = f"fw-client/{pkg_version('fw_client')}"
    kwargs = {"platform": platform.platform()} | kwargs
    comments = list(args) + [f"{k}:{v}" if v else k for k, v in kwargs.items()]
    return f"{useragent} ({'; '.join(comments)})"


def httpx_pop_auth_header(request):
    """Pop authorization header from request to enable anonymous request."""
    request.headers.pop("authorization", None)
    return request


httpx_anon = FunctionAuth(httpx_pop_auth_header)
