@echo off
echo Starting Roblox Voice Creator...
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Check .env
if not exist .env (
    echo .env file not found!
    echo Please copy .env.example to .env and add your API keys.
    pause
    exit /b 1
)

REM Run the application
python src\main.py %*

pause
