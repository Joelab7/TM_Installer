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
    echo Requesting administrative privileges...
    set "VBS_SCRIPT=%TEMP%\~runas_install.vbs"
    
    echo Set UAC = CreateObject^("Shell.Application"^) > "!VBS_SCRIPT!"
    echo UAC.ShellExecute "cmd.exe", "/c """"%~f0""", "", "runas", 1 >> "!VBS_SCRIPT!"
    
    wscript "!VBS_SCRIPT!"
    timeout /t 2 >nul
    del /f /q "!VBS_SCRIPT!" 2>nul
    exit /b
)

:run_as_admin
:: Afficher des informations de débogage
echo [DEBUG] Installation with administrative privileges...
echo [DEBUG] Current directory: %CD%
echo [DEBUG] Windows version:
ver
echo.

:: Vérifier si le script est exécuté en tant qu'administrateur
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] This script must be run as administrator.
    echo Please right-click on the script and select "Run as administrator".
    pause
    exit /b 1
)

echo ===================================
echo Installing Telegram Manager
echo ===================================
echo.

echo Checking Python...

:: Try different Python commands
set PYTHON_CMD=python
%PYTHON_CMD% --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set PYTHON_CMD=python3
    %PYTHON_CMD% --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        set PYTHON_CMD=py
        %PYTHON_CMD% --version >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            echo Python is not installed. Attempting installation...
            
            where winget >nul 2>&1
            if %ERRORLEVEL% EQU 0 (
                echo Checking curl...
                where curl >nul 2>&1
                if %ERRORLEVEL% NEQ 0 (
                    echo Installing curl...
                    winget install -e --id cURL.cURL
                    if %ERRORLEVEL% NEQ 0 (
                        echo [ERROR] Failed to install curl. Python installation canceled.
                        pause
                        exit /b 1
                    )
                )
                
                echo Downloading Python 3.11.9...
                curl -o python_installer.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
                if %ERRORLEVEL% NEQ 0 (
                    echo [ERROR] Failed to download Python 3.11.9
                    pause
                    exit /b 1
                )
                
                echo Installing Python 3.11.9...
                python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
                del python_installer.exe
                
                if %ERRORLEVEL% EQU 0 (
                    echo Python installed successfully.
                    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python311"
                    
                    echo Updating PATH...
                    setx PATH "%PATH%;%PYTHON_PATH%;%PYTHON_PATH%\Scripts"
                    set "PATH=%PATH%;%PYTHON_PATH%;%PYTHON_PATH%\Scripts"
                    
                    set PYTHON_CMD=python
                    echo Verifying Python installation...
                    %PYTHON_CMD% --version
                    if %ERRORLEVEL% NEQ 0 (
                        echo [ERROR] Python installation verification failed.
                        pause
                        exit /b 1
                    )
                ) else (
                    echo [ERROR] Python installation failed. Error code: %ERRORLEVEL%
                    echo.
                    echo Opening browser to download Python 3.11.9...
                    start "" "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
                    echo.
                    echo ===============================================================
                    echo INSTRUCTIONS FOR MANUAL INSTALLATION OF PYTHON 3.11.9
                    echo ===============================================================
                    echo 1. In the installer, CHECK the box "Add Python 3.11 to PATH"
                    echo 2. Click on "Install Now"
                    echo 3. If a user account control prompt appears, click on "Yes"
                    echo 4. Wait for the installation to finish
                    echo 5. Once the installation is complete, click on "Close"
                    echo 6. Relaunch this installation program
                    echo ===============================================================
                    pause
                    exit /b 1
                )
            ) else (
                echo [ERROR] Winget is not available. Automatic installation impossible.
                echo.
                echo Opening browser to download Python 3.11.9...
                start "" "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
                echo.
                echo ===============================================================
                echo INSTRUCTIONS FOR MANUAL INSTALLATION OF PYTHON 3.11.9
                echo ===============================================================
                echo 1. Execute the downloaded python-3.11.9-amd64.exe file
                echo 2. IMPORTANT : Check the box "Add Python 3.11 to PATH"
                echo 3. Click on "Install Now"
                echo 4. If a user account control prompt appears, click on "Yes"
                echo 5. Wait for the installation to finish
                echo 6. Once the installation is complete, click on "Close"
                echo 7. Restart your computer
                echo 8. Relaunch this installation program
                echo ===============================================================
                pause
                exit /b 1
            )
        )
    )
)

echo Python detection in English: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

echo Checking Python version...
%PYTHON_CMD% -c "import sys; print('Version detected:', sys.version); exit(0 if sys.version_info >= (3, 8) else 1)"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python 3.8 or higher is required.
    pause
    exit /b 1
)

echo Python is already installed. Checking pywin32...
%PYTHON_CMD% -c "import win32com" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo pywin32 is not installed. Attempting installation...
    %PYTHON_CMD% -m pip install pywin32
    if %ERRORLEVEL% EQU 0 (
        echo pywin32 installed successfully.
    ) else (
        echo [WARNING] pywin32 could not be installed. Some features may not work correctly.
    )
) else (
    echo pywin32 is already installed.
)

echo ===================================
echo Checking Git...
echo ===================================
:: Vérifier si Git est installé
git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Git is not installed. Attempting installation...
    
    where winget >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo Installation de Git via winget...
        winget install --id Git.Git -e --accept-package-agreements --accept-source-agreements
        
        if %ERRORLEVEL% EQU 0 (
            echo Git installed successfully.
            echo Updating PATH...
            setx PATH "%PATH%;C:\\Program Files\\Git\\cmd"
            set "PATH=%PATH%;C:\\Program Files\\Git\\cmd"
            
            echo Checking Git installation...
            git --version
            if %ERRORLEVEL% NEQ 0 (
                echo [ERROR] Git installation verification failed.
                goto :install_git_manually
            )
        ) else (
            echo [ERROR] Git installation failed. Error code: %ERRORLEVEL%
            goto :install_git_manually
        )
    ) else (
        echo [ERROR] Winget is not available. Automatic installation impossible.
        goto :install_git_manually
    )
) else (
    echo Git is already installed.
    git --version
)

echo.
goto :git_install_success

:install_git_manually
echo.
echo Opening browser to download Git 2.51.0...
start "" "https://github.com/git-for-windows/git/releases/download/v2.51.0.windows.1/Git-2.51.0-64-bit.exe"
echo.
echo ===============================================================
echo INSTRUCTIONS FOR MANUAL INSTALLATION OF GIT 2.51.0
echo ===============================================================
echo 1. Execute the downloaded Git-2.51.0-64-bit.exe file
echo 2. Follow the installation steps with default parameters
echo 3. IMPORTANT : Select 'Git from the command line and also from 3rd-party software'
echo 4. Continue the installation with default options
echo 5. If a user account control prompt appears, click on "Yes"
echo 6. Once the installation is complete, click on "Finish"
echo 7. Restart your computer
echo 8. Relaunch this installation program
echo ===============================================================
pause
exit /b 1

:git_install_success
echo.
echo Git verification completed successfully.
echo.

echo ===================================
echo Dependencies verification completed
echo ===================================
echo.

echo Launching installer...
%PYTHON_CMD% "%~dp0setup_installer.py"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================
    echo Installation completed successfully!
    echo ===================================
) else (
    echo.
    echo ===================================
    echo Installation failed
    echo ===================================
)

echo.
pause
