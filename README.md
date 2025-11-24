# Sistema de Facturas Electrónicas - Cali SAE

Sistema de procesamiento de facturas electrónicas UBL 2.0 DIAN Colombia con arquitectura Clean y soporte multi-cliente.

## 🚀 Características

- **Arquitectura Clean** - Separación en capas: Domain, Infrastructure, Presentation
- **Multi-cliente** - Soporte para múltiples clientes mediante tabs (Agrobuitron, Juan Camilo Rosas, El Paisano)
- **UI Moderna** - Interfaz gráfica con PyQt6
- **Procesamiento XML** - Parser para facturas electrónicas UBL 2.0 de la DIAN Colombia
- **Exportación flexible** - CSV o actualización de archivos Excel existentes
- **Sistema de reportes** - Panel de administración con auditoría completa
- **Actualización automática** - Descarga actualizaciones desde GitHub
- **Multi-threading** - Procesamiento sin bloqueo de interfaz

## 📋 Requisitos

- Python 3.8 o superior
- Windows / Linux / macOS

## 🔧 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/LuisVeraVR/cali-sae.git
cd cali-sae
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar la aplicación:
```bash
python main.py
```

## 🔑 Credenciales por Defecto

- **Administrador**: `admin` / `admin123`
  - Acceso completo + panel de reportes

- **Operador**: `operador` / `FacturasElectronicas2024`
  - Solo procesamiento de facturas

## 📁 Estructura del Proyecto

```
cali-sae/
├── main.py                          # Punto de entrada principal
├── requirements.txt                 # Dependencias del proyecto
├── config.json                      # Configuración
├── facturas_users.db               # Base de datos SQLite
│
└── src/
    ├── domain/                     # Capa de Dominio
    │   ├── entities/              # Entidades de negocio
    │   ├── repositories/          # Interfaces de repositorios
    │   └── use_cases/            # Casos de uso
    │
    ├── infrastructure/            # Capa de Infraestructura
    │   ├── database/             # Implementaciones SQLite
    │   ├── parsers/              # Parser XML UBL 2.0
    │   ├── exporters/            # Exportadores CSV/Excel
    │   └── updater/              # Sistema de actualizaciones
    │
    └── presentation/              # Capa de Presentación
        ├── controllers/          # Controladores
        ├── views/               # Ventanas PyQt6
        │   └── tabs/           # Tabs por cliente
        └── widgets/            # Componentes reutilizables
```

## 💼 Clientes Soportados

### Agrobuitron ✅
Cliente completamente funcional con:
- Procesamiento de archivos ZIP con XMLs
- Exportación a CSV o Excel
- Validación de datos
- Reportes automáticos

### Juan Camilo Rosas 🔄
Estructura base implementada, lista para personalizar.

### El Paisano 🔄
Estructura base implementada, lista para personalizar.

## 🎯 Uso

### 1. Inicio de Sesión
- Ingresar usuario y contraseña
- Opción para cambiar contraseña

### 2. Procesamiento de Facturas (Tab Agrobuitron)
- Seleccionar uno o más archivos ZIP con XMLs
- Elegir formato de salida: CSV o Excel
- Si es Excel, seleccionar archivo y hoja
- Hacer clic en "PROCESAR FACTURAS"
- Ver progreso en tiempo real

### 3. Panel de Reportes (Solo Admin)
- Click en "Ver Reportes" en el header
- Ver historial de procesamiento
- Exportar reportes a CSV
- Estadísticas de uso

## 🔄 Sistema de Actualizaciones

El sistema verifica automáticamente al iniciar si hay nuevas versiones disponibles en:
```
https://github.com/LuisVeraVR/cali-sae
```

Si hay una actualización disponible, se muestra un diálogo para descargarla opcionalmente.

## 📊 Base de Datos

SQLite con 2 tablas principales:

### users
- Usuarios del sistema
- Contraseñas hasheadas con SHA-256
- Tipos: admin / operator

### reports
- Auditoría de procesamiento
- Usuario, empresa, archivo, registros
- Fecha y tamaño de archivo

## 🏗️ Arquitectura Clean

### Capa de Dominio (Domain)
Contiene la lógica de negocio pura, independiente de frameworks:
- **Entidades**: User, Invoice, Product, Report
- **Interfaces de Repositorios**: Contratos para persistencia
- **Casos de Uso**: Lógica de aplicación

### Capa de Infraestructura (Infrastructure)
Implementaciones concretas:
- **Repositorios SQLite**: Persistencia de datos
- **Parser XML**: Lectura de facturas UBL 2.0
- **Exportadores**: CSV y Excel
- **Updater**: Descarga desde GitHub

### Capa de Presentación (Presentation)
Interfaz de usuario con PyQt6:
- **Controladores**: Coordinan UI con casos de uso
- **Vistas**: Ventanas y componentes visuales
- **Tabs**: Un tab por cada cliente

## 🛠️ Tecnologías

- **Python 3.8+**
- **PyQt6** - Interfaz gráfica
- **SQLite3** - Base de datos
- **openpyxl** - Manejo de Excel
- **requests** - Actualizaciones HTTP
- **packaging** - Versionado semántico

## 📝 Agregar un Nuevo Cliente

1. Duplicar un tab existente (ej: `agrobuitron_tab.py`)
2. Renombrar la clase y personalizar
3. Importar en `main_window.py`
4. Agregar el tab al QTabWidget

Ejemplo:
```python
from .tabs.nuevo_cliente_tab import NuevoClienteTab

# En MainWindow._create_content()
self.nuevo_cliente_tab = NuevoClienteTab(self.main_controller)
self.tabs.addTab(self.nuevo_cliente_tab, "NUEVO CLIENTE")
```

## 🧪 Testing

Para ejecutar pruebas (cuando se implementen):
```bash
pytest tests/
```

## 📦 Crear Ejecutable

Para crear un ejecutable standalone:
```bash
pyinstaller --onefile --windowed --name "SistemaFacturas" main.py
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto es privado y propietario.

## 👤 Autor

**Luis Vera**
- GitHub: [@LuisVeraVR](https://github.com/LuisVeraVR)

## 📞 Soporte

Para reportar bugs o solicitar funcionalidades, abrir un issue en:
https://github.com/LuisVeraVR/cali-sae/issues

---

**Versión:** 2.1.0
**Última actualización:** Noviembre 2025
