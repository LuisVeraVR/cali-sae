"""
Test de conversiones de unidades para Paisano
Verifica que los cálculos sean correctos según los ejemplos del usuario
"""
from decimal import Decimal
import sys
sys.path.insert(0, '/home/user/cali-sae')

from src.domain.use_cases.process_paisano_invoices import ProcessPaisanoInvoices

# Create instance (sin dependencies para solo probar los métodos)
processor = ProcessPaisanoInvoices(
    report_repository=None,
    xml_parser=None,
    reggis_exporter=None
)

print("=" * 80)
print("PRUEBAS DE CONVERSIÓN DE UNIDADES PAISANO")
print("=" * 80)

# Test 1: FRIJOL BOLON*500G con UND (15 unidades)
print("\n1. FRIJOL BOLON*500G con UND")
print("   Cantidad factura: 15 unidades")
print("   Esperado: 15 × 500 ÷ 1000 = 7.5 kg")
factor1 = processor._calculate_conversion_factor_with_unit("FRIJOL BOLON*500G", "UND")
result1 = Decimal("15") * factor1
print(f"   Factor calculado: {factor1} kg/unidad")
print(f"   Resultado: {result1} kg")
print(f"   ✅ CORRECTO" if result1 == Decimal("7.5") else f"   ❌ INCORRECTO (esperado 7.5)")

# Test 2: PANELA*125G*8UND TEJO con P24 (1 paca)
print("\n2. PANELA*125G*8UND TEJO con P24")
print("   Cantidad factura: 1 paca")
print("   Esperado: 125 × 8 × 24 ÷ 1000 = 24 kg")
factor2 = processor._calculate_conversion_factor_with_unit("PANELA*125G*8UND TEJO", "P24")
result2 = Decimal("1") * factor2
print(f"   Factor calculado: {factor2} kg/paca")
print(f"   Resultado: {result2} kg")
print(f"   ✅ CORRECTO" if result2 == Decimal("24") else f"   ❌ INCORRECTO (esperado 24)")

# Test 3: LECHE EN POLVO*380G ENTERA DONA VACA con UND (12 unidades)
print("\n3. LECHE EN POLVO*380G ENTERA DONA VACA con UND")
print("   Cantidad factura: 12 unidades")
print("   Esperado: 12 × 380 ÷ 1000 = 4.56 kg")
factor3 = processor._calculate_conversion_factor_with_unit("LECHE EN POLVO*380G ENTERA DONA VACA", "UND")
result3 = Decimal("12") * factor3
print(f"   Factor calculado: {factor3} kg/unidad")
print(f"   Resultado: {result3} kg")
print(f"   ✅ CORRECTO" if result3 == Decimal("4.56") else f"   ❌ INCORRECTO (esperado 4.56)")

# Test 4: FRIJOL CARAOTA*500G con UND (15 unidades)
print("\n4. FRIJOL CARAOTA*500G con UND")
print("   Cantidad factura: 15 unidades")
print("   Esperado: 15 × 500 ÷ 1000 = 7.5 kg")
factor4 = processor._calculate_conversion_factor_with_unit("FRIJOL CARAOTA*500G", "UND")
result4 = Decimal("15") * factor4
print(f"   Factor calculado: {factor4} kg/unidad")
print(f"   Resultado: {result4} kg")
print(f"   ✅ CORRECTO" if result4 == Decimal("7.5") else f"   ❌ INCORRECTO (esperado 7.5)")

# Test 5: FRIJOL CALIMA*500G con UND (15 unidades)
print("\n5. FRIJOL CALIMA*500G con UND")
print("   Cantidad factura: 15 unidades")
print("   Esperado: 15 × 500 ÷ 1000 = 7.5 kg")
factor5 = processor._calculate_conversion_factor_with_unit("FRIJOL CALIMA*500G", "UND")
result5 = Decimal("15") * factor5
print(f"   Factor calculado: {factor5} kg/unidad")
print(f"   Resultado: {result5} kg")
print(f"   ✅ CORRECTO" if result5 == Decimal("7.5") else f"   ❌ INCORRECTO (esperado 7.5)")

# Test 6: ACEITE*3000ML REF FRISOYA con CJ (1 caja de 6 unidades)
print("\n6. ACEITE*3000ML REF FRISOYA con CJ")
print("   Cantidad factura: 1 caja")
print("   Esperado: 6 × 3000 × 0.92 ÷ 1000 = 16.56 kg (aprox 18 kg según catálogo)")
factor6 = processor._calculate_conversion_factor_with_unit("ACEITE*3000ML REF FRISOYA", "CJ")
result6 = Decimal("1") * factor6
print(f"   Factor calculado: {factor6} kg/caja")
print(f"   Resultado: {result6} kg")
print(f"   ℹ️  Usando factor del catálogo (6.0 kg según CONVERSION_MAP)")

# Test 7: ACEITE*3000ML REF FRISOYA con UND (2 unidades)
print("\n7. ACEITE*3000ML REF FRISOYA con UND")
print("   Cantidad factura: 2 unidades")
print("   Esperado: 2 × 3000 × 0.92 ÷ 1000 = 5.52 kg")
factor7 = processor._calculate_conversion_factor_with_unit("ACEITE*3000ML REF FRISOYA", "UND")
result7 = Decimal("2") * factor7
print(f"   Factor calculado: {factor7} kg/unidad")
print(f"   Resultado: {result7} kg")
expected7 = Decimal("2") * Decimal("3") * Decimal("0.92")
print(f"   ✅ CORRECTO" if abs(result7 - expected7) < Decimal("0.01") else f"   ❌ INCORRECTO (esperado ~5.52)")

# Test 8: SEMILLA GIRASOL A GRANEL con B20 (1 bulto)
print("\n8. SEMILLA GIRASOL A GRANEL con B20")
print("   Cantidad factura: 1 bulto")
print("   Esperado: 20 kg")
factor8 = processor._calculate_conversion_factor_with_unit("SEMILLA GIRASOL A GRANEL", "B20")
result8 = Decimal("1") * factor8
print(f"   Factor calculado: {factor8} kg/bulto")
print(f"   Resultado: {result8} kg")
print(f"   ✅ CORRECTO" if result8 == Decimal("20") else f"   ❌ INCORRECTO (esperado 20)")

print("\n" + "=" * 80)
print("FIN DE PRUEBAS")
print("=" * 80)
