@echo off
setlocal

set APP_NAME=Procesador de Resoluciones
set DIST_PATH=C:\My Software Folder
set EXE_PATH=%DIST_PATH%\%APP_NAME%.exe

echo ============================================================
echo  BUILD: %APP_NAME%
echo ============================================================

:: Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
) else (
    echo Advertencia: no se encontro entorno virtual, usando Python del sistema.
)

:: Eliminar ejecutable anterior si existe
if exist "%EXE_PATH%" (
    echo Eliminando version anterior: %EXE_PATH%
    del /f /q "%EXE_PATH%"
)

:: Limpiar carpetas de build anteriores
echo Limpiando carpetas de build anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist"  rmdir /s /q "dist"

:: Ejecutar PyInstaller
echo Compilando...
pyinstaller --onefile --windowed ^
    --name "%APP_NAME%" ^
    --distpath "%DIST_PATH%" ^
    --icon="assets/icon.ico" ^
    --add-data "assets;assets" ^
    --add-data "config.json;." ^
    launcher.py

:: Verificar resultado
if exist "%EXE_PATH%" (
    echo.
    echo ============================================================
    echo  BUILD EXITOSO
    echo  Ejecutable generado en: %EXE_PATH%
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo  ERROR: No se genero el ejecutable. Revisa los errores.
    echo ============================================================
    exit /b 1
)

endlocal
pause
