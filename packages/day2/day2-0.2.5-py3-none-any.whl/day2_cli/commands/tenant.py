"""Tenant commands for the MontyCloud DAY2 CLI."""

from typing import Optional

import click
from rich.console import Console

from day2.exceptions import Day2Error, ProfileNotFoundError
from day2_cli.utils.context import get_enhanced_context, with_common_options
from day2_cli.utils.exit_codes import handle_error_with_exit
from day2_cli.utils.output_formatter import format_item_output, format_list_output

console = Console()


@click.group()
def tenant() -> None:
    """Tenant commands."""


@tenant.command("list")
@click.option("--page-token", type=str, default=None, help="Page token for pagination")
@click.option("--page-size", type=int, default=10, help="Page size")
@with_common_options()
def list_tenants(
    page_token: str,
    page_size: int,
    output: Optional[str] = None,
    profile: Optional[str] = None,
) -> None:
    """List tenants.

    This command lists tenants that the user has access to.
    """
    try:
        # Get enhanced context with both global and local options
        context = get_enhanced_context(output=output, profile=profile)
        session = context["session"]
        output_format = context["output_format"]
        result = session.tenant.list_tenants(page_size=page_size, page_token=page_token)

        if not result.tenants:
            console.print("[yellow]No tenants found.[/yellow]")
            return

        # Convert tenant objects to dictionaries for output
        tenant_list = []
        for tenant_item in result.tenants:
            tenant_dict = {
                "id": tenant_item.id,
                "name": tenant_item.name,
                "owner": tenant_item.owner or "N/A",
                "feature": tenant_item.feature,
                "created_by": tenant_item.created_by,
            }
            tenant_list.append(tenant_dict)

        # Define columns for table output
        columns = {
            "id": "ID",
            "name": "Name",
            "owner": "Owner",
            "feature": "Feature",
            "created_by": "Created By",
        }

        # Format and output the tenant list
        format_list_output(tenant_list, "Tenants", columns, output_format)

        if result.next_page_token:
            console.print(
                f"[yellow]More results available. Use --page-token={result.next_page_token} to get the next page.[/yellow]"
            )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)


@tenant.command("get")
@with_common_options(include_tenant_id=True)
def get_tenant(
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """Get details of a specific tenant.

    TENANT-ID: ID of the tenant to get details for. If not provided, uses the default tenant from the current profile.
    """
    try:
        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        result = session.tenant.get_tenant(resolved_tenant_id)

        # Convert tenant object to dictionary for output
        tenant_dict = {
            "id": result.id,
            "name": result.name,
            "description": result.description or "N/A",
            "owner": result.owner or "N/A",
            "parent_tenant_id": result.parent_tenant_id or "N/A",
            "feature": result.feature,
            "category_id": result.category_id or "N/A",
            "created_by": result.created_by,
            "created_at": str(result.created_at),
            "modified_by": result.modified_by or "N/A",
            "modified_at": str(result.modified_at),
        }

        # Format and output the tenant details
        format_item_output(
            tenant_dict, f"Tenant: {result.name} (ID: {result.id})", output_format
        )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)


@tenant.command("list-accounts")
@click.option("--page-size", type=int, default=10, help="Page size, Default is 10")
@click.option(
    "--page-number",
    type=int,
    default=1,
    help="Page number for pagination, Default is 1",
)
@with_common_options(include_tenant_id=True)
def list_accounts(
    page_size: int = 10,
    page_number: int = 1,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """List accounts for a specific tenant.

    TENANT-ID: ID of the tenant to list accounts for. If not provided, uses the default tenant from the current profile.
    """
    try:
        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        result = session.tenant.list_accounts(
            tenant_id=resolved_tenant_id, page_size=page_size, page_number=page_number
        )

        if not result.accounts:
            console.print(
                "[yellow]No accounts found for the specified tenant.[/yellow]"
            )
            return

        # Convert account objects to dictionaries for output
        account_list = []
        for account_item in result.accounts:
            account_dict = {
                "number": account_item.number,
                "name": account_item.name,
                "status": account_item.status,
                "type": account_item.type,
                "permission_model": account_item.permission_model,
                "onboarded_date": account_item.onboarded_date,
            }
            account_list.append(account_dict)

        # Define columns for table output
        columns = {
            "number": "Number",
            "name": "Name",
            "status": "Status",
            "type": "Type",
            "permission_model": "Permission Model",
            "onboarded_date": "Onboarded Date",
        }

        # Format and output the account list
        format_list_output(
            account_list,
            f"Accounts for Tenant: {resolved_tenant_id}",
            columns,
            output_format,
        )

        # Check if there are more accounts
        if result.has_more:
            console.print(
                f"[yellow]More results available. Use --page-number={result.page_number + 1} to get the next page.[/yellow]"
            )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)
