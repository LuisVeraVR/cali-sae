"""

XML Invoice Parser - Parses UBL 2.0 DIAN Colombia invoices

"""

import xml.etree.ElementTree as ET

import zipfile
import re
from pathlib import Path
from typing import List, Optional
from decimal import Decimal

from datetime import datetime


from ...domain.entities.invoice import Invoice

from ...domain.entities.product import Product

from .paisano_product_catalog import PaisanoProductCatalog


class XMLInvoiceParser:
    """Parser for UBL 2.0 DIAN Colombia electronic invoices"""

    def __init__(self):

        # UBL 2.0 DIAN namespaces

        self.namespaces = {
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            "sts": "dian:gov:co:facturaelectronica:Structures-2-1",
        }

        # Catálogo de productos de El Paisano
        self.product_catalog = PaisanoProductCatalog()

    def parse_zip_file(self, zip_path: str) -> List[Invoice]:
        """
        Parse all XML invoices from a ZIP file

        Args:
            zip_path: Path to ZIP file


        Returns:

            List of parsed invoices

        """

        invoices = []

        try:

            with zipfile.ZipFile(zip_path, "r") as zip_ref:

                # Find all XML files in ZIP

                xml_files = [
                    f for f in zip_ref.namelist() if f.lower().endswith(".xml")
                ]

                for xml_file in xml_files:

                    try:

                        xml_content = zip_ref.read(xml_file)

                        invoice = self.parse_xml_content(
                            xml_content, xml_file, Path(zip_path).name
                        )

                        if invoice:

                            invoices.append(invoice)

                    except Exception as e:

                        print(f"Error parsing XML {xml_file}: {str(e)}")

                        continue

        except Exception as e:

            print(f"Error reading ZIP file {zip_path}: {str(e)}")

        return invoices

    def parse_xml_file(self, xml_path: str) -> Optional[Invoice]:
        """Parse a single XML file on disk"""
        try:
            content = Path(xml_path).read_bytes()
            return self.parse_xml_content(
                content, Path(xml_path).name, Path(xml_path).parent.name
            )
        except Exception as exc:
            print(f"Error parsing XML file {xml_path}: {exc}")
            return None

    def parse_directory(self, directory: str) -> List[Invoice]:
        """Parse all XML files in a directory (recursive)"""
        invoices: List[Invoice] = []
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            return invoices

        xml_files = list(dir_path.rglob("*.xml"))
        for xml_file in xml_files:
            invoice = self.parse_xml_file(str(xml_file))
            if invoice:
                invoices.append(invoice)
        return invoices

    def parse_xml_content(
        self, xml_content: bytes, xml_filename: str = "", zip_filename: str = ""
    ) -> Invoice:
        """

        Parse XML content to Invoice entity



        Args:

            xml_content: XML content as bytes

            xml_filename: Name of the XML file

            zip_filename: Name of the ZIP file



        Returns:

            Invoice entity or None if parsing fails

        """

        try:

            root = ET.fromstring(xml_content)

            # Extract invoice data

            invoice_number = self._get_text(root, ".//cbc:ID", "")

            issue_date_str = self._get_text(root, ".//cbc:IssueDate", "")

            due_date_str = self._get_text(root, ".//cbc:DueDate", "")

            currency = self._get_text(root, ".//cbc:DocumentCurrencyCode", "COP")

            # Parse dates

            issue_date = self._parse_date(issue_date_str)

            due_date = self._parse_date(due_date_str) if due_date_str else None

            # Extract supplier (seller) data

            supplier = root.find(
                ".//cac:AccountingSupplierParty/cac:Party", self.namespaces
            )

            seller_nit = ""

            seller_name = ""

            seller_municipality = ""

            if supplier is not None:

                seller_nit = self._get_text(supplier, ".//cbc:CompanyID", "")

                seller_name = self._get_text(supplier, ".//cbc:RegistrationName", "")

                seller_municipality = self._get_text(supplier, ".//cbc:CityName", "")

            # Extract customer (buyer) data

            customer = root.find(
                ".//cac:AccountingCustomerParty/cac:Party", self.namespaces
            )

            buyer_nit = ""

            buyer_name = ""

            if customer is not None:
                # Try multiple locations for buyer NIT
                # 1. Try PartyTaxScheme/CompanyID (most common in Colombia)
                buyer_nit = self._get_text(customer, ".//cac:PartyTaxScheme/cbc:CompanyID", "")

                # 2. If not found, try PartyIdentification/ID
                if not buyer_nit:
                    buyer_nit = self._get_text(customer, ".//cac:PartyIdentification/cbc:ID", "")

                # 3. If not found, try direct CompanyID (fallback)
                if not buyer_nit:
                    buyer_nit = self._get_text(customer, ".//cbc:CompanyID", "")

                buyer_name = self._get_text(customer, ".//cbc:RegistrationName", "")

            # Create invoice entity

            invoice = Invoice(
                invoice_number=invoice_number,
                issue_date=issue_date,
                due_date=due_date,
                currency=currency,
                seller_nit=seller_nit,
                seller_name=seller_name,
                seller_municipality=seller_municipality,
                buyer_nit=buyer_nit,
                buyer_name=buyer_name,
                xml_filename=xml_filename,
                zip_filename=zip_filename,
                processed_at=datetime.now(),
            )

            # Extract product lines

            lines = root.findall(".//cac:InvoiceLine", self.namespaces)

            for line in lines:

                product = self._parse_product_line(line)

                if product:

                    invoice.add_product(product)

            return invoice

        except Exception as e:

            print(f"Error parsing XML content: {str(e)}")

            return None

    def _extract_kilos_from_name(self, product_name: str) -> Optional[Decimal]:
        """
        Extrae los kilos del nombre del producto.

        Formato esperado: "NOMBRE*PRESENTACION=X,X KILOS EMPAQUE"
        Ejemplo: "FRIJOL CALIMA*500G=12,5 KILOS PACA" -> 12.5

        Args:
            product_name: Nombre del producto

        Returns:
            Decimal con los kilos o None si no se encuentra el patrón
        """
        try:
            # Buscar patrón: =NUMERO KILOS o =NUMERO KILO
            pattern = r'=\s*(\d+(?:[,\.]\d+)?)\s+KILOS?\b'
            match = re.search(pattern, product_name, re.IGNORECASE)

            if match:
                kilos_str = match.group(1).replace(',', '.')
                return Decimal(kilos_str)
        except Exception as e:
            print(f"Error extrayendo kilos del nombre '{product_name}': {str(e)}")

        return None

    def _parse_product_line(self, line_element) -> Product:
        """
        Parse a product line from InvoiceLine element

        Args:
            line_element: XML element for InvoiceLine

        Returns:
            Product entity
        """
        try:
            # Product name
            name = self._get_text(line_element, ".//cbc:Description", "")

            # Underlying code (schemeID="999")
            underlying_code = self._get_text(
                line_element, './/cbc:ID[@schemeID="999"]', ""
            )

            # Unit of measure
            unit_element = line_element.find(".//cbc:InvoicedQuantity", self.namespaces)
            unit_code = (
                unit_element.get("unitCode", "") if unit_element is not None else ""
            )
            # Guardar el código original para la columna "Unidad Original"
            original_unit_code = unit_code
            unit_of_measure = self._convert_unit_code(unit_code)

            # Quantity original (tal como viene en el XML)
            quantity_str = self._get_text(line_element, ".//cbc:InvoicedQuantity", "0")
            original_quantity = Decimal(quantity_str.replace(",", "."))

            # Buscar kilos en el catálogo de productos
            kilos_per_unit = self.product_catalog.get_kilos_for_product(name)

            # Si no se encuentra en el catálogo, intentar extraer del nombre del producto
            if kilos_per_unit is None:
                kilos_per_unit = self._extract_kilos_from_name(name)

            # Calcular cantidad convertida
            if kilos_per_unit:
                # Si hay kilos (del catálogo o del nombre), multiplicar cantidad original por los kilos
                quantity = original_quantity * kilos_per_unit
            else:
                # Si no hay kilos, usar la cantidad original
                quantity = original_quantity

            # Unit price
            unit_price_str = self._get_text(
                line_element, ".//cac:Price/cbc:PriceAmount", "0"
            )
            unit_price = Decimal(unit_price_str.replace(",", "."))

            # Total price (try TaxableAmount first, then LineExtensionAmount)
            total_price_str = self._get_text(
                line_element, ".//cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount", ""
            )
            if not total_price_str or total_price_str == "0":
                total_price_str = self._get_text(
                    line_element, ".//cbc:LineExtensionAmount", "0"
                )

            total_price = Decimal(total_price_str.replace(",", "."))

            # IVA percentage
            iva_str = self._get_text(
                line_element,
                ".//cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent",
                "0",
            )
            iva_percentage = (
                Decimal(iva_str.replace(",", ".")) if iva_str else Decimal("0")
            )

            if iva_percentage == 0:
                # Try compute from taxable vs tax amount
                iva_percentage = self._compute_iva_from_amounts(line_element)

            if iva_percentage == 0:
                # Try read custom tag like <Impto>19</Impto>
                iva_percentage = self._find_impto_value(line_element)

            return Product(
                name=name,
                underlying_code=underlying_code,
                unit_of_measure=unit_of_measure,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                iva_percentage=iva_percentage,
                original_quantity=original_quantity,
                original_unit_code=original_unit_code,
            )

        except Exception as e:

            print(f"Error parsing product line: {str(e)}")

            return None

    def _get_text(self, element, xpath: str, default: str = "") -> str:
        """

        Get text from XML element using xpath



        Args:

            element: XML element

            xpath: XPath expression

            default: Default value if not found



        Returns:

            Text content or default

        """

        try:

            found = element.find(xpath, self.namespaces)

            if found is not None and found.text is not None:

                return found.text

            # Try without namespaces as fallback

            simple_xpath = (
                xpath.replace("cbc:", "")
                .replace("cac:", "")
                .replace("ext:", "")
                .replace("sts:", "")
            )

            found = element.find(simple_xpath)

            if found is not None and found.text is not None:

                return found.text

            return default

        except Exception:

            return default

    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse date string to datetime

        Args:
            date_str: Date string in YYYY-MM-DD format


        Returns:

            datetime object or current datetime if parsing fails

        """

        try:

            return datetime.strptime(date_str, "%Y-%m-%d")

        except Exception:

            return datetime.now()

    def _convert_unit_code(self, code: str) -> str:
        """
        Convert UBL unit code to human-readable unit

        Args:
            code: UBL unit code (e.g., KGM, LTR)

        Returns:
            Human-readable unit (e.g., Kg, Lt)
        """
        mapping = {
            "KGM": "Kg",
            "LTR": "Lt",
            "LT": "Lt",
            "NIU": "Un",
            "MTR": "Mt",
            "HUR": "Hr",
            "GRM": "Gr",
            "TNE": "Tn",
            "MLT": "Ml",
            "CMT": "Cm",
            "M2": "M2",
            "M3": "M3",
            "DAY": "Día",
            "MON": "Mes",
            "ANN": "Año",
            "PCE": "Pz",
            "SET": "Set",
            "PAR": "Par",
            "DZN": "Docena",
            "BOX": "Caja",
            "BAG": "Bolsa",
            "BTL": "Botella",
            "CAN": "Lata",
        }
        return mapping.get((code or "").upper(), code if code else "Un")

    def _compute_iva_from_amounts(self, line_element) -> Decimal:
        """Fallback: compute IVA% from TaxAmount/TaxableAmount"""
        tax_amount_str = self._get_text(
            line_element, ".//cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount", ""
        )
        taxable_str = self._get_text(
            line_element, ".//cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount", ""
        )
        try:
            tax_amount = (
                Decimal(tax_amount_str.replace(",", "."))
                if tax_amount_str
                else Decimal("0")
            )
            taxable = (
                Decimal(taxable_str.replace(",", ".")) if taxable_str else Decimal("0")
            )
            if taxable and tax_amount:
                return (tax_amount / taxable) * Decimal("100")
        except Exception:
            return Decimal("0")
        return Decimal("0")

    def _find_impto_value(self, element) -> Decimal:
        """Search any tag containing 'IMPT' text to extract IVA percentage"""
        try:
            for node in element.iter():
                tag = node.tag.lower() if hasattr(node, "tag") and node.tag else ""
                if "impt" in tag or "impto" in tag:
                    if node.text:
                        try:
                            return Decimal(str(node.text).replace(",", "."))
                        except Exception:
                            continue
        except Exception:
            pass
        return Decimal("0")
