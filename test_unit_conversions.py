#!/usr/bin/env python3
"""
Test script para verificar las correcciones en las conversiones de unidades
Basado en los ejemplos proporcionados por el usuario
"""
from decimal import Decimal
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from domain.use_cases.process_paisano_invoices import ProcessPaisanoInvoices


def test_conversions():
    """Test conversions with user examples"""

    # Create a minimal instance to test conversion methods
    processor = ProcessPaisanoInvoices(
        report_repository=None,
        xml_parser=None,
        reggis_exporter=None,
        conversion_repository=None
    )

    print("=" * 80)
    print("PRUEBA DE CONVERSIONES DE UNIDADES - CORRECCIONES")
    print("=" * 80)
    print()

    # Test cases: (product_name, unit_code, cantidad_original, expected_kg, note)
    test_cases = [
        # CASO 1: Productos UND - deben usar solo gramos del nombre
        ("FRIJOL CALIMA*500G", "UND", Decimal("10"), Decimal("5.0"),
         "UND: 10 unidades × 500g ÷ 1000 = 5 kg"),

        ("ACEITE SOYA*500CC", "UND", Decimal("10"), Decimal("5.0"),
         "UND: 10 unidades × 500cc ÷ 1000 = 5 litros"),

        # CASO 2: Productos con P24, B20, etc. - número × gramos ÷ 1000 × cantidad
        ("PANELA*125G*8UND TEJO", "P24", Decimal("3"), Decimal("72.0"),
         "P24: 3 × (24 × 1000g ÷ 1000) = 3 × 24 = 72 kg (125g × 8 = 1000g)"),

        ("FRIJOL CALIMA*500G", "P25", Decimal("55"), Decimal("687.5"),
         "P25: 55 × (25 × 500g ÷ 1000) = 55 × 12.5 = 687.5 kg"),

        ("FRIJOL CALIMA*500G", "B20", Decimal("10"), Decimal("100.0"),
         "B20: 10 × (20 × 500g ÷ 1000) = 10 × 10 = 100 kg"),

        # CASO 3: Productos CJ (cajas) - extraer unidades del nombre
        # NOTA: En este caso el producto dice "CAJA X 6UNID DE 3000"
        # Pero el nombre que llega es solo "ACEITE*3000ML REF FRISOYA"
        # Por lo tanto, usará el factor del catálogo (6.0)
        ("ACEITE*3000ML REF FRISOYA", "CJ", Decimal("1"), Decimal("6.0"),
         "CJ: 1 caja × 6.0 kg (factor catálogo) = 6 litros (NOTA: si el nombre tuviera 'X 6UNID' sería 18)"),

        # CASO 4: Productos CJ con unidades en el nombre
        ("ACEITE*3000ML X 6UNID", "CJ", Decimal("1"), Decimal("18.0"),
         "CJ: 1 caja × (6 unid × 3000ml ÷ 1000) = 18 litros"),

        # CASO 5: Detectar aceites para cambiar a litros
        ("ACEITE SOYA*500CC LA ORLANDESA E", "CJ", Decimal("1"), Decimal("12.0"),
         "CJ: 1 caja × 12.0 litros (factor catálogo, debe estar en LT)"),
    ]

    all_passed = True
    for product_name, unit_code, cantidad_original, expected_kg, note in test_cases:
        # Calculate conversion factor
        factor = processor._calculate_conversion_factor_with_unit(product_name, unit_code)
        converted_qty = cantidad_original * factor

        # Check if product is oil (for unit verification)
        is_oil = processor._is_oil_product(product_name)
        expected_unit = "Lt" if is_oil else "Kg"

        # Check if conversion is correct (allow small rounding differences)
        is_correct = abs(converted_qty - expected_kg) < Decimal("0.01")
        status = "✓ PASS" if is_correct else "✗ FAIL"

        if not is_correct:
            all_passed = False

        print(f"{status}")
        print(f"  Producto: {product_name}")
        print(f"  Unidad Original: {unit_code}")
        print(f"  Nota: {note}")
        print(f"  Cantidad Original: {cantidad_original} {unit_code}")
        print(f"  Factor: {factor}")
        print(f"  Convertido: {converted_qty} {expected_unit}")
        print(f"  Esperado: {expected_kg} {expected_unit}")
        print(f"  Es aceite: {'Sí' if is_oil else 'No'}")
        if not is_correct:
            print(f"  DIFERENCIA: {converted_qty - expected_kg}")
        print()

    print("=" * 80)
    if all_passed:
        print("✓ TODAS LAS PRUEBAS PASARON")
    else:
        print("✗ ALGUNAS PRUEBAS FALLARON")
    print("=" * 80)

    return all_passed


if __name__ == "__main__":
    success = test_conversions()
    sys.exit(0 if success else 1)
