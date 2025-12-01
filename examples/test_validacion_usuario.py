#!/usr/bin/env python3
"""
Test de validación con los ejemplos proporcionados por el usuario
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.services.product_converter import ProductConverter


def test_ejemplos_usuario():
    """
    Validar con los ejemplos exactos del usuario:
    - ALPISTE*450G = 450 * 25 / 1000 * 2 = 22.5
    - FRIJOL CALIMA*450G = 450 * 25 / 1000 * 6 = 67.5
    - HOJUELAS AZUCARADAS*40G = 40 * 80 / 1000 * 12 = 38.4
    - ARVEJA VERDE*450G = 450 * 25 / 1000 * (cantidad)
    """

    # Tabla de presentaciones por CATEGORÍA (sin tamaños específicos)
    presentaciones = {
        # Categorías generales
        "ALPISTE": 25,
        "FRIJOL CALIMA": 25,
        "ARVEJA VERDE": 25,
        "ARROZ": 25,
        "HARINA": 24,
        "PASTA": 24,
        "ATUN": 48,
        "ACEITE": 25,

        # Casos especiales con tamaño específico
        "HOJUELAS AZUCARADAS*40G": 80,  # Presentación específica para 40G
    }

    converter = ProductConverter(presentaciones)

    print("=" * 80)
    print("VALIDACIÓN CON EJEMPLOS DEL USUARIO")
    print("=" * 80)
    print()

    # Test 1: ALPISTE*450G con cantidad=2
    print("Test 1: ALPISTE*450G")
    print("-" * 80)
    kilos, info = converter.convert_to_kilos("ALPISTE*450G", cantidad=2)
    esperado = (450 * 25 / 1000) * 2  # 22.5
    print(f"  Producto: ALPISTE*450G")
    print(f"  Cantidad: 2")
    print(f"  Presentación encontrada: {info['presentacion']} ({info['presentacion_source']})")
    print(f"  Fórmula: {info['formula']}")
    print(f"  Resultado: {float(kilos):.1f} kg")
    print(f"  Esperado: {esperado:.1f} kg")
    print(f"  ✓ CORRECTO" if abs(float(kilos) - esperado) < 0.01 else f"  ✗ ERROR")
    print()

    # Test 2: FRIJOL CALIMA*450G con cantidad=6
    print("Test 2: FRIJOL CALIMA*450G")
    print("-" * 80)
    kilos, info = converter.convert_to_kilos("FRIJOL CALIMA*450G", cantidad=6)
    esperado = (450 * 25 / 1000) * 6  # 67.5
    print(f"  Producto: FRIJOL CALIMA*450G")
    print(f"  Cantidad: 6")
    print(f"  Presentación encontrada: {info['presentacion']} ({info['presentacion_source']})")
    print(f"  Fórmula: {info['formula']}")
    print(f"  Resultado: {float(kilos):.1f} kg")
    print(f"  Esperado: {esperado:.1f} kg")
    print(f"  ✓ CORRECTO" if abs(float(kilos) - esperado) < 0.01 else f"  ✗ ERROR")
    print()

    # Test 3: HOJUELAS AZUCARADAS*40G con cantidad=12
    print("Test 3: HOJUELAS AZUCARADAS*40G")
    print("-" * 80)
    kilos, info = converter.convert_to_kilos("HOJUELAS AZUCARADAS*40G", cantidad=12)
    esperado = (40 * 80 / 1000) * 12  # 38.4
    print(f"  Producto: HOJUELAS AZUCARADAS*40G")
    print(f"  Cantidad: 12")
    print(f"  Presentación encontrada: {info['presentacion']} ({info['presentacion_source']})")
    print(f"  Fórmula: {info['formula']}")
    print(f"  Resultado: {float(kilos):.1f} kg")
    print(f"  Esperado: {esperado:.1f} kg")
    print(f"  ✓ CORRECTO" if abs(float(kilos) - esperado) < 0.01 else f"  ✗ ERROR")
    print()

    # Test 4: ARVEJA VERDE*450G con cantidad=3
    print("Test 4: ARVEJA VERDE*450G")
    print("-" * 80)
    kilos, info = converter.convert_to_kilos("ARVEJA VERDE*450G", cantidad=3)
    esperado = (450 * 25 / 1000) * 3  # 33.75
    print(f"  Producto: ARVEJA VERDE*450G")
    print(f"  Cantidad: 3")
    print(f"  Presentación encontrada: {info['presentacion']} ({info['presentacion_source']})")
    print(f"  Fórmula: {info['formula']}")
    print(f"  Resultado: {float(kilos):.1f} kg")
    print(f"  Esperado: {esperado:.1f} kg")
    print(f"  ✓ CORRECTO" if abs(float(kilos) - esperado) < 0.01 else f"  ✗ ERROR")
    print()

    # Tests adicionales: Verificar que funciona con cualquier tamaño
    print("=" * 80)
    print("TESTS ADICIONALES: Diferentes tamaños del mismo producto")
    print("=" * 80)
    print()

    tamaños_test = [
        ("ALPISTE*250G", 1, 25),
        ("ALPISTE*450G", 1, 25),
        ("ALPISTE*500G", 1, 25),
        ("ALPISTE*1KG", 1, 25),
        ("FRIJOL CALIMA*250G", 1, 25),
        ("FRIJOL CALIMA*500G", 1, 25),
        ("FRIJOL CALIMA*750G", 1, 25),
    ]

    print(f"{'Producto':<30} {'Cantidad':>8} {'Presentación':>12} {'Kilos':>8}")
    print("-" * 80)
    for producto, cantidad, presentacion_esperada in tamaños_test:
        kilos, info = converter.convert_to_kilos(producto, cantidad)
        status = "✓" if info['presentacion'] == presentacion_esperada else "✗"
        print(f"{producto:<30} {cantidad:>8} {info['presentacion']:>12.0f} {float(kilos):>8.3f} {status}")

    print()
    print("=" * 80)
    print("✅ VALIDACIÓN COMPLETADA")
    print("=" * 80)


if __name__ == "__main__":
    test_ejemplos_usuario()
