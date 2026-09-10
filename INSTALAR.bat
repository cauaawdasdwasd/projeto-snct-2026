@echo off
setlocal
title Instalar Sob Analise
pushd "%~dp0"

if exist ".venv\Scripts\python.exe" goto check_venv

py -3.11 -c "import struct; assert struct.calcsize('P') == 8" >nul 2>&1
if errorlevel 1 goto missing_python

py -3.11 -m venv .venv
if errorlevel 1 goto failed

:check_venv
".venv\Scripts\python.exe" -c "import sys, struct; assert sys.version_info[:2] == (3, 11) and struct.calcsize('P') == 8" >nul 2>&1
if errorlevel 1 goto incompatible_venv

".venv\Scripts\python.exe" -m pip install --only-binary=:all: -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip check
if errorlevel 1 goto failed

echo.
echo Instalacao concluida. Abra JOGAR.bat para iniciar.
if /i not "%~1"=="--no-pause" pause
popd
endlocal
exit /b 0

:missing_python
echo Instale o Python 3.11 de 64 bits com o Python Launcher.
echo Depois execute INSTALAR.bat novamente.
goto failed

:incompatible_venv
echo A pasta .venv existente nao usa Python 3.11 de 64 bits.
echo Renomeie essa pasta como backup e execute INSTALAR.bat novamente.
goto failed

:failed
echo.
echo Nao foi possivel preparar o ambiente. Confira o erro acima.
if /i not "%~1"=="--no-pause" pause
popd
endlocal
exit /b 1
