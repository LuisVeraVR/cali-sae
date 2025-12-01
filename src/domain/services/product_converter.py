"""
Product Converter Service
Converts product quantities to kilograms using presentation table
"""
import re
import unicodedata
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

# Pandas is optional - only needed for convert_dataframe method
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None


class ProductConverter:
    """
    Converts product quantities to kilograms based on product name and presentation table.

    Formula: kilos = (gramos_extraidos * presentacion / 1000) * cantidad_factura

    Example:
        >>> converter = ProductConverter(presentaciones_dict)
        >>> kilos = converter.convert_to_kilos("ACEITE SOYA*500CC", cantidad=10)
        >>> # If ACEITE SOYA*500CC has Presentacion=24: kilos = (500 * 24 / 1000) * 10 = 120 kg
    """

    def __init__(self, presentaciones: Dict[str, int]):
        """
        Initialize converter with presentations table.

        Args:
            presentaciones: Dictionary mapping product names to presentation values
                           Example: {"ARROZ*500G": 25, "ACEITE SOYA*500CC": 24}
        """
        self.presentaciones = {k: Decimal(str(v)) for k, v in presentaciones.items()}
        self._build_catalog()

    def _build_catalog(self):
        """Build normalized catalog for fuzzy matching"""
        self._normalized_catalog = []
        for name, presentacion in self.presentaciones.items():
            tokens = self._normalize_tokens(name)
            self._normalized_catalog.append((name, presentacion, tokens))

    def _normalize_tokens(self, name: str) -> List[str]:
        """Normalize product name into tokens for matching"""
        if not name:
            return []

        # Remove accents
        nfkd = unicodedata.normalize("NFKD", name)
        cleaned = "".join(c for c in nfkd if not unicodedata.combining(c))
        cleaned = cleaned.upper()

        # Replace special characters with spaces
        for ch in "*-/_,.;":
            cleaned = cleaned.replace(ch, " ")

        # Normalize measurement units BEFORE tokenization
        # GR/GRAMOS -> G, ML -> CC, KILO/KILOS -> KG
        cleaned = re.sub(r'(\d+)\s*(?:GR|GRAMOS)\b', r'\1G', cleaned)
        cleaned = re.sub(r'(\d+)\s*ML\b', r'\1CC', cleaned)
        cleaned = re.sub(r'(\d+)\s*(?:KILO|KILOS)\b', r'\1KG', cleaned)

        # Tokenize
        tokens = cleaned.split()

        # Remove common stopwords
        stop = {"DE", "LA", "EL", "LOS", "LAS", "A", "AL", "DEL"}
        return [t for t in tokens if t and t not in stop]

    def _extract_key_components(self, tokens: List[str]) -> dict:
        """
        Extract key components from tokenized product name.

        Returns dict with:
        - core_words: main product words (ACEITE, FRIJOL, ARROZ, etc.)
        - measurements: unit measurements (500G, 1KG, 250CC, etc.)
        - modifiers: descriptive words (AGRANEL, BLANCA, VERDE, etc.)
        """
        core_words = []
        measurements = []
        modifiers = []

        # Common product categories
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
            "FRISOYA", "MIGUEL", "REF", "CRAKENAS", "TRICOLOR", "SAN",
            "SOYA", "ROBINA", "BONGUERO", "CARG", "TO", "CRAKENA",
            "SALTALI", "CARACOTA", "GRUESO"
        }

        for token in tokens:
            # Check if it's a measurement (contains numbers)
            if re.search(r'\d+', token):
                measurements.append(token)
            elif token in product_categories:
                core_words.append(token)
            elif token in common_modifiers:
                modifiers.append(token)
            else:
                # Unknown word - treat as core word
                core_words.append(token)

        return {
            "core_words": core_words,
            "measurements": measurements,
            "modifiers": modifiers
        }

    def _find_presentacion(self, product_name: str) -> Optional[Decimal]:
        """
        Find presentation value for product using intelligent fuzzy matching.

        Strategy:
        1. First try exact match (including measurements)
        2. If not found, try matching by product name only (ignore measurements)

        This allows:
        - "ALPISTE*450G" to match "ALPISTE" (category-level presentation)
        - "HOJUELAS AZUCARADAS*40G" to match exact entry if exists

        Returns None if no good match found.
        """
        tokens = self._normalize_tokens(product_name)
        if not tokens:
            return None

        # Extract components from input product
        input_components = self._extract_key_components(tokens)
        input_core = set(input_components["core_words"])
        input_measurements = set(input_components["measurements"])
        input_modifiers = set(input_components["modifiers"])

        best_score = 0.0
        best_presentacion = None
        best_match_type = None

        for _, presentacion, cat_tokens in self._normalized_catalog:
            # Extract components from catalog entry
            cat_components = self._extract_key_components(cat_tokens)
            cat_core = set(cat_components["core_words"])
            cat_measurements = set(cat_components["measurements"])
            cat_modifiers = set(cat_components["modifiers"])

            # Core words must match
            if not input_core or not cat_core:
                continue

            core_overlap = input_core.intersection(cat_core)
            if not core_overlap:
                continue

            # Calculate component scores
            core_score = len(core_overlap) / min(len(input_core), len(cat_core))

            # Measurement score with TWO modes:
            # Mode 1: Both have measurements → strict match (prefer exact size matches)
            # Mode 2: Catalog has no measurements → flexible match (category-level)
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
                # Catalog entry has NO measurements (category-level entry like "ALPISTE", "FRIJOL CALIMA")
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

            # Modifier score
            if input_modifiers or cat_modifiers:
                modifier_overlap = input_modifiers.intersection(cat_modifiers)
                if input_modifiers and cat_modifiers:
                    modifier_score = len(modifier_overlap) / min(len(input_modifiers), len(cat_modifiers))
                else:
                    modifier_score = 0.5
            else:
                modifier_score = 1.0

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
                best_presentacion = presentacion
                best_match_type = match_type
            elif match_type == "category" and (best_match_type != "exact") and final_score >= best_score:
                best_score = final_score
                best_presentacion = presentacion
                best_match_type = match_type
            elif final_score > best_score and best_match_type not in ["exact", "category"]:
                best_score = final_score
                best_presentacion = presentacion
                best_match_type = match_type

        # Require good match (70%+)
        return best_presentacion if best_score >= 0.70 else None

    def _extract_grams_from_name(self, product_name: str) -> int:
        """
        Extract grams from product name.

        Examples:
        - 'HARINA*500G' -> 500
        - 'FRIJOL*250GR' -> 250
        - 'PANELA*125G*8UND' -> 1000 (125g × 8 units)
        - 'AZUCAR*1KG' -> 1000
        - 'ARROZ*24KILOS' -> 24000

        Returns 0 if no grams found.
        """
        if not product_name:
            return 0

        name_upper = product_name.upper()

        # Look for KG/KILO/KILOS patterns first
        match_kg = re.search(r'(\d+)\s*(?:KG|KILO|KILOS)\b', name_upper)
        if match_kg:
            return int(match_kg.group(1)) * 1000

        # Look for patterns like "125G*8UND" (grams × units)
        match_multi = re.search(r'(\d+)\s*(?:G|GR|GRAMOS)\s*\*\s*(\d+)\s*UND', name_upper)
        if match_multi:
            grams = int(match_multi.group(1))
            units = int(match_multi.group(2))
            return grams * units

        # Look for G/GR/GRAMOS patterns
        match = re.search(r'(\d+)\s*(?:G|GR|GRAMOS)\b', name_upper)
        if match:
            return int(match.group(1))

        return 0

    def _extract_volume_cc_from_name(self, product_name: str) -> int:
        """
        Extract volume in CC/ML from product name.

        Examples:
        - 'ACEITE*500CC' -> 500
        - 'ACEITE*500ML' -> 500
        - 'ACEITE*3000CC' -> 3000

        Returns 0 if no volume found.
        """
        if not product_name:
            return 0

        name_upper = product_name.upper()
        match = re.search(r'(\d+)\s*(?:CC|ML)\b', name_upper)
        if match:
            return int(match.group(1))

        return 0

    def convert_to_kilos(
        self,
        product_name: str,
        cantidad: float,
        default_presentacion: int = 1
    ) -> Tuple[Decimal, dict]:
        """
        Convert product quantity to kilograms.

        Formula: kilos = (gramos_extraidos * presentacion / 1000) * cantidad_factura

        Args:
            product_name: Product name (SUBY from invoice)
            cantidad: Quantity from invoice
            default_presentacion: Default presentation value if product not found (default: 1)

        Returns:
            Tuple of (kilos, info_dict) where info_dict contains:
            - gramos_extraidos: grams/cc extracted from name
            - presentacion: presentation value used
            - presentacion_source: "table" or "default"
            - formula: string showing the calculation
        """
        # Extract grams or cc
        grams = self._extract_grams_from_name(product_name)
        if grams == 0:
            # Try volume (CC/ML)
            grams = self._extract_volume_cc_from_name(product_name)

        # Find presentation in table
        presentacion = self._find_presentacion(product_name)
        presentacion_source = "table"

        if presentacion is None:
            presentacion = Decimal(str(default_presentacion))
            presentacion_source = "default"

        # Calculate kilos
        if grams > 0:
            kilos = (Decimal(str(grams)) * presentacion / Decimal("1000")) * Decimal(str(cantidad))
        else:
            # No grams/cc found - use presentation as direct multiplier
            kilos = presentacion * Decimal(str(cantidad))

        # Build info dict
        info = {
            "gramos_extraidos": grams,
            "presentacion": float(presentacion),
            "presentacion_source": presentacion_source,
            "formula": f"({grams} * {presentacion} / 1000) * {cantidad} = {kilos:.3f} kg"
        }

        return kilos, info

    def convert_dataframe(
        self,
        df,  # pd.DataFrame
        product_column: str = "SUBY",
        cantidad_column: str = "Cantidad",
        output_column: str = "Kilos",
        default_presentacion: int = 1,
        add_info_columns: bool = False
    ):  # -> pd.DataFrame
        """
        Convert all rows in a DataFrame to kilograms.

        Requires pandas to be installed.

        Args:
            df: Input DataFrame with product names and quantities
            product_column: Name of column containing product names (default: "SUBY")
            cantidad_column: Name of column containing quantities (default: "Cantidad")
            output_column: Name of output column for kilos (default: "Kilos")
            default_presentacion: Default presentation if product not found (default: 1)
            add_info_columns: If True, add columns with conversion details (default: False)

        Returns:
            DataFrame with added Kilos column (and optional info columns)

        Raises:
            ImportError: If pandas is not installed

        Example:
            >>> df = pd.DataFrame({
            ...     "SUBY": ["ACEITE SOYA*500CC", "ARROZ*500G", "FRIJOL CALIMA AGRANEL"],
            ...     "Cantidad": [10, 5, 2]
            ... })
            >>> converter = ProductConverter(presentaciones)
            >>> df_result = converter.convert_dataframe(df)
            >>> print(df_result[["SUBY", "Cantidad", "Kilos"]])
        """
        if not HAS_PANDAS:
            raise ImportError(
                "pandas is required for convert_dataframe method. "
                "Install it with: pip install pandas"
            )

        df = df.copy()

        results = []
        for _, row in df.iterrows():
            product_name = row[product_column]
            cantidad = row[cantidad_column]

            kilos, info = self.convert_to_kilos(
                product_name,
                cantidad,
                default_presentacion=default_presentacion
            )

            results.append({
                "kilos": float(kilos),
                **info
            })

        # Add kilos column
        df[output_column] = [r["kilos"] for r in results]

        # Optionally add info columns
        if add_info_columns:
            df[f"{output_column}_Gramos"] = [r["gramos_extraidos"] for r in results]
            df[f"{output_column}_Presentacion"] = [r["presentacion"] for r in results]
            df[f"{output_column}_Source"] = [r["presentacion_source"] for r in results]
            df[f"{output_column}_Formula"] = [r["formula"] for r in results]

        return df


# Convenience function for quick conversions
def convert_product_to_kilos(
    product_name: str,
    cantidad: float,
    presentaciones: Dict[str, int],
    default_presentacion: int = 1
) -> float:
    """
    Quick conversion function.

    Args:
        product_name: Product name (SUBY)
        cantidad: Quantity from invoice
        presentaciones: Dictionary of product names to presentation values
        default_presentacion: Default if product not found (default: 1)

    Returns:
        Kilos as float

    Example:
        >>> kilos = convert_product_to_kilos(
        ...     "ACEITE SOYA*500CC",
        ...     cantidad=10,
        ...     presentaciones={"ACEITE SOYA*500CC LA ORLANDESA E": 24}
        ... )
        >>> print(kilos)  # 120.0
    """
    converter = ProductConverter(presentaciones)
    kilos, _ = converter.convert_to_kilos(product_name, cantidad, default_presentacion)
    return float(kilos)
