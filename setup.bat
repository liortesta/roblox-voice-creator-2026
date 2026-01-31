@echo off
echo ==========================================
echo   Roblox Voice Creator - Setup
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some packages may have failed to install
    echo PyAudio might need manual installation on Windows
    echo Try: pip install pipwin ^&^& pipwin install pyaudio
)

echo [4/4] Creating .env file...
if not exist .env (
    copy .env.example .env
    echo Created .env file - please edit it with your API keys!
) else (
    echo .env file already exists
)

echo.
echo ==========================================
echo   Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run: run.bat
echo.
pause
