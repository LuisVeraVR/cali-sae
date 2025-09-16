# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['advanced_invoice_system.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['openpyxl', 'openpyxl.workbook', 'openpyxl.worksheet', 'openpyxl.styles', 'requests', 'sqlite3', 'tkinter', 'tkinter.font', 'tkinter.ttk', 'xml.etree.ElementTree', 'zipfile', 'datetime', 'threading', 'pathlib', 'hashlib', 'json', 'csv'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pandas', 'numpy', 'matplotlib', 'scipy', 'PIL', 'cv2', 'tensorflow', 'torch', 'sklearn', 'IPython', 'jupyter', 'notebook', 'pytest', 'test', 'unittest', 'pdb', 'pydoc'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SistemaFacturas_v2.0_Simple',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
