from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class Policy(BaseModel):
    """
    Details of a policy associated with a compliance finding.

    Attributes:
        policy_group: The group this policy belongs to.
        policy_id: The unique identifier for the policy.
    """

    policy_group: str = Field(..., alias="PolicyGroup")
    policy_id: str = Field(..., alias="PolicyId")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class ComplianceBotFinding(BaseModel):
    """
    Details of a Compliance Bot finding.

    Attributes:
        account_number: AWS account number where the finding was detected.
        compliance_type: The compliance type. Allowed values: "Non-Compliant", "Compliant".
        config_rule_invoked_time: The time the config rule was invoked.
        config_rule_name: Name of the AWS Config rule.
        created_at: Timestamp when the finding was created.
        description: Description of the finding.
        id: Unique identifier for the finding.
        metadata: Additional metadata for the finding.
        policies: List of associated policies.
        region_code: AWS region code.
        remediation_task_exists: Whether a remediation task exists for this finding.
        resource_id: ID of the affected resource.
        resource_type: Type of the affected resource.
        result_recorded_time: The time the result was recorded.
        updated_at: Timestamp when the finding was last updated.
    """

    account_number: str = Field(..., alias="AccountNumber")
    compliance_type: str = Field(..., alias="ComplianceType")
    config_rule_invoked_time: datetime = Field(..., alias="ConfigRuleInvokedTime")
    config_rule_name: str = Field(..., alias="ConfigRuleName")
    created_at: datetime = Field(..., alias="CreatedAt")
    description: str = Field(..., alias="Description")
    id: str = Field(..., alias="Id")
    metadata: str = Field(..., alias="Metadata")
    policies: List[Policy] = Field(..., alias="Policies")
    region_code: str = Field(..., alias="RegionCode")
    remediation_task_exists: bool = Field(..., alias="RemediationTaskExists")
    resource_id: str = Field(..., alias="ResourceId")
    resource_type: str = Field(..., alias="ResourceType")
    result_recorded_time: datetime = Field(..., alias="ResultRecordedTime")
    updated_at: datetime = Field(..., alias="UpdatedAt")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class ListComplianceBotFindingsOutput(BaseModel):
    """
    Output model for the list_compliance_bot_findings operation.

    Attributes:
        page_number: The current page number of the results.
        has_more: Whether there are more findings to retrieve.
        findings: List of Compliance Bot findings.
    """

    page_number: int = Field(..., alias="PageNumber")
    has_more: bool = Field(..., alias="HasMore")
    findings: List[ComplianceBotFinding] = Field(..., alias="Findings")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class ResourceType(BaseModel):
    """
    Details of a resource type supported by the Compliance Bot.

    Attributes:
        label: The display label for the resource type.
        resource_type: The resource type identifier.
    """

    label: str = Field(..., alias="Label")
    resource_type: str = Field(..., alias="ResourceType")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class ListComplianceBotResourceTypesOutput(BaseModel):
    """
    Output model for the list_compliance_bot_resource_types operation.

    Attributes:
        resource_types: List of resource types supported by the Compliance Bot.
    """

    resource_types: List[ResourceType] = Field(..., alias="ResourceTypes")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class ListComplianceBotPolicyGroupsOutput(BaseModel):
    """
    Output model for the list_compliance_bot_policy_groups operation.

    Attributes:
        policy_groups: List of policy groups.
    """

    policy_groups: List[str] = Field(..., alias="PolicyGroups")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")
