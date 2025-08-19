"""Tenant models for the MontyCloud SDK."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TenantDetails(BaseModel):
    """Details of a tenant.

    Attributes:
        id: Unique identifier of the tenant
        name: Name of the tenant
        description: Description of the tenant
        parent_tenant_id: ID of the parent tenant if this is a sub-tenant
        created_at: Timestamp when the tenant was created
        created_by: User who created the tenant
        modified_at: Timestamp of last modification
        modified_by: User who last modified the tenant
        owner: Owner of the tenant
        document_url: URL to the tenant's documentation
        feature: Feature set associated with the tenant
        category_id: Category identifier for the tenant
    """

    id: Optional[str] = Field(None, alias="ID")
    name: str = Field(alias="Name")
    description: Optional[str] = Field(None, alias="Description")
    parent_tenant_id: Optional[str] = Field(None, alias="ParentTenantId")
    created_at: Optional[datetime] = Field(None, alias="CreatedAt")
    created_by: Optional[str] = Field(None, alias="CreatedBy")
    modified_at: Optional[datetime] = Field(None, alias="ModifiedAt")
    modified_by: Optional[str] = Field(None, alias="ModifiedBy")
    owner: Optional[str] = Field(None, alias="Owner")
    document_url: Optional[str] = Field(None, alias="DocumentURL")
    feature: Optional[str] = Field(None, alias="Feature")
    category_id: Optional[str] = Field(None, alias="CategoryId")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class ListTenantsOutput(BaseModel):
    """Output of list_tenants operation.

    Attributes:
        tenants: List of tenant details
        next_page_token: Token for fetching the next page of results
    """

    tenants: List[TenantDetails] = Field(alias="Tenants", default=[])
    next_page_token: Optional[str] = Field(None, alias="NextPageToken")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class GetTenantOutput(TenantDetails):
    """Output of get_tenant operation.

    This class inherits all attributes from TenantDetails without modification.
    See TenantDetails for the complete list of attributes.
    """


class Account(BaseModel):
    """Details of an account.

    Attributes:
        number: AWS account number
        name: Account name
        status: Current status of the account
        type: Type of the account
        permission_model: Permission model used for the account
        onboarded_date: Date when the account was onboarded
    """

    number: str = Field(alias="Number")
    name: str = Field(alias="Name")
    status: str = Field(alias="Status")
    type: str = Field(alias="Type")
    permission_model: str = Field(alias="PermissionModel")
    onboarded_date: str = Field(alias="OnboardedDate")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class ListAccountsOutput(BaseModel):
    """Output of list_accounts operation.

    Attributes:
        accounts: List of account details
        has_more: Whether there are more pages of results
        page_number: Current page number
    """

    accounts: List[Account] = Field(alias="Accounts", default=[])
    has_more: bool = Field(alias="HasMore", default=False)
    page_number: int = Field(alias="PageNumber")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")
