@echo off
chcp 65001 > nul
title LIVE BET CORE • Teste de Envio Discord
echo ==============================================================================
echo Disparando card de teste para o Discord (#cblol)...
echo ==============================================================================
echo.
python check_health.py --ping-discord
pause
