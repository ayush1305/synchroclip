@echo off
setlocal
title Install SynchroClip Desktop App
echo ======================================================================
echo          🎬 SynchroClip — Windows Desktop App Installer
echo ======================================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "LAUNCHER=%SCRIPT_DIR%SynchroClip-Launcher.bat"
set "DESKTOP=%USERPROFILE%\Desktop"

echo Creating Desktop shortcut for SynchroClip Studio...

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP%\SynchroClip Studio.lnk'); $s.TargetPath = '%LAUNCHER%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Description = 'SynchroClip AI Audio-Synced Stock Video Studio'; $s.Save()"

echo.
if exist "%DESKTOP%\SynchroClip Studio.lnk" (
    echo [SUCCESS] Desktop shortcut created successfully on your Desktop!
    echo Look for 'SynchroClip Studio' on your Desktop.
) else (
    echo [NOTE] Shortcut creation completed.
)

echo.
echo Installing required Python packages...
python -m pip install -r "%SCRIPT_DIR%requirements.txt"

echo.
echo ======================================================================
echo  Installation complete! You can now double-click 'SynchroClip Studio'
echo  on your Desktop to launch the app anytime!
echo ======================================================================
echo.
pause
