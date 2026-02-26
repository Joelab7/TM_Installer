@echo off
setlocal enabledelayedexpansion

echo Recherche du fichier install.bat...
cd /d "%~dp0"

rem Chercher dans le répertoire courant (settings up)
if exist "install.bat" (
    echo Fichier trouvé dans le répertoire courant: %cd%\install.bat
    "install.bat"
    goto :end
)

rem Chercher dans les sous-dossiers
for /d %%d in (*) do (
    if exist "%%d\install.bat" (
        echo Fichier trouvé dans le sous-dossier: %%d
        cd "%%d"
        "install.bat"
        goto :end
    )
)

rem Chercher dans le répertoire parent
cd ..
if exist "install.bat" (
    echo Fichier trouvé dans le répertoire parent: %cd%\install.bat
    "install.bat"
    goto :end
)

rem Chercher récursivement depuis le répertoire parent
for /r %%f in (install.bat) do (
    echo Fichier trouvé recursivement: %%f
    start "" "%%f"
    goto :end
)

echo Erreur: Fichier install.bat introuvable
echo Répertoire actuel: %cd%
echo Contenu du répertoire:
dir /b
pause

:end
endlocal
