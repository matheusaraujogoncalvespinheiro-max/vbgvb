@echo off
chcp 65001 > nul
echo ====================================================
echo      ENVIANDO PROJETO PARA O GITHUB
echo ====================================================
echo.
echo Repositório: https://github.com/matheusaraujogoncalvespinheiro-max/vbgvb.git
echo.
echo Se abrir uma janela do navegador ou do GitHub, clique em "Sign in with your browser" para autorizar.
echo.
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo ====================================================
    echo   PROJETO ENVIADO COM SUCESSO PARA O GITHUB!
    echo ====================================================
) else (
    echo.
    echo Ocorreu um erro ao enviar. Verifique o login no GitHub.
)
pause
