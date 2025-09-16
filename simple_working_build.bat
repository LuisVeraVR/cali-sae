@echo off
echo ================================
echo  BUILD SIMPLE Y FUNCIONAL
echo  Sin problemas de dependencias
echo ================================

REM Verificar Python
python --version
if errorlevel 1 (
    echo ERROR: Python no encontrado
    pause
    exit /b 1
)

REM Instalar solo las dependencias esenciales
echo Instalando dependencias básicas...
pip install --upgrade pip
pip install pyinstaller
pip install openpyxl
pip install requests

REM Verificar instalaciones
echo Verificando instalaciones...
python -c "import openpyxl; print('✓ openpyxl OK')"
python -c "import requests; print('✓ requests OK')"
python -c "import tkinter; print('✓ tkinter OK')"
python -c "import sqlite3; print('✓ sqlite3 OK')"

REM Limpiar builds anteriores
echo Limpiando builds anteriores...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
del *.spec 2>nul

REM Build básico sin pandas (más estable)
echo.
echo ================================
echo  CONSTRUYENDO SIN PANDAS
echo ================================
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "SistemaFacturas_v2.0_Simple" ^
    --icon=NONE ^
    --distpath "release" ^
    --hidden-import openpyxl ^
    --hidden-import openpyxl.workbook ^
    --hidden-import openpyxl.worksheet ^
    --hidden-import openpyxl.styles ^
    --hidden-import requests ^
    --hidden-import sqlite3 ^
    --hidden-import tkinter ^
    --hidden-import tkinter.font ^
    --hidden-import tkinter.ttk ^
    --hidden-import xml.etree.ElementTree ^
    --hidden-import zipfile ^
    --hidden-import datetime ^
    --hidden-import threading ^
    --hidden-import pathlib ^
    --hidden-import hashlib ^
    --hidden-import json ^
    --hidden-import csv ^
    --exclude-module pandas ^
    --exclude-module numpy ^
    --exclude-module matplotlib ^
    --exclude-module scipy ^
    --exclude-module PIL ^
    --exclude-module cv2 ^
    --exclude-module tensorflow ^
    --exclude-module torch ^
    --exclude-module sklearn ^
    --exclude-module IPython ^
    --exclude-module jupyter ^
    --exclude-module notebook ^
    --exclude-module pytest ^
    --exclude-module test ^
    --exclude-module unittest ^
    --exclude-module pdb ^
    --exclude-module pydoc ^
    --clean ^
    --noconfirm ^
    --strip ^
    --noupx ^
    advanced_invoice_system.py

echo.
echo ================================
echo  VERIFICANDO RESULTADO
echo ================================

if exist "release\SistemaFacturas_v2.0_Simple.exe" (
    echo.
    echo ✓ BUILD EXITOSO
    echo.
    echo Archivo: release\SistemaFacturas_v2.0_Simple.exe
    echo.
    
    REM Mostrar tamaño del archivo
    dir "release\SistemaFacturas_v2.0_Simple.exe" | find "SistemaFacturas_v2.0_Simple.exe"
    
    echo.
    echo ================================
    echo  PASOS SIGUIENTES
    echo ================================
    echo.
    echo 1. Probar el ejecutable en esta máquina
    echo 2. Probar en máquina limpia (sin Python)
    echo 3. Subir a VirusTotal.com para verificar
    echo 4. Si funciona bien, proceder con firma digital
    echo.
    echo ¿Quieres probar el ejecutable ahora? (S/N)
    set /p test_choice=
    
    if /i "%test_choice%"=="S" (
        echo Ejecutando aplicación...
        cd release
        start SistemaFacturas_v2.0_Simple.exe
        cd ..
    )
    
    echo.
    pause
    explorer release
    
) else (
    echo.
    echo ✗ BUILD FALLÓ
    echo.
    echo Posibles causas:
    echo 1. Archivo principal no encontrado
    echo 2. Error en el código Python
    echo 3. Problema con PyInstaller
    echo.
    echo Revisa los errores mostrados arriba
    echo.
    pause
)

echo.
echo ================================
echo  CONSEJOS PARA DISTRIBUCIÓN
echo ================================
echo.
echo ✓ Archivo sin pandas = Menor tamaño y más estable
echo ✓ Funciones CSV nativas = Sin dependencias externas  
echo ✓ Solo librerías estándar = Menos detecciones antivirus
echo.
echo Próximos pasos recomendados:
echo 1. Firmar digitalmente el ejecutable
echo 2. Crear documentación de usuario
echo 3. Probar en diferentes versiones de Windows
echo.
pause