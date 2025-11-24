"""
Main Controller - Coordinates main application logic between UI and use cases
"""
from typing import List, Callable, Optional, Tuple
from ...domain.use_cases.process_invoices import ProcessInvoices
from ...domain.use_cases.check_updates import CheckUpdates, DownloadUpdate
from ...domain.entities.user import User


class MainController:
    """Controller for main application operations"""

    def __init__(
        self,
        process_invoices_use_case: ProcessInvoices,
        check_updates_use_case: CheckUpdates,
        download_update_use_case: DownloadUpdate,
        current_user: User
    ):
        """
        Initialize main controller

        Args:
            process_invoices_use_case: Use case for processing invoices
            check_updates_use_case: Use case for checking updates
            download_update_use_case: Use case for downloading updates
            current_user: Current logged in user
        """
        self.process_invoices_use_case = process_invoices_use_case
        self.check_updates_use_case = check_updates_use_case
        self.download_update_use_case = download_update_use_case
        self.current_user = current_user

    def process_invoices(
        self,
        zip_files: List[str],
        company: str,
        output_format: str = 'csv',
        excel_file: Optional[str] = None,
        excel_sheet: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[bool, str, int]:
        """
        Process invoice ZIP files

        Args:
            zip_files: List of ZIP file paths
            company: Company name
            output_format: 'csv' or 'excel'
            excel_file: Excel file path (if format is 'excel')
            excel_sheet: Excel sheet name (if format is 'excel')
            progress_callback: Optional callback for progress updates

        Returns:
            Tuple of (success, message, records_processed)
        """
        return self.process_invoices_use_case.execute(
            zip_files=zip_files,
            company=company,
            username=self.current_user.username,
            output_format=output_format,
            excel_file=excel_file,
            excel_sheet=excel_sheet,
            progress_callback=progress_callback
        )

    def check_updates(self) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Check for updates from GitHub

        Returns:
            Tuple of (update_available, latest_version, download_url, release_notes)
        """
        return self.check_updates_use_case.execute()

    def download_update(self, download_url: str, output_path: str) -> Tuple[bool, str]:
        """
        Download update from URL

        Args:
            download_url: URL to download from
            output_path: Where to save the file

        Returns:
            Tuple of (success, message)
        """
        return self.download_update_use_case.execute(download_url, output_path)

    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.current_user.is_admin()

    def get_username(self) -> str:
        """Get current username"""
        return self.current_user.username

    def get_user_type(self) -> str:
        """Get current user type"""
        return self.current_user.user_type
