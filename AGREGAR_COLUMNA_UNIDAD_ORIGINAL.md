# Cómo Agregar la Columna "Unidad Original" al Excel

## Resumen
La nueva funcionalidad agrega una columna **"Unidad Original"** que muestra la unidad de medida tal como viene en la factura original (UND, P25, CJ, etc.), permitiendo distinguir entre diferentes tipos de empaques.

## Conversiones por Unidad

### Pacas (P25, P20, P12, etc.)
**Fórmula**: `(número_paca × gramos ÷ 1000) × cantidad`

**Ejemplos**:
- FRIJOL CALIMA*500G con P25:
  - Factor: 25 × 500 ÷ 1000 = **12.5 kg/paca**
  - 55 pacas × 12.5 = **687.5 kg**

- FRIJOL CALIMA*250G con P25:
  - Factor: 25 × 250 ÷ 1000 = **6.25 kg/paca**
  - 15 pacas × 6.25 = **93.75 kg**

### Unidades (UND)
**Fórmula**: Usa el factor del catálogo hardcodeado

**Ejemplo**:
- FRIJOL CALIMA*500G con UND:
  - Factor del catálogo: **7.5 kg/und**
  - 15 und × 7.5 = **112.5 kg**

### Cajas (CJ24, CJ12, etc.)
**Fórmula**: `(número_caja × gramos ÷ 1000) × cantidad`

**Ejemplo**:
- ACEITE*500CC con CJ24:
  - Factor: 24 × 500 ÷ 1000 = **12 kg/caja**

## Pasos para Agregar la Columna al Excel

### Opción 1: Agregar Manualmente a tu Plantilla Excel

1. **Abre tu archivo Excel de plantilla** (el que usas para exportar facturas)

2. **Localiza la columna "Unidad Medida"** (generalmente columna D o E)

3. **Inserta una nueva columna después de "Unidad Medida"**:
   - Click derecho en la siguiente columna
   - Selecciona "Insertar columna"

4. **Nombra la nueva columna "Unidad Original"** en la fila 1

5. **Guarda el archivo**

### Opción 2: Verificar que el Sistema la Cree Automáticamente

El Excel Exporter está configurado para reconocer cualquiera de estos nombres de columna:
- `Unidad Original`
- `Unit Original`
- `Original Unit`

Si tu plantilla tiene alguno de estos nombres, el sistema escribirá automáticamente en esa columna.

## Resultado Esperado en el Excel

| Nombre Producto | Unidad Medida | **Unidad Original** | Cantidad | Cantidad Original |
|----------------|---------------|---------------------|----------|-------------------|
| FRIJOL CALIMA*500G | Kg | **P25** | 687,5 | 55 |
| FRIJOL CALIMA*500G | Kg | **UND** | 112,5 | 15 |
| FRIJOL CALIMA*250G | Kg | **P25** | 93,75 | 15 |
| ACEITE*500CC | Kg | **P25** | 687,5 | 55 |

## Verificación

### Debug Logging
Al procesar facturas, verás mensajes como:
```
[CONVERSION] FRIJOL CALIMA*500G con P25: P25 × 500g ÷ 1000 = 12.5 kg
[CONVERSION] FRIJOL CALIMA*500G con UND: Factor del catálogo = 7.5 kg
```

### Tests
Ejecuta los tests de validación:
```bash
python test_conversion_calculation.py
```

Deberías ver:
```
✓ PASS - FRIJOL CALIMA*500G con P25: 55 × 12.5 = 687.5 kg
✓ PASS - FRIJOL CALIMA*500G con UND: 15 × 7.5 = 112.5 kg
✓ PASS - FRIJOL CALIMA*250G con P25: 15 × 6.25 = 93.75 kg
```

## Troubleshooting

### La columna "Unidad Original" está vacía
- **Causa**: El parser no está extrayendo la unidad correctamente
- **Solución**: Verifica que el PDF tenga la unidad en el formato esperado (P25, UND, CJ, etc.)
- **Debug**: Activa el logging del parser v2 para ver qué se está extrayendo

### Las conversiones no coinciden
- **Causa**: El factor de conversión no se calcula correctamente
- **Solución**: Verifica el logging `[CONVERSION]` para ver qué factor se está usando
- **Verifica**:
  - Que el producto tenga gramos en el nombre (ej: *500G)
  - Que la unidad sea reconocida (P25, P20, UND, etc.)

### La columna no aparece en el Excel final
- **Causa**: Tu plantilla Excel no tiene la columna "Unidad Original"
- **Solución**: Agrega manualmente la columna siguiendo la Opción 1

## Soporte

Si encuentras problemas:
1. Ejecuta `python test_conversion_calculation.py` para verificar conversiones
2. Revisa los logs `[DEBUG]` y `[CONVERSION]` durante el procesamiento
3. Verifica que tu plantilla Excel tenga la columna "Unidad Original"
