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
        self.settings_dir = self.project_root / "Settings up"
        
    def create_shortcut(self, target_path, shortcut_name, shortcut_dir, icon_path=None):
        """Crée un raccourci Windows.
        
        Args:
            target_path: Chemin du fichier cible
            shortcut_name: Nom du raccourci (sans extension .lnk)
            shortcut_dir: Répertoire où créer le raccourci
            icon_path: Chemin de l'icône (optionnel)
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Créer le chemin complet du raccourci
            shortcut_path = os.path.join(shortcut_dir, f"{shortcut_name}.lnk")
            
            # Initialiser COM
            pythoncom.CoInitialize()
            
            try:
                # Créer le raccourci
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                
                # Configurer le raccourci
                shortcut.TargetPath = str(target_path)
                shortcut.WorkingDirectory = str(target_path.parent)
                shortcut.WindowStyle = 1  # 1 = Normal
                
                # Ajouter l'icône si spécifiée
                if icon_path and os.path.exists(icon_path):
                    shortcut.IconLocation = f"{os.path.abspath(icon_path)},0"
                    print(f"[INFO] Icône appliquée: {icon_path}")
                else:
                    # Utiliser l'icône par défaut du système
                    shortcut.IconLocation = target_path
                    print(f"[WARNING] Icône non trouvée, utilisation de l'icône par défaut")
                
                # Sauvegarder le raccourci
                shortcut.save()
                print(f"[SUCCESS] Raccourci créé: {shortcut_path}")
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
        """Crée les raccourcis d'installation et désinstallation à la racine du projet."""
        print(f"[INFO] Création des raccourcis dans: {self.project_root}")
        
        # Vérifier que les fichiers batch existent
        install_bat = self.settings_dir / "install.bat"
        uninstall_bat = self.settings_dir / "uninstall.bat"
        
        if not install_bat.exists():
            print(f"[ERROR] Fichier introuvable: {install_bat}")
            return False
            
        if not uninstall_bat.exists():
            print(f"[ERROR] Fichier introuvable: {uninstall_bat}")
            return False
        
        # Chemins des icônes (dans settings images)
        install_icon = self.settings_dir / "settings images" / "Installation_icon.ico"
        uninstall_icon = self.settings_dir / "settings images" / "Uninstallation_icon.ico"
        
        # Créer le raccourci d'installation
        install_success = self.create_shortcut(
            target_path=install_bat,
            shortcut_name="installation_tool",
            shortcut_dir=str(self.project_root),
            icon_path=install_icon if install_icon.exists() else None
        )
        
        # Créer le raccourci de désinstallation
        uninstall_success = self.create_shortcut(
            target_path=uninstall_bat,
            shortcut_name="uninstallation_tool", 
            shortcut_dir=str(self.project_root),
            icon_path=uninstall_icon if uninstall_icon.exists() else None
        )
        
        # Résumé
        if install_success and uninstall_success:
            print("\n[SUCCESS] Tous les raccourcis ont été créés avec succès!")
            print(f"  - installation_tool.lnk -> {install_bat}")
            print(f"  - uninstallation_tool.lnk -> {uninstall_bat}")
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
