#!/usr/bin/env python3
"""
Script de lancement pour Telegram Manager.
Exécute simplement 'python -m src.main' depuis le dossier setup.
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Point d'entrée principal."""
    # Déterminer le chemin du dossier setup
    setup_dir = Path(__file__).parent.absolute() / 'setup'
    
    # Vérifier que le dossier setup existe
    if not setup_dir.exists():
        print(f"Error: The 'setup' directory is not found in {setup_dir.parent}")
        return 1
    
    # Commande à exécuter
    cmd = [sys.executable, '-m', 'src.main']
    
    try:
        # Exécuter la commande dans le dossier setup
        subprocess.run(cmd, cwd=str(setup_dir), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the application: {e}")
        return e.returncode
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
