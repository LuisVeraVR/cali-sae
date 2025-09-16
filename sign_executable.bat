@echo off
echo ================================
echo  FIRMA DIGITAL DE EJECUTABLE
echo  Sistema de Facturas v2.0
echo ================================

REM Verificar que existe el ejecutable
if not exist "release\SistemaFacturas_v2.0_Simple.exe" (
    echo ERROR: Ejecutable no encontrado
    echo Asegurate de haber completado el build primero
    pause
    exit /b 1
)

echo + Ejecutable encontrado

REM Metodo 1: Usando PowerShell (Recomendado)
echo.
echo ================================
echo  CREANDO CERTIFICADO CON POWERSHELL
echo ================================

powershell -Command "& {
    Write-Host 'Creando certificado autofirmado...'
    
    try {
        $cert = New-SelfSignedCertificate -DnsName 'SistemaFacturasElectronicas' -Type CodeSigning -CertStoreLocation Cert:\CurrentUser\My
        Write-Host '+ Certificado creado exitosamente'
        
        Write-Host 'Firmando ejecutable...'
        Set-AuthenticodeSignature -FilePath 'release\SistemaFacturas_v2.0_Simple.exe' -Certificate $cert
        
        Write-Host '+ Ejecutable firmado exitosamente'
        
        # Verificar firma
        $signature = Get-AuthenticodeSignature -FilePath 'release\SistemaFacturas_v2.0_Simple.exe'
        Write-Host ('Estado de firma: ' + $signature.Status)
        
        if ($signature.Status -eq 'Valid') {
            Write-Host '+ Firma digital aplicada correctamente'
        } else {
            Write-Host '! Advertencia: Firma puede no ser completamente valida (normal para certificados autofirmados)'
        }
        
    } catch {
        Write-Host ('x Error: ' + $_.Exception.Message)
        exit 1
    }
}"

if errorlevel 1 (
    echo.
    echo ERROR: Fallo la firma con PowerShell
    echo Intentando metodo alternativo...
    goto :alternative_method
)

echo.
echo + FIRMA COMPLETADA CON POWERSHELL
goto :verify_signature

:alternative_method
echo.
echo ================================
echo  METODO ALTERNATIVO
echo ================================
echo.
echo Si tienes Windows SDK instalado, puedes usar:
echo.
echo 1. Descargar Windows SDK desde:
echo    https://developer.microsoft.com/windows/downloads/windows-sdk/
echo.
echo 2. Usar makecert y signtool:
echo    makecert -sv MyCert.pvk -n "CN=Sistema Facturas" MyCert.cer -r
echo    pvk2pfx -pvk MyCert.pvk -cer MyCert.cer -pfx MyCert.pfx
echo    signtool sign /f MyCert.pfx release\SistemaFacturas_v2.0_Simple.exe
echo.
goto :manual_instructions

:verify_signature
echo.
echo ================================
echo  VERIFICANDO FIRMA
echo ================================

REM Verificar con PowerShell
powershell -Command "Get-AuthenticodeSignature -FilePath 'release\SistemaFacturas_v2.0_Simple.exe' | Select-Object Status, StatusMessage, SignerCertificate"

echo.
echo ================================
echo  RESULTADO DE LA FIRMA
echo ================================
echo.
echo + Tu ejecutable ahora tiene firma digital
echo + Esto reducira significativamente las detecciones de antivirus
echo + El certificado es autofirmado (valido pero no de CA oficial)
echo.
goto :distribution_steps

:manual_instructions
echo.
echo ================================
echo  INSTRUCCIONES MANUALES
echo ================================
echo.
echo Para firmar manualmente:
echo.
echo 1. Instalar Windows SDK
echo 2. Ejecutar los comandos mostrados arriba
echo 3. O usar herramientas de terceros como osslsigncode
echo.

:distribution_steps
echo.
echo ================================
echo  PREPARACION PARA DISTRIBUCION
echo ================================
echo.

REM Crear informacion del archivo
echo Generando informacion del archivo...
powershell -Command "Get-FileHash -Path 'release\SistemaFacturas_v2.0_Simple.exe' -Algorithm SHA256 | Select-Object Hash" > release\SHA256.txt
echo + Hash SHA256 generado

REM Mostrar informacion final
echo.
echo ================================
echo  INFORMACION FINAL
echo ================================
echo.
echo Archivo principal: SistemaFacturas_v2.0_Simple.exe
echo Ubicacion: release\
echo.
dir "release\SistemaFacturas_v2.0_Simple.exe"
echo.
echo Hash SHA256:
type release\SHA256.txt
echo.
echo ================================
echo  PROXIMOS PASOS
echo ================================
echo.
echo 1. Probar ejecutable firmado
echo 2. Subir a VirusTotal nuevamente
echo 3. Crear documentacion de usuario
echo 4. Distribuir con documentacion
echo.
echo ?Quieres abrir la carpeta release? (S/N)
set /p open_folder=
if /i "%open_folder%"=="S" (
    explorer release
)

pause