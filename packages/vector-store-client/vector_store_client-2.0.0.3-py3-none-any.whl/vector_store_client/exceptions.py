"""
Vector Store Client Exceptions.

This module defines the exception hierarchy for the Vector Store client.
All exceptions inherit from VectorStoreError to provide consistent error handling.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Union


class VectorStoreError(Exception):
    """
    Base exception for Vector Store client.
    
    All client-specific exceptions inherit from this class to provide
    consistent error handling and identification.
    
    Attributes:
        message (str): Human-readable error message
        details (Optional[Dict]): Additional error details
    """
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details and any(v is not None and v != {} and v != [] and v != 0 and v is not False for v in self.details.values()):
            return f"{self.message} - Details: {self.details}"
        return self.message


class ValidationError(VectorStoreError):
    """
    Raised when data validation fails.
    
    This exception is raised when input data does not meet validation
    requirements, such as missing required fields, invalid data types,
    or constraint violations.
    
    Attributes:
        message (str): Human-readable error message
        field_errors (Dict[str, List[str]]): Field-specific validation errors
        data (Any): Original data that failed validation
    """
    
    def __init__(
        self, 
        message: str, 
        field_errors: Optional[Dict[str, List[str]]] = None,
        data: Optional[Any] = None
    ) -> None:
        super().__init__(message, {"field_errors": field_errors, "data": data})
        self.field_errors = field_errors or {}
        self.data = data
    
    def add_field_error(self, field: str, error: str) -> None:
        """Add a field-specific validation error."""
        if field not in self.field_errors:
            self.field_errors[field] = []
        self.field_errors[field].append(error)
    
    def has_errors(self) -> bool:
        """Check if there are any field errors."""
        return bool(self.field_errors)


class ConnectionError(VectorStoreError):
    """
    Raised when connection to server fails.
    
    This exception is raised when the client cannot establish or maintain
    a connection to the Vector Store server, including network issues,
    timeouts, and server unavailability.
    
    Attributes:
        message (str): Human-readable error message
        url (str): URL that failed to connect
        timeout (float): Timeout value used
        retry_count (int): Number of retry attempts made
    """
    
    def __init__(
        self, 
        message: str, 
        url: Optional[str] = None,
        timeout: Optional[float] = None,
        retry_count: int = 0
    ) -> None:
        details = {
            "url": url,
            "timeout": timeout,
            "retry_count": retry_count
        }
        super().__init__(message, details)
        self.url = url
        self.timeout = timeout
        self.retry_count = retry_count


class JsonRpcError(VectorStoreError):
    """
    Raised when JSON-RPC protocol error occurs.
    
    This exception is raised when there are issues with the JSON-RPC
    protocol, such as invalid requests, malformed responses, or
    protocol version mismatches.
    
    Attributes:
        message (str): Human-readable error message
        code (int): JSON-RPC error code
        method (str): Method that caused the error
        request_id: ID of the failed request
    """
    
    def __init__(
        self, 
        message: str, 
        code: Optional[int] = None,
        method: Optional[str] = None,
        request_id: Optional[str] = None,
        request: Optional[Dict[str, Any]] = None
    ) -> None:
        details = {
            "code": code,
            "method": method,
            "request_id": request_id,
            "request": request
        }
        super().__init__(message, details)
        self.code = code
        self.method = method
        self.request_id = request_id
        self.request = request


class ServerError(VectorStoreError):
    """
    Raised when server returns error response.
    
    This exception is raised when the Vector Store server returns an
    error response, including HTTP errors, server-side validation
    failures, and internal server errors.
    
    Attributes:
        message (str): Human-readable error message
        status_code (int): HTTP status code
        response_data (Dict): Full response data from server
        request_data (Dict): Request data that caused the error
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response: Optional[Dict[str, Any]] = None
    ) -> None:
        # Handle both response_data and response for backward compatibility
        if response is not None and response_data is None:
            response_data = response
            
        details = {
            "status_code": status_code,
            "response_data": response_data,
            "request_data": request_data
        }
        super().__init__(message, details)
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_data = request_data or {}
        self.response = self.response_data  # Alias for backward compatibility


class NotFoundError(VectorStoreError):
    """
    Raised when requested resource is not found.
    
    This exception is raised when trying to access a chunk, configuration,
    or other resource that does not exist in the Vector Store.
    
    Attributes:
        message (str): Human-readable error message
        resource_type (str): Type of resource that was not found
        resource_id (str): ID of the missing resource
    """
    
    def __init__(
        self, 
        message: str, 
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> None:
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        super().__init__(message, details)
        self.resource_type = resource_type
        self.resource_id = resource_id


class DuplicateError(VectorStoreError):
    """
    Raised when trying to create duplicate resource.
    
    This exception is raised when trying to create a chunk or other
    resource that already exists, based on unique constraints.
    
    Attributes:
        message (str): Human-readable error message
        resource_type (str): Type of resource that is duplicate
        resource_id (str): ID of the duplicate resource
        existing_data (Dict): Data of the existing resource
    """
    
    def __init__(
        self, 
        message: str, 
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        existing_data: Optional[Dict[str, Any]] = None
    ) -> None:
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "existing_data": existing_data
        }
        super().__init__(message, details)
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.existing_data = existing_data or {} 


class SVOError(VectorStoreError):
    """
    Raised when SVO (Semantic Vector Operations) service error occurs.
    
    This exception is raised when there are issues with the SVO service,
    such as chunking errors, processing failures, or service unavailability.
    
    Attributes:
        message (str): Human-readable error message
        code (str): SVO error code
        chunk_error (Dict): Chunk-specific error details
    """
    
    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None,
        chunk_error: Optional[Dict[str, Any]] = None
    ) -> None:
        details = {
            "code": code,
            "chunk_error": chunk_error
        }
        super().__init__(message, details)
        self.code = code
        self.chunk_error = chunk_error or {}


class EmbeddingError(VectorStoreError):
    """
    Raised when embedding service operations fail.
    
    This exception is raised when embedding generation fails,
    including model errors, dimension mismatches, and service errors.
    
    Attributes:
        message (str): Human-readable error message
        code (Optional[str]): Error code from embedding service
        details (Optional[Dict]): Additional error details
    """
    
    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, {"code": code, "details": details})
        self.code = code
        self.details = details or {}


class UserCancelledError(VectorStoreError):
    """
    Raised when user cancels an operation.
    
    This exception is raised when a user cancels an operation
    that requires confirmation, such as bulk deletions.
    
    Attributes:
        message (str): Human-readable error message
        operation (Optional[str]): Name of the cancelled operation
    """
    
    def __init__(
        self, 
        message: str, 
        operation: Optional[str] = None
    ) -> None:
        super().__init__(message, {"operation": operation})
        self.operation = operation


# Phase 6: Optimization and Expansion Exceptions

class PluginError(VectorStoreError):
    """
    Raised when plugin operations fail.
    
    This exception is raised when there are issues with plugin
    execution, configuration, or registration.
    
    Attributes:
        message (str): Human-readable error message
        plugin_name (str): Name of the plugin that failed
        plugin_type (str): Type of the plugin
        operation (str): Operation that failed
    """
    
    def __init__(
        self, 
        message: str, 
        plugin_name: Optional[str] = None,
        plugin_type: Optional[str] = None,
        operation: Optional[str] = None
    ) -> None:
        details = {
            "plugin_name": plugin_name,
            "plugin_type": plugin_type,
            "operation": operation
        }
        super().__init__(message, details)
        self.plugin_name = plugin_name
        self.plugin_type = plugin_type
        self.operation = operation


class MiddlewareError(VectorStoreError):
    """
    Raised when middleware operations fail.
    
    This exception is raised when there are issues with middleware
    execution, configuration, or chain processing.
    
    Attributes:
        message (str): Human-readable error message
        middleware_name (str): Name of the middleware that failed
        middleware_type (str): Type of the middleware
        stage (str): Stage in middleware chain where error occurred
    """
    
    def __init__(
        self, 
        message: str, 
        middleware_name: Optional[str] = None,
        middleware_type: Optional[str] = None,
        stage: Optional[str] = None
    ) -> None:
        details = {
            "middleware_name": middleware_name,
            "middleware_type": middleware_type,
            "stage": stage
        }
        super().__init__(message, details)
        self.middleware_name = middleware_name
        self.middleware_type = middleware_type
        self.stage = stage


class MonitoringError(VectorStoreError):
    """
    Raised when monitoring operations fail.
    
    This exception is raised when there are issues with performance
    monitoring, metrics collection, or health checks.
    
    Attributes:
        message (str): Human-readable error message
        metric_name (str): Name of the metric that failed
        operation (str): Monitoring operation that failed
        component (str): Component being monitored
    """
    
    def __init__(
        self, 
        message: str, 
        metric_name: Optional[str] = None,
        operation: Optional[str] = None,
        component: Optional[str] = None
    ) -> None:
        details = {
            "metric_name": metric_name,
            "operation": operation,
            "component": component
        }
        super().__init__(message, details)
        self.metric_name = metric_name
        self.operation = operation
        self.component = component


class BackupError(VectorStoreError):
    """
    Raised when backup/restore operations fail.
    
    This exception is raised when there are issues with creating
    backups, restoring data, or backup validation.
    
    Attributes:
        message (str): Human-readable error message
        backup_path (str): Path to backup file
        operation (str): Backup operation that failed
        file_size (int): Size of backup file in bytes
    """
    
    def __init__(
        self, 
        message: str, 
        backup_path: Optional[str] = None,
        operation: Optional[str] = None,
        file_size: Optional[int] = None
    ) -> None:
        details = {
            "backup_path": backup_path,
            "operation": operation,
            "file_size": file_size
        }
        super().__init__(message, details)
        self.backup_path = backup_path
        self.operation = operation
        self.file_size = file_size


class MigrationError(VectorStoreError):
    """
    Raised when data migration operations fail.
    
    This exception is raised when there are issues with migrating
    data between vector stores or processing migration batches.
    
    Attributes:
        message (str): Human-readable error message
        source_client (str): Source client identifier
        target_client (str): Target client identifier
        batch_number (int): Number of the failed batch
        total_migrated (int): Total chunks migrated before failure
    """
    
    def __init__(
        self, 
        message: str, 
        source_client: Optional[str] = None,
        target_client: Optional[str] = None,
        batch_number: Optional[int] = None,
        total_migrated: Optional[int] = None
    ) -> None:
        details = {
            "source_client": source_client,
            "target_client": target_client,
            "batch_number": batch_number,
            "total_migrated": total_migrated
        }
        super().__init__(message, details)
        self.source_client = source_client
        self.target_client = target_client
        self.batch_number = batch_number
        self.total_migrated = total_migrated


class StreamingError(VectorStoreError):
    """
    Raised when streaming operations fail.
    
    This exception is raised when there are issues with streaming
    large datasets, batch processing, or stream management.
    
    Attributes:
        message (str): Human-readable error message
        stream_type (str): Type of stream operation
        batch_number (int): Number of the failed batch
        total_processed (int): Total items processed before failure
    """
    
    def __init__(
        self, 
        message: str, 
        stream_type: Optional[str] = None,
        batch_number: Optional[int] = None,
        total_processed: Optional[int] = None
    ) -> None:
        details = {
            "stream_type": stream_type,
            "batch_number": batch_number,
            "total_processed": total_processed
        }
        super().__init__(message, details)
        self.stream_type = stream_type
        self.batch_number = batch_number
        self.total_processed = total_processed 


class TimeoutError(VectorStoreError):
    """
    Raised when a request times out.
    
    This exception is raised when a request to the server exceeds
    the specified timeout period.
    
    Attributes:
        message (str): Human-readable error message
        duration (float): Timeout duration in seconds
        operation (str): Operation that timed out
    """
    
    def __init__(
        self, 
        message: str, 
        duration: Optional[float] = None,
        operation: Optional[str] = None
    ) -> None:
        details = {
            "duration": duration,
            "operation": operation
        }
        super().__init__(message, details)
        self.duration = duration
        self.operation = operation


class AuthenticationError(VectorStoreError):
    """
    Raised when authentication fails.
    
    This exception is raised when the client cannot authenticate
    with the server due to invalid credentials or missing authentication.
    
    Attributes:
        message (str): Human-readable error message
        auth_type (str): Type of authentication that failed
        credentials_provided (bool): Whether credentials were provided
    """
    
    def __init__(
        self, 
        message: str, 
        auth_type: Optional[str] = None,
        credentials_provided: bool = False
    ) -> None:
        details = {
            "auth_type": auth_type,
            "credentials_provided": credentials_provided
        }
        super().__init__(message, details)
        self.auth_type = auth_type
        self.credentials_provided = credentials_provided


class AuthorizationError(VectorStoreError):
    """
    Raised when authorization fails.
    
    This exception is raised when the client is authenticated but
    does not have permission to perform the requested operation.
    
    Attributes:
        message (str): Human-readable error message
        required_permission (str): Permission that was required
        user_permissions (List[str]): Permissions the user has
    """
    
    def __init__(
        self, 
        message: str, 
        required_permission: Optional[str] = None,
        user_permissions: Optional[List[str]] = None
    ) -> None:
        details = {
            "required_permission": required_permission,
            "user_permissions": user_permissions or []
        }
        super().__init__(message, details)
        self.required_permission = required_permission
        self.user_permissions = user_permissions or []


class RateLimitError(VectorStoreError):
    """
    Raised when rate limit is exceeded.
    
    This exception is raised when the client exceeds the server's
    rate limiting policies.
    
    Attributes:
        message (str): Human-readable error message
        retry_after (int): Seconds to wait before retrying
        limit_type (str): Type of rate limit exceeded
        current_usage (int): Current usage count
        limit_value (int): Maximum allowed usage
    """
    
    def __init__(
        self, 
        message: str, 
        retry_after: Optional[int] = None,
        limit_type: Optional[str] = None,
        current_usage: Optional[int] = None,
        limit_value: Optional[int] = None
    ) -> None:
        details = {
            "retry_after": retry_after,
            "limit_type": limit_type,
            "current_usage": current_usage,
            "limit_value": limit_value
        }
        super().__init__(message, details)
        self.retry_after = retry_after
        self.limit_type = limit_type
        self.current_usage = current_usage
        self.limit_value = limit_value


class ResourceNotFoundError(VectorStoreError):
    """
    Raised when a requested resource is not found.
    
    This exception is raised when the client requests a resource
    that does not exist on the server.
    
    Attributes:
        message (str): Human-readable error message
        resource_type (str): Type of resource that was not found
        resource_id (str): ID of the resource that was not found
    """
    
    def __init__(
        self, 
        message: str, 
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> None:
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        super().__init__(message, details)
        self.resource_type = resource_type
        self.resource_id = resource_id


class ResourceConflictError(VectorStoreError):
    """
    Raised when there is a conflict with a resource.
    
    This exception is raised when the client tries to create or
    modify a resource that conflicts with an existing resource.
    
    Attributes:
        message (str): Human-readable error message
        resource_type (str): Type of resource in conflict
        resource_id (str): ID of the resource in conflict
        conflict_type (str): Type of conflict
    """
    
    def __init__(
        self, 
        message: str, 
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        conflict_type: Optional[str] = None
    ) -> None:
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "conflict_type": conflict_type
        }
        super().__init__(message, details)
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.conflict_type = conflict_type


# HTTP Status Code Specific Errors

class BadRequestError(VectorStoreError):
    """Raised for HTTP 400 Bad Request errors."""
    pass


class UnauthorizedError(AuthenticationError):
    """Raised for HTTP 401 Unauthorized errors."""
    pass


class ForbiddenError(AuthorizationError):
    """Raised for HTTP 403 Forbidden errors."""
    pass


class NotFoundError(ResourceNotFoundError):
    """Raised for HTTP 404 Not Found errors."""
    pass


class MethodNotAllowedError(VectorStoreError):
    """Raised for HTTP 405 Method Not Allowed errors."""
    pass


class ConflictError(ResourceConflictError):
    """Raised for HTTP 409 Conflict errors."""
    pass


class UnprocessableEntityError(VectorStoreError):
    """Raised for HTTP 422 Unprocessable Entity errors."""
    pass


class TooManyRequestsError(RateLimitError):
    """Raised for HTTP 429 Too Many Requests errors."""
    pass


class RequestEntityTooLargeError(VectorStoreError):
    """Raised for HTTP 413 Request Entity Too Large errors."""
    pass


class UnsupportedMediaTypeError(VectorStoreError):
    """Raised for HTTP 415 Unsupported Media Type errors."""
    pass


class RequestedRangeNotSatisfiableError(VectorStoreError):
    """Raised for HTTP 416 Requested Range Not Satisfiable errors."""
    pass


class ExpectationFailedError(VectorStoreError):
    """Raised for HTTP 417 Expectation Failed errors."""
    pass


class MisdirectedRequestError(VectorStoreError):
    """Raised for HTTP 421 Misdirected Request errors."""
    pass


class UnavailableForLegalReasonsError(VectorStoreError):
    """Raised for HTTP 451 Unavailable For Legal Reasons errors."""
    pass


class InternalServerError(ServerError):
    """Raised for HTTP 500 Internal Server Error."""
    pass


class ServiceUnavailableError(ServerError):
    """Raised for HTTP 503 Service Unavailable."""
    pass 


def create_from_http_status(
    status_code: int, 
    message: Optional[str] = None,
    response_data: Optional[Dict[str, Any]] = None,
    request_data: Optional[Dict[str, Any]] = None
) -> VectorStoreError:
    """
    Create appropriate exception from HTTP status code.
    
    Parameters:
        status_code (int): HTTP status code
        message (str, optional): Custom error message
        response_data (Dict, optional): Response data
        request_data (Dict, optional): Request data
        
    Returns:
        VectorStoreError: Appropriate exception for the status code
    """
    if message is None:
        message = f"HTTP {status_code} error"
    
    if status_code == 400:
        return BadRequestError(message)
    elif status_code == 401:
        return UnauthorizedError(message)
    elif status_code == 403:
        return ForbiddenError(message)
    elif status_code == 404:
        return NotFoundError(message)
    elif status_code == 405:
        return MethodNotAllowedError(message)
    elif status_code == 409:
        return ConflictError(message)
    elif status_code == 413:
        return RequestEntityTooLargeError(message)
    elif status_code == 415:
        return UnsupportedMediaTypeError(message)
    elif status_code == 416:
        return RequestedRangeNotSatisfiableError(message)
    elif status_code == 417:
        return ExpectationFailedError(message)
    elif status_code == 421:
        return MisdirectedRequestError(message)
    elif status_code == 422:
        return UnprocessableEntityError(message)
    elif status_code == 429:
        return TooManyRequestsError(message)
    elif status_code == 451:
        return UnavailableForLegalReasonsError(message)
    elif status_code == 500:
        return InternalServerError(message, status_code=status_code, response_data=response_data, request_data=request_data)
    elif status_code == 503:
        return ServiceUnavailableError(message, status_code=status_code, response_data=response_data, request_data=request_data)
    else:
        return ServerError(message, status_code=status_code, response_data=response_data, request_data=request_data)


def create_from_json_rpc_error(
    error_data: Union[Dict[str, Any], int],
    method: Optional[str] = None,
    request_id: Optional[str] = None
) -> JsonRpcError:
    """
    Create JsonRpcError from JSON-RPC error data.
    
    Parameters:
        error_data (Union[Dict, int]): JSON-RPC error data or error code
        method (str, optional): Method that was called
        request_id (str, optional): Request ID
        
    Returns:
        JsonRpcError: JSON-RPC error exception
    """
    if isinstance(error_data, int):
        # If error_data is just a code, create minimal error
        code = error_data
        message = f"JSON-RPC error {code}"
    else:
        # If error_data is a dict, extract code and message
        code = error_data.get("code")
        message = error_data.get("message", "JSON-RPC error")
    
    return JsonRpcError(
        message=message,
        code=code,
        method=method,
        request_id=request_id
    ) 


class ChunkingError(VectorStoreError):
    """
    Raised when chunking operations fail.
    
    This exception is raised when text chunking operations fail,
    such as SVO chunker errors or chunk processing issues.
    
    Attributes:
        message (str): Human-readable error message
        chunk_data (Optional[Any]): Chunk data that caused the error
    """
    
    def __init__(
        self, 
        message: str, 
        chunk_data: Optional[Any] = None
    ) -> None:
        super().__init__(message, {"chunk_data": chunk_data})
        self.chunk_data = chunk_data


class EmbeddingError(VectorStoreError):
    """
    Raised when embedding operations fail.
    
    This exception is raised when embedding generation or processing
    operations fail, such as embedding service errors.
    
    Attributes:
        message (str): Human-readable error message
        text (Optional[str]): Text that failed to embed
        embedding_data (Optional[Any]): Embedding data that caused the error
    """
    
    def __init__(
        self, 
        message: str, 
        text: Optional[str] = None,
        embedding_data: Optional[Any] = None
    ) -> None:
        super().__init__(message, {"text": text, "embedding_data": embedding_data})
        self.text = text
        self.embedding_data = embedding_data 