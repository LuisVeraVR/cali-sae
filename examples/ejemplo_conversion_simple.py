#!/usr/bin/env python3
"""
Ejemplo simple de uso del ProductConverter (sin pandas)
Demuestra cómo convertir productos a kilos usando la tabla de presentaciones
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.services.product_converter import ProductConverter


# ============================================================================
# TABLA DE PRESENTACIONES (del Excel que proporcionaste)
# ============================================================================
PRESENTACIONES = {
    # Aceites
    "ACEITE SOYA*500CC LA ORLANDESA E": 24,
    "ACEITE SOYA*1000CC LA ORLANDESA E": 12,
    "ACEITE SOYA*3000CC LA ORLANDESA": 51,
    "ACEITE SAN MIGUEL DE SOYA*500CC": 24,
    "ACEITE SAN MIGUEL DE SOYA*1000CC": 12,
    "ACEITE SAN MIGUEL DE SOYA*3000CC": 12,
    "ACEITE SAN MIGUEL DE SOYA*5000CC": 4,

    # Arroces
    "ARVEJA VERDE*500G": 25,
    "ARVEJA VERDE*250G": 25,
    "ARROZ*500G": 25,
    "ARROZ AGRANEL": 50,
    "ARVEJA VERDE AGRANEL": 50,
    "ARROZ BONGUERO*500G": 25,
    "ARROZ SONORA*500GR": 25,

    # Frijoles
    "FRIJOL CALIMA*500G": 25,
    "FRIJOL CALIMA AGRANEL": 50,
    "FRIJOL CARAOTA AGRANEL": 50,
    "FRIJOL CARAOTA*500G": 25,
    "FRIJOL CARG/TO*500G": 25,
    "FRIJOL CARG/TO AGRANEL": 50,
    "BLANCUILLO*500G FRIJOL": 25,

    # Pastas
    "PASTA SALTALI*250G MACARRONCITO": 24,
    "PASTA ZONIA*250G MACARRON": 24,
    "PASTA ZONIA*250G C/ANGEL": 24,
    "PASTA ZONIA*250G CORBATA": 24,
    "PASTA COMARRICO*500G SPAGUETTI": 12,

    # Harinas
    "HARINA AREPA*500G BLANCA": 24,
    "HARINA TRIGO UND*500G LA VECINA": 25,
    "HARINA DE TRIGO*500G LA MONJITA": 24,

    # Leche
    "LECHE EN POLVO*380GR ENTERA NUTRALAC": 30,
    "LECHE EN POLVO*900GR ENTERA NUTRALAC": 13,
    "LECHE EN POLVO*900GR ENTERA DONA VACA": 13,

    # Otros
    "PANELA REDONDA*500GR": 48,
    "PANELA TEJO/8UND*125GR": 8,
    "AZUCAR BLANCA*50KG": 50,
    "LENTEJA*500G": 25,
    "GARBANZO*500G": 25,
    "GARBANZO AGRANEL": 50,
}


def main():
    print("=" * 80)
    print("EJEMPLOS DE CONVERSIÓN DE PRODUCTOS A KILOS")
    print("=" * 80)
    print()

    # Crear el converter
    converter = ProductConverter(PRESENTACIONES)

    print("📋 EJEMPLO 1: Productos con nombres exactos")
    print("-" * 80)
    ejemplos_exactos = [
        ("ACEITE SOYA*500CC LA ORLANDESA E", 10),
        ("ARROZ*500G", 5),
        ("FRIJOL CALIMA AGRANEL", 2),
    ]

    for product_name, cantidad in ejemplos_exactos:
        kilos, info = converter.convert_to_kilos(product_name, cantidad)
        print(f"\n  Producto: {product_name}")
        print(f"  Cantidad: {cantidad}")
        print(f"  Fórmula:  {info['formula']}")
        print(f"  ➜ RESULTADO: {kilos:.3f} kg")

    print("\n\n📋 EJEMPLO 2: Productos con orden diferente de palabras")
    print("-" * 80)
    ejemplos_orden = [
        ("ACEITE 500CC", 10, "→ debe matchear con ACEITE SOYA*500CC LA ORLANDESA E"),
        ("500CC ACEITE SOYA", 10, "→ orden invertido"),
        ("AGRANEL FRIJOL CALIMA", 2, "→ orden invertido"),
        ("PASTA ZONIA 250G", 8, "→ sin asterisco"),
    ]

    for product_name, cantidad, nota in ejemplos_orden:
        kilos, info = converter.convert_to_kilos(product_name, cantidad)
        print(f"\n  Producto: {product_name} {nota}")
        print(f"  Cantidad: {cantidad}")
        print(f"  Presentación: {info['presentacion']} ({info['presentacion_source']})")
        print(f"  ➜ RESULTADO: {kilos:.3f} kg")

    print("\n\n📋 EJEMPLO 3: Diferentes unidades (G vs GR, ML vs CC)")
    print("-" * 80)
    ejemplos_unidades = [
        ("HARINA*500G BLANCA", 1),
        ("HARINA*500GR BLANCA", 1),  # GR se convierte a G
        ("ACEITE*500ML", 1),  # ML se convierte a CC
        ("ACEITE*500CC", 1),
    ]

    for product_name, cantidad in ejemplos_unidades:
        kilos, info = converter.convert_to_kilos(product_name, cantidad)
        print(f"  {product_name:35} → {kilos:.3f} kg (gramos: {info['gramos_extraidos']})")

    print("\n\n📋 EJEMPLO 4: Casos especiales")
    print("-" * 80)
    casos_especiales = [
        ("AZUCAR BLANCA*50KG", 1, "→ producto con KG en el nombre"),
        ("PANELA*125G*8UND TEJO", 1, "→ 125g × 8 unidades = 1000g"),
        ("ARROZ AGRANEL", 1, "→ A GRANEL sin gramos"),
        ("PRODUCTO NUEVO*500G", 1, "→ NO en tabla, usa presentación=1"),
    ]

    for product_name, cantidad, nota in casos_especiales:
        kilos, info = converter.convert_to_kilos(product_name, cantidad)
        print(f"\n  {product_name} {nota}")
        print(f"  Presentación: {info['presentacion']} ({info['presentacion_source']})")
        print(f"  ➜ {kilos:.3f} kg")

    print("\n\n📋 EJEMPLO 5: Comparación de productos similares")
    print("-" * 80)
    print("\n  Mismo producto, diferentes tamaños:")
    tamaños = [
        ("ACEITE SOYA*500CC", 1),
        ("ACEITE SOYA*1000CC", 1),
        ("ACEITE SOYA*3000CC", 1),
    ]

    for product_name, cantidad in tamaños:
        kilos, info = converter.convert_to_kilos(product_name, cantidad)
        print(f"  {product_name:30} → {kilos:.3f} kg (present: {info['presentacion']})")

    print("\n\n📋 EJEMPLO 6: Factura completa simulada")
    print("-" * 80)
    factura = [
        ("ACEITE SOYA*500CC LA ORLANDESA E", 10, 15000),
        ("ARROZ*500G", 5, 3000),
        ("FRIJOL CALIMA AGRANEL", 2, 150000),
        ("PASTA ZONIA*250G MACARRON", 8, 2500),
        ("HARINA AREPA*500G BLANCA", 6, 4000),
    ]

    print(f"\n  {'Producto':<40} {'Cant':>5} {'Kilos':>8} {'$/Unid':>10} {'$/Kilo':>10}")
    print("  " + "-" * 80)

    total_kilos = 0
    for product_name, cantidad, precio_unitario in factura:
        kilos, info = converter.convert_to_kilos(product_name, cantidad)
        precio_x_kilo = precio_unitario / float(kilos)
        total_kilos += float(kilos)

        print(f"  {product_name:<40} {cantidad:>5} {kilos:>8.2f} {precio_unitario:>10,} {precio_x_kilo:>10.2f}")

    print("  " + "-" * 80)
    print(f"  {'TOTAL':<40} {'':<5} {total_kilos:>8.2f} kg")

    print("\n\n" + "=" * 80)
    print("✅ TODOS LOS EJEMPLOS COMPLETADOS")
    print("=" * 80)


if __name__ == "__main__":
    main()
