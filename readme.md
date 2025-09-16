# 🧾 Sistema de Facturas Electrónicas v2.0

Sistema profesional para extracción y procesamiento de facturas electrónicas DIAN (Colombia).

## 📋 Características

- **🔐 Autenticación segura** con usuarios admin y operador
- **🏢 Multi-empresa** (AGROBUITRON implementado, MG y ROSAS en desarrollo)
- **📊 Procesamiento XML** de facturas electrónicas UBL
- **📄 Exportación CSV** con formato específico por empresa
- **📈 Actualización Excel** de archivos existentes
- **👨‍💼 Panel administrativo** con reportes de actividad
- **🔄 Actualizaciones automáticas** desde repositorio

## 🚀 Instalación Rápida

### Para Usuarios Finales:
1. Descargar `Sistema_Facturas_v2.0.exe`
2. Ejecutar como administrador
3. ¡Listo para usar!

### Para Desarrolladores:
```bash
# Clonar repositorio
git clone https://github.com/LuisVeraVR/operator-auto.git
cd operator-auto

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python advanced_invoice_system.py
```

## 👥 Usuarios por Defecto

| Usuario | Contraseña | Tipo | Permisos |
|---------|------------|------|----------|
| `admin` | `admin123` | Administrador | Todos + Reportes |
| `operador` | `FacturasElectronicas2024` | Operador | Procesamiento básico |

## 🏗️ Build del Ejecutable

### Método Simple (Recomendado):
```batch
# Ejecutar script de build
build_simple_working.bat
```

### Método con Pandas:
```batch
# Si necesitas funcionalidad completa de pandas
build_fixed_dependencies.bat
```

### Resultado:
- Ejecutable en: `dist/release/Sistema_Facturas_v2.0.exe`
- Tamaño aproximado: 15-25 MB (simple) / 80-120 MB (completo)

## 🏢 Empresas Soportadas

### ✅ AGROBUITRON SAS (Implementado)
- Procesamiento completo de facturas XML
- Extracción de datos específicos
- Formato CSV personalizado
- Actualización de Excel existente

### 🚧 MG y ROSAS (En Desarrollo)
- Funcionalidad planificada
- Estructuras preparadas
- Próximas versiones

## 📁 Estructura de Archivos de Salida

### Archivos CSV:
```
AGROBUITRON_Facturas_YYYYMMDD_HHMMSS.csv
```

### Campos Extraídos:
- N° Factura, Nombre Producto, Codigo Subyacente
- Unidad Medida, Cantidad, Precio Unitario, Precio Total
- Fecha Factura, Fecha Pago
- Datos del Comprador y Vendedor
- Información fiscal (IVA, Municipio, etc.)

## 🔧 Funcionalidades Técnicas

- **🗄️ Base de datos SQLite** para usuarios y reportes
- **🌐 Actualizaciones remotas** vía GitHub API
- **📜 Procesamiento XML** con namespaces UBL estándar
- **🔒 Hashing SHA-256** para contraseñas
- **📊 Logging completo** de operaciones
- **🧵 Procesamiento multi-hilo** para mejor rendimiento

## 🛡️ Seguridad

- Autenticación obligatoria
- Contraseñas hasheadas
- Validación de archivos XML
- Logs de auditoría
- Base de datos local encriptada

## 📈 Reportes Administrativos

### Panel de Admin:
- Lista de procesamientos realizados
- Estadísticas por usuario y empresa
- Exportación de reportes a CSV
- Métricas de archivos procesados

## 🔄 Actualizaciones

El sistema verifica automáticamente:
- Nuevas versiones disponibles
- Descarga automática opcional
- Notificación al usuario
- Repositorio: `https://github.com/LuisVeraVR/operator-auto`

## 📞 Soporte Técnico

- **Email**: soporte@empresa.com
- **Repositorio**: [GitHub Issues](https://github.com/LuisVeraVR/operator-auto/issues)
- **Versión actual**: v2.1.0
- **Última actualización**: Septiembre 2024

## 📋 Requisitos del Sistema

### Mínimos:
- Windows 10/11 (64-bit)
- 4 GB RAM
- 100 MB espacio libre
- .NET Framework 4.7+ (para firma digital)

### Recomendados:
- Windows 11 (64-bit)
- 8 GB RAM
- 500 MB espacio libre
- Conexión a internet (para actualizaciones)

## 🏷️ Historial de Versiones

### v2.1.0 (Actual)
- ✅ Sistema de autenticación completo
- ✅ Panel administrativo
- ✅ Reportes de actividad
- ✅ Multi-empresa preparado
- ✅ Actualizaciones automáticas

### v2.0.0
- ✅ AGROBUITRON implementado
- ✅ Procesamiento XML UBL
- ✅ Exportación CSV/Excel
- ✅ Interfaz gráfica mejorada

### v1.0.0
- ✅ Funcionalidad básica
- ✅ Procesamiento simple
- ✅ Interfaz inicial

## 📜 Licencia

Uso comercial. Todos los derechos reservados.
Copyright © 2024 - Sistema de Facturas Electrónicas

---

## 🚀 Desarrollo y Contribuciones

Este proyecto está en desarrollo activo. Para contribuir:

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 🙏 Agradecimientos

- Comunidad Python
- Documentación DIAN Colombia
- Contribuidores del proyecto
- Usuarios y testers

---

**⚡ ¡Sistema diseñado para máxima eficiencia y confiabilidad en el procesamiento de facturas electrónicas!**