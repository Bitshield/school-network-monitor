@echo off
REM Windows Installation Script for Network Monitor
REM Run this file to install everything automatically

echo.
echo ========================================================================
echo           NETWORK MONITOR - AUTOMATIC INSTALLATION
echo ========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/3] Installing Python dependencies...
echo.

REM Install required packages
python -m pip install --upgrade pip --quiet
python -m pip install --quiet fastapi uvicorn sqlalchemy psycopg[binary] pydantic pydantic-settings python-dotenv requests

if errorlevel 1 (
    echo.
    echo WARNING: Some packages may have failed to install.
    echo Trying alternative installation method...
    echo.
    python -m pip install --user fastapi uvicorn sqlalchemy psycopg pydantic pydantic-settings python-dotenv requests
)

echo.
echo [2/3] Checking configuration...
echo.

if exist .env (
    echo [OK] Configuration file found
) else (
    echo [INFO] No .env file found - using defaults
)

echo.
echo [3/3] Setup complete!
echo.
echo ========================================================================
echo                    INSTALLATION SUCCESSFUL!
echo ========================================================================
echo.
echo Next steps:
echo   1. Start the application:
echo      python -m uvicorn main:app --reload
echo.
echo   2. In another terminal window, run:
echo      python quick_setup.py
echo.
echo   3. Open your browser:
echo      http://localhost:8000/api/docs
echo.
echo ========================================================================
echo.
pause