"""Assessment commands for the MontyCloud DAY2 CLI."""

import json
import textwrap
from typing import Any, Optional, Tuple

import click
from rich.console import Console
from rich.table import Table

from day2.exceptions import Day2Error, ProfileNotFoundError
from day2.models.assessment import (
    AnswerQuestionInput,
    CreateAssessmentInput,
    GenerateAssessmentReportInput,
    RunAssessmentInput,
)
from day2_cli.utils.context import get_enhanced_context, with_common_options
from day2_cli.utils.exit_codes import ExitCodes, exit_with_error, handle_error_with_exit
from day2_cli.utils.output_formatter import (
    format_item_output,
    format_list_output,
    format_simple_output,
)

console = Console()


@click.group()
def assessment() -> None:
    """Assessment commands."""


@assessment.command("list")
@click.option("--status", help="Filter by assessment status (PENDING or COMPLETED)")
@click.option("--keyword", help="Filter by keyword")
@click.option("--page-token", help="Page token for pagination")
@click.option("--page-size", type=int, default=10, help="Page size")
@with_common_options(include_tenant_id=True)
def list_assessments(
    status: Optional[str],
    keyword: Optional[str],
    page_token: Optional[str],
    page_size: int,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """List assessments for a tenant.

    If --tenant-id is not provided, uses the default tenant configured with 'day2 profile create' or 'day2 auth login'.
    """
    try:
        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        # Call the client method with explicit parameters
        # Ensure status is not None when passing to the API
        status_value = status or "PENDING"  # Default to PENDING if not specified

        result = session.assessment.list_assessments(
            tenant_id=resolved_tenant_id,
            status=status_value,
            keyword=keyword,
            page_token=page_token,
            page_size=page_size,
        )

        if not result.assessments:
            format_simple_output("No assessments found.", format_override=output_format)
            return

        # Convert assessment objects to dictionaries for the formatter
        assessments_data = []
        for assessment_item in result.assessments:
            created_at = (
                assessment_item.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if assessment_item.created_at
                else "N/A"
            )
            last_run_at = (
                assessment_item.last_run_at.strftime("%Y-%m-%d %H:%M:%S")
                if assessment_item.last_run_at
                else "N/A"
            )
            assessments_data.append(
                {
                    "id": assessment_item.id,
                    "name": assessment_item.name,
                    "status": assessment_item.status,
                    "total_questions": assessment_item.total_questions,
                    "answered_questions": assessment_item.answered_questions,
                    "created_at": created_at,
                    "last_run_at": last_run_at,
                }
            )

        # Define column mapping for the formatter
        columns = {
            "id": "ID",
            "name": "Name",
            "status": "Status",
            "total_questions": "Total Questions",
            "answered_questions": "Answered Questions",
            "created_at": "Created At",
            "last_run_at": "Last Run At",
        }

        # Format and output the results
        format_list_output(
            items=assessments_data,
            title=f"Assessments for Tenant: {resolved_tenant_id}",
            columns=columns,
            format_override=output_format,
        )

        # Display pagination information
        if result.next_page_token:
            format_simple_output(
                f"More results available. Use --page-token={result.next_page_token} to get the next page.",
                format_override=output_format,
            )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)


@assessment.command("get")
@click.argument("assessment-id")
@with_common_options(include_tenant_id=True)
def get_assessment(
    assessment_id: str,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """Get details of an assessment.

    If --tenant-id is not provided, uses the default tenant configured with 'day2 profile create' or 'day2 auth login'.

    ASSESSMENT-ID: ID of the assessment to get details for.
    """
    try:
        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        # Call the client method with explicit parameters
        result = session.assessment.get_assessment(resolved_tenant_id, assessment_id)

        # Format timestamps
        created_at = (
            result.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if result.created_at
            else "N/A"
        )
        updated_at = (
            result.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            if result.updated_at
            else "N/A"
        )
        last_run_at = (
            result.last_run_at.strftime("%Y-%m-%d %H:%M:%S")
            if result.last_run_at
            else "N/A"
        )

        # Convert assessment object to dictionary for the formatter
        assessment_data = {
            "ID": result.id,
            "Name": result.name,
            "Description": result.description or "N/A",
            "Status": result.status,
            "Assessment ARN": result.assessment_arn,
            "Owner": result.owner,
            "Diagram URL": result.diagram_url or "N/A",
            "Environment": result.environment or "N/A",
            "Improvement Status": result.improvement_status,
            "In Sync": result.in_sync,
            "Industry": result.industry or "N/A",
            "Industry Type": result.industry_type or "N/A",
            "Region": result.region_code or "N/A",
            "Scope": result.scope or "N/A",
            "Risk Counts": result.risk_counts,
            "Total Questions": result.total_questions,
            "Answered Questions": result.answered_questions,
            "Lenses": ", ".join(result.lenses) if result.lenses else "N/A",
            "Lens Alias": result.lens_alias,
            "Lens ARN": result.lens_arn,
            "Lens Version": result.lens_version,
            "Lens Name": result.lens_name,
            "Lens Status": result.lens_status,
            "AWS Updated At": result.aws_updated_at,
            "Created At": created_at,
            "Updated At": updated_at,
            "Last Run At": last_run_at,
            "Execution ID": result.execution_id or "N/A",
        }

        # Format and output the results
        format_item_output(
            item=assessment_data,
            title=f"Assessment Details: {result.name}",
            format_override=output_format,
        )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)


@assessment.command("create")
@click.option("--name", required=True, help="Name of the assessment")
@click.option("--description", help="Description of the assessment")
@click.option("--review-owner", help="Email of the review owner")
@click.option(
    "--scope",
    required=True,
    help='Scope of the assessment as JSON string. Format: {"Project": {}, "Accounts": [{"AccountNumber": "123456789012", "Regions": ["us-east-1"]}]} or for project-based: {"Project": {"ProjectId": "project-123", "Applications": ["app1"]}, "Accounts": ["123456789012"]}',
)
@click.option(
    "--lenses",
    default="AWS Well-Architected Framework",
    help="Comma-separated list of lenses to use (default: AWS Well-Architected Framework)",
)
@click.option(
    "--region-code", default="us-east-1", help="AWS region code (default: us-east-1)"
)
@click.option(
    "--environment", default="PRODUCTION", help="Environment (default: PRODUCTION)"
)
@with_common_options(include_tenant_id=True)
def create_assessment(
    name: str,
    description: Optional[str],
    review_owner: Optional[str],
    scope: Optional[str],
    lenses: Optional[str],
    region_code: str,
    environment: str,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """Create a new assessment.

    If --tenant-id is not provided, uses the default tenant configured with 'day2 profile create' or 'day2 auth login'.
    """
    try:
        # Validate required inputs first before creating session
        if not scope:
            exit_with_error("Scope is required", ExitCodes.VALIDATION_ERROR)

        try:
            scope_data = json.loads(scope)
            if not isinstance(scope_data, dict):
                exit_with_error(
                    "Scope must be a JSON object (dictionary), not a list or primitive value",
                    ExitCodes.VALIDATION_ERROR,
                )
        except json.JSONDecodeError:
            exit_with_error(
                "Scope must be a valid JSON string", ExitCodes.VALIDATION_ERROR
            )

        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        # Parse lenses if provided
        lenses_list = []
        if lenses:
            lenses_list = [lens.strip() for lens in lenses.split(",")]

        # Set default values for optional parameters
        description_value = description or ""
        review_owner_value = review_owner or ""

        # Create a proper CreateAssessmentInput object
        assessment_input = CreateAssessmentInput(
            AssessmentName=name,
            Description=description_value,
            ReviewOwner=review_owner_value,
            Scope=scope_data,
            Lenses=lenses_list,
            RegionCode=region_code,
            Environment=environment,
        )

        result = session.assessment.create_assessment(
            tenant_id=resolved_tenant_id, data=assessment_input
        )

        # Create assessment data for output using only available attributes
        assessment_data = {
            "ID": result.id,
            "Assessment ARN": result.assessment_arn,
            "Name": name,
            "Description": description_value or "N/A",
            "Environment": environment,
            "Region": region_code,
            "Lenses": ", ".join(lenses_list) if lenses_list else "N/A",
            "Review Owner": review_owner_value or "N/A",
        }

        # Format and output the result
        format_item_output(
            item=assessment_data,
            title="Assessment Created Successfully",
            format_override=output_format,
        )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)


@assessment.command("questions")
@click.argument("assessment-id")
@click.argument("pillar-id")
@with_common_options(include_tenant_id=True)
def list_questions(
    assessment_id: str,
    pillar_id: str,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """List questions for a specific pillar in an assessment.

    If --tenant-id is not provided, uses the default tenant configured with 'day2 profile create' or 'day2 auth login'.

    ASSESSMENT-ID: ID of the assessment to list questions for.
    PILLAR-ID: ID of the pillar to list questions for (required). Allowed values: security, costOptimization, reliability, performance, operationalExcellence, sustainability.
    """
    try:
        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        # Call the client method with explicit parameters
        result = session.assessment.list_questions(
            tenant_id=resolved_tenant_id,
            assessment_id=assessment_id,
            pillar_id=pillar_id,
        )

        # Ensure we handle None values properly for the calculation
        total = result.total_questions or 0
        answered = result.answered_questions or 0
        remaining = total - answered

        # Display summary information
        summary_data = {
            "pillar_id": pillar_id,
            "total_questions": total,
            "answered_questions": answered,
            "remaining_questions": remaining,
        }

        if output_format == "json":
            # For JSON output, include the summary in the response
            questions_data: list[dict[str, Any]] = []
        else:
            # For table output, display the summary first
            format_simple_output(
                f"Pillar: {pillar_id}\nQuestions: {total} total, {answered} answered, {remaining} remaining",
                format_override=output_format,
            )

            # Create a table for the questions
            questions_data = []

        # Process each question
        for i, question in enumerate(result.questions, 1):
            # Determine status for display
            is_answered = question.is_answered or False
            status_text = "Answered" if is_answered else "Not Answered"
            risk = question.risk if question.risk else "N/A"

            # Add to questions data
            questions_data.append(
                {
                    "index": i,
                    "id": question.id,
                    "title": question.title,
                    "is_answered": is_answered,
                    "status": status_text,
                    "risk": risk,
                }
            )

        # Format and output the results
        if output_format == "json":
            # For JSON output, include both summary and questions
            output_data = {"summary": summary_data, "questions": questions_data}
            console.print(json.dumps(output_data, indent=2, default=str))
        else:
            # For table output, display the questions table
            columns = {
                "index": "#",
                "id": "Question ID",
                "title": "Title",
                "status": "Status",
                "risk": "Risk",
            }

            format_list_output(
                items=questions_data,
                title=f"Questions for Pillar: {pillar_id}",
                columns=columns,
                format_override=output_format,
            )

            # Add hint for more details
            format_simple_output(
                "To see details of a specific question, use the 'question' command with the Assessment ID and Question ID.",
                format_override=output_format,
            )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)


@assessment.command("question")
@click.argument("assessment-id")
@click.argument("question-id")
@with_common_options(include_tenant_id=True)
def get_question(
    assessment_id: str,
    question_id: str,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """Get details of a specific question.

    If --tenant-id is not provided, uses the default tenant configured with 'day2 profile create' or 'day2 auth login'.
    """
    try:
        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        # Call the client method with explicit parameters
        result = session.assessment.get_question(
            tenant_id=resolved_tenant_id,
            assessment_id=assessment_id,
            question_id=question_id,
        )

        # Format the output based on the selected format
        if output_format and output_format.lower() == "json":
            # Convert to a dictionary for JSON output
            question_data: dict[str, Any] = {
                "id": result.id,
                "title": result.title,
                "description": result.description,
                "pillar_id": result.pillar_id,
                "pillar_name": result.pillar_name,
                "is_answered": result.is_answered,
                "status": "Answered" if result.is_answered else "Not Answered",
                "risk": result.risk if result.is_answered else "UNANSWERED",
            }

            # Add answer-related fields if the question is answered
            if result.is_answered:
                question_data["reason"] = result.reason or "NONE"
                question_data["notes"] = result.notes or ""

                # Add selected choices
                if result.selected_choices or result.choice_answers:
                    choice_ids = result.selected_choices or result.choice_answers
                    selected_choices = []

                    for choice_id in choice_ids:
                        # Handle both string and dictionary formats for choice_answers
                        if isinstance(choice_id, dict) and "ChoiceId" in choice_id:
                            choice_id = choice_id["ChoiceId"]

                        # Find the choice title if available
                        choice_title = next(
                            (
                                choice["Title"]
                                for choice in result.choices
                                if choice["ChoiceId"] == choice_id
                            ),
                            "Unknown",
                        )
                        selected_choices.append(
                            {"id": choice_id, "title": choice_title}
                        )

                    question_data["selected_choices"] = selected_choices

            # Add available choices
            if result.choices:
                question_data["choices"] = (
                    [
                        {
                            "id": choice.get("ChoiceId"),
                            "title": choice.get("Title"),
                            "description": choice.get("Description", ""),
                        }
                        for choice in result.choices
                    ]
                    if result.choices
                    else []
                )

            # Output as JSON
            console.print(json.dumps(question_data, indent=2))
        else:
            # Display question details in a structured table format
            # Create main question details table
            question_table = Table(title=f"Question Details: {result.id}")
            question_table.add_column("Property", style="cyan", min_width=12)
            question_table.add_column("Value", style="white")

            question_table.add_row("Question", result.title)
            question_table.add_row("ID", result.id)
            question_table.add_row(
                "Pillar", f"{result.pillar_name} ({result.pillar_id})"
            )

            # Format description to wrap nicely
            wrapped_description = "\n".join(textwrap.wrap(result.description, width=80))
            question_table.add_row("Description", wrapped_description)

            # Show status and risk information
            status_display = (
                "[green]Answered[/green]"
                if result.is_answered
                else "[yellow]Not Answered[/yellow]"
            )
            question_table.add_row("Status", status_display)

            if result.is_answered:
                question_table.add_row("Risk", result.risk or "Not specified")
                question_table.add_row("Reason", result.reason or "Not provided")
                if result.notes:
                    wrapped_notes = "\n".join(textwrap.wrap(result.notes, width=80))
                    question_table.add_row("Notes", wrapped_notes)

            console.print(question_table)

            # Show selected choices if answered
            if result.is_answered and (
                result.selected_choices or result.choice_answers
            ):
                console.print("\n[bold]Selected Choices:[/bold]")
                selected_table = Table()
                selected_table.add_column("Choice ID", style="cyan")
                selected_table.add_column("Title", style="green")

                # Use selected_choices or choice_answers, whichever is available
                choice_ids = result.selected_choices or result.choice_answers

                for choice_id in choice_ids:
                    # Handle both string and dictionary formats for choice_answers
                    if isinstance(choice_id, dict) and "ChoiceId" in choice_id:
                        choice_id = choice_id["ChoiceId"]

                    # Find the choice title if available
                    choice_title = next(
                        (
                            choice["Title"]
                            for choice in result.choices
                            if choice["ChoiceId"] == choice_id
                        ),
                        "Unknown",
                    )
                    selected_table.add_row(choice_id, choice_title)

                console.print(selected_table)

            # Display available choices in a clean table
            if result.choices:
                console.print("\n[bold]Available Choices:[/bold]")
                choices_table = Table()
                choices_table.add_column("Choice ID", style="cyan", min_width=30)
                choices_table.add_column("Title", style="white")
                choices_table.add_column("Description", style="dim", max_width=60)

                for choice in result.choices:
                    # Wrap description if it's long
                    description = choice.get("Description", "")
                    if len(description) > 60:
                        description = "\n".join(textwrap.wrap(description, width=60))

                    choices_table.add_row(
                        choice["ChoiceId"], choice["Title"], description
                    )

                console.print(choices_table)

        # Show hint for answering the question (only for table output)
        if not result.is_answered and output_format != "json":
            # Get a couple of example choice IDs for the hint
            example_choices = []
            if result.choices and len(result.choices) >= 2:
                # Use first two choices as examples
                example_choices = [
                    result.choices[0]["ChoiceId"],
                    result.choices[1]["ChoiceId"],
                ]
            elif result.choices:
                # Use just one choice if only one available
                example_choices = [result.choices[0]["ChoiceId"]]

            if example_choices:
                choices_str = ",".join(
                    example_choices[:2]
                )  # Limit to 2 for readability
                console.print(
                    f"\n[dim]To answer this question, use the 'answer' command with choice IDs from the table above:\n\n"
                    f"Example:\n"
                    f"day2 assessment answer {assessment_id} {question_id} \\\n"
                    f"    --reason BUSINESS_PRIORITIES \\\n"
                    f'    --choices "{choices_str}" \\\n'
                    f'    --notes "Your implementation notes"[/dim]'
                )
            else:
                console.print(
                    "\n[dim]To answer this question, use the 'answer' command.[/dim]"
                )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)


@assessment.command("answer")
@click.argument("assessment-id")
@click.argument("question-id")
@click.option(
    "--reason",
    type=click.Choice(
        [
            "OUT_OF_SCOPE",
            "BUSINESS_PRIORITIES",
            "ARCHITECTURE_CONSTRAINTS",
            "OTHER",
            "NONE",
        ]
    ),
    required=True,
    help="Reason for the answer",
)
@click.option(
    "--choices",
    help="Comma-separated list of choice IDs to select (get from 'question' command)",
)
@click.option("--notes", help="Additional notes for the answer")
@click.option(
    "--applicable/--not-applicable",
    default=True,
    help="Whether the question is applicable to the assessment",
)
@with_common_options(include_tenant_id=True)
def answer_question(
    assessment_id: str,
    question_id: str,
    reason: str,
    choices: Optional[str],
    notes: Optional[str],
    applicable: bool,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """Answer a question in an assessment.

    Before using this command, you must obtain the actual question ID and choice IDs:

    1. List questions: day2 assessment questions ASSESSMENT-ID PILLAR-ID
    2. Get question details: day2 assessment question ASSESSMENT-ID QUESTION-ID
    3. Use the real choice IDs from the question details

    If --tenant-id is not provided, uses the default tenant configured with 'day2 profile create' or 'day2 auth login'.

    ASSESSMENT-ID: ID of the assessment that contains the question.
    QUESTION-ID: ID of the question to answer (get from 'questions' command).
    """
    try:
        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        # Parse selected choices if provided and create choice_updates dictionary
        choice_updates = {}
        if choices:
            # Skip validation for now to avoid performance issues - process choices directly
            for choice_id in [choice.strip() for choice in choices.split(",")]:
                # Use plain dictionary as shown in the example
                choice_updates[choice_id] = {"Status": "SELECTED"}

        # Create the answer input with the new format
        answer_data = AnswerQuestionInput(
            LensAlias="wellarchitected",
            ChoiceUpdates=choice_updates,
            Reason=reason,
            Notes=notes or "",
            IsApplicable=applicable,
        )

        # Submit the answer
        result = session.assessment.answer_question(
            tenant_id=resolved_tenant_id,
            assessment_id=assessment_id,
            question_id=question_id,
            data=answer_data,
        )

        # Create answer output data for both JSON and table formats
        answer_output = {
            "Status": result.status,
            "Message": result.message,
            "Question ID": result.id or question_id,
            "Assessment ID": assessment_id,
            "Selected Choices": choices or "N/A",
            "Reason": reason,
            "Notes": notes or "N/A",
            "Applicable": "Yes" if applicable else "No",
        }

        # Format and output the result
        format_item_output(
            item=answer_output,
            title="Question Answered Successfully",
            format_override=output_format,
        )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)


@assessment.command("findings")
@click.argument("assessment-id")
@click.option(
    "--severity",
    multiple=True,
    help="Filter by severity (HIGH, MEDIUM, LOW) (can be used multiple times)",
)
@click.option(
    "--status",
    multiple=True,
    help="Filter by status (OPEN, RESOLVED, SUPPRESSED) (can be used multiple times)",
)
@click.option(
    "--account",
    multiple=True,
    help="Filter by account number (can be used multiple times)",
)
@click.option(
    "--region", multiple=True, help="Filter by region code (can be used multiple times)"
)
@click.option(
    "--resource-type",
    multiple=True,
    help="Filter by resource type (can be used multiple times)",
)
@click.option(
    "--question-id",
    multiple=True,
    help="Filter by question ID (can be used multiple times)",
)
@click.option(
    "--resource-id",
    multiple=True,
    help="Filter by resource ID (can be used multiple times)",
)
@click.option(
    "--pillar-id",
    multiple=True,
    help="Filter by pillar ID (can be used multiple times). Allowed values: security, costOptimization, reliability, performance, operationalExcellence, sustainability.",
)
@click.option("--page-token", help="Page token for pagination")
@click.option("--page-size", type=int, default=10, help="Page size")
@with_common_options(include_tenant_id=True)
def list_findings(
    assessment_id: str,
    severity: Tuple[str, ...],
    status: Tuple[str, ...],
    account: Tuple[str, ...],
    region: Tuple[str, ...],
    resource_type: Tuple[str, ...],
    question_id: Tuple[str, ...],
    resource_id: Tuple[str, ...],
    pillar_id: Tuple[str, ...],
    page_token: Optional[str],
    page_size: int,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
    check_id: Tuple[str, ...] = (),
    best_practice_id: Tuple[str, ...] = (),
    best_practice_risk: Tuple[str, ...] = (),
) -> None:
    """List findings for an assessment.

    If --tenant-id is not provided, uses the default tenant configured with 'day2 profile create' or 'day2 auth login'.

    ASSESSMENT-ID: ID of the assessment to list findings for.
    """
    try:
        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        # Call the client method with explicit parameters
        result = session.assessment.list_findings(
            tenant_id=resolved_tenant_id,
            assessment_id=assessment_id,
            status=list(status) if status else None,
            severity=list(severity) if severity else None,
            account_number=list(account) if account else None,
            region_code=list(region) if region else None,
            resource_type=list(resource_type) if resource_type else None,
            question_ids=list(question_id) if question_id else None,
            resource_ids=list(resource_id) if resource_id else None,
            pillar_ids=list(pillar_id) if pillar_id else None,
            page_token=page_token,
            page_size=page_size,
            check_ids=list(check_id) if check_id else None,
            best_practice_ids=list(best_practice_id) if best_practice_id else None,
            best_practice_risk=list(best_practice_risk) if best_practice_risk else None,
        )

        if not result.records:
            format_simple_output("No findings found.", format_override=output_format)
            return

        # Convert findings to a list of dictionaries for the formatter
        findings_data = []

        for finding in result.records:
            # Add finding to the list
            findings_data.append(
                {
                    "finding_id": finding.finding_id,
                    "title": finding.title,
                    "severity": finding.severity,
                    "status": finding.status,
                    "resource_type": finding.resource_type,
                    "account_number": finding.account_number,
                    "region_code": finding.region_code,
                    "pillar_id": finding.pillar_id,
                    "check_id": finding.check_id,
                    "best_practice_id": finding.best_practice_id,
                    "best_practice": finding.best_practice,
                    "best_practice_risk": finding.best_practice_risk,
                }
            )

        # Define column mapping for the formatter
        columns = {
            "finding_id": "Finding ID",
            "title": "Title",
            "severity": "Severity",
            "status": "Status",
            "resource_type": "Resource Type",
            "account_number": "Account",
            "region_code": "Region",
            "pillar_id": "Pillar ID",
            "check_id": "Check ID",
            "best_practice_id": "Best Practice ID",
            "best_practice": "Best Practice",
            "best_practice_risk": "Best Practice Risk",
        }

        # Format and output the results
        format_list_output(
            items=findings_data,
            title=f"Findings for Assessment: {assessment_id}",
            columns=columns,
            format_override=output_format,
        )

        # Display pagination information
        if result.next_page_token:
            format_simple_output(
                f"More results available. Use --page-token={result.next_page_token} to get the next page.",
                format_override=output_format,
            )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)


@assessment.command("run")
@click.argument("assessment-id")
@click.option(
    "--lens-name",
    default="AWS Well-Architected Framework",
    help="The name of the lens to use for the assessment (default: AWS Well-Architected Framework).",
)
@click.option(
    "--pillar-id",
    help="The ID of the pillar to assess. Allowed values: security, costOptimization, reliability, performance, operationalExcellence, sustainability.",
)
@click.option(
    "--question-id",
    help="The ID of a specific question to assess within the selected pillar.",
)
@click.option(
    "--best-practice-id",
    help="The ID of a best practice to evaluate for the selected question ID.",
)
@with_common_options(include_tenant_id=True)
def run_assessment(
    assessment_id: str,
    tenant_id: Optional[str],
    lens_name: str,
    pillar_id: Optional[str],
    question_id: Optional[str],
    best_practice_id: Optional[str],
    output: Optional[str] = None,
    profile: Optional[str] = None,
) -> None:
    """Run an assessment.

    If --tenant-id is not provided, uses the default tenant configured with 'day2 profile create' or 'day2 auth login'.

    ASSESSMENT-ID: ID of the assessment to run.
    """
    try:
        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        # Create the input model
        run_input = RunAssessmentInput(
            LensName=lens_name,
            PillarId=pillar_id,
            QuestionId=question_id,
            BestPracticeId=best_practice_id,
        )

        # Call the client method to run the assessment
        result = session.assessment.run_assessment(
            tenant_id=resolved_tenant_id,
            assessment_id=assessment_id,
            data=run_input,
        )

        # Format and output the result
        run_data = {
            "id": result.run_id,
            "lens_name": lens_name,
            "pillar_id": pillar_id or "N/A",
            "question_id": question_id or "N/A",
            "best_practice_id": best_practice_id or "N/A",
        }

        format_item_output(
            item=run_data,
            title=f"Assessment Run Details: {result.run_id}",
            format_override=output_format,
        )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)


@assessment.command("generate-report")
@click.argument("assessment-id")
@click.option(
    "--cloud-provider",
    default="AWS",
    help="Cloud provider name (default: AWS)",
)
@click.option(
    "--pillar-id",
    multiple=True,
    help="Filter findings by pillar ID (Can be used multiple times). Allowed values: security, costOptimization, reliability, performance, operationalExcellence, sustainability.",
)
@click.option(
    "--severity",
    multiple=True,
    help="Filter findings by severity levels (Can be used multiple times). Allowed values: High, Critical, Medium, Low, Informational.",
)
@click.option(
    "--status",
    multiple=True,
    help="Filter findings by statuses (Can be used multiple times). Allowed values: Failed, Error, Suppressed, Passed.",
)
@click.option(
    "--account-number",
    multiple=True,
    help="Filter findings by account numbers. Can be used multiple times.",
)
@click.option(
    "--region-code",
    multiple=True,
    help="Filter findings by AWS region codes. Can be used multiple times.",
)
@click.option(
    "--best-practice-risk-exposure",
    multiple=True,
    help="Filter findings by best practice risk exposure (can be used multiple times). Allowed values: High, Medium, Low.",
)
@click.option(
    "--unique-report",
    default=False,
    help="Whether to return unique findings in the report (default: False).",
)
@click.option(
    "--lenses",
    default="AWS Well-Architected Framework",
    help="Comma-separated list of lenses to filter findings (default: AWS Well-Architected Framework).",
)
@with_common_options(include_tenant_id=True)
def generate_report(
    assessment_id: str,
    cloud_provider: str,
    pillar_id: Tuple[str, ...],
    severity: Tuple[str, ...],
    status: Tuple[str, ...],
    account_number: Tuple[str, ...],
    region_code: Tuple[str, ...],
    best_practice_risk_exposure: Tuple[str, ...],
    unique_report: bool,
    lenses: str,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """Generate a report for a specific assessment.

    If --tenant-id is not provided, uses the default tenant configured with 'day2 profile create' or 'day2 auth login'.

    ASSESSMENT-ID: ID of the assessment to generate the report for.
    """
    try:
        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        # Parse lenses into a list
        lenses_list = [lens.strip() for lens in lenses.split(",")]

        # Create the input model
        report_input = GenerateAssessmentReportInput(
            CloudProvider=cloud_provider,
            PillarIds=list(pillar_id) if pillar_id else None,
            Severity=list(severity) if severity else None,
            Status=list(status) if status else None,
            AccountNumber=list(account_number) if account_number else None,
            RegionCode=list(region_code) if region_code else None,
            BestPracticeRiskExposure=(
                list(best_practice_risk_exposure)
                if best_practice_risk_exposure
                else None
            ),
            UniqueReport=unique_report,
            Lenses=lenses_list,
        )
        # Call the client method to generate the report
        result = session.assessment.generate_report(
            tenant_id=resolved_tenant_id,
            assessment_id=assessment_id,
            data=report_input,
        )

        # Format and output the result
        report_data = {
            "id": result.report_id,
            "cloud_provider": cloud_provider,
            "pillar_id": ", ".join(pillar_id) if pillar_id else "N/A",
            "severity": ", ".join(severity) if severity else "N/A",
            "status": ", ".join(status) if status else "N/A",
            "account_number": ", ".join(account_number) if account_number else "N/A",
            "region_code": ", ".join(region_code) if region_code else "N/A",
            "best_practice_risk_exposure": (
                ", ".join(best_practice_risk_exposure)
                if best_practice_risk_exposure
                else "N/A"
            ),
            "unique_report": unique_report,
            "lenses": ", ".join(lenses_list),
        }

        format_item_output(
            item=report_data,
            title=f"Generated Report successfully: {result.report_id}",
            format_override=output_format,
        )

    except (Day2Error, ProfileNotFoundError) as e:
        handle_error_with_exit(e)
