"""
Type definitions for the Finalsa Common Lambda library.

This module contains all the type hints and protocols used throughout the library
to ensure type safety and better IDE support.
"""

import logging

# Forward references
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
    runtime_checkable,
)

from typing_extensions import NotRequired, ParamSpec

# Type variables
T = TypeVar('T')
P = ParamSpec('P')
ReturnType = TypeVar('ReturnType')

# Basic AWS Lambda types
LambdaEvent = Dict[str, Any]
LambdaContext = Any  # AWS Lambda context object
LambdaResponse = Union[Dict[str, Any], List[Dict[str, Any]]]

# HTTP related types
HttpMethod = Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
HttpStatusCode = int
HttpHeaders = Dict[str, str]
HttpQueryParams = Dict[str, Union[str, List[str]]]
HttpPathParams = Dict[str, str]
HttpBody = Union[str, Dict[str, Any], List[Any], None]

class HttpEventDict(TypedDict):
    """AWS API Gateway HTTP event structure."""
    httpMethod: HttpMethod
    path: str
    headers: NotRequired[HttpHeaders]
    body: NotRequired[Optional[str]]
    queryStringParameters: NotRequired[Optional[HttpQueryParams]]
    pathParameters: NotRequired[Optional[HttpPathParams]]
    resource: NotRequired[str]
    requestContext: NotRequired[Dict[str, Any]]
    multiValueHeaders: NotRequired[Dict[str, List[str]]]
    multiValueQueryStringParameters: NotRequired[Dict[str, List[str]]]
    isBase64Encoded: NotRequired[bool]

class HttpResponseDict(TypedDict):
    """AWS API Gateway HTTP response structure."""
    statusCode: HttpStatusCode
    headers: HttpHeaders
    body: str
    multiValueHeaders: NotRequired[Dict[str, List[str]]]
    isBase64Encoded: NotRequired[bool]

# SQS related types
class SqsRecordDict(TypedDict, total=False):
    """SQS record structure."""
    messageId: str
    receiptHandle: str
    body: str
    attributes: Dict[str, str]
    messageAttributes: Dict[str, Any]
    md5OfBody: str
    eventSource: Literal['aws:sqs']
    eventSourceARN: str
    awsRegion: str

class SqsEventDict(TypedDict):
    """SQS event structure."""
    Records: List[SqsRecordDict]


if TYPE_CHECKING:
    from finalsa.common.lambdas.http.HttpResponse import HttpResponse

# Handler function types
HttpHandlerFunc = Callable[..., Union[Dict[str, Any], 'HttpResponse', None]]
SqsHandlerFunc = Callable[..., Union[Dict[str, Any], str, None]]
GenericHandlerFunc = Union[HttpHandlerFunc, SqsHandlerFunc]

# Decorator types
HttpDecorator = Callable[[HttpHandlerFunc], HttpHandlerFunc]
SqsDecorator = Callable[[SqsHandlerFunc], SqsHandlerFunc]

# Meta information types
class HttpMetaDict(TypedDict, total=False):
    """HTTP request metadata."""
    correlation_id: str
    trace_id: str
    span_id: str
    user_id: Optional[str]
    authorization: Optional[str]
    timestamp: str
    request_id: str

class SqsMetaDict(TypedDict, total=False):
    """SQS message metadata."""
    correlation_id: str
    trace_id: str
    span_id: str
    message_id: str
    receipt_handle: str
    timestamp: str
    retry_count: int
    topic: str

# Configuration types
class AppConfigDict(TypedDict, total=False):
    """Application configuration."""
    app_name: str
    log_level: str
    aws_region: str
    environment: str
    timeout: int
    memory_size: int

# Error types
class ErrorResponseDict(TypedDict):
    """Standard error response structure."""
    error: str
    message: str
    details: Optional[Dict[str, Any]]
    timestamp: str
    correlation_id: Optional[str]

# Protocol definitions
@runtime_checkable
class HandlerProtocol(Protocol):
    """Protocol for handler functions."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Handler function signature."""
        ...

@runtime_checkable
class AppEntryProtocol(Protocol):
    """Protocol for AppEntry objects."""

    app_name: Optional[str]
    logger: logging.Logger
    sqs: 'SqsHandlerProtocol'
    http: 'HttpHandlerProtocol'

    def execute(self, event: LambdaEvent, context: Optional[LambdaContext] = None) -> LambdaResponse:
        """Execute the handler for the given event."""
        ...

@runtime_checkable
class HttpHandlerProtocol(Protocol):
    """Protocol for HTTP handlers."""

    def get(self, path: str) -> HttpDecorator:
        """Register GET handler."""
        ...

    def post(self, path: str) -> HttpDecorator:
        """Register POST handler."""
        ...

    def put(self, path: str) -> HttpDecorator:
        """Register PUT handler."""
        ...

    def delete(self, path: str) -> HttpDecorator:
        """Register DELETE handler."""
        ...

    def process(self, event: HttpEventDict, context: LambdaContext) -> HttpResponseDict:
        """Process HTTP event."""
        ...

@runtime_checkable
class SqsHandlerProtocol(Protocol):
    """Protocol for SQS handlers."""

    def handler(self, topic: str, retries: int = 0) -> SqsDecorator:
        """Register SQS handler for specific topic."""
        ...

    def default(self, retries: int = 0) -> SqsDecorator:
        """Register default SQS handler."""
        ...

    def process(self, event: SqsEventDict, context: LambdaContext) -> List[Optional[Dict[str, Any]]]:
        """Process SQS event."""
        ...

@runtime_checkable
class LoggerProtocol(Protocol):
    """Protocol for logger objects."""

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None: ...

# Generic types for extensibility
HandlerRegistry = Dict[str, Tuple[HandlerProtocol, List[str]]]
PathRegistry = Dict[str, Dict[str, HandlerProtocol]]
RegexRegistry = Dict[str, str]

# Union types for common use cases
AnyEvent = Union[HttpEventDict, SqsEventDict, LambdaEvent]
AnyResponse = Union[HttpResponseDict, List[Optional[Dict[str, Any]]], LambdaResponse]
AnyHandler = Union[HttpHandlerFunc, SqsHandlerFunc]
AnyMeta = Union[HttpMetaDict, SqsMetaDict]

# Type guards
def is_http_event(event: LambdaEvent) -> bool:
    """Check if event is an HTTP event."""
    return 'httpMethod' in event and 'path' in event

def is_sqs_event(event: LambdaEvent) -> bool:
    """Check if event is an SQS event."""
    return 'Records' in event and len(event['Records']) > 0 and \
           event['Records'][0].get('eventSource') == 'aws:sqs'

# Validation functions
def validate_http_path(path: str) -> bool:
    """Validate HTTP path format."""
    if not path or not isinstance(path, str):
        return False
    return path.startswith('/')


def validate_http_method(method: str) -> bool:
    """Validate HTTP method."""
    valid_methods = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'}
    return method.upper() in valid_methods

# Exception types with type hints
class LambdaError(Exception):
    """Base exception for lambda errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

class HttpError(LambdaError):
    """HTTP-specific error."""

    def __init__(
        self,
        message: str,
        status_code: HttpStatusCode = 500,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, details)
        self.status_code = status_code

class SqsError(LambdaError):
    """SQS-specific error."""

    def __init__(
        self,
        message: str,
        topic: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, details)
        self.topic = topic
