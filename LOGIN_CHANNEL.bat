@echo off
title Channel Manual Safe Login Helper
color 0a

cd /d "%~dp0"
set PYTHONPATH=%cd%;%cd%\.venv\Lib\site-packages;%PYTHONPATH%

set PY_EXE=python
if exist "%USERPROFILE%\AppData\Roaming\uv\python\cpython-3.11.17-windows-x86_64-none\python.exe" (
    set PY_EXE="%USERPROFILE%\AppData\Roaming\uv\python\cpython-3.11.17-windows-x86_64-none\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set PY_EXE=".venv\Scripts\python.exe"
)

echo ==============================================================================
echo             OMNICHANNEL MANUAL SAFE LOGIN (HUMAN-IN-THE-LOOP)
echo ==============================================================================
echo.
if "%~1"=="" (
    set /p CH_KEY="Enter Channel Key (e.g. test, yt_crypto, my_new_channel): "
) else (
    set CH_KEY=%~1
)

echo.
echo [1/2] Launching Genuine Google Chrome for channel: %CH_KEY% ...
echo [2/2] Please log in with your credentials and complete 2FA in the opened Chrome window.
echo.
%PY_EXE% "omnichannel_powerhouse\manual_auth_helper.py" --channel "%CH_KEY%" --platform youtube
echo.
echo Done! Session saved.
pause
