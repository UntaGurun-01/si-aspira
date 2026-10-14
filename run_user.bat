@echo off
title Panel User - Si ASPIRA (PORT 5000)
echo ========================================================
echo   Si ASPIRA - PANEL USER (MAHASISWA)
echo ========================================================
echo.
echo Memulai server Panel User di http://localhost:5000 ...
echo Buka di browser: http://localhost:5000
echo.
cd /d "%~dp0"
python app.py
pause
