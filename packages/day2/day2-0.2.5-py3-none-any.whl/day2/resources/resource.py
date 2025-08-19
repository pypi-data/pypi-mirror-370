"""Resource client for the MontyCloud DAY2 API."""

from typing import TYPE_CHECKING, Dict, List, Optional, Union

from day2.client.base import BaseClient
from day2.models.resource import (
    GetInventorySummaryOutput,
    ListRegionsOutput,
    ListResourceTypesOutput,
)

if TYPE_CHECKING:
    from day2.session import Session


class ResourceClient(BaseClient):
    """Client for interacting with Resource service."""

    def __init__(self, session: "Session"):
        """Initialize a new ResourceClient.

        Args:
            session: MontyCloud session.
        """
        super().__init__(session, "resource")

    def list_resource_types(
        self, tenant_id: str, cloud_provider: str = "AWS"
    ) -> ListResourceTypesOutput:
        """List resource types supported by MontyCloud for a specific cloud provider.

        Args:
            tenant_id: ID of the tenant to list resource types for.
            cloud_provider: Cloud provider for which to list resource types (default is "AWS").

        Returns:
            ListResourceTypesOutput: Object containing list of resource types.

        Raises:
            ResourceNotFoundError: If the tenant does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.resource
            >>> response = client.list_resource_types("tenant-123", cloud_provider="AWS")
            >>> for resource_type in response.resource_types:
            ...     print(f"label: {resource_type.label}")
            ...     print(f"resource_type: {resource_type.resource_type}")
        """
        params = {"CloudProvider": cloud_provider}
        response = self._make_request(
            "GET", f"tenants/{tenant_id}/resources/resource-types", params=params
        )
        return ListResourceTypesOutput.model_validate(response)

    def list_regions(
        self, tenant_id: str, cloud_provider: str = "AWS"
    ) -> ListRegionsOutput:
        """List available regions for a tenant from a specific cloud provider.

        This method retrieves the list of regions available for resources
        in the specified tenant environment for the given cloud provider.

        Args:
            tenant_id: The ID of the tenant to get regions for.
            cloud_provider: Cloud provider for which to get regions (default is "AWS").

        Returns:
            ListRegionsOutput: Object containing a list of regions with their
                codes and display names.

        Raises:
            ResourceNotFoundError: If the tenant does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.resource
            >>> response = client.list_regions("tenant-123", cloud_provider="AWS")
            >>> for region in response.regions:
            ...     print(f"label: {region.label}")
            ...     print(f"region_code: {region.region_code}")
        """
        params = {"CloudProvider": cloud_provider}
        response = self._make_request(
            "GET", f"tenants/{tenant_id}/resources/regions", params=params
        )
        return ListRegionsOutput.model_validate(response)

    def get_inventory_summary(
        self,
        tenant_id: str,
        cloud_provider: str = "AWS",
        summary_type: str = "By-Account",
        resource_type: Optional[List[str]] = None,
        account_number: Optional[List[str]] = None,
        region_code: Optional[List[str]] = None,
    ) -> GetInventorySummaryOutput:
        """Get inventory summary for a specific tenant, with optional filters.

        Args:
            tenant_id: ID of the tenant to get inventory summary for.
            cloud_provider: Cloud provider to filter by (default: "AWS").
            summary_type: Type of summary to retrieve. Allowed values: "By-ResourceType", "By-Region", "By-Account" (default: "By-Account").
            resource_type: List of resource types to filter by. Allowed values are those returned by `list_resource_types` method.
            account_number: List of account numbers to filter by.
            region_code: List of region codes to filter by. Allowed values are those returned by `list_regions` method.

        Returns:
            GetInventorySummaryOutput: Object containing inventory summary.

        Raises:
            ResourceNotFoundError: If the tenant does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.resource
            >>> response = client.get_inventory_summary(
            ...     tenant_id="your-tenant-id",
            ...     cloud_provider="AWS",
            ...     summary_type="By-Account",
            ...     resource_type=["Lambda"],
            ...     account_number=["123456789012"],
            ...     region_code=["us-east-1"]
            ... )
            >>> print(response)
        """
        params: Dict[str, Union[str, List[str]]] = {
            "CloudProvider": cloud_provider,
            "SummaryType": summary_type,
        }

        if resource_type:
            params["ResourceType"] = resource_type
        if account_number:
            params["AccountNumber"] = account_number
        if region_code:
            params["RegionCode"] = region_code

        response = self._make_request(
            "GET", f"tenants/{tenant_id}/resources/inventory-summary", params=params
        )
        return GetInventorySummaryOutput.model_validate(response)
