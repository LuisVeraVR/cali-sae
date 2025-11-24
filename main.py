"""
Main Entry Point - Cali SAE
Sistema de Facturas Electrónicas
Clean Architecture with PyQt6
"""
import sys
from PyQt6.QtWidgets import QApplication

# Domain layer
from src.domain.use_cases.authenticate_user import AuthenticateUser, ChangePassword
from src.domain.use_cases.process_invoices import ProcessInvoices
from src.domain.use_cases.process_jcr_invoices import ProcessJCRInvoices
from src.domain.use_cases.process_paisano_invoices import ProcessPaisanoInvoices
from src.domain.use_cases.generate_report import GetReports, ExportReports
from src.domain.use_cases.check_updates import CheckUpdates, DownloadUpdate

# Infrastructure layer
from src.infrastructure.database.sqlite_user_repository import SQLiteUserRepository
from src.infrastructure.database.sqlite_report_repository import SQLiteReportRepository
from src.infrastructure.database.paisano_conversion_repository import (
    PaisanoConversionRepository,
)
from src.infrastructure.parsers.xml_invoice_parser import XMLInvoiceParser
from src.infrastructure.exporters.invoice_exporter import InvoiceExporter
from src.infrastructure.exporters.csv_exporter import CSVExporter
from src.infrastructure.exporters.jcr_reggis_exporter import JCRReggisExporter
from src.infrastructure.updater.github_updater import GitHubUpdater

# Presentation layer
from src.presentation.controllers.auth_controller import AuthController
from src.presentation.controllers.main_controller import MainController
from src.presentation.controllers.reports_controller import ReportsController
from src.presentation.views.auth_window import AuthWindow
from src.presentation.views.main_window import MainWindow
from src.presentation.views.reports_window import ReportsWindow


class Application:
    """Main application class with dependency injection"""

    VERSION = "2.1.0"
    DB_PATH = "facturas_users.db"

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Cali SAE")
        self.app.setApplicationVersion(self.VERSION)

        # Initialize repositories
        self.user_repository = SQLiteUserRepository(self.DB_PATH)
        self.report_repository = SQLiteReportRepository(self.DB_PATH)
        self.paisano_conversion_repository = PaisanoConversionRepository(self.DB_PATH)

        # Initialize infrastructure services
        self.xml_parser = XMLInvoiceParser()
        self.invoice_exporter = InvoiceExporter()
        self.csv_exporter = CSVExporter()
        self.jcr_reggis_exporter = JCRReggisExporter()
        self.github_updater = GitHubUpdater(
            repo_owner="LuisVeraVR", repo_name="cali-sae"
        )

        # Initialize use cases for authentication
        self.authenticate_use_case = AuthenticateUser(self.user_repository)
        self.change_password_use_case = ChangePassword(self.user_repository)

        # Initialize auth controller
        self.auth_controller = AuthController(
            self.authenticate_use_case, self.change_password_use_case
        )

        # Windows
        self.auth_window = None
        self.main_window = None
        self.reports_window = None

        # Current user (set after login)
        self.current_user = None

    def run(self):
        """Run the application"""
        self.show_auth_window()
        return self.app.exec()

    def show_auth_window(self):
        """Show authentication window"""
        self.auth_window = AuthWindow(self.auth_controller)
        self.auth_window.login_successful.connect(self.on_login_successful)
        self.auth_window.show()

    def on_login_successful(self, user):
        """Handle successful login"""
        self.current_user = user

        # Initialize use cases that require user context
        self.process_invoices_use_case = ProcessInvoices(
            self.report_repository, self.xml_parser, self.invoice_exporter
        )

        self.process_jcr_invoices_use_case = ProcessJCRInvoices(
            self.report_repository,
            None,  # csv_parser - will be created per file
            self.jcr_reggis_exporter,
        )

        self.process_paisano_invoices_use_case = ProcessPaisanoInvoices(
            self.report_repository,
            self.xml_parser,
            self.jcr_reggis_exporter,
            self.paisano_conversion_repository,
        )

        self.get_reports_use_case = GetReports(self.report_repository)

        self.export_reports_use_case = ExportReports(
            self.report_repository, self.csv_exporter
        )

        self.check_updates_use_case = CheckUpdates(self.github_updater, self.VERSION)
        self.download_update_use_case = DownloadUpdate(self.github_updater)

        # Initialize main controller
        self.main_controller = MainController(
            self.process_invoices_use_case,
            self.process_jcr_invoices_use_case,
            self.process_paisano_invoices_use_case,
            self.check_updates_use_case,
            self.download_update_use_case,
            self.current_user,
            self.paisano_conversion_repository,
        )

        # Initialize reports controller
        self.reports_controller = ReportsController(
            self.get_reports_use_case, self.export_reports_use_case
        )

        # Show main window
        self.show_main_window()

    def show_main_window(self):
        """Show main application window"""
        self.main_window = MainWindow(self.main_controller, self.reports_controller)
        self.main_window.logout_requested.connect(self.on_logout)
        self.main_window.reports_requested.connect(self.show_reports_window)
        self.main_window.show()

    def show_reports_window(self):
        """Show reports window (admin only)"""
        if self.main_controller.is_admin():
            if self.reports_window is None or not self.reports_window.isVisible():
                self.reports_window = ReportsWindow(
                    self.reports_controller, self.main_window
                )
                self.reports_window.show()
            else:
                self.reports_window.raise_()
                self.reports_window.activateWindow()

    def on_logout(self):
        """Handle user logout"""
        self.current_user = None
        self.main_window = None
        self.reports_window = None
        self.show_auth_window()


def main():
    """Main entry point"""
    app = Application()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
