"""Base client implementation for the MontyCloud DAY2 SDK."""

import json
import logging

# Use TYPE_CHECKING to avoid circular imports
from typing import TYPE_CHECKING, Any, Dict

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from day2.exceptions import (
    AuthenticationError,
    ClientError,
    ResourceNotFoundError,
    ServerError,
    ValidationError,
)

if TYPE_CHECKING:
    from day2.session import Session

logger = logging.getLogger(__name__)


class BaseClient:
    """Base client for MontyCloud API services."""

    def __init__(self, session: "Session", service_name: str):
        """Initialize a new client.

        Args:
            session: MontyCloud session.
            service_name: Name of the service this client will interact with.
        """
        self.session = session
        self.service_name = service_name
        self._config = session._config

    def _get_endpoint_url(self, endpoint: str) -> str:
        """Get the full URL for an endpoint.

        Args:
            endpoint: API endpoint path.

        Returns:
            Full URL for the endpoint.
        """
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        # For MontyCloud API, we don't include the service name in the URL
        return f"{self._config.api_url}/{endpoint}"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests.

        Returns:
            Headers dictionary including authentication and tenant context.
        """
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": (
                str(self.session.credentials.api_key)
                if self.session.credentials.api_key
                else ""
            ),
        }

        # Add User-Agent header
        from day2._version import __version__

        user_agent = f"day2-sdk/{__version__}"
        if (
            hasattr(self.session, "user_agent_suffix")
            and self.session.user_agent_suffix
        ):
            user_agent += f" {self.session.user_agent_suffix}"
        headers["User-Agent"] = user_agent

        # Add Authorization header if available
        # Use auth_token (which is actually the api_secret_key internally)
        if (
            hasattr(self.session.credentials, "secret_key")
            and self.session.credentials.secret_key
        ):
            headers["Authorization"] = self.session.credentials.secret_key

        if self.session.tenant_id:
            headers["x-tenant-id"] = str(self.session.tenant_id)

        return headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions.

        Args:
            response: Response from API request.

        Returns:
            Response data as dictionary.

        Raises:
            ValidationError: If the request was invalid (400).
            AuthenticationError: If authentication failed (401).
            ResourceNotFoundError: If the requested resource was not found (404).
            ClientError: For other client errors (4xx).
            ServerError: For server errors (5xx).
        """
        request_id = response.headers.get("x-request-id")

        try:
            data: Dict[str, Any] = response.json()
            logger.debug("Response data: %s", json.dumps(data, indent=2)[:1000])
        except ValueError:
            data = {"Message": response.text}
            logger.debug("Response text: %s", response.text[:1000])

        if 400 <= response.status_code < 500:
            message = data.get("Message", "Client error")

            if response.status_code == 400:
                raise ValidationError(message, response.status_code, request_id)
            if response.status_code in (401, 403):
                raise AuthenticationError(message, response.status_code, request_id)
            if response.status_code == 404:
                raise ResourceNotFoundError(message, response.status_code, request_id)
            raise ClientError(message, response.status_code, request_id)

        if response.status_code >= 500:
            message = data.get("Message", "Server error")
            raise ServerError(message, response.status_code, request_id)

        return dict(data)

    def _request_with_retry(
        self, method: str, url: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Make an API request with retry logic based on configuration.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            **kwargs: Additional arguments to pass to requests.request

        Returns:
            Dict containing the parsed response

        Raises:
            ClientError: For client errors (4xx)
            ServerError: For server errors (5xx)
        """

        # Define the actual request function to retry
        def _do_request() -> Dict[str, Any]:
            headers = self._get_headers()

            # Update headers with any provided in kwargs
            request_kwargs = kwargs.copy()
            if "headers" in request_kwargs:
                headers.update(request_kwargs.pop("headers"))

            # Log request details
            logger.debug(
                "Making %s request to %s with headers %s and kwargs %s",
                method,
                url,
                headers,
                request_kwargs,
            )

            try:
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    timeout=self._config.timeout,
                    **request_kwargs,
                )

                # Log response details
                logger.debug("Received response with status %s", response.status_code)
                logger.debug("Response headers: %s", response.headers)
                logger.debug("Response content: %s", response.text[:1000])

                return self._handle_response(response)
            except requests.RequestException as e:
                logger.error("Request failed: %s", str(e))
                raise ServerError(str(e), 0, None) from e

        # Create a retry object with config values
        r = retry(
            stop=stop_after_attempt(self._config.max_retries),
            wait=wait_exponential(
                multiplier=self._config.retry_backoff_factor,
                min=self._config.retry_min_delay,
                max=self._config.retry_max_delay,
            ),
            retry=retry_if_exception_type(ServerError),
            reraise=True,
        )

        # Apply retry to our request function and call it
        return r(_do_request)()

    def _make_request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Make an API request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            endpoint: API endpoint path.
            **kwargs: Additional arguments to pass to requests.

        Returns:
            Response data as dictionary.
        """
        # Handle JSON data
        if "json_data" in kwargs:
            kwargs["json"] = kwargs.pop("json_data")

        url = self._get_endpoint_url(endpoint)
        logger.debug("Making request to %s %s", method, url)
        # Pass the full URL to the request method
        return self._request_with_retry(method, url, **kwargs)
