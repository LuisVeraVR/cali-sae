"""
Process El Paisano Invoices Use Case
Parses XML/PDF invoices from folders and exports to Reggis CSV
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
    """Use case for processing El Paisano invoices from XML/PDF files"""

    # Conversion map: Product name -> Kilos per unit
    # Formula: kilos_totales = Factor * Cantidad_Factura
    #
    # Estos valores representan los kilos totales por unidad/paca/caja/bulto
    # y se multiplican directamente por la cantidad de la factura
    CONVERSION_MAP = {
        "ACEITE SOYA*1000CC SAN MIGUEL EX": Decimal("12.0"),
        "ACEITE SOYA*500CC SAN MIGUEL EX": Decimal("12.0"),
        "ACEITE*1000ML REF FRISOYA": Decimal("12.0"),
        "ACEITE*2000ML REF FRISOYA": Decimal("12.0"),
        "ACEITE*3000ML REF FRISOYA": Decimal("18.0"),  # Caja × 6 unid de 3000ml × 0.92 ≈ 16.56 kg
        "ACEITE*500ML REF FRISOYA": Decimal("12.0"),
        "ALPISTE A GRANEL": Decimal("50.0"),
        "ALPISTE*250G": Decimal("6.25"),
        "ALPISTE*450G": Decimal("11.25"),
        "ALPISTE*500G": Decimal("12.5"),
        "ARROZ A GRANEL": Decimal("50.0"),
        "ARROZ*500G": Decimal("12.5"),
        "ARVEJA VERDE*400G": Decimal("10.0"),
        "ARVEJA VERDE*450G": Decimal("11.25"),
        "ARVEJA VERDE*500G": Decimal("6.0"),
        "AZUCAR BLANCO*1KG PROVIDENCIA": Decimal("25.0"),
        "AZUCAR BLANCO*500G PROVIDENCIA": Decimal("12.5"),
        "BLANQUILLO*250G FRIJOL": Decimal("6.25"),
        "BLANQUILLO*400G FRIJOL": Decimal("10.0"),
        "BLANQUILLO*450G FRIJOL": Decimal("11.25"),
        "BLANQUILLO*500G FRIJOL": Decimal("6.0"),
        # "CEBADA PERLADA A GRANEL CON IVA" - Removido: usa detección automática A GRANEL (50 kg)
        "CUCHUCO*450G FINO": Decimal("11.25"),
        "CUCHUCO*450G GRUESO VALLE": Decimal("11.25"),
        "FRIJOL BOLON*250G": Decimal("6.25"),
        "FRIJOL BOLON*500G": Decimal("6.0"),
        "FRIJOL CALIMA*250G": Decimal("6.25"),
        "FRIJOL CALIMA*400G": Decimal("10.0"),
        "FRIJOL CALIMA*450G": Decimal("11.25"),
        "FRIJOL CALIMA*500G": Decimal("7.5"),
        "FRIJOL CARAOTA*250G": Decimal("6.25"),
        "FRIJOL CARAOTA*450G": Decimal("11.25"),
        "FRIJOL CARAOTA*500G": Decimal("6.0"),
        "FRIJOL CARG/TO*250G": Decimal("6.25"),
        "FRIJOL CARG/TO*450G": Decimal("11.25"),
        "FRIJOL CARG/TO*500G": Decimal("6.0"),
        "GARBANZO*450G": Decimal("11.25"),
        "GARBANZO*500G": Decimal("6.0"),
        "HARINA AREPA*500G BCA P/24 LL/27": Decimal("13.5"),
        "HOJUELAS AZUCARADAS*40G": Decimal("3.2"),
        "LECHE EN POLVO*380G ENTERA DONA VACA": Decimal("4.56"),
        "LENTEJA*250G": Decimal("6.25"),
        "LENTEJA*400G": Decimal("10.0"),
        "LENTEJA*450G": Decimal("11.25"),
        "LENTEJA*500G": Decimal("12.5"),
        "MAIZ PIRA*250G": Decimal("6.25"),
        "MAIZ PIRA*450G": Decimal("11.25"),
        "MAIZ PIRA*500G": Decimal("12.5"),
        "MANI C/PIEL*500G": Decimal("12.5"),
        "PAJARINA*250G": Decimal("6.25"),
        "PAJARINA*500G": Decimal("12.5"),
        "PANELA*125G*8UND TEJO": Decimal("24.0"),
        "PANELA*500G CUADRADA": Decimal("24.0"),
        "SEMILLA GIRASOL A GRANEL": Decimal("20.0"),
        "SEMILLA GIRASOL*200G": Decimal("2.4"),
        "SERVILLETA BCA NUBE*300UND": Decimal("2.11"),
        "TOALLA COCINA BCO NUBE": Decimal("6.0"),
    }

    def __init__(
        self,
        report_repository: ReportRepositoryInterface,
        xml_parser,  # XMLInvoiceParser
        reggis_exporter,  # JCRReggisExporter (Reggis CSV exporter)
        conversion_repository=None,  # PaisanoConversionRepository
        pdf_parser=None  # PaisanoPDFParser
    ):
        self.report_repository = report_repository
        self.xml_parser = xml_parser
        self.reggis_exporter = reggis_exporter
        self.conversion_repository = conversion_repository
        self.pdf_parser = pdf_parser
        self._reload_catalog()

    def execute(
        self,
        input_paths: List[str],
        username: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> tuple[bool, str, int]:
        """
        Process XML/PDF invoices (folders or individual files) and export to Reggis CSV

        Args:
            input_paths: List of folder paths or XML/PDF file paths
            username: Username of the person processing
            progress_callback: Optional callback for progress updates (current, total)

        Returns:
            Tuple of (success, message, records_processed)
        """
        if not input_paths:
            return False, "No se seleccionaron archivos o carpetas", 0

        all_invoices: List[Invoice] = []
        files_to_process = self._expand_input_paths(input_paths)
        total_items = len(files_to_process)

        if not total_items:
            return False, "No se encontraron archivos XML o PDF", 0

        # Reload catalog each run to pick up new conversions
        self._reload_catalog()

        for idx, path in enumerate(files_to_process):
            if progress_callback:
                progress_callback(idx, total_items)

            try:
                invoices = self._parse_input_path(path)
                all_invoices.extend(invoices)
            except Exception as exc:
                print(f"Error processing {path}: {exc}")
                continue

        if not all_invoices:
            return False, "No se encontraron facturas validas en los archivos", 0

        try:
            # Apply conversion factors to kilos and recompute unit price
            original_quantities = {}
            missing_products = 0

            for invoice in all_invoices:
                for product in invoice.products:
                    original_qty = product.quantity
                    product.original_quantity = original_qty

                    # Get conversion factor (catalog first, then heuristics)
                    # NUEVO: Ajustar factor según la unidad original (UND, P25, CJ, etc.)
                    factor = self._calculate_conversion_factor_with_unit(
                        product.name,
                        product.original_unit_code or product.unit_of_measure
                    )
                    if factor == Decimal("1"):
                        missing_products += 1

                    # Force underlying code
                    product.underlying_code = "SPN-1"

                    # Convert quantity to kg: kilos_totales = Factor * Cantidad_Factura
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
            message = f"Datos exportados exitosamente al formato Reggis:\\n{output_file}"
            if missing_products:
                message += f"\\nAdvertencia: {missing_products} productos sin factor de conversion (usado 1:1)."
        except Exception as exc:
            return False, f"Error al exportar datos: {exc}", 0

        total_records = sum(invoice.get_product_count() for invoice in all_invoices)
        total_size = sum(Path(p).stat().st_size for p in files_to_process if Path(p).exists())

        report = Report(
            id=None,
            username=username,
            company="EL PAISANO",
            filename=", ".join([Path(f).name for f in input_paths]),
            records_processed=total_records,
            created_at=datetime.now(),
            file_size=total_size
        )
        self.report_repository.create(report)

        if progress_callback:
            progress_callback(total_items, total_items)

        return True, message, total_records

    # --- Helpers ---
    def _reload_catalog(self):
        """Load hardcoded + DB conversions and precompute tokens for fuzzy matching"""
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
        cleaned = re.sub(r'(\\d+)\\s*(?:GR|GRAMOS)\\b', r'\\1G', cleaned)
        cleaned = re.sub(r'(\\d+)\\s*ML\\b', r'\\1CC', cleaned)
        cleaned = re.sub(r'(\\d+)\\s*(?:KILO|KILOS)\\b', r'\\1KG', cleaned)

        tokens = cleaned.split()
        # Remove common stopwords
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
            "BLANCUILLO", "TOALLA", "SERVILLETA", "CEBADA", "ALPISTE",
            "CUCHUCO", "BOLON", "CARAOTA", "MANI", "PAJARINA"
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
            "FRISOYA", "MIGUEL", "REF", "CRAKENAS", "TRICOLOR", "SOYA",
            "SAN", "FINO", "CUADRADA", "PIEL"
        }

        for token in tokens:
            # Check if it's a measurement (contains numbers + units)
            if re.search(r'\\d+', token):
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

    def _calculate_conversion_factor_with_unit(self, product_name: str, unit_code: str) -> Decimal:
        """
        Calculate conversion factor considering both product name AND unit code.

        Unit codes:
        - UND: Unidad individual (calcula: gramos ÷ 1000 o volumen × densidad)
        - P25, P20, P12: Pacas (calcula: num_paca × gramos ÷ 1000)
        - CJ, CAJ: Cajas (usa factor del catálogo)
        - B20, B10: Bultos con peso fijo (B20 = 20 kg)
        - Kg: Kilos (ya está en kilos, factor 1.0)

        Examples:
        - FRIJOL CALIMA*500G con UND: (500 ÷ 1000) = 0.5 kg por unidad
        - FRIJOL CALIMA*500G con P25: (25 × 500 ÷ 1000) = 12.5 kg por paca
        - SEMILLA GIRASOL A GRANEL con B20: 20 kg por bulto
        """
        if not unit_code:
            return self._calculate_conversion_factor(product_name)

        unit_upper = unit_code.upper().strip()

        # Si ya viene en kilos, no convertir
        if unit_upper in ["KG", "KGM"]:
            return Decimal("1.0")

        # Detectar bultos con peso fijo (B20, B10, B25, etc.)
        import re
        bulto_match = re.match(r'B(\d+)', unit_upper)
        if bulto_match:
            bulto_kg = Decimal(bulto_match.group(1))
            print(f"[CONVERSION] {product_name} con {unit_code}: Bulto de {bulto_kg} kg")
            return bulto_kg

        # Detectar pacas (P25, P20, P12, etc.)
        paca_match = re.match(r'P(\d+)', unit_upper)
        if paca_match:
            paca_count = int(paca_match.group(1))
            # Extraer gramos del nombre del producto
            grams = self._extract_grams_from_name(product_name)
            if grams:
                # Formula: (paca_count × gramos ÷ 1000)
                factor = (Decimal(str(paca_count)) * grams) / Decimal("1000")
                print(f"[CONVERSION] {product_name} con {unit_code}: P{paca_count} × {grams}g ÷ 1000 = {factor} kg")
                return factor
            # Si no hay gramos en el nombre, usar volumen (CC/ML)
            volume_cc = self._extract_volume_cc_from_name(product_name)
            if volume_cc:
                # Formula: (paca_count × volumen_cc ÷ 1000) × densidad
                density = Decimal("0.92")  # Para aceites
                factor = (Decimal(str(paca_count)) * volume_cc * density) / Decimal("1000")
                print(f"[CONVERSION] {product_name} con {unit_code}: P{paca_count} × {volume_cc}cc × {density} ÷ 1000 = {factor} kg")
                return factor

        # Detectar cajas con número (CJ12, CJ24, etc.)
        caja_match = re.match(r'(?:CJ|CAJ)(\d+)', unit_upper)
        if caja_match:
            caja_count = int(caja_match.group(1))
            # Extraer gramos del nombre del producto
            grams = self._extract_grams_from_name(product_name)
            if grams:
                # Formula: (caja_count × gramos ÷ 1000)
                factor = (Decimal(str(caja_count)) * grams) / Decimal("1000")
                print(f"[CONVERSION] {product_name} con {unit_code}: CJ{caja_count} × {grams}g ÷ 1000 = {factor} kg")
                return factor
            # Si no hay gramos en el nombre, usar volumen (CC/ML)
            volume_cc = self._extract_volume_cc_from_name(product_name)
            if volume_cc:
                # Formula: (caja_count × volumen_cc ÷ 1000) × densidad
                density = Decimal("0.92")  # Para aceites
                factor = (Decimal(str(caja_count)) * volume_cc * density) / Decimal("1000")
                print(f"[CONVERSION] {product_name} con {unit_code}: CJ{caja_count} × {volume_cc}cc × {density} ÷ 1000 = {factor} kg")
                return factor

        # Para UND (unidades individuales): calcular basándose en gramos/volumen del producto
        if unit_upper == "UND":
            # Intentar extraer gramos del nombre
            grams = self._extract_grams_from_name(product_name)
            if grams:
                factor = grams / Decimal("1000")
                print(f"[CONVERSION] {product_name} con UND: {grams}g ÷ 1000 = {factor} kg por unidad")
                return factor

            # Intentar extraer volumen (para aceites, etc.)
            volume_cc = self._extract_volume_cc_from_name(product_name)
            if volume_cc:
                density = Decimal("0.92")  # Para aceites
                factor = (volume_cc * density) / Decimal("1000")
                print(f"[CONVERSION] {product_name} con UND: {volume_cc}cc × {density} ÷ 1000 = {factor} kg por unidad")
                return factor

            # Si es producto a granel con UND, usar peso estándar
            if self._is_bulk_product(product_name):
                factor = Decimal("50.0")
                print(f"[CONVERSION] {product_name} con UND: Producto a granel = {factor} kg")
                return factor

        # Para CJ, CAJ (sin número) y otros códigos, usar el factor del catálogo
        factor = self._calculate_conversion_factor(product_name)
        print(f"[CONVERSION] {product_name} con {unit_code}: Factor del catálogo = {factor} kg")
        return factor

    def _calculate_conversion_factor(self, product_name: str) -> Decimal:
        """
        Calculate conversion factor with multiple strategies:
        1. Catalog/fuzzy match (preferred)
        2. Extract grams from name (e.g., 500G, 1KG)
        3. Extract volume in CC/ML (uses oil density 0.92)
        4. Bulk products (AGRANEL) default to 50kg
        """
        # Try catalog (returns None if no match)
        catalog_factor = self._get_conversion_factor(product_name)
        if catalog_factor is not None:
            return catalog_factor

        grams = self._extract_grams_from_name(product_name)
        if grams:
            return grams / Decimal("1000")

        volume_cc = self._extract_volume_cc_from_name(product_name)
        if volume_cc:
            density = Decimal("0.92")  # Oil density approximation
            return (volume_cc / Decimal("1000")) * density

        if self._is_bulk_product(product_name):
            return Decimal("50.0")

        return Decimal("1")

    def _get_conversion_factor(self, product_name: str) -> Optional[Decimal]:
        """
        Get conversion factor from catalog using fuzzy matching.

        Returns:
            Decimal if found, otherwise None
        """
        if not product_name:
            return None

        normalized_tokens = self._normalize_tokens(product_name)
        return self._match_factor(normalized_tokens)

    def _match_factor(self, tokens: List[str]):
        """
        Find best factor by intelligent component matching.

        Strategy:
        1. Prefer exact matches (same size and core product)
        2. Allow category matches (same core product, any size)

        This allows:
        - "ALPISTE*450G" to match "ALPISTE*450G" exactly (priority)
        - "ALPISTE*450G" to match "ALPISTE A GRANEL" (category-level)
        - "ACEITE 500CC" vs "500CC ACEITE" (order independent)

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
        best_match_type = None

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

            # Core score: intersection / smaller set (allows catalog to have more words)
            core_score = len(core_overlap) / min(len(input_core), len(cat_core)) if input_core and cat_core else 0

            # Measurement score with TWO modes:
            # Mode 1: Both have measurements -> strict match (prefer exact size matches)
            # Mode 2: Catalog has no measurements -> flexible match (category-level)
            if input_measurements and cat_measurements:
                # Both have measurements - check if they match
                measurement_overlap = input_measurements.intersection(cat_measurements)
                if measurement_overlap:
                    # Exact size match - PRIORITY
                    measurement_score = 1.0
                    match_type = "exact"
                else:
                    # Different sizes - low score
                    measurement_score = 0.2
                    match_type = "different_size"
            elif not cat_measurements:
                # Catalog entry has NO measurements (category-level entry like "ALPISTE A GRANEL")
                # This is PERFECT for any size variant
                measurement_score = 1.0
                match_type = "category"
            elif not input_measurements:
                # Input has no measurements but catalog does
                measurement_score = 0.5
                match_type = "partial"
            else:
                measurement_score = 1.0
                match_type = "none"

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
            # Increased weight for core (60%) and measurements (30%)
            final_score = (
                core_score * 0.60 +
                measurement_score * 0.30 +
                modifier_score * 0.10
            )

            # Prioritize exact matches over category matches
            if match_type == "exact" and final_score >= best_score:
                best_score = final_score
                best_factor = factor
                best_match_type = match_type
            elif match_type == "category" and (best_match_type != "exact") and final_score >= best_score:
                best_score = final_score
                best_factor = factor
                best_match_type = match_type
            elif final_score > best_score and best_match_type not in ["exact", "category"]:
                best_score = final_score
                best_factor = factor
                best_match_type = match_type

        # Require good match (70%+) - maintains precision while handling variations
        return best_factor if best_score >= 0.70 else None

    def _extract_grams_from_name(self, name: str) -> Optional[Decimal]:
        """
        Extract grams or kilos from product name, considering multipliers.

        Examples:
        - "PANELA*125G*8UND" → 125 × 8 = 1000 gramos
        - "FRIJOL*500G" → 500 gramos
        - "LECHE*380G" → 380 gramos
        """
        import re
        if not name:
            return None

        # Pattern 1: Detect "XG*YUND" or "XG*Y" (grams with unit multiplier)
        # Examples: "125G*8UND", "250G*4", "500G*2UND"
        match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:G|GR|GRAMOS)\s*\*\s*(\d+)\s*(?:UND|UNID)?', name, re.IGNORECASE)
        if match:
            grams = match.group(1).replace('.', '').replace(',', '.')
            multiplier = match.group(2)
            try:
                total_grams = Decimal(grams) * Decimal(multiplier)
                print(f"[EXTRACT_GRAMS] {name}: {grams}g × {multiplier} = {total_grams}g")
                return total_grams
            except Exception:
                return None

        # Pattern 2: Simple grams (no multiplier)
        match = re.search(r'(\d+(?:[.,]\d+)?)\s*(G|GR|GRAMOS)\b', name, re.IGNORECASE)
        if match:
            value = match.group(1).replace('.', '').replace(',', '.')
            try:
                return Decimal(value)
            except Exception:
                return None

        # Pattern 3: Kilos
        match = re.search(r'(\d+(?:[.,]\d+)?)\s*(KG|KILO|KILOS)\b', name, re.IGNORECASE)
        if match:
            value = match.group(1).replace('.', '').replace(',', '.')
            try:
                return Decimal(value) * Decimal("1000")
            except Exception:
                return None
        return None

    def _extract_volume_cc_from_name(self, name: str) -> Optional[Decimal]:
        """Extract volume in CC/ML from product name"""
        import re
        if not name:
            return None
        match = re.search(r'(\d+(?:[.,]\d+)?)\s*(CC|ML)\b', name, re.IGNORECASE)
        if not match:
            return None
        value = match.group(1).replace('.', '').replace(',', '.')
        try:
            return Decimal(value)
        except Exception:
            return None

    def _is_bulk_product(self, name: str) -> bool:
        """Identify bulk/granel products"""
        if not name:
            return False
        normalized = name.upper()
        return "AGRANEL" in normalized or "A GRANEL" in normalized or "GRANEL" in normalized

    def _expand_input_paths(self, paths: List[str]) -> List[Path]:
        """Return a flat list of XML/PDF files from provided paths"""
        collected: List[Path] = []
        for raw_path in paths:
            p = Path(raw_path)
            if p.is_dir():
                collected.extend(
                    sorted(
                        f
                        for f in p.rglob("*")
                        if f.is_file() and f.suffix.lower() in {".xml", ".pdf"}
                    )
                )
            elif p.is_file() and p.suffix.lower() in {".xml", ".pdf"}:
                collected.append(p)
        return collected

    def _parse_input_path(self, path: Path) -> List[Invoice]:
        """Parse a single XML or PDF path into invoices"""
        if not path.exists() or not path.is_file():
            return []

        suffix = path.suffix.lower()
        if suffix == ".xml":
            invoice = self.xml_parser.parse_xml_file(str(path))
            return [invoice] if invoice else []

        if suffix == ".pdf":
            if not self.pdf_parser:
                print(f"No hay parser PDF configurado para {path}")
                return []
            invoice = self.pdf_parser.parse_pdf_file(str(path))
            return [invoice] if invoice else []

        return []
