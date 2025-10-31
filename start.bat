@echo off
echo ============================================================
echo  Price Tracker Pro - Starting...
echo ============================================================
echo.

python run.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo  Error occurred! Check the message above.
    echo ============================================================
    pause
)
