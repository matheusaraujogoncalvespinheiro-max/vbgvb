@echo off
chcp 65001 > nul
echo ====================================================
echo      INICIANDO O JOGO (MODO DESENVOLVIMENTO)
echo ====================================================
"C:\Users\07881389109\AppData\Local\Programs\Python\Python311\python.exe" main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocorreu um erro ao executar o jogo.
    pause
)
