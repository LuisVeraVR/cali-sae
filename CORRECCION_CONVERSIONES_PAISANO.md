# Corrección de Conversiones - El Paisano

## Problema Identificado

Las conversiones de productos de El Paisano no se estaban calculando correctamente porque:

1. **Factores mal definidos**: Los factores en el catálogo (24, 25, 48, 50) representaban el número de unidades por bulto/caja, NO el peso en kilogramos por unidad.

2. **Fórmula incorrecta**: Se multiplicaba la cantidad por el factor sin considerar el peso real de cada unidad individual.

## Solución Implementada

### Nueva Lógica de Conversión

La nueva lógica extrae automáticamente el peso o volumen del nombre del producto y calcula la conversión correcta:

#### 1. Productos con Gramos (500G, 250G, 1KG, etc.)

**Fórmula**: `kg = unidades × (gramos / 1000)`

**Ejemplos**:
- 10 unidades de **HARINA AREPA\*500G** → 10 × 0.5 = **5 kg**
- 12 unidades de **FRIJOL CALIMA\*250G** → 12 × 0.25 = **3 kg**
- 48 unidades de **PANELA\*500GR** → 48 × 0.5 = **24 kg**
- 1 unidad de **PANELA REDONDA\*24KILOS** → 1 × 24 = **24 kg**

**Patrones reconocidos**: G, GR, GRAMOS, KG, KILO, KILOS

#### 2. Productos con Volumen en CC (500CC, 1000CC, etc.)

**Fórmula**: `kg = unidades × (cc / 1000) × densidad`

**Densidad del aceite**: 0.92 g/ml

**Ejemplos**:
- 24 unidades de **ACEITE SOYA\*500CC** → 24 × 0.46 = **11.04 kg**
- 12 unidades de **ACEITE\*1000CC** → 12 × 0.92 = **11.04 kg**
- 6 unidades de **ACEITE\*3000CC** → 6 × 2.76 = **16.56 kg**

#### 3. Productos A Granel (Sacos de 50 kg)

**Fórmula**: `kg = sacos × factor_catálogo`

**Factor estándar**: 50 kg por saco

**Ejemplos**:
- 2 sacos de **ARROZ AGRANEL** → 2 × 50 = **100 kg**
- 3 sacos de **FRIJOL CALIMA AGRANEL** → 3 × 50 = **150 kg**
- 1 saco de **LENTEJA A GRANEL** → 1 × 50 = **50 kg**

#### 4. Productos sin Información de Conversión

Para productos que no tienen gramos, volumen, ni están a granel (como galletas, productos especiales), se mantienen en unidades sin conversión (factor = 1).

## Cambios en el Código

### Archivo: `src/domain/use_cases/process_paisano_invoices.py`

#### Nuevas Funciones

1. **`_extract_grams_from_name()`**: Extrae gramos del nombre del producto
   - Reconoce: 500G, 250GR, 1KG, 24KILOS, etc.

2. **`_extract_volume_cc_from_name()`**: Extrae volumen en CC del nombre
   - Reconoce: 500CC, 1000CC, 3000CC, etc.

3. **`_calculate_conversion_factor()`**: Calcula el factor de conversión correcto
   - Prioridad: gramos → volumen → granel → sin conversión
   - Retorna el peso en kg por unidad

#### Modificación en la Lógica de Conversión

**Antes**:
```python
normalized_tokens = self._normalize_tokens(product.name)
factor = self._match_factor(normalized_tokens)
converted_qty = original_qty * factor
```

**Después**:
```python
factor = self._calculate_conversion_factor(product.name)
converted_qty = original_qty * factor
```

## Validación

Se creó un script de pruebas (`test_paisano_conversions.py`) que valida 13 casos de conversión diferentes:

- ✓ 10 productos con gramos
- ✓ 3 productos con volumen (CC)
- ✓ 3 productos a granel
- ✓ 2 productos con KG/KILOS en el nombre
- ✓ 1 producto sin conversión

**Resultado**: ✓ TODAS LAS PRUEBAS PASARON

## Impacto

### Correcciones Principales

1. **Productos de 500G**: Ahora se convierten correctamente
   - Antes: 10 unidades × 24 = 240 kg ❌
   - Ahora: 10 unidades × 0.5 = 5 kg ✓

2. **Aceites**: Ahora usan densidad real
   - Antes: 24 unidades × 24 = 576 kg ❌
   - Ahora: 24 unidades × 0.46 = 11.04 kg ✓

3. **Productos a granel**: Se mantienen correctos
   - 2 sacos × 50 = 100 kg ✓

### Recálculo del Precio Unitario

El precio unitario se recalcula automáticamente después de la conversión:

```python
if converted_qty > 0:
    product.unit_price = product.total_price / converted_qty
```

Esto garantiza que:
- **Precio Total** se mantiene igual (correcto)
- **Precio Unitario** ahora refleja el precio por kg (correcto)
- **Cantidad Original** se preserva en el campo separado

## Ejecución de Pruebas

Para ejecutar las pruebas de conversión:

```bash
python test_paisano_conversions.py
```

Esto mostrará:
- ✓ Productos probados
- ✓ Factores calculados
- ✓ Conversiones esperadas vs obtenidas
- ✓ Estado de las pruebas (PASS/FAIL)

## Próximos Pasos

1. **Validar con datos reales**: Procesar facturas reales de El Paisano y verificar que las conversiones sean correctas
2. **Ajustar densidades**: Si hay otros líquidos además de aceite, agregar densidades específicas
3. **Productos especiales**: Identificar productos que necesiten conversiones específicas y agregarlos al catálogo

## Resumen

✅ **Problema resuelto**: Las conversiones ahora se basan en el peso real de cada producto extraído de su nombre

✅ **Precisión mejorada**: Los factores ahora representan kg por unidad, no unidades por bulto

✅ **Compatibilidad**: Los productos a granel siguen usando el catálogo de factores

✅ **Validado**: Todas las pruebas pasan correctamente

✅ **Committed**: Cambios guardados en el repositorio con mensaje descriptivo
