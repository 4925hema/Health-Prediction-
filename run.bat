@echo off
echo ========================================
echo Student Health Monitoring System
echo Python + Flask + Machine Learning
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found! Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.
echo Starting the application...
echo.
echo The web interface will open at: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.

python app.py

pause
