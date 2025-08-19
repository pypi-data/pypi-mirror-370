"""Cost commands for the MontyCloud DAY2 CLI."""

from typing import Optional

import click
from rich.console import Console

from day2.exceptions import Day2Error, ProfileNotFoundError
from day2_cli.utils.context import get_enhanced_context, with_common_options
from day2_cli.utils.exit_codes import handle_error_with_exit
from day2_cli.utils.output_formatter import format_item_output

console = Console()


@click.group()
def cost() -> None:
    """Cost commands."""


@cost.command("get-cost-by-charge-type")
@click.option(
    "--cloud-provider",
    type=str,
    default="AWS",
    help="Cloud provider (e.g., AWS, Azure). Default is AWS.",
)
@click.option(
    "--start-date",
    type=str,
    required=True,
    help="Start date in YYYY-MM-DD format.",
)
@click.option(
    "--end-date",
    type=str,
    required=True,
    help="End date in YYYY-MM-DD format.",
)
@with_common_options(include_tenant_id=True)
def get_cost_by_charge_type(
    cloud_provider: str,
    start_date: str,
    end_date: str,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """Get cost breakdown by charge type for a tenant.

    TENANT-ID: The ID of the tenant to fetch cost data for.
    """
    try:
        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        # Fetch cost data
        result = session.cost.get_cost_by_charge_type(
            tenant_id=resolved_tenant_id,
            cloud_provider=cloud_provider,
            start_date=start_date,
            end_date=end_date,
        )

        # Convert cost data to dictionary for output
        cost_dict = {
            "total_cost": result.total_cost,
            "usage": result.usage,
            "bundled_discount": result.bundled_discount,
            "credit": result.credit,
            "discount": result.discount,
            "discounted_usage": result.discounted_usage,
            "fee": result.fee,
            "refund": result.refund,
            "ri_fee": result.ri_fee,
            "tax": result.tax,
            "savings_plan_upfront_fee": result.savings_plan_upfront_fee,
            "savings_plan_recurring_fee": result.savings_plan_recurring_fee,
            "savings_plan_covered_usage": result.savings_plan_covered_usage,
            "savings_plan_negation": result.savings_plan_negation,
            "spp_discount": result.spp_discount,
            "distributor_discount": result.distributor_discount,
        }

        # Format and output the cost data
        format_item_output(
            cost_dict, f"Cost Breakdown for Tenant: {resolved_tenant_id}", output_format
        )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)
