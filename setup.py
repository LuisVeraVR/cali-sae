from cx_Freeze import setup, Executable
import sys
import os

# Dependencias que necesita incluir
build_exe_options = {
    "packages": [
        "tkinter", 
        "xml.etree.ElementTree", 
        "zipfile", 
        "pandas", 
        "openpyxl", 
        "datetime", 
        "threading",
        "pathlib",
        "hashlib",
        "json",
        "requests",
        "packaging"
    ],
    "excludes": [
        "test", 
        "unittest", 
        "email", 
        "html", 
        "http", 
        "urllib", 
        "xml.sax",
        "pydoc_data",
        "distutils"
    ],
    "include_files": [
        # Incluir archivos adicionales si es necesario
        # ("ruta/archivo", "archivo_destino")
    ],
    "optimize": 2,
    "zip_include_packages": ["*"],
    "zip_exclude_packages": []
}

# Configuración específica para Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Oculta la ventana de consola

# Configuración del ejecutable
executables = [
    Executable(
        "invoice_extractor.py",
        base=base,
        target_name="Sistema_Facturas_Electronicas.exe",
        icon=None,  # Puedes agregar un archivo .ico aquí
        copyright="2024 - Sistema de Facturas Electrónicas",
        trademarks="Procesamiento de Facturas DIAN"
    )
]

# Configuración del setup
setup(
    name="Sistema Facturas Electrónicas",
    version="1.0.0",
    description="Sistema para extracción de datos de facturas electrónicas DIAN",
    author="Tu Nombre/Empresa",
    author_email="contacto@empresa.com",
    options={"build_exe": build_exe_options},
    executables=executables
)
