#!/usr/bin/env python3
"""
Ejemplo de uso del ProductConverter con datos reales
Demuestra cómo convertir productos a kilos usando la tabla de presentaciones
"""
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.services.product_converter import ProductConverter, convert_product_to_kilos


# ============================================================================
# 1. TABLA DE PRESENTACIONES (del Excel que proporcionaste)
# ============================================================================
PRESENTACIONES = {
    # Aceites
    "ACEITE SOYA*500CC LA ORLANDESA E": 24,
    "ARVEJA VERDE*500G": 25,
    "ARVEJA VERDE*250G": 25,
    "ARROZ*500G": 25,
    "AVENA HOJUELA*250G": 24,
    "ATUN ROBINA/H LOMO/AGUA*175G": 48,
    "ATUN SABOR/P*175G LOMO/ACEITE": 48,
    "ATUN SABOR/P*175G LOMO/AGUA": 48,
    "AVENA HOJUELA*200G": 48,
    "AVENA HOJUELA*500G": 24,
    "BLANCUILLO*500 G FRIJOL": 25,
    "FRIJOL CALIMA*500G": 25,
    "FRIJOL CALIMA*250G": 25,
    "FRIJOL PALICERO*500G": 25,
    "GARBANZO*500G": 25,
    "BLANCUILLO*500G FRIJOL": 25,
    "FRIJOL CARG/TO*500G": 25,
    "FRIJOL BOLA*500G": 25,
    "HARINA AREPA*500G BLANCA": 24,
    "HARINA AREPA*500G AMARILLA": 24,
    "HARINA TRIGO UND*500G LA VECINA": 25,
    "ACEITE SOYA*250CC LA ORLANDESA": 24,
    "ACEITE SOYA*900CC LA ORLANDESA E": 24,
    "ACEITE SOYA*900CC LA ORLANDESA E": 12,
    "ACEITE SOYA*1000CC LA ORLANDESA E": 12,
    "HARINA DE TRIGO FARALLONES*500GR": 25,
    "PANELA REDONDA*500GR": 48,
    "PANELA REDONDA/ZUND*500GR 1000GR": 24,
    "LENTEJA*500G": 25,
    "LENTEJA*250G": 25,
    "MAIZ PIRA*500G": 25,
    "PASTA SALTALI*250G MACARRONCITO": 24,
    "ARROZ AGRANEL": 50,
    "FRIJOL CARAOTA AGRANEL": 50,
    "PASTA SALTALI*250G C/ANGEL": 24,
    "FRIJOL CO*450G/500G C/ANGEL": 12,
    "PASTA COMARRICO*500G SPAGUETTI": 12,
    "PASTA ZONIA*250G MACARRON": 24,
    "PASTA SALTALI*250G CONCHITA": 24,
    "PASTA ZONIA*250G SPAGUETTI": 24,
    "PASTA ZONIA*250G C/ANGEL": 24,
    "PASTA SALTALI*250G SPAGHETTI": 24,
    "PASTA ZONIA*250G CORBATA": 24,
    "ARVEJA VERDE AGRANEL": 50,
    "FRIJOL CALIMA AGRANEL": 50,
    "LENTEJA A GRANEL": 50,
    "FRIJOL CARG/TO AGRANEL": 50,
    "BLANQUILLO GRUESO VALLE": 25,
    "PASTA ZONIA*200G C/ANGEL": 24,
    "PANELA REDONDA*500G": 48,
    "FRIJOL CARAOTA*500G": 25,
    "FRIJOL BLANCA*500G": 25,
    "AZUCAR BLANCA*50KG": 50,
    "ACEITE SOYA*3000CC LA ORLANDESA": 51,
    "LECHE EN POLVO*380GR ENTERA NUTRALAC": 30,
    "ARROZ BONGUERO*500G": 25,
    "ARROZ SONORA*500GR": 25,
    "PANELA TEJO/8UND*125GR": 8,
    "HARINA TRIGO*500G LA MONJITA": 24,
    "LECHE EN POLVO*900GR ENTERA NUTRALAC": 13,
    "BLANQUILLO*500G": 50,
    "GARBANZO AGRANEL": 50,
    "ACEITE SOYA*500CC LA ORLANDESA E": 4,
    "ARROZ SONORA*500G": 50,
    "GALLETAS CRAKENAS CLUB IND 8*10": 4,
    "LECHE EN POLVO*380GR ENTERA DONA VACA": 30,
    "LECHE EN POLVO*900GR ENTERA DONA VACA": 13,
    "ATUN ROBINA/SOLIDARIO/AGUA": 48,
    "ACEITE SAN MIGUEL DE SOYA*500CC": 24,
    "ACEITE SAN MIGUEL DE SOYA*500CC": 31,
    "ACEITE SAN MIGUEL DE SOYA*5000CC": 4,
    "ACEITE SAN MIGUEL DE SOYA*1000CC": 12,
    "PANELA*500GR CARMELITA": 48,
    "AZUCAR*500GR CARMELITA": 25,
    "FRIJOL*500G": 25,
    "AZUCAR*500G CARMELITA": 25,
    "AZUCAR BLANCA*1KG YOGUETA": 25,
    "PASTA C/ANGEL*250G ZONIA**": 24,
    "PASTA ZONIA*250G CODITO": 24,
    "HARINA DE TRIGO*500G LA MONJITA**": 24,
    "LECHE EN POLVO*900G ENTERA DONA VACA": 13,
    "PASTA CONCHITA*250G ZONIA**": 24,
    "HARINA DE TRIGO*500G LA VECINA**": 25,
    "BLANQUILLO*500G LA VECINA": 50,
    "HARINA DE TRIGO*500G LA VECINA": 25,
    "FRIJOL CARG/TO*500G": 25,
    "ARVEJA VERDE A GRANEL": 50,
    "ACEITE SAN MIGUEL DE SOYA*250CC": 48,
    "ACEITE SAN MIGUEL DE SOYA*3000CC": 12,
    "FRIJOL CARG/TO A GRANEL": 50,
    "PASTA COMARRICO*500G ESPAGUETI": 24,
}


# ============================================================================
# 2. EJEMPLO 1: Conversión simple de un producto
# ============================================================================
def ejemplo_conversion_simple():
    print("=" * 80)
    print("EJEMPLO 1: CONVERSIÓN SIMPLE")
    print("=" * 80)
    print()

    # Crear el converter con la tabla de presentaciones
    converter = ProductConverter(PRESENTACIONES)

    # Ejemplos de productos
    ejemplos = [
        ("ACEITE SOYA*500CC LA ORLANDESA E", 10),
        ("ACEITE 500CC", 10),  # Sin marca - debe matchear
        ("500CC ACEITE SOYA", 10),  # Orden diferente
        ("ARROZ*500G", 5),
        ("FRIJOL CALIMA AGRANEL", 2),
        ("PASTA ZONIA 250G", 8),
        ("HARINA 500G", 6),  # Sin marca específica
        ("PRODUCTO DESCONOCIDO*500G", 3),  # No en tabla
    ]

    for product_name, cantidad in ejemplos:
        kilos, info = converter.convert_to_kilos(product_name, cantidad)

        print(f"Producto: {product_name}")
        print(f"Cantidad factura: {cantidad}")
        print(f"Gramos extraídos: {info['gramos_extraidos']}")
        print(f"Presentación: {info['presentacion']} ({info['presentacion_source']})")
        print(f"Fórmula: {info['formula']}")
        print(f"➜ RESULTADO: {kilos:.3f} kg")
        print()


# ============================================================================
# 3. EJEMPLO 2: Conversión de DataFrame completo
# ============================================================================
def ejemplo_dataframe():
    print("=" * 80)
    print("EJEMPLO 2: CONVERSIÓN DE DATAFRAME")
    print("=" * 80)
    print()

    # Simular datos de factura
    df_factura = pd.DataFrame({
        "SUBY": [
            "ACEITE SOYA*500CC LA ORLANDESA E",
            "ARROZ*500G",
            "FRIJOL CALIMA AGRANEL",
            "PASTA ZONIA*250G MACARRON",
            "HARINA AREPA*500G BLANCA",
            "LECHE EN POLVO*900GR ENTERA NUTRALAC",
            "ACEITE 1000CC",  # Orden diferente
            "FRIJOL CALIMA 500G",  # Sin asterisco
            "PRODUCTO NUEVO*750G",  # No en tabla
        ],
        "Cantidad": [10, 5, 2, 8, 6, 4, 3, 7, 2],
        "PrecioUnitario": [15000, 3000, 150000, 2500, 4000, 35000, 28000, 2800, 5000]
    })

    print("FACTURA ORIGINAL:")
    print(df_factura)
    print("\n")

    # Convertir a kilos
    converter = ProductConverter(PRESENTACIONES)
    df_resultado = converter.convert_dataframe(
        df_factura,
        product_column="SUBY",
        cantidad_column="Cantidad",
        output_column="Kilos",
        add_info_columns=True  # Agregar columnas con detalles
    )

    print("FACTURA CON CONVERSIÓN A KILOS:")
    print(df_resultado[[
        "SUBY",
        "Cantidad",
        "Kilos",
        "Kilos_Gramos",
        "Kilos_Presentacion",
        "Kilos_Source"
    ]])
    print("\n")

    # Calcular precio por kilo
    df_resultado["PrecioXKilo"] = df_resultado["PrecioUnitario"] / df_resultado["Kilos"]

    print("CON PRECIO POR KILO:")
    print(df_resultado[[
        "SUBY",
        "Kilos",
        "PrecioUnitario",
        "PrecioXKilo"
    ]])
    print("\n")


# ============================================================================
# 4. EJEMPLO 3: Función rápida de conversión
# ============================================================================
def ejemplo_funcion_rapida():
    print("=" * 80)
    print("EJEMPLO 3: FUNCIÓN RÁPIDA")
    print("=" * 80)
    print()

    # Usar función de conveniencia para conversiones rápidas
    kilos = convert_product_to_kilos(
        product_name="ACEITE SOYA*500CC",
        cantidad=10,
        presentaciones=PRESENTACIONES
    )

    print(f"ACEITE SOYA*500CC, cantidad=10")
    print(f"➜ {kilos:.3f} kg")
    print()


# ============================================================================
# 5. EJEMPLO 4: Casos especiales
# ============================================================================
def ejemplo_casos_especiales():
    print("=" * 80)
    print("EJEMPLO 4: CASOS ESPECIALES")
    print("=" * 80)
    print()

    converter = ProductConverter(PRESENTACIONES)

    casos = [
        # Diferentes unidades
        ("HARINA*500G BLANCA", 1),
        ("HARINA*500GR BLANCA", 1),  # GR vs G
        ("ACEITE*500ML", 1),  # ML vs CC
        ("ACEITE*500CC", 1),

        # Productos con KG
        ("AZUCAR BLANCA*50KG", 1),

        # Productos con múltiples unidades
        ("PANELA*125G*8UND TEJO", 1),  # 125g × 8 = 1000g

        # Productos A GRANEL (sin gramos en el nombre)
        ("ARROZ AGRANEL", 1),
        ("FRIJOL CALIMA AGRANEL", 1),
    ]

    for product_name, cantidad in casos:
        kilos, info = converter.convert_to_kilos(product_name, cantidad)
        print(f"{product_name:50} → {kilos:.3f} kg (presentación: {info['presentacion']})")

    print()


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    ejemplo_conversion_simple()
    ejemplo_dataframe()
    ejemplo_funcion_rapida()
    ejemplo_casos_especiales()

    print("=" * 80)
    print("✅ EJEMPLOS COMPLETADOS")
    print("=" * 80)
