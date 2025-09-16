@echo off
echo ================================
echo  BUILD CON DEPENDENCIAS CORREGIDAS
echo  Sistema de Facturas v2.0
echo ================================

REM Verificar e instalar dependencias específicas
echo Verificando e instalando dependencias...
pip install --upgrade pip
pip install pandas openpyxl numpy requests sqlite3 packaging

REM Verificar instalación de numpy específicamente
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')" 
if errorlevel 1 (
    echo ERROR: NumPy no se pudo importar
    echo Instalando NumPy específicamente...
    pip install --force-reinstall numpy
)

REM Verificar pandas
python -c "import pandas; print(f'Pandas version: {pandas.__version__}')"
if errorlevel 1 (
    echo ERROR: Pandas no se pudo importar
    echo Instalando Pandas específicamente...
    pip install --force-reinstall pandas
)

REM Limpiar builds anteriores
echo Limpiando builds anteriores...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"

REM Crear archivo spec personalizado
echo Creando archivo spec con dependencias específicas...
echo # -*- mode: python ; coding: utf-8 -*- > sistema_facturas.spec
echo. >> sistema_facturas.spec
echo import sys >> sistema_facturas.spec
echo from PyInstaller.building.build_main import Analysis, PYZ, EXE >> sistema_facturas.spec
echo. >> sistema_facturas.spec
echo a = Analysis( >> sistema_facturas.spec
echo     ['advanced_invoice_system.py'], >> sistema_facturas.spec
echo     pathex=[], >> sistema_facturas.spec
echo     binaries=[], >> sistema_facturas.spec
echo     datas=[], >> sistema_facturas.spec
echo     hiddenimports=[ >> sistema_facturas.spec
echo         'pandas', >> sistema_facturas.spec
echo         'pandas._libs', >> sistema_facturas.spec
echo         'pandas._libs.tslibs', >> sistema_facturas.spec
echo         'pandas._libs.tslibs.base', >> sistema_facturas.spec
echo         'pandas._libs.tslibs.timezones', >> sistema_facturas.spec
echo         'pandas._libs.tslibs.nattype', >> sistema_facturas.spec
echo         'pandas._libs.tslibs.np_datetime', >> sistema_facturas.spec
echo         'pandas._libs.tslibs.timedeltas', >> sistema_facturas.spec
echo         'pandas._libs.tslibs.timestamps', >> sistema_facturas.spec
echo         'pandas.io', >> sistema_facturas.spec
echo         'pandas.io.formats', >> sistema_facturas.spec
echo         'pandas.io.formats.format', >> sistema_facturas.spec
echo         'pandas.io.common', >> sistema_facturas.spec
echo         'pandas.io.parsers', >> sistema_facturas.spec
echo         'pandas.core', >> sistema_facturas.spec
echo         'pandas.core.computation', >> sistema_facturas.spec
echo         'pandas.core.ops', >> sistema_facturas.spec
echo         'numpy', >> sistema_facturas.spec
echo         'numpy.core', >> sistema_facturas.spec
echo         'numpy.core._multiarray_umath', >> sistema_facturas.spec
echo         'numpy.core.multiarray', >> sistema_facturas.spec
echo         'numpy.core.umath', >> sistema_facturas.spec
echo         'numpy.linalg', >> sistema_facturas.spec
echo         'numpy.random', >> sistema_facturas.spec
echo         'openpyxl', >> sistema_facturas.spec
echo         'openpyxl.workbook', >> sistema_facturas.spec
echo         'openpyxl.worksheet', >> sistema_facturas.spec
echo         'openpyxl.styles', >> sistema_facturas.spec
echo         'requests', >> sistema_facturas.spec
echo         'sqlite3', >> sistema_facturas.spec
echo         'tkinter', >> sistema_facturas.spec
echo         'tkinter.font', >> sistema_facturas.spec
echo         'tkinter.ttk', >> sistema_facturas.spec
echo         'xml.etree.ElementTree', >> sistema_facturas.spec
echo         'zipfile', >> sistema_facturas.spec
echo         'datetime', >> sistema_facturas.spec
echo         'threading', >> sistema_facturas.spec
echo         'pathlib', >> sistema_facturas.spec
echo         'hashlib', >> sistema_facturas.spec
echo         'json', >> sistema_facturas.spec
echo         'csv', >> sistema_facturas.spec
echo         'packaging', >> sistema_facturas.spec
echo         'packaging.version', >> sistema_facturas.spec
echo     ], >> sistema_facturas.spec
echo     hookspath=[], >> sistema_facturas.spec
echo     hooksconfig={}, >> sistema_facturas.spec
echo     runtime_hooks=[], >> sistema_facturas.spec
echo     excludes=[ >> sistema_facturas.spec
echo         'matplotlib', >> sistema_facturas.spec
echo         'scipy', >> sistema_facturas.spec
echo         'PIL', >> sistema_facturas.spec
echo         'cv2', >> sistema_facturas.spec
echo         'tensorflow', >> sistema_facturas.spec
echo         'torch', >> sistema_facturas.spec
echo         'sklearn', >> sistema_facturas.spec
echo         'IPython', >> sistema_facturas.spec
echo         'jupyter', >> sistema_facturas.spec
echo         'notebook', >> sistema_facturas.spec
echo         'pytest', >> sistema_facturas.spec
echo         'test', >> sistema_facturas.spec
echo     ], >> sistema_facturas.spec
echo     noarchive=False, >> sistema_facturas.spec
echo     optimize=0, >> sistema_facturas.spec
echo ^) >> sistema_facturas.spec
echo. >> sistema_facturas.spec
echo pyz = PYZ^(a.pure^) >> sistema_facturas.spec
echo. >> sistema_facturas.spec
echo exe = EXE^( >> sistema_facturas.spec
echo     pyz, >> sistema_facturas.spec
echo     a.scripts, >> sistema_facturas.spec
echo     a.binaries, >> sistema_facturas.spec
echo     a.datas, >> sistema_facturas.spec
echo     [], >> sistema_facturas.spec
echo     name='Sistema_Facturas_v2.0', >> sistema_facturas.spec
echo     debug=False, >> sistema_facturas.spec
echo     bootloader_ignore_signals=False, >> sistema_facturas.spec
echo     strip=False, >> sistema_facturas.spec
echo     upx=False, >> sistema_facturas.spec
echo     upx_exclude=[], >> sistema_facturas.spec
echo     runtime_tmpdir=None, >> sistema_facturas.spec
echo     console=False, >> sistema_facturas.spec
echo     disable_windowed_traceback=False, >> sistema_facturas.spec
echo     argv_emulation=False, >> sistema_facturas.spec
echo     target_arch=None, >> sistema_facturas.spec
echo     codesign_identity=None, >> sistema_facturas.spec
echo     entitlements_file=None, >> sistema_facturas.spec
echo ^) >> sistema_facturas.spec

echo Archivo spec creado exitosamente

REM Build usando el archivo spec
echo Construyendo con archivo spec personalizado...
pyinstaller --clean --noconfirm sistema_facturas.spec

REM Verificar resultado
if exist "dist\Sistema_Facturas_v2.0.exe" (
    echo.
    echo ================================
    echo  BUILD EXITOSO CON DEPENDENCIAS
    echo ================================
    echo.
    echo Ejecutable: dist\Sistema_Facturas_v2.0.exe
    echo.
    echo Probando dependencias en el ejecutable...
    echo.
    
    REM Mostrar información del archivo
    dir "dist\Sistema_Facturas_v2.0.exe"
    echo.
    echo IMPORTANTE: Antes de distribuir, prueba el ejecutable
    echo para verificar que todas las dependencias funcionan.
    echo.
    pause
    explorer dist
) else (
    echo.
    echo ================================
    echo  ERROR EN EL BUILD
    echo ================================
    echo.
    echo Revisa los errores mostrados arriba.
    echo.
    echo Diagnósticos posibles:
    echo 1. Verificar que pandas y numpy estén instalados correctamente
    echo 2. Comprobar versiones de las dependencias
    echo 3. Reinstalar PyInstaller si es necesario
    echo.
    pause
)