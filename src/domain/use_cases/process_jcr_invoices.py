"""
Process JCR Invoices Use Case
Processes Juan Camilo Rosas invoices from CSV/TXT files
"""
from typing import List, Callable, Optional
from datetime import datetime
from pathlib import Path
from ..entities.invoice import Invoice
from ..entities.report import Report
from ..repositories.report_repository import ReportRepositoryInterface


class ProcessJCRInvoices:
    """
    Use case for processing Juan Camilo Rosas invoices from CSV/TXT files
    """

    def __init__(
        self,
        report_repository: ReportRepositoryInterface,
        csv_parser,  # JCRCsvParser - injected from infrastructure
        reggis_exporter  # JCRReggisExporter - injected from infrastructure
    ):
        self.report_repository = report_repository
        self.csv_parser = csv_parser
        self.reggis_exporter = reggis_exporter

    def execute(
        self,
        csv_files: List[str],
        municipality: str,
        iva_percentage: str,
        username: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> tuple[bool, str, int]:
        """
        Process Juan Camilo Rosas invoice CSV/TXT files and export to Reggis format

        Args:
            csv_files: List of paths to CSV or TXT files
            municipality: Municipality name for the invoices
            iva_percentage: IVA percentage to use
            username: Username of the person processing
            progress_callback: Optional callback for progress updates (current, total)

        Returns:
            Tuple of (success, message, records_processed)
        """
        if not csv_files:
            return False, "No se seleccionaron archivos CSV/TXT", 0

        all_invoices: List[Invoice] = []
        original_quantities = {}  # Store original quantities for export
        total_files = len(csv_files)

        # Parse all CSV/TXT files
        for idx, csv_file in enumerate(csv_files):
            if progress_callback:
                progress_callback(idx, total_files)

            try:
                # Create parser instance for this file
                from ...infrastructure.parsers.jcr_csv_parser import JCRCsvParser

                parser = JCRCsvParser(csv_file)
                invoices = parser.parse()

                # Store original quantities before conversion
                for invoice in invoices:
                    for product in invoice.products:
                        key = (invoice.invoice_number, product.name)
                        # The original quantity is stored separately
                        # For now, we'll use the converted quantity
                        # This should be enhanced to store actual original from file
                        original_quantities[key] = product.quantity

                    # Set municipality if not already set
                    if not invoice.seller_municipality:
                        invoice.seller_municipality = municipality

                all_invoices.extend(invoices)

            except Exception as e:
                # Continue processing other files even if one fails
                print(f"Error processing {csv_file}: {str(e)}")
                return False, f"Error procesando archivo {Path(csv_file).name}: {str(e)}", 0

        if not all_invoices:
            return False, "No se encontraron facturas válidas en los archivos", 0

        # Export invoices to Reggis format
        try:
            # Update exporter with municipality and IVA
            self.reggis_exporter.municipality = municipality
            self.reggis_exporter.iva_percentage = iva_percentage

            output_file = self.reggis_exporter.export_to_reggis_csv(
                all_invoices,
                original_quantities
            )
            message = f"Datos exportados exitosamente al formato Reggis:\n{output_file}"

        except Exception as e:
            return False, f"Error al exportar datos: {str(e)}", 0

        # Calculate total records (sum of all products in all invoices)
        total_records = sum(invoice.get_product_count() for invoice in all_invoices)

        # Calculate total file size
        total_size = sum(
            Path(csv_file).stat().st_size
            for csv_file in csv_files
            if Path(csv_file).exists()
        )

        # Create report
        report = Report(
            id=None,
            username=username,
            company="JUAN CAMILO ROSAS",
            filename=", ".join([Path(f).name for f in csv_files]),
            records_processed=total_records,
            created_at=datetime.now(),
            file_size=total_size
        )

        self.report_repository.create(report)

        if progress_callback:
            progress_callback(total_files, total_files)

        return True, message, total_records
