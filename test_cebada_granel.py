#!/usr/bin/env python3
"""
Test específico para CEBADA PERLADA A GRANEL CON IVA
"""
import re
from decimal import Decimal
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from domain.use_cases.process_paisano_invoices import ProcessPaisanoInvoices

def test_cebada_granel():
    """Test para CEBADA PERLADA A GRANEL CON IVA"""

    print("=" * 80)
    print("TEST: CEBADA PERLADA A GRANEL CON IVA")
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

    # Test 1: Verificar que se detecta como producto A GRANEL
    product_name = "CEBADA PERLADA A GRANEL CON IVA"
    is_bulk = processor._is_bulk_product(product_name)

    print(f"Test 1: ¿Se detecta como A GRANEL?")
    print(f"  Producto: {product_name}")
    print(f"  Es A GRANEL: {'✓ SÍ' if is_bulk else '✗ NO'}")
    print()

    # Test 2: Factor de conversión
    factor = processor._calculate_conversion_factor(product_name)
    expected_factor = Decimal("50.0")  # Productos A GRANEL = 50 kg

    is_correct = abs(factor - expected_factor) < Decimal("0.01")
    status = "✓ PASS" if is_correct else "✗ FAIL"

    print(f"Test 2: Factor de conversión")
    print(f"  {status}")
    print(f"  Factor calculado: {factor}")
    print(f"  Factor esperado: {expected_factor}")
    print()

    # Test 3: Con unidad específica
    unit_codes = ["UND", "P25", "KG", "BL"]  # Posibles unidades para A GRANEL

    print(f"Test 3: Conversión con diferentes unidades")
    for unit_code in unit_codes:
        factor_with_unit = processor._calculate_conversion_factor_with_unit(
            product_name,
            unit_code
        )
        print(f"  Con {unit_code}: {factor_with_unit} kg")
    print()

    # Test 4: Verificar que el regex puede capturar líneas con este producto
    print("Test 4: Patrones regex")
    print()

    # Simular diferentes formatos de línea que podría tener en el PDF
    test_lines = [
        "|001 000046 CEBADA PERLADA A GRANEL CON IVA 01 2 BL 25,000.00 0.00 50,000.00 5.00*|",
        "|001 000046 CEBADA PERLADA A GRANEL CON IVA 01 2 UND 25,000.00 0.00 50,000.00 5.00*|",
        "001 000046 CEBADA PERLADA A GRANEL CON IVA 01 2 BL 25,000.00 0.00 50,000.00 5.00*",
        "|001 000046 CEBADA PERLADA A GRANEL CON IVA 01 2 KG 25,000.00 0.00 50,000.00 5.00*|",
    ]

    # Pattern similar al del parser
    pattern = re.compile(
        r'\|?(\d{3})\s+(\d{6})\s+(.+?)\s+\d{2}\s+(\d+)\s+([A-Z0-9]+)\s+([\d,\.]+)\s+[\d,\.]+\s+([\d,\.]+)\s+([\d\.]+)\*?\|?'
    )

    for i, line in enumerate(test_lines, 1):
        match = pattern.search(line)
        if match:
            product_desc = match.group(3).strip()
            unit = match.group(5)
            qty = match.group(4)
            print(f"  Línea {i}: ✓ CAPTURADO")
            print(f"    Producto: {product_desc}")
            print(f"    Unidad: {unit}")
            print(f"    Cantidad: {qty}")
        else:
            print(f"  Línea {i}: ✗ NO CAPTURADO")
            print(f"    {line}")
        print()

    # Test 5: Variaciones del nombre
    print("Test 5: Variaciones del nombre que deberían detectarse")
    variations = [
        "CEBADA PERLADA A GRANEL CON IVA",
        "CEBADA PERLADA AGRANEL CON IVA",
        "CEBADA PERLADA A GRANEL",
        "CEBADA A GRANEL",
    ]

    for variation in variations:
        is_bulk = processor._is_bulk_product(variation)
        factor = processor._calculate_conversion_factor(variation)
        print(f"  '{variation}'")
        print(f"    A GRANEL: {'✓' if is_bulk else '✗'}, Factor: {factor}")
    print()

    print("=" * 80)
    print("✓ Tests completados")
    print("=" * 80)

if __name__ == "__main__":
    test_cebada_granel()
