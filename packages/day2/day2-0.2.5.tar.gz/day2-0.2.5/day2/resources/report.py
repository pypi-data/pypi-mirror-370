"""Reports resource implementation for the MontyCloud DAY2 SDK."""

from day2.client.base import BaseClient
from day2.models.report import (
    GetReportDetailsOutput,
    GetReportOutput,
    ListReportsOutput,
)
from day2.session import Session


class ReportClient(BaseClient):
    """Client for interacting with the Report service."""

    def __init__(self, session: Session) -> None:
        """Initialize a new ReportClient.

        Args:
            session: MontyCloud session.
        """
        super().__init__(session, "report")

    def get_report_details(
        self, tenant_id: str, report_id: str
    ) -> GetReportDetailsOutput:
        """Get details of a specific report.

        Args:
            tenant_id: ID of the tenant that owns the report.
            report_id: ID of the report to retrieve details for.

        Returns:
            GetReportDetailsOutput: Object containing report details.

        Raises:
            ResourceNotFoundError: If the report does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.report
            >>> response = client.get_report_details(tenant_id="tenant-123", report_id="report-123")
            >>> print(f"Report Type: {response.report_type}")
            >>> print(f"Report Status: {response.status}")
            >>> print(f"Export Format: {response.export_format}")
        """
        response = self._make_request("GET", f"tenants/{tenant_id}/reports/{report_id}")
        return GetReportDetailsOutput.model_validate(response)

    def get_report(
        self, tenant_id: str, report_id: str, file_name: str
    ) -> GetReportOutput:
        """Get the download URL for a specific report.

        Args:
            tenant_id: ID of the tenant that owns the report.
            report_id: ID of the report to retrieve.
            file_name: Desired name for the downloaded report file.

        Returns:
            GetReportOutput: Object containing the download URL.

        Raises:
            ResourceNotFoundError: If the report does not exist.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.report
            >>> response = client.get_report(tenant_id="tenant-123", report_id="report-123", file_name="test_filename")
            >>> print(f"Download URL: {response.download_url}")
        """
        params = {"FileName": file_name}

        response = self._make_request(
            "GET",
            f"tenants/{tenant_id}/reports/{report_id}/download-url",
            params=params,
        )
        return GetReportOutput.model_validate(response)

    def list_reports(
        self, tenant_id: str, cloud_provider: str = "AWS"
    ) -> ListReportsOutput:
        """Retrieves up to 100 of the most recent reports for a tenant, ordered by creation time (newest first).

        Args:
            tenant_id: ID of the tenant that owns the reports.
            cloud_provider: Cloud provider for which to list reports (default is "AWS").

        Returns:
            ListReportsOutput: Object containing a list of report items (maximum 100).

        Raises:
            ResourceNotFoundError: If no reports are found.
            ClientError: If the request is invalid.
            ServerError: If an internal server error occurs.
            AuthenticationError: If authentication fails.

        Examples:
            >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
            >>> client = session.report
            >>> response = client.list_reports(tenant_id="tenant-123", cloud_provider="AWS")
            >>> for report in response.reports:
            >>> print(f"Report Name: {report.report_name}, Status: {report.status}")
        """
        params = {"CloudProvider": cloud_provider}
        response = self._make_request(
            "GET", f"tenants/{tenant_id}/reports/", params=params
        )
        return ListReportsOutput.model_validate(response)
