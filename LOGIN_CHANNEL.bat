@echo off
title Channel Manual Safe Login Helper
color 0a

cd /d "%~dp0"

echo ==============================================================================
echo             OMNICHANNEL MANUAL SAFE LOGIN (NATIVE CHROME)
echo ==============================================================================
echo.
if "%~1"=="" (
    set /p CH_KEY="Enter Channel Key (e.g. test, yt_crypto, my_channel): "
) else (
    set CH_KEY=%~1
)

set PROFILE_DIR=%cd%\yt_uploader\profiles\%CH_KEY%
if not exist "%PROFILE_DIR%" mkdir "%PROFILE_DIR%"

echo.
echo [1/2] Opening Genuine Google Chrome for '%CH_KEY%'...
echo [2/2] Isolated Profile Path: %PROFILE_DIR%
echo.

set CHROME_EXE="C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist %CHROME_EXE% (
    set CHROME_EXE="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
)

start "" %CHROME_EXE% --user-data-dir="%PROFILE_DIR%" --no-first-run --no-default-browser-check "https://studio.youtube.com/?approve_browser_access=true"

echo ==============================================================================
echo Chrome is now opening directly on your desktop!
echo.
echo 1. Enter your Google Email and Password in the opened Chrome window.
echo 2. Complete 2FA / OTP verification on your phone.
echo 3. Once you see YouTube Studio, you can close Chrome.
echo.
echo Your session and cookies will be locked in this channel profile forever!
echo ==============================================================================
echo.
pause
