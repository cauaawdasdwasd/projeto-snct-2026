@echo off
setlocal
cd /d "%~dp0"

where git >nul 2>nul
if errorlevel 1 (
    echo Git nao foi encontrado neste computador.
    pause
    exit /b 1
)

git rev-parse --is-inside-work-tree >nul 2>nul
if errorlevel 1 (
    echo Esta pasta ainda nao esta conectada ao GitHub.
    pause
    exit /b 1
)

echo Buscando atualizacoes no GitHub...
git fetch --prune origin
if errorlevel 1 goto :erro

git pull --ff-only origin main
if errorlevel 1 (
    echo.
    echo A atualizacao nao foi aplicada para proteger alteracoes locais.
    echo Abra o GitHub Desktop para conferir e resolver as diferencas.
    pause
    exit /b 1
)

echo.
echo Projeto atualizado com sucesso.
pause
exit /b 0

:erro
echo.
echo Nao foi possivel consultar o GitHub. Confira a internet e o login.
pause
exit /b 1
