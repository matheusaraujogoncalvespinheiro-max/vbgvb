@echo off
chcp 65001 > nul
echo ====================================================
echo        GERANDO EXECUTÁVEL DO JOGO (.EXE)
echo ====================================================
echo.
echo Compilando com PyInstaller... Por favor aguarde...

"C:\Users\07881389109\AppData\Local\Programs\Python\Python311\Scripts\pyinstaller.exe" --noconfirm --onedir --windowed --name "MeuJogo" --add-data "parte principal do jogo.mp4;." --add-data "background_reverse.mp4;." main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================================
    echo   EXECUTÁVEL GERADO COM SUCESSO NA PASTA dist\MeuJogo!
    echo ====================================================
) else (
    echo.
    echo Houve um erro ao gerar o executável.
)
pause
