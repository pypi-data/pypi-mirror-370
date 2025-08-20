import pydantic
from _typeshed import Incomplete
from litestar import Litestar, Request, Response
from litestar.controller import Controller
from litestar.middleware import MiddlewareProtocol
from litestar.middleware.logging import LoggingMiddleware, LoggingMiddlewareConfig
from litestar.openapi.spec import SecurityRequirement as SecurityRequirement
from litestar.types import ASGIApp as ASGIApp, Receive as Receive, Scope as Scope, Send as Send
from litestar.types.callable_types import LifespanHook as LifespanHook
from litestar.types.composite_types import Middleware as Middleware
from pydantic import BaseModel
from tlc import __git_revision__ as __git_revision__, __version__ as __version__
from tlc.core import ObjectRegistry as ObjectRegistry, Table as Table
from tlc.core.json_helper import JsonHelper as JsonHelper
from tlc.core.object import Object as Object
from tlc.core.object_type_registry import MalformedContentError as MalformedContentError, NotRegisteredError as NotRegisteredError, ObjectTypeRegistry as ObjectTypeRegistry
from tlc.core.objects.mutable_object import MutableObject as MutableObject
from tlc.core.objects.mutable_objects.configuration import Configuration as Configuration
from tlc.core.objects.tables.system_tables.indexing_tables.config_indexing_table import ConfigIndexingTable as ConfigIndexingTable
from tlc.core.objects.tables.system_tables.indexing_tables.run_indexing_table import RunIndexingTable as RunIndexingTable
from tlc.core.objects.tables.system_tables.indexing_tables.table_indexing_table import TableIndexingTable as TableIndexingTable
from tlc.core.objects.tables.system_tables.log_table import LogTable as LogTable
from tlc.core.url import Url as Url, UrlAliasRegistry as UrlAliasRegistry
from tlc.core.url_adapter import IfExistsOption as IfExistsOption
from tlc.core.url_adapter_registry import UrlAdapterRegistry as UrlAdapterRegistry
from tlc.core.utils.telemetry import Telemetry as Telemetry
from tlc.core.utils.track_project_metadata import compute_project_usage_metadata as compute_project_usage_metadata
from tlc.service.authentication import ActivateJwtOnApiKeyMiddleware as ActivateJwtOnApiKeyMiddleware, JwtAuthenticationMiddleware as JwtAuthenticationMiddleware, TimestampHmacAuthenticationMiddleware as TimestampHmacAuthenticationMiddleware, TimestampSkewException as TimestampSkewException
from tlc.service.external_data_transcoders import get_transcoder as get_transcoder
from tlc.service.tlc_lrucache import LRUCacheStore as LRUCacheStore, LRUCacheStoreConfig as LRUCacheStoreConfig
from tlc.service.watch_manager import is_watch_enabled as is_watch_enabled, start_watch_subprocess as start_watch_subprocess, stop_watch_subprocess as stop_watch_subprocess
from tlccli.subcommands.ngrok_helper import NGrokHelper
from tlcsaas.transaction import InsufficientCredits
from typing import Any, Literal, TypeVar

logger: Incomplete

class LitestarStateConstants:
    """Constants for the Litestar state."""
    HOST_IP: str
    OBJECT_SERVICE_RUNNING_URLS: str
    NGROK_OBJECT_SERVICE_URL: str

def internal_server_error_handler(request: Request, exception: Exception) -> Response:
    """Catch-all for application errors."""
def insufficient_credits_handler(request: Request, exception: InsufficientCredits) -> Response:
    """Handler for insufficient credits."""
def timestamp_skew_handler(request: Request, exception: TimestampSkewException) -> Response:
    """Handler for timestamp skew."""
def resolve_cache_timeout() -> int: ...

class TLCObject(pydantic.BaseModel):
    """In-flight representation of a TLCObject."""
    type: str
    url: str | None
    model_config: Incomplete

class TLCPatchOptions(pydantic.BaseModel):
    """TLC patch request."""
    delete_old_url: bool
    model_config: Incomplete

class TLCPatchRequest(pydantic.BaseModel):
    """In-flight representation of a patch request for a TLCObject."""
    patch_object: TLCObject
    patch_options: TLCPatchOptions
    model_config: Incomplete

class ReindexRequest(pydantic.BaseModel):
    '''Request model for re-indexing operations.

    :param force: Whether to force re-indexing to disregard the state of the current index timestamp files.
    :param types: The types of objects to reindex. Defaults to "all".
    '''
    force: bool
    types: list[Literal['run', 'table', 'config', 'all']]
    model_config: Incomplete

class RollbackDeleteContext:
    """A context manager for rollback object creation without interfering with InsufficientCredits."""
    def __init__(self, url: Url) -> None: ...
    def rollback(self) -> None: ...
    def __enter__(self) -> RollbackDeleteContext: ...
    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> Literal[False]:
        """Exit the context, performing rollback if not committed and handling exceptions."""

def get_ip_addresses() -> list[str]: ...
def get_running_urls() -> list[str]: ...

profiler: Incomplete

def format_yaml_for_logging(data: dict | list, indent: int = 4) -> str: ...
def open_in_web_browser(url: str) -> None: ...
def open_dashboard_in_web_browser(app: Litestar) -> None: ...
async def startup(app: Litestar) -> None:
    """Setup HTTP client for connecting to 3LC Data Service"""
async def shutdown(app: Litestar) -> None:
    """Perform any required cleanup before terminating the application"""
async def root() -> Response:
    """Root endpoint of the service"""
async def live() -> Response:
    """Endpoint for checking if the service is running."""

class ObjectServiceFeatures(BaseModel):
    post_external_data: bool

class ObjectServiceUserInfo(BaseModel):
    user_id: str
    tenant_id: str
    user_full_name: str
    user_email: str
    tenant_name: str

class DashboardAnnotations(BaseModel):
    banner_icon_url: str
    banner_background_color: str
    banner_message: str
    title_message: str

def get_status() -> dict[str, Any]:
    """Returns status of the service"""

last_lru_stats: dict[str, Any] | None

def get_last_lru_stats() -> dict[str, Any] | None: ...
async def status(request: Request) -> dict[str, Any]:
    """Returns status of the service"""

class ETagMiddleware(MiddlewareProtocol):
    """A middleware that may serve 304 not modified responses based on ETag headers.

    Only affects endpoints/responses that have previously been served with ETag. Other requests are passed through.

    If the request contains an If-None-Match header with the same ETag as the previous response, a 304 Not Modified
    response is returned.
    """
    app: Incomplete
    def __init__(self, app: ASGIApp, **kwargs: Any) -> None: ...
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...

class ObjectRoutesController(Controller):
    """Controller for all object-related routes"""
    path: str
    cache_time_out: Incomplete
    async def get_encoded_url(self, encoded_url: str, request: Request) -> Response[TLCObject]: ...
    async def get_encoded_url_rows(self, encoded_url: str, attribute: str, request: Request) -> Response[bytes]: ...
    async def list_urls(self) -> list[str]:
        """Return all the objects.

        Returns:
            list[Any]: List of the URLs of all the objects.
        """
    async def request_reindex(self, data: ReindexRequest) -> Response:
        """Request a reindex operation.

        :param data: The reindex request parameters.
        :returns: Response with status message.
        """
    async def new_object(self, data: TLCObject) -> Response:
        """Create a new object.

        :param data: Object to be created
        :returns: Empty response. URL of the created object will be in the 'Location' field of the response headers.
        """
    async def delete_object(self, encoded_url: str) -> None:
        """Delete an object.

        :param encoded_url: URL of the object to be deleted.
        :raises: HTTPException if no object can be found at the URL.
        """
    async def update_object(self, encoded_url: str, data: TLCPatchRequest) -> Response:
        """Update the attributes of an object.


        Raises:
            HTTPException: If the object type of `obj_in` does not match the
            type of the object at `object_url`.
        """

class ExternalDataRoutesController(Controller):
    """Controller for all external data-related routes"""
    path: str
    cache_time_out: Incomplete
    async def get_encoded_url(self, encoded_url: str) -> bytes: ...
    async def post_encoded_url(self, request: Request, owner_url: str, base_name: str, extension: str) -> Response:
        """Write a new file with given binary contents.

        :param request: The request object.
        :param owner_url: The URL of the tlc Object that owns the file. Currently only support Table owners, data will
            be written in the table's bulk data folder.
        :param base_name: The base name of the file or folder to be created. Used to provide more context to the
            filename.
        :param extension: The extension of the file.

        :returns: A response with a 201 status code and a Location header pointing to the newly created file.
        """
    async def get_encoded_url_binary_contents(self, encoded_url: str, format: str) -> Response: ...

class SettingsRoutesController(Controller):
    """Controller for all settings-related routes"""
    path: str
    async def get_settings_key_value(self, settings_scope: str, settings_key: str) -> Response: ...
    async def put_settings_key_value(self, request: Request, settings_scope: str, settings_key: str) -> Response:
        """Create or update the value for a setting by key.

        :param request: The request object.
        :param settings_scope: The scope of the setting.
        :param settings_key: The key for the setting.
        """
    async def delete_settings_key_value(self, settings_scope: str, settings_key: str) -> None: ...

class TLCCustomLoggingMiddleware(LoggingMiddleware):
    """Custom middleware to log object service requests and responses.

    Logs request and response data to loglevel.INFO, together with the time it takes to complete the request.
    """
    def __init__(self, app: ASGIApp, config: LoggingMiddlewareConfig) -> None: ...
    async def log_request(self, scope: Scope, receive: Receive) -> None:
        """Record the start time and log the request data."""
    def log_response(self, scope: Scope) -> None:
        """Measure elapsed time and log the response data."""
    def log_message(self, values: dict[str, Any]) -> None:
        """Log a message.

        This is a copy of the superclass' method, with special case handling of the /status endpoint, and url decoding
        of the path.

        :param values: Extract values to log.
        :returns: None
        """

class NGrokOutputAdaptor:
    """Helper class to format output from NGrokHelper for the Object Service."""
    ngrok_helper: Incomplete
    role: Incomplete
    def __init__(self, role: str, ngrok_helper: NGrokHelper) -> None: ...
    async def output_public_url(self, app: Litestar) -> None: ...
T = TypeVar('T')

def create_litestar_app(host: str, port: int, use_ngrok: bool, dashboard: bool = False, after_startup_handler: list[LifespanHook] | LifespanHook | None = None, after_shutdown_handler: list[LifespanHook] | LifespanHook | None = None) -> Litestar: ...
