@echo off
echo ================================
echo  INSTALACIÓN DE DEPENDENCIAS
echo  Sistema de Facturas v2.0
echo ================================

REM Verificar Python
python --version
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en PATH
    echo.
    echo Descarga Python desde: https://python.org/downloads/
    echo Asegúrate de marcar "Add Python to PATH" durante la instalación
    pause
    exit /b 1
)

echo ✓ Python encontrado

REM Verificar pip
pip --version
if errorlevel 1 (
    echo ERROR: pip no está disponible
    echo Instalando pip...
    python -m ensurepip --upgrade
    if errorlevel 1 (
        echo ERROR: No se pudo instalar pip
        pause
        exit /b 1
    )
)

echo ✓ pip encontrado

REM Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias desde requirements.txt
echo.
echo Instalando dependencias desde requirements.txt...
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Falló la instalación desde requirements.txt
        echo Intentando instalación manual...
        goto :manual_install
    )
    echo ✓ Dependencias instaladas desde requirements.txt
    goto :verify
) else (
    echo ADVERTENCIA: requirements.txt no encontrado
    echo Procediendo con instalación manual...
    goto :manual_install
)

:manual_install
echo.
echo ================================
echo  INSTALACIÓN MANUAL
echo ================================
echo.

echo Instalando openpyxl...
pip install openpyxl>=3.1.0
if errorlevel 1 (
    echo ERROR: No se pudo instalar openpyxl
    goto :error
)

echo Instalando requests...
pip install requests>=2.28.0
if errorlevel 1 (
    echo ERROR: No se pudo instalar requests
    goto :error
)

echo Instalando packaging...
pip install packaging>=21.0
if errorlevel 1 (
    echo ERROR: No se pudo instalar packaging
    goto :error
)

echo Instalando pyinstaller...
pip install pyinstaller>=5.10.0
if errorlevel 1 (
    echo ERROR: No se pudo instalar pyinstaller
    goto :error
)

:verify
echo.
echo ================================
echo  VERIFICACIÓN DE INSTALACIÓN
echo ================================
echo.

echo Verificando openpyxl...
python -c "import openpyxl; print(f'✓ openpyxl {openpyxl.__version__} OK')"
if errorlevel 1 (
    echo ✗ openpyxl FALLO
    goto :error
)

echo Verificando requests...
python -c "import requests; print(f'✓ requests {requests.__version__} OK')"
if errorlevel 1 (
    echo ✗ requests FALLO
    goto :error
)

echo Verificando packaging...
python -c "import packaging; print(f'✓ packaging {packaging.__version__} OK')"
if errorlevel 1 (
    echo ✗ packaging FALLO
    goto :error
)

echo Verificando pyinstaller...
pyinstaller --version
if errorlevel 1 (
    echo ✗ pyinstaller FALLO
    goto :error
)
echo ✓ pyinstaller OK

echo.
echo Verificando módulos del sistema...
python -c "import tkinter; print('✓ tkinter OK')" || echo ✗ tkinter FALLO
python -c "import sqlite3; print('✓ sqlite3 OK')" || echo ✗ sqlite3 FALLO
python -c "import xml.etree.ElementTree; print('✓ xml OK')" || echo ✗ xml FALLO
python -c "import zipfile; print('✓ zipfile OK')" || echo ✗ zipfile FALLO
python -c "import csv; print('✓ csv OK')" || echo ✗ csv FALLO
python -c "import json; print('✓ json OK')" || echo ✗ json FALLO
python -c "import hashlib; print('✓ hashlib OK')" || echo ✗ hashlib FALLO
python -c "import datetime; print('✓ datetime OK')" || echo ✗ datetime FALLO
python -c "import threading; print('✓ threading OK')" || echo ✗ threading FALLO

echo.
echo ================================
echo  INSTALACIÓN COMPLETADA
echo ================================
echo.
echo ✓ Todas las dependencias han sido instaladas correctamente
echo.
echo Próximos pasos:
echo 1. Ejecutar: python advanced_invoice_system.py (para desarrollo)
echo 2. O ejecutar: build_simple_working.bat (para crear ejecutable)
echo.
pause
goto :end

:error
echo.
echo ================================
echo  ERROR EN LA INSTALACIÓN
echo ================================
echo.
echo Algunas dependencias no se pudieron instalar correctamente.
echo.
echo Soluciones posibles:
echo 1. Verificar conexión a internet
echo 2. Ejecutar como administrador
echo 3. Actualizar pip: python -m pip install --upgrade pip
echo 4. Crear entorno virtual: python -m venv venv
echo 5. Activar entorno: venv\Scripts\activate
echo 6. Intentar instalación nuevamente
echo.
echo Si el problema persiste, instalar manualmente:
echo pip install openpyxl requests packaging pyinstaller
echo.
pause

:end