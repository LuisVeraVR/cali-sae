
"""
CSV Exporter - Exports invoices and reports to CSV format
"""
import csv
from pathlib import Path
from datetime import datetime
from typing import List

from ...domain.entities.invoice import Invoice
from ...domain.entities.report import Report


class CSVExporter:
    """Exports data to CSV format with Excel compatibility (UTF-8 BOM, semicolon separator)"""

    def export_to_csv(self, invoices: List[Invoice], company: str) -> str:
        """
        Export invoices to CSV file

        Args:
            invoices: List of Invoice entities
            company: Company name (e.g., 'AGROBUITRON')

        Returns:
            Path to the generated CSV file
        """
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        date_folder = now.strftime("%d-%m-%Y")
        filename = f"{company}_Facturas_{timestamp}.csv"
        output_dir = Path("data") / company / date_folder / "archivos"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename

        # Define column order (specific for each company)
        column_order = self._get_column_order(company)

        # Prepare rows
        rows = []
        for invoice in invoices:
            for product in invoice.products:
                row = {
                    'N? Factura': invoice.invoice_number,
                    'Nombre Producto': product.name,
                    'Codigo Subyacente': product.underlying_code,
                    'Unidad Medida': product.unit_of_measure,
                    'Cantidad': product.get_formatted_quantity(),
                    'Precio Unitario': product.get_formatted_unit_price(),
                    'Precio Total': product.get_formatted_total_price(),
                    'Fecha Factura': invoice.get_issue_date_formatted(),
                    'Fecha Pago': invoice.get_due_date_formatted(),
                    'Nit Comprador': invoice.buyer_nit,
                    'Nombre Comprador': invoice.buyer_name,
                    'Nit Vendedor': invoice.seller_nit,
                    'Nombre Vendedor': invoice.seller_name,
                    'Principal V,C': 'V',
                    'Municipio': invoice.seller_municipality,
                    'Iva': f"{product.get_formatted_iva()}%",
                    'Descripci?n': '',
                    'Activa Factura': 'S?',
                    'Activa Bodega': 'S?',
                    'Incentivo': '',
                    'Cantidad Original': product.get_formatted_quantity(),
                    'Moneda': invoice.format_currency_code()
                }
                rows.append(row)

        # Write CSV with UTF-8 BOM for Excel compatibility
        with output_path.open('w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=column_order,
                delimiter=';',
                extrasaction='ignore'
            )

            writer.writeheader()
            writer.writerows(rows)

        return str(output_path.resolve())

    def export_reports(self, reports: List[Report], output_path: str) -> None:
        """
        Export reports to CSV file

        Args:
            reports: List of Report entities
            output_path: Path where to save the CSV file
        """
        column_order = [
            'Usuario',
            'Empresa',
            'Archivo',
            'Registros Procesados',
            'Fecha',
            'Tama?o (MB)'
        ]

        rows = []
        for report in reports:
            row = {
                'Usuario': report.username,
                'Empresa': report.company,
                'Archivo': report.filename,
                'Registros Procesados': report.records_processed,
                'Fecha': report.get_datetime(),
                'Tama?o (MB)': f"{report.get_file_size_mb():.2f}"
            }
            rows.append(row)

        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=column_order,
                delimiter=';'
            )

            writer.writeheader()
            writer.writerows(rows)

    def _get_column_order(self, company: str) -> List[str]:
        """
        Get column order based on company

        Args:
            company: Company name

        Returns:
            List of column names in order
        """
        # For now, all companies use the same column order
        # This can be customized per company in the future
        return [
            'N? Factura',
            'Nombre Producto',
            'Codigo Subyacente',
            'Unidad Medida',
            'Cantidad',
            'Precio Unitario',
            'Precio Total',
            'Fecha Factura',
            'Fecha Pago',
            'Nit Comprador',
            'Nombre Comprador',
            'Nit Vendedor',
            'Nombre Vendedor',
            'Principal V,C',
            'Municipio',
            'Iva',
            'Descripci?n',
            'Activa Factura',
            'Activa Bodega',
            'Incentivo',
            'Cantidad Original',
            'Moneda'
        ]
