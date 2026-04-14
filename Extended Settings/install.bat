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
    :: Demande d'élévation des privilèges via VBS
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

:: Essayer différentes commandes Python
set PYTHON_CMD=python
%PYTHON_CMD% --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set PYTHON_CMD=python3
    %PYTHON_CMD% --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        set PYTHON_CMD=py
        %PYTHON_CMD% --version >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            :: Python 3.11.9 n'est pas installé, ouvrir le lien de téléchargement
            echo Python 3.11.9 not found.
            echo Opening download link in your browser...
            start "" "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
            echo.
            echo Please download and install Python 3.11.9, then rerun this script.
            echo.
            pause
            exit /b 1
        )
    )
)

:: Vérification spécifique de Python 3.11.9
%PYTHON_CMD% -c "import sys; exit(0 if (sys.version_info.major, sys.version_info.minor, sys.version_info.micro) == (3, 11, 9) else 1)" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Incorrect Python version. This script requires Python 3.11.9 exactly.
    echo Current version:
    %PYTHON_CMD% --version
    echo.
    echo Opening download link for Python 3.11.9...
    start "" "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    echo.
    echo Please install Python 3.11.9, then rerun this script.
    echo.
    pause
    exit /b 1
)

:: Vérification de pywin32
%PYTHON_CMD% -c "import win32com" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    %PYTHON_CMD% -m pip install pywin32 >nul 2>&1
)


:: Lancer l'installateur
echo Launching installer...
%PYTHON_CMD% "%SCRIPT_DIR%\setup_installer.py"
if %ERRORLEVEL% NEQ 0 (
    echo Error occurred during execution of setup_installer.py
    pause
    exit /b 1
)

exit
