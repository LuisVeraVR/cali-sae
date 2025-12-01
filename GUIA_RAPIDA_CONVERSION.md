# 🚀 Guía Rápida: Conversión de Productos a Kilos

## Uso Básico

### 1. Importar y crear converter

```python
from src.domain.services.product_converter import ProductConverter

# Tu tabla de presentaciones (del Excel)
presentaciones = {
    "ACEITE SOYA*500CC LA ORLANDESA E": 24,
    "ARVEJA VERDE*500G": 25,
    "ARROZ*500G": 25,
    "FRIJOL CALIMA*500G": 25,
    "FRIJOL CALIMA AGRANEL": 50,
    "PASTA ZONIA*250G MACARRON": 24,
    "HARINA AREPA*500G BLANCA": 24,
    "LECHE EN POLVO*900GR ENTERA NUTRALAC": 13,
    # ... más productos
}

# Crear converter
converter = ProductConverter(presentaciones)
```

### 2. Convertir un producto

```python
# Ejemplo: ACEITE SOYA*500CC, cantidad = 10
kilos, info = converter.convert_to_kilos("ACEITE SOYA*500CC", cantidad=10)

print(f"Kilos: {kilos}")              # 120.0
print(f"Fórmula: {info['formula']}")  # (500 * 24 / 1000) * 10 = 120.000 kg
```

### 3. Convertir DataFrame (facturas completas)

```python
import pandas as pd

# Tu DataFrame de facturas
df = pd.DataFrame({
    "SUBY": [
        "ACEITE SOYA*500CC LA ORLANDESA E",
        "ARROZ*500G",
        "FRIJOL CALIMA AGRANEL"
    ],
    "Cantidad": [10, 5, 2],
    "PrecioUnitario": [15000, 3000, 150000]
})

# Convertir todo el DataFrame
df = converter.convert_dataframe(df)

# Calcular precio por kilo
df["PrecioXKilo"] = df["PrecioUnitario"] / df["Kilos"]

print(df[["SUBY", "Cantidad", "Kilos", "PrecioXKilo"]])
```

## ✨ Ventajas

### 1. Maneja variaciones de nombres

```python
# Todos estos dan el mismo resultado (120 kg):
converter.convert_to_kilos("ACEITE 500CC", 10)
converter.convert_to_kilos("500CC ACEITE", 10)
converter.convert_to_kilos("ACEITE SOYA 500CC", 10)
```

### 2. Normaliza unidades automáticamente

```python
# Estos son equivalentes:
converter.convert_to_kilos("HARINA*500G", 1)   # G
converter.convert_to_kilos("HARINA*500GR", 1)  # GR → G
converter.convert_to_kilos("ACEITE*500ML", 1)  # ML → CC
converter.convert_to_kilos("ACEITE*500CC", 1)  # CC
```

### 3. Productos sin match usan presentación = 1

```python
# Producto no en tabla
kilos, info = converter.convert_to_kilos("PRODUCTO NUEVO*500G", 1)
# kilos = (500 * 1 / 1000) * 1 = 0.5 kg
# info['presentacion_source'] = 'default'
```

## 📋 Fórmula

```
kilos = (gramos_extraidos * presentacion / 1000) * cantidad_factura
```

Donde:
- **gramos_extraidos**: Se extrae del nombre (500G, 250G, 1KG, 500CC, etc.)
- **presentacion**: Se busca en la tabla usando matching inteligente
- **cantidad_factura**: La cantidad de la línea de factura

## 🎯 Casos Especiales

```python
# Productos A GRANEL (sin gramos en nombre)
converter.convert_to_kilos("ARROZ AGRANEL", 1)  # 50 kg

# Productos con KG
converter.convert_to_kilos("AZUCAR*50KG", 1)  # 2500 kg

# Productos con múltiples unidades
converter.convert_to_kilos("PANELA*125G*8UND", 1)  # 8 kg (125g × 8)
```

## 📝 Información Detallada

```python
kilos, info = converter.convert_to_kilos("ACEITE 500CC", 10)

# info contiene:
{
    'gramos_extraidos': 500,
    'presentacion': 24.0,
    'presentacion_source': 'table',  # o 'default'
    'formula': '(500 * 24 / 1000) * 10 = 120.000 kg'
}
```

## 🏃 Ejecutar Ejemplos

```bash
# Ver ejemplos completos
python examples/ejemplo_conversion_simple.py

# Ver todos los casos de prueba
python examples/ejemplo_conversion_productos.py  # (requiere pandas)
```

## 📚 Documentación Completa

Ver: `docs/CONVERSION_PRODUCTOS.md`
