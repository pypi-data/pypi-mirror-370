"""Bot commands for the MontyCloud DAY2 CLI."""

import json
from typing import Optional

import click
from rich.console import Console

from day2.exceptions import Day2Error, ProfileNotFoundError
from day2_cli.utils.context import get_enhanced_context, with_common_options
from day2_cli.utils.exit_codes import handle_error_with_exit
from day2_cli.utils.output_formatter import format_list_output, format_simple_output

console = Console()


@click.group()
def bot() -> None:
    """Bot commands."""


@bot.command("list-compliance-resource-types")
@with_common_options(include_tenant_id=True)
def resource_types(
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """List resource types for the compliance bot."""
    try:
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        result = session.bot.list_compliance_bot_resource_types(resolved_tenant_id)

        if not result.resource_types:
            format_simple_output(
                "No resource types found.", format_override=output_format
            )
            return

        resource_type_list = [
            {"resource_type": rt.resource_type, "label": rt.label}
            for rt in result.resource_types
        ]
        columns = {
            "resource_type": "Resource Type",
            "label": "Label",
        }

        format_list_output(
            resource_type_list,
            "Compliance Bot Resource Types",
            columns,
            output_format,
        )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)


@bot.command("list-compliance-policy-groups")
@with_common_options(include_tenant_id=True)
def policy_groups(
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """List policy groups for the compliance bot."""
    try:
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        result = session.bot.list_compliance_bot_policy_groups(resolved_tenant_id)

        if not result.policy_groups:
            format_simple_output(
                "No policy groups found.", format_override=output_format
            )
            return

        if output_format == "json":
            console.print(json.dumps({"PolicyGroups": result.policy_groups}, indent=2))
        else:
            policy_group_list = [
                {"policy_groups": group} for group in result.policy_groups
            ]
            columns = {
                "policy_groups": "Policy Groups",
            }
            format_list_output(
                policy_group_list,
                "Compliance Bot Policy Groups",
                columns,
                output_format,
            )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)


@bot.command("list-compliance-findings")
@click.option(
    "--status",
    type=str,
    help="Compliance type to filter findings by (Compliant, Non-Compliant)",
)
@click.option(
    "--account-number", type=str, help="AWS account number to filter findings by"
)
@click.option("--region-code", type=str, help="AWS region code to filter findings by")
@click.option(
    "--policy-group",
    type=str,
    help="Policy group to filter findings by. Allowed values are the values returned by the `day2 bot list-compliance-policy-groups` command.",
)
@click.option(
    "--resource-type",
    type=str,
    help="Resource type to filter findings by. Allowed values are the values returned by the `day2 bot list-compliance-resource-types` command.",
)
@click.option("--resource-id", type=str, help="Resource ID to filter findings by")
@click.option(
    "--page-size",
    type=int,
    default=10,
    help="Number of findings per page (default: 10)",
)
@click.option(
    "--page-number", type=int, default=1, help="Page number to fetch (default: 1)"
)
@with_common_options(include_tenant_id=True)
def findings(
    status: Optional[str],
    account_number: Optional[str],
    region_code: Optional[str],
    policy_group: Optional[str],
    resource_type: Optional[str],
    resource_id: Optional[str],
    page_size: int,
    page_number: int,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """List the compliance bot findings."""
    try:
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        result = session.bot.list_compliance_bot_findings(
            tenant_id=resolved_tenant_id,
            status=status,
            account_number=account_number,
            region_code=region_code,
            policy_group=policy_group,
            resource_type=resource_type,
            resource_id=resource_id,
            page_size=page_size,
            page_number=page_number,
        )

        if not result.findings:
            format_simple_output("No findings found.", format_override=output_format)
            return

        findings_list = []
        for finding in result.findings:
            findings_list.append(
                {
                    "id": finding.id,
                    "account_number": finding.account_number,
                    "compliance_type": finding.compliance_type,
                    "config_rule_invoked_time": str(finding.config_rule_invoked_time),
                    "config_rule_name": finding.config_rule_name,
                    "created_at": str(finding.created_at),
                    "updated_at": str(finding.updated_at),
                    "description": finding.description,
                    "metadata": finding.metadata,
                    "region_code": finding.region_code,
                    "remediation_task_exists": finding.remediation_task_exists,
                    "resource_id": finding.resource_id,
                    "resource_type": finding.resource_type,
                    "result_recorded_time": str(finding.result_recorded_time),
                    "policy_groups": (
                        "; ".join([p.policy_group for p in finding.policies])
                        if finding.policies
                        else ""
                    ),
                }
            )

        # Only show a subset of columns for table output, all for json
        if output_format != "json":
            columns = {
                "id": "Finding ID",
                "account_number": "Account",
                "compliance_type": "Compliance Type",
                "config_rule_name": "Config Rule Name",
                "description": "Description",
                "region_code": "Region",
                "remediation_task_exists": "Remediation Task Exists",
                "resource_id": "Resource ID",
                "resource_type": "Resource Type",
                "policy_groups": "Policy Groups",
            }
        else:
            columns = {
                "id": "Finding ID",
                "account_number": "Account",
                "compliance_type": "Compliance Type",
                "config_rule_invoked_time": "Config Rule Invoked",
                "config_rule_name": "Config Rule Name",
                "created_at": "Created At",
                "updated_at": "Updated At",
                "description": "Description",
                "metadata": "Metadata",
                "region_code": "Region",
                "remediation_task_exists": "Remediation Task Exists",
                "resource_id": "Resource ID",
                "resource_type": "Resource Type",
                "result_recorded_time": "Result Recorded",
                "policy_groups": "Policy Groups",
            }

        format_list_output(
            findings_list,
            "Compliance Bot Findings",
            columns,
            output_format,
        )

        # Note for table output about detailed fields
        if output_format != "json":
            console.print(
                "[green]Please use --output json for detailed information of findings.[/green]"
            )

        # Check if there are more results
        if result.has_more:
            console.print(
                f"[yellow]More results available. Use --page-number={result.page_number + 1} to get the next page.[/yellow]"
            )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)
