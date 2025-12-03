#!/usr/bin/env python3
"""
Test para verificar cálculos de conversión según unidad de medida
"""
from decimal import Decimal
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from domain.use_cases.process_paisano_invoices import ProcessPaisanoInvoices

def test_conversions():
    """Test conversion calculations for different unit types"""

    print("=" * 80)
    print("TEST: Conversiones por Unidad de Medida")
    print("=" * 80)
    print()

    # Create a minimal processor instance
    processor = ProcessPaisanoInvoices(
        report_repository=None,
        xml_parser=None,
        reggis_exporter=None,
        conversion_repository=None,
        pdf_parser=None
    )

    test_cases = [
        # (product_name, unit_code, expected_factor, description)
        ("FRIJOL CALIMA*500G", "P25", Decimal("12.5"), "P25: 25 × 500 ÷ 1000 = 12.5 kg/paca"),
        ("FRIJOL CALIMA*250G", "P25", Decimal("6.25"), "P25: 25 × 250 ÷ 1000 = 6.25 kg/paca"),
        ("FRIJOL CALIMA*500G", "UND", Decimal("7.5"), "UND: Factor del catálogo = 7.5 kg/und"),
        ("ACEITE*500CC", "P25", Decimal("12.5"), "P25: 25 × 500 ÷ 1000 = 12.5 kg/paca"),
        ("ACEITE*500CC", "P20", Decimal("10.0"), "P20: 20 × 500 ÷ 1000 = 10.0 kg/paca"),
        ("ARROZ*500G", "P25", Decimal("12.5"), "P25: 25 × 500 ÷ 1000 = 12.5 kg/paca"),
    ]

    all_passed = True
    for product_name, unit_code, expected_factor, description in test_cases:
        # Calculate factor
        factor = processor._calculate_conversion_factor_with_unit(product_name, unit_code)

        # Check if correct
        is_correct = abs(factor - expected_factor) < Decimal("0.01")
        status = "✓ PASS" if is_correct else "✗ FAIL"

        if not is_correct:
            all_passed = False

        print(f"{status}")
        print(f"  Producto: {product_name}")
        print(f"  Unidad: {unit_code}")
        print(f"  Descripción: {description}")
        print(f"  Factor calculado: {factor}")
        print(f"  Factor esperado: {expected_factor}")
        if not is_correct:
            print(f"  DIFERENCIA: {factor - expected_factor}")
        print()

    # Now test full conversion with quantities
    print("=" * 80)
    print("TEST: Conversión Completa (factor × cantidad)")
    print("=" * 80)
    print()

    full_test_cases = [
        # (product_name, unit_code, quantity, expected_kg)
        ("FRIJOL CALIMA*500G", "P25", Decimal("55"), Decimal("687.5")),  # 12.5 × 55 = 687.5
        ("FRIJOL CALIMA*500G", "UND", Decimal("15"), Decimal("112.5")),  # 7.5 × 15 = 112.5
        ("FRIJOL CALIMA*250G", "P25", Decimal("15"), Decimal("93.75")),  # 6.25 × 15 = 93.75
    ]

    for product_name, unit_code, quantity, expected_kg in full_test_cases:
        # Calculate factor
        factor = processor._calculate_conversion_factor_with_unit(product_name, unit_code)

        # Calculate total kg
        total_kg = factor * quantity

        # Check if correct
        is_correct = abs(total_kg - expected_kg) < Decimal("0.01")
        status = "✓ PASS" if is_correct else "✗ FAIL"

        if not is_correct:
            all_passed = False

        print(f"{status}")
        print(f"  Producto: {product_name}")
        print(f"  Unidad: {unit_code}")
        print(f"  Cantidad: {quantity}")
        print(f"  Factor: {factor}")
        print(f"  Total Kg calculado: {total_kg}")
        print(f"  Total Kg esperado: {expected_kg}")
        if not is_correct:
            print(f"  DIFERENCIA: {total_kg - expected_kg}")
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
