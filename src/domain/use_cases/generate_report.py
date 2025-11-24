"""
Generate Report Use Case
"""
from typing import List
from datetime import datetime
from ..entities.report import Report
from ..repositories.report_repository import ReportRepositoryInterface


class GetReports:
    """Use case for retrieving reports"""

    def __init__(self, report_repository: ReportRepositoryInterface):
        self.report_repository = report_repository

    def execute(self) -> List[Report]:
        """
        Get all reports

        Returns:
            List of all reports
        """
        return self.report_repository.get_all()

    def execute_by_user(self, username: str) -> List[Report]:
        """
        Get reports for a specific user

        Args:
            username: The username

        Returns:
            List of reports for the user
        """
        return self.report_repository.get_by_username(username)

    def execute_by_company(self, company: str) -> List[Report]:
        """
        Get reports for a specific company

        Args:
            company: The company name

        Returns:
            List of reports for the company
        """
        return self.report_repository.get_by_company(company)


class GetReportStatistics:
    """Use case for getting report statistics"""

    def __init__(self, report_repository: ReportRepositoryInterface):
        self.report_repository = report_repository

    def execute(self) -> dict:
        """
        Get statistics about reports

        Returns:
            Dictionary with statistics
        """
        return self.report_repository.get_statistics()


class ExportReports:
    """Use case for exporting reports to CSV"""

    def __init__(
        self,
        report_repository: ReportRepositoryInterface,
        csv_exporter
    ):
        self.report_repository = report_repository
        self.csv_exporter = csv_exporter

    def execute(self, output_path: str) -> tuple[bool, str]:
        """
        Export all reports to CSV

        Args:
            output_path: Path where to save the CSV file

        Returns:
            Tuple of (success, message)
        """
        try:
            reports = self.report_repository.get_all()

            if not reports:
                return False, "No hay reportes para exportar"

            self.csv_exporter.export_reports(reports, output_path)
            return True, f"Reportes exportados exitosamente a:\n{output_path}"

        except Exception as e:
            return False, f"Error al exportar reportes: {str(e)}"
