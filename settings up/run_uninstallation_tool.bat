@echo off
setlocal enabledelayedexpansion

echo Recherche du fichier uninstall.bat...
cd /d "%~dp0"

rem Chercher dans le répertoire courant (settings up)
if exist "uninstall.bat" (
    echo Fichier trouvé dans le répertoire courant: %cd%\uninstall.bat
    "uninstall.bat"
    goto :end
)

rem Chercher dans les sous-dossiers
for /d %%d in (*) do (
    if exist "%%d\uninstall.bat" (
        echo Fichier trouvé dans le sous-dossier: %%d
        cd "%%d"
        "uninstall.bat"
        goto :end
    )
)

rem Chercher dans le répertoire parent
cd ..
if exist "uninstall.bat" (
    echo Fichier trouvé dans le répertoire parent: %cd%\uninstall.bat
    "uninstall.bat"
    goto :end
)

rem Chercher récursivement depuis le répertoire parent
for /r %%f in (uninstall.bat) do (
    echo Fichier trouvé recursivement: %%f
    start "" "%%f"
    goto :end
)

echo Erreur: Fichier uninstall.bat introuvable
echo Répertoire actuel: %cd%
echo Contenu du répertoire:
dir /b
pause

:end
endlocal
