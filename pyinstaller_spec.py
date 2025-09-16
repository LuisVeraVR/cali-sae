# -*- mode: python ; coding: utf-8 -*-
"""
Configuración optimizada de PyInstaller para evitar detección de antivirus
"""

import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

# Configuración de análisis con exclusiones específicas
a = Analysis(
    ['advanced_invoice_system.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Agregar archivos de datos legítimos si los hay
        # ('config.json', '.'),
        # ('README.md', '.'),
    ],
    hiddenimports=[
        # Imports específicos necesarios
        'pandas',
        'openpyxl', 
        'requests',
        'sqlite3',
        'tkinter',
        'tkinter.font',
        'tkinter.ttk',
        'xml.etree.ElementTree',
        'zipfile',
        'datetime',
        'threading',
        'pathlib',
        'hashlib',
        'json',
        'csv',
        'os',
        'sys',
        'platform',
        'logging',
        'time',
        'random'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Excluir módulos que pueden ser sospechosos o innecesarios
        'matplotlib',
        'scipy', 
        'numpy',
        'PIL',
        'Pillow',
        'cv2',
        'tensorflow',
        'torch',
        'sklearn',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'test',
        'unittest',
        'pdb',
        'pydoc',
        'distutils',
        'setuptools',
        'pip',
        'wheel',
        'pkg_resources',
        'pywin32',
        'win32api',
        'win32con',
        'win32gui',
        'win32process',
        'win32security',
        'win32service',
        'win32serviceutil',
        '_ssl',
        '_hashlib',
        '_ctypes',
        'multiprocessing',
        'concurrent.futures',
        'asyncio',
        'email',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna'
    ],
    noarchive=False,
    optimize=1,  # Nivel de optimización moderado
)

# Filtrar binarios sospechosos
a.binaries = [x for x in a.binaries if not any(
    suspicious in x[0].lower() for suspicious in [
        'libcrypto', 'libssl', 'openssl', 'crypto', 
        'win32', 'pythoncom', 'pywintypes', '_ssl'
    ]
)]

# Filtrar datos sospechosos  
a.datas = [x for x in a.datas if not any(
    suspicious in x[0].lower() for suspicious in [
        'test', 'example', 'sample', 'demo', 'debug'
    ]
)]

# Crear archivo PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Configuración del ejecutable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SistemaFacturas_v2.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # No usar strip para evitar comportamiento sospechoso
    upx=False,    # Desactivar UPX - puede ser detectado como empaquetador malicioso
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Aplicación de ventana
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Información de versión para Windows
    version='version_info.txt'
)

# Crear información de versión
version_info = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 1, 0, 0),
    prodvers=(2, 1, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Procesamiento de Documentos SAS'),
        StringStruct(u'FileDescription', u'Sistema de Facturas Electronicas DIAN'),
        StringStruct(u'FileVersion', u'2.1.0.0'),
        StringStruct(u'InternalName', u'SistemaFacturas'),
        StringStruct(u'LegalCopyright', u'Copyright 2024 - Uso Empresarial'),
        StringStruct(u'OriginalFilename', u'SistemaFacturas_v2.0.exe'),
        StringStruct(u'ProductName', u'Sistema de Facturas Electronicas'),
        StringStruct(u'ProductVersion', u'2.1.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

# Escribir archivo de información de versión
with open('version_info.txt', 'w') as f:
    f.write(version_info)

# Si queremos crear un directorio en lugar de un archivo único:
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=False,
#     upx_exclude=[],
#     name='SistemaFacturas_v2.0'
# )