# 📚 Cómo Definir Presentaciones Correctamente

## 🎯 Concepto Clave

Las **presentaciones** se definen por **TIPO DE PRODUCTO**, no por tamaño específico.

- Los **gramos/cc** se extraen del nombre de la factura
- La **presentación** se busca por categoría de producto
- La **fórmula** combina ambos: `kilos = (gramos * presentacion / 1000) * cantidad`

## ✅ Forma Correcta

### Opción 1: Por Categoría (Recomendado)

Define presentaciones SIN el tamaño específico:

```python
presentaciones = {
    # Categorías generales - funcionan para CUALQUIER tamaño
    "ALPISTE": 25,           # Funciona para 250G, 450G, 500G, 1KG, etc.
    "FRIJOL CALIMA": 25,     # Funciona para cualquier tamaño
    "ARVEJA VERDE": 25,
    "ARROZ": 25,
    "HARINA": 24,
    "PASTA": 24,
    "ATUN": 48,
    "ACEITE": 25,
}
```

**Ventajas:**
- Más simple y mantenible
- Funciona con cualquier tamaño de producto
- Si llega un nuevo tamaño, automáticamente usa la presentación correcta

### Opción 2: Por Tamaño Específico (Excepciones)

Para productos con presentación diferente según tamaño:

```python
presentaciones = {
    # Categoría general
    "HOJUELAS AZUCARADAS": 24,  # Para tamaños normales

    # Excepción para tamaño específico
    "HOJUELAS AZUCARADAS*40G": 80,  # Presentación especial para 40G
}
```

El sistema **prioriza matches exactos**, entonces:
- `HOJUELAS AZUCARADAS*40G` → usa presentación 80 (match exacto)
- `HOJUELAS AZUCARADAS*50G` → usa presentación 24 (match de categoría)

## 📋 Ejemplos Reales

### Ejemplo 1: Granos con Diferentes Tamaños

```python
# Tabla de presentaciones
presentaciones = {
    "ALPISTE": 25,
    "FRIJOL CALIMA": 25,
}

# Facturas
productos = [
    ("ALPISTE*250G", 2),
    ("ALPISTE*450G", 2),
    ("ALPISTE*500G", 2),
    ("ALPISTE*1KG", 2),
    ("FRIJOL CALIMA*450G", 6),
    ("FRIJOL CALIMA*500G", 6),
]

# Resultados
ALPISTE*250G × 2  = (250 * 25 / 1000) * 2 = 12.5 kg
ALPISTE*450G × 2  = (450 * 25 / 1000) * 2 = 22.5 kg ✓
ALPISTE*500G × 2  = (500 * 25 / 1000) * 2 = 25.0 kg
ALPISTE*1KG × 2   = (1000 * 25 / 1000) * 2 = 50.0 kg
FRIJOL CALIMA*450G × 6 = (450 * 25 / 1000) * 6 = 67.5 kg ✓
FRIJOL CALIMA*500G × 6 = (500 * 25 / 1000) * 6 = 75.0 kg
```

### Ejemplo 2: Productos con Presentación Especial

```python
# Tabla de presentaciones
presentaciones = {
    "HARINA": 24,
    "ATUN": 48,
    "HOJUELAS AZUCARADAS*40G": 80,  # Específico
}

# Facturas
productos = [
    ("HARINA*500G", 1),
    ("HARINA AREPA*500G BLANCA", 1),
    ("ATUN*175G LOMO/ACEITE", 12),
    ("HOJUELAS AZUCARADAS*40G", 12),
]

# Resultados
HARINA*500G × 1 = (500 * 24 / 1000) * 1 = 12.0 kg
HARINA AREPA*500G BLANCA × 1 = (500 * 24 / 1000) * 1 = 12.0 kg
ATUN*175G × 12 = (175 * 48 / 1000) * 12 = 100.8 kg
HOJUELAS AZUCARADAS*40G × 12 = (40 * 80 / 1000) * 12 = 38.4 kg ✓
```

## 🔧 Cómo Migrar de Tabla Antigua

### Si tenías:

```python
presentaciones = {
    "ALPISTE*250G": 25,
    "ALPISTE*450G": 25,
    "ALPISTE*500G": 25,
    "ALPISTE*1KG": 25,
    "FRIJOL CALIMA*250G": 25,
    "FRIJOL CALIMA*450G": 25,
    "FRIJOL CALIMA*500G": 25,
    # ... muchas entradas repetidas
}
```

### Simplifica a:

```python
presentaciones = {
    "ALPISTE": 25,
    "FRIJOL CALIMA": 25,
}
```

¡Funciona exactamente igual pero es mucho más simple!

## ⚠️ Casos Especiales

### Productos A GRANEL

Para productos A GRANEL (sin gramos en el nombre), la presentación es el peso del bulto:

```python
presentaciones = {
    "ARROZ AGRANEL": 50,  # 50 kg por bulto
    "FRIJOL CALIMA AGRANEL": 50,
}

# Factura: ARROZ AGRANEL, cantidad=2
# Resultado: 50 * 2 = 100 kg
```

### Productos con Múltiples Unidades

```python
# Factura: PANELA*125G*8UND, cantidad=1
# El sistema extrae: 125G * 8 = 1000G
# Si presentación de "PANELA" es 8:
# Resultado: (1000 * 8 / 1000) * 1 = 8 kg
```

## 🧪 Verificar tu Tabla

Ejecuta el test de validación:

```bash
python test_validacion_usuario.py
```

O prueba manualmente:

```python
from src.domain.services.product_converter import ProductConverter

presentaciones = {
    "ALPISTE": 25,
    "FRIJOL CALIMA": 25,
}

converter = ProductConverter(presentaciones)

# Probar con diferentes tamaños
kilos, info = converter.convert_to_kilos("ALPISTE*450G", cantidad=2)
print(f"ALPISTE*450G × 2 = {kilos} kg")
print(f"Presentación usada: {info['presentacion']}")
print(f"Fórmula: {info['formula']}")
```

## 📊 Resumen de la Fórmula

```
kilos = (gramos_extraidos * presentacion / 1000) * cantidad_factura
```

Donde:
- **gramos_extraidos**: Del nombre de la factura (450G, 500G, 1KG, etc.)
- **presentacion**: De la tabla por categoría (25, 24, 48, etc.)
- **cantidad_factura**: Cantidad en la línea de factura

## ✨ Ventajas del Nuevo Sistema

1. ✅ **Más simple**: Menos entradas en la tabla
2. ✅ **Más flexible**: Funciona con nuevos tamaños automáticamente
3. ✅ **Más mantenible**: Un solo lugar para cada categoría
4. ✅ **Excepciones**: Puedes definir presentaciones específicas cuando sea necesario
5. ✅ **Orden independiente**: "ACEITE 500G" = "500G ACEITE"
6. ✅ **Normalización**: 500G = 500GR, 500ML = 500CC

## 🎓 Ejemplo Completo

```python
from src.domain.services.product_converter import ProductConverter

# 1. Define presentaciones por categoría
presentaciones = {
    # Granos
    "ALPISTE": 25,
    "ARROZ": 25,
    "FRIJOL CALIMA": 25,
    "ARVEJA VERDE": 25,
    "LENTEJA": 25,

    # Harinas
    "HARINA": 24,

    # Pastas
    "PASTA": 24,

    # Atún
    "ATUN": 48,

    # Aceites
    "ACEITE": 25,

    # Excepciones
    "HOJUELAS AZUCARADAS*40G": 80,
}

# 2. Crear converter
converter = ProductConverter(presentaciones)

# 3. Convertir productos de factura
facturas = [
    ("ALPISTE*450G", 2),
    ("FRIJOL CALIMA*450G", 6),
    ("HOJUELAS AZUCARADAS*40G", 12),
    ("HARINA*500G", 1),
]

for producto, cantidad in facturas:
    kilos, info = converter.convert_to_kilos(producto, cantidad)
    print(f"{producto:30} × {cantidad:2} = {float(kilos):6.1f} kg")
```

**Salida:**
```
ALPISTE*450G                   ×  2 =   22.5 kg
FRIJOL CALIMA*450G             ×  6 =   67.5 kg
HOJUELAS AZUCARADAS*40G        × 12 =   38.4 kg
HARINA*500G                    ×  1 =   12.0 kg
```

---

💡 **Tip**: Empieza definiendo presentaciones por categoría (sin tamaño). Solo agrega entradas específicas con tamaño cuando realmente necesites una presentación diferente.
