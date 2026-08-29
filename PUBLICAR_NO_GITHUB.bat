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

echo Arquivos alterados:
git status --short
echo.
set /p "MENSAGEM=Descreva brevemente a alteracao: "
if not defined MENSAGEM set "MENSAGEM=Atualiza o projeto Sob Analise"

git add -A
git diff --cached --quiet
if not errorlevel 1 (
    echo.
    echo Nao ha alteracoes novas para publicar.
    pause
    exit /b 0
)

git commit -m "%MENSAGEM%"
if errorlevel 1 goto :erro

echo.
echo Sincronizando antes de enviar...
git pull --rebase origin main
if errorlevel 1 (
    echo.
    echo A sincronizacao encontrou um conflito. Nada foi enviado.
    echo Abra o GitHub Desktop para resolver o conflito com seguranca.
    pause
    exit /b 1
)

git push origin main
if errorlevel 1 goto :erro

echo.
echo Alteracoes publicadas com sucesso.
pause
exit /b 0

:erro
echo.
echo Nao foi possivel publicar. Confira o login e tente novamente.
pause
exit /b 1
