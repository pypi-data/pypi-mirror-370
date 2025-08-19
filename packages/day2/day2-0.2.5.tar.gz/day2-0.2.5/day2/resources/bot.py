"""Bot service client for MontyCloud Day2 SDK."""

from typing import Dict, Optional, Union

from day2.client.base import BaseClient
from day2.models.bot import (
    ListComplianceBotFindingsOutput,
    ListComplianceBotPolicyGroupsOutput,
    ListComplianceBotResourceTypesOutput,
)
from day2.session import Session


class BotClient(BaseClient):
    """Client for interacting with the Bot service."""

    def __init__(self, session: Session) -> None:
        """Initialize a new BotClient.

        Args:
            session: MontyCloud session.
        """
        super().__init__(session, "bot")

    def list_compliance_bot_findings(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        account_number: Optional[str] = None,
        region_code: Optional[str] = None,
        policy_group: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        page_size: int = 10,
        page_number: int = 1,
    ) -> ListComplianceBotFindingsOutput:
        """List compliance bot findings for a tenant.

        Args:
            tenant_id: ID of the tenant to list findings for.
            status: Compliance type to filter findings by ("Compliant", "Non-Compliant").
            account_number: AWS account number to filter findings by.
            region_code: AWS region code to filter findings by.
            policy_group: Policy group to filter findings by. Allowed values are those returned by the `list_compliance_bot_policy_groups` method.
            resource_type: Resource type to filter findings by. Allowed values are those returned by the `list_compliance_bot_resource_types` method.
            resource_id: Resource ID to filter findings by.
            page_size: Number of findings per page (default: 10).
            page_number: Page number to fetch (default: 1).

        Returns:
            ListComplianceBotFindingsOutput: Contains findings and pagination information.

        Raises:
            ResourceNotFoundError: If the tenant does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.bot
            >>> response = client.list_compliance_bot_findings(
            ...     tenant_id="tenant-123",
            ...     status="Non-Compliant",
            ...     account_number="123456789012",
            ...     region_code="us-east-1",
            ...     policy_group="Security",
            ...     resource_type="S3",
            ...     resource_id="bucket-123",
            ...     page_size=10,
            ...     page_number=1
            ... )
            >>> for finding in response.findings:
            ...     print(f"{finding.id}: {finding.compliance_type} - {finding.resource_type}")

        """
        params: Dict[str, Union[str, int]] = {
            "PageSize": str(page_size),
            "PageNumber": str(page_number),
        }
        if status:
            params["Status"] = status
        if account_number:
            params["AccountNumber"] = account_number
        if region_code:
            params["RegionCode"] = region_code
        if policy_group:
            params["PolicyGroup"] = policy_group
        if resource_type:
            params["ResourceType"] = resource_type
        if resource_id:
            params["ResourceId"] = resource_id

        response = self._make_request(
            "GET",
            f"tenants/{tenant_id}/bots/compliance/findings",
            params=params,
        )
        return ListComplianceBotFindingsOutput.model_validate(response)

    def list_compliance_bot_resource_types(
        self,
        tenant_id: str,
    ) -> ListComplianceBotResourceTypesOutput:
        """List supported resource types for the compliance bot findings in a tenant.

        Args:
            tenant_id: ID of the tenant to list resource types for.

        Returns:
            ListComplianceBotResourceTypesOutput: Contains the list of supported compliance bot resource types.

        Raises:
            ResourceNotFoundError: If the tenant does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.bot
            >>> response = client.list_compliance_bot_resource_types(tenant_id="tenant-123")
            >>> for resource_type in response.resource_types:
            ...     print(f"{resource_type.resource_type}: {resource_type.label}")

        """
        response = self._make_request(
            "GET",
            f"tenants/{tenant_id}/bots/compliance/resource-types",
        )
        return ListComplianceBotResourceTypesOutput.model_validate(response)

    def list_compliance_bot_policy_groups(
        self,
        tenant_id: str,
    ) -> ListComplianceBotPolicyGroupsOutput:
        """List policy groups for the compliance bot findings in a tenant.

        Args:
            tenant_id: ID of the tenant to get policy groups for.

        Returns:
            ListComplianceBotPolicyGroupsOutput: Contains the list of policy group names.

        Raises:
            ResourceNotFoundError: If the tenant does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.bot
            >>> response = client.list_compliance_bot_policy_groups(tenant_id="tenant-123")
            >>> for group in response.policy_groups:
            ...     print(group)

        """
        response = self._make_request(
            "GET",
            f"tenants/{tenant_id}/bots/compliance/policy-groups",
        )
        return ListComplianceBotPolicyGroupsOutput.model_validate(response)
