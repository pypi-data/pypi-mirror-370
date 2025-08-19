"""Resource commands for the MontyCloud DAY2 CLI."""

from typing import List, Optional

import click
from rich.console import Console

from day2.exceptions import Day2Error
from day2_cli.utils.context import get_enhanced_context, with_common_options
from day2_cli.utils.exit_codes import handle_error_with_exit
from day2_cli.utils.output_formatter import format_list_output

console = Console()


@click.group()
def resource() -> None:
    """Resource commands."""


@resource.command("list-resource-types")
@click.option(
    "--cloud-provider",
    default="AWS",
    help="Cloud provider for which to list resource types (default is 'AWS').",
)
@with_common_options(include_tenant_id=True)
def list_resource_types(
    cloud_provider: str,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """List resource types supported by MontyCloud for a specific cloud provider.

    If --tenant-id is not provided, uses the default tenant configured with 'day2 profile create' or 'day2 auth login'.
    """
    try:
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        # Call the updated client method that returns a list of objects
        result = session.resource.list_resource_types(
            resolved_tenant_id, cloud_provider
        )

        # Convert resource types list of objects to list of dictionaries for the formatter
        resource_types_data = [
            {"resource_type": resource_type.resource_type, "label": resource_type.label}
            for resource_type in sorted(
                result.resource_types, key=lambda resource_type: resource_type.label
            )
        ]

        # Define column mapping for the formatter
        columns = {
            "resource_type": "Resource Type",
            "label": "Label",
        }

        # Format and output the results
        format_list_output(
            items=resource_types_data,
            title=f"Resource Types for Tenant ({cloud_provider}):\n{resolved_tenant_id}",
            columns=columns,
            format_override=output_format,
        )

    except Day2Error as e:
        handle_error_with_exit(e)


@resource.command("list-regions")
@click.option(
    "--cloud-provider",
    default="AWS",
    help="Cloud provider for which to get regions (default is 'AWS').",
)
@with_common_options(include_tenant_id=True)
def list_regions(
    cloud_provider: str,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """List available regions for a tenant from a specific cloud provider."""
    try:
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        # Get regions from the API
        regions_result = session.resource.list_regions(
            resolved_tenant_id, cloud_provider
        )

        # Convert to list format for output formatting (already list-of-objects)
        regions_data = [
            {"region_code": region.region_code, "label": region.label}
            for region in sorted(
                regions_result.regions, key=lambda region: region.label
            )
        ]

        # Define columns for output
        columns = {
            "region_code": "Region Code",
            "label": "Region Name",
        }

        # Format and output the results
        format_list_output(
            items=regions_data,
            title=f"{cloud_provider} Regions for Tenant:\n{resolved_tenant_id}",
            columns=columns,
            format_override=output_format,
        )

    except Day2Error as e:
        handle_error_with_exit(e)


@resource.command("get-inventory-summary")
@click.option(
    "--cloud-provider",
    type=str,
    default="AWS",
    help="Cloud provider to filter by. Default is AWS.",
)
@click.option(
    "--summary-type",
    type=str,
    default="By-Account",
    help='Type of summary to retrieve. Allowed values: "By-ResourceType", "By-Region", "By-Account". Default is By-Account.',
)
@click.option(
    "--resource-type",
    type=str,
    multiple=True,
    help="Filter by resource type (can be used multiple times). Allowed values are the resource types returned by the `day2 resource list-resource-types` command.",
)
@click.option(
    "--account-number",
    type=str,
    multiple=True,
    help="Filter by account number (can be used multiple times)",
)
@click.option(
    "--region-code",
    type=str,
    multiple=True,
    help="Filter by region code (can be used multiple times). Allowed values are the region codes returned by the `day2 resource list-regions` command.",
)
@with_common_options(include_tenant_id=True)
def get_inventory_summary(
    cloud_provider: str,
    summary_type: str,
    resource_type: List[str],
    account_number: List[str],
    region_code: List[str],
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """Get inventory summary for a specific tenant.
    TENANT-ID: ID of the tenant to get inventory summary for. If not provided, uses the default tenant from the current profile.
    """
    try:
        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        result = session.resource.get_inventory_summary(
            tenant_id=resolved_tenant_id,
            cloud_provider=cloud_provider,
            summary_type=summary_type,
            resource_type=list(resource_type) if resource_type else None,
            account_number=list(account_number) if account_number else None,
            region_code=list(region_code) if region_code else None,
        )

        if not result.inventory_summary:
            console.print(
                "[yellow]No inventory summary found for the specified tenant and filters.[/yellow]"
            )
            return

        # Prepare data for output
        inventory_list = []
        columns = {}  # Define columns here to ensure it's always initialized
        for item in result.inventory_summary:
            if summary_type == "By-ResourceType":
                inventory_list.append(
                    {
                        "resource_type": item.resource_type,
                        "resource_count": item.resource_count,
                    }
                )
                columns = {"resource_type": "Resource Type", "resource_count": "Count"}
            elif summary_type == "By-Region":
                inventory_list.append(
                    {
                        "region_code": item.region_code,
                        "resource_count": item.resource_count,
                    }
                )
                columns = {"region_code": "Region Code", "resource_count": "Count"}
            elif summary_type == "By-Account":
                inventory_list.append(
                    {
                        "account_number": item.account_number,
                        "resource_count": item.resource_count,
                    }
                )
                columns = {
                    "account_number": "Account Number",
                    "resource_count": "Count",
                }
            else:
                console.print("[red]Invalid summary type.[/red]")
                return

        # Format and output the inventory summary
        format_list_output(
            inventory_list,
            f"Inventory Summary for Tenant: {resolved_tenant_id}",
            columns,
            output_format,
        )

    except Day2Error as e:
        handle_error_with_exit(e)
