"""
Invoice Exporter - Main exporter that combines CSV and Excel exporters
"""
from typing import List, Optional
from .csv_exporter import CSVExporter
from .excel_exporter import ExcelExporter
from ...domain.entities.invoice import Invoice


class InvoiceExporter:
    """Main exporter that provides unified interface for CSV and Excel exports"""

    def __init__(self):
        self.csv_exporter = CSVExporter()
        self.excel_exporter = ExcelExporter()

    def export_to_csv(self, invoices: List[Invoice], company: str) -> str:
        """
        Export invoices to CSV

        Args:
            invoices: List of invoices
            company: Company name

        Returns:
            Path to generated CSV file
        """
        return self.csv_exporter.export_to_csv(invoices, company)

    def export_to_excel(
        self,
        invoices: List[Invoice],
        excel_file: str,
        sheet_name: Optional[str] = None
    ) -> None:
        """
        Export invoices to Excel

        Args:
            invoices: List of invoices
            excel_file: Path to Excel file
            sheet_name: Sheet name (optional)
        """
        self.excel_exporter.export_to_excel(invoices, excel_file, sheet_name)
