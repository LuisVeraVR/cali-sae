"""
Process Invoices Use Case
"""
from typing import List, Callable, Optional
from datetime import datetime
from pathlib import Path
from ..entities.invoice import Invoice
from ..entities.report import Report
from ..repositories.report_repository import ReportRepositoryInterface


class ProcessInvoices:
    """
    Use case for processing invoices from ZIP files containing XML files
    """

    def __init__(
        self,
        report_repository: ReportRepositoryInterface,
        xml_parser,  # Will be injected from infrastructure
        file_exporter  # Will be injected from infrastructure
    ):
        self.report_repository = report_repository
        self.xml_parser = xml_parser
        self.file_exporter = file_exporter

    def execute(
        self,
        zip_files: List[str],
        company: str,
        username: str,
        output_format: str = 'csv',  # 'csv' or 'excel'
        excel_file: Optional[str] = None,
        excel_sheet: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> tuple[bool, str, int]:
        """
        Process invoice ZIP files and export data

        Args:
            zip_files: List of paths to ZIP files containing XML invoices
            company: Company name (e.g., 'AGROBUITRON')
            username: Username of the person processing
            output_format: 'csv' or 'excel'
            excel_file: Path to Excel file (if output_format is 'excel')
            excel_sheet: Sheet name in Excel (if output_format is 'excel')
            progress_callback: Optional callback for progress updates (current, total)

        Returns:
            Tuple of (success, message, records_processed)
        """
        if not zip_files:
            return False, "No se seleccionaron archivos ZIP", 0

        if output_format == 'excel' and not excel_file:
            return False, "Debe seleccionar un archivo Excel", 0

        all_invoices: List[Invoice] = []
        total_files = len(zip_files)

        # Parse all ZIP files
        for idx, zip_file in enumerate(zip_files):
            if progress_callback:
                progress_callback(idx, total_files)

            try:
                invoices = self.xml_parser.parse_zip_file(zip_file)
                all_invoices.extend(invoices)
            except Exception as e:
                # Continue processing other files even if one fails
                print(f"Error processing {zip_file}: {str(e)}")
                continue

        if not all_invoices:
            return False, "No se encontraron facturas válidas en los archivos", 0

        # Export invoices
        try:
            if output_format == 'csv':
                output_file = self.file_exporter.export_to_csv(all_invoices, company)
                message = f"Datos exportados exitosamente a:\n{output_file}"
            else:  # excel
                self.file_exporter.export_to_excel(
                    all_invoices,
                    excel_file,
                    excel_sheet
                )
                message = f"Datos exportados exitosamente a:\n{excel_file}"
        except Exception as e:
            return False, f"Error al exportar datos: {str(e)}", 0

        # Calculate total records (sum of all products in all invoices)
        total_records = sum(invoice.get_product_count() for invoice in all_invoices)

        # Calculate total file size
        total_size = sum(Path(zip_file).stat().st_size for zip_file in zip_files if Path(zip_file).exists())

        # Create report
        report = Report(
            id=None,
            username=username,
            company=company,
            filename=", ".join([Path(f).name for f in zip_files]),
            records_processed=total_records,
            created_at=datetime.now(),
            file_size=total_size
        )

        self.report_repository.create(report)

        if progress_callback:
            progress_callback(total_files, total_files)

        return True, message, total_records
