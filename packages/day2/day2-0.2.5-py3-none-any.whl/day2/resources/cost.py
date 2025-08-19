from typing import Dict

from day2.client.base import BaseClient
from day2.models.cost import GetCostByChargeTypeOutput
from day2.session import Session


class CostClient(BaseClient):
    """Client for interacting with the Cost service."""

    def __init__(self, session: Session) -> None:
        """Initialize a new CostClient.

        Args:
            session: MontyCloud session.
        """
        super().__init__(session, "cost")

    def get_cost_by_charge_type(
        self,
        tenant_id: str,
        cloud_provider: str,
        start_date: str,
        end_date: str,
    ) -> GetCostByChargeTypeOutput:
        """Get cost breakdown by charge type for a tenant.

        Args:
            tenant_id: The ID of the tenant to fetch cost data for.
            cloud_provider: The cloud provider (e.g., "AWS", "Azure").
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.

        Returns:
            GetCostByChargeTypeOutput: Object containing cost breakdown by charge type.

        Raises:
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.cost
            >>> response = client.get_cost_by_charge_type(
            ...     tenant_id="tenant-123",
            ...     cloud_provider="AWS",
            ...     start_date="2023-01-01",
            ...     end_date="2023-01-31"
            ... )
            >>> print(f"Total Cost: {response.total_cost}")
            >>> print(f"Bundled Discount: {response.bundled_discount}")
        """
        params: Dict[str, str] = {
            "CloudProvider": cloud_provider,
            "StartDate": start_date,
            "EndDate": end_date,
        }
        response = self._make_request(
            "GET", f"tenants/{tenant_id}/cost/cost-by-charge-type", params=params
        )
        return GetCostByChargeTypeOutput.model_validate(response)
