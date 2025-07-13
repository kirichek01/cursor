@echo off
echo ========================================
echo    MT5 Flask Server Launcher
echo ========================================
echo.

cd /d "%~dp0"
echo Current directory: %CD%

echo.
echo Installing dependencies...
pip install flask MetaTrader5 requests flet plotly pandas numpy

echo.
echo Starting MT5 Flask Server...
echo Server will be available at: http://localhost:5000
echo.

python mt5_server.py

echo.
echo Server stopped. Press any key to exit...
pause
