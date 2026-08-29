@echo off
setlocal
title Sob Analise

pushd "%~dp0"

if exist ".venv\Scripts\python.exe" goto run_venv

py -3.11 --version >nul 2>&1
if not errorlevel 1 goto run_py311

python --version >nul 2>&1
if not errorlevel 1 goto run_python

echo.
echo Python nao foi encontrado neste computador.
echo Instale o Python 3.11 ou superior para executar Sob Analise.
goto failed

:run_venv
".venv\Scripts\python.exe" main.py
goto finished

:run_py311
py -3.11 main.py
goto finished

:run_python
python main.py

:finished
if not errorlevel 1 goto success

echo.
echo O jogo foi encerrado por causa de um erro.
echo Confira se as dependencias foram instaladas com:
echo pip install -r requirements.txt

:failed
echo.
pause
popd
exit /b 1

:success
popd
endlocal
exit /b 0
