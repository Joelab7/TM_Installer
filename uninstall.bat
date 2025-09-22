@echo off
setlocal enabledelayedexpansion

:: Define the script directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=!SCRIPT_DIR:~0,-1!"

:: Display the execution path
echo ===================================
echo Uninstalling Telegram Manager
echo ===================================
echo.
echo Execution path: %~dp0
echo.

:: Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not in the PATH. Attempting detection...
    set "PYTHON_PATH="
    
    :: Check common Python locations
    for %%i in ("%LOCALAPPDATA%\Programs\Python\Python3*\python.exe") do set "PYTHON_PATH=%%i"
    if not defined PYTHON_PATH (
        for %%i in ("%PROGRAMFILES%\Python3*\python.exe") do set "PYTHON_PATH=%%i"
    )
    
    if not defined PYTHON_PATH (
        echo Error: Python is not installed or not in the PATH.
        echo Please install Python 3.8 or higher from https://www.python.org/downloads/
        pause
        exit /b 1
    )
) else (
    set "PYTHON_PATH=python"
)

echo Python detected: !PYTHON_PATH!

:: Launch the uninstaller Python
echo.
echo Launching uninstaller...
"!PYTHON_PATH!" "%SCRIPT_DIR%\setup_uninstaller.py"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================
    echo Uninstalling completed !
    echo ===================================
) else (
    echo.
    echo ===================================
    echo Error during uninstalling
    echo ===================================
)

echo.
pause