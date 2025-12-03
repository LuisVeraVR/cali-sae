#!/usr/bin/env python3
"""
Test script para verificar que las conversiones de unidad funcionen correctamente
"""
from decimal import Decimal
from datetime import datetime
from src.domain.entities.product import Product
from src.domain.entities.invoice import Invoice

def test_product_with_unit_codes():
    """Test que los productos preserven la unidad original"""

    print("=" * 80)
    print("TEST: Verificar que original_unit_code se preserve correctamente")
    print("=" * 80)
    print()

    # Test 1: Producto con P25
    product_p25 = Product(
        name="FRIJOL CALIMA*500G",
        underlying_code="SPN-1",
        unit_of_measure="P25",
        quantity=Decimal("55"),
        unit_price=Decimal("1000"),
        total_price=Decimal("55000"),
        iva_percentage=Decimal("0"),
        original_unit_code="P25"  # Unidad original
    )

    print("Test 1: FRIJOL CALIMA*500G con P25")
    print(f"  Nombre: {product_p25.name}")
    print(f"  Cantidad: {product_p25.quantity}")
    print(f"  Unidad Medida: {product_p25.unit_of_measure}")
    print(f"  Unidad Original: {product_p25.get_original_unit_code()}")
    print(f"  ¿Tiene original_unit_code? {product_p25.original_unit_code is not None}")
    print()

    # Test 2: Producto con UND
    product_und = Product(
        name="FRIJOL CALIMA*500G",
        underlying_code="SPN-1",
        unit_of_measure="UND",
        quantity=Decimal("15"),
        unit_price=Decimal("1000"),
        total_price=Decimal("15000"),
        iva_percentage=Decimal("0"),
        original_unit_code="UND"  # Unidad original
    )

    print("Test 2: FRIJOL CALIMA*500G con UND")
    print(f"  Nombre: {product_und.name}")
    print(f"  Cantidad: {product_und.quantity}")
    print(f"  Unidad Medida: {product_und.unit_of_measure}")
    print(f"  Unidad Original: {product_und.get_original_unit_code()}")
    print(f"  ¿Tiene original_unit_code? {product_und.original_unit_code is not None}")
    print()

    # Test 3: Crear una factura con estos productos
    invoice = Invoice(
        invoice_number="DP000123",
        issue_date=datetime.now(),
        due_date=datetime.now(),
        currency="COP",
        seller_nit="900691476",
        seller_name="DISTRIBUIDORA EL PAISANO SAS",
        seller_municipality="CALI",
        buyer_nit="123456789",
        buyer_name="CLIENTE TEST",
        xml_filename="test.pdf",
        zip_filename="",
        processed_at=datetime.now()
    )

    invoice.add_product(product_p25)
    invoice.add_product(product_und)

    print("Test 3: Factura con múltiples productos")
    print(f"  Número Factura: {invoice.invoice_number}")
    print(f"  Total Productos: {invoice.get_product_count()}")
    print()

    for idx, product in enumerate(invoice.products, 1):
        print(f"  Producto {idx}:")
        print(f"    Nombre: {product.name}")
        print(f"    Unidad Original: '{product.get_original_unit_code()}'")
        print(f"    Cantidad: {product.quantity}")
        print()

    print("=" * 80)
    print("✓ Tests completados")
    print("=" * 80)

if __name__ == "__main__":
    test_product_with_unit_codes()
