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
    # Incluye productos A GRANEL y productos con conversiones específicas del catálogo
    CONVERSION_MAP = {
        # Productos A GRANEL (bultos/sacos de 50 kg)
        "ARROZ AGRANEL": Decimal("50"),
        "ARROZ A GRANEL": Decimal("50"),
        "ARVEJA VERDE AGRANEL": Decimal("50"),
        "ARVEJA VERDE A GRANEL": Decimal("50"),
        "BLANQUILLO AGRANEL FRIJOL": Decimal("50"),
        "BLANQUILLO A GRANEL FRIJOL": Decimal("50"),
        "FRIJOL CALIMA AGRANEL": Decimal("50"),
        "FRIJOL CALIMA A GRANEL": Decimal("50"),
        "FRIJOL CARAOTA AGRANEL": Decimal("50"),
        "FRIJOL CARG/TO AGRANEL": Decimal("50"),
        "FRIJOL CARG/TO A GRANEL": Decimal("50"),
        "GARBANZO AGRANEL": Decimal("50"),
        "LENTEJA A GRANEL": Decimal("50"),
        "CEBADA PERLADA A GRANEL CON IVA": Decimal("50"),

        # ACEITES (usando densidad 1.0 kg/litro para simplificar)
        # ACEITE*500ML: 24 unidades = 12 kg → 0.5 kg/unidad
        "ACEITE*500ML REF FRISOYA": Decimal("0.5"),
        "ACEITE SOYA*500CC LA ORLANDESA E": Decimal("0.5"),
        "ACEITE SOYA*500CC SU ACEITE": Decimal("0.5"),
        "ACEITE SAN MIGUEL DE SOYA*500CC": Decimal("0.5"),
        "ACEITE SOYA*250CC LA ORLANDESA": Decimal("0.25"),
        "ACEITE SAN MIGUEL DE SOYA*250CC": Decimal("0.25"),

        # ACEITE*1000ML: 12 unidades = 12 kg → 1 kg/unidad
        "ACEITE*1000ML REF FRISOYA": Decimal("1"),
        "ACEITE SOYA*1000CC LA ORLANDESA E": Decimal("1"),
        "ACEITE SAN MIGUEL DE SOYA*1000CC": Decimal("1"),

        # ACEITE*2000ML: 6 unidades = 12 kg → 2 kg/unidad
        "ACEITE*2000ML REF FRISOYA": Decimal("2"),

        # ACEITE*3000ML: 1 caja = 18 kg (6 unidades) → 3 kg/unidad
        "ACEITE*3000ML REF FRISOYA": Decimal("3"),
        "ACEITE SOYA*3000CC LA ORLANDESA": Decimal("3"),
        "ACEITE SAN MIGUEL DE SOYA*3000CC": Decimal("3"),

        # ACEITE*5000ML: 2 unidades = 6 kg → 3 kg/unidad
        "ACEITE*5000ML REF FRISOYA": Decimal("3"),
        "ACEITE SOYA*5000CC LA ORLANDESA E": Decimal("5"),
        "ACEITE SAN MIGUEL DE SOYA*5000CC": Decimal("5"),

        # SEMILLAS
        # SEMILLA GIRASOL x GRANEL: bulto = 20 kg
        "SEMILLA GIRASOL x GRANEL": Decimal("20"),
        "SEMILLA GIRASOL AGRANEL": Decimal("20"),
        # SEMILLA GIRASOL*200G: 12 unidades = 2.4 kg → 0.2 kg/unidad
        "SEMILLA GIRASOL*200G": Decimal("0.2"),

        # HOJUELAS AZUCARADAS
        # HOJUELAS AZUCARADAS*40G: 80 unidades = 3.2 kg → 0.04 kg/unidad
        "HOJUELAS AZUCARADAS*40G": Decimal("0.04"),

        # LECHE EN POLVO
        # LECHE*380G: 12 unidades = 4.56 kg → 0.38 kg/unidad
        "LECHE EN POLVO*380G ENTERA DONA VACA": Decimal("0.38"),
        "LECHE EN POLVO*380GR ENTERA NUTRALAC": Decimal("0.38"),
        "LECHE EN POLVO*380GR ENTERA DONA VACA": Decimal("0.38"),
        # LECHE*900G: usar extracción automática (0.9 kg)
        "LECHE EN POLVO*900GR ENTERA NUTRALAC": Decimal("0.9"),
        "LECHE EN POLVO*900GR ENTERA DONA VACA": Decimal("0.9"),
        "LECHE EN POLVO*900G ENTERA DONA VACA": Decimal("0.9"),

        # AZUCAR
        # AZUCAR BLANCO*1KG: paca = 25 kg (25 unidades × 1 kg)
        "AZUCAR BLANCO*1KG PROVIDENCIA": Decimal("1"),

        # PANELA
        # PANELA*125G*8UND TEJO: usar extracción automática (0.125 kg × 8 = 1 kg por paquete)
        "PANELA*125G*8UND TEJO": Decimal("1"),
        "PANELA TEJO/8UND*125GR": Decimal("1"),

        # Productos especiales sin gramos/volumen (mantener como unidades)
        "GALLETAS CRAKENAS CLUB IND 8*10": Decimal("1"),
        "TOALLA COCINA BCO NUBE": Decimal("1"),
        "SERVILLETA BCA NUBE*300UND": Decimal("1"),
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

        # If found in catalog, use that factor (even if it's 1)
        if catalog_factor is not None:
            return catalog_factor

        # PRIORITY 2: Not in catalog, try to extract grams from name
        grams = self._extract_grams_from_name(product_name)
        if grams > 0:
            # Convert grams to kg: 500G -> 0.5 kg per unit
            return Decimal(str(grams)) / Decimal("1000")

        # PRIORITY 3: Try to extract volume in CC for liquids
        volume_cc = self._extract_volume_cc_from_name(product_name)
        if volume_cc > 0:
            # For oil: using density = 1.0 kg/litro for simplification
            # 500CC = 0.5 litros = 0.5 kg, 1000CC = 1 litro = 1 kg
            density = Decimal("1.0")
            kg_per_unit = (Decimal(str(volume_cc)) / Decimal("1000")) * density
            return kg_per_unit

        # No conversion info found, return 1 (keep as units)
        return Decimal("1")

    def _match_factor(self, tokens: List[str]):
        """
        Find best factor by token overlap.

        Returns:
            Decimal if found in catalog with score >= 0.95, None otherwise
        """
        if not tokens:
            return None
        best_score = 0.0
        best_factor = None
        token_set = set(tokens)
        for _, factor, cat_tokens in self._normalized_catalog:
            common = token_set.intersection(cat_tokens)
            if not common:
                continue
            # Score based on both product tokens AND catalog tokens
            # to avoid partial matches like "FRIJOL CALIMA*500G" matching "FRIJOL CALIMA AGRANEL"
            score = len(common) / max(len(cat_tokens), len(token_set))
            if score > best_score:
                best_score = score
                best_factor = factor
        # Require almost exact match (95%); otherwise None
        return best_factor if best_score >= 0.95 else None
