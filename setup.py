from cx_Freeze import setup, Executable
import sys
import os

# Configuración MÍNIMA - solo excluir lo realmente innecesario
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
        "requests"
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
        "invoice_extractor.py",
        base=base,
        target_name="Sistema_Facturas_Electronicas.exe",
        icon=None,
        copyright="2024 - Sistema de Facturas Electrónicas"
    )
]

# Setup
setup(
    name="Sistema Facturas Electrónicas",
    version="1.0.0",
    description="Sistema para extracción de facturas electrónicas DIAN",
    options={"build_exe": build_exe_options},
    executables=executables
)