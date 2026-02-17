@echo off
cd /d "%~dp0"
echo ---------------------------------------
echo Starting AstroPulse Gold...
echo ---------------------------------------

REM Попытка активации виртуального окружения, если оно есть в папке выше
if exist "..\venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call ..\venv\Scripts\activate
)

echo Launching Streamlit...
streamlit run main.py

if %errorlevel% neq 0 (
    echo.
    echo ---------------------------------------
    echo ERROR: Failed to launch application.
    echo Make sure you have installed libraries: pip install -r requirements.txt
    echo ---------------------------------------
    pause
    exit /b
)
pause
