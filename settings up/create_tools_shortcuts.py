import os
import sys
import pythoncom
from win32com.client import Dispatch
import ctypes
import shutil
from pathlib import Path


class ProjectShortcutCreator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        # Chercher le dossier settings avec plusieurs noms possibles
        possible_settings = ["Settings up", "settings up", "settings", "Settings"]
        self.settings_dir = None
        for name in possible_settings:
            candidate = self.project_root / name
            if candidate.exists():
                self.settings_dir = candidate
                break
        
        if not self.settings_dir:
            print(f"[WARNING] Dossier de paramètres introuvable, utilisation du répertoire parent")
            self.settings_dir = self.project_root
        
    def find_batch_files(self):
        """Cherche dynamiquement les fichiers batch avec plusieurs noms possibles."""
        print(f"[DEBUG] Recherche dans le dossier: {self.settings_dir}")
        print(f"[DEBUG] Contenu du dossier settings:")
        
        # Lister tous les fichiers pour le débogage
        try:
            for item in self.settings_dir.iterdir():
                if item.is_file():
                    print(f"[DEBUG]   Fichier: {item.name}")
                elif item.is_dir():
                    print(f"[DEBUG]   Dossier: {item.name}")
        except Exception as e:
            print(f"[ERROR] Impossible de lister le dossier: {e}")
        
        possible_pairs = [
            ("install.bat", "uninstall.bat"),
            ("install.exe", "uninstall.exe"),
            ("setup.bat", "cleanup.bat"),
            ("run_install.bat", "run_uninstall.bat")
        ]
        
        for install_name, uninstall_name in possible_pairs:
            install_path = self.settings_dir / install_name
            uninstall_path = self.settings_dir / uninstall_name
            
            print(f"[DEBUG] Test: {install_name} -> {install_path.exists()}")
            print(f"[DEBUG] Test: {uninstall_name} -> {uninstall_path.exists()}")
            
            if install_path.exists() and uninstall_path.exists():
                print(f"[INFO] Fichiers trouvés: {install_name}, {uninstall_name}")
                return install_path, uninstall_path
        
        # Si aucun pair trouvé, chercher individuellement
        install_files = list(self.settings_dir.glob("install*.bat")) + list(self.settings_dir.glob("install*.exe"))
        uninstall_files = list(self.settings_dir.glob("uninstall*.bat")) + list(self.settings_dir.glob("uninstall*.exe"))
        
        print(f"[DEBUG] Fichiers install trouvés individuellement: {[f.name for f in install_files]}")
        print(f"[DEBUG] Fichiers uninstall trouvés individuellement: {[f.name for f in uninstall_files]}")
        
        if install_files and uninstall_files:
            return install_files[0], uninstall_files[0]
        
        return None, None
        
    def find_icon(self, icon_type):
        """Cherche une icône avec plusieurs noms possibles."""
        icon_dirs = [
            self.settings_dir / "settings images",
            self.settings_dir / "images",
            self.settings_dir / "icons",
            self.settings_dir
        ]
        
        possible_names = [
            f"{icon_type}_icon.ico",
            f"{icon_type}.ico",
            f"{icon_type}_icon.png",
            f"{icon_type}.png",
            "icon.ico",
            "icon.png",
            "app.ico",
            "app.png"
        ]
        
        for icon_dir in icon_dirs:
            if not icon_dir.exists():
                continue
            for name in possible_names:
                icon_path = icon_dir / name
                if icon_path.exists():
                    return icon_path
        
        return None
        
    def create_portable_shortcut(self, target_filename, shortcut_name, shortcut_dir, icon_path=None):
        """Crée un raccourci portable qui fonctionne sur n'importe quel appareil."""
        try:
            # Créer le chemin complet du raccourci
            shortcut_path = os.path.join(shortcut_dir, f"{shortcut_name}.lnk")
            
            # Initialiser COM
            pythoncom.CoInitialize()
            
            try:
                # Créer le raccourci
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                
                # Créer un script batch temporaire pour la portabilité
                batch_content = f"""@echo off
setlocal enabledelayedexpansion

echo Recherche du fichier {target_filename}...
cd /d "%~dp0"

rem Chercher dans le répertoire courant (settings up)
if exist "{target_filename}" (
    echo Fichier trouvé dans le répertoire courant: %cd%\\{target_filename}
    "{target_filename}"
    goto :end
)

rem Chercher dans les sous-dossiers
for /d %%d in (*) do (
    if exist "%%d\\{target_filename}" (
        echo Fichier trouvé dans le sous-dossier: %%d
        cd "%%d"
        "{target_filename}"
        goto :end
    )
)

rem Chercher dans le répertoire parent
cd ..
if exist "{target_filename}" (
    echo Fichier trouvé dans le répertoire parent: %cd%\\{target_filename}
    "{target_filename}"
    goto :end
)

rem Chercher récursivement depuis le répertoire parent
for /r %%f in ({target_filename}) do (
    echo Fichier trouvé recursivement: %%f
    start "" "%%f"
    goto :end
)

echo Erreur: Fichier {target_filename} introuvable
echo Répertoire actuel: %cd%
echo Contenu du répertoire:
dir /b
pause

:end
endlocal
"""
                
                # Créer le script batch portable dans le dossier settings up
                batch_filename = f"run_{shortcut_name.replace(' ', '_')}.bat"
                batch_path = os.path.join(str(self.settings_dir), batch_filename)
                
                with open(batch_path, 'w', encoding='utf-8') as f:
                    f.write(batch_content)
                
                # Configurer le raccourci pour pointer vers le script batch
                shortcut.TargetPath = batch_path
                shortcut.WorkingDirectory = str(self.settings_dir)
                shortcut.WindowStyle = 1  # 1 = Normal
                
                # Ajouter l'icône si spécifiée
                if icon_path and os.path.exists(icon_path):
                    shortcut.IconLocation = f"{os.path.abspath(icon_path)},0"
                    print(f"[INFO] Icône appliquée: {icon_path}")
                else:
                    # Utiliser une icône système par défaut
                    system_icons = [
                        r"C:\Windows\System32\shell32.dll,0",  # Dossier
                        r"C:\Windows\System32\imageres.dll,0",  # Image
                        r"C:\Windows\System32\imageres.dll,102", # Paramètres
                        sys.executable  # Python
                    ]
                    for icon in system_icons:
                        try:
                            shortcut.IconLocation = icon
                            print(f"[INFO] Icône système utilisée: {icon}")
                            break
                        except:
                            continue
                
                # Sauvegarder le raccourci
                shortcut.save()
                print(f"[SUCCESS] Raccourci portable créé: {shortcut_path}")
                print(f"[INFO] Script batch associé: {batch_path}")
                return True
                
            finally:
                # Nettoyer COM
                pythoncom.CoUninitialize()
                
        except Exception as e:
            print(f"[ERROR] Échec de création du raccourci {shortcut_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_project_shortcuts(self):
        """Crée les raccourcis d'installation et désinstallation portables à la racine du projet."""
        print(f"[INFO] Création des raccourcis portables dans: {self.project_root}")
        
        # Chercher dynamiquement les fichiers batch
        install_bat, uninstall_bat = self.find_batch_files()
        
        if not install_bat:
            print(f"[ERROR] Aucun fichier d'installation trouvé")
            return False
            
        if not uninstall_bat:
            print(f"[ERROR] Aucun fichier de désinstallation trouvé")
            return False
        
        print(f"[INFO] Fichiers trouvés: {install_bat.name}, {uninstall_bat.name}")
        
        # Chercher les icônes dynamiquement
        install_icon = self.find_icon("installation")
        uninstall_icon = self.find_icon("uninstallation")
        
        # Créer le raccourci d'installation portable
        install_success = self.create_portable_shortcut(
            target_filename=install_bat.name,
            shortcut_name="installation_tool",
            shortcut_dir=str(self.project_root),
            icon_path=install_icon
        )
        
        # Créer le raccourci de désinstallation portable
        uninstall_success = self.create_portable_shortcut(
            target_filename=uninstall_bat.name,
            shortcut_name="uninstallation_tool", 
            shortcut_dir=str(self.project_root),
            icon_path=uninstall_icon
        )
        
        # Résumé
        if install_success and uninstall_success:
            print("\n[SUCCESS] Tous les raccourcis portables ont été créés avec succès!")
            print(f"  - installation_tool.lnk -> recherche automatique de {install_bat.name}")
            print(f"  - uninstallation_tool.lnk -> recherche automatique de {uninstall_bat.name}")
            print("\n[INFO] Ces raccourcis fonctionneront sur n'importe quel appareil")
            return True
        else:
            print("\n[ERROR] Certains raccourcis n'ont pas pu être créés.")
            return False


def main():
    """Point d'entrée principal du script."""
    print("=" * 60)
    print("Créateur de raccourcis des paramètres d'installation et de désinstallation Telegram Manager")
    print("=" * 60)
    
    try:
        creator = ProjectShortcutCreator()
        success = creator.create_project_shortcuts()
        
        if success:
            print("\nOpération terminée avec succès!")
        else:
            print("\nOpération terminée avec des erreurs.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n[ERROR] Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
