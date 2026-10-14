@echo off
title Panel Admin - Si ASPIRA (PORT 5001)
echo ========================================================
echo   Si ASPIRA - PANEL ADMIN (PORT 5001)
echo ========================================================
echo.
echo Memulai server Panel Admin di http://localhost:5001 ...
echo Buka di browser: http://localhost:5001
echo.
cd /d "%~dp0"
python app.py
pause
