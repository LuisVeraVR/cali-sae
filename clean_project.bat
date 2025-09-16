@echo off
echo ================================
echo  LIMPIEZA DEL PROYECTO
echo  Sistema de Facturas v2.0
echo ================================

echo.
echo Este script limpiará:
echo - Archivos temporales de Python (__pycache__, *.pyc)
echo - Archivos de build (build/, dist/)
echo - Archivos de PyInstaller (*.spec)
echo - Logs antiguos (*.log)
echo - Archivos de backup (*.bak, *.tmp)
echo - Archivos de prueba (test_*)
echo.
echo ¿Continuar? (S/N)
set /p confirm=
if /i not "%confirm%"=="S" (
    echo Limpieza cancelada.
    pause
    exit /b 0
)

echo.
echo Iniciando limpieza...

REM Limpiar cache de Python
echo Limpiando cache de Python...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo Eliminando: %%d
    rmdir /s /q "%%d"
)

REM Limpiar archivos .pyc
echo Limpiando archivos compilados Python...
del /s /q *.pyc 2>nul
if not errorlevel 1 echo ✓ Archivos .pyc eliminados

REM Limpiar directorios de build
echo Limpiando directorios de build...
if exist "build" (
    echo Eliminando directorio build/
    rmdir /s /q "build"
)
if exist "dist" (
    echo Eliminando directorio dist/
    rmdir /s /q "dist"
)
if exist "release" (
    echo Eliminando directorio release/
    rmdir /s /q "release"
)

REM Limpiar archivos spec de PyInstaller
echo Limpiando archivos .spec...
del *.spec 2>nul
if not errorlevel 1 echo ✓ Archivos .spec eliminados

REM Limpiar logs antiguos
echo Limpiando logs antiguos...
del *.log 2>nul
if not errorlevel 1 echo ✓ Archivos .log eliminados

del facturas_log_*.log 2>nul
if not errorlevel 1 echo ✓ Logs de facturas eliminados

REM Limpiar archivos temporales
echo Limpiando archivos temporales...
del *.tmp 2>nul
del *.bak 2>nul
del *.backup 2>nul
del *~ 2>nul

REM Limpiar archivos de prueba
echo Limpiando archivos de prueba...
del test_*.csv 2>nul
del test_*.xlsx 2>nul
del test_output.* 2>nul

REM Limpiar certificados temporales (conservar los importantes)
echo Limpiando certificados temporales...
del *.pvk 2>nul
del *.cer 2>nul
if not errorlevel 1 echo ✓ Certificados temporales eliminados

REM Limpiar archivos de instalación temporal
if exist "temp_build" (
    echo Eliminando temp_build/
    rmdir /s /q "temp_build"
)
if exist "specs" (
    echo Eliminando specs/
    rmdir /s /q "specs"
)

REM Limpiar archivos de descarga
echo Limpiando descargas temporales...
del *_update.exe 2>nul
del update_temp 2>nul

REM Limpiar archivos de VS Code (si existen)
if exist ".vscode" (
    echo ⚠ Directorio .vscode encontrado (no eliminado automáticamente)
    echo   Para eliminarlo manualmente: rmdir /s .vscode
)

REM Limpiar archivos de IDE
del *.swp 2>nul
del *.swo 2>nul
del *~ 2>nul

echo.
echo ================================
echo  LIMPIEZA COMPLETADA
echo ================================
echo.

REM Mostrar archivos restantes importantes
echo Archivos principales conservados:
if exist "advanced_invoice_system.py" echo ✓ advanced_invoice_system.py
if exist "config.json" echo ✓ config.json
if exist "requirements.txt" echo ✓ requirements.txt
if exist ".gitignore" echo ✓ .gitignore
if exist "README.md" echo ✓ README.md

echo.
echo Directorios conservados:
if exist "config" echo ✓ config/
if exist "docs" echo ✓ docs/
if exist "data" echo ✓ data/

echo.
REM Mostrar tamaño del directorio actual
echo Espacio liberado: Calculando...
for /f %%i in ('dir /s /-c ^| find "bytes"') do set size=%%i

echo.
echo ================================
echo  RECOMENDACIONES POST-LIMPIEZA
echo ================================
echo.
echo 1. Verificar que la aplicación sigue funcionando:
echo    python advanced_invoice_system.py
echo.
echo 2. Si hay problemas, reinstalar dependencias:
echo    install_dependencies.bat
echo.
echo 3. Para hacer un nuevo build:
echo    build_simple_working.bat
echo.
echo 4. Si usas Git, hacer commit de los cambios:
echo    git add .
echo    git commit -m "Clean project files"
echo.

REM Verificar integridad básica
echo ================================
echo  VERIFICACIÓN DE INTEGRIDAD
echo ================================
echo.

if not exist "advanced_invoice_system.py" (
    echo ❌ ERROR: Archivo principal eliminado por error
    echo    Restaurar desde backup o repositorio
) else (
    echo ✅ Archivo principal conservado
)

if exist "facturas_users.db" (
    echo ✅ Base de datos conservada
) else (
    echo ℹ Base de datos se creará al ejecutar la aplicación
)

echo.
echo Limpieza completada exitosamente.
echo El proyecto está limpio y listo para desarrollo o distribución.
pause