"""Tenant resource implementation for the MontyCloud DAY2 SDK."""

from typing import Optional

from day2.client.base import BaseClient
from day2.models.tenant import GetTenantOutput, ListAccountsOutput, ListTenantsOutput
from day2.session import Session


class TenantClient(BaseClient):
    """Client for interacting with the Tenant service."""

    def __init__(self, session: Session) -> None:
        """Initialize a new TenantClient.

        Args:
            session: MontyCloud session.
        """
        super().__init__(session, "tenant")

    def list_tenants(
        self, page_size: int = 10, page_token: Optional[str] = None
    ) -> ListTenantsOutput:
        """List tenants that the user has access to.

        Args:
            page_size: Number of tenants to be fetched in a page (default: 10).
            page_token: Token for pagination.

        Returns:
            ListTenantsOutput: Object containing list of tenants and pagination info.

        Raises:
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.tenant
            >>> response = client.list_tenants(page_size=10)
            >>> for tenant in response.tenants:
            ...     print(f"{tenant.id}: {tenant.name}")
            >>> # To get the next page of results:
            >>> if response.next_page_token:
            ...     next_page = client.list_tenants(page_size=10, page_token=response.next_page_token)
        """
        params: dict[str, object] = {
            "PageSize": page_size,
        }

        if page_token:
            params["PageToken"] = page_token

        response = self._make_request("GET", "tenants/", params=params)
        return ListTenantsOutput.model_validate(response)

    def get_tenant(self, tenant_id: str) -> GetTenantOutput:
        """Get details of a specific tenant.

        Args:
            tenant_id: ID of the tenant to get details for.

        Returns:
            GetTenantOutput: Object containing tenant details.

        Raises:
            ResourceNotFoundError: If the tenant does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.tenant
            >>> response = client.get_tenant("tenant-123")
            >>> print(f"Tenant name: {response.name}")
        """
        # The endpoint for getting tenant details is directly using the tenant ID in the path
        response = self._make_request("GET", f"tenants/{tenant_id}")
        return GetTenantOutput.model_validate(response)

    def list_accounts(
        self, tenant_id: str, page_size: int = 10, page_number: int = 1
    ) -> ListAccountsOutput:
        """List accounts associated with a specific tenant.

        Args:
            tenant_id: ID of the tenant to list accounts for.
            page_size: Number of accounts to be fetched in a page (default: 10).
            page_number: Page number for pagination (default: 1).

        Returns:
            ListAccountsOutput: Object containing list of accounts and pagination info.

        Raises:
            ResourceNotFoundError: If the tenant does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.tenant
            >>> response = client.list_accounts("tenant-123", page_size=10)
            >>> for account in response.accounts:
            ...     print(f"{account.number}: {account.name}")
        """
        params: dict[str, object] = {
            "PageSize": page_size,
            "PageNumber": page_number,
        }

        response = self._make_request(
            "GET", f"tenants/{tenant_id}/accounts", params=params
        )
        return ListAccountsOutput.model_validate(response)
