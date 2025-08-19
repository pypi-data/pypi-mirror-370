"""Assessment resource implementation for the MontyCloud DAY2 SDK."""

from typing import Dict, List, Optional, Union

from day2.client.base import BaseClient
from day2.models.assessment import (
    AnswerQuestionInput,
    AnswerQuestionOutput,
    CreateAssessmentInput,
    CreateAssessmentOutput,
    GenerateAssessmentReportInput,
    GenerateAssessmentReportOutput,
    GetAssessmentOutput,
    GetQuestionOutput,
    ListAssessmentsOutput,
    ListFindingsOutput,
    ListQuestionsOutput,
    RunAssessmentInput,
    RunAssessmentOutput,
)
from day2.session import Session


class AssessmentClient(BaseClient):
    """Client for interacting with the Assessment service."""

    def __init__(self, session: Session) -> None:
        """Initialize a new AssessmentClient.

        Args:
            session: MontyCloud session.
        """
        super().__init__(session, "assessment")

    def list_assessments(
        self,
        tenant_id: str,
        status: str,
        keyword: Optional[str] = None,
        page_size: int = 10,
        page_token: Optional[str] = None,
    ) -> ListAssessmentsOutput:
        """List assessments in a tenant.

        Args:
            tenant_id: The ID of the tenant to list assessments for.
            status: Status to filter assessments by. Must be one of ["PENDING", "COMPLETED"].
            keyword: Optional keyword to filter assessments by name or description.
            page_size: The number of assessments per page (default: 10).
            page_token: Token for pagination.

        Returns:
            ListAssessmentsOutput: Object containing list of assessments and pagination info.

        Raises:
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.assessment
            >>> response = client.list_assessments(tenant_id="tenant-123", status="PENDING", page_size=10)
            >>> for assessment in response.assessments:
            ...     print(f"{assessment.id}: {assessment.name}")
            >>> # To get the next page of results:
            >>> if response.next_page_token:
            ...     next_page = client.list_assessments(tenant_id="tenant-123", status="PENDING",
            ...                                        page_size=10, page_token=response.next_page_token)
        """
        params = {
            "Status": status,
            "PageSize": page_size,
        }

        if keyword:
            params["Keyword"] = keyword

        if page_token:
            params["PageToken"] = page_token

        response = self._make_request(
            "GET", f"tenants/{tenant_id}/assessments/", params=params
        )
        return ListAssessmentsOutput.model_validate(response)

    def get_assessment(self, tenant_id: str, assessment_id: str) -> GetAssessmentOutput:
        """Get details of a specific assessment.

        Args:
            tenant_id: ID of the tenant the assessment belongs to.
            assessment_id: ID of the assessment to get details for.

        Returns:
            GetAssessmentOutput: Object containing assessment details.

        Raises:
            ResourceNotFoundError: If the assessment does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.assessment
            >>> response = client.get_assessment("tenant-123", "assessment-123")
            >>> print(f"Assessment name: {response.name}")
        """
        response = self._make_request(
            "GET", f"tenants/{tenant_id}/assessments/{assessment_id}"
        )
        return GetAssessmentOutput.model_validate(response)

    def create_assessment(
        self, tenant_id: str, data: CreateAssessmentInput
    ) -> CreateAssessmentOutput:
        """Create a new assessment in a tenant.

        Args:
            tenant_id: The ID of the tenant to create the assessment in.
            data: The assessment data to create.

        Returns:
            CreateAssessmentOutput: Object containing the created assessment details.

        Raises:
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.assessment
            >>> data = CreateAssessmentInput(
            ...     name="My Assessment",
            ...     description="Assessment description",
            ...     review_owner="example_user",  # Cannot contain special characters like @, +, -, =
            ...     scope={
            ...         "Project": {},
            ...         "Accounts": [
            ...             {"AccountNumber": "123456789012", "Regions": ["us-east-1", "us-west-2"]}
            ...         ]
            ...     },
            ...     region_code="us-east-1",
            ...     environment="PRODUCTION",
            ...     industry_type="Technology",
            ...     industry="Software",
            ... )
            >>> response = client.create_assessment("tenant-123", data)
            >>> print(f"Created assessment with ID: {response.id}")
        """
        # Create the payload with fields in the exact order expected by the test
        payload = {
            "AssessmentName": data.name,
            "Description": data.description,
            "ReviewOwner": data.review_owner,
            "Scope": data.scope,
            "Lenses": data.lenses,
            "Tags": data.tags if data.tags else {},
            "RegionCode": data.region_code,
            "Environment": data.environment,
        }

        # Add optional fields if they have values
        if data.hosted_account_number is not None:
            payload["HostedAccountNumber"] = data.hosted_account_number
        if data.diagram_url is not None:
            payload["DiagramURL"] = data.diagram_url
        if data.industry_type is not None:
            payload["IndustryType"] = data.industry_type
        if data.industry is not None:
            payload["Industry"] = data.industry

        response = self._make_request(
            "POST",
            f"tenants/{tenant_id}/assessments/",
            json=payload,
        )
        return CreateAssessmentOutput.model_validate(response)

    def list_questions(
        self, tenant_id: str, assessment_id: str, pillar_id: str
    ) -> ListQuestionsOutput:
        """List questions by pillar ID for an assessment in a tenant.

        Args:
            tenant_id: ID of the tenant the assessment belongs to.
            assessment_id: ID of the assessment to get questions for.
            pillar_id: ID of the pillar to get questions for. Allowed values: security, costOptimization,
                reliability, performance, operationalExcellence, sustainability.

        Returns:
            ListQuestionsOutput: Object containing list of questions for the specified pillar.

        Raises:
            ResourceNotFoundError: If the assessment or pillar does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.assessment
            >>> response = client.list_questions("tenant-123", "assessment-123", "pillar-123")
            >>> for question in response.questions:
            ...     print(f"{question.id}: {question.title}")
        """
        params = {"PillarId": pillar_id}

        response = self._make_request(
            "GET",
            f"tenants/{tenant_id}/assessments/{assessment_id}/questions",
            params=params,
        )
        return ListQuestionsOutput.model_validate(response)

    def get_question(
        self, tenant_id: str, assessment_id: str, question_id: str
    ) -> GetQuestionOutput:
        """Get details of a specific question for an assessment in a tenant.

        Args:
            tenant_id: ID of the tenant the assessment belongs to.
            assessment_id: ID of the assessment the question belongs to.
            question_id: ID of the question to get details for.

        Returns:
            GetQuestionOutput: Object containing question details.

        Raises:
            ResourceNotFoundError: If the assessment or question does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.assessment
            >>> response = client.get_question("tenant-123", "assessment-123", "question-123")
            >>> print(f"Question: {response.title}")
            >>> print(f"Status: {'Answered' if response.is_answered else 'Not answered'}")
        """
        response = self._make_request(
            "GET",
            f"tenants/{tenant_id}/assessments/{assessment_id}/questions/{question_id}",
        )
        # Create the output model and set the id field
        result = GetQuestionOutput.model_validate(response)
        result.id = question_id

        # If PillarName is not in the response but we have a PillarId, try to set it
        if not result.pillar_name and result.pillar_id:
            # Common pillar mappings
            pillar_names = {
                "operational-excellence": "Operational Excellence",
                "security": "Security",
                "reliability": "Reliability",
                "performance-efficiency": "Performance Efficiency",
                "cost-optimization": "Cost Optimization",
                "sustainability": "Sustainability",
            }
            result.pillar_name = pillar_names.get(result.pillar_id, result.pillar_id)

        return result

    def answer_question(
        self,
        tenant_id: str,
        assessment_id: str,
        question_id: str,
        data: AnswerQuestionInput,
    ) -> AnswerQuestionOutput:
        """Answer a specific question for an assessment in a tenant.

        Args:
            tenant_id: ID of the tenant the assessment belongs to.
            assessment_id: ID of the assessment the question belongs to.
            question_id: ID of the question to answer.
            data: The answer data for the question.

        Returns:
            AnswerQuestionOutput: Object containing the status and message from the API.

        Raises:
            ResourceNotFoundError: If the assessment or question does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.assessment
            >>> data = AnswerQuestionInput(
            ...     Reason="ARCHITECTURE_CONSTRAINTS",
            ...     ChoiceUpdates={"choice1": {"Status": "SELECTED"}, "choice2": {"Status": "SELECTED"}},
            ...     Notes="Additional notes about the answer",
            ...     IsApplicable=True,
            ...     LensAlias="wellarchitected"
            ... )
            >>> response = client.answer_question("tenant-123", "assessment-123", "question-123", data)
            >>> print(f"Status: {response.status}, Message: {response.message}")
        """
        # The API expects the data directly, not wrapped
        model_data = data.model_dump(by_alias=True)

        response = self._make_request(
            "PUT",
            f"tenants/{tenant_id}/assessments/{assessment_id}/questions/{question_id}",
            json=model_data,
        )

        # Create the output model with the success response
        result = AnswerQuestionOutput.model_validate(response)

        # Set the question ID from the parameter
        result.id = question_id

        return result

    def list_findings(
        self,
        tenant_id: str,
        assessment_id: str,
        status: Optional[List[str]] = None,
        severity: Optional[List[str]] = None,
        account_number: Optional[List[str]] = None,
        region_code: Optional[List[str]] = None,
        resource_type: Optional[List[str]] = None,
        question_ids: Optional[List[str]] = None,
        resource_ids: Optional[List[str]] = None,
        pillar_ids: Optional[List[str]] = None,
        check_ids: Optional[List[str]] = None,
        best_practice_ids: Optional[List[str]] = None,
        best_practice_risk: Optional[List[str]] = None,
        page_size: int = 10,
        page_token: Optional[str] = None,
    ) -> ListFindingsOutput:
        """List findings for a specific assessment in a tenant.

        Args:
            tenant_id: ID of the tenant the assessment belongs to.
            assessment_id: ID of the assessment to list findings for.
            status: Optional list of statuses to filter findings by.
            severity: Optional list of severities to filter findings by (e.g., 'HIGH', 'MEDIUM', 'LOW').
            account_number: Optional list of account numbers to filter findings by.
            region_code: Optional list of region codes to filter findings by.
            resource_type: Optional list of resource types to filter findings by.
            question_ids: Optional list of question IDs to filter findings by.
            resource_ids: Optional list of resource IDs to filter findings by.
            pillar_ids: Optional list of pillar IDs to filter findings by. Allowed values: security, costOptimization,
                reliability, performance, operationalExcellence, sustainability.
            page_size: The number of findings per page (default: 10).
            page_token: Token for pagination.

        Returns:
            ListFindingsOutput: Object containing list of findings and pagination info.

        Raises:
            ResourceNotFoundError: If the assessment does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.assessment
            >>> response = client.list_findings(
            ...     tenant_id="tenant-123",
            ...     assessment_id="assessment-123",
            ...     severity=["HIGH"],
            ...     page_size=10
            ... )
            >>> for finding in response.records:
            ...     print(f"{finding.finding_id}: {finding.title} - {finding.severity}")
            >>> # To get the next page of results:
            >>> if response.next_page_token:
            ...     next_page = client.list_findings(
            ...         tenant_id="tenant-123",
            ...         assessment_id="assessment-123",
            ...         severity=["HIGH"],
            ...         page_size=10,
            ...         page_token=response.next_page_token
            ...     )
        """
        params: Dict[str, Union[str, List[str]]] = {
            "PageSize": str(page_size),
        }
        if page_token is not None:
            params["PageToken"] = page_token

        filter_params = [
            ("Status", status),
            ("Severity", severity),
            ("AccountNumber", account_number),
            ("RegionCode", region_code),
            ("ResourceType", resource_type),
            ("QuestionIds", question_ids),
            ("ResourceIds", resource_ids),
            ("PillarIds", pillar_ids),
            ("CheckIds", check_ids),
            ("BestPracticeIds", best_practice_ids),
            ("BestPracticeRisk", best_practice_risk),
        ]

        for param_name, param_value in filter_params:
            if param_value is None:
                continue
            if isinstance(param_value, list):
                if not param_value:
                    continue
                if len(param_value) == 1:
                    params[param_name] = str(param_value[0])
                else:
                    params[param_name] = [str(v) for v in param_value]
            else:
                params[param_name] = str(param_value)

        response = self._make_request(
            "GET",
            f"tenants/{tenant_id}/assessments/{assessment_id}/findings",
            params=params,
        )
        return ListFindingsOutput.model_validate(response)

    def run_assessment(
        self, tenant_id: str, assessment_id: str, data: RunAssessmentInput
    ) -> RunAssessmentOutput:
        """Run an assessment for a specific tenant.

        Args:
            tenant_id: ID of the tenant the assessment belongs to.
            assessment_id: ID of the assessment to run.
            data: Input data for running the assessment.

        Returns:
            RunAssessmentOutput: Object containing the run ID of the assessment.

        Raises:
            ResourceNotFoundError: If the assessment does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.assessment
            >>> run_input = RunAssessmentInput(
            ...     lens_name="AWS Well-Architected Framework",
            ...     pillar_id="security",
            ...     question_id="question-123",
            ...     best_practice_id="best-practice-456"
            ... )
            >>> response = client.run_assessment("tenant-123", "assessment-456", run_input)
            >>> print(f"Run ID: {response.run_id}")
        """
        # Prepare the payload using the input model
        payload = {
            "LensName": data.lens_name,
            "PillarId": data.pillar_id,
            "QuestionId": data.question_id,
            "BestPracticeId": data.best_practice_id,
        }

        # Make the POST request to run the assessment
        response = self._make_request(
            "POST",
            f"tenants/{tenant_id}/assessments/{assessment_id}/run",
            json=payload,
        )

        # Validate and return the output model
        return RunAssessmentOutput.model_validate(response)

    def generate_report(
        self, tenant_id: str, assessment_id: str, data: GenerateAssessmentReportInput
    ) -> GenerateAssessmentReportOutput:
        """Generate a report for a specific assessment.

        Args:
            tenant_id: ID of the tenant the assessment belongs to.
            assessment_id: ID of the assessment to generate the report for.
            data: Input data for generating the report.

        Returns:
            GenerateAssessmentReportOutput: Object containing the report ID.

        Raises:
            ResourceNotFoundError: If the assessment does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.assessment
            >>> data = GenerateAssessmentReportInput(
            ...     cloud_provider="AWS",
            ...     pillar_ids=["security", "reliability"],
            ...     severity=["High", "Medium"],
            ...     status=["Failed"],
            ...     account_number=["123456789012"],
            ...     region_code=["us-east-1", "us-west-2"],
            ...     unique_report=True,
            ...     lenses=["AWS Well-Architected Framework"]
            ...     best_practice_risk_exposure=["High", "Medium"]
            ... )
            >>> response = client.generate_report("tenant-123", "assessment-123", data)
            >>> print(f"Report ID: {response.report_id}")
        """
        # Prepare the payload using the input model
        payload = {
            "CloudProvider": data.cloud_provider,
            "PillarIds": data.pillar_ids,
            "Severity": data.severity,
            "Status": data.status,
            "AccountNumber": data.account_number,
            "RegionCode": data.region_code,
            "UniqueReport": data.unique_report,
            "Lenses": data.lenses,
            "BestPracticeRiskExposure": data.best_practice_risk_exposure,
        }

        # Make the POST request to generate the report
        response = self._make_request(
            "POST",
            f"tenants/{tenant_id}/assessments/{assessment_id}/reports",
            json=payload,
        )

        # Validate and return the output model
        return GenerateAssessmentReportOutput.model_validate(response)
