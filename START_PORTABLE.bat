@echo off
setlocal enabledelayedexpansion
title MoneyPrinterTurbo - 5X Master Video Engine

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"
echo ==============================================================
echo       🎬 5X MASTER DOCUMENTARY & VIDEO ENGINE 🎬
echo ==============================================================
echo Project Directory: %PROJECT_DIR%

:: 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found on this PC!
    echo Please install Python 3.11 from python.org or run:
    echo winget install Python.Python.3.11
    pause
    exit /b 1
)

:: 2. Check FFmpeg
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg is not found in system PATH.
    echo Video rendering requires FFmpeg. You can install it via:
    echo winget install Gyan.FFmpeg
    echo.
)

:: 3. Check and Repair .venv if copied from another PC
set "RECREATE_VENV=0"
if exist ".venv" (
    if exist ".venv\pyvenv.cfg" (
        for /f "tokens=1,* delims==" %%A in (.venv\pyvenv.cfg) do (
            set "KEY=%%A"
            set "VAL=%%B"
            set "KEY=!KEY: =!"
            if /i "!KEY!"=="home" (
                set "PY_HOME=!VAL:~1!"
                if not exist "!PY_HOME!" (
                    echo [NOTICE] This folder was copied from another PC.
                    echo Resetting .venv for this new PC...
                    set "RECREATE_VENV=1"
                )
            )
        )
    )
) else (
    set "RECREATE_VENV=1"
)

if "!RECREATE_VENV!"=="1" (
    if exist ".venv" rd /s /q ".venv"
    echo [SETUP] Creating fresh virtual environment for this PC...
    python -m venv .venv
    echo [SETUP] Installing required dependencies...
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install streamlit moviepy edge-tts requests loguru toml pydub
)

:: 4. Start WebUI Dashboard
echo [LAUNCH] Starting Streamlit WebUI Dashboard on http://localhost:8501...
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_DIR%\.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

set "PYTHONPATH=%PROJECT_DIR%"
"%PYTHON_EXE%" -m streamlit run .\webui\Main.py --server.port 8501 --server.headless false

pause
