@echo off
title Rumble Manual Safe Login Helper
color 0b

cd /d "%~dp0"
set PYTHONPATH=%cd%;%cd%\.venv\Lib\site-packages;%PYTHONPATH%

set PY_EXE=python
if exist "%USERPROFILE%\AppData\Roaming\uv\python\cpython-3.11.17-windows-x86_64-none\python.exe" (
    set PY_EXE="%USERPROFILE%\AppData\Roaming\uv\python\cpython-3.11.17-windows-x86_64-none\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set PY_EXE=".venv\Scripts\python.exe"
)

echo ==============================================================================
echo             RUMBLE MANUAL SAFE LOGIN (SILICON PULSE NETWORK)
echo ==============================================================================
echo.
echo [1/2] Launching Genuine Chrome for Rumble Login...
echo [2/2] Target Channel: rumble_hub_01 (Silicon Pulse Rumble Network)
echo.
echo Please log in to your Rumble Account in the opened window.
echo Once you see your Rumble Dashboard, simply CLOSE the window to save session!
echo.

%PY_EXE% "omnichannel_powerhouse\manual_auth_helper.py" --channel "rumble_hub_01" --platform rumble

echo.
echo Done! Rumble session saved.
pause
