"""
Tests for vector_store_client.exceptions module.

This module tests all exception classes and utility functions
defined in the exceptions module.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
from typing import Dict, List, Any

from vector_store_client.exceptions import (
    # Base exception
    VectorStoreError,
    
    # Core exceptions
    ValidationError, ConnectionError, JsonRpcError, ServerError,
    
    # Resource exceptions
    NotFoundError, DuplicateError, ResourceNotFoundError, ResourceConflictError,
    
    # Adapter exceptions
    SVOError, EmbeddingError,
    
    # User exceptions
    UserCancelledError,
    
    # Plugin and middleware exceptions
    PluginError, MiddlewareError,
    
    # Monitoring exceptions
    MonitoringError,
    
    # Backup and migration exceptions
    BackupError, MigrationError, StreamingError,
    
    # Timeout and authentication exceptions
    TimeoutError, AuthenticationError, AuthorizationError,
    
    # Rate limiting exceptions
    RateLimitError,
    
    # HTTP status exceptions
    BadRequestError, UnauthorizedError, ForbiddenError, MethodNotAllowedError,
    ConflictError, UnprocessableEntityError, TooManyRequestsError,
    RequestEntityTooLargeError, UnsupportedMediaTypeError,
    RequestedRangeNotSatisfiableError, ExpectationFailedError,
    MisdirectedRequestError, UnavailableForLegalReasonsError,
    InternalServerError, ServiceUnavailableError,
    
    # Utility functions
    create_from_http_status, create_from_json_rpc_error
)


class TestVectorStoreError:
    """Test base VectorStoreError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = VectorStoreError("Test error")
        
        assert error.message == "Test error"
        assert error.details == {}
        assert str(error) == "Test error"
    
    def test_init_with_details(self):
        """Test initialization with details."""
        details = {"code": 500, "url": "http://test.com"}
        error = VectorStoreError("Test error", details)
        
        assert error.message == "Test error"
        assert error.details == details
        assert "Test error - Details:" in str(error)
    
    def test_str_with_empty_details(self):
        """Test string representation with empty details."""
        error = VectorStoreError("Test error", {})
        
        assert str(error) == "Test error"
    
    def test_str_with_none_details(self):
        """Test string representation with None details."""
        error = VectorStoreError("Test error", None)
        
        assert str(error) == "Test error"


class TestValidationError:
    """Test ValidationError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = ValidationError("Validation failed")
        
        assert error.message == "Validation failed"
        assert error.field_errors == {}
        assert error.data is None
        assert not error.has_errors()
    
    def test_init_with_field_errors(self):
        """Test initialization with field errors."""
        field_errors = {"name": ["Required field"], "age": ["Must be positive"]}
        error = ValidationError("Validation failed", field_errors)
        
        assert error.message == "Validation failed"
        assert error.field_errors == field_errors
        assert error.has_errors()
    
    def test_init_with_data(self):
        """Test initialization with data."""
        data = {"name": "", "age": -1}
        error = ValidationError("Validation failed", data=data)
        
        assert error.message == "Validation failed"
        assert error.data == data
    
    def test_add_field_error(self):
        """Test adding field error."""
        error = ValidationError("Validation failed")
        
        error.add_field_error("name", "Required field")
        error.add_field_error("name", "Must be string")
        
        assert error.field_errors["name"] == ["Required field", "Must be string"]
        assert error.has_errors()
    
    def test_has_errors_empty(self):
        """Test has_errors with empty field errors."""
        error = ValidationError("Validation failed")
        
        assert not error.has_errors()


class TestConnectionError:
    """Test ConnectionError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = ConnectionError("Connection failed")
        
        assert error.message == "Connection failed"
        assert error.url is None
        assert error.timeout is None
        assert error.retry_count == 0
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        error = ConnectionError(
            "Connection failed",
            url="http://test.com",
            timeout=30.0,
            retry_count=3
        )
        
        assert error.message == "Connection failed"
        assert error.url == "http://test.com"
        assert error.timeout == 30.0
        assert error.retry_count == 3


class TestJsonRpcError:
    """Test JsonRpcError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = JsonRpcError("JSON-RPC error")
        
        assert error.message == "JSON-RPC error"
        assert error.code is None
        assert error.method is None
        assert error.request_id is None
        assert error.request is None
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        request = {"method": "test", "params": {}}
        error = JsonRpcError(
            "JSON-RPC error",
            code=-32601,
            method="test_method",
            request_id="123",
            request=request
        )
        
        assert error.message == "JSON-RPC error"
        assert error.code == -32601
        assert error.method == "test_method"
        assert error.request_id == "123"
        assert error.request == request


class TestServerError:
    """Test ServerError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = ServerError("Server error")
        
        assert error.message == "Server error"
        assert error.status_code is None
        assert error.response_data == {}
        assert error.request_data == {}
        assert error.response == {}
    
    def test_init_with_response_data(self):
        """Test initialization with response_data."""
        response_data = {"error": "Internal error"}
        error = ServerError("Server error", response_data=response_data)
        
        assert error.message == "Server error"
        assert error.response_data == response_data
        assert error.response == response_data  # Backward compatibility
    
    def test_init_with_response(self):
        """Test initialization with response."""
        response = {"error": "Internal error"}
        error = ServerError("Server error", response=response)
        
        assert error.message == "Server error"
        assert error.response == response
        assert error.response_data == response  # Backward compatibility


class TestNotFoundError:
    """Test NotFoundError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = NotFoundError("Not found")
        
        assert error.message == "Not found"
        assert error.resource_type is None
        assert error.resource_id is None
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        error = NotFoundError("Not found", "chunk", "123")
        
        assert error.message == "Not found"
        assert error.resource_type == "chunk"
        assert error.resource_id == "123"


class TestDuplicateError:
    """Test DuplicateError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = DuplicateError("Duplicate found")
        
        assert error.message == "Duplicate found"
        assert error.resource_type is None
        assert error.resource_id is None
        assert error.existing_data == {}
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        existing_data = {"id": "123", "name": "test"}
        error = DuplicateError("Duplicate found", "chunk", "123", existing_data)
        
        assert error.message == "Duplicate found"
        assert error.resource_type == "chunk"
        assert error.resource_id == "123"
        assert error.existing_data == existing_data


class TestSVOError:
    """Test SVOError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = SVOError("SVO error")
        
        assert error.message == "SVO error"
        assert error.code is None
        assert error.chunk_error == {}
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        chunk_error = {"line": 10, "message": "Syntax error"}
        error = SVOError("SVO error", "SYNTAX_ERROR", chunk_error)
        
        assert error.message == "SVO error"
        assert error.code == "SYNTAX_ERROR"
        assert error.chunk_error == chunk_error


class TestEmbeddingError:
    """Test EmbeddingError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = EmbeddingError("Embedding error")
        
        assert error.message == "Embedding error"
        assert error.code is None
        assert error.details == {}
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        details = {"model": "test-model", "dimension": 384}
        error = EmbeddingError("Embedding error", "MODEL_ERROR", details)
        
        assert error.message == "Embedding error"
        assert error.code == "MODEL_ERROR"
        assert error.details == details


class TestUserCancelledError:
    """Test UserCancelledError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = UserCancelledError("Operation cancelled")
        
        assert error.message == "Operation cancelled"
        assert error.operation is None
    
    def test_init_with_operation(self):
        """Test initialization with operation."""
        error = UserCancelledError("Operation cancelled", "search")
        
        assert error.message == "Operation cancelled"
        assert error.operation == "search"


class TestPluginError:
    """Test PluginError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = PluginError("Plugin error")
        
        assert error.message == "Plugin error"
        assert error.plugin_name is None
        assert error.plugin_type is None
        assert error.operation is None
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        error = PluginError("Plugin error", "test_plugin", "processor", "init")
        
        assert error.message == "Plugin error"
        assert error.plugin_name == "test_plugin"
        assert error.plugin_type == "processor"
        assert error.operation == "init"


class TestMiddlewareError:
    """Test MiddlewareError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = MiddlewareError("Middleware error")
        
        assert error.message == "Middleware error"
        assert error.middleware_name is None
        assert error.middleware_type is None
        assert error.stage is None
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        error = MiddlewareError("Middleware error", "test_middleware", "logging", "pre")
        
        assert error.message == "Middleware error"
        assert error.middleware_name == "test_middleware"
        assert error.middleware_type == "logging"
        assert error.stage == "pre"


class TestMonitoringError:
    """Test MonitoringError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = MonitoringError("Monitoring error")
        
        assert error.message == "Monitoring error"
        assert error.metric_name is None
        assert error.operation is None
        assert error.component is None
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        error = MonitoringError("Monitoring error", "response_time", "search", "client")
        
        assert error.message == "Monitoring error"
        assert error.metric_name == "response_time"
        assert error.operation == "search"
        assert error.component == "client"


class TestBackupError:
    """Test BackupError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = BackupError("Backup error")
        
        assert error.message == "Backup error"
        assert error.backup_path is None
        assert error.operation is None
        assert error.file_size is None
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        error = BackupError("Backup error", "/path/backup.json", "create", 1024)
        
        assert error.message == "Backup error"
        assert error.backup_path == "/path/backup.json"
        assert error.operation == "create"
        assert error.file_size == 1024


class TestMigrationError:
    """Test MigrationError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = MigrationError("Migration error")
        
        assert error.message == "Migration error"
        assert error.source_client is None
        assert error.target_client is None
        assert error.batch_number is None
        assert error.total_migrated is None
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        error = MigrationError("Migration error", "v1", "v2", 5, 1000)
        
        assert error.message == "Migration error"
        assert error.source_client == "v1"
        assert error.target_client == "v2"
        assert error.batch_number == 5
        assert error.total_migrated == 1000


class TestStreamingError:
    """Test StreamingError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = StreamingError("Streaming error")
        
        assert error.message == "Streaming error"
        assert error.stream_type is None
        assert error.batch_number is None
        assert error.total_processed is None
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        error = StreamingError("Streaming error", "chunks", 10, 500)
        
        assert error.message == "Streaming error"
        assert error.stream_type == "chunks"
        assert error.batch_number == 10
        assert error.total_processed == 500


class TestTimeoutError:
    """Test TimeoutError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = TimeoutError("Timeout error")
        
        assert error.message == "Timeout error"
        assert error.duration is None
        assert error.operation is None
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        error = TimeoutError("Timeout error", 30.0, "search")
        
        assert error.message == "Timeout error"
        assert error.duration == 30.0
        assert error.operation == "search"


class TestAuthenticationError:
    """Test AuthenticationError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = AuthenticationError("Authentication error")
        
        assert error.message == "Authentication error"
        assert error.auth_type is None
        assert error.credentials_provided is False
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        error = AuthenticationError("Authentication error", "api_key", True)
        
        assert error.message == "Authentication error"
        assert error.auth_type == "api_key"
        assert error.credentials_provided is True


class TestAuthorizationError:
    """Test AuthorizationError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = AuthorizationError("Authorization error")
        
        assert error.message == "Authorization error"
        assert error.required_permission is None
        assert error.user_permissions == []
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        user_permissions = ["read", "write"]
        error = AuthorizationError("Authorization error", "admin", user_permissions)
        
        assert error.message == "Authorization error"
        assert error.required_permission == "admin"
        assert error.user_permissions == user_permissions


class TestRateLimitError:
    """Test RateLimitError class."""
    
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = RateLimitError("Rate limit error")
        
        assert error.message == "Rate limit error"
        assert error.retry_after is None
        assert error.limit_type is None
        assert error.current_usage is None
        assert error.limit_value is None
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        error = RateLimitError("Rate limit error", 60, "requests", 100, 1000)
        
        assert error.message == "Rate limit error"
        assert error.retry_after == 60
        assert error.limit_type == "requests"
        assert error.current_usage == 100
        assert error.limit_value == 1000


class TestHTTPStatusExceptions:
    """Test HTTP status code exceptions."""
    
    def test_bad_request_error(self):
        """Test BadRequestError."""
        error = BadRequestError("Bad request")
        assert error.message == "Bad request"
    
    def test_unauthorized_error(self):
        """Test UnauthorizedError."""
        error = UnauthorizedError("Unauthorized")
        assert error.message == "Unauthorized"
        assert isinstance(error, AuthenticationError)
    
    def test_forbidden_error(self):
        """Test ForbiddenError."""
        error = ForbiddenError("Forbidden")
        assert error.message == "Forbidden"
        assert isinstance(error, AuthorizationError)
    
    def test_method_not_allowed_error(self):
        """Test MethodNotAllowedError."""
        error = MethodNotAllowedError("Method not allowed")
        assert error.message == "Method not allowed"
    
    def test_conflict_error(self):
        """Test ConflictError."""
        error = ConflictError("Conflict")
        assert error.message == "Conflict"
        assert isinstance(error, ResourceConflictError)
    
    def test_unprocessable_entity_error(self):
        """Test UnprocessableEntityError."""
        error = UnprocessableEntityError("Unprocessable entity")
        assert error.message == "Unprocessable entity"
    
    def test_too_many_requests_error(self):
        """Test TooManyRequestsError."""
        error = TooManyRequestsError("Too many requests")
        assert error.message == "Too many requests"
        assert isinstance(error, RateLimitError)
    
    def test_request_entity_too_large_error(self):
        """Test RequestEntityTooLargeError."""
        error = RequestEntityTooLargeError("Request entity too large")
        assert error.message == "Request entity too large"
    
    def test_unsupported_media_type_error(self):
        """Test UnsupportedMediaTypeError."""
        error = UnsupportedMediaTypeError("Unsupported media type")
        assert error.message == "Unsupported media type"
    
    def test_requested_range_not_satisfiable_error(self):
        """Test RequestedRangeNotSatisfiableError."""
        error = RequestedRangeNotSatisfiableError("Range not satisfiable")
        assert error.message == "Range not satisfiable"
    
    def test_expectation_failed_error(self):
        """Test ExpectationFailedError."""
        error = ExpectationFailedError("Expectation failed")
        assert error.message == "Expectation failed"
    
    def test_misdirected_request_error(self):
        """Test MisdirectedRequestError."""
        error = MisdirectedRequestError("Misdirected request")
        assert error.message == "Misdirected request"
    
    def test_unavailable_for_legal_reasons_error(self):
        """Test UnavailableForLegalReasonsError."""
        error = UnavailableForLegalReasonsError("Unavailable for legal reasons")
        assert error.message == "Unavailable for legal reasons"
    
    def test_internal_server_error(self):
        """Test InternalServerError."""
        error = InternalServerError("Internal server error")
        assert error.message == "Internal server error"
        assert isinstance(error, ServerError)
    
    def test_service_unavailable_error(self):
        """Test ServiceUnavailableError."""
        error = ServiceUnavailableError("Service unavailable")
        assert error.message == "Service unavailable"
        assert isinstance(error, ServerError)


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_create_from_http_status_400(self):
        """Test create_from_http_status with 400."""
        error = create_from_http_status(400, "Bad request")
        
        assert isinstance(error, BadRequestError)
        assert error.message == "Bad request"
    
    def test_create_from_http_status_401(self):
        """Test create_from_http_status with 401."""
        error = create_from_http_status(401, "Unauthorized")
        
        assert isinstance(error, UnauthorizedError)
        assert error.message == "Unauthorized"
    
    def test_create_from_http_status_403(self):
        """Test create_from_http_status with 403."""
        error = create_from_http_status(403, "Forbidden")
        
        assert isinstance(error, ForbiddenError)
        assert error.message == "Forbidden"
    
    def test_create_from_http_status_404(self):
        """Test create_from_http_status with 404."""
        error = create_from_http_status(404, "Not found")
        
        assert isinstance(error, NotFoundError)
        assert error.message == "Not found"
    
    def test_create_from_http_status_405(self):
        """Test create_from_http_status with 405."""
        error = create_from_http_status(405, "Method not allowed")
        
        assert isinstance(error, MethodNotAllowedError)
        assert error.message == "Method not allowed"
    
    def test_create_from_http_status_409(self):
        """Test create_from_http_status with 409."""
        error = create_from_http_status(409, "Conflict")
        
        assert isinstance(error, ConflictError)
        assert error.message == "Conflict"
    
    def test_create_from_http_status_422(self):
        """Test create_from_http_status with 422."""
        error = create_from_http_status(422, "Unprocessable entity")
        
        assert isinstance(error, UnprocessableEntityError)
        assert error.message == "Unprocessable entity"
    
    def test_create_from_http_status_429(self):
        """Test create_from_http_status with 429."""
        error = create_from_http_status(429, "Too many requests")
        
        assert isinstance(error, TooManyRequestsError)
        assert error.message == "Too many requests"
    
    def test_create_from_http_status_413(self):
        """Test create_from_http_status with 413."""
        error = create_from_http_status(413, "Request entity too large")
        
        assert isinstance(error, RequestEntityTooLargeError)
        assert error.message == "Request entity too large"
    
    def test_create_from_http_status_415(self):
        """Test create_from_http_status with 415."""
        error = create_from_http_status(415, "Unsupported media type")
        
        assert isinstance(error, UnsupportedMediaTypeError)
        assert error.message == "Unsupported media type"
    
    def test_create_from_http_status_416(self):
        """Test create_from_http_status with 416."""
        error = create_from_http_status(416, "Range not satisfiable")
        
        assert isinstance(error, RequestedRangeNotSatisfiableError)
        assert error.message == "Range not satisfiable"
    
    def test_create_from_http_status_417(self):
        """Test create_from_http_status with 417."""
        error = create_from_http_status(417, "Expectation failed")
        
        assert isinstance(error, ExpectationFailedError)
        assert error.message == "Expectation failed"
    
    def test_create_from_http_status_421(self):
        """Test create_from_http_status with 421."""
        error = create_from_http_status(421, "Misdirected request")
        
        assert isinstance(error, MisdirectedRequestError)
        assert error.message == "Misdirected request"
    
    def test_create_from_http_status_451(self):
        """Test create_from_http_status with 451."""
        error = create_from_http_status(451, "Unavailable for legal reasons")
        
        assert isinstance(error, UnavailableForLegalReasonsError)
        assert error.message == "Unavailable for legal reasons"
    
    def test_create_from_http_status_500(self):
        """Test create_from_http_status with 500."""
        error = create_from_http_status(500, "Internal server error")
        
        assert isinstance(error, InternalServerError)
        assert error.message == "Internal server error"
    
    def test_create_from_http_status_503(self):
        """Test create_from_http_status with 503."""
        error = create_from_http_status(503, "Service unavailable")
        
        assert isinstance(error, ServiceUnavailableError)
        assert error.message == "Service unavailable"
    
    def test_create_from_http_status_unknown(self):
        """Test create_from_http_status with unknown status code."""
        error = create_from_http_status(999, "Unknown error")
        
        assert isinstance(error, ServerError)
        assert error.message == "Unknown error"
        assert error.status_code == 999
    
    def test_create_from_http_status_with_response_data(self):
        """Test create_from_http_status with response data."""
        response_data = {"error": "Test error"}
        error = create_from_http_status(400, "Bad request", response_data)
        
        assert isinstance(error, BadRequestError)
        # BadRequestError doesn't have response_data attribute
    
    def test_create_from_json_rpc_error_dict(self):
        """Test create_from_json_rpc_error with dict."""
        error_data = {
            "code": -32601,
            "message": "Method not found"
        }
        error = create_from_json_rpc_error(error_data, "test_method", "123")
        
        assert isinstance(error, JsonRpcError)
        assert error.message == "Method not found"
        assert error.code == -32601
        assert error.method == "test_method"
        assert error.request_id == "123"
    
    def test_create_from_json_rpc_error_int(self):
        """Test create_from_json_rpc_error with int."""
        error = create_from_json_rpc_error(-32601, "test_method", "123")
        
        assert isinstance(error, JsonRpcError)
        assert error.message == "JSON-RPC error -32601"
        assert error.code == -32601
        assert error.method == "test_method"
        assert error.request_id == "123" 