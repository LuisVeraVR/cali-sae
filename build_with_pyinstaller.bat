@echo off
echo ================================
echo  CONSTRUYENDO CON PYINSTALLER
echo  Sistema de Facturas Electronicas v2.0
echo ================================

REM Verificar si PyInstaller está instalado
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

REM Verificar dependencias necesarias
echo Verificando dependencias...
python -c "import pandas, openpyxl, numpy, requests, sqlite3" 2>nul
if errorlevel 1 (
    echo Instalando dependencias faltantes...
    pip install pandas openpyxl numpy requests
)

REM Limpiar builds anteriores
echo Limpiando archivos anteriores...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"

REM Construir con PyInstaller
echo Construyendo ejecutable con PyInstaller...
pyinstaller ^
    --onedir ^
    --windowed ^
    --name "Sistema_Facturas_v2.0" ^
    --hidden-import pandas ^
    --hidden-import openpyxl ^
    --hidden-import numpy ^
    --hidden-import requests ^
    --hidden-import sqlite3 ^
    --hidden-import tkinter ^
    --hidden-import tkinter.font ^
    --hidden-import xml.etree.ElementTree ^
    --hidden-import zipfile ^
    --hidden-import datetime ^
    --hidden-import threading ^
    --hidden-import pathlib ^
    --hidden-import hashlib ^
    --hidden-import json ^
    --hidden-import csv ^
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
    --clean ^
    advanced_invoice_system.py

REM Verificar si la construcción fue exitosa
if exist "dist\Sistema_Facturas_v2.0" (
    echo.
    echo ================================
    echo  CONSTRUCCION EXITOSA!
    echo ================================
    echo.
    echo El ejecutable se encuentra en:
    echo dist\Sistema_Facturas_v2.0\
    echo.
    echo Archivo principal:
    echo Sistema_Facturas_v2.0.exe
    echo.
    echo Para distribuir, comprime toda la carpeta
    echo 'dist\Sistema_Facturas_v2.0'
    echo.
    
    REM Crear ZIP automáticamente
    echo Creando archivo ZIP para distribución...
    cd dist
    powershell "Compress-Archive -Path 'Sistema_Facturas_v2.0' -DestinationPath 'Sistema_Facturas_v2.0.zip' -Force"
    if exist "Sistema_Facturas_v2.0.zip" (
        echo.
        echo ZIP creado exitosamente: dist\Sistema_Facturas_v2.0.zip
        echo Tamaño del ZIP:
        dir "Sistema_Facturas_v2.0.zip" | find "Sistema_Facturas_v2.0.zip"
    )
    cd ..
    echo.
    echo Presiona cualquier tecla para abrir la carpeta dist...
    pause > nul
    explorer dist
) else (
    echo.
    echo ================================
    echo  ERROR EN LA CONSTRUCCION
    echo ================================
    echo.
    echo Revisa los errores mostrados arriba
    echo.
    pause
)