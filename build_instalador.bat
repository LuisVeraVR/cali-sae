@echo off
echo ================================
echo  CONSTRUYENDO INSTALADOR
echo  Sistema de Facturas Electronicas
echo ================================

REM Limpiar builds anteriores
echo Limpiando archivos anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Instalar dependencias si es necesario
echo Verificando dependencias...
pip install cx_Freeze pandas openpyxl requests packaging

REM Construir el ejecutable
echo Construyendo ejecutable...
python setup.py build

REM Verificar si la construcción fue exitosa
if exist "build" (
    echo.
    echo ================================
    echo  CONSTRUCCION EXITOSA!
    echo ================================
    echo.
    echo El ejecutable se encuentra en la carpeta 'build'
    echo Archivo principal: Sistema_Facturas_Electronicas.exe
    echo.
    echo Para distribuir, comprime toda la carpeta 'build'
    echo y enviala a los usuarios finales.
    echo.
    pause
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
