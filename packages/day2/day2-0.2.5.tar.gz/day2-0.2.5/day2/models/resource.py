"""Resource models for the MontyCloud DAY2 API."""

from typing import List, Union

from pydantic import BaseModel, ConfigDict, Field


class ResourceTypeItem(BaseModel):
    """Represents a single resource type entry returned by list_resource_types operation.

    Attributes:
        label: Display label for the resource type.
        resource_type: Resource type identifier.
    """

    model_config = ConfigDict(extra="allow")

    label: str = Field(alias="Label", description="Display label for the resource type")
    resource_type: str = Field(
        alias="ResourceType", description="Resource type identifier"
    )


class ListResourceTypesOutput(BaseModel):
    """Output model for list_resource_types operation.

    Attributes:
        resource_types: List of resource type entries containing label and identifier.
    """

    model_config = ConfigDict(extra="allow")

    resource_types: List[ResourceTypeItem] = Field(
        alias="ResourceTypes",
        description="List of resource type entries containing label and identifier",
    )


class RegionItem(BaseModel):
    """Represents a single region entry returned by list_regions operation.

    Attributes:
        label: Display label for the region.
        region_code: Region code identifier (e.g., 'us-east-1').
    """

    model_config = ConfigDict(extra="allow")

    label: str = Field(alias="Label", description="Display label for the region")
    region_code: str = Field(
        alias="RegionCode", description="Region code identifier (e.g., 'us-east-1')"
    )


class ListRegionsOutput(BaseModel):
    """Output model for list_regions operation.

    Attributes:
        regions: List of region entries with code and label.
    """

    model_config = ConfigDict(extra="allow")

    regions: List[RegionItem] = Field(
        alias="Regions", description="List of regions with code and label"
    )


class InventorySummaryByResourceType(BaseModel):
    """Summary of inventory by resource type.

    Attributes:
        resource_type: The type of the resource.
        resource_count: The number of resources of this type.
    """

    model_config = ConfigDict(extra="allow")

    resource_type: str = Field(
        ..., alias="ResourceType", description="The type of the resource."
    )
    resource_count: int = Field(
        ..., alias="ResourceCount", description="The number of resources of this type."
    )


class InventorySummaryByRegion(BaseModel):
    """Summary of inventory by region.

    Attributes:
        region_code: The AWS region code (e.g., us-east-1).
        resource_count: The number of resources in this region.
    """

    model_config = ConfigDict(extra="allow")

    region_code: str = Field(
        ..., alias="RegionCode", description="The AWS region code."
    )
    resource_count: int = Field(
        ...,
        alias="ResourceCount",
        description="The number of resources in this region.",
    )


class InventorySummaryByAccountNumber(BaseModel):
    """Summary of inventory by account.

    Attributes:
        account_number: The AWS account number.
        resource_count: The number of resources in this account.
    """

    model_config = ConfigDict(extra="allow")

    account_number: str = Field(
        ..., alias="AccountNumber", description="The AWS account number."
    )
    resource_count: int = Field(
        ...,
        alias="ResourceCount",
        description="The number of resources in this account.",
    )


class GetInventorySummaryOutput(BaseModel):
    """Output model for get_inventory_summary operation.

    Attributes:
        inventory_summary: List of inventory summaries by resource type, region, or account.
    """

    model_config = ConfigDict(extra="allow")

    inventory_summary: Union[
        List[InventorySummaryByResourceType],
        List[InventorySummaryByRegion],
        List[InventorySummaryByAccountNumber],
    ] = Field(
        default=[],
        alias="InventorySummary",
        description="List of inventory summaries by resource type, region, or account.",
    )
