# 📊 Calculadora de Kilos de Productos

Script de Python para calcular automáticamente los kilos totales de productos a partir de la información del nombre del producto (SUBY), presentación y cantidad.

## ✨ Características

1. **Validación automática de Presentacion**: Corrige la columna según la familia del producto
2. **Extracción de gramos**: Lee automáticamente gramos/kilos del nombre del producto
3. **Cálculo preciso**: Aplica la fórmula `kilos_totales = (Presentacion × gramos / 1000) × Cantidad`

## 📋 Requisitos

```bash
pip install pandas openpyxl
```

## 🚀 Uso Rápido

### Opción 1: Procesar un archivo Excel

```python
from calcular_kilos_productos import procesar_archivo_excel

# Procesar archivo
df_resultado = procesar_archivo_excel(
    ruta_entrada='mis_productos.xlsx',
    ruta_salida='mis_productos_procesados.xlsx',
    hoja=0  # Primera hoja (puede ser nombre o índice)
)

print(f"Total kilos: {df_resultado['kilos_totales'].sum():.2f} kg")
```

### Opción 2: Trabajar con DataFrame directamente

```python
import pandas as pd
from calcular_kilos_productos import calcular_kilos_totales

# Cargar tus datos
df = pd.read_excel('mis_productos.xlsx')

# Procesar
df_resultado = calcular_kilos_totales(df)

# Guardar
df_resultado.to_excel('resultado.xlsx', index=False)
```

## 📊 Columnas Requeridas

Tu archivo/DataFrame debe tener estas columnas:

- **SUBY**: Nombre del producto (ej: "ARROZ*500G", "ACEITE SOYA*500CC")
- **Presentacion**: Número de unidades por caja/bulto
- **Cantidad**: Cantidad facturada (unidades)

## 🏷️ Familias de Productos

El script detecta automáticamente la familia y corrige la Presentacion:

| Familia | Presentacion | Palabras Clave |
|---------|-------------|----------------|
| **Granos** | 25 | ARROZ, FRIJOL, LENTEJA, GARBANZO, MAIZ, MAZAMORRA, CUCHUCO, AGRANEL |
| **Harina** | 24 | HARINA, AVENA HOJUELA, HOJUELAS DE MAIZ |
| **Pastas** | 24 | PASTA, MACARRON, SPAGUETTI, C/ANGEL, CONCHITA, CORBATA |
| **Atun** | 48 | ATUN |
| **Aceite** | 25 | ACEITE |

## 📐 Fórmula de Cálculo

```
kilos_totales = (Presentacion × gramos_producto ÷ 1000) × Cantidad
```

**Ejemplo:**
- Producto: "ARROZ*500G"
- Presentacion: 25 (unidades por bulto)
- Cantidad: 5 (bultos facturados)

**Cálculo:**
```
kilos_totales = (25 × 500 ÷ 1000) × 5
kilos_totales = (12.5) × 5
kilos_totales = 62.5 kg
```

## 📝 Ejemplo de Uso Completo

```python
import pandas as pd
from calcular_kilos_productos import calcular_kilos_totales

# Crear datos de ejemplo
datos = {
    'SUBY': [
        'ARROZ*500G',
        'ACEITE SOYA*500CC LA ORLANDESA E',
        'HARINA AREPA*500G BLANCA',
        'PASTA SANTALI*250G MACARRONCITO',
        'ATUN ROBIN/H LOMO/AGUA*175G',
        'FRIJOL CALIMA*500G',
        'PANELA REDONDA*24KILOS'
    ],
    'Presentacion': [30, 20, 24, 24, 48, 25, 10],  # Algunas incorrectas
    'Cantidad': [5, 10, 8, 12, 6, 4, 2]
}

df = pd.DataFrame(datos)

# Procesar
df_resultado = calcular_kilos_totales(df)

# Ver resultado
print(df_resultado[['SUBY', 'Presentacion', 'gramos_producto',
                    'Cantidad', 'kilos_totales']])

# Estadísticas
print(f"\nTotal productos: {len(df_resultado)}")
print(f"Total kilos: {df_resultado['kilos_totales'].sum():.2f} kg")
print(f"Productos con gramos detectados: {(df_resultado['gramos_producto'] > 0).sum()}")
```

**Salida:**
```
                               SUBY  Presentacion  gramos_producto  Cantidad  kilos_totales
0                        ARROZ*500G            25              500         5           62.5
1  ACEITE SOYA*500CC LA ORLANDESA E            25              500        10          125.0
2          HARINA AREPA*500G BLANCA            24              500         8           96.0
3   PASTA SANTALI*250G MACARRONCITO            24              250        12           72.0
4       ATUN ROBIN/H LOMO/AGUA*175G            48              175         6           50.4
5                FRIJOL CALIMA*500G            25              500         4           50.0
6            PANELA REDONDA*24KILOS            10            24000         2          480.0

Total productos: 7
Total kilos: 935.9 kg
Productos con gramos detectados: 7
```

## 🔍 Patrones de Extracción de Gramos

El script reconoce estos patrones en el nombre del producto:

| Patrón | Ejemplo | Gramos Extraídos |
|--------|---------|------------------|
| **\*500G** | ARROZ*500G | 500 |
| **\*250GR** | PANELA*250GR | 250 |
| **\*1000GRS** | HARINA*1000GRS | 1000 |
| **\*500CC** | ACEITE*500CC | 500 |
| **\*2KG** | AZUCAR*2KG | 2000 |
| **\*24KILOS** | PANELA*24KILOS | 24000 |

## 📤 Columnas de Salida

El DataFrame procesado incluye:

- Todas las columnas originales
- **Presentacion** (corregida según familia)
- **gramos_producto** (nueva columna con gramos extraídos)
- **kilos_totales** (nueva columna calculada)

## ⚠️ Manejo de Casos Especiales

- **Producto sin unidad en el nombre**: `gramos_producto = 0`, `kilos_totales = 0`
- **Producto sin familia detectada**: Mantiene `Presentacion` original
- **Valores nulos/vacíos**: Se manejan sin romper el proceso

## 🎯 Ejecutar el Ejemplo

```bash
python calcular_kilos_productos.py
```

Esto genera `resultado_ejemplo.xlsx` con datos de prueba procesados.

## 📞 Soporte

Para problemas o mejoras, verifica que:

1. Las columnas requeridas existen en tu DataFrame
2. Los nombres de productos siguen el formato con unidades (G, GR, KG, CC)
3. Pandas y openpyxl están instalados correctamente

## 📄 Licencia

Script libre para uso en el proyecto CALI-SAE.
