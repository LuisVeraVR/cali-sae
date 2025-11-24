"""
CSV/TXT Parser for Juan Camilo Rosas invoices
Reads plain text invoice files and converts to domain entities
"""
import csv
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
from pathlib import Path
from ...domain.entities.invoice import Invoice
from ...domain.entities.product import Product


class UnitConverter:
    """Handles unit conversions for Juan Camilo Rosas products"""

    # Conversion table: {unit_name: {units: X, weight_per_unit_kg: Y, total_kg: Z}}
    CONVERSIONS = {
        'MEGA': {
            'units': 5,
            'weight_description': '7 LIBRAS C/U',
            'total_kg': Decimal('17.5')
        },
        'REDONDA': {
            'units': 48,
            'weight_description': '1 LIBRA C/U',
            'total_kg': Decimal('24')
        },
        'LIBRAS': {
            'units': 10,
            'weight_description': '4 LIBRAS C/U',
            'total_kg': Decimal('20')
        },
        'KAO': {
            'units': 20,
            'weight_description': '',
            'total_kg': Decimal('20')  # Default, adjust if needed
        },
        'PASTUANIO': {
            'units': 16,
            'weight_description': 'KILOS',
            'total_kg': Decimal('16')
        },
        'PASTILLA LIBRA': {
            'units': 32,
            'weight_description': 'UNIDADES',
            'total_kg': Decimal('32')  # Default, adjust if needed
        }
    }

    @classmethod
    def convert_quantity(cls, unit_name: str, original_quantity: Decimal) -> Decimal:
        """
        Convert original quantity to the converted quantity based on unit type

        Args:
            unit_name: Name of the unit (MEGA, REDONDA, etc.)
            original_quantity: Original quantity from the input file

        Returns:
            Converted quantity in the appropriate unit
        """
        unit_name_upper = unit_name.strip().upper()

        if unit_name_upper in cls.CONVERSIONS:
            conversion = cls.CONVERSIONS[unit_name_upper]
            # Converted quantity = original_quantity * total_kg
            return original_quantity * conversion['total_kg']

        # If no conversion found, return original quantity
        return original_quantity

    @classmethod
    def get_unit_measure(cls, unit_name: str) -> str:
        """
        Get the unit of measure for Reggis format
        Returns: Kg, Un, or Lt
        """
        unit_name_upper = unit_name.strip().upper()

        # Most conversions are in Kg
        if unit_name_upper in ['MEGA', 'REDONDA', 'LIBRAS', 'PASTUANIO']:
            return 'Kg'
        elif unit_name_upper in ['KAO', 'PASTILLA LIBRA']:
            return 'Un'

        # Default to Un (units)
        return 'Un'


class JCRCsvParser:
    """Parser for Juan Camilo Rosas CSV/TXT invoice files"""

    # Expected input columns
    INPUT_COLUMNS = [
        'NUMERO DE FACTURA',
        'IDENTIFICACION',
        'NOMBRE CLIENTE',
        'NOMBRE PRODUCTO',
        'CANTIDAD',
        'UNIDAD DE MEDIDA',
        'VALOR BRUTO',
        'FECHA FACTURA',
        'FECHA VENCIMIENTO'
    ]

    # Seller information (constant for Juan Camilo Rosas)
    SELLER_NIT = '1003516945'
    SELLER_NAME = 'JUAN CAMILO ROSAS'

    def __init__(self, file_path: str):
        """
        Initialize parser with file path

        Args:
            file_path: Path to the CSV or TXT file
        """
        self.file_path = Path(file_path)
        self.invoices: List[Invoice] = []

    def parse(self) -> List[Invoice]:
        """
        Parse the CSV/TXT file and return list of invoices

        Returns:
            List of Invoice entities
        """
        self.invoices = []

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                # Try to detect the delimiter
                sample = file.read(1024)
                file.seek(0)

                # Detect delimiter (comma, tab, or semicolon)
                delimiter = self._detect_delimiter(sample)

                reader = csv.DictReader(file, delimiter=delimiter)

                # Group rows by invoice number
                invoice_groups = self._group_by_invoice(reader)

                # Process each invoice
                for invoice_number, rows in invoice_groups.items():
                    invoice = self._create_invoice(invoice_number, rows)
                    if invoice:
                        self.invoices.append(invoice)

            return self.invoices

        except Exception as e:
            raise Exception(f"Error parsing CSV file: {str(e)}")

    def _detect_delimiter(self, sample: str) -> str:
        """Detect the delimiter used in the CSV file"""
        delimiters = [',', '\t', ';', '|']
        delimiter_counts = {d: sample.count(d) for d in delimiters}
        return max(delimiter_counts, key=delimiter_counts.get)

    def _group_by_invoice(self, reader: csv.DictReader) -> Dict[str, List[Dict[str, Any]]]:
        """Group rows by invoice number"""
        groups = {}

        for row in reader:
            # Normalize column names (remove extra spaces)
            normalized_row = {k.strip(): v.strip() if isinstance(v, str) else v
                            for k, v in row.items()}

            invoice_number = normalized_row.get('NUMERO DE FACTURA', '').strip()

            if not invoice_number:
                continue

            if invoice_number not in groups:
                groups[invoice_number] = []

            groups[invoice_number].append(normalized_row)

        return groups

    def _create_invoice(self, invoice_number: str, rows: List[Dict[str, Any]]) -> Invoice:
        """Create an Invoice entity from grouped rows"""
        if not rows:
            return None

        # Get common invoice data from first row
        first_row = rows[0]

        try:
            # Parse dates
            issue_date = self._parse_date(first_row.get('FECHA FACTURA', ''))
            due_date = self._parse_date(first_row.get('FECHA VENCIMIENTO', ''))

            # Create invoice
            invoice = Invoice(
                invoice_number=invoice_number,
                issue_date=issue_date,
                due_date=due_date,
                currency='COP',  # Default currency
                seller_nit=self.SELLER_NIT,
                seller_name=self.SELLER_NAME,
                seller_municipality='',  # Will be filled from UI or config
                buyer_nit=first_row.get('IDENTIFICACION', '').strip(),
                buyer_name=first_row.get('NOMBRE CLIENTE', '').strip()
            )

            # Add products
            for row in rows:
                product = self._create_product(row)
                if product:
                    invoice.add_product(product)

            return invoice

        except Exception as e:
            print(f"Error creating invoice {invoice_number}: {str(e)}")
            return None

    def _create_product(self, row: Dict[str, Any]) -> Product:
        """Create a Product entity from a row"""
        try:
            product_name = row.get('NOMBRE PRODUCTO', '').strip()
            unit_of_measure = row.get('UNIDAD DE MEDIDA', '').strip()
            original_quantity = self._parse_decimal(row.get('CANTIDAD', '0'))
            valor_bruto = self._parse_decimal(row.get('VALOR BRUTO', '0'))

            # Convert quantity using UnitConverter
            converted_quantity = UnitConverter.convert_quantity(unit_of_measure, original_quantity)

            # Calculate unit price: valor_bruto / converted_quantity
            if converted_quantity > 0:
                unit_price = valor_bruto / converted_quantity
            else:
                unit_price = Decimal('0')

            # Get the appropriate unit measure for Reggis
            reggis_unit = UnitConverter.get_unit_measure(unit_of_measure)

            product = Product(
                name=product_name,
                underlying_code='SPN-1',  # Fixed value
                unit_of_measure=reggis_unit,
                quantity=converted_quantity,  # Converted quantity
                unit_price=unit_price,
                total_price=valor_bruto,
                iva_percentage=Decimal('0')  # Will be set later if needed
            )

            return product

        except Exception as e:
            print(f"Error creating product: {str(e)}")
            return None

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        if not date_str:
            return datetime.now()

        # Try different date formats
        date_formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%Y%m%d'
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        # If no format matches, return current date
        return datetime.now()

    def _parse_decimal(self, value: str) -> Decimal:
        """Parse string to Decimal, handling different formats"""
        if not value:
            return Decimal('0')

        # Remove currency symbols and spaces
        cleaned = value.strip().replace('$', '').replace(' ', '')

        # Handle comma as thousands separator and dot as decimal
        if ',' in cleaned and '.' in cleaned:
            # Format like 1,234.56
            cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Could be either thousands or decimal
            # If more than 2 digits after comma, it's thousands
            parts = cleaned.split(',')
            if len(parts[-1]) > 2:
                cleaned = cleaned.replace(',', '')
            else:
                cleaned = cleaned.replace(',', '.')

        try:
            return Decimal(cleaned)
        except:
            return Decimal('0')
