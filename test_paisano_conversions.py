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
        # FRIJOLES con presentación específica en el catálogo
        # FRIJOL CALIMA*500G: Presentacion=25, gramos=500 → (25 × 500 / 1000) = 12.5 kg por caja
        ("FRIJOL CALIMA*500G", Decimal("55"), Decimal("687.5"), "Catálogo: 55 cajas × 12.5 kg/caja = 687.5 kg"),
        ("FRIJOL CALIMA 500G", Decimal("55"), Decimal("687.5"), "Catálogo: 55 cajas × 12.5 kg/caja = 687.5 kg"),

        # ACEITES - Products in CATALOG with Presentacion
        # ACEITE*500ML: Presentacion=24, volumen=500ml → (24 × 500 / 1000) = 12 kg por caja
        ("ACEITE SOYA*500CC LA ORLANDESA E", Decimal("1"), Decimal("12.0"), "Catálogo: 1 caja × 12 kg/caja = 12 kg"),
        ("ACEITE*500ML REF FRISOYA", Decimal("2"), Decimal("24.0"), "Catálogo: 2 cajas × 12 kg/caja = 24 kg"),

        # ACEITE*1000ML: Presentacion=12, volumen=1000ml → (12 × 1000 / 1000) = 12 kg por caja
        ("ACEITE*1000ML REF FRISOYA", Decimal("1"), Decimal("12.0"), "Catálogo: 1 caja × 12 kg/caja = 12 kg"),
        ("ACEITE SOYA*1000CC LA ORLANDESA E", Decimal("3"), Decimal("36.0"), "Catálogo: 3 cajas × 12 kg/caja = 36 kg"),

        # ACEITE*2000ML: Presentacion=6, volumen=2000ml → (6 × 2000 / 1000) = 12 kg por caja
        ("ACEITE*2000ML REF FRISOYA", Decimal("5"), Decimal("60.0"), "Catálogo: 5 cajas × 12 kg/caja = 60 kg"),

        # ACEITE*3000ML: Presentacion=6, volumen=3000ml → (6 × 3000 / 1000) = 18 kg por caja
        ("ACEITE SOYA*3000CC LA ORLANDESA", Decimal("2"), Decimal("36.0"), "Catálogo: 2 cajas × 18 kg/caja = 36 kg"),

        # SEMILLAS
        # SEMILLA GIRASOL*200G: Presentacion=12, gramos=200 → (12 × 200 / 1000) = 2.4 kg por caja
        ("SEMILLA GIRASOL*200G", Decimal("5"), Decimal("12.0"), "Catálogo: 5 cajas × 2.4 kg/caja = 12 kg"),
        # SEMILLA GIRASOL AGRANEL: A GRANEL = 20 kg por bulto
        ("SEMILLA GIRASOL AGRANEL", Decimal("1"), Decimal("20.0"), "Catálogo: 1 bulto × 20 kg/bulto = 20 kg"),

        # LECHE EN POLVO
        # LECHE*380G: Presentacion=12, gramos=380 → (12 × 380 / 1000) = 4.56 kg por caja
        ("LECHE EN POLVO*380G ENTERA DONA VACA", Decimal("10"), Decimal("45.6"), "Catálogo: 10 cajas × 4.56 kg/caja = 45.6 kg"),
        # LECHE*900G: Presentacion=12, gramos=900 → (12 × 900 / 1000) = 10.8 kg por caja
        ("LECHE EN POLVO*900GR ENTERA NUTRALAC", Decimal("5"), Decimal("54.0"), "Catálogo: 5 cajas × 10.8 kg/caja = 54 kg"),

        # HOJUELAS AZUCARADAS
        # HOJUELAS*40G: Presentacion=80, gramos=40 → (80 × 40 / 1000) = 3.2 kg por caja
        ("HOJUELAS AZUCARADAS*40G", Decimal("10"), Decimal("32.0"), "Catálogo: 10 cajas × 3.2 kg/caja = 32 kg"),

        # AZUCAR
        # AZUCAR*1KG: Presentacion=25, gramos=1000 → (25 × 1000 / 1000) = 25 kg por paca
        ("AZUCAR BLANCO*1KG PROVIDENCIA", Decimal("3"), Decimal("75.0"), "Catálogo: 3 pacas × 25 kg/paca = 75 kg"),

        # PANELA TEJO
        # PANELA*125G*8UND: Presentacion=24, 8 tejos × 125g = 1000g → (24 × 1000 / 1000) = 24 kg por caja
        ("PANELA*125G*8UND TEJO", Decimal("2"), Decimal("48.0"), "Catálogo: 2 cajas × 24 kg/caja = 48 kg"),

        # Products A GRANEL (peso directo en kg)
        ("ARROZ AGRANEL", Decimal("2"), Decimal("100.0"), "A GRANEL: 2 bultos × 50 kg/bulto = 100 kg"),
        ("ARROZ A GRANEL", Decimal("2"), Decimal("100.0"), "A GRANEL: 2 bultos × 50 kg/bulto = 100 kg"),
        ("FRIJOL CALIMA AGRANEL", Decimal("3"), Decimal("150.0"), "A GRANEL: 3 sacos × 50 kg/saco = 150 kg"),
        ("LENTEJA A GRANEL", Decimal("1"), Decimal("50.0"), "A GRANEL: 1 saco × 50 kg/saco = 50 kg"),
        ("CEBADA PERLADA A GRANEL CON IVA", Decimal("2"), Decimal("100.0"), "A GRANEL: 2 bultos × 50 kg/bulto = 100 kg"),

        # Products NOT in catalog (Presentacion=1, automatic extraction)
        ("HARINA AREPA*500G BLANCA", Decimal("10"), Decimal("5.0"), "Auto: 10 unidades × 0.5 kg = 5 kg"),
        ("FRIJOL NUEVO*250G", Decimal("12"), Decimal("3.0"), "Auto: 12 unidades × 0.25 kg = 3 kg"),
        ("PRODUCTO NUEVO*500G", Decimal("10"), Decimal("5.0"), "Auto: 10 unidades × 0.5 kg = 5 kg"),
        ("ACEITE NUEVO*500CC", Decimal("24"), Decimal("12.0"), "Auto: 24 unidades × 0.5 kg = 12 kg"),

        # Products with KG in name
        ("AZUCAR BLANCA*50KG", Decimal("2"), Decimal("100.0"), "Auto: 2 unidades × 50 kg = 100 kg"),
        ("PANELA REDONDA*24KILOS", Decimal("1"), Decimal("24.0"), "Auto: 1 unidad × 24 kg = 24 kg"),

        # Products without conversion info (should stay as units)
        ("GALLETAS CRAKENAS CLUB IND 8*10", Decimal("10"), Decimal("10.0"), "Catálogo: 10 unidades × 1 = 10 unidades"),
        ("TOALLA COCINA BCO NUBE", Decimal("5"), Decimal("5.0"), "Catálogo: 5 unidades × 1 = 5 unidades"),
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
