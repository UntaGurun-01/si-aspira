@echo off
title Start Both Panels - Si ASPIRA
echo ========================================================
echo   Si ASPIRA - START BOTH SERVERS
echo ========================================================
echo.
echo 1. Menjalankan Panel User (Mahasiswa) di Port 5000...
start "Panel User (Port 5000)" cmd /k "cd /d \"%~dp0\" && python app.py"

timeout /t 2 /nobreak >nul

echo 2. Menjalankan Panel Admin di Port 5001...
start "Panel Admin (Port 5001)" cmd /k "cd /d \"%~dp0panel admin\" && python app.py"

echo.
echo ========================================================
echo   Kedua server berhasil dijalankan di jendela terpisah!
echo   - Panel User  : http://localhost:5000
echo   - Panel Admin : http://localhost:5001
echo ========================================================
timeout /t 5
