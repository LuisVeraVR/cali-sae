"""
Paisano PDF Parser
Extracts invoice metadata and product lines from El Paisano PDF invoices.
"""
from __future__ import annotations

import re
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

try:
    import pdfplumber
except ImportError:  # pragma: no cover - optional dependency until installed
    pdfplumber = None

from ...domain.entities.invoice import Invoice
from ...domain.entities.product import Product


class PaisanoPDFParser:
    """Parser for El Paisano PDF invoices"""

    DEFAULT_SELLER_NIT = "900691476"
    DEFAULT_SELLER_NAME = "DISTRIBUIDORA EL PAISANO SAS"

    def parse_pdf_file(self, pdf_path: str) -> Optional[Invoice]:
        """
        Parse a single Paisano PDF invoice into an Invoice entity.
        Returns None when parsing fails or no products are detected.
        """
        if pdfplumber is None:
            print("pdfplumber no esta instalado; instale pdfplumber para leer PDF de Paisano.")
            return None

        path = Path(pdf_path)
        if not path.exists() or not path.is_file():
            return None

        try:
            with pdfplumber.open(path) as pdf:
                full_text = self._extract_text(pdf)
                invoice_number = self._extract_invoice_number(full_text) or path.stem
                issue_date = self._extract_date(full_text) or datetime.now()
                due_date = self._extract_due_date(full_text, issue_date)
                buyer_nit, buyer_name = self._extract_buyer(full_text)
                municipality = self._extract_municipality(full_text)
                products = self._extract_products(pdf, full_text)
        except Exception as exc:
            print(f"Error parsing PDF {pdf_path}: {exc}")
            return None

        if not products:
            return None

        invoice = Invoice(
            invoice_number=invoice_number,
            issue_date=issue_date,
            due_date=due_date,
            currency="COP",
            seller_nit=self.DEFAULT_SELLER_NIT,
            seller_name=self.DEFAULT_SELLER_NAME,
            seller_municipality=municipality or "",
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
        """Try to capture invoice number from common labels"""
        patterns = [
            r"FACTURA(?: DE VENTA)?\s*(?:N[oº°]|#|No\.?|N°)?\s*[:#]?\s*([A-Z0-9\-]+)",
            r"NRO\s*[:#]?\s*([A-Z0-9\-]+)",
            r"DP\d{6,}",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_date(self, text: str) -> Optional[datetime]:
        """Find the first date in the text"""
        date_match = re.search(r"(\d{2}[/-]\d{2}[/-]\d{4})", text)
        if not date_match:
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", text)

        if not date_match:
            return None

        date_str = date_match.group(1)
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str, fmt)
            except Exception:
                continue
        return None

    def _extract_due_date(self, text: str, issue_date: datetime) -> Optional[datetime]:
        """Look for due date; fallback to issue_date + 45 days"""
        match = re.search(r"(VENCE|VENCIMIENTO)\s*[:#]?\s*(\d{2}[/-]\d{2}[/-]\d{4})", text, re.IGNORECASE)
        if match:
            raw = match.group(2)
            for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(raw, fmt)
                except Exception:
                    continue
        return issue_date + timedelta(days=45) if issue_date else None

    def _extract_buyer(self, text: str) -> Tuple[str, str]:
        """Extract buyer name and NIT from text"""
        buyer_name = ""
        buyer_nit = ""

        client_match = re.search(r"CLIENTE[:\s]+(.+)", text, re.IGNORECASE)
        if client_match:
            buyer_name = client_match.group(1).strip().splitlines()[0]

        nit_matches = re.findall(r"NIT[:\s]*([0-9\.\-]+)", text, re.IGNORECASE)
        for nit in nit_matches:
            cleaned = re.sub(r"[^0-9]", "", nit)
            if cleaned and cleaned != self.DEFAULT_SELLER_NIT:
                buyer_nit = cleaned
                break

        return buyer_nit, buyer_name

    def _extract_municipality(self, text: str) -> str:
        """Capture municipality from common labels"""
        muni_match = re.search(r"(CIUDAD|MUNICIPIO)[:\s]+([A-ZÁÉÍÓÚÜ\s]+)", text, re.IGNORECASE)
        if muni_match:
            return muni_match.group(2).strip()
        return ""

    # --- Product extraction ---
    def _extract_products(self, pdf, full_text: str) -> List[Product]:
        """Extract product rows from tables; fallback to text lines"""
        products: List[Product] = []
        for page in pdf.pages:
            try:
                tables = page.extract_tables() or []
            except Exception:
                tables = []

            for table in tables:
                products.extend(self._parse_table(table))

        if not products:
            products.extend(self._parse_lines_from_text(full_text))

        return products

    def _parse_table(self, table: List[List[str]]) -> List[Product]:
        rows = [[(cell or "").strip() for cell in row] for row in table if row]
        if not rows:
            return []

        header = [cell.lower() for cell in rows[0]]
        has_header = self._looks_like_header(header)
        col_map = self._detect_columns(header if has_header else [])
        data_rows = rows[1:] if has_header else rows

        products: List[Product] = []
        for row in data_rows:
            product = self._parse_product_row(row, col_map)
            if product:
                products.append(product)
        return products

    def _looks_like_header(self, header: List[str]) -> bool:
        keywords = {"descripcion", "producto", "detalle", "cant", "vr", "unit", "total"}
        return any(any(word in cell for word in keywords) for cell in header)

    def _detect_columns(self, header: List[str]) -> dict:
        col_map = {}
        for idx, col in enumerate(header):
            if not col:
                continue
            normalized = col.replace(" ", "")
            low = col.lower()
            if "descr" in low or "producto" in low or "detalle" in low:
                col_map["name"] = idx
            if "cant" in low:
                col_map["quantity"] = idx
            if "unit" in low or "vrunit" in normalized or "v.unit" in normalized:
                col_map["unit_price"] = idx
            if "total" in low:
                col_map["total"] = idx
            if "iva" in low:
                col_map["iva"] = idx
        return col_map

    def _parse_product_row(self, row: List[str], col_map: dict) -> Optional[Product]:
        cells = [(cell or "").strip() for cell in row]

        name_idx = col_map.get("name")
        qty_idx = col_map.get("quantity")
        unit_idx = col_map.get("unit_price")
        total_idx = col_map.get("total")
        iva_idx = col_map.get("iva")

        name = cells[name_idx] if name_idx is not None and name_idx < len(cells) else ""
        if not name:
            non_numeric = [c for c in cells if not self._is_numeric_like(c)]
            name = max(non_numeric, key=len) if non_numeric else ""

        quantity = self._to_decimal(cells[qty_idx]) if qty_idx is not None and qty_idx < len(cells) else Decimal("0")
        unit_price = self._to_decimal(cells[unit_idx]) if unit_idx is not None and unit_idx < len(cells) else Decimal("0")
        total_price = self._to_decimal(cells[total_idx]) if total_idx is not None and total_idx < len(cells) else Decimal("0")
        iva = self._to_decimal(cells[iva_idx]) if iva_idx is not None and iva_idx < len(cells) else Decimal("0")

        if total_price == 0 and unit_price and quantity:
            total_price = unit_price * quantity
        if unit_price == 0 and total_price and quantity:
            unit_price = total_price / quantity

        if not name or (quantity == 0 and total_price == 0):
            return None

        return Product(
            name=name,
            underlying_code="",
            unit_of_measure="Un",
            quantity=quantity if quantity != 0 else Decimal("1"),
            unit_price=unit_price,
            total_price=total_price if total_price != 0 else unit_price * (quantity or Decimal("1")),
            iva_percentage=iva,
            original_unit_code="Un",  # Paisano PDFs typically use "Un" (units)
        )

    def _parse_lines_from_text(self, text: str) -> List[Product]:
        """
        Fallback parser for PDFs where tables are not detected.
        It looks for lines ending with qty/unit/total patterns.
        """
        products: List[Product] = []
        pattern = re.compile(
            r"(.+?)\s+(\d[\d\.,]*)\s+(\d[\d\.,]*)\s+(\d[\d\.,]*)$"
        )

        for raw_line in text.splitlines():
            line = raw_line.strip()
            match = pattern.match(line)
            if not match:
                continue

            name = match.group(1).strip()
            quantity = self._to_decimal(match.group(2))
            unit_price = self._to_decimal(match.group(3))
            total_price = self._to_decimal(match.group(4))

            if not name or quantity == 0:
                continue

            products.append(
                Product(
                    name=name,
                    underlying_code="",
                    unit_of_measure="Un",
                    quantity=quantity,
                    unit_price=unit_price if unit_price != 0 else (total_price / quantity if quantity else Decimal("0")),
                    total_price=total_price if total_price != 0 else unit_price * quantity,
                    iva_percentage=Decimal("0"),
                    original_unit_code="Un",  # Paisano PDFs typically use "Un" (units)
                )
            )

        return products

    # --- Utilities ---
    def _to_decimal(self, value) -> Decimal:
        """Convert strings like '1.234,56' or '1,234.56' to Decimal"""
        if value is None:
            return Decimal("0")
        text = str(value).strip()
        if not text:
            return Decimal("0")
        text = text.replace("\n", " ")
        text = re.sub(r"[^\d,\.\-]", "", text)
        # Try typical formats
        try:
            if "," in text and text.count(",") == 1 and text.rfind(",") > text.rfind("."):
                normalized = text.replace(".", "").replace(",", ".")
            else:
                normalized = text.replace(",", "")
            return Decimal(normalized)
        except Exception:
            try:
                return Decimal(text.replace(",", "."))
            except Exception:
                return Decimal("0")

    def _is_numeric_like(self, value: str) -> bool:
        return bool(re.fullmatch(r"[0-9\.,]+", value.strip())) if value else False
