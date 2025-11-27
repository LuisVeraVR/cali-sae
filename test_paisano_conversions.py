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

    # Test cases: (product_name, original_quantity, expected_kg)
    test_cases = [
        # Products with grams
        ("HARINA AREPA*500G BLANCA", Decimal("10"), Decimal("5.0")),  # 10 units × 0.5 kg = 5 kg
        ("FRIJOL CALIMA*250G", Decimal("12"), Decimal("3.0")),  # 12 units × 0.25 kg = 3 kg
        ("AZUCAR BLANCA*500G", Decimal("24"), Decimal("12.0")),  # 24 units × 0.5 kg = 12 kg
        ("PANELA*500GR", Decimal("48"), Decimal("24.0")),  # 48 units × 0.5 kg = 24 kg

        # Products with volume (CC)
        ("ACEITE SOYA*500CC LA ORLANDESA E", Decimal("24"), Decimal("11.04")),  # 24 × 0.46 kg ≈ 11.04 kg
        ("ACEITE SOYA*1000CC LA ORLANDESA E", Decimal("12"), Decimal("11.04")),  # 12 × 0.92 kg ≈ 11.04 kg
        ("ACEITE*3000CC", Decimal("6"), Decimal("16.56")),  # 6 × 2.76 kg ≈ 16.56 kg

        # Products a granel (sacks)
        ("ARROZ AGRANEL", Decimal("2"), Decimal("100.0")),  # 2 sacks × 50 kg = 100 kg
        ("FRIJOL CALIMA AGRANEL", Decimal("3"), Decimal("150.0")),  # 3 sacks × 50 kg = 150 kg
        ("LENTEJA A GRANEL", Decimal("1"), Decimal("50.0")),  # 1 sack × 50 kg = 50 kg

        # Products with KG in name
        ("AZUCAR BLANCA*50KG", Decimal("2"), Decimal("100.0")),  # 2 × 50 kg = 100 kg
        ("PANELA REDONDA*24KILOS", Decimal("1"), Decimal("24.0")),  # 1 × 24 kg = 24 kg

        # Products without conversion info (should stay as units)
        ("GALLETAS CRAKENAS CLUB IND 8*10", Decimal("10"), Decimal("10.0")),  # 10 units (no conversion)
    ]

    print("=" * 80)
    print("PRUEBA DE CONVERSIONES DE PRODUCTOS EL PAISANO")
    print("=" * 80)
    print()

    all_passed = True
    for product_name, original_qty, expected_kg in test_cases:
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
        print(f"  Cantidad Original: {original_qty} unidades")
        print(f"  Factor: {factor}")
        print(f"  Convertido: {converted_kg} kg")
        print(f"  Esperado: {expected_kg} kg")
        if not is_correct:
            print(f"  DIFERENCIA: {converted_kg - expected_kg} kg")
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
