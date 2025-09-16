@echo off
echo ================================
echo  CREACIÓN DE CERTIFICADO Y FIRMA
echo ================================

REM Verificar si existe signtool (parte de Windows SDK)
where signtool >nul 2>&1
if errorlevel 1 (
    echo ADVERTENCIA: signtool no encontrado
    echo Descarga Windows SDK desde:
    echo https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
    echo.
    echo Alternativa: Usar PowerShell para firma básica
    goto :powershell_sign
)

REM Crear certificado autofirmado
echo Creando certificado autofirmado...
makecert -sv "SistemaFacturas.pvk" -n "CN=Sistema Facturas Electronicas" "SistemaFacturas.cer" -b 01/01/2024 -e 01/01/2026 -r

REM Convertir a PFX
echo Convirtiendo certificado...
pvk2pfx -pvk "SistemaFacturas.pvk" -cer "SistemaFacturas.cer" -pfx "SistemaFacturas.pfx"

REM Firmar el ejecutable
echo Firmando ejecutable...
signtool sign /f "SistemaFacturas.pfx" /t http://timestamp.digicert.com "release\SistemaFacturas_v2.0.exe"

echo.
echo FIRMA COMPLETADA
goto :end

:powershell_sign
echo.
echo Usando PowerShell para crear certificado básico...
powershell -Command "& { ^
    $cert = New-SelfSignedCertificate -DnsName 'SistemaFacturas' -Type CodeSigning -CertStoreLocation Cert:\CurrentUser\My; ^
    $password = ConvertTo-SecureString -String 'facturas2024' -Force -AsPlainText; ^
    Export-PfxCertificate -Cert $cert -FilePath 'SistemaFacturas.pfx' -Password $password; ^
    Set-AuthenticodeSignature -FilePath 'release\SistemaFacturas_v2.0.exe' -Certificate $cert ^
}"

:end
echo.
echo ================================
echo  PROCESO COMPLETADO
echo ================================
echo.
echo El ejecutable ha sido firmado digitalmente
echo Esto reducirá significativamente las detecciones
echo.
pause