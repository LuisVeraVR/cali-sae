"""
Script para calcular kilos totales de productos a partir de SUBY, Presentacion y Cantidad.

Este script:
1. Valida/corrige la columna Presentacion según la familia del producto
2. Extrae gramos del nombre del producto (SUBY)
3. Calcula kilos_totales = (Presentacion * gramos_producto / 1000) * Cantidad
"""

import pandas as pd
import re
from typing import Tuple


# Definición de familias de productos y sus presentaciones correctas
FAMILIAS_PRODUCTOS = {
    'Granos': {
        'presentacion': 25,
        'palabras_clave': ['ARROZ', 'FRIJOL', 'LENTEJA', 'GARBANZO', 'MAIZ',
                          'MAZAMORRA', 'CUCHUCO', 'AGRANEL']
    },
    'Harina': {
        'presentacion': 24,
        'palabras_clave': ['HARINA', 'AVENA HOJUELA', 'HOJUELAS DE MAIZ']
    },
    'Pastas': {
        'presentacion': 24,
        'palabras_clave': ['PASTA', 'MACARRON', 'SPAGUETTI', 'C/ANGEL',
                          'CONCHITA', 'CORBATA']
    },
    'Atun': {
        'presentacion': 48,
        'palabras_clave': ['ATUN']
    },
    'Aceite': {
        'presentacion': 25,
        'palabras_clave': ['ACEITE']
    }
}


def detectar_familia_producto(nombre_producto: str) -> Tuple[str, int]:
    """
    Detecta la familia del producto y retorna su presentación correcta.

    Args:
        nombre_producto: Nombre del producto (columna SUBY)

    Returns:
        Tupla (nombre_familia, presentacion_correcta)
        Si no encuentra familia, retorna (None, None)
    """
    if pd.isna(nombre_producto):
        return None, None

    nombre_upper = str(nombre_producto).upper()

    # Buscar coincidencias con palabras clave de cada familia
    for familia, config in FAMILIAS_PRODUCTOS.items():
        for palabra_clave in config['palabras_clave']:
            if palabra_clave in nombre_upper:
                return familia, config['presentacion']

    return None, None


def extraer_gramos_producto(nombre_producto: str) -> int:
    """
    Extrae los gramos del nombre del producto.

    Busca patrones como:
    - 500G, 250GR, 1000GRS -> retorna gramos directamente
    - 1KG, 2KILOS -> convierte a gramos (multiplica por 1000)
    - 500CC -> retorna como gramos (para líquidos)

    Args:
        nombre_producto: Nombre del producto (columna SUBY)

    Returns:
        Gramos del producto. Si no encuentra nada, retorna 0.
    """
    if pd.isna(nombre_producto):
        return 0

    nombre_upper = str(nombre_producto).upper()

    # Patrón para buscar KG o KILOS (convertir a gramos)
    match_kg = re.search(r'(\d+)\s*(?:KG|KILO|KILOS)\b', nombre_upper)
    if match_kg:
        return int(match_kg.group(1)) * 1000

    # Patrón para buscar G, GR, GRS, CC (ya están en gramos)
    match_g = re.search(r'(\d+)\s*(?:G|GR|GRS|CC)\b', nombre_upper)
    if match_g:
        return int(match_g.group(1))

    # No se encontró ninguna unidad
    return 0


def calcular_kilos_totales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula kilos totales de productos corrigiendo Presentacion y extrayendo gramos.

    El DataFrame debe tener las columnas:
    - SUBY: Nombre del producto
    - Presentacion: Número de unidades por caja/bulto
    - Cantidad: Cantidad de la factura (unidades facturadas)

    Args:
        df: DataFrame con las columnas mencionadas

    Returns:
        DataFrame con columnas adicionales:
        - Presentacion (corregida según familia)
        - gramos_producto (extraídos del nombre)
        - kilos_totales (calculados con la fórmula)
    """
    # Validar que existan las columnas necesarias
    columnas_requeridas = ['SUBY', 'Presentacion', 'Cantidad']
    for col in columnas_requeridas:
        if col not in df.columns:
            raise ValueError(f"El DataFrame debe tener la columna '{col}'")

    # Crear una copia para no modificar el DataFrame original
    df_resultado = df.copy()

    # 1. CORREGIR PRESENTACION según familia del producto
    print("Paso 1: Corrigiendo columna Presentacion según familia...")
    for idx, row in df_resultado.iterrows():
        familia, presentacion_correcta = detectar_familia_producto(row['SUBY'])

        if familia and presentacion_correcta:
            # Si detectamos familia, verificar si Presentacion actual es diferente
            if pd.notna(row['Presentacion']) and row['Presentacion'] != presentacion_correcta:
                print(f"  Fila {idx}: '{row['SUBY']}' -> Familia: {familia}, "
                      f"Presentacion: {row['Presentacion']} -> {presentacion_correcta}")
                df_resultado.at[idx, 'Presentacion'] = presentacion_correcta
            elif pd.isna(row['Presentacion']):
                # Si no tiene Presentacion, asignar la correcta
                df_resultado.at[idx, 'Presentacion'] = presentacion_correcta

    # 2. EXTRAER GRAMOS del nombre del producto
    print("\nPaso 2: Extrayendo gramos del nombre del producto...")
    df_resultado['gramos_producto'] = df_resultado['SUBY'].apply(extraer_gramos_producto)

    # Mostrar algunos ejemplos
    ejemplos = df_resultado[df_resultado['gramos_producto'] > 0].head(5)
    if not ejemplos.empty:
        print("  Ejemplos de gramos extraídos:")
        for idx, row in ejemplos.iterrows():
            print(f"    '{row['SUBY']}' -> {row['gramos_producto']}g")

    # 3. CALCULAR KILOS_TOTALES
    print("\nPaso 3: Calculando kilos_totales...")
    # Formula: kilos_totales = (Presentacion * gramos_producto / 1000) * Cantidad
    df_resultado['kilos_totales'] = (
        df_resultado['Presentacion'] *
        df_resultado['gramos_producto'] / 1000
    ) * df_resultado['Cantidad']

    # Manejar casos donde no hay gramos (dejar en 0 o NaN)
    df_resultado['kilos_totales'] = df_resultado['kilos_totales'].fillna(0)

    print(f"\n✓ Proceso completado. {len(df_resultado)} filas procesadas.")

    return df_resultado


def procesar_archivo_excel(ruta_entrada: str, ruta_salida: str = None,
                           hoja: str = 0) -> pd.DataFrame:
    """
    Procesa un archivo Excel y guarda el resultado.

    Args:
        ruta_entrada: Ruta al archivo Excel de entrada
        ruta_salida: Ruta para guardar el archivo procesado (opcional)
        hoja: Nombre o índice de la hoja a procesar (default: 0)

    Returns:
        DataFrame procesado
    """
    print(f"Leyendo archivo: {ruta_entrada}")
    df = pd.read_excel(ruta_entrada, sheet_name=hoja)

    print(f"Archivo cargado: {len(df)} filas, {len(df.columns)} columnas")
    print(f"Columnas disponibles: {', '.join(df.columns.tolist())}\n")

    # Procesar el DataFrame
    df_procesado = calcular_kilos_totales(df)

    # Guardar resultado si se especifica ruta de salida
    if ruta_salida:
        print(f"\nGuardando resultado en: {ruta_salida}")
        df_procesado.to_excel(ruta_salida, index=False)
        print("✓ Archivo guardado exitosamente.")

    return df_procesado


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Ejemplo 1: Crear un DataFrame de prueba
    print("=" * 70)
    print("EJEMPLO 1: DataFrame de prueba")
    print("=" * 70 + "\n")

    datos_prueba = {
        'SUBY': [
            'ARROZ*500G',
            'ACEITE SOYA*500CC LA ORLANDESA E',
            'HARINA AREPA*500G BLANCA',
            'PASTA SANTALI*250G MACARRONCITO',
            'ATUN ROBIN/H LOMO/AGUA*175G',
            'FRIJOL CALIMA*500G',
            'PANELA REDONDA*24KILOS',
            'PRODUCTO SIN UNIDAD'
        ],
        'Presentacion': [30, 20, 24, 24, 48, 25, 10, 12],  # Algunas incorrectas
        'Cantidad': [5, 10, 8, 12, 6, 4, 2, 5]
    }

    df_prueba = pd.DataFrame(datos_prueba)

    print("DataFrame original:")
    print(df_prueba)
    print("\n" + "=" * 70 + "\n")

    # Procesar
    df_resultado = calcular_kilos_totales(df_prueba)

    print("\n" + "=" * 70)
    print("DataFrame procesado:")
    print("=" * 70)
    print(df_resultado[['SUBY', 'Presentacion', 'gramos_producto',
                        'Cantidad', 'kilos_totales']])

    # Guardar resultado de ejemplo
    df_resultado.to_excel('resultado_ejemplo.xlsx', index=False)
    print("\n✓ Resultado guardado en 'resultado_ejemplo.xlsx'")

    # Ejemplo 2: Procesar un archivo Excel (descomentar para usar)
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Procesar archivo Excel")
    print("=" * 70 + "\n")

    df_resultado = procesar_archivo_excel(
        ruta_entrada='mis_productos.xlsx',
        ruta_salida='mis_productos_procesados.xlsx',
        hoja=0  # Primera hoja
    )

    # Ver estadísticas
    print("\nEstadísticas del procesamiento:")
    print(f"- Total de productos: {len(df_resultado)}")
    print(f"- Productos con gramos detectados: {(df_resultado['gramos_producto'] > 0).sum()}")
    print(f"- Total kilos calculados: {df_resultado['kilos_totales'].sum():.2f} kg")
    """
