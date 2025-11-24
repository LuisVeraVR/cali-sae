"""
Reports Controller - Coordinates report operations between UI and use cases
"""
from typing import List, Tuple
from ...domain.use_cases.generate_report import GetReports, ExportReports
from ...domain.entities.report import Report


class ReportsController:
    """Controller for report operations"""

    def __init__(
        self,
        get_reports_use_case: GetReports,
        export_reports_use_case: ExportReports
    ):
        """
        Initialize reports controller

        Args:
            get_reports_use_case: Use case for getting reports
            export_reports_use_case: Use case for exporting reports
        """
        self.get_reports_use_case = get_reports_use_case
        self.export_reports_use_case = export_reports_use_case

    def get_all_reports(self) -> List[Report]:
        """
        Get all reports

        Returns:
            List of all reports
        """
        return self.get_reports_use_case.execute()

    def get_reports_by_user(self, username: str) -> List[Report]:
        """
        Get reports for a specific user

        Args:
            username: Username

        Returns:
            List of reports for the user
        """
        return self.get_reports_use_case.execute_by_user(username)

    def get_reports_by_company(self, company: str) -> List[Report]:
        """
        Get reports for a specific company

        Args:
            company: Company name

        Returns:
            List of reports for the company
        """
        return self.get_reports_use_case.execute_by_company(company)

    def export_reports(self, output_path: str) -> Tuple[bool, str]:
        """
        Export reports to CSV

        Args:
            output_path: Path where to save the CSV

        Returns:
            Tuple of (success, message)
        """
        return self.export_reports_use_case.execute(output_path)
