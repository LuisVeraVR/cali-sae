from cx_Freeze import setup, Executable
import sys
import os

# Configuración MÍNIMA - solo excluir lo realmente innecesario
build_exe_options = {
    "packages": [
        "tkinter", 
        "tkinter.font",
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
        "sqlite3",
        "csv"
    ],
    "excludes": [
        "test",
        "unittest", 
        "pydoc_data",
        "matplotlib",
        "numpy.distutils",
        "scipy",
        "IPython",
        "jupyter",
        "notebook"
    ],
    "include_files": [],
    "optimize": 1  # Cambiado a 1 para evitar sobre-optimización
}

# Configuración específica para Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Ejecutable
executables = [
    Executable(
        "advanced_invoice_system.py",
        base=base,
        target_name="Sistema_Facturas_v2.0.exe",
        icon=None,
        copyright="2024 - Sistema de Facturas Electrónicas v2.0"
    )
]

# Setup
setup(
    name="Sistema Facturas Electrónicas v2.0",
    version="2.1.0",
    description="Sistema avanzado para extracción de facturas electrónicas DIAN con autenticación",
    options={"build_exe": build_exe_options},
    executables=executables
)