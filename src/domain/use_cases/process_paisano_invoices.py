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

    # Conversion map: normalized product name -> Presentacion (units per box/bulk)
    # These values represent how many units come in a box/bulk package
    # Formula used: kilos_totales = (Presentacion × gramos / 1000) × Cantidad
    #
    # Para productos A GRANEL: la Presentacion es el peso del bulto en kg
    # Para productos empacados: la Presentacion es el número de unidades por caja
    CONVERSION_MAP = {
        # Productos A GRANEL (peso del bulto en kg)
        # Estos ya son kg directos, no necesitan conversión adicional
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

        # ACEITES (Presentacion = unidades por caja)
        # ACEITE*500ML: 24 unidades por caja → (24 × 500ml / 1000) = 12 kg por caja
        "ACEITE*500ML REF FRISOYA": Decimal("24"),
        "ACEITE SOYA*500CC LA ORLANDESA E": Decimal("24"),
        "ACEITE SOYA*500CC SU ACEITE": Decimal("24"),
        "ACEITE SAN MIGUEL DE SOYA*500CC": Decimal("24"),
        "ACEITE SOYA*250CC LA ORLANDESA": Decimal("24"),
        "ACEITE SAN MIGUEL DE SOYA*250CC": Decimal("24"),

        # ACEITE*1000ML: 12 unidades por caja → (12 × 1000ml / 1000) = 12 kg por caja
        "ACEITE*1000ML REF FRISOYA": Decimal("12"),
        "ACEITE SOYA*1000CC LA ORLANDESA E": Decimal("12"),
        "ACEITE SAN MIGUEL DE SOYA*1000CC": Decimal("12"),

        # ACEITE*2000ML: 6 unidades por caja → (6 × 2000ml / 1000) = 12 kg por caja
        "ACEITE*2000ML REF FRISOYA": Decimal("6"),

        # ACEITE*3000ML: 6 unidades por caja → (6 × 3000ml / 1000) = 18 kg por caja
        "ACEITE*3000ML REF FRISOYA": Decimal("6"),
        "ACEITE SOYA*3000CC LA ORLANDESA": Decimal("6"),
        "ACEITE SAN MIGUEL DE SOYA*3000CC": Decimal("6"),

        # ACEITE*5000ML: 2-3 unidades por caja
        "ACEITE*5000ML REF FRISOYA": Decimal("2"),
        "ACEITE SOYA*5000CC LA ORLANDESA E": Decimal("2"),
        "ACEITE SAN MIGUEL DE SOYA*5000CC": Decimal("2"),

        # SEMILLAS
        # SEMILLA GIRASOL x GRANEL: bulto = 20 kg (peso directo)
        "SEMILLA GIRASOL x GRANEL": Decimal("20"),
        "SEMILLA GIRASOL AGRANEL": Decimal("20"),
        # SEMILLA GIRASOL*200G: 12 unidades por caja → (12 × 200g / 1000) = 2.4 kg por caja
        "SEMILLA GIRASOL*200G": Decimal("12"),

        # HOJUELAS AZUCARADAS
        # HOJUELAS AZUCARADAS*40G: 80 unidades por caja → (80 × 40g / 1000) = 3.2 kg por caja
        "HOJUELAS AZUCARADAS*40G": Decimal("80"),

        # LECHE EN POLVO
        # LECHE*380G: 12 unidades por caja → (12 × 380g / 1000) = 4.56 kg por caja
        "LECHE EN POLVO*380G ENTERA DONA VACA": Decimal("12"),
        "LECHE EN POLVO*380GR ENTERA NUTRALAC": Decimal("12"),
        "LECHE EN POLVO*380GR ENTERA DONA VACA": Decimal("12"),
        # LECHE*900G: 12 unidades por caja → (12 × 900g / 1000) = 10.8 kg por caja
        "LECHE EN POLVO*900GR ENTERA NUTRALAC": Decimal("12"),
        "LECHE EN POLVO*900GR ENTERA DONA VACA": Decimal("12"),
        "LECHE EN POLVO*900G ENTERA DONA VACA": Decimal("12"),

        # AZUCAR
        # AZUCAR BLANCO*1KG: 25 unidades por paca → (25 × 1kg / 1) = 25 kg por paca
        "AZUCAR BLANCO*1KG PROVIDENCIA": Decimal("25"),

        # PANELA
        # PANELA*125G*8UND TEJO: 24 paquetes por caja, cada paquete = 1kg → 24 kg por caja
        "PANELA*125G*8UND TEJO": Decimal("24"),
        "PANELA TEJO/8UND*125GR": Decimal("24"),

        # FRIJOLES empacados (código 50025 indica Presentacion = 25)
        "FRIJOL CALIMA*500G": Decimal("25"),
        "FRIJOL CALIMA 500G": Decimal("25"),

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
        Examples:
        - 'HARINA*500G' -> 500
        - 'FRIJOL*250G' -> 250
        - 'PANELA*500GR' -> 500
        - 'PANELA*125G*8UND' -> 1000 (125g × 8 units)
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

        # Look for patterns like "125G*8UND" or "125GR*8UND" (grams × units)
        match_multi = re.search(r'(\d+)\s*(?:G|GR|GRAMOS)\s*\*\s*(\d+)\s*UND', name_upper)
        if match_multi:
            grams = int(match_multi.group(1))
            units = int(match_multi.group(2))
            return grams * units

        # Look for G/GR/GRAMOS patterns (500G, 250GR, etc.)
        match = re.search(r'(\d+)\s*(?:G|GR|GRAMOS)\b', name_upper)
        if match:
            return int(match.group(1))

        return 0

    def _extract_volume_cc_from_name(self, product_name: str) -> int:
        """
        Extract volume in CC/ML from product name
        Examples:
        - 'ACEITE*500CC' -> 500
        - 'ACEITE*500ML' -> 500
        - 'ACEITE*3000CC' -> 3000
        Returns 0 if no volume found
        """
        import re
        if not product_name:
            return 0

        name_upper = product_name.upper()
        # Look for patterns like 500CC, 500ML, 1000CC, 1000ML, etc.
        match = re.search(r'(\d+)\s*(?:CC|ML)\b', name_upper)
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
        import re
        if not name:
            return []
        # Remove accents, uppercase, strip non-alnum
        nfkd = unicodedata.normalize("NFKD", name)
        cleaned = "".join(c for c in nfkd if not unicodedata.combining(c))
        cleaned = cleaned.upper()
        for ch in "*-/_,.;":
            cleaned = cleaned.replace(ch, " ")

        # Normalize measurement units BEFORE tokenization
        # Convert common variations to standard forms
        # GR/GRAMOS -> G, ML -> CC, KILO/KILOS -> KG
        cleaned = re.sub(r'(\d+)\s*(?:GR|GRAMOS)\b', r'\1G', cleaned)
        cleaned = re.sub(r'(\d+)\s*ML\b', r'\1CC', cleaned)
        cleaned = re.sub(r'(\d+)\s*(?:KILO|KILOS)\b', r'\1KG', cleaned)

        tokens = cleaned.split()
        # Remove common stopwords (but not "EN" when part of "EN POLVO")
        stop = {"DE", "LA", "EL", "LOS", "LAS", "A", "AL", "DEL"}
        return [t for t in tokens if t and t not in stop]

    def _extract_key_components(self, tokens: List[str]) -> dict:
        """
        Extract key components from tokenized product name
        Returns dict with:
        - core_words: main product words (ACEITE, FRIJOL, ARROZ, etc.)
        - measurements: unit measurements (500G, 1KG, 250CC, etc.)
        - modifiers: descriptive words (AGRANEL, BLANCA, VERDE, etc.)
        """
        import re

        core_words = []
        measurements = []
        modifiers = []

        # Common product categories (always core words)
        product_categories = {
            "ACEITE", "FRIJOL", "ARROZ", "ARVEJA", "PANELA", "HARINA",
            "PASTA", "LECHE", "AZUCAR", "LENTEJA", "GARBANZO", "BLANQUILLO",
            "ATUN", "AVENA", "MAIZ", "GALLETAS", "SEMILLA", "HOJUELAS",
            "BLANCUILLO", "TOALLA", "SERVILLETA", "CEBADA"
        }

        # Common modifiers/descriptors
        common_modifiers = {
            "AGRANEL", "GRANEL", "BLANCA", "BLANCO", "VERDE", "CALIMA",
            "PERLADA", "CARAOTA", "PALICERO", "BOLA", "MORENA", "PIRA",
            "GIRASOL", "AZUCARADAS", "POLVO", "ENTERA", "COCINA", "IND",
            "CLUB", "BCO", "NUBE", "CARMELITA", "REDONDA", "DONA", "VACA",
            "NUTRALAC", "PROVIDENCIA", "TEJO", "SALTALI", "COMARRICO",
            "ZONIA", "CARACOL", "MACARRONCITO", "SPAGHETTI", "CONCHITA",
            "CORBATA", "CODITO", "GRUESO", "VALLE", "ANGEL", "ORLANDESA",
            "FRISOYA", "MIGUEL", "REF", "CRAKENAS", "TRICOLOR"
        }

        for token in tokens:
            # Check if it's a measurement (contains numbers + units)
            if re.search(r'\d+', token):
                # Has numbers - likely a measurement
                measurements.append(token)
            elif token in product_categories:
                core_words.append(token)
            elif token in common_modifiers:
                modifiers.append(token)
            else:
                # Unknown word - treat as core word (could be brand or product type)
                core_words.append(token)

        return {
            "core_words": core_words,
            "measurements": measurements,
            "modifiers": modifiers
        }

    def _calculate_conversion_factor(self, product_name: str) -> Decimal:
        """
        Calculate conversion factor based on product name.

        Formula: factor = (Presentacion × gramos / 1000)

        Where:
        - Presentacion: units per box/bulk (from catalog or default = 1)
        - gramos: extracted from product name (500G, 250G, 1000ML, etc.)

        Priority:
        1. Check catalog for Presentacion (units per box/bulk or kg per bulto for A GRANEL)
        2. If product is A GRANEL: return Presentacion directly (already in kg)
        3. If product is NOT A GRANEL: extract grams/volume from name
        4. Calculate: (Presentacion × gramos / 1000) = kg per box/caja

        Returns:
            Decimal: conversion factor in kg per unit (to multiply by invoice quantity)
        """
        if not product_name:
            return Decimal("1")

        # Step 1: Get Presentacion from catalog (units per box/bulk or kg for A GRANEL)
        normalized_tokens = self._normalize_tokens(product_name)
        presentacion = self._match_factor(normalized_tokens)

        # Check if product is A GRANEL
        name_upper = product_name.upper()
        is_a_granel = "AGRANEL" in name_upper.replace(" ", "") or "A GRANEL" in name_upper

        # Step 2: If A GRANEL, return Presentacion directly (already in kg)
        if is_a_granel:
            if presentacion is not None:
                return presentacion  # Already in kg (e.g., 50 kg per bulto)
            else:
                # Default for unknown A GRANEL products
                return Decimal("50")

        # Step 3: Extract grams or volume from product name
        grams = self._extract_grams_from_name(product_name)

        # If no grams found, try volume in CC/ML for liquids
        if grams == 0:
            volume_cc = self._extract_volume_cc_from_name(product_name)
            if volume_cc > 0:
                # For liquids: assume density = 1.0 kg/liter (simplified)
                # So 500CC = 500ml = 500g
                grams = volume_cc

        # Step 4: Calculate conversion factor
        # Formula: (Presentacion × gramos / 1000) = kg per box/caja
        if grams > 0:
            if presentacion is not None:
                # Use catalog Presentacion
                # Example: FRIJOL CALIMA*500G with Presentacion=25
                # → (25 × 500 / 1000) = 12.5 kg per caja
                return (presentacion * Decimal(str(grams))) / Decimal("1000")
            else:
                # No catalog entry, assume Presentacion = 1 (individual units)
                # Example: "PRODUCTO NUEVO*500G" → (1 × 500 / 1000) = 0.5 kg per unit
                return Decimal(str(grams)) / Decimal("1000")

        # No conversion info found
        # If in catalog with no grams (special products), use catalog value
        if presentacion is not None:
            return presentacion

        # Otherwise, keep as units
        return Decimal("1")

    def _match_factor(self, tokens: List[str]):
        """
        Find best factor by intelligent component matching.

        This improved algorithm handles variations in word order and focuses on
        key components (product type + measurements) rather than exact token matches.

        Examples that now match:
        - "ACEITE 500CC" vs "500CC ACEITE"
        - "ACEITE SOYA 500CC LA ORLANDESA" vs "ACEITE SOYA 500CC"

        Returns:
            Decimal if found in catalog with good match, None otherwise
        """
        if not tokens:
            return None

        # Extract components from input product
        input_components = self._extract_key_components(tokens)
        input_core = set(input_components["core_words"])
        input_measurements = set(input_components["measurements"])
        input_modifiers = set(input_components["modifiers"])

        best_score = 0.0
        best_factor = None

        for _, factor, cat_tokens in self._normalized_catalog:
            # Extract components from catalog entry
            cat_components = self._extract_key_components(cat_tokens)
            cat_core = set(cat_components["core_words"])
            cat_measurements = set(cat_components["measurements"])
            cat_modifiers = set(cat_components["modifiers"])

            # Calculate component-based score
            # Core words must match (ACEITE, FRIJOL, etc.)
            if not input_core or not cat_core:
                continue

            core_overlap = input_core.intersection(cat_core)
            if not core_overlap:
                continue  # No core product match

            # Score calculation with weights:
            # - Core words: 50% weight (must match)
            # - Measurements: 40% weight (important for size/quantity)
            # - Modifiers: 10% weight (nice to have but not critical)

            # Core score: intersection / smaller set (allows catalog to have more words)
            core_score = len(core_overlap) / min(len(input_core), len(cat_core)) if input_core and cat_core else 0

            # Measurement score
            if input_measurements or cat_measurements:
                measurement_overlap = input_measurements.intersection(cat_measurements)
                # For measurements, we want exact match if they exist
                if input_measurements and cat_measurements:
                    measurement_score = len(measurement_overlap) / len(input_measurements)
                elif not input_measurements and cat_measurements:
                    # Input has no measurements but catalog does - ok if core matches
                    measurement_score = 0.5
                else:
                    # Input has measurements but catalog doesn't
                    measurement_score = 0.3
            else:
                measurement_score = 1.0  # No measurements in either

            # Modifier score (less critical)
            if input_modifiers or cat_modifiers:
                modifier_overlap = input_modifiers.intersection(cat_modifiers)
                if input_modifiers and cat_modifiers:
                    modifier_score = len(modifier_overlap) / min(len(input_modifiers), len(cat_modifiers))
                else:
                    modifier_score = 0.5  # Partial credit if one is missing
            else:
                modifier_score = 1.0  # No modifiers in either

            # Weighted final score
            final_score = (
                core_score * 0.50 +
                measurement_score * 0.40 +
                modifier_score * 0.10
            )

            if final_score > best_score:
                best_score = final_score
                best_factor = factor

        # Require strong match (75%+) - lowered from 95% to handle variations
        # This allows "ACEITE 500CC" to match "ACEITE SOYA 500CC LA ORLANDESA"
        # as long as core product type and measurement match
        return best_factor if best_score >= 0.75 else None
