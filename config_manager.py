import json
import requests
import os
from datetime import datetime, timedelta

class ConfigManager:
    """Gestor de configuraciones remotas para actualizaciones dinámicas"""
    
    def __init__(self):
        self.config_url = "https://raw.githubusercontent.com/tu-usuario/facturas-config/main/config.json"
        self.local_config_file = "app_config.json"
        self.cache_duration = timedelta(hours=4)  # Cache por 4 horas
        
    def get_remote_config(self):
        """Obtener configuración desde repositorio remoto"""
        try:
            response = requests.get(self.config_url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def load_local_config(self):
        """Cargar configuración local desde archivo"""
        try:
            if os.path.exists(self.local_config_file):
                with open(self.local_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return self.get_default_config()
    
    def save_local_config(self, config):
        """Guardar configuración localmente"""
        try:
            config['last_update'] = datetime.now().isoformat()
            with open(self.local_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    def get_config(self):
        """Obtener configuración (remota si está disponible, local como fallback)"""
        local_config = self.load_local_config()
        
        # Verificar si necesita actualizar
        needs_update = True
        if local_config and 'last_update' in local_config:
            try:
                last_update = datetime.fromisoformat(local_config['last_update'])
                if datetime.now() - last_update < self.cache_duration:
                    needs_update = False
            except:
                pass
        
        if needs_update:
            remote_config = self.get_remote_config()
            if remote_config:
                self.save_local_config(remote_config)
                return remote_config
        
        return local_config
    
    def get_default_config(self):
        """Configuración por defecto"""
        return {
            "version": "1.0.0",
            "companies": {
                "AGROBUITRON": {
                    "enabled": True,
                    "xml_namespaces": {
                        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
                        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
                        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
                        "sts": "dian:gov:co:facturaelectronica:Structures-2-1"
                    },
                    "field_mappings": {
                        "invoice_id": ".//cbc:ID",
                        "issue_date": ".//cbc:IssueDate",
                        "due_date": ".//cbc:DueDate",
                        "currency": ".//cbc:DocumentCurrencyCode"
                    },
                    "output_fields": [
                        "N° Factura", "Nombre Producto", "Codigo Subyacente", 
                        "Unidad Medida", "Cantidad", "Precio Unitario", 
                        "Precio Total", "Fecha Factura", "Fecha Pago",
                        "Nit Comprador", "Nombre Comprador", "Nit Vendedor", 
                        "Nombre Vendedor", "Principal V,C", "Municipio", 
                        "Iva", "Descripción", "Activa Factura", "Activa Bodega", 
                        "Incentivo", "Cantidad Original", "Moneda"
                    ],
                    "default_values": {
                        "Principal V,C": "V",
                        "Activa Factura": "Sí",
                        "Activa Bodega": "Sí",
                        "Descripción": "",
                        "Incentivo": ""
                    }
                },
                "MG": {
                    "enabled": False,
                    "message": "Funcionalidad en desarrollo"
                },
                "ROSAS": {
                    "enabled": False,
                    "message": "Funcionalidad en desarrollo"
                }
            },
            "unit_codes": {
                "KGM": "Kg", "LTR": "Lt", "LT": "Lt", "NIU": "Un", 
                "MTR": "Mt", "HUR": "Hr", "GRM": "Gr", "TNE": "Tn",
                "MLT": "Ml", "CMT": "Cm", "M2": "M2", "M3": "M3"
            },
            "currency_codes": {
                "COP": "1", "USD": "2", "EUR": "3"
            },
            "app_settings": {
                "csv_separator": ";",
                "decimal_places": 5,
                "decimal_separator": ",",
                "date_format": "%Y-%m-%d",
                "encoding": "utf-8-sig"
            }
        }

# Ejemplo de uso del gestor de configuraciones
if __name__ == "__main__":
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    print("Configuración cargada:")
    print(json.dumps(config, indent=2, ensure_ascii=False))
