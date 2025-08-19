from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class GetReportDetailsOutput(BaseModel):
    """Details of a generated report.

    Attributes:
        report_id: Unique identifier for the report.
        report_type: Type of the report.
        status: Current status of the report generation (e.g., "Pending", "Success", "Failed").
        export_format: Format of the report (e.g., "PDF", "CSV", "JSON").
        created_at: Timestamp when the report was created.
        updated_at: Timestamp when the report was last updated.
        created_by: Identifier of the user who created the report.
    """

    report_id: str = Field(alias="ReportId")
    report_type: str = Field(alias="ReportType")
    status: str = Field(alias="Status")
    export_format: str = Field(alias="ExportFormat")
    created_at: datetime = Field(alias="CreatedAt")
    updated_at: datetime = Field(alias="UpdatedAt")
    created_by: str = Field(alias="CreatedBy")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


class GetReportOutput(BaseModel):
    """Details of a downloadable report.

    Attributes:
        download_url: URL to download the generated report.
    """

    download_url: str = Field(alias="DownloadURL")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")


# Models for handling listing report
class ReportItem(BaseModel):
    """Details of individual report item.

    Attributes:
        report_id: Unique identifier for the report.
        report_name: Name of the report.
        report_type: Type of the report.
        status: Current status of the report generation (e.g., "Pending", "Success", "Failed").
        export_format: Format of the report (e.g., "PDF", "CSV", "JSON").
        created_at: Timestamp when the report was created.
    """

    report_id: str = Field(alias="ReportId")
    report_name: str = Field(alias="ReportName")
    report_type: str = Field(alias="ReportType")
    status: str = Field(alias="Status")
    export_format: str = Field(alias="ExportFormat")
    created_at: datetime = Field(alias="CreatedAt")


class ListReportsOutput(BaseModel):
    """Output model for the ListReports API.

    Attributes:
        reports: List of report items.
    """

    reports: List[ReportItem] = Field(alias="Records", default=[])
