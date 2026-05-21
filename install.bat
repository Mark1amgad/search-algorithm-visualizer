@echo off
cd /d "%~dp0"
echo Installing dependencies for Search Algorithm Visualizer...
echo.
pip install -r requirements.txt
echo.
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: All dependencies installed.
    echo You can now run start.bat to launch the visualizer.
) else (
    echo ERROR: Installation failed.
    echo Make sure Python and pip are installed and available in PATH.
)
echo.
pause
