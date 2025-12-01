# Conversión de Productos a Kilos

Sistema robusto para convertir cantidades de productos a kilogramos usando una tabla de presentaciones.

## 📋 Descripción

Este módulo implementa un sistema inteligente de conversión que:

1. **Extrae gramos/cc** del nombre del producto (250G, 500G, 380GR, 900GR, 175G, 500CC, 3000CC, etc.)
2. **Busca la Presentación** en la tabla usando matching inteligente (maneja variaciones de orden y nombres)
3. **Calcula kilos** usando la fórmula: `kilos = (gramos * presentacion / 1000) * cantidad`

## 🎯 Características

### Matching Inteligente
- ✅ **Orden independiente**: "ACEITE 500CC" = "500CC ACEITE"
- ✅ **Normalización de unidades**: 380G = 380GR, 500ML = 500CC, 1KILO = 1KG
- ✅ **Flexible con marcas**: "ACEITE 500CC" matchea con "ACEITE SOYA 500CC LA ORLANDESA"
- ✅ **Maneja productos A GRANEL** correctamente
- ✅ **Productos con múltiples unidades**: "PANELA*125G*8UND" = 1000g

### Robustez
- Si el producto no está en la tabla, usa `Presentacion = 1`
- Maneja nombres con o sin asteriscos
- Maneja variaciones de unidades (G, GR, GRAMOS, KG, KILO, KILOS, CC, ML)

## 🚀 Uso

### 1. Importar el módulo

```python
from src.domain.services.product_converter import ProductConverter
```

### 2. Crear tabla de presentaciones

```python
PRESENTACIONES = {
    "ACEITE SOYA*500CC LA ORLANDESA E": 24,
    "ARROZ*500G": 25,
    "FRIJOL CALIMA AGRANEL": 50,
    "PASTA ZONIA*250G MACARRON": 24,
    # ... más productos
}
```

### 3. Crear converter

```python
converter = ProductConverter(PRESENTACIONES)
```

### 4. Convertir productos

#### Conversión simple

```python
kilos, info = converter.convert_to_kilos(
    product_name="ACEITE SOYA*500CC",
    cantidad=10
)

print(f"Kilos: {kilos}")
print(f"Fórmula: {info['formula']}")
print(f"Presentación: {info['presentacion']} ({info['presentacion_source']})")
```

**Salida:**
```
Kilos: 120.000
Fórmula: (500 * 24 / 1000) * 10 = 120.000 kg
Presentación: 24.0 (table)
```

#### Conversión con DataFrame (requiere pandas)

```python
import pandas as pd

df = pd.DataFrame({
    "SUBY": ["ACEITE SOYA*500CC", "ARROZ*500G", "FRIJOL CALIMA AGRANEL"],
    "Cantidad": [10, 5, 2]
})

df_resultado = converter.convert_dataframe(
    df,
    product_column="SUBY",
    cantidad_column="Cantidad",
    output_column="Kilos",
    add_info_columns=True  # Opcional: agregar columnas con detalles
)

print(df_resultado[["SUBY", "Cantidad", "Kilos"]])
```

#### Función rápida

```python
from src.domain.services.product_converter import convert_product_to_kilos

kilos = convert_product_to_kilos(
    product_name="ACEITE SOYA*500CC",
    cantidad=10,
    presentaciones=PRESENTACIONES
)
```

## 📊 Ejemplos

### Ejemplo 1: Diferentes órdenes

```python
# Todos estos son equivalentes:
converter.convert_to_kilos("ACEITE SOYA 500CC", 10)      # 120 kg
converter.convert_to_kilos("500CC ACEITE SOYA", 10)      # 120 kg
converter.convert_to_kilos("ACEITE 500CC", 10)           # 120 kg
```

### Ejemplo 2: Diferentes unidades

```python
# Todos se normalizan correctamente:
converter.convert_to_kilos("HARINA*500G", 1)    # 12 kg
converter.convert_to_kilos("HARINA*500GR", 1)   # 12 kg (GR → G)
converter.convert_to_kilos("ACEITE*500ML", 1)   # 12 kg (ML → CC)
converter.convert_to_kilos("ACEITE*500CC", 1)   # 12 kg
```

### Ejemplo 3: Productos especiales

```python
# Productos con KG
converter.convert_to_kilos("AZUCAR*50KG", 1)           # 2500 kg

# Productos con múltiples unidades
converter.convert_to_kilos("PANELA*125G*8UND", 1)     # 8 kg (125g × 8)

# Productos A GRANEL (sin gramos en el nombre)
converter.convert_to_kilos("ARROZ AGRANEL", 1)        # 50 kg
```

### Ejemplo 4: Producto no en tabla

```python
# Usa presentación = 1 por defecto
kilos, info = converter.convert_to_kilos("PRODUCTO NUEVO*500G", 1)
# kilos = (500 * 1 / 1000) * 1 = 0.5 kg
# info['presentacion_source'] = 'default'
```

## 📁 Estructura

```
src/domain/services/
└── product_converter.py          # Módulo principal

examples/
├── ejemplo_conversion_simple.py  # Ejemplos sin pandas
└── ejemplo_conversion_productos.py  # Ejemplos con pandas

docs/
└── CONVERSION_PRODUCTOS.md       # Esta documentación
```

## 🔧 Fórmula de Conversión

```
kilos = (gramos_extraidos * presentacion / 1000) * cantidad_factura
```

Donde:
- **gramos_extraidos**: Gramos o CC extraídos del nombre del producto
- **presentacion**: Valor de la tabla (unidades por caja/bulto) o 1 si no existe
- **cantidad_factura**: Cantidad de la línea de factura

### Casos especiales:

1. **Productos A GRANEL** (sin gramos): La presentación es el peso del bulto en kg
   ```
   kilos = presentacion * cantidad_factura
   ```

2. **Productos con KG en el nombre**: Se convierte a gramos (1KG = 1000g)
   ```
   "AZUCAR*50KG" → 50000 gramos
   ```

3. **Productos con múltiples unidades**: Se multiplican
   ```
   "PANELA*125G*8UND" → 125g × 8 = 1000g
   ```

## 🧪 Tests

Ejecutar ejemplos:

```bash
# Sin pandas
python examples/ejemplo_conversion_simple.py

# Con pandas (requiere pandas instalado)
python examples/ejemplo_conversion_productos.py
```

## ⚙️ Algoritmo de Matching

El sistema usa un algoritmo de matching inteligente que:

1. **Normaliza unidades**: GR→G, ML→CC, KILO→KG
2. **Extrae componentes**:
   - Palabras principales (ACEITE, FRIJOL, ARROZ, etc.)
   - Medidas (500G, 1KG, 250CC, etc.)
   - Modificadores (AGRANEL, BLANCA, LA ORLANDESA, etc.)
3. **Calcula score por componentes**:
   - 50% palabras principales
   - 40% medidas
   - 10% modificadores
4. **Requiere match ≥ 75%** para considerar válido

Esto permite que productos con nombres similares pero no idénticos se emparejen correctamente.

## 📝 Notas

- El módulo funciona sin pandas, pero `convert_dataframe()` requiere pandas instalado
- Los nombres de productos se normalizan automáticamente (mayúsculas, sin acentos)
- Las palabras comunes (DE, LA, EL, etc.) se eliminan para mejorar el matching
- El sistema es case-insensitive y maneja acentos automáticamente

## 🔄 Integración con El Paisano

Este módulo se integra con el sistema existente de El Paisano en:
- `src/domain/use_cases/process_paisano_invoices.py`

El `ProcessPaisanoInvoices` usa internamente el mismo algoritmo para convertir productos.
