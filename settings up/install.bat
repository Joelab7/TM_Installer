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
            where winget >nul 2>&1
            if %ERRORLEVEL% EQU 0 (
                where curl >nul 2>&1
                if %ERRORLEVEL% NEQ 0 (
                    winget install -e --id cURL.cURL >nul 2>&1
                    if %ERRORLEVEL% NEQ 0 (
                        exit /b 1
                    )
                )
                
                curl -o python_installer.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe >nul 2>&1
                if %ERRORLEVEL% NEQ 0 (
                    exit /b 1
                )
                
                python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 >nul 2>&1
                del python_installer.exe >nul 2>&1
                
                if %ERRORLEVEL% EQU 0 (
                    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python311"
                    setx PATH "%PATH%;%PYTHON_PATH%;%PYTHON_PATH%\Scripts" >nul 2>&1
                    set "PATH=%PATH%;%PYTHON_PATH%;%PYTHON_PATH%\Scripts"
                    
                    set PYTHON_CMD=python
                    %PYTHON_CMD% --version >nul 2>&1
                    if %ERRORLEVEL% NEQ 0 (
                        exit /b 1
                    )
                ) else (
                    exit /b 1
                )
            ) else (
                exit /b 1
            )
        )
    )
)

:: Vérification de la version de Python
%PYTHON_CMD% -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    exit /b 1
)

:: Vérification de pywin32
%PYTHON_CMD% -c "import win32com" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    %PYTHON_CMD% -m pip install pywin32 >nul 2>&1
)

:: Vérifier si Git est installé
git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where winget >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        winget install --id Git.Git -e --accept-package-agreements --accept-source-agreements >nul 2>&1
        
        if %ERRORLEVEL% EQU 0 (
            setx PATH "%PATH%;C:\\Program Files\\Git\\cmd" >nul 2>&1
            set "PATH=%PATH%;C:\\Program Files\\Git\\cmd"
        )
    )
)

:: Lancer l'installateur complètement en arrière-plan
start /B "" %PYTHON_CMD% "%SCRIPT_DIR%\setup_installer.py" >nul 2>&1

exit
