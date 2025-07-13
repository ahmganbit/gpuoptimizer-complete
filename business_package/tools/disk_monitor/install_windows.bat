@echo off
echo ========================================
echo Professional Disk Space Monitor
echo Windows Installation Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Creating configuration file...
if not exist config.json (
    python disk_monitor.py --init
)

echo.
echo Creating reports directory...
if not exist reports mkdir reports

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit config.json with your settings
echo 2. Configure email settings for alerts
echo 3. Run: python disk_monitor.py --once
echo 4. For continuous monitoring: python disk_monitor.py --daemon
echo.
pause 