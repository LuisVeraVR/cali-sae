"""
Catálogo de productos de El Paisano con información de kilos por presentación.
Este listado se usa para convertir cantidades de productos a kilos.
"""
import re
from decimal import Decimal
from typing import Optional, Dict


class PaisanoProductCatalog:
    """Catálogo de productos con información de conversión a kilos"""

    def __init__(self):
        self.products = self._load_products()

    def _load_products(self) -> Dict[str, Decimal]:
        """
        Carga el catálogo de productos con sus kilos por unidad.
        El formato es: "NOMBRE*PRESENTACION" -> kilos
        """
        catalog = {}

        # Listado de productos con formato: "NOMBRE*PRESENTACION=X,X KILOS EMPAQUE"
        raw_products = """
FRIJOL CALIMA*500G=12,5 KILOS PACA
LENTEJA*500G=12,5 KILOS PACA
ARVEJA VERDE*500G=12,5 KILOS PACA
FRIJOL CALIMA*250G=6,25 KILOS PACA
LENTEJA*250G=6,25 KILOS PACA
ACEITE SOYA*1000CC SAN MIGUEL EX=12 KILOS CAJA
ACEITE SOYA*500CC SAN MIGUEL EX=12 KILO CAJA
FRIJOL CALIMA*400G=10 KILOS PACA
LENTEJA*400G=10 KILOS PACA
HOJUELAS AZUCARADAS*40G=3,2 KILOS CAJA
ALPISTE*450G=11,25 KILOS PACA
ALPISTE A GRANEL=50 KILOS BULTO
BLANQUILLO*400G FRIJOL=10 KILOS PACA
FRIJOL CALIMA*450G=11,25 KILOS PACA
FRIJOL CARG/TO*450G=11,25 KILOS PACA
LENTEJA*450G=11,25 KILOS PACA
MAIZ PIRA*450G=11,25 KILOS PACA
SEMILLA GIRASOL A GRANEL=20 KILOS BULTO
ALPISTE*450G=11,25 KILOS PACA
ARVEJA VERDE*450G=11,25 KILOS PACA
BLANQUILLO*400G FRIJOL=10 KILOS PACA
CUCHUCO*450G FINO=11,25 KILOS PACA
CUCHUCO*450G GRUESO VALLE=11,25 KILOS PACA
FRIJOL CALIMA*450G=11,25 KILOS PACA
FRIJOL CARAOTA*450G=11,25 KILOS PACA
FRIJOL CARG/TO*450G=11,25 KILOS PACA
LENTEJA*450G=11,25 KILOS PACA
MAIZ PIRA*450G=11,25 KILOS PACA
MANI C/PIEL*500G=12,5 KILOS PACA
LENTEJA*450G=11,25 KILOS PACA
FRIJOL CALIMA*450G=11,25 KILOS PACA
BLANQUILLO*450G FRIJOL=11,25 KILOS PACA
MAIZ PIRA*450G=11,25 KILOS PACA
FRIJOL CARG/TO*250G=6,25 KILOS
FRIJOL CARG/TO*250G=6,25 KILOS
FRIJOL CALIMA*400G=10 KILOS PACA
FRIJOL BOLON*500G=12,5 KILOS PACA
FRIJOL CARAOTA*500G=12,5 KILOS PACA
FRIJOL CALIMA*500G=12,5 KILOS PACA
LENTEJA*250G=6,25 KILOS
LENTEJA*500G=12,5 KILOS PACA
ARVEJA VERDE*400G=10 KILOS PACA
ARVEJA VERDE*500G=12,5 KILOS PACA
BLANQUILLO*250G FRIJOL=6,25 KILOS
BLANQUILLO*400G FRIJOL=10 KILOS PACA
BLANQUILLO*500G FRIJOL=12,5 KILOS PACA
MAIZ PIRA*500G=12,5 KILOS PACA
FRIJOL CALIMA*500G=12,5 KILOS PACA
FRIJOL CALIMA*250G=6,25 KILOS
ARVEJA VERDE*500G=12,5 KILOS PACA
ALPISTE*500G=12,5 KILOS PACA
ALPISTE*250G=6,25 KILOS
BLANQUILLO*500G FRIJOL=12,5 KILOS PACA
BLANQUILLO*250G FRIJOL=6,25 KILOS
FRIJOL BOLON*500G=12,5 KILOS PACA
FRIJOL BOLON*250G=6,25 KILOS
FRIJOL CARAOTA*500G=12,5 KILOS PACA
FRIJOL CARAOTA*250G=6,25 KILOS
FRIJOL CARG/TO*250G=6,25 KILOS
LENTEJA*500G=12,5 KILOS PACA
LENTEJA*250G=6,25 KILOS
MAIZ PIRA*250G=6,25 KILOS
ALPISTE A GRANEL=50 KILOS BULTO
CEBADA PERLADA A GRANEL CON IVA=25 KILOS BULTO
BLANQUILLO*450G FRIJOL=11,25 KILOS PACA
MAIZ PIRA*450G=11,25 KILOS PACA
HARINA AREPA*500G BCA P/24 LL/27=13, KILOS PACA EN OFERTA
ARROZ*500G=12,5 KILOS PACA
FRIJOL CALIMA*500G=12,5 KILOS PACA
ALPISTE*450G=11,25 KILOS PACA
CUCHUCO*450G GRUESO VALLE=11,25 KILOS PACA
FRIJOL CALIMA*450G=11,25 KILOS PACA
FRIJOL CARG/TO*450G=11,25 KILOS PACA
GARBANZO*450G=11,25 KILOS PACA
LENTEJA*450G=11,25 KILOS PACA
MAIZ PIRA*450G=11,25 KILOS PACA
FRIJOL CARG/TO*500G=12,5 KILOS PACA
PANELA*500G CUADRADA=24 KILOS PACA
PANELA*125G*8UND TEJO=24 KILOS PACA
ARROZ*500G=12,5 KILOS PACA
AZUCAR BLANCO*500G PROVIDENCIA=12,5 KILOS PACA
AZUCAR BLANCO*1KG PROVIDENCIA=25 KILOS PACA
LENTEJA*500G=12,5 KILOS PACA
LENTEJA*250G=6,25 KILOS
FRIJOL CALIMA*500G=12,5 KILOS PACA
ARROZ A GRANEL=50 KILOS BULTO
ARROZ*500G=12,5 KILOS PACA
FRIJOL CARG/TO*500G=12,5 KILOS PACA
FRIJOL CARG/TO*500G=12,5 KILOS PACA
FRIJOL CALIMA*450G=11,25 KILOS PACA
LENTEJA*450G=11,25 KILOS PACA
FRIJOL CARAOTA*450G=11,25 KILOS PACA
LENTEJA*250G=6,25 KILOS PACA
FRIJOL CALIMA*250G=6,25 KILOS PACA
SEMILLA GIRASOL*200G=5 KILOS PACA
ALPISTE*450G=11,25 KILOS PACA
PAJARINA*500G=12,5 KILOS PACA
PAJARINA*250G=6,25 KILOS
ARVEJA VERDE*450G=11,25 KILOS PACA
BLANQUILLO*450G FRIJOL=11,25 KILOS PACA
GARBANZO*450G=11,25 KILOS PACA
LENTEJA*450G=11,25 KILOS PACA
ALPISTE*450G=11,25 KILOS PACA
ARVEJA VERDE*450G=11,25 KILOS PACA
BLANQUILLO*450G FRIJOL=11,25 KILOS PACA
GARBANZO*450G=11,25 KILOS PACA
LENTEJA*450G=11,25 KILOS PACA
MANI C/PIEL*500G=12,5 KILOS PACA
ACEITE*1000ML REF FRISOYA=12 KILOS CAJA
ACEITE*2000ML REF FRISOYA=12 KILOS CAJA
ACEITE*3000ML REF FRISOYA=18 KILOS CAJA
ACEITE*3000ML REF FRISOYA=18 KILOS CAJA
FRIJOL BOLON*500G=12,5 KILOS PACA
FRIJOL CALIMA*500G=12,5 KILOS PACA
FRIJOL CARAOTA*500G=12,5 KILOS PACA
FRIJOL CARG/TO*500G=12,5 KILOS PACA
GARBANZO*500G=12,5 KILOS PACA
SEMILLA GIRASOL*200G=20 KILOS BULTO
SERVILLETA BCA NUBE*300UND=2,63 KILOS CAJA
BLANQUILLO*500G FRIJOL=12,5 KILOS PACA
ACEITE*1000ML REF FRISOYA=12 KILOS CAJA
ACEITE*2000ML REF FRISOYA=12 KILOS CAJA
ACEITE*3000ML REF FRISOYA=18 KILOS CAJA
ACEITE*2000ML REF FRISOYA=12 KILOS CAJA
ARROZ*500G=12,5 KILOS PACA
ARVEJA VERDE*500G=12,5 KILOS PACA
BLANQUILLO*500G FRIJOL=12,5 KILOS PACA
FRIJOL BOLON*500G=12,5 KILOS PACA
FRIJOL CALIMA*500G=12,5 KILOS PACA
FRIJOL CARAOTA*500G=12,5 KILOS PACA
FRIJOL CARG/TO*500G=12,5 KILOS PACA
GARBANZO*500G=12,5 KILOS PACA
LECHE EN POLVO*380G ENTERA DONA VACA=11,4 KILOS CAJA
LENTEJA*500G=12,5 KILOS PACA
PANELA*125G*8UND TEJO=24 KILOS PACA
SEMILLA GIRASOL*200G=20 KILOS BULTO
TOALLA COCINA BCO NUBE=6 KILOS CAJA
ACEITE*500ML REF FRISOYA=12 KILOS CAJA
ARROZ A GRANEL=50 KILOS BULTO
PANELA*500G CUADRADA=24 KILOS PACA
LENTEJA*500G=12,5 KILOS PACA
"""

        # Parsear cada línea
        for line in raw_products.strip().split('\n'):
            if not line.strip():
                continue

            kilos = self._extract_kilos(line)
            if kilos is not None:
                # Extraer el nombre del producto (antes del '=')
                product_key = line.split('=')[0].strip()
                catalog[product_key] = kilos

        return catalog

    def _extract_kilos(self, product_line: str) -> Optional[Decimal]:
        """
        Extrae los kilos de una línea del listado.
        Formato: "NOMBRE*PRESENTACION=X,X KILOS EMPAQUE"
        """
        try:
            # Buscar patrón: =NUMERO KILOS o =NUMERO KILO (ignorar KILOS PACA EN OFERTA)
            pattern = r'=\s*(\d+(?:[,\.]\d+)?)\s+KILOS?\b'
            match = re.search(pattern, product_line, re.IGNORECASE)

            if match:
                kilos_str = match.group(1).replace(',', '.')
                return Decimal(kilos_str)
        except Exception as e:
            print(f"Error extrayendo kilos de '{product_line}': {str(e)}")

        return None

    def get_kilos_for_product(self, product_name: str) -> Optional[Decimal]:
        """
        Busca los kilos para un producto dado su nombre.

        Args:
            product_name: Nombre del producto (puede venir del XML)

        Returns:
            Decimal con los kilos o None si no se encuentra
        """
        # Buscar coincidencia exacta
        if product_name in self.products:
            return self.products[product_name]

        # Buscar coincidencia aproximada (sin espacios y en mayúsculas)
        normalized_name = product_name.upper().replace(' ', '')
        for key, kilos in self.products.items():
            normalized_key = key.upper().replace(' ', '')
            if normalized_name == normalized_key:
                return kilos

        # Buscar por inicio del nombre (para casos donde el XML tiene menos info)
        for key, kilos in self.products.items():
            if product_name.upper().startswith(key.split('*')[0].upper()):
                # Verificar que también coincida la presentación si existe
                if '*' in product_name:
                    product_presentation = product_name.split('*')[1].split('=')[0].strip()
                    key_presentation = key.split('*')[1].strip() if '*' in key else ''
                    if product_presentation.upper() == key_presentation.upper():
                        return kilos

        return None

    def get_all_products(self) -> Dict[str, Decimal]:
        """Retorna todo el catálogo de productos"""
        return self.products.copy()
