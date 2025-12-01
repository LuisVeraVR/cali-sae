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
        # Products with GRAMS (should use automatic extraction: kg = units × grams/1000)
        ("HARINA AREPA*500G BLANCA", Decimal("10"), Decimal("5.0"), "Auto: 10 × 0.5 kg = 5 kg"),
        ("FRIJOL CALIMA*500G", Decimal("55"), Decimal("27.5"), "Auto: 55 × 0.5 kg = 27.5 kg"),
        ("FRIJOL CALIMA*250G", Decimal("12"), Decimal("3.0"), "Auto: 12 × 0.25 kg = 3 kg"),
        ("AZUCAR BLANCA*500G", Decimal("24"), Decimal("12.0"), "Auto: 24 × 0.5 kg = 12 kg"),
        ("PANELA*500GR", Decimal("48"), Decimal("24.0"), "Auto: 48 × 0.5 kg = 24 kg"),
        ("AZUCAR BLANCA*50KG", Decimal("2"), Decimal("100.0"), "Auto: 2 × 50 kg = 100 kg"),
        ("PANELA REDONDA*24KILOS", Decimal("1"), Decimal("24.0"), "Auto: 1 × 24 kg = 24 kg"),

        # ACEITES - Products in CATALOG (density 1.0 kg/litro)
        ("ACEITE SOYA*500CC LA ORLANDESA E", Decimal("24"), Decimal("12.0"), "Catálogo: 24 × 0.5 kg = 12 kg"),
        ("ACEITE SOYA*1000CC LA ORLANDESA E", Decimal("12"), Decimal("12.0"), "Catálogo: 12 × 1 kg = 12 kg"),
        ("ACEITE SOYA*3000CC LA ORLANDESA", Decimal("6"), Decimal("18.0"), "Catálogo: 6 × 3 kg = 18 kg"),
        ("ACEITE*1000ML REF FRISOYA", Decimal("12"), Decimal("12.0"), "Catálogo: 12 × 1 kg = 12 kg"),
        ("ACEITE*2000ML REF FRISOYA", Decimal("6"), Decimal("12.0"), "Catálogo: 6 × 2 kg = 12 kg"),

        # SEMILLAS
        ("SEMILLA GIRASOL*200G", Decimal("12"), Decimal("2.4"), "Catálogo: 12 × 0.2 kg = 2.4 kg"),
        ("SEMILLA GIRASOL AGRANEL", Decimal("1"), Decimal("20.0"), "Catálogo: 1 × 20 kg/bulto = 20 kg"),

        # LECHE EN POLVO
        ("LECHE EN POLVO*380G ENTERA DONA VACA", Decimal("12"), Decimal("4.56"), "Catálogo: 12 × 0.38 kg = 4.56 kg"),
        ("LECHE EN POLVO*900GR ENTERA NUTRALAC", Decimal("12"), Decimal("10.8"), "Catálogo: 12 × 0.9 kg = 10.8 kg"),

        # HOJUELAS
        ("HOJUELAS AZUCARADAS*40G", Decimal("80"), Decimal("3.2"), "Catálogo: 80 × 0.04 kg = 3.2 kg"),

        # AZUCAR
        ("AZUCAR BLANCO*1KG PROVIDENCIA", Decimal("25"), Decimal("25.0"), "Catálogo: 25 × 1 kg = 25 kg"),

        # PANELA TEJO
        ("PANELA*125G*8UND TEJO", Decimal("24"), Decimal("24.0"), "Catálogo: 24 × 1 kg = 24 kg"),

        # Products A GRANEL (should use catalog factor 50 kg per sack)
        ("ARROZ AGRANEL", Decimal("2"), Decimal("100.0"), "Catálogo: 2 × 50 kg/saco = 100 kg"),
        ("ARROZ A GRANEL", Decimal("2"), Decimal("100.0"), "Catálogo: 2 × 50 kg/saco = 100 kg"),
        ("FRIJOL CALIMA AGRANEL", Decimal("3"), Decimal("150.0"), "Catálogo: 3 × 50 kg/saco = 150 kg"),
        ("LENTEJA A GRANEL", Decimal("1"), Decimal("50.0"), "Catálogo: 1 × 50 kg/saco = 50 kg"),
        ("CEBADA PERLADA A GRANEL CON IVA", Decimal("2"), Decimal("100.0"), "Catálogo: 2 × 50 kg/bulto = 100 kg"),

        # Products NOT in catalog (should use automatic extraction with density 1.0)
        ("PRODUCTO NUEVO*500G", Decimal("10"), Decimal("5.0"), "Auto: 10 × 0.5 kg = 5 kg"),
        ("ACEITE NUEVO*500CC", Decimal("24"), Decimal("12.0"), "Auto: 24 × 0.5 kg = 12 kg (densidad 1.0)"),

        # Products without conversion info (should stay as units)
        ("GALLETAS CRAKENAS CLUB IND 8*10", Decimal("10"), Decimal("10.0"), "Catálogo: 10 × 1 = 10 unidades"),
        ("TOALLA COCINA BCO NUBE", Decimal("5"), Decimal("5.0"), "Catálogo: 5 × 1 = 5 unidades"),
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
