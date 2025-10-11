@echo off
setlocal enabledelayedexpansion

:: Définir le répertoire du script
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=!SCRIPT_DIR:~0,-1!"

:: Vérifier les privilèges administrateur
net session >nul 2>&1
if %ERRORLEVEL% == 0 (
    goto :run_as_admin
) else (
    set "VBS_SCRIPT=%TEMP%\~runas_%RANDOM%.vbs"
    
    > "!VBS_SCRIPT!" echo Set UAC = CreateObject^("Shell.Application"^)
    >> "!VBS_SCRIPT!" echo UAC.ShellExecute "cmd.exe", "/c """"%~f0""", "", "runas", 0
    
    cscript "!VBS_SCRIPT!" >nul 2>&1
    timeout /t 2 >nul
    del /f /q "!VBS_SCRIPT!" >nul 2>&1
    exit /b
)

:run_as_admin
:: Vérifier si le script est exécuté en tant qu'administrateur
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    exit /b 1
)

:: Vérifier si Python est disponible
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set "PYTHON_PATH="
    
    :: Vérifier les emplacements courants de Python
    for %%i in ("%LOCALAPPDATA%\Programs\Python\Python3*\python.exe") do set "PYTHON_PATH=%%i"
    if not defined PYTHON_PATH (
        for %%i in ("%PROGRAMFILES%\Python3*\python.exe") do set "PYTHON_PATH=%%i"
    )
    
    if not defined PYTHON_PATH (
        exit /b 1
    )
) else (
    set "PYTHON_PATH=python"
)

:: Lancer le désinstalleur complètement en arrière-plan
set "LAUNCH_SCRIPT=%TEMP%\~launch_uninstall_%RANDOM%.vbs"

> "!LAUNCH_SCRIPT!" echo Set WshShell = CreateObject^("WScript.Shell"^)
>> "!LAUNCH_SCRIPT!" echo WshShell.Run "cmd /c """"!PYTHON_PATH!"" ""%SCRIPT_DIR%\setup_uninstaller.py""""", 0, False

cscript "!LAUNCH_SCRIPT!" >nul 2>&1
timeout /t 2 >nul
del /f /q "!LAUNCH_SCRIPT!" >nul 2>&1

exit