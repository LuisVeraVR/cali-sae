"""
Paisano PDF Parser - VERSION 2 (Windows Compatible)
Extrae datos de facturas PDF de El Paisano con múltiples patrones
"""
from __future__ import annotations

import re
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from ...domain.entities.invoice import Invoice
from ...domain.entities.product import Product


class PaisanoPDFParser:
    """Parser for El Paisano PDF invoices - VERSION 2"""

    DEFAULT_SELLER_NIT = "900691476"
    DEFAULT_SELLER_NAME = "DISTRIBUIDORA EL PAISANO SAS"

    def parse_pdf_file(self, pdf_path: str) -> Optional[Invoice]:
        """
        Parse a single Paisano PDF invoice into an Invoice entity.
        Returns None when parsing fails or no products are detected.
        """
        if pdfplumber is None:
            print("pdfplumber no esta instalado; instale con: pip install pdfplumber")
            return None

        path = Path(pdf_path)
        if not path.exists() or not path.is_file():
            return None

        try:
            with pdfplumber.open(path) as pdf:
                full_text = self._extract_text(pdf)

                # Debug: print first 500 chars
                print(f"\n[DEBUG] Primeros 500 caracteres del PDF:")
                print(full_text[:500])

                # Extract invoice metadata
                invoice_number = self._extract_invoice_number(full_text) or path.stem
                issue_date = self._extract_issue_date(full_text) or datetime.now()
                due_date = self._extract_due_date(full_text, issue_date)
                buyer_nit, buyer_name = self._extract_buyer(full_text)
                municipality = self._extract_municipality(full_text)

                print(f"[DEBUG] Factura: {invoice_number}")
                print(f"[DEBUG] Fecha: {issue_date}")
                print(f"[DEBUG] Cliente: {buyer_name}")

                # Extract products from text (multiple patterns)
                products = self._extract_products_from_text(full_text)

                print(f"[DEBUG] Productos extraídos: {len(products)}")

        except Exception as exc:
            print(f"Error parsing PDF {pdf_path}: {exc}")
            import traceback
            traceback.print_exc()
            return None

        if not products:
            print(f"No se encontraron productos en {pdf_path}")
            return None

        invoice = Invoice(
            invoice_number=invoice_number,
            issue_date=issue_date,
            due_date=due_date,
            currency="COP",
            seller_nit=self.DEFAULT_SELLER_NIT,
            seller_name=self.DEFAULT_SELLER_NAME,
            seller_municipality=municipality or "CALI",
            buyer_nit=buyer_nit,
            buyer_name=buyer_name,
            xml_filename=path.name,
            zip_filename="",
            processed_at=datetime.now(),
        )

        for product in products:
            invoice.add_product(product)

        return invoice

    # --- Metadata extraction ---
    def _extract_text(self, pdf) -> str:
        """Concatenate all text from the PDF pages"""
        chunks = []
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            chunks.append(page_text)
        return "\n".join(chunks)

    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number - El Paisano format: DP0XXXXXX"""
        # Try specific El Paisano format first
        match = re.search(r"(DP0\d{6})", text, re.IGNORECASE)
        if match:
            return match.group(1).upper()

        # Try "Numero:" pattern
        match = re.search(r"Numero:\s*([A-Z0-9\-]+)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None

    def _extract_issue_date(self, text: str) -> Optional[datetime]:
        """Extract issue date - El Paisano format: 2025-NOV-13"""
        # Try El Paisano format: 2025-NOV-13 or YYYY-MES-DD
        paisano_match = re.search(
            r"(\d{4})-(ENE|FEB|MAR|ABR|MAY|JUN|JUL|AGO|SEP|OCT|NOV|DIC)-(\d{2})",
            text,
            re.IGNORECASE
        )
        if paisano_match:
            return self._parse_paisano_date_parts(
                paisano_match.group(1),
                paisano_match.group(2),
                paisano_match.group(3)
            )

        # Fallback to standard formats
        date_match = re.search(r"(\d{2}[/-]\d{2}[/-]\d{4})", text)
        if date_match:
            date_str = date_match.group(1)
            for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(date_str, fmt)
                except Exception:
                    continue

        return None

    def _extract_due_date(self, text: str, issue_date: datetime) -> Optional[datetime]:
        """Extract due date - El Paisano format"""
        # Try to find "Fecha de Vencimiento: YYYY-MES-DD"
        due_match = re.search(
            r"Fecha de Vencimiento.*?(\d{4})-(ENE|FEB|MAR|ABR|MAY|JUN|JUL|AGO|SEP|OCT|NOV|DIC)-(\d{2})",
            text,
            re.IGNORECASE | re.DOTALL
        )
        if due_match:
            return self._parse_paisano_date_parts(
                due_match.group(1),
                due_match.group(2),
                due_match.group(3)
            )

        # Extract days from payment terms
        days_match = re.search(r"CREDITO A (\d+) DIAS", text, re.IGNORECASE)
        if days_match and issue_date:
            days = int(days_match.group(1))
            return issue_date + timedelta(days=days)

        # Default: 45 days
        return issue_date + timedelta(days=45) if issue_date else None

    def _parse_paisano_date_parts(self, year_str: str, month_str: str, day_str: str) -> Optional[datetime]:
        """Parse El Paisano date parts: year, month (ENE-DIC), day"""
        try:
            year = int(year_str)
            day = int(day_str)

            month_map = {
                "ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4,
                "MAY": 5, "JUN": 6, "JUL": 7, "AGO": 8,
                "SEP": 9, "OCT": 10, "NOV": 11, "DIC": 12
            }
            month = month_map.get(month_str.upper(), 1)

            return datetime(year, month, day)
        except Exception:
            return None

    def _extract_buyer(self, text: str) -> Tuple[str, str]:
        """Extract buyer name and NIT from text"""
        buyer_name = ""
        buyer_nit = ""

        # Try to find "Cliente :" pattern
        client_match = re.search(r"Cliente\s*:\s*([^\|]+)", text, re.IGNORECASE)
        if client_match:
            buyer_name = client_match.group(1).strip()

        # Find NIT - exclude seller NIT (900691476)
        nit_matches = re.findall(r"NIT\.*\s*:\s*([0-9\.\-]+)", text, re.IGNORECASE)
        for nit in nit_matches:
            cleaned = re.sub(r"[^0-9]", "", nit)
            if cleaned and cleaned != self.DEFAULT_SELLER_NIT:
                buyer_nit = cleaned
                break

        return buyer_nit, buyer_name

    def _extract_municipality(self, text: str) -> str:
        """Capture municipality from common labels"""
        # Try to find "Ciudad :" pattern
        muni_match = re.search(r"Ciudad\s*:\s*([A-Z]+)", text, re.IGNORECASE)
        if muni_match:
            return muni_match.group(1).strip()

        return "CALI"  # Default

    # --- Product extraction ---
    def _extract_products_from_text(self, text: str) -> List[Product]:
        """
        Extract products from text using MULTIPLE regex patterns.
        Tries different patterns to handle variations in PDF extraction.
        """
        products: List[Product] = []

        # Pattern 1: With pipe separators (most common)
        # |001 000002 FRIJOL CALIMA*500G 01 55 P25 105,000.00 0.00 5,775,000.00 0.00*|
        pattern1 = re.compile(
            r'\|(\d{3})\s+(\d{6})\s+(.+?)\s+\d{2}\s+(\d+)\s+([A-Z0-9]+)\s+([\d,\.]+)\s+[\d,\.]+\s+([\d,\.]+)\s+([\d\.]+)\*?\|'
        )

        for match in pattern1.finditer(text):
            product = self._parse_product_match(match)
            if product:
                products.append(product)

        if products:
            print(f"[DEBUG] Pattern 1 (pipe) encontró {len(products)} productos")
            return products

        # Pattern 2: Without pipe at end (some PDFs)
        # |001 000002 FRIJOL CALIMA*500G 01 55 P25 105,000.00 0.00 5,775,000.00 0.00*
        pattern2 = re.compile(
            r'\|(\d{3})\s+(\d{6})\s+(.+?)\s+\d{2}\s+(\d+)\s+([A-Z0-9]+)\s+([\d,\.]+)\s+[\d,\.]+\s+([\d,\.]+)\s+([\d\.]+)\*?'
        )

        for match in pattern2.finditer(text):
            product = self._parse_product_match(match)
            if product:
                products.append(product)

        if products:
            print(f"[DEBUG] Pattern 2 (no pipe end) encontró {len(products)} productos")
            return products

        # Pattern 3: Without initial pipe (alternate extraction)
        # 001 000002 FRIJOL CALIMA*500G 01 55 P25 105,000.00 0.00 5,775,000.00 0.00*
        pattern3 = re.compile(
            r'^(\d{3})\s+(\d{6})\s+(.+?)\s+\d{2}\s+(\d+)\s+([A-Z0-9]+)\s+([\d,\.]+)\s+[\d,\.]+\s+([\d,\.]+)\s+([\d\.]+)\*?',
            re.MULTILINE
        )

        for match in pattern3.finditer(text):
            product = self._parse_product_match(match)
            if product:
                products.append(product)

        if products:
            print(f"[DEBUG] Pattern 3 (no pipe start) encontró {len(products)} productos")
            return products

        # Pattern 4: Flexible spacing
        # Handles variable spaces between fields
        pattern4 = re.compile(
            r'(\d{3})\s+(\d{6})\s+(.+?)\s+\d{2}\s+(\d+)\s+([A-Z0-9]+)\s+([\d,\.]+)\s+[\d,\.]+\s+([\d,\.]+)\s+([\d\.]+)',
            re.MULTILINE
        )

        for match in pattern4.finditer(text):
            product = self._parse_product_match(match)
            if product:
                products.append(product)

        if products:
            print(f"[DEBUG] Pattern 4 (flexible) encontró {len(products)} productos")
        else:
            print("[DEBUG] Ningún patrón encontró productos")
            print(f"[DEBUG] Longitud del texto: {len(text)} caracteres")
            # Print sample lines that might be products
            print("[DEBUG] Líneas que contienen números de 3 dígitos:")
            for line in text.split('\n'):
                if re.match(r'.*\d{3}\s+\d{6}', line):
                    print(f"  {line[:100]}")

        return products

    def _parse_product_match(self, match) -> Optional[Product]:
        """Parse a regex match into a Product"""
        try:
            reg = match.group(1)
            item_code = match.group(2)
            description = match.group(3).strip()
            quantity_str = match.group(4)
            unit = match.group(5)  # This is the original unit code (UND, P25, CJ, etc.)
            unit_price_str = match.group(6).replace(",", "").replace(".", "")
            total_price_str = match.group(7).replace(",", "").replace(".", "")
            iva_str = match.group(8)

            # Adjust decimal places (El Paisano uses format: 105,000.00 = 105000.00)
            # Remove commas and keep last 2 digits as decimals
            def parse_paisano_number(s: str) -> Decimal:
                """Parse El Paisano number format: 105,000.00 or 5,084,033.00"""
                # Remove all commas and dots first
                cleaned = s.replace(",", "").replace(".", "")
                # Insert decimal point before last 2 digits
                if len(cleaned) >= 2:
                    integer_part = cleaned[:-2]
                    decimal_part = cleaned[-2:]
                    return Decimal(f"{integer_part}.{decimal_part}") if integer_part else Decimal(f"0.{decimal_part}")
                else:
                    return Decimal(cleaned) if cleaned else Decimal("0")

            quantity = Decimal(quantity_str)
            unit_price = parse_paisano_number(match.group(6))
            total_price = parse_paisano_number(match.group(7))
            iva_percentage = Decimal(iva_str.replace(",", "."))

            product = Product(
                name=description,
                underlying_code="SPN-1",
                unit_of_measure=unit,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                iva_percentage=iva_percentage,
                original_unit_code=unit,  # NUEVO: Preservar la unidad original (UND, P25, CJ, etc.)
            )

            return product

        except Exception as e:
            print(f"[DEBUG] Error parsing product match: {e}")
            return None
