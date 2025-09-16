#!/usr/bin/env python3
"""
Script para corregir automáticamente el problema de pandas
Ejecutar este script para modificar advanced_invoice_system.py
"""

import re
import shutil
from datetime import datetime

def fix_pandas_import():
    """Corregir el import de pandas en advanced_invoice_system.py"""
    
    # Hacer backup
    backup_name = f"advanced_invoice_system_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    try:
        shutil.copy('advanced_invoice_system.py', backup_name)
        print(f"✓ Backup creado: {backup_name}")
    except Exception as e:
        print(f"⚠ No se pudo crear backup: {e}")
    
    # Leer archivo original
    try:
        with open('advanced_invoice_system.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Error: advanced_invoice_system.py no encontrado")
        return False
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False
    
    # Realizar reemplazos
    print("🔧 Aplicando correcciones...")
    
    # 1. Reemplazar import pandas
    old_import = "import pandas as pd"
    new_import = """try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Pandas no disponible - usando CSV nativo")"""
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        print("✓ Import de pandas corregido")
    else:
        print("⚠ Import de pandas no encontrado o ya corregido")
    
    # 2. Agregar función CSV nativa después de los imports
    csv_function = '''
def save_to_csv_native(data_list, filename, columns=None):
    """Guardar datos a CSV usando el módulo csv nativo (sin pandas)"""
    if not data_list:
        return None
    
    try:
        import csv
        
        # Aplanar datos si es necesario
        flattened_data = []
        for item in data_list:
            if isinstance(item, list):
                flattened_data.extend(item)
            else:
                flattened_data.append(item)
        
        # Si no se especifican columnas, usar las del primer elemento
        if columns is None and flattened_data:
            if isinstance(flattened_data[0], dict):
                columns = list(flattened_data[0].keys())
        
        if not columns:
            return None
            
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns, delimiter=';')
            writer.writeheader()
            
            for row in flattened_data:
                if isinstance(row, dict):
                    # Asegurar que todas las columnas estén presentes
                    clean_row = {col: row.get(col, '') for col in columns}
                    writer.writerow(clean_row)
        
        return filename
    except Exception as e:
        print(f"Error guardando CSV nativo: {e}")
        return None

'''
    
    # Encontrar donde insertar la función (después de los imports)
    import_section_end = content.find('# ==========================\n#  UTILIDADES GENERALES')
    if import_section_end == -1:
        import_section_end = content.find('class AuthenticationWindow:')
    
    if import_section_end != -1 and 'save_to_csv_native' not in content:
        content = content[:import_section_end] + csv_function + '\n' + content[import_section_end:]
        print("✓ Función CSV nativa agregada")
    else:
        print("⚠ No se pudo insertar función CSV o ya existe")
    
    # 3. Modificar _save_csv_agro para usar fallback
    old_csv_method = re.search(r'def _save_csv_agro\(self\):.*?return None', content, re.DOTALL)
    
    if old_csv_method:
        new_csv_method = '''def _save_csv_agro(self):
        """Generar archivo CSV para AGROBUITRON (con fallback sin pandas)"""
        if not self.extracted_data:
            return None
        
        try:
            # Definir orden de columnas específico para AGROBUITRON
            column_order = [
                'N° Factura', 'Nombre Producto', 'Codigo Subyacente', 'Unidad Medida',
                'Cantidad', 'Precio Unitario', 'Precio Total', 'Fecha Factura', 'Fecha Pago',
                'Nit Comprador', 'Nombre Comprador', 'Nit Vendedor', 'Nombre Vendedor',
                'Principal V,C', 'Municipio', 'Iva', 'Descripción', 'Activa Factura',
                'Activa Bodega', 'Incentivo', 'Cantidad Original', 'Moneda'
            ]
            
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"AGROBUITRON_Facturas_{timestamp}.csv"
            
            # Usar pandas si está disponible, sino CSV nativo
            if HAS_PANDAS:
                try:
                    # Aplanar datos
                    rows = []
                    for x in self.extracted_data:
                        if isinstance(x, list):
                            rows.extend(x)
                        else:
                            rows.append(x)

                    # Crear DataFrame
                    df = pd.DataFrame(rows)
                    df = df.reindex(columns=column_order, fill_value="")
                    
                    # Guardar CSV
                    df.to_csv(csv_filename, index=False, encoding="utf-8-sig", sep=";")
                    return csv_filename
                    
                except Exception as e:
                    print(f"Error con pandas, usando CSV nativo: {e}")
                    # Fallback a CSV nativo
                    return save_to_csv_native(self.extracted_data, csv_filename, column_order)
            else:
                # Usar CSV nativo directamente
                return save_to_csv_native(self.extracted_data, csv_filename, column_order)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando CSV: {str(e)}")
            return None'''
        
        content = content.replace(old_csv_method.group(0), new_csv_method)
        print("✓ Método _save_csv_agro corregido")
    else:
        print("⚠ Método _save_csv_agro no encontrado")
    
    # Guardar archivo corregido
    try:
        with open('advanced_invoice_system.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Archivo corregido guardado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error guardando archivo corregido: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Corrector automático de dependencias pandas")
    print("=" * 50)
    
    if fix_pandas_import():
        print("\n✅ CORRECCIÓN COMPLETADA")
        print("\nPróximos pasos:")
        print("1. Ejecutar: python advanced_invoice_system.py (para probar)")
        print("2. Ejecutar: build_simple_working.bat (para crear ejecutable)")
    else:
        print("\n❌ CORRECCIÓN FALLÓ")
        print("Revisa los errores mostrados arriba")
    
    input("\nPresiona Enter para continuar...")
