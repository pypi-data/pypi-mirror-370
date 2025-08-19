from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Assessment(BaseModel):
    """Details of an assessment.

    Attributes:
        id: Assessment identifier
        name: Name of the assessment
        description: Description of the assessment
        status: Current status of the assessment
        assessment_arn: AWS ARN of the assessment
        lenses: List of lens identifiers used in the assessment
        total_questions: Total number of questions in the assessment
        answered_questions: Number of questions that have been answered
        created_at: Timestamp when the assessment was created
        updated_at: Timestamp when the assessment was last updated
        last_run_at: Timestamp of the last execution run (if completed)
    """

    id: str = Field(alias="AssessmentId")
    name: str = Field(alias="AssessmentName")
    description: str = Field(alias="Description")
    status: str = Field(alias="Status")
    assessment_arn: str = Field(alias="AssessmentArn")
    lenses: List[str] = Field(alias="Lenses")
    total_questions: int = Field(alias="TotalQuestions")
    answered_questions: int = Field(alias="AnsweredQuestions")
    created_at: Optional[datetime] = Field(None, alias="CreatedAt")
    updated_at: Optional[datetime] = Field(None, alias="UpdatedAt")
    last_run_at: Optional[datetime] = Field(None, alias="LastRunAt")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class ListAssessmentsOutput(BaseModel):
    """Output of list_assessments operation.

    Attributes:
        assessments: List of assessment details
        next_page_token: Token for fetching the next page of results
    """

    assessments: List[Assessment] = Field(alias="Assessments")
    next_page_token: Optional[str] = Field(None, alias="NextPageToken")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class CreateAssessmentInput(BaseModel):
    """Input for creating an assessment.

    The scope parameter can be in one of two formats:

    1. Account-based scope:
       ```python
       {
           "Project": {},
           "Accounts": [
               {"AccountNumber": "123456789012", "Regions": ["us-east-1", "us-west-2"]}
           ]
       }
       ```

    2. Project-based scope:
       ```python
       {
           "Project": {"ProjectId": "proj-123", "Applications": ["app1", "app2"]},
           "Accounts": ["123456789012"]
       }
       ```

    Attributes:
        name: Name of the assessment
        description: Description of the assessment
        review_owner: Email or identifier of the review owner
        scope: Scope configuration (see formats above)
        lenses: List of lens aliases to use (defaults to ["AWS Well-Architected Framework"] only "AWS Well-Architected Framework" is supported)
        tags: Key-value pairs for tagging the assessment
        region_code: AWS region code where the assessment is created
        environment: Environment type (e.g., PRODUCTION, DEVELOPMENT)
        hosted_account_number: Optional AWS account number for hosting
        diagram_url: Optional URL to architecture diagram
        industry_type: Optional industry type classification
        industry: Optional industry specification
    """

    name: str = Field(alias="AssessmentName")
    description: str = Field(alias="Description")
    review_owner: str = Field(alias="ReviewOwner")
    scope: Dict[str, Any] = Field(alias="Scope")
    lenses: Optional[List[str]] = Field(
        default=["AWS Well-Architected Framework"], alias="Lenses"
    )
    tags: Optional[Dict[str, Any]] = Field(default={}, alias="Tags")
    region_code: str = Field(alias="RegionCode")
    environment: str = Field(alias="Environment")
    hosted_account_number: Optional[str] = Field(
        default=None, alias="HostedAccountNumber"
    )
    diagram_url: Optional[str] = Field(default=None, alias="DiagramURL")
    industry_type: Optional[str] = Field(default=None, alias="IndustryType")
    industry: Optional[str] = Field(default=None, alias="Industry")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class GetAssessmentOutput(BaseModel):
    """Output of get_assessment operation.

    Attributes:
        id: Assessment identifier
        name: Name of the assessment
        description: Description of the assessment
        status: Current status of the assessment
        assessment_arn: AWS ARN of the assessment
        created_at: Timestamp when the assessment was created
        updated_at: Timestamp when the assessment was last updated
        answered_questions: Number of questions that have been answered
        total_questions: Total number of questions in the assessment
        lenses: List of lens identifiers used in the assessment
        owner: Owner of the assessment
        diagram_url: URL to architecture diagram (if provided)
        environment: Environment type
        improvement_status: Status of improvement plan
        in_sync: Synchronization status indicator
        industry: Industry specification
        industry_type: Industry type classification
        region_code: AWS region code
        scope: Scope configuration
        risk_counts: Dictionary of risk counts by severity
        lens_alias: Primary lens alias
        lens_arn: AWS ARN of the lens
        lens_version: Version of the lens
        lens_name: Name of the lens
        lens_status: Status of the lens
        aws_updated_at: Timestamp of  the last AWS update
        last_run_at: Timestamp of the last execution run (if completed)
        execution_id: ID of the last execution run (if completed)
    """

    id: str = Field(alias="AssessmentId")
    name: str = Field(alias="AssessmentName")
    description: str = Field(alias="Description")
    status: str = Field(alias="Status")
    assessment_arn: str = Field(alias="AssessmentArn")
    created_at: datetime = Field(alias="CreatedAt")
    updated_at: datetime = Field(alias="UpdatedAt")
    answered_questions: int = Field(alias="AnsweredQuestions")
    total_questions: int = Field(alias="TotalQuestions")
    lenses: List[str] = Field(alias="Lenses")
    owner: str = Field(alias="Owner")
    diagram_url: Optional[str] = Field(None, alias="DiagramURL")
    environment: str = Field(alias="Environment")
    improvement_status: str = Field(alias="ImprovementStatus")
    in_sync: int = Field(alias="InSync")
    industry: Optional[str] = Field(None, alias="Industry")
    industry_type: Optional[str] = Field(None, alias="IndustryType")
    region_code: str = Field(alias="RegionCode")
    scope: List[Dict[str, Any]] = Field(alias="Scope")
    risk_counts: Dict[str, Any] = Field(alias="RiskCounts")
    lens_alias: str = Field(alias="LensAlias")
    lens_arn: str = Field(alias="LensArn")
    lens_version: str = Field(alias="LensVersion")
    lens_name: str = Field(alias="LensName")
    lens_status: str = Field(alias="LensStatus")
    aws_updated_at: str = Field(
        alias="AWSUpdatedAt"
    )  # Changed to str to handle timezone format
    last_run_at: Optional[datetime] = Field(
        None, alias="LastRunAt"
    )  # Optional since it will be present only when the execution run is completed for the assessment
    execution_id: Optional[str] = Field(
        None, alias="ExecutionId"
    )  # Optional since it will be present only when the execution run is completed for the assessment

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class CreateAssessmentOutput(BaseModel):
    """Output of create_assessment operation.

    Note:
        According to the OpenAPI specification, this only returns the AssessmentId and AssessmentArn.

    Attributes:
        id: Newly created assessment identifier
        assessment_arn: AWS ARN of the newly created assessment
    """

    # Fields from the OpenAPI spec
    id: str = Field(alias="AssessmentId")
    assessment_arn: str = Field(alias="AssessmentArn")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class Question(BaseModel):
    """Details of an assessment question.

    Attributes:
        id: Question identifier
        title: Title of the question
        pillar_id: ID of the pillar this question belongs to
        risk: Current risk level (HIGH, MEDIUM, LOW, or UNANSWERED)
        reason: Reason for the current answer (if applicable)
        description: Detailed description of the question
        pillar_name: Name of the pillar this question belongs to
        is_answered: Whether the question has been answered
        choices: Available choices for the question
        selected_choices: Currently selected choice IDs
        notes: Additional notes for the answer
    """

    id: str = Field(alias="QuestionId")
    title: str = Field(alias="QuestionTitle")
    pillar_id: str = Field(alias="PillarId")
    risk: Optional[str] = Field(None, alias="Risk")
    reason: Optional[str] = Field(None, alias="Reason")

    # These fields are not in the API response, but we'll add them with default values
    # to maintain compatibility with our code
    description: Optional[str] = Field("", alias="QuestionDescription")
    pillar_name: Optional[str] = Field("", alias="PillarName")
    is_answered: Optional[bool] = Field(False, alias="IsAnswered")
    choices: Optional[List[Dict[str, Any]]] = Field(None, alias="Choices")
    selected_choices: Optional[List[str]] = Field(None, alias="SelectedChoices")
    notes: Optional[str] = Field(None, alias="Notes")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class ListQuestionsOutput(BaseModel):
    """Output of list_questions operation.

    Attributes:
        questions: List of question details
        total_questions: Total number of questions
        answered_questions: Number of questions that have been answered
        pillar_id: ID of the pillar (if filtered by pillar)
        pillar_name: Name of the pillar (if filtered by pillar)
    """

    questions: List[Question] = Field(alias="Questions")

    # These fields are not in the API response, but we'll add them with default values
    # to maintain compatibility with our code
    total_questions: Optional[int] = Field(0, alias="TotalQuestions")
    answered_questions: Optional[int] = Field(0, alias="AnsweredQuestions")
    pillar_id: Optional[str] = Field("", alias="PillarId")
    pillar_name: Optional[str] = Field("", alias="PillarName")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

        # If these fields aren't in the API response, calculate them from the questions
        if self.questions and not self.pillar_id and len(self.questions) > 0:
            self.pillar_id = self.questions[0].pillar_id

        # Calculate total and answered questions
        if self.questions:
            self.total_questions = len(self.questions)
            self.answered_questions = sum(
                1 for q in self.questions if q.risk and q.risk != "UNANSWERED"
            )

            # Set is_answered based on risk
            for question in self.questions:
                question.is_answered = (
                    question.risk is not None and question.risk != "UNANSWERED"
                )


class GetQuestionOutput(BaseModel):
    """Output of get_question operation.

    Attributes:
        title: Title of the question
        description: Detailed description of the question
        pillar_id: ID of the pillar this question belongs to
        choices: Available choices for answering the question
        is_applicable: Whether the question is applicable
        risk: Current risk level (if answered)
        reason: Reason for marking as not applicable
        helpful_resource_url: URL to helpful resources
        improvement_plan_url: URL to improvement plan
        choice_answers: Currently selected choice answers
        id: Question identifier
        pillar_name: Name of the pillar
        notes: Additional notes
        is_answered: Whether the question has been answered
        selected_choices: List of selected choice IDs
    """

    # Fields directly from the API response
    title: str = Field(alias="QuestionTitle")
    description: str = Field(alias="QuestionDescription")
    pillar_id: str = Field(alias="PillarId")
    choices: List[Dict[str, Any]] = Field(alias="Choices")
    is_applicable: bool = Field(alias="IsApplicable")
    risk: Optional[str] = Field(None, alias="Risk")
    reason: Optional[str] = Field(None, alias="Reason")
    helpful_resource_url: Optional[str] = Field(None, alias="HelpfulResourceUrl")
    improvement_plan_url: Optional[str] = Field(None, alias="ImprovementPlanUrl")
    choice_answers: List[Union[str, Dict[str, Any]]] = Field(
        default_factory=list, alias="ChoiceAnswers"
    )

    # Fields we compute or add for convenience
    id: Optional[str] = None  # Will be set from the question_id parameter
    pillar_name: Optional[str] = None  # Will be set if available in the response
    notes: Optional[str] = Field(None, alias="Notes")  # May be in API response
    is_answered: bool = False  # Computed based on risk

    # For backward compatibility
    # Use the same type as choice_answers to avoid type errors
    selected_choices: List[str] = Field(
        default_factory=list
    )  # Alias for choice_answers

    # Allow extra fields
    model_config = ConfigDict(extra="allow")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

        # Process choice_answers to handle both string and dictionary formats
        processed_choice_answers: List[str] = []
        for choice in self.choice_answers:
            if isinstance(choice, str):
                processed_choice_answers.append(choice)
            elif isinstance(choice, dict) and "ChoiceId" in choice:
                processed_choice_answers.append(choice["ChoiceId"])

        # Use type casting to satisfy mypy
        self.choice_answers = cast(
            List[Union[str, Dict[str, Any]]], processed_choice_answers
        )

        # Set selected_choices as an alias for choice_answers
        self.selected_choices = processed_choice_answers

        # Set is_answered based on whether selected_choices has items
        self.is_answered = bool(self.selected_choices)


class ChoiceStatus(BaseModel):
    """Status of a choice in an answer.

    Attributes:
        status: Status of the choice (SELECTED or UNSELECTED)
    """

    status: str = Field("SELECTED", alias="Status")

    model_config = ConfigDict(extra="allow")


class AnswerQuestionInput(BaseModel):
    """Input for answering a question.

    Attributes:
        lens_alias: Alias of the lens (defaults to 'wellarchitected')
        choice_updates: Dictionary mapping choice IDs to their status
        notes: Additional notes about the answer
        is_applicable: Whether the question is applicable (defaults to True)
        reason: Reason if not applicable (OUT_OF_SCOPE, BUSINESS_PRIORITIES,
            ARCHITECTURE_CONSTRAINTS, OTHER, or NONE)
        selected_choices: List of selected choice IDs (deprecated, use choice_updates)
        risk: Risk level (deprecated, automatically calculated)
    """

    lens_alias: str = Field("wellarchitected", alias="LensAlias")
    choice_updates: Dict[str, ChoiceStatus] = Field(
        default_factory=dict, alias="ChoiceUpdates"
    )
    notes: Optional[str] = Field(None, alias="Notes")
    is_applicable: bool = Field(True, alias="IsApplicable")
    reason: str = Field("NONE", alias="Reason")

    # For backward compatibility - excluded from model_dump
    selected_choices: Optional[List[str]] = Field(None, exclude=True)
    risk: Optional[str] = Field(
        None, exclude=True
    )  # Risk is no longer used in the new API format

    # Allow extra fields
    model_config = ConfigDict(extra="allow")

    def __init__(self, **data: Any) -> None:
        # Validate reason is one of the allowed values
        valid_reasons = [
            "OUT_OF_SCOPE",
            "BUSINESS_PRIORITIES",
            "ARCHITECTURE_CONSTRAINTS",
            "OTHER",
            "NONE",
        ]
        if "reason" in data or "Reason" in data:
            reason = data.get("reason") or data.get("Reason")
            if reason and reason not in valid_reasons:
                data["Reason"] = "OTHER"

        super().__init__(**data)


class AnswerQuestionOutput(BaseModel):
    """Output of answer_question operation.

    Note:
        The API returns a success message with status and message fields.

    Attributes:
        status: Status of the operation (e.g., 'success')
        message: Descriptive message about the operation result
        id: Question identifier (added for convenience)
    """

    # Fields directly from the API response
    status: str = Field(alias="Status")
    message: str = Field(alias="Message")

    id: Optional[str] = None

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class Finding(BaseModel):
    """Details of a finding.

    Attributes:
        finding_id: Unique identifier for the finding
        resource_id: ID of the affected resource
        resource_type: Type of the affected resource (e.g., AWS::EC2::Instance)
        account_number: AWS account number where the resource exists
        region_code: AWS region where the resource exists
        check_id: ID of the check that generated this finding
        recommendation: Recommended action to address the finding
        remediation: Whether remediation is available
        created_at: Timestamp when the finding was created
        question_id: Related assessment question ID
        question: Related assessment question text
        pillar_id: ID of the related pillar
        severity: Severity level (HIGH, MEDIUM, LOW)
        status: Current status of the finding (OPEN, RESOLVED, SUPPRESSED)
        title: Title of the finding
        description: Detailed description of the finding
        best_practice_id: ID of the related best practice
        best_practice: Description of the best practice
        best_practice_risk: Risk level associated with not following the best practice
    """

    finding_id: str = Field(alias="FindingId")
    resource_id: str = Field(alias="ResourceId")
    resource_type: str = Field(alias="ResourceType")
    account_number: str = Field(alias="AccountNumber")
    region_code: str = Field(alias="RegionCode")
    check_id: str = Field(alias="CheckId")
    recommendation: str = Field(alias="Recommendation")
    remediation: bool = Field(alias="Remediation")
    created_at: str = Field(alias="CreatedAt")
    question_id: str = Field(alias="QuestionId")
    question: str = Field(alias="Question")
    pillar_id: str = Field(alias="PillarId")
    severity: str = Field(alias="Severity")
    status: str = Field(alias="Status")
    title: str = Field(alias="Title")
    description: str = Field(alias="Description")
    best_practice_id: str = Field(alias="BestPracticeId")
    best_practice: str = Field(alias="BestPractice")
    best_practice_risk: str = Field(alias="BestPracticeRisk")
    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class ListFindingsOutput(BaseModel):
    """Output of list_findings operation.

    Attributes:
        records: List of finding details
        next_page_token: Token for fetching the next page of results
    """

    records: List[Finding] = Field(alias="Records", default=[])
    next_page_token: Optional[str] = Field(None, alias="NextPageToken")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class RunAssessmentInput(BaseModel):
    """
    Model for running an assessment with specific filters.

    Attributes:
        lens_name: Name of the lens (default: "AWS Well-Architected Framework").
        pillar_id: Optional ID of the pillar. Allowed values: security, costOptimization,
            reliability, performance, operationalExcellence, sustainability.
        question_id: Optional ID of the specific question.
        best_practice_id: Optional ID of the best practice.
    """

    lens_name: Optional[str] = Field(
        default="AWS Well-Architected Framework", alias="LensName"
    )
    pillar_id: Optional[str] = Field(None, alias="PillarId")
    question_id: Optional[str] = Field(None, alias="QuestionId")
    best_practice_id: Optional[str] = Field(None, alias="BestPracticeId")

    @model_validator(mode="after")
    def validate_payload(self) -> "RunAssessmentInput":
        lensname = self.lens_name
        if lensname != "AWS Well-Architected Framework":
            raise ValueError(
                "Currently, only 'AWS Well-Architected Framework' lens is supported."
            )

        if self.question_id and not self.pillar_id:
            raise ValueError("If 'question_id' is provided, 'pillar_id' is mandatory.")

        if self.best_practice_id and (not self.question_id or not self.pillar_id):
            raise ValueError(
                "If 'best_practice_id' is provided, both 'question_id' and 'pillar_id' are mandatory."
            )
        return self

    # Allow extra fields
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class RunAssessmentOutput(BaseModel):
    """Output of run_assessment operation.

    Attributes:
        run_id: Unique identifier for the assessment run.
    """

    run_id: str = Field(alias="RunId")

    # Allow extra fields
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class GenerateAssessmentReportInput(BaseModel):
    """Input for generate_report operation.

    Attributes:
        cloud_provider: Cloud provider name (default: AWS).
        pillar_ids: List of pillar IDs to filter findings. Allowed values: security, costOptimization,
            reliability, performance, operationalExcellence, sustainability.
        severity: List of severity levels to filter findings. Allowed values: High, Critical, Medium, Low, Informational.
        status: List of statuses to filter findings. Allowed values: Failed, Error, Suppressed, Passed.
        account_number: List of AWS account numbers to filter findings.
        region_code: List of AWS region codes to filter findings.
        unique_report: Whether to return unique findings in the report (default: False).
        lenses: List of well-architected lenses to filter findings.
        best_practice_risk_exposure: List of best practice risk exposures to filter findings. Allowed values: High, Medium, Low.
    """

    cloud_provider: str = Field(
        default="AWS",
        alias="CloudProvider",
        description="Cloud provider name.",
    )
    pillar_ids: Optional[List[str]] = Field(
        default=None,
        alias="PillarIds",
        description="List of pillar IDs to filter findings.",
    )
    severity: Optional[List[str]] = Field(
        default=None,
        alias="Severity",
        description="List of severity levels to filter findings.",
    )
    status: Optional[List[str]] = Field(
        default=None, alias="Status", description="List of statuses to filter findings."
    )
    account_number: Optional[List[str]] = Field(
        default=None,
        alias="AccountNumber",
        description="List of AWS account numbers to filter findings.",
    )
    region_code: Optional[List[str]] = Field(
        default=None,
        alias="RegionCode",
        description="List of AWS region codes to filter findings.",
    )
    unique_report: Optional[bool] = Field(
        default=False,
        alias="UniqueReport",
        description="Whether to return unique findings in the report.",
    )
    lenses: Optional[List[str]] = Field(
        default=["AWS Well-Architected Framework"],
        alias="Lenses",
        description="List of well-architected lenses to filter findings.",
    )
    best_practice_risk_exposure: Optional[List[str]] = Field(
        default=None,
        alias="BestPracticeRiskExposure",
        description="List of best practice risk exposures to filter findings.",
    )

    # Allow extra fields
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class GenerateAssessmentReportOutput(BaseModel):
    """Output of generate_report operation.

    Attributes:
        report_id: Unique identifier for the generated report.
    """

    report_id: str = Field(alias="ReportId")

    # Allow extra fields
    model_config = ConfigDict(extra="allow", populate_by_name=True)
