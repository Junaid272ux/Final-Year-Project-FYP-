@echo off
title VAM - Voice Assistant Module
color 0B
echo.
echo  ========================================================
echo   VAM - Voice Assistant Module
echo   Computer Assistant Using Python
echo   By Memoona Razzaq (2022-ag-6166)
echo   UAF Sub Campus, Toba Tek Singh
echo  ========================================================
echo.
echo  [*] Checking Python...
python --version
echo.
echo  [*] Installing requirements...
pip install -r requirements.txt --quiet
echo.
echo  [*] Starting VAM server...
echo  [*] Open your browser at: http://127.0.0.1:5000
echo.
start "" http://127.0.0.1:5000
python app.py
pause
