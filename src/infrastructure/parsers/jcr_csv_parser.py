"""
CSV/TXT Parser for Juan Camilo Rosas invoices
Reads plain text invoice files and converts to domain entities
"""
import csv
import re
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
from pathlib import Path
from ...domain.entities.invoice import Invoice
from ...domain.entities.product import Product


class UnitConverter:
    """Handles unit conversions for Juan Camilo Rosas products"""

    # Factores de conversión por tipo de producto (según presentación)
    CONVERSION_FACTORS = {
        'GRANOS': Decimal('25'),
        'GRANO': Decimal('25'),
        'FRIJOL': Decimal('25'),
        'LENTEJA': Decimal('25'),
        'GARBANZO': Decimal('25'),
        'ARVEJA': Decimal('25'),
        'BLANQUILLO': Decimal('25'),
        'HARINA': Decimal('24'),
        'PASTAS': Decimal('24'),
        'PASTA': Decimal('24'),
        'ATUN': Decimal('48'),
        'ACEITE': Decimal('25')
    }

    # Conversion table: {unit_name: {units: X, weight_description: Y, total_kg: Z}}
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
            'total_kg': Decimal('20')  # 4 lb * 10 und ≈ 20 kg (regla de negocio)
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
    def extract_grams_from_name(cls, product_name: str) -> int:
        """
        Extrae los gramos del nombre del producto.
        Ejemplos: 'BLANQUILLO*400G FRIJOL' -> 400
                  'FRIJOL CALIMA*450G' -> 450
        Retorna 0 si no encuentra gramos.
        """
        name_upper = (product_name or "").upper()

        # Buscar patrones como 400G, 450G, etc.
        match = re.search(r'(\d+)\s*G\b', name_upper)
        if match:
            return int(match.group(1))

        return 0

    @classmethod
    def detect_product_category(cls, product_name: str) -> str:
        """
        Detecta la categoría del producto para aplicar el factor de conversión correcto.
        """
        name_upper = (product_name or "").upper()

        for category in cls.CONVERSION_FACTORS.keys():
            if category in name_upper:
                return category

        # Default: si no se detecta, asumimos GRANOS
        return 'GRANOS'

    @classmethod
    def convert_with_grams(cls, product_name: str, original_quantity: Decimal) -> Decimal:
        """
        Convierte la cantidad usando la fórmula de gramos:
        1. Buscar gramos en el nombre (ej: 400G)
        2. Si tiene gramos: (gramos * cantidad_original) / 1000 * factor_conversion
        3. Si no tiene gramos: cantidad_original (sin conversión)
        """
        grams = cls.extract_grams_from_name(product_name)

        if grams > 0:
            # Tiene gramos en el nombre: aplicar conversión
            # Paso 1: (gramos * cantidad_original) / 1000 = kilos
            kilos = (Decimal(str(grams)) * original_quantity) / Decimal('1000')

            # Paso 2: kilos * factor_conversion
            category = cls.detect_product_category(product_name)
            factor = cls.CONVERSION_FACTORS.get(category, Decimal('25'))

            converted_quantity = kilos * factor
            return converted_quantity
        else:
            # No tiene gramos: usar cantidad original sin conversión
            return original_quantity

    @classmethod
    def detect_unit_from_product_name(cls, product_name: str, unit_of_measure: str) -> str:
        """
        Detect unit type based on product name text plus unit_of_measure fallback.
        Example: 'Panela 4 libras cjx10 und. cod 210048' -> 'LIBRAS'
        """
        name = (product_name or "").upper()
        um = (unit_of_measure or "").upper().strip()

        if "MEGA" in name:
            return "MEGA"
        if "REDONDA" in name:
            return "REDONDA"
        # Panela 4 libras cjx10 und -> usamos LIBRAS para aplicar 20 kg por unidad
        if "4 LIBRAS" in name or "4 LIBRA" in name:
            return "LIBRAS"
        if "PASTUANIO" in name or "PASTU" in name:
            return "PASTUANIO"
        if "PASTILLA" in name and "LIBRA" in name:
            return "PASTILLA LIBRA"
        if "KAO" in name:
            return "KAO"
        if "KILO" in name or "KILOS" in name:
            return "PASTUANIO"

        # Fallback: lo que venga en UNIDAD DE MEDIDA o el nombre
        return um or name

    @classmethod
    def convert_quantity(cls, unit_name: str, original_quantity: Decimal) -> Decimal:
        """
        Convert original quantity to the converted quantity based on unit type
        """
        unit_name_upper = (unit_name or '').strip().upper()

        if unit_name_upper in cls.CONVERSIONS:
            conversion = cls.CONVERSIONS[unit_name_upper]
            # Converted quantity = original_quantity * total_kg (regla de negocio)
            return original_quantity * conversion['total_kg']

        # If no conversion found, return original quantity
        return original_quantity

    @classmethod
    def get_unit_measure(cls, unit_name: str) -> str:
        """
        Get the unit of measure for Reggis format
        Returns: Kg, Un, or Lt
        (Hoy ya no lo usamos para el export, pero lo dejamos por si se requiere)
        """
        unit_name_upper = (unit_name or '').strip().upper()

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
        'FECHA VENCIMIENTO',
        'IVA'  # Columna opcional de IVA
    ]

    # Seller information (constant for Juan Camilo Rosas)
    SELLER_NIT = '1003516945'
    SELLER_NAME = 'JUAN CAMILO ROSAS'

    def __init__(self, file_path: str, iva_percentage: str = '0'):
        """
        Initialize parser with file path

        Args:
            file_path: Path to the CSV or TXT file
            iva_percentage: Default IVA percentage to use if not in CSV
        """
        self.file_path = Path(file_path)
        self.iva_percentage = iva_percentage
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
            normalized_row = {
                (k.strip() if isinstance(k, str) else k):
                    (v.strip() if isinstance(v, str) else v)
                for k, v in row.items()
            }

            invoice_number = (normalized_row.get('NUMERO DE FACTURA', '') or '').strip()

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
                buyer_nit=(first_row.get('IDENTIFICACION', '') or '').strip(),
                buyer_name=(first_row.get('NOMBRE CLIENTE', '') or '').strip()
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
            product_name = (row.get('NOMBRE PRODUCTO', '') or '').strip()
            unit_of_measure = (row.get('UNIDAD DE MEDIDA', '') or '').strip()
            original_quantity = self._parse_decimal(row.get('CANTIDAD', '0'))
            valor_bruto = self._parse_decimal(row.get('VALOR BRUTO', '0'))

            # Leer el IVA del CSV si está disponible, sino usar el default
            iva_str = (row.get('IVA', '') or '').strip()
            if iva_str:
                # Remover el símbolo % si está presente
                iva_str = iva_str.replace('%', '').strip()
                iva_percentage = self._parse_decimal(iva_str)
            else:
                # Usar el IVA que viene del parámetro de la interfaz
                iva_str_clean = self.iva_percentage.replace('%', '').strip()
                iva_percentage = self._parse_decimal(iva_str_clean) if iva_str_clean else Decimal('0')

            # Usar la nueva lógica de conversión con gramos
            converted_quantity = UnitConverter.convert_with_grams(
                product_name,
                original_quantity
            )

            # Calculate unit price: valor_bruto / converted_quantity
            if converted_quantity > 0:
                unit_price = valor_bruto / converted_quantity
            else:
                unit_price = Decimal('0')

            # TODOS los productos se exportan en Kg
            reggis_unit = "Kg"

            product = Product(
                name=product_name,
                underlying_code='SPN-1',  # Fixed value
                unit_of_measure=reggis_unit,          # SIEMPRE Kg
                quantity=converted_quantity,          # Cantidad convertida
                unit_price=unit_price,
                total_price=valor_bruto,
                iva_percentage=iva_percentage,        # IVA correcto (5%, 19%, etc.)
                original_quantity=original_quantity   # Cantidad original del archivo
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
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue

        # If no format matches, return current date
        return datetime.now()

    def _parse_decimal(self, value) -> Decimal:
        """Parse value to Decimal, handling different formats (Colombian style included)"""
        if value is None:
            return Decimal('0')

        # Si ya viene como Decimal/int/float, lo convertimos a string
        if not isinstance(value, str):
            value = str(value)

        if not value:
            return Decimal('0')

        # Remove currency symbols and spaces
        cleaned = value.strip().replace('$', '').replace(' ', '')

        # Case: has BOTH comma and dot (e.g. 1,234.56 or 1.234,56)
        if ',' in cleaned and '.' in cleaned:
            # Asumimos: coma miles, punto decimal (1,234.56)
            cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Could be thousands or decimal separator
            parts = cleaned.split(',')
            if len(parts[-1]) > 2:
                # 1,234,567 -> 1234567
                cleaned = cleaned.replace(',', '')
            else:
                # 840,50 -> 840.50
                cleaned = cleaned.replace(',', '.')
        elif '.' in cleaned:
            # Only dots present: can be thousands separator (840.000) or decimal (840.5)
            parts = cleaned.split('.')
            # If all groups after the first are length 3, treat as thousands separator
            # 840.000 -> ['840', '000'] -> len('000') == 3 -> thousands
            # 1.234.567 -> ['1', '234', '567'] -> OK
            if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
                cleaned = ''.join(parts)

        try:
            return Decimal(cleaned)
        except Exception:
            return Decimal('0')
