@echo off
title OmniChannel Supreme Studio Control Server
color 0b

echo ==============================================================================
echo       OMNICHANNEL SUPREME STUDIO (500X ZERO-TOKEN AUTONOMOUS ENGINE)
echo ==============================================================================
echo.
echo [1/3] Setting up Python Environment & Path...
cd /d "%~dp0"
set PYTHONPATH=%cd%;%cd%\.venv\Lib\site-packages;%PYTHONPATH%

set PY_EXE=python
if exist "%USERPROFILE%\AppData\Roaming\uv\python\cpython-3.11.17-windows-x86_64-none\python.exe" (
    set PY_EXE="%USERPROFILE%\AppData\Roaming\uv\python\cpython-3.11.17-windows-x86_64-none\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set PY_EXE=".venv\Scripts\python.exe"
)

echo [2/3] Starting Studio Web Server & REST API on http://localhost:8899...
start "" http://localhost:8899

echo [3/3] Server is live! Press Ctrl+C in this window to stop the server.
echo.
%PY_EXE% -m uvicorn omnichannel_powerhouse.server:app --host 0.0.0.0 --port 8899
pause
