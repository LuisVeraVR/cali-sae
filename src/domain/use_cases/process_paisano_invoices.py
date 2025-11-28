"""
Process El Paisano Invoices Use Case
Parses XML invoices from folders and exports to Reggis CSV
"""
from typing import List, Callable, Optional
from decimal import Decimal
from datetime import datetime
from pathlib import Path
import unicodedata
from ..entities.invoice import Invoice
from ..entities.report import Report
from ..repositories.report_repository import ReportRepositoryInterface


class ProcessPaisanoInvoices:
    """Use case for processing El Paisano invoices from XML folders"""

    # Conversion map: normalized product name -> factor to kilos
    CONVERSION_MAP = {
        "ACEITE SOYA*500CC LA ORLANDESA E": Decimal("24"),
        "ARVEJA VERDE*500G": Decimal("25"),
        "ARVEJA VERDE*250G": Decimal("25"),
        "ARROZ*500G": Decimal("25"),
        "AVENA HOJUELA*250G": Decimal("24"),
        "ATUN ROBIN/H LOMO/AGUA*175G": Decimal("48"),
        "ATUN SABOR/P*175G LOMO/ACEITE": Decimal("48"),
        "ATUN SABOR/P*175G LOMO/AGUA": Decimal("48"),
        "AVENA HOJUELA*200G": Decimal("48"),
        "AVENA HOJUELA*500G": Decimal("24"),
        "BLANQUILLO*250G FRIJOL": Decimal("25"),
        "FRIJOL CALIMA*500G": Decimal("25"),
        "FRIJOL CALIMA*250G": Decimal("25"),
        "FRIJOL PALICERO*500G": Decimal("25"),
        "GARBANZO*500G": Decimal("25"),
        "BLANQUILLO*500G FRIJOL": Decimal("25"),
        "FRIJOL CARG/TO*500G": Decimal("25"),
        "FRIJOL BOLON*500G": Decimal("25"),
        "HARINA AREPA*500G BLANCA": Decimal("24"),
        "HARINA AREPA*500G AMARILLA": Decimal("24"),
        "HARINA TRIGO UND*500G LA VECINA": Decimal("25"),
        "ACEITE SOYA*250CC LA ORLANDESA": Decimal("24"),
        "ACEITE SOYA*500CC SU ACEITE": Decimal("24"),
        "ACEITE SOYA*900CC LA ORLANDESA E": Decimal("12"),
        "ACEITE SOYA*1000CC LA ORLANDESA E": Decimal("12"),
        "HARINA DE TRIGO FARALLONES*500GR": Decimal("25"),
        "PANELA*500GR": Decimal("48"),
        "PANELA REDONDA/2UND*500GR 1000GR": Decimal("24"),
        "LENTEJA*500G": Decimal("25"),
        "LENTEJA*250G": Decimal("25"),
        "MAIZ PIRA*500G": Decimal("25"),
        "MAZAMORRA*500G BLANCA": Decimal("25"),
        "PASTA SANTALI*250G MACARRONCITO": Decimal("24"),
        "ARROZ AGRANEL": Decimal("50"),
        "FRIJOL CARAOTA AGRANEL": Decimal("50"),
        "PASTA SANTALI*250G C/ANGEL": Decimal("24"),
        "PASTA COMARRICO*500 C/ANGEL": Decimal("12"),
        "PASTA COMARRICO*500G SPAGUETTI": Decimal("12"),
        "PASTA ZONIA*250G CONCHITA": Decimal("24"),
        "PASTA ZONIA*250G MACARRON": Decimal("24"),
        "PASTA SANTALI*250G CONCHITA": Decimal("24"),
        "PASTA ZONIA*200G ESPAGUETTI": Decimal("24"),
        "PASTA ZONIA*250G C/ANGEL": Decimal("24"),
        "PASTA SANTALI*250G SPAGUETTI": Decimal("24"),
        "PASTA ZONIA*250G CORBATA": Decimal("24"),
        "PASTA ZONIA*250G SPAGUETTI": Decimal("24"),
        "ARVEJA VERDE AGRANEL": Decimal("50"),
        "FRIJOL CALIMA AGRANEL": Decimal("50"),
        "LENTEJA A GRANEL": Decimal("50"),
        "FRIJOL CARG/TO AGRANEL": Decimal("50"),
        "CUCHUCO*450G GRUESO VALLE": Decimal("25"),
        "PASTA ZONIA*200G C/ANGEL": Decimal("24"),
        "PANELA REDONDA*24KILOS": Decimal("24"),
        "PANELA REDONDA*500GR": Decimal("48"),
        "FRIJOL CARAOTA*500G": Decimal("25"),
        "AZUCAR BLANCA*500G": Decimal("25"),
        "AZUCAR BLANCA*50KG": Decimal("50"),
        "ACEITE SOYA*3000CC LA ORLANDESA": Decimal("51"),
        "LECHE EN POLVO*380GR ENTERA NUTRALAC": Decimal("30"),
        "ARROZ BONGUERO*500G": Decimal("25"),
        "ARROZ SONORA*500GR": Decimal("25"),
        "PANELA TEJO/8UND*125GR": Decimal("8"),
        "HARINA TRIGO*500G LA MONJITA": Decimal("24"),
        "LECHE EN POLVO*900GR ENTERA NUTRALAC": Decimal("13"),
        "BLANQUILLO AGRANEL FRIJOL": Decimal("50"),
        "GARBANZO AGRANEL": Decimal("50"),
        "ACEITE SOYA*5000CC LA ORLANDESA E": Decimal("4"),
        "ARROZ SONORA*250GR": Decimal("50"),
        "GALLETAS CRAKENAS CLUB IND 8*10": Decimal("1"),
        "LECHE EN POLVO*380GR ENTERA DONA VACA": Decimal("30"),
        "LECHE EN POLVO*900GR ENTERA DONA VACA": Decimal("13"),
        "ATUN D/SANCHO*175G LOMO/AGUA": Decimal("48"),
        "ACEITE SAN MIGUEL DE SOYA*500CC": Decimal("24"),
        "ACEITE SAN MIGUEL DE SOYA*3000CC": Decimal("51"),
        "ACEITE SAN MIGUEL DE SOYA*5000CC": Decimal("4"),
        "ACEITE SAN MIGUEL DE SOYA*1000CC": Decimal("12"),
        "PANELA*500GR CUADRADA": Decimal("48"),
        "AZUCAR*500GR CARMELITA": Decimal("25"),
        "FRIJOL CALIMA A GRANEL": Decimal("50"),
        "ARROZ SONORA*500G": Decimal("25"),
        "AZUCAR*500G CARMELITA": Decimal("25"),
        "AZUCAR CARMELITA*500GR**": Decimal("25"),
        "PASTA C/ANGEL*250G ZONIA**": Decimal("24"),
        "PASTA SPAGUETTI*250G ZONIA**": Decimal("24"),
        "HARINA DE TRIGO*500G LA MONJITA**": Decimal("24"),
        "LECHE EN POLVO*900G ENTERA DONA VACA": Decimal("13"),
        "PASTA CONCHA*250G ZONIA**": Decimal("24"),
        "HARINA DE TRIGO*500G LA VECINA**": Decimal("25"),
        "BLANQUILLO A GRANEL FRIJOL": Decimal("50"),
        "HARINA DE TRIGO*500G LA VECINA": Decimal("25"),
        "FRIJOL CARG/TO*250G": Decimal("25"),
        "ARVEJA VERDE A GRANEL": Decimal("50"),
        "ACEITE SAN MIGUEL DE SOYA*250CC": Decimal("48"),
        "HOJUELAS DE MAIZ*220G SUNSHINE": Decimal("12"),
        "FRIJOL CARG/TO A GRANEL": Decimal("50"),
        "PASTA ZONIA*250G ESPAGUETI": Decimal("24"),
    }

    def __init__(
        self,
        report_repository: ReportRepositoryInterface,
        xml_parser,  # XMLInvoiceParser
        reggis_exporter,  # JCRReggisExporter (Reggis CSV exporter)
        conversion_repository=None  # PaisanoConversionRepository
    ):
        self.report_repository = report_repository
        self.xml_parser = xml_parser
        self.reggis_exporter = reggis_exporter
        self.conversion_repository = conversion_repository
        self._reload_catalog()

    def execute(
        self,
        xml_paths: List[str],
        username: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> tuple[bool, str, int]:
        """
        Process XML invoices (folders or individual XML files) and export to Reggis CSV

        Args:
            xml_paths: List of folder paths or XML file paths
            username: Username of the person processing
            progress_callback: Optional callback for progress updates (current, total)

        Returns:
            Tuple of (success, message, records_processed)
        """
        if not xml_paths:
            return False, "No se seleccionaron archivos o carpetas XML", 0

        all_invoices: List[Invoice] = []
        total_items = len(xml_paths)

        # Reload catalog each run to pick up new conversions
        self._reload_catalog()

        for idx, path in enumerate(xml_paths):
            if progress_callback:
                progress_callback(idx, total_items)

            try:
                p = Path(path)
                if p.is_dir():
                    invoices = self.xml_parser.parse_directory(str(p))
                elif p.is_file() and p.suffix.lower() == ".xml":
                    invoice = self.xml_parser.parse_xml_file(str(p))
                    invoices = [invoice] if invoice else []
                else:
                    invoices = []

                all_invoices.extend(invoices)
            except Exception as exc:
                print(f"Error processing {path}: {exc}")
                continue

        if not all_invoices:
            return False, "No se encontraron facturas válidas en los archivos", 0

        try:
            # Apply conversion factors to kilos and recompute unit price
            original_quantities = {}
            missing_products = 0

            for invoice in all_invoices:
                for product in invoice.products:
                    original_qty = product.quantity
                    product.original_quantity = original_qty

                    # Calculate conversion factor based on product name
                    factor = self._calculate_conversion_factor(product.name)
                    if factor == Decimal("1"):
                        missing_products += 1

                    # Force underlying code
                    product.underlying_code = "SPN-1"

                    # Convert quantity to kg using the calculated factor
                    converted_qty = original_qty * factor
                    product.quantity = converted_qty
                    product.unit_of_measure = "Kg" if factor != Decimal("1") else "Un"

                    # Recalculate unit price based on converted quantity
                    if converted_qty > 0:
                        product.unit_price = product.total_price / converted_qty

                    original_quantities[(invoice.invoice_number, product.name)] = original_qty

            # Default to using invoice data for municipio/IVA; keep exporter defaults
            self.reggis_exporter.municipality = ""
            self.reggis_exporter.iva_percentage = "0"

            output_file = self.reggis_exporter.export_to_reggis_csv(
                all_invoices,
                original_quantities=original_quantities,
                company="EL PAISANO"
            )
            message = f"Datos exportados exitosamente al formato Reggis:\n{output_file}"
            if missing_products:
                message += f"\nAdvertencia: {missing_products} productos sin factor de conversión (usado 1:1)."
        except Exception as exc:
            return False, f"Error al exportar datos: {exc}", 0

        total_records = sum(invoice.get_product_count() for invoice in all_invoices)
        total_size = sum(
            Path(p).stat().st_size
            for p in xml_paths
            if Path(p).exists()
        )

        report = Report(
            id=None,
            username=username,
            company="EL PAISANO",
            filename=", ".join([Path(f).name for f in xml_paths]),
            records_processed=total_records,
            created_at=datetime.now(),
            file_size=total_size
        )
        self.report_repository.create(report)

        if progress_callback:
            progress_callback(total_items, total_items)

        return True, message, total_records

    # --- Helpers ---
    def _extract_grams_from_name(self, product_name: str) -> int:
        """
        Extract grams from product name
        Examples: 'HARINA*500G' -> 500, 'FRIJOL*250G' -> 250, 'PANELA*500GR' -> 500
        Returns 0 if no grams found
        """
        import re
        if not product_name:
            return 0

        name_upper = product_name.upper()

        # Look for KG/KILO/KILOS patterns first (1KG, 2KG, 24KILOS, etc.)
        match_kg = re.search(r'(\d+)\s*(?:KG|KILO|KILOS)\b', name_upper)
        if match_kg:
            return int(match_kg.group(1)) * 1000

        # Look for G/GR/GRAMOS patterns (500G, 250GR, etc.)
        match = re.search(r'(\d+)\s*(?:G|GR|GRAMOS)\b', name_upper)
        if match:
            return int(match.group(1))

        return 0

    def _extract_volume_cc_from_name(self, product_name: str) -> int:
        """
        Extract volume in CC from product name
        Examples: 'ACEITE*500CC' -> 500, 'ACEITE*3000CC' -> 3000
        Returns 0 if no volume found
        """
        import re
        if not product_name:
            return 0

        name_upper = product_name.upper()
        # Look for patterns like 500CC, 1000CC, etc.
        match = re.search(r'(\d+)\s*CC\b', name_upper)
        if match:
            return int(match.group(1))

        return 0

    def _reload_catalog(self):
        """Load hardcoded + DB conversions and precompute tokens"""
        self._normalized_catalog = []
        catalog = dict(self.CONVERSION_MAP)
        if self.conversion_repository:
            try:
                db_map = self.conversion_repository.get_all()
                catalog.update({k: Decimal(str(v)) for k, v in db_map.items()})
            except Exception as exc:
                print(f"Error loading Paisano conversions from DB: {exc}")
        for name, factor in catalog.items():
            tokens = self._normalize_tokens(name)
            self._normalized_catalog.append((name, factor, tokens))

    def _normalize_tokens(self, name: str) -> List[str]:
        """Normalize product name into a list of tokens for fuzzy matching"""
        if not name:
            return []
        # Remove accents, uppercase, strip non-alnum
        nfkd = unicodedata.normalize("NFKD", name)
        cleaned = "".join(c for c in nfkd if not unicodedata.combining(c))
        cleaned = cleaned.upper()
        for ch in "*-/_,.;":
            cleaned = cleaned.replace(ch, " ")
        tokens = cleaned.split()
        # Remove common stopwords
        stop = {"DE", "LA", "EL", "LOS", "LAS", "A", "AL", "DEL"}
        return [t for t in tokens if t and t not in stop]

    def _calculate_conversion_factor(self, product_name: str) -> Decimal:
        """
        Calculate conversion factor based on product name.

        Priority:
        1. FIRST: Check catalog for exact product match
        2. If not in catalog: Extract grams from name (500G, 250G, etc.)
        3. If not in catalog: Extract volume in CC (500CC, 1000CC, etc.)
        4. Otherwise: return 1 (no conversion)

        Returns:
            Decimal: conversion factor to convert units to kg
        """
        if not product_name:
            return Decimal("1")

        # PRIORITY 1: Check catalog first
        normalized_tokens = self._normalize_tokens(product_name)
        catalog_factor = self._match_factor(normalized_tokens)

        # If found in catalog, use that factor
        if catalog_factor != Decimal("1"):
            return catalog_factor

        # PRIORITY 2: Not in catalog, try to extract grams from name
        grams = self._extract_grams_from_name(product_name)
        if grams > 0:
            # Convert grams to kg: 500G -> 0.5 kg per unit
            return Decimal(str(grams)) / Decimal("1000")

        # PRIORITY 3: Try to extract volume in CC for liquids
        volume_cc = self._extract_volume_cc_from_name(product_name)
        if volume_cc > 0:
            # For oil: density ≈ 0.92 g/ml, so 500CC ≈ 460g ≈ 0.46 kg
            # For simplicity, we use 0.92 as default density for oils
            density = Decimal("0.92")
            kg_per_unit = (Decimal(str(volume_cc)) / Decimal("1000")) * density
            return kg_per_unit

        # No conversion info found, return 1 (keep as units)
        return Decimal("1")

    def _match_factor(self, tokens: List[str]) -> Decimal:
        """Find best factor by token overlap; fallback 1"""
        if not tokens:
            return Decimal("1")
        best_score = 0.0
        best_factor = Decimal("1")
        token_set = set(tokens)
        for _, factor, cat_tokens in self._normalized_catalog:
            common = token_set.intersection(cat_tokens)
            if not common:
                continue
            score = len(common) / max(len(cat_tokens), 1)
            if score > best_score:
                best_score = score
                best_factor = factor
        # Require minimum overlap; otherwise 1
        return best_factor if best_score >= 0.5 else Decimal("1")
