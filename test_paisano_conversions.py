#!/usr/bin/env python3
"""
Test script for Paisano product conversions
Verifies that the new conversion logic works correctly
"""
from decimal import Decimal
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from domain.use_cases.process_paisano_invoices import ProcessPaisanoInvoices


def test_conversions():
    """Test various product conversions"""

    # Create a minimal instance to test conversion methods
    processor = ProcessPaisanoInvoices(
        report_repository=None,
        xml_parser=None,
        reggis_exporter=None,
        conversion_repository=None
    )

    # Test cases: (product_name, original_quantity, expected_kg, note)
    test_cases = [
        # Products in CATALOG (should use catalog factors)
        ("HARINA AREPA*500G BLANCA", Decimal("10"), Decimal("10"), "Catálogo: factor 24"),
        ("FRIJOL CALIMA*250G", Decimal("12"), Decimal("12"), "Catálogo: factor 25"),
        ("AZUCAR BLANCA*500G", Decimal("24"), Decimal("24"), "Catálogo: factor 25"),
        ("PANELA*500GR", Decimal("48"), Decimal("48"), "Catálogo: factor 48"),
        ("ACEITE SOYA*500CC LA ORLANDESA E", Decimal("24"), Decimal("24"), "Catálogo: factor 24"),
        ("ACEITE SOYA*1000CC LA ORLANDESA E", Decimal("12"), Decimal("12"), "Catálogo: factor 12"),
        ("ACEITE SOYA*3000CC LA ORLANDESA", Decimal("6"), Decimal("6"), "Catálogo: factor 51"),

        # Products a granel in CATALOG
        ("ARROZ AGRANEL", Decimal("2"), Decimal("2"), "Catálogo: factor 50 (kg por saco)"),
        ("FRIJOL CALIMA AGRANEL", Decimal("3"), Decimal("3"), "Catálogo: factor 50"),
        ("LENTEJA A GRANEL", Decimal("1"), Decimal("1"), "Catálogo: factor 50"),

        # Products in CATALOG with KG
        ("AZUCAR BLANCA*50KG", Decimal("2"), Decimal("2"), "Catálogo: factor 50"),
        ("PANELA REDONDA*24KILOS", Decimal("1"), Decimal("1"), "Catálogo: factor 24"),

        # Products NOT in catalog (should use automatic extraction)
        ("PRODUCTO NUEVO*500G", Decimal("10"), Decimal("5.0"), "Auto: 10 × 0.5 kg = 5 kg"),
        ("ACEITE NUEVO*500CC", Decimal("24"), Decimal("11.04"), "Auto: 24 × 0.46 kg = 11.04 kg"),

        # Products without conversion info (should stay as units)
        ("GALLETAS CRAKENAS CLUB IND 8*10", Decimal("10"), Decimal("10.0"), "Sin conversión"),
    ]

    print("=" * 80)
    print("PRUEBA DE CONVERSIONES DE PRODUCTOS EL PAISANO")
    print("=" * 80)
    print()

    all_passed = True
    for product_name, original_qty, expected_kg, note in test_cases:
        # Calculate conversion factor
        factor = processor._calculate_conversion_factor(product_name)
        converted_kg = original_qty * factor

        # Check if conversion is correct (allow small rounding differences)
        is_correct = abs(converted_kg - expected_kg) < Decimal("0.01")
        status = "✓ PASS" if is_correct else "✗ FAIL"

        if not is_correct:
            all_passed = False

        print(f"{status}")
        print(f"  Producto: {product_name}")
        print(f"  Nota: {note}")
        print(f"  Cantidad Original: {original_qty} unidades")
        print(f"  Factor: {factor}")
        print(f"  Convertido: {converted_kg}")
        print(f"  Esperado: {expected_kg}")
        if not is_correct:
            print(f"  DIFERENCIA: {converted_kg - expected_kg}")
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
