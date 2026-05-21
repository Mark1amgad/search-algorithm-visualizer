@echo off
cd /d "%~dp0"
echo Starting Search Algorithm Visualizer...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Could not run the visualizer.
    echo Make sure Python is installed and dependencies are set up.
    echo Run install.bat first if you have not already done so.
    pause
)
