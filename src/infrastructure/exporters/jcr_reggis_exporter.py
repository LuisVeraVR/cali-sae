
"""
Reggis CSV Exporter for Juan Camilo Rosas
Exports invoices to the specific Reggis format
"""
import csv
from pathlib import Path
from datetime import datetime
from typing import List
from decimal import Decimal

from ...domain.entities.invoice import Invoice


class JCRReggisExporter:
    """
    Exports Juan Camilo Rosas invoices to Reggis CSV format

    Reggis Format Columns:
    N? Factura, Nombre Producto, Codigo Subyacente, Unidad Medida en Kg,Un,Lt,
    Cantidad (5 decimales - separador coma), Precio Unitario (5 decimales - separador coma),
    Fecha Factura A?o-Mes-Dia, Fecha Pago A?o-Mes-Dia, Nit Comprador (Existente),
    Nombre Comprador, Nit Vendedor (Existente), Nombre Vendedor, Principal V,C,
    Municipio (Nombre Exacto de la Ciudad), Iva (N?%), Descripci?n, Activa,
    Factura Activa, Bodega, Incentivo, Cantidad Original (5 decimales - separador coma),
    Moneda (1,2,3), Valor Total
    """

    # Reggis column order
    REGGIS_COLUMNS = [
        'N? Factura',
        'Nombre Producto',
        'Codigo Subyacente',
        'Unidad Medida en Kg,Un,Lt',
        'Cantidad (5 decimales - separador coma)',
        'Precio Unitario (5 decimales - separador coma)',
        'Fecha Factura A?o-Mes-Dia',
        'Fecha Pago A?o-Mes-Dia',
        'Nit Comprador (Existente)',
        'Nombre Comprador',
        'Nit Vendedor (Existente)',
        'Nombre Vendedor',
        'Principal V,C',
        'Municipio (Nombre Exacto de la Ciudad)',
        'Iva (N?%)',
        'Descripci?n',
        'Activa',
        'Factura Activa',
        'Bodega',
        'Incentivo',
        'Cantidad Original (5 decimales - separador coma)',
        'Moneda (1,2,3)',
        'Valor Total'
    ]

    def __init__(self, municipality: str = '', iva_percentage: str = '0'):
        """
        Initialize exporter

        Args:
            municipality: Municipality name for all invoices
            iva_percentage: Default IVA percentage
        """
        self.municipality = municipality
        self.iva_percentage = iva_percentage

    def export_to_reggis_csv(
        self,
        invoices: List[Invoice],
        original_quantities: dict = None,
        company: str = "JUAN CAMILO ROSAS"
    ) -> str:
        """
        Export invoices to Reggis CSV format

        Args:
            invoices: List of Invoice entities
            original_quantities: Dictionary mapping (invoice_number, product_name) to original quantity
            company: Company name used for output folder/name

        Returns:
            Path to the generated CSV file
        """
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        date_folder = now.strftime("%d-%m-%Y")
        safe_company = company if company else "JUAN CAMILO ROSAS"
        prefix = safe_company.replace(" ", "_")
        filename = f"{prefix}_Reggis_Facturas_{timestamp}.csv"
        output_dir = Path("data") / safe_company / date_folder / "archivos"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename

        # Prepare rows
        rows = []
        for invoice in invoices:
            for product in invoice.products:
                # Get original quantity if available
                key = (invoice.invoice_number, product.name)
                if original_quantities and key in original_quantities:
                    original_qty = original_quantities[key]
                else:
                    # If not available, use the converted quantity
                    original_qty = product.quantity

                row = {
                    'N? Factura': invoice.invoice_number,
                    'Nombre Producto': product.name,
                    'Codigo Subyacente': 'SPN-1',
                    'Unidad Medida en Kg,Un,Lt': product.unit_of_measure,
                    'Cantidad (5 decimales - separador coma)': self._format_decimal(product.quantity),
                    'Precio Unitario (5 decimales - separador coma)': self._format_decimal(product.unit_price),
                    'Fecha Factura A?o-Mes-Dia': invoice.get_issue_date_formatted(),
                    'Fecha Pago A?o-Mes-Dia': invoice.get_due_date_formatted(),
                    'Nit Comprador (Existente)': invoice.buyer_nit,
                    'Nombre Comprador': invoice.buyer_name,
                    'Nit Vendedor (Existente)': invoice.seller_nit,  # Always '1003516945'
                    'Nombre Vendedor': invoice.seller_name,  # Always 'JUAN CAMILO ROSAS'
                    'Principal V,C': 'V',  # Always 'V'
                    'Municipio (Nombre Exacto de la Ciudad)': self.municipality if self.municipality else invoice.seller_municipality,
                    'Iva (N?%)': f"{self.iva_percentage}%",
                    'Descripci?n': '',  # Always empty
                    'Activa': '1',  # Always 1
                    'Factura Activa': '1',  # Always 1
                    'Bodega': '',
                    'Incentivo': '',
                    'Cantidad Original (5 decimales - separador coma)': self._format_decimal(original_qty),
                    'Moneda (1,2,3)': '1',  # Always 1 (COP)
                    'Valor Total': self._format_decimal(product.total_price)
                }
                rows.append(row)

        # Write CSV with UTF-8 BOM for Excel compatibility
        # Using comma as delimiter as specified in Reggis format
        with output_path.open('w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=self.REGGIS_COLUMNS,
                delimiter=',',  # Using comma for Reggis format
                extrasaction='ignore'
            )

            writer.writeheader()
            writer.writerows(rows)

        return str(output_path.resolve())

    def _format_decimal(self, value) -> str:
        """
        Format decimal with 5 decimals and comma as decimal separator

        Args:
            value: Decimal or numeric value

        Returns:
            Formatted string with comma as decimal separator
        """
        if isinstance(value, str):
            try:
                value = Decimal(value)
            except:
                return "0,00000"

        # Format with 5 decimals
        formatted = f"{float(value):.5f}"

        # Replace dot with comma
        return formatted.replace('.', ',')
