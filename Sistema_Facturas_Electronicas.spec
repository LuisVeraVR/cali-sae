# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['invoice_extractor.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pandas', 'openpyxl', 'numpy', 'requests', 'tkinter', 'xml.etree.ElementTree', 'zipfile', 'datetime', 'threading', 'pathlib', 'hashlib', 'json'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'PIL', 'cv2', 'tensorflow', 'torch', 'sklearn', 'IPython', 'jupyter', 'notebook', 'pytest', 'test'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Sistema_Facturas_Electronicas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Sistema_Facturas_Electronicas',
)
