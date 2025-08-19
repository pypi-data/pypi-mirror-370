"""Tests for the MontyCloud Day2 SDK exceptions."""

import pytest

from day2.exceptions import (
    AuthenticationError,
    ClientError,
    Day2Error,
    ResourceNotFoundError,
    ServerError,
    TenantContextError,
    ValidationError,
)


class TestDay2Error:
    """Test cases for the base Day2Error exception."""

    def test_day2_error_initialization(self):
        """Test Day2Error can be initialized with a message."""
        error = Day2Error("Test error message")
        assert str(error) == "Test error message"

    def test_day2_error_inheritance(self):
        """Test Day2Error inherits from Exception."""
        error = Day2Error("Test error")
        assert isinstance(error, Exception)

    def test_day2_error_with_empty_message(self):
        """Test Day2Error can be initialized with empty message."""
        error = Day2Error("")
        assert str(error) == ""


class TestClientError:
    """Test cases for ClientError exception."""

    def test_client_error_initialization(self):
        """Test ClientError initialization with required parameters."""
        error = ClientError("Bad request", 400)
        assert error.status_code == 400
        assert error.request_id is None
        assert str(error) == "Bad request (Status: 400, RequestId: None)"

    def test_client_error_with_request_id(self):
        """Test ClientError initialization with request ID."""
        error = ClientError("Bad request", 400, "req-123")
        assert error.status_code == 400
        assert error.request_id == "req-123"
        assert str(error) == "Bad request (Status: 400, RequestId: req-123)"

    def test_client_error_inheritance(self):
        """Test ClientError inherits from Day2Error."""
        error = ClientError("Test error", 400)
        assert isinstance(error, Day2Error)
        assert isinstance(error, Exception)

    def test_client_error_attributes(self):
        """Test ClientError preserves all attributes."""
        error = ClientError("Validation failed", 422, "req-456")
        assert hasattr(error, "status_code")
        assert hasattr(error, "request_id")
        assert error.status_code == 422
        assert error.request_id == "req-456"


class TestServerError:
    """Test cases for ServerError exception."""

    def test_server_error_initialization(self):
        """Test ServerError initialization with required parameters."""
        error = ServerError("Internal server error", 500)
        assert error.status_code == 500
        assert error.request_id is None
        assert str(error) == "Internal server error (Status: 500, RequestId: None)"

    def test_server_error_with_request_id(self):
        """Test ServerError initialization with request ID."""
        error = ServerError("Service unavailable", 503, "req-789")
        assert error.status_code == 503
        assert error.request_id == "req-789"
        assert str(error) == "Service unavailable (Status: 503, RequestId: req-789)"

    def test_server_error_inheritance(self):
        """Test ServerError inherits from Day2Error."""
        error = ServerError("Test error", 500)
        assert isinstance(error, Day2Error)
        assert isinstance(error, Exception)

    def test_server_error_attributes(self):
        """Test ServerError preserves all attributes."""
        error = ServerError("Gateway timeout", 504, "req-999")
        assert hasattr(error, "status_code")
        assert hasattr(error, "request_id")
        assert error.status_code == 504
        assert error.request_id == "req-999"


class TestValidationError:
    """Test cases for ValidationError exception."""

    def test_validation_error_inheritance(self):
        """Test ValidationError inherits from ClientError."""
        error = ValidationError("Invalid input", 422)
        assert isinstance(error, ClientError)
        assert isinstance(error, Day2Error)
        assert isinstance(error, Exception)

    def test_validation_error_message_format(self):
        """Test ValidationError message formatting."""
        error = ValidationError("Required field missing", 422, "req-validation")
        assert (
            str(error)
            == "Required field missing (Status: 422, RequestId: req-validation)"
        )


class TestResourceNotFoundError:
    """Test cases for ResourceNotFoundError exception."""

    def test_resource_not_found_default_status(self):
        """Test ResourceNotFoundError uses default 404 status code."""
        error = ResourceNotFoundError("Tenant not found")
        assert error.status_code == 404
        assert error.request_id is None
        assert str(error) == "Tenant not found (Status: 404, RequestId: None)"

    def test_resource_not_found_custom_status(self):
        """Test ResourceNotFoundError with custom status code."""
        error = ResourceNotFoundError("Resource not found", 410, "req-gone")
        assert error.status_code == 410
        assert error.request_id == "req-gone"
        assert str(error) == "Resource not found (Status: 410, RequestId: req-gone)"

    def test_resource_not_found_inheritance(self):
        """Test ResourceNotFoundError inherits from ClientError."""
        error = ResourceNotFoundError("Not found")
        assert isinstance(error, ClientError)
        assert isinstance(error, Day2Error)
        assert isinstance(error, Exception)

    def test_resource_not_found_with_request_id_only(self):
        """Test ResourceNotFoundError with request ID but default status."""
        error = ResourceNotFoundError("Assessment not found", request_id="req-123")
        assert error.status_code == 404
        assert error.request_id == "req-123"
        assert str(error) == "Assessment not found (Status: 404, RequestId: req-123)"


class TestAuthenticationError:
    """Test cases for AuthenticationError exception."""

    def test_authentication_error_inheritance(self):
        """Test AuthenticationError inherits from ClientError."""
        error = AuthenticationError("Invalid credentials", 401)
        assert isinstance(error, ClientError)
        assert isinstance(error, Day2Error)
        assert isinstance(error, Exception)

    def test_authentication_error_message_format(self):
        """Test AuthenticationError message formatting."""
        error = AuthenticationError("Token expired", 401, "req-auth")
        assert str(error) == "Token expired (Status: 401, RequestId: req-auth)"


class TestTenantContextError:
    """Test cases for TenantContextError exception."""

    def test_tenant_context_error_default_status(self):
        """Test TenantContextError uses default 400 status code."""
        error = TenantContextError("Invalid tenant context")
        assert error.status_code == 400
        assert error.request_id is None
        assert str(error) == "Invalid tenant context (Status: 400, RequestId: None)"

    def test_tenant_context_error_custom_status(self):
        """Test TenantContextError with custom status code."""
        error = TenantContextError("Tenant access denied", 403, "req-tenant")
        assert error.status_code == 403
        assert error.request_id == "req-tenant"
        assert str(error) == "Tenant access denied (Status: 403, RequestId: req-tenant)"

    def test_tenant_context_error_inheritance(self):
        """Test TenantContextError inherits from ClientError."""
        error = TenantContextError("Context error")
        assert isinstance(error, ClientError)
        assert isinstance(error, Day2Error)
        assert isinstance(error, Exception)

    def test_tenant_context_error_with_request_id_only(self):
        """Test TenantContextError with request ID but default status."""
        error = TenantContextError("No tenant specified", request_id="req-456")
        assert error.status_code == 400
        assert error.request_id == "req-456"
        assert str(error) == "No tenant specified (Status: 400, RequestId: req-456)"


class TestExceptionRaising:
    """Test cases for raising and catching exceptions."""

    def test_raise_and_catch_day2_error(self):
        """Test raising and catching Day2Error."""
        with pytest.raises(Day2Error) as exc_info:
            raise Day2Error("Test error")

        assert str(exc_info.value) == "Test error"

    def test_raise_and_catch_client_error(self):
        """Test raising and catching ClientError."""
        with pytest.raises(ClientError) as exc_info:
            raise ClientError("Client error", 400, "req-123")

        error = exc_info.value
        assert error.status_code == 400
        assert error.request_id == "req-123"

    def test_catch_client_error_as_day2_error(self):
        """Test catching ClientError as Day2Error (inheritance)."""
        with pytest.raises(Day2Error):
            raise ClientError("Error", 400)

    def test_catch_server_error_as_day2_error(self):
        """Test catching ServerError as Day2Error (inheritance)."""
        with pytest.raises(Day2Error):
            raise ServerError("Error", 500)

    def test_catch_specific_exceptions(self):
        """Test catching specific exception types."""
        # ResourceNotFoundError
        with pytest.raises(ResourceNotFoundError):
            raise ResourceNotFoundError("Not found")

        # AuthenticationError
        with pytest.raises(AuthenticationError):
            raise AuthenticationError("Auth failed", 401)

        # TenantContextError
        with pytest.raises(TenantContextError):
            raise TenantContextError("Context error")

        # ValidationError
        with pytest.raises(ValidationError):
            raise ValidationError("Validation failed", 422)
