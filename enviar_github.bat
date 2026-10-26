@echo off
chcp 65001 > nul
echo ====================================================
echo      ENVIANDO PROJETO PARA O GITHUB
echo ====================================================
echo.
echo Repositório: https://github.com/matheusaraujogoncalvespinheiro-max/vbgvb.git
echo.

echo 1. Adicionando arquivos modificados e novos...
git add .

echo 2. Registrando commit com as alterações...
git commit -m "update: atualizacoes do jogo" > nul 2>&1

echo 3. Enviando para o GitHub...
echo (Se abrir uma janela no navegador, confirme para autorizar)
echo.
git push -u origin main
echo.

if %ERRORLEVEL% EQU 0 (
    echo ====================================================
    echo   PROJETO ENVIADO COM SUCESSO PARA O GITHUB!
    echo ====================================================
) else (
    echo.
    echo Ocorreu um erro ao enviar. Verifique a conexao e o login no GitHub.
)
pause
