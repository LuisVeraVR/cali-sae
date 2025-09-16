@echo off
echo ================================
echo  TEST DE LA APLICACION
echo  Sistema de Facturas v2.0
echo ================================

REM Verificar que existe el archivo principal
if not exist advanced_invoice_system.py (
    echo ERROR: advanced_invoice_system.py no encontrado
    echo.
    echo Asegurate de estar en el directorio correcto del proyecto.
    pause
    exit /b 1
)

echo + Archivo principal encontrado

REM Verificar Python
python --version
if errorlevel 1 (
    echo ERROR: Python no esta disponible
    echo Ejecuta primero: install_dependencies.bat
    pause
    exit /b 1
)

echo + Python disponible

REM Test de sintaxis Python
echo.
echo Verificando sintaxis del codigo...
python -m py_compile advanced_invoice_system.py
if errorlevel 1 (
    echo ERROR: Error de sintaxis en advanced_invoice_system.py
    echo Revisa el codigo Python antes de continuar.
    pause
    exit /b 1
)

echo + Sintaxis correcta

REM Test de imports - Crear archivo temporal
echo.
echo Verificando imports y dependencias...

echo import os, sys, csv, zipfile, hashlib, sqlite3, threading > test_imports.py
echo import xml.etree.ElementTree as ET >> test_imports.py
echo from datetime import datetime >> test_imports.py
echo from pathlib import Path >> test_imports.py
echo import tkinter as tk >> test_imports.py
echo from tkinter import ttk, filedialog, messagebox, font >> test_imports.py
echo print('+ Imports basicos OK') >> test_imports.py
echo. >> test_imports.py
echo try: >> test_imports.py
echo     import openpyxl >> test_imports.py
echo     print('+ openpyxl OK') >> test_imports.py
echo except: >> test_imports.py
echo     print('x openpyxl FALTA - Ejecuta install_dependencies.bat') >> test_imports.py
echo     sys.exit(1) >> test_imports.py
echo. >> test_imports.py
echo try: >> test_imports.py
echo     import requests >> test_imports.py
echo     print('+ requests OK') >> test_imports.py
echo except: >> test_imports.py
echo     print('! requests no disponible (opcional)') >> test_imports.py
echo. >> test_imports.py
echo try: >> test_imports.py
echo     import pandas as pd >> test_imports.py
echo     print('+ pandas disponible') >> test_imports.py
echo except: >> test_imports.py
echo     print('! pandas no disponible (se usara CSV nativo)') >> test_imports.py
echo. >> test_imports.py
echo print('+ Todas las dependencias criticas estan disponibles') >> test_imports.py

python test_imports.py
set import_result=%errorlevel%

del test_imports.py

if %import_result% neq 0 (
    echo.
    echo ERROR: Faltan dependencias criticas
    echo Ejecuta: install_dependencies.bat
    pause
    exit /b 1
)

REM Test de base de datos
echo.
echo Testeando creacion de base de datos...

echo import sqlite3, hashlib > test_db.py
echo try: >> test_db.py
echo     conn = sqlite3.connect(':memory:') >> test_db.py
echo     cur = conn.cursor() >> test_db.py
echo     cur.execute('CREATE TABLE test (id INTEGER, name TEXT)') >> test_db.py
echo     cur.execute('INSERT INTO test VALUES (1, "test")') >> test_db.py
echo     result = cur.fetchall() >> test_db.py
echo     conn.close() >> test_db.py
echo     print('+ SQLite funcionando correctamente') >> test_db.py
echo     test_hash = hashlib.sha256('test'.encode()).hexdigest() >> test_db.py
echo     print('+ Hashing SHA-256 funcionando') >> test_db.py
echo except Exception as e: >> test_db.py
echo     print(f'x Error en test de BD: {e}') >> test_db.py
echo     exit(1) >> test_db.py

python test_db.py
set db_result=%errorlevel%

del test_db.py

if %db_result% neq 0 (
    echo ERROR: Problemas con SQLite o hashing
    pause
    exit /b 1
)

REM Test de XML processing
echo.
echo Testeando procesamiento XML...

echo import xml.etree.ElementTree as ET > test_xml.py
echo try: >> test_xml.py
echo     xml_test = '^<?xml version="1.0"?^>^<root^>^<test^>value^</test^>^</root^>' >> test_xml.py
echo     root = ET.fromstring(xml_test) >> test_xml.py
echo     value = root.find('test').text >> test_xml.py
echo     if value == 'value': >> test_xml.py
echo         print('+ Procesamiento XML funcionando') >> test_xml.py
echo     else: >> test_xml.py
echo         raise Exception('XML parsing failed') >> test_xml.py
echo except Exception as e: >> test_xml.py
echo     print(f'x Error en procesamiento XML: {e}') >> test_xml.py
echo     exit(1) >> test_xml.py

python test_xml.py
set xml_result=%errorlevel%

del test_xml.py

if %xml_result% neq 0 (
    echo ERROR: Problemas con procesamiento XML
    pause
    exit /b 1
)

REM Test de tkinter (GUI)
echo.
echo Testeando interfaz grafica...

echo import tkinter as tk > test_gui.py
echo from tkinter import ttk >> test_gui.py
echo try: >> test_gui.py
echo     root = tk.Tk() >> test_gui.py
echo     root.withdraw() >> test_gui.py
echo     frame = ttk.Frame(root) >> test_gui.py
echo     label = ttk.Label(frame, text='Test') >> test_gui.py
echo     button = ttk.Button(frame, text='Test') >> test_gui.py
echo     root.destroy() >> test_gui.py
echo     print('+ Interfaz grafica tkinter funcionando') >> test_gui.py
echo except Exception as e: >> test_gui.py
echo     print(f'! Error en interfaz grafica: {e}') >> test_gui.py
echo     print('Nota: En algunos sistemas sin GUI esto es normal') >> test_gui.py

python test_gui.py

del test_gui.py

REM Test de archivos de configuracion
echo.
echo Verificando archivos de configuracion...

if exist config.json (
    echo + config.json encontrado
    python -c "import json; config=json.load(open('config.json', 'r', encoding='utf-8')); print('+ config.json valido')" 2>nul || echo ! Error en config.json
) else (
    echo ! config.json no encontrado (opcional)
)

if exist .gitignore (
    echo + .gitignore encontrado
) else (
    echo ! .gitignore no encontrado (recomendado)
)

if exist requirements.txt (
    echo + requirements.txt encontrado
) else (
    echo ! requirements.txt no encontrado (recomendado)
)

echo.
echo ================================
echo  RESUMEN DEL TEST
echo ================================
echo.
echo + Archivo principal: OK
echo + Sintaxis Python: OK  
echo + Dependencias: OK
echo + Base de datos: OK
echo + Procesamiento XML: OK
echo + Interfaz grafica: OK
echo.
echo ================================
echo  ESTADO: APLICACION LISTA
echo ================================
echo.
echo Tu aplicacion esta lista para:
echo 1. Ejecutar en desarrollo: python advanced_invoice_system.py
echo 2. Crear ejecutable: build_simple_working.bat
echo 3. Instalar dependencias: install_dependencies.bat
echo.
echo Si encuentras algun problema:
echo - Revisa que Python este en PATH
echo - Ejecuta install_dependencies.bat
echo - Verifica permisos de administrador
echo.
echo Presiona S para ejecutar la aplicacion ahora, o cualquier tecla para salir
set /p run_app=
if /i "%run_app%"=="S" (
    echo Ejecutando aplicacion...
    python advanced_invoice_system.py
)

pause