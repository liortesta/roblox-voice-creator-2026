@echo off
chcp 65001 >nul
title Voice Creator - Kids Edition
echo =======================================
echo    Voice Creator - Kids Edition
echo =======================================
echo.
cd /d "%~dp0"
python src/kids_interface.py
pause
