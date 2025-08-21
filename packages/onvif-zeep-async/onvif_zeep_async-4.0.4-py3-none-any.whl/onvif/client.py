"""ONVIF Client."""

from __future__ import annotations

import asyncio
import datetime as dt
import logging
import os.path
from collections.abc import Callable
from typing import Any, TypeVar

import zeep.helpers
from zeep.cache import SqliteCache
from zeep.client import AsyncClient as BaseZeepAsyncClient
from zeep.proxy import AsyncServiceProxy
from zeep.wsdl import Document
from zeep.wsse.username import UsernameToken

import aiohttp
import httpx
from aiohttp import BasicAuth, ClientSession, DigestAuthMiddleware, TCPConnector
from onvif.definition import SERVICES
from onvif.exceptions import ONVIFAuthError, ONVIFError, ONVIFTimeoutError
from requests import Response

from .const import KEEPALIVE_EXPIRY
from .managers import NotificationManager, PullPointManager
from .settings import DEFAULT_SETTINGS
from .transport import ASYNC_TRANSPORT
from .types import FastDateTime, ForgivingTime
from .util import (
    create_no_verify_ssl_context,
    normalize_url,
    obscure_user_pass_url,
    path_isfile,
    strip_user_pass_url,
    utcnow,
)
from .wrappers import retry_connection_error
from .wsa import WsAddressingIfMissingPlugin
from .zeep_aiohttp import AIOHTTPTransport

logger = logging.getLogger("onvif")
logging.basicConfig(level=logging.INFO)
logging.getLogger("zeep.client").setLevel(logging.CRITICAL)

_SENTINEL = object()
_WSDL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wsdl")
_DEFAULT_TIMEOUT = 90
_PULLPOINT_TIMEOUT = 90
_CONNECT_TIMEOUT = 30
_READ_TIMEOUT = 90
_WRITE_TIMEOUT = 90
# Keepalive is set on the connector, not in ClientTimeout
_NO_VERIFY_SSL_CONTEXT = create_no_verify_ssl_context()


def safe_func(func):
    """Ensure methods to raise an ONVIFError Exception when some thing was wrong."""

    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            raise ONVIFError(err) from err

    return wrapped


class UsernameDigestTokenDtDiff(UsernameToken):
    """
    UsernameDigestToken class, with a time offset parameter that can be adjusted;
    This allows authentication on cameras without being time synchronized.
    Please note that using NTP on both end is the recommended solution,
    this should only be used in "safe" environments.
    """

    def __init__(self, user, passw, dt_diff=None, **kwargs):
        super().__init__(user, passw, **kwargs)
        # Date/time difference in datetime.timedelta
        self.dt_diff = dt_diff

    def apply(self, envelope, headers):
        old_created = self.created
        if self.created is None:
            self.created = dt.datetime.now(tz=dt.timezone.utc).replace(tzinfo=None)
        if self.dt_diff is not None:
            self.created += self.dt_diff
        result = super().apply(envelope, headers)
        self.created = old_created
        return result


_DOCUMENT_CACHE: dict[str, Document] = {}

original_load = Document.load


class DocumentWithDeferredLoad(Document):
    def load(self, *args: Any, **kwargs: Any) -> None:
        """Deferred load of the document."""

    def original_load(self, *args: Any, **kwargs: Any) -> None:
        """Original load of the document."""
        return original_load(self, *args, **kwargs)


class AsyncTransportProtocolErrorHandler(AIOHTTPTransport):
    """
    Retry on remote protocol error.

    http://datatracker.ietf.org/doc/html/rfc2616#section-8.1.4 allows the server
    # to close the connection at any time, we treat this as a normal and try again
    # once since
    """

    @retry_connection_error(
        attempts=2, exception=aiohttp.ServerDisconnectedError, backoff=0
    )
    async def post(
        self, address: str, message: str, headers: dict[str, str]
    ) -> httpx.Response:
        return await super().post(address, message, headers)

    @retry_connection_error(
        attempts=2, exception=aiohttp.ServerDisconnectedError, backoff=0
    )
    async def get(
        self,
        address: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        return await super().get(address, params, headers)

    @retry_connection_error(
        attempts=2, exception=aiohttp.ServerDisconnectedError, backoff=0
    )
    async def post_xml(
        self, address: str, envelope: Any, headers: dict[str, str]
    ) -> Response:
        return await super().post_xml(address, envelope, headers)


async def _cached_document(url: str) -> Document:
    """Load external XML document from disk."""
    if url in _DOCUMENT_CACHE:
        return _DOCUMENT_CACHE[url]
    loop = asyncio.get_event_loop()

    def _load_document() -> DocumentWithDeferredLoad:
        document = DocumentWithDeferredLoad(
            url, ASYNC_TRANSPORT, settings=DEFAULT_SETTINGS
        )
        # Override the default datetime type to use FastDateTime
        # This is a workaround for the following issue:
        # https://github.com/mvantellingen/python-zeep/pull/1370
        schema = document.types.documents.get_by_namespace(
            "http://www.w3.org/2001/XMLSchema", False
        )[0]
        logger.debug("Overriding default datetime type to use FastDateTime")
        instance = FastDateTime(is_global=True)
        schema.register_type(FastDateTime._default_qname, instance)

        logger.debug("Overriding default time type to use ForgivingTime")
        instance = ForgivingTime(is_global=True)
        schema.register_type(ForgivingTime._default_qname, instance)

        document.types.add_documents([None], url)
        # Perform the original load
        document.original_load(url)
        return document

    document = await loop.run_in_executor(None, _load_document)
    _DOCUMENT_CACHE[url] = document
    return document


_T = TypeVar("_T")


def handle_snapshot_errors(func: Callable[..., _T]) -> Callable[..., _T]:
    """Decorator to handle snapshot URI errors."""

    async def wrapper(self, uri: str, *args: Any, **kwargs: Any) -> _T:
        try:
            return await func(self, uri, *args, **kwargs)
        except TimeoutError as error:
            raise ONVIFTimeoutError(
                f"Timed out fetching {obscure_user_pass_url(uri)}: {error}"
            ) from error
        except aiohttp.ClientError as error:
            raise ONVIFError(
                f"Error fetching {obscure_user_pass_url(uri)}: {error}"
            ) from error

    return wrapper


class ZeepAsyncClient(BaseZeepAsyncClient):
    """Overwrite create_service method to be async."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_ns_prefix("wsnt", "http://docs.oasis-open.org/wsn/b-2")
        self.set_ns_prefix("wsa", "http://www.w3.org/2005/08/addressing")

    def create_service(self, binding_name, address):
        """
        Create a new ServiceProxy for the given binding name and address.
        :param binding_name: The QName of the binding
        :param address: The address of the endpoint
        """
        try:
            binding = self.wsdl.bindings[binding_name]
        except KeyError:
            raise ValueError(
                f"No binding found with the given QName. Available bindings "
                f"are: {', '.join(self.wsdl.bindings.keys())}"
            ) from None
        return AsyncServiceProxy(self, binding, address=address)


class ONVIFService:
    """
    Python Implemention for ONVIF Service.
    Services List:
        DeviceMgmt DeviceIO Event AnalyticsDevice Display Imaging Media
        PTZ Receiver RemoteDiscovery Recording Replay Search Extension

    >>> from onvif import ONVIFService
    >>> device_service = ONVIFService('http://192.168.0.112/onvif/device_service',
    ...                           'admin', 'foscam',
    ...                           '/etc/onvif/wsdl/devicemgmt.wsdl')
    >>> ret = device_service.GetHostname()
    >>> print ret.FromDHCP
    >>> print ret.Name
    >>> device_service.SetHostname(dict(Name='newhostname'))
    >>> ret = device_service.GetSystemDateAndTime()
    >>> print ret.DaylightSavings
    >>> print ret.TimeZone
    >>> dict_ret = device_service.to_dict(ret)
    >>> print dict_ret['TimeZone']

    There are two ways to pass parameter to services methods
    1. Dict
        params = {'Name': 'NewHostName'}
        device_service.SetHostname(params)
    2. Type Instance
        params = device_service.create_type('SetHostname')
        params.Hostname = 'NewHostName'
        device_service.SetHostname(params)
    """

    @safe_func
    def __init__(
        self,
        xaddr: str,
        user: str | None,
        passwd: str | None,
        url: str,
        encrypt=True,
        no_cache=False,
        dt_diff=None,
        binding_name="",
        binding_key="",
        read_timeout: int | None = None,
        write_timeout: int | None = None,
    ) -> None:
        if not path_isfile(url):
            raise ONVIFError(f"{url} doesn`t exist!")

        self.url = url
        self.xaddr = xaddr
        self.binding_key = binding_key
        # Set soap header for authentication
        self.user = user
        self.passwd = passwd
        # Indicate wether password digest is needed
        self.encrypt = encrypt
        self.dt_diff = dt_diff
        self.binding_name = binding_name
        # Create soap client
        self._connector = TCPConnector(
            ssl=_NO_VERIFY_SSL_CONTEXT,
            keepalive_timeout=KEEPALIVE_EXPIRY,
        )
        self._session = ClientSession(
            connector=self._connector,
            timeout=aiohttp.ClientTimeout(
                total=_DEFAULT_TIMEOUT,
                connect=_CONNECT_TIMEOUT,
                sock_read=read_timeout or _READ_TIMEOUT,
            ),
        )
        self.transport = (
            AsyncTransportProtocolErrorHandler(
                session=self._session,
                verify_ssl=False,
            )
            if no_cache
            else AIOHTTPTransport(
                session=self._session,
                verify_ssl=False,
                cache=SqliteCache(),
            )
        )
        self.document: Document | None = None
        self.zeep_client_authless: ZeepAsyncClient | None = None
        self.ws_client_authless: AsyncServiceProxy | None = None
        self.zeep_client: ZeepAsyncClient | None = None
        self.ws_client: AsyncServiceProxy | None = None
        self.create_type: Callable | None = None
        self.loop = asyncio.get_event_loop()

    async def setup(self):
        """Setup the transport."""
        settings = DEFAULT_SETTINGS
        binding_name = self.binding_name
        wsse = UsernameDigestTokenDtDiff(
            self.user, self.passwd, dt_diff=self.dt_diff, use_digest=self.encrypt
        )
        self.document = await _cached_document(self.url)
        self.zeep_client_authless = ZeepAsyncClient(
            wsdl=self.document,
            transport=self.transport,
            settings=settings,
            plugins=[WsAddressingIfMissingPlugin()],
        )
        self.ws_client_authless = self.zeep_client_authless.create_service(
            binding_name, self.xaddr
        )
        self.zeep_client = ZeepAsyncClient(
            wsdl=self.document,
            wsse=wsse,
            transport=self.transport,
            settings=settings,
            plugins=[WsAddressingIfMissingPlugin()],
        )
        self.ws_client = self.zeep_client.create_service(binding_name, self.xaddr)
        namespace = binding_name[binding_name.find("{") + 1 : binding_name.find("}")]
        available_ns = self.zeep_client.namespaces
        active_ns = (
            list(available_ns.keys())[list(available_ns.values()).index(namespace)]
            or "ns0"
        )
        self.create_type = lambda x: self.zeep_client.get_element(active_ns + ":" + x)()

    async def close(self):
        """Close the transport."""
        await self.transport.aclose()
        await self._session.close()
        await self._connector.close()

    @staticmethod
    @safe_func
    def to_dict(zeepobject):
        """Convert a WSDL Type instance into a dictionary."""
        return {} if zeepobject is None else zeep.helpers.serialize_object(zeepobject)

    def __getattr__(self, name):
        """
        Call the real onvif Service operations,
        See the official wsdl definition for the
        APIs detail(API name, request parameters,
        response parameters, parameter types, etc...)
        """

        def service_wrapper(func):
            """Wrap service call."""

            @safe_func
            def wrapped(params=None):
                def call(params=None):
                    # No params
                    if params is None:
                        params = {}
                    else:
                        params = ONVIFService.to_dict(params)
                    try:
                        ret = func(**params)
                    except TypeError:
                        ret = func(params)
                    return ret

                return call(params)

            return wrapped

        builtin = name.startswith("__") and name.endswith("__")
        if builtin:
            return self.__dict__[name]
        if name.startswith("authless_"):
            return service_wrapper(getattr(self.ws_client_authless, name.split("_")[1]))
        return service_wrapper(getattr(self.ws_client, name))


class ONVIFCamera:
    """
    Python Implementation ONVIF compliant device
    This class integrates onvif services

    adjust_time parameter allows authentication on cameras without being time synchronized.
    Please note that using NTP on both end is the recommended solution,
    this should only be used in "safe" environments.
    Also, this cannot be used on AXIS camera, as every request is authenticated, contrary to ONVIF standard

    >>> from onvif import ONVIFCamera
    >>> mycam = ONVIFCamera('192.168.0.112', 80, 'admin', '12345')
    >>> mycam.devicemgmt.GetServices(False)
    >>> media_service = mycam.create_media_service()
    >>> ptz_service = mycam.create_ptz_service()
    # Get PTZ Configuration:
    >>> mycam.ptz.GetConfiguration()
    # Another way:
    >>> ptz_service.GetConfiguration()
    """

    def __init__(
        self,
        host: str,
        port: int,
        user: str | None,
        passwd: str | None,
        wsdl_dir: str = _WSDL_PATH,
        encrypt=True,
        no_cache=False,
        adjust_time=False,
    ) -> None:
        os.environ.pop("http_proxy", None)
        os.environ.pop("https_proxy", None)
        self.host = host
        self.port = int(port)
        self.user = user
        self.passwd = passwd
        self.wsdl_dir = wsdl_dir
        self.encrypt = encrypt
        self.no_cache = no_cache
        self.adjust_time = adjust_time
        self.dt_diff = None
        self.xaddrs = {}
        self._has_broken_relative_timestamps: bool = False
        self._capabilities: dict[str, Any] | None = None

        # Active service client container
        self.services: dict[tuple[str, str | None], ONVIFService] = {}

        self.to_dict = ONVIFService.to_dict

        self._snapshot_uris = {}
        self._snapshot_connector = TCPConnector(ssl=_NO_VERIFY_SSL_CONTEXT)
        self._snapshot_client = ClientSession(connector=self._snapshot_connector)

    async def get_capabilities(self) -> dict[str, Any]:
        """Get device capabilities."""
        if self._capabilities is None:
            await self.update_xaddrs()
        return self._capabilities

    async def update_xaddrs(self):
        """Update xaddrs for services."""
        self.dt_diff = None
        devicemgmt = await self.create_devicemgmt_service()
        if self.adjust_time:
            try:
                sys_date = await devicemgmt.authless_GetSystemDateAndTime()
            except zeep.exceptions.Fault:
                # Looks like we should try with auth
                sys_date = await devicemgmt.GetSystemDateAndTime()
            cdate = sys_date.UTCDateTime
            cam_date = dt.datetime(
                cdate.Date.Year,
                cdate.Date.Month,
                cdate.Date.Day,
                cdate.Time.Hour,
                cdate.Time.Minute,
                cdate.Time.Second,
            )
            self.dt_diff = cam_date - dt.datetime.utcnow()
            await devicemgmt.close()
            del self.services[devicemgmt.binding_key]
            devicemgmt = await self.create_devicemgmt_service()

        # Get XAddr of services on the device
        self.xaddrs = {}
        capabilities = await devicemgmt.GetCapabilities({"Category": "All"})
        for name in capabilities:
            capability = capabilities[name]
            try:
                if name.lower() in SERVICES and capability is not None:
                    namespace = SERVICES[name.lower()]["ns"]
                    self.xaddrs[namespace] = normalize_url(capability["XAddr"])
            except Exception:
                logger.exception("Unexpected service type")
        try:
            self._capabilities = self.to_dict(capabilities)
        except Exception:
            logger.exception("Failed to parse capabilities")

    def has_broken_relative_time(
        self,
        expected_interval: dt.timedelta,
        current_time: dt.datetime | None,
        termination_time: dt.datetime | None,
    ) -> bool:
        """Mark timestamps as broken if a subscribe request returns an unexpected result."""
        logger.debug(
            "%s: Checking for broken relative timestamps: expected_interval: %s, current_time: %s, termination_time: %s",
            self.host,
            expected_interval,
            current_time,
            termination_time,
        )
        if not current_time:
            logger.debug("%s: Device returned no current time", self.host)
            return False
        if not termination_time:
            logger.debug("%s: Device returned no current time", self.host)
            return False
        if current_time.tzinfo is None:
            logger.debug(
                "%s: Device returned no timezone info for current time", self.host
            )
            return False
        if termination_time.tzinfo is None:
            logger.debug(
                "%s: Device returned no timezone info for termination time", self.host
            )
            return False
        actual_interval = termination_time - current_time
        if abs(actual_interval.total_seconds()) < (
            expected_interval.total_seconds() / 2
        ):
            logger.debug(
                "%s: Broken relative timestamps detected, switching to absolute timestamps: expected interval: %s, actual interval: %s",
                self.host,
                expected_interval,
                actual_interval,
            )
            self._has_broken_relative_timestamps = True
            return True
        logger.debug(
            "%s: Relative timestamps OK: expected interval: %s, actual interval: %s",
            self.host,
            expected_interval,
            actual_interval,
        )
        return False

    def get_next_termination_time(self, duration: dt.timedelta) -> str:
        """Calculate subscription absolute termination time."""
        if not self._has_broken_relative_timestamps:
            return f"PT{int(duration.total_seconds())}S"
        absolute_time: dt.datetime = utcnow() + duration
        if dt_diff := self.dt_diff:
            absolute_time += dt_diff
        return absolute_time.isoformat(timespec="seconds").replace("+00:00", "Z")

    async def create_pullpoint_manager(
        self,
        interval: dt.timedelta,
        subscription_lost_callback: Callable[[], None],
    ) -> PullPointManager:
        """Create a pullpoint manager."""
        manager = PullPointManager(self, interval, subscription_lost_callback)
        await manager.start()
        return manager

    async def create_notification_manager(
        self,
        address: str,
        interval: dt.timedelta,
        subscription_lost_callback: Callable[[], None],
    ) -> NotificationManager:
        """Create a notification manager."""
        manager = NotificationManager(
            self, address, interval, subscription_lost_callback
        )
        await manager.start()
        return manager

    async def close(self) -> None:
        """Close all transports."""
        await self._snapshot_client.close()
        await self._snapshot_connector.close()
        for service in self.services.values():
            await service.close()

    async def get_snapshot_uri(self, profile_token: str) -> str:
        """Get the snapshot uri for a given profile."""
        uri = self._snapshot_uris.get(profile_token, _SENTINEL)
        if uri is _SENTINEL:
            media_service = await self.create_media_service()
            req = media_service.create_type("GetSnapshotUri")
            req.ProfileToken = profile_token
            uri = None
            try:
                result = await media_service.GetSnapshotUri(req)
            except zeep.exceptions.Fault as error:
                logger.warning(
                    "%s: Failed to get snapshot URI for profile %s: %s",
                    self.host,
                    profile_token,
                    error,
                )
            else:
                try:
                    uri = normalize_url(result.Uri)
                except (AttributeError, KeyError):
                    # AttributeError is raised when result.Uri is missing
                    # https://github.com/home-assistant/core/issues/135494
                    logger.warning(
                        "%s: The device returned an invalid snapshot URI", self.host
                    )
            self._snapshot_uris[profile_token] = uri
        return uri

    async def get_snapshot(
        self, profile_token: str, basic_auth: bool = False
    ) -> bytes | None:
        """Get a snapshot image from the camera."""
        uri = await self.get_snapshot_uri(profile_token)
        if uri is None:
            return None

        auth: BasicAuth | None = None
        middlewares: tuple[DigestAuthMiddleware, ...] | None = None

        if self.user and self.passwd:
            if basic_auth:
                auth = BasicAuth(self.user, self.passwd)
            else:
                # Use DigestAuthMiddleware for digest auth
                middlewares = (DigestAuthMiddleware(self.user, self.passwd),)

        response = await self._try_snapshot_uri(uri, auth=auth, middlewares=middlewares)
        content = await self._try_read_snapshot_content(uri, response)

        # If the request fails with a 401, strip user/pass from URL and retry
        if (
            response.status == 401
            and (stripped_uri := strip_user_pass_url(uri))
            and stripped_uri != uri
        ):
            response = await self._try_snapshot_uri(
                stripped_uri, auth=auth, middlewares=middlewares
            )
            content = await self._try_read_snapshot_content(uri, response)

        if response.status == 401:
            raise ONVIFAuthError(f"Failed to authenticate to {uri}")

        if response.status < 300:
            return content

        return None

    @handle_snapshot_errors
    async def _try_read_snapshot_content(
        self,
        uri: str,
        response: aiohttp.ClientResponse,
    ) -> bytes:
        """Try to read the snapshot URI."""
        return await response.read()

    @handle_snapshot_errors
    async def _try_snapshot_uri(
        self,
        uri: str,
        auth: BasicAuth | None = None,
        middlewares: tuple[DigestAuthMiddleware, ...] | None = None,
    ) -> aiohttp.ClientResponse:
        return await self._snapshot_client.get(uri, auth=auth, middlewares=middlewares)

    def get_definition(
        self, name: str, port_type: str | None = None
    ) -> tuple[str, str, str]:
        """Returns xaddr and wsdl of specified service"""
        # Check if the service is supported
        if name not in SERVICES:
            raise ONVIFError(f"Unknown service {name}")
        wsdl_file = SERVICES[name]["wsdl"]
        namespace = SERVICES[name]["ns"]

        binding_name = "{{{}}}{}".format(namespace, SERVICES[name]["binding"])

        if port_type:
            namespace += "/" + port_type

        wsdlpath = os.path.join(self.wsdl_dir, wsdl_file)
        if not path_isfile(wsdlpath):
            raise ONVIFError(f"No such file: {wsdlpath}")

        # XAddr for devicemgmt is fixed:
        if name == "devicemgmt":
            xaddr = "{}:{}/onvif/device_service".format(
                self.host
                if (self.host.startswith("http://") or self.host.startswith("https://"))
                else f"http://{self.host}",
                self.port,
            )
            return xaddr, wsdlpath, binding_name

        # Get other XAddr
        xaddr = self.xaddrs.get(namespace)
        if not xaddr:
            raise ONVIFError(
                f"Device doesn`t support service: {name} with namespace {namespace}"
            )

        return xaddr, wsdlpath, binding_name

    async def create_onvif_service(
        self,
        name: str,
        port_type: str | None = None,
        read_timeout: int | None = None,
        write_timeout: int | None = None,
    ) -> ONVIFService:
        """Create ONVIF service client"""
        name = name.lower()
        # Don't re-create bindings if the xaddr remains the same.
        # The xaddr can change when a new PullPointSubscription is created.
        binding_key = (name, port_type)

        xaddr, wsdl_file, binding_name = self.get_definition(name, port_type)

        existing_service = self.services.get(binding_key)
        if existing_service:
            if existing_service.xaddr == xaddr:
                return existing_service
            else:
                # Close the existing service since it's no longer valid.
                # This can happen when a new PullPointSubscription is created.
                logger.debug(
                    "Closing service %s with %s", binding_key, existing_service.xaddr
                )
                # Hold a reference to the task so it doesn't get
                # garbage collected before it completes.
                await existing_service.close()
            self.services.pop(binding_key)

        logger.debug("Creating service %s with %s", binding_key, xaddr)

        service = ONVIFService(
            xaddr,
            self.user,
            self.passwd,
            wsdl_file,
            self.encrypt,
            no_cache=self.no_cache,
            dt_diff=self.dt_diff,
            binding_name=binding_name,
            binding_key=binding_key,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
        )
        await service.setup()

        self.services[binding_key] = service

        return service

    async def create_devicemgmt_service(self) -> ONVIFService:
        """Service creation helper."""
        return await self.create_onvif_service("devicemgmt")

    async def create_media_service(self) -> ONVIFService:
        """Service creation helper."""
        return await self.create_onvif_service("media")

    async def create_ptz_service(self) -> ONVIFService:
        """Service creation helper."""
        return await self.create_onvif_service("ptz")

    async def create_imaging_service(self) -> ONVIFService:
        """Service creation helper."""
        return await self.create_onvif_service("imaging")

    async def create_deviceio_service(self) -> ONVIFService:
        """Service creation helper."""
        return await self.create_onvif_service("deviceio")

    async def create_events_service(self) -> ONVIFService:
        """Service creation helper."""
        return await self.create_onvif_service("events")

    async def create_analytics_service(self) -> ONVIFService:
        """Service creation helper."""
        return await self.create_onvif_service("analytics")

    async def create_recording_service(self) -> ONVIFService:
        """Service creation helper."""
        return await self.create_onvif_service("recording")

    async def create_search_service(self) -> ONVIFService:
        """Service creation helper."""
        return await self.create_onvif_service("search")

    async def create_replay_service(self) -> ONVIFService:
        """Service creation helper."""
        return await self.create_onvif_service("replay")

    async def create_pullpoint_service(self) -> ONVIFService:
        """Service creation helper."""
        return await self.create_onvif_service(
            "pullpoint",
            port_type="PullPointSubscription",
            read_timeout=_PULLPOINT_TIMEOUT,
            write_timeout=_PULLPOINT_TIMEOUT,
        )

    async def create_notification_service(self) -> ONVIFService:
        """Service creation helper."""
        return await self.create_onvif_service("notification")

    async def create_subscription_service(
        self, port_type: str | None = None
    ) -> ONVIFService:
        """Service creation helper."""
        return await self.create_onvif_service("subscription", port_type=port_type)

    async def create_receiver_service(self) -> ONVIFService:
        """Service creation helper."""
        return await self.create_onvif_service("receiver")
