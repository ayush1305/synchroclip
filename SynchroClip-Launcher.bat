@echo off
setlocal enabledelayedexpansion
title SynchroClip Studio Launcher
echo ======================================================================
echo          🎬 SynchroClip — AI Audio-Synced Stock Video Studio
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/2] Checking dependencies...
python -m pip install -q -r requirements.txt

echo.
echo [2/2] Launching SynchroClip Studio...
echo Opening browser at http://localhost:8080 ...
start "" http://localhost:8080

echo.
echo Studio is running! Keep this window open while using the studio.
echo.
python run.py

pause
