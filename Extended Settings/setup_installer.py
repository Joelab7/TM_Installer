import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import winreg
import ctypes
import win32com.client
import pythoncom  # Ajout pour la gestion COM
import win32con
import urllib.request
import zipfile
import tempfile
import threading
import socket
import ssl


class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Manager Installation")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#FFFFFF')
        self.style.configure('TLabel', background='#FFFFFF', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10))
        
        # Variables
        self.install_dir = tk.StringVar(value=os.environ['PROGRAMFILES'])
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_start_menu = tk.BooleanVar(value=True)
        self.installation_in_progress = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # En-tête
        header = ttk.Label(
            main_frame, 
            text="Telegram Manager Installation",
            font=('Segoe UI', 16, 'bold'),foreground='#4FC3F7'
        )
        header.pack(pady=(0, 20))
        
        # Frame de contenu
        content = ttk.Frame(main_frame)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Sélection du répertoire d'installation
        dir_frame = ttk.Frame(content)
        dir_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(dir_frame, text="Installation directory :").pack(anchor='w')
        
        dir_entry_frame = ttk.Frame(dir_frame)
        dir_entry_frame.pack(fill=tk.X, pady=5)
        
        self.dir_entry = ttk.Entry(dir_entry_frame, textvariable=self.install_dir, width=50, foreground='#4FC3F7')
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(dir_entry_frame, text="Browse...", command=self.browse_directory)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Options d'installation
        options_frame = ttk.LabelFrame(content, text="Installation options", padding=10)
        options_frame.pack(fill=tk.X, pady=10)
        
        ttk.Checkbutton(
            options_frame, 
            text="Create a shortcut on the desktop(recommended)",
            variable=self.create_desktop_shortcut,
            style='Blue.TCheckbutton'
        ).pack(anchor='w', pady=2)
        
        # Espacement
        ttk.Frame(content, height=20).pack()
        
        # Style pour la barre de progression
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Custom.Horizontal.TProgressbar",
            thickness=20,
            troughcolor='#f0f0f0',
            background='#4FC3F7',  # Couleur bleu
            troughrelief='flat',
            borderwidth=1,
            lightcolor='#66BB6A',
            darkcolor='#388E3C',
            bordercolor='#E0E0E0'
        )
        
        # Frame pour la barre de progression avec une bordure
        progress_frame = ttk.Frame(main_frame, style='TFrame')
        progress_frame.pack(fill=tk.X, pady=(10, 0), padx=5)
        
        # Barre de progression
        self.progress = ttk.Progressbar(
            progress_frame, 
            orient=tk.HORIZONTAL, 
            length=400, 
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress.pack(fill=tk.X, expand=True, pady=5, padx=5)
        
        # Message d'état
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            main_frame, 
            textvariable=self.status_var,
            foreground='#4FC3F7',
            font=('Segoe UI', 8)
        )
        self.status_label.pack(pady=(5, 0))
        
        # Boutons
        btn_frame = ttk.Frame(content)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.install_btn = ttk.Button(
            btn_frame, 
            text="Install", 
            command=self.start_installation,
            style='Accent.TButton'
        )
        self.install_btn.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Cancel", 
            command=self.root.quit
        ).pack(side=tk.RIGHT)
        self.status_label.pack(pady=(5, 0))
        
        # Style pour les checkbuttons avec couleur bleue claire quand sélectionné
        self.style.configure('Blue.TCheckbutton',
                           font=('Segoe UI', 10),
                           foreground='#000000',  # Texte noir
                           background='#FFFFFF')

        self.style.map('Blue.TCheckbutton',
                      background=[('active', '#E3F2FD'),  # Fond très clair au survol
                                 ('selected', '#4FC3F7')], # Bleu clair quand sélectionné
                      indicatorcolor=[('selected', '#4FC3F7')])  # Couleur de la case elle-même

        # Configuration pour le bouton de base aussi
        self.style.configure('Accent.TButton',
                           font=('Segoe UI', 10, 'bold'),
                           background='#1976D2',  # Bleu moderne pour le bouton principal
                           foreground='white')

        self.style.map('Accent.TButton',
                      background=[('active', '#2196F3'),  # Bleu plus clair au survol
                                 ('pressed', '#0D47A1')], # Bleu foncé quand pressé
                      relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

        # Supprimer les bordures de focus pour éviter les pointillés noirs
        self.style.configure('Accent.TButton', focuscolor='none')
        self.style.map('Accent.TButton', bordercolor=[('focus', '#1976D2'), ('!focus', '#1976D2')])

        # Configuration pour le bouton de base aussi
        self.style.configure('TButton',
                           font=('Segoe UI', 10),
                           background='#1976D2',  # Bleu moderne
                           foreground='white')
        self.style.map('TButton',
                      background=[('active', '#42A5F5'),  # Bleu au survol
                                 ('pressed', '#1E88E5')])  # Bleu plus foncé quand pressé

        # Supprimer les bordures de focus pour éviter les pointillés noirs
        self.style.configure('TButton', focuscolor='none')
        self.style.map('TButton', bordercolor=[('focus', '#1976D2'), ('!focus', '#1976D2')])

    def browse_directory(self):
        """Ouvre une boîte de dialogue pour sélectionner le dossier d'installation."""
        try:
            # Utiliser le répertoire de base approprié selon les droits d'administration
            initial_dir = self.install_dir.get()
            if not initial_dir or not os.path.exists(initial_dir):
                initial_dir = os.path.expanduser('~')  # Dossier personnel par défaut
                
            # Ouvrir la boîte de dialogue de sélection de dossier
            directory = filedialog.askdirectory(
                title="Select the installation directory",
                mustexist=False,  # Permet de créer un nouveau dossier
                initialdir=initial_dir
            )
            
            if directory:
                # Normaliser le chemin pour éviter les problèmes de format
                directory = os.path.normpath(directory)
                self.install_dir.set(directory)
                
                # Mettre à jour le statut pour confirmer la sélection
                self.update_status(f"Installation directory selected : {directory}", 0, '#4FC3F7')
        except Exception as e:
            error_msg = f"Error selecting directory : {e}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)

    def update_status(self, message, progress=None, color=None):
        if hasattr(self, 'status_var'):
            self.status_var.set(message)

            # Appliquer la couleur si spécifiée
            if color and hasattr(self, 'status_label'):
                self.status_label.config(foreground=color)

        if progress is not None and hasattr(self, 'progress'):
            # Mettre à jour la valeur de la barre de progression
            current_value = self.progress['value']
            target_value = float(progress)
            
            # Animation fluide de la barre de progression
            steps = 10
            step = (target_value - current_value) / steps
            
            def animate(step_count=0):
                if step_count < steps:
                    new_value = current_value + (step * (step_count + 1))
                    self.progress['value'] = min(max(new_value, 0), 100)
                    self.root.update_idletasks()
                    self.root.after(20, animate, step_count + 1)
                else:
                    self.progress['value'] = target_value
            
            # Démarrer l'animation
            self.root.after(0, animate)
            
            # Forcer la mise à jour de l'interface
            self.root.update_idletasks()
        
        # Mettre à jour l'interface
        self.root.update()
    
    def _get_desktop_path(self):
        """Récupère le chemin du bureau en fonction de la langue du système."""
        try:
            import ctypes
            from ctypes import wintypes, windll
            
            # Utiliser SHGetFolderPath pour obtenir le vrai chemin du bureau
            CSIDL_DESKTOP = 0  # Bureau
            SHGFP_TYPE_CURRENT = 0  # Récupérer le chemin actuel, pas la valeur par défaut
            
            buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOP, None, SHGFP_TYPE_CURRENT, buf)
            
            desktop_path = buf.value
            print(f"[DEBUG] Desktop path detected: {desktop_path}")
            return desktop_path
            
        except Exception as e:
            print(f"[ERROR] Failed to detect desktop path: {e}")
            # Fallback sur les chemins standards
            user_profile = os.path.expanduser('~')
            for path in [os.path.join(user_profile, 'Bureau'), 
                        os.path.join(user_profile, 'Desktop'),
                        os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')]:
                if os.path.isdir(path):
                    print(f"[DEBUG] Using fallback path: {path}")
                    return path
            return user_profile  # Dernier recours
            
    def _get_start_menu_path(self):
        """Récupère le chemin du menu Démarrer en fonction de la langue du système."""
        try:
            import ctypes
            from ctypes import wintypes, windll
            
            # Utiliser SHGetFolderPath pour obtenir le vrai chemin du menu Démarrer
            CSIDL_PROGRAMS = 2  # Menu Démarrer (Tous les utilisateurs)
            SHGFP_TYPE_CURRENT = 0  # Récupérer le chemin actuel, pas la valeur par défaut
            
            buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            windll.shell32.SHGetFolderPathW(None, CSIDL_PROGRAMS, None, SHGFP_TYPE_CURRENT, buf)
            
            start_menu_path = buf.value
            print(f"[DEBUG] Start menu path detected: {start_menu_path}")
            return start_menu_path
            
        except Exception as e:
            print(f"[ERROR] Failed to detect start menu path: {e}")
            # Fallback sur les chemins standards
            all_users_profile = os.environ.get('ALLUSERSPROFILE', '')
            for path in [
                os.path.join(all_users_profile, r'Microsoft\Windows\Start Menu\Programs'),
                os.path.join(os.environ.get('PROGRAMDATA', ''), r'Microsoft\Windows\Start Menu\Programs')
            ]:
                if os.path.isdir(path):
                    print(f"[DEBUG] Using fallback path: {path}")
                    return path
            return os.path.join(all_users_profile, r'Microsoft\Windows\Start Menu\Programs')  # Dernier recours
            
    def create_shortcut(self, target, name, directory):
        """Crée un raccourci Windows qui demande l'élévation des privilèges."""
        try:
            import pythoncom
            from win32com.client import Dispatch
            import ctypes
            import sys
            import os
            
            # Créer le chemin complet du raccourci
            shortcut_path = os.path.join(directory, f"{name}.lnk")
            
            # Initialiser COM
            pythoncom.CoInitialize()
            
            try:
                # Créer le raccourci
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                
                # Obtenir les chemins nécessaires
                target_dir = os.path.dirname(target)
                setup_src_path = os.path.join(target_dir, "setup", "src")
                pythonw_exe = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
                
                # Vérifier si pythonw.exe existe, sinon utiliser python.exe
                if not os.path.exists(pythonw_exe):
                    pythonw_exe = sys.executable
                    
                # Configurer le raccourci pour exécuter directement pythonw.exe avec les arguments
                shortcut.TargetPath = pythonw_exe
                shortcut.Arguments = f'"{os.path.join(setup_src_path, "main.py")}"'
                shortcut.WorkingDirectory = setup_src_path
                shortcut.WindowStyle = 0  # 0 = Caché
                
                # Chemin de l'icône pour Telegram Manager
                icon_path = os.path.join(target_dir, 'setup', 'src', 'telegram_manager', 'resources', 'icons', 'app_icon.ico')
                
                if os.path.exists(icon_path):
                    try:
                        from PyQt6.QtWidgets import QApplication, QMainWindow
                        from PyQt6.QtGui import QIcon
                        
                        # Vérifier si l'icône est valide avec QMainWindow
                        app = QApplication.instance() or QApplication([])
                        window = QMainWindow()
                        window.setWindowIcon(QIcon(icon_path))
                        
                        # Si on arrive ici, l'icône est valide
                        shortcut.IconLocation = f"{os.path.abspath(icon_path)},0"
                        print(f"[INFO] Icon loaded successfully for {name}")
                        
                        # Nettoyer
                        window.close()
                        if QApplication.instance() is None:
                            app.quit()
                            
                    except Exception as e:
                        print(f"[WARNING] Failed to load icon with QMainWindow: {e}")
                        # Fallback vers la méthode standard
                        shortcut.IconLocation = f"{os.path.abspath(icon_path)},0"
                else:
                    print(f"[WARNING] Icon file not found: {icon_path}")
                    shortcut.IconLocation = sys.executable
                
                # Sauvegarder le raccourci
                shortcut.save()
                
                # Configurer l'élévation des privilèges
                try:
                    from win32com.shell import shell, shellcon
                    from win32com.storagecon import STGM_READWRITE
                    
                    persist_file = pythoncom.CoCreateInstance(
                        shell.CLSID_ShellLink,
                        None,
                        pythoncom.CLSCTX_INPROC_SERVER,
                        pythoncom.IID_IPersistFile
                    )
                    
                    persist_file.Load(shortcut_path, STGM_READWRITE)
                    shell_link = persist_file.QueryInterface(shell.IID_IShellLinkDataList)
                    
                    # Définir le flag pour exiger l'élévation
                    SLDF_RUNAS_USER1 = 0x2000
                    flags = shell_link.GetFlags()
                    flags |= SLDF_RUNAS_USER1
                    shell_link.SetFlags(flags)
                    
                    # Sauvegarder les modifications
                    persist_file.Save(shortcut_path, True)
                    
                except Exception as e:
                    print(f"[WARNING] Unable to force elevation: {e}")
                
                return True
                
            finally:
                # Nettoyer COM
                pythoncom.CoUninitialize()
                
        except Exception as e:
            print(f"[WARNING] Failed to create shortcut {name}: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def extract_from_pack(self, target_dir):
        """Extrait le contenu d'un fichier ZIP depuis le répertoire PACK vers le répertoire d'installation."""
        print(f"[DEBUG] Starting extract_from_pack with target_dir: {target_dir}")
        
        try:
            # Obtenir le chemin du répertoire PACK (même niveau que le script)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            pack_dir = os.path.join(script_dir, 'PACK')
            
            print(f"[DEBUG] Script directory: {script_dir}")
            print(f"[DEBUG] PACK directory: {pack_dir}")
            
            # Vérifier si le répertoire PACK existe
            if not os.path.exists(pack_dir):
                error_msg = f"PACK directory not found: {pack_dir}"
                print(f"[ERROR] {error_msg}")
                messagebox.showerror("Installation Error", error_msg)
                return False
            
            # Rechercher tous les fichiers ZIP dans le répertoire PACK
            zip_files = [f for f in os.listdir(pack_dir) if f.lower().endswith('.zip')]
            
            if not zip_files:
                error_msg = f"No ZIP file found in PACK directory: {pack_dir}"
                print(f"[ERROR] {error_msg}")
                messagebox.showerror("Installation Error", error_msg)
                return False
            
            # Utiliser le premier fichier ZIP trouvé (peu importe le nom)
            zip_file = zip_files[0]
            zip_path = os.path.join(pack_dir, zip_file)
            print(f"[DEBUG] Using ZIP file: {zip_path}")
            
            # Créer le répertoire cible s'il n'existe pas
            os.makedirs(target_dir, exist_ok=True)
            
            # Vérifier que le répertoire est accessible en écriture
            test_file = os.path.join(target_dir, 'test_write.tmp')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"[DEBUG] Directory {target_dir} is writable")
            except Exception as e:
                print(f"[ERROR] Unable to write to {target_dir}: {e}")
                messagebox.showerror("Installation Error", f"Unable to write to {target_dir}: {e}")
                return False
            
            # Forcer l'utilisation du sous-répertoire 'Telegram Manager'
            final_target_dir = target_dir
            if not target_dir.endswith('Telegram Manager'):
                final_target_dir = os.path.join(target_dir, 'Telegram Manager')
                os.makedirs(final_target_dir, exist_ok=True)
                print(f"[DEBUG] Using subdirectory: {final_target_dir}")
            else:
                final_target_dir = target_dir
            
            # Mettre à jour la variable de classe avec le chemin final
            self.install_dir.set(final_target_dir)
            print(f"[DEBUG] Installation directory set to: {final_target_dir}")
            
            # Extraire le fichier ZIP
            self.update_status("Extracting files from PACK archive...", 30)
            print(f"[DEBUG] Extracting {zip_path} to {final_target_dir}")
            
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Lister les fichiers dans le ZIP
                    file_list = zip_ref.namelist()
                    print(f"[DEBUG] Files in ZIP: {len(file_list)} files")
                    
                    # Extraire tous les fichiers dans le répertoire final
                    zip_ref.extractall(final_target_dir)
                    print(f"[DEBUG] Files extracted successfully to {final_target_dir}")
                    
                    # Si le ZIP contient un dossier racine (ex: TG_MANAGER-EN/), déplacer les fichiers
                    extracted_files = os.listdir(final_target_dir)
                    for item in extracted_files:
                        item_path = os.path.join(final_target_dir, item)
                        if os.path.isdir(item_path) and item not in ['setup', 'requirements.txt']:
                            # Déplacer le contenu du sous-dossier vers le répertoire parent
                            src_path = os.path.join(final_target_dir, item)
                            
                            # Déplacer tous les fichiers du sous-dossier vers la racine
                            for sub_item in os.listdir(src_path):
                                sub_src = os.path.join(src_path, sub_item)
                                sub_dest = os.path.join(final_target_dir, sub_item)
                                shutil.move(sub_src, sub_dest)
                            
                            # Supprimer le sous-dossier vide
                            try:
                                os.rmdir(src_path)
                            except:
                                pass
                    
                    print(f"[DEBUG] File structure reorganized for Telegram Manager")
                    
            except zipfile.BadZipFile:
                error_msg = f"The file {zip_file} is not a valid ZIP archive"
                print(f"[ERROR] {error_msg}")
                messagebox.showerror("Extraction Error", error_msg)
                return False
            except Exception as e:
                error_msg = f"Error extracting ZIP file: {e}"
                print(f"[ERROR] {error_msg}")
                messagebox.showerror("Extraction Error", error_msg)
                return False
            
            # Vérifier que les fichiers ont été extraits
            # (Plus de vérification - installation directe)
            
            print(f"[DEBUG] Extraction completed successfully in {final_target_dir}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to extract from PACK: {e}"
            print(error_msg)
            messagebox.showerror("Extraction Error", error_msg)
            return False

    def get_safe_install_dir(self):
        """Retourne un chemin d'installation sécurisé pour l'application.
        
        Returns:
            str: Chemin d'installation sélectionné par l'utilisateur ou un emplacement par défaut.
        """
        # Utiliser le répertoire choisi par l'utilisateur s'il est valide
        user_dir = self.install_dir.get().strip()
        if user_dir:
            try:
                # Vérifier si le chemin est accessible en écriture
                test_file = os.path.join(user_dir, 'test_write.tmp')
                os.makedirs(user_dir, exist_ok=True)
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                return user_dir
            except (OSError, IOError) as e:
                print(f"Unable to use directory {user_dir}: {e}")
        
        # If the user directory is not valid, try default locations
        possible_locations = [
            os.path.join(os.environ['PROGRAMFILES'], 'Telegram Manager'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Telegram Manager'),
            os.path.join(os.path.expanduser('~'), 'Telegram Manager')
        ]
        
        # Vérifier les emplacements possibles
        for location in possible_locations:
            try:
                # Vérifier si le chemin est accessible en écriture
                test_file = os.path.join(location, 'test_write.tmp')
                os.makedirs(location, exist_ok=True)
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                return location
            except (OSError, IOError):
                continue
                
        # Si aucun emplacement n'est accessible, utiliser le répertoire temporaire
        temp_dir = os.path.join(tempfile.gettempdir(), 'Telegram_Manager')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
        
    def _run_installation(self):
        """Exécute le processus d'installation dans un thread séparé."""
        install_dir = None
        try:
            # Use the directory chosen by the user
            install_dir = self.install_dir.get()
            print(f"[DEBUG] _run_installation - Installation directory selected: {install_dir}")
            
            # Verify that the directory is valid
            if not install_dir or not install_dir.strip():
                error_msg = "Please select a valid installation directory"
                print(f"[ERROR] {error_msg}")
                self.root.after(0, self.update_status, error_msg, 0)
                self.root.after(0, messagebox.showerror, "Installation Error", error_msg)
                return
            
            # Verify if the directory exists
            print(f"[DEBUG] Directory verification: {install_dir}")
            if not os.path.exists(install_dir):
                print(f"[DEBUG] Directory creation: {install_dir}")
                try:
                    os.makedirs(install_dir, exist_ok=True)
                except Exception as e:
                    error_msg = f"Failed to create directory {install_dir}: {e}"
                    print(f"[ERROR] {error_msg}")
                    self.root.after(0, self.update_status, error_msg, 0)
                    self.root.after(0, messagebox.showerror, "Installation Error", error_msg)
                    return
            
            # Verify write permissions
            test_file = os.path.join(install_dir, 'test_write.tmp')
            try:
                print(f"[DEBUG] Test write permissions in {test_file}")
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print("[DEBUG] Write permissions test successful")
            except Exception as e:
                error_msg = f"Failed to write to directory {install_dir}: {e}"
                print(f"[ERROR] {error_msg}")
                self.root.after(0, self.update_status, error_msg, 0)
                self.root.after(0, messagebox.showerror, "Installation Error", error_msg)
                return
            
            # Remove temporary directory if it exists
            temp_repo = os.path.join(install_dir, 'repo')
            if os.path.exists(temp_repo):
                print(f"[DEBUG] Temporary directory removal: {temp_repo}")
                try:
                    shutil.rmtree(temp_repo, ignore_errors=True)
                except Exception as e:
                    print(f"[ATTENTION] Unable to remove temporary directory {temp_repo}: {e}")
            
            # Extraire les fichiers depuis le répertoire PACK
            status_msg = "Extracting files from PACK directory..."
            print(f"[DEBUG] {status_msg}")
            self.root.after(0, self.update_status, status_msg, 30)
            
            # Extraire depuis PACK
            print(f"[DEBUG] Calling extract_from_pack with install_dir={install_dir}")
            if not self.extract_from_pack(install_dir):
                error_msg = "Failed to extract files from PACK directory"
                print(f"[ERROR] {error_msg}")
                self.root.after(0, self.update_status, error_msg, 0)
                self.root.after(0, messagebox.showerror, "Installation Error", error_msg)
            else:
                print(f"[DEBUG] File extraction completed successfully in {install_dir}")
                install_dir = self.install_dir.get()
                
                # Install dependencies
                self.root.after(0, self.update_status, "Installing dependencies...", 90)
                print("[DEBUG] Installing dependencies...")
                requirements_path = os.path.join(install_dir, 'requirements.txt')
                # (Plus de vérification - installation directe des dépendances)
                try:
                    print(f"[DEBUG] Executing: {sys.executable} -m pip install -r {requirements_path}")
                    process = subprocess.Popen(
                        [sys.executable, '-m', 'pip', 'install', '-r', requirements_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    stdout, stderr = process.communicate()
                    
                    if process.returncode == 0:
                        print("[DEBUG] Dependencies installed successfully")
                        if stdout:
                            print("[DEBUG] pip output:", stdout)
                    else:
                        error_msg = f"Failed to install dependencies (code {process.returncode})"
                        print(f"[ERROR] {error_msg}")
                        print("[ERROR] Error output:", stderr)
                        self.root.after(0, messagebox.showwarning, 
                                     "Warning", 
                                     f"{error_msg}\n\nPlease manually install dependencies with the command :\npip install -r {requirements_path}")
                except Exception as e:
                    error_msg = f"Error installing dependencies: {str(e)}"
                    print(f"[ERROR] {error_msg}")
                    self.root.after(0, messagebox.showerror, 
                                 "Error", 
                                 f"{error_msg}\n\nPlease manually install dependencies with the command :\npip install -r {requirements_path}")
                
                # Success message
                success_msg = f"Installation completed successfully in {install_dir}"
                print(f"[SUCCESS] {success_msg}")
                self.root.after(0, self.update_status, success_msg, 100)
                
                # Lancer l'application
                launch_path = os.path.join(install_dir, 'launch.py')
                try:
                    # Créer un raccourci sur le bureau si demandé
                    if self.create_desktop_shortcut.get():
                        try:
                            # Forcer l'utilisation du bureau public
                            public_desktop = os.path.join(os.environ.get('PUBLIC', ''), 'Desktop')
                            os.makedirs(public_desktop, exist_ok=True)  # Créer le dossier s'il n'existe pas
                            print(f"[DEBUG] Using public desktop: {public_desktop}")
                            
                            # Créer le raccourci
                            shortcut_created = self.create_shortcut(
                                os.path.join(install_dir, 'launch.py'),
                                'Telegram Manager',
                                public_desktop
                            )
                            
                            if shortcut_created:
                                print("[DEBUG] The shortcut has been created on the desktop")
                                success_msg += "\n- The shortcut has been created on the desktop"
                            else:
                                raise Exception("Failed to create the shortcut")
                                
                        except Exception as e:
                            error_msg = f"[ERROR] Failed to create the shortcut on the desktop: {e}"
                            print(error_msg)
                            success_msg += "\n- Failed to create the shortcut on the desktop"
            
                    # Create a shortcut in the Start Menu (always enabled)
                    try:
                        # Get the Start Menu path
                        start_menu_path = self._get_start_menu_path()
                        os.makedirs(start_menu_path, exist_ok=True)
                        print(f"[DEBUG] Using Start Menu: {start_menu_path}")
                        
                        # Create the shortcut in the Start Menu
                        start_menu_shortcut_created = self.create_shortcut(
                            os.path.join(install_dir, 'launch.py'),
                            'Telegram Manager',
                            start_menu_path
                        )
                        
                        if start_menu_shortcut_created:
                            print("[DEBUG] The shortcut has been created in the Start Menu")
                            success_msg += "\n- The shortcut has been created in the Start Menu"
                        else:
                            print("[WARNING] Failed to create the shortcut in the Start Menu")
                            success_msg += "\n- Failed to create the shortcut in the Start Menu"
                            
                    except Exception as e:
                        error_msg = f"[WARNING] Error creating Start Menu shortcut: {e}"
                        print(error_msg)
                        success_msg += "\n- Failed to create the shortcut in the Start Menu"
                        
                    # Launch the application in the background
                    setup_src_path = os.path.join(install_dir, 'setup', 'src')
                    main_script = os.path.join(setup_src_path, 'main.py')
                    if os.path.exists(main_script):
                        subprocess.Popen(
                            [sys.executable, main_script],
                            cwd=setup_src_path,
                            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP,
                            close_fds=True
                        )
                        print("[DEBUG] Application launched in the background successfully")
                    else:
                        print(f"[ERROR] Main file not found: {main_script}")
                    print("[DEBUG] Application launched successfully")
                    
                    success_msg += "\n\nTelegram Manager has been launched automatically."
                    
                except Exception as e:
                    error_msg = f"[ERROR] Failed to launch Telegram Manager: {e}"
                    print(error_msg)
                    success_msg += "\n\nFailed to launch Telegram Manager automatically. Please launch it manually by running 'launch.py' in the installation directory."
            
                self.root.after(0, messagebox.showinfo, "Installation successful", success_msg)
                return
                
            # Mettre à jour le statut de l'installation
            self.root.after(0, self.update_status, "Installation completed successfully!", 100)
            
        except Exception as e:
            error_msg = f"Unexpected error during installation : {e}"
            print(error_msg)
            self.root.after(0, self.update_status, error_msg, 0)
            self.root.after(0, messagebox.showerror, "Installation error", error_msg)
        finally:
            # Réactiver le bouton d'installation dans tous les cas
            if hasattr(self, 'install_btn'):
                self.root.after(0, self.install_btn.config, {
                    'state': tk.NORMAL, 
                    'text': 'Retry' if self.installation_in_progress else 'Install'
                })
            self.installation_in_progress = False

    def start_installation(self):
        """Lance le processus d'installation de l'application."""
        if self.installation_in_progress:
            return
            
        self.installation_in_progress = True
        if hasattr(self, 'install_btn'):
            self.install_btn.config(state=tk.DISABLED)
        
        # Démarrer l'installation dans un thread séparé
        threading.Thread(target=self._run_installation, daemon=True).start()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    # Créer un fichier de log pour le débogage
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Log_file.log')
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("=== Installation started ===\n")
    
    def log(message):
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[LOG] {message}\n")
        print(f"[LOG] {message}")
    
    try:
        log("Installation started...")
        
        if not is_admin():
            log("Elevation of privileges required...")
            try:
                script_path = os.path.abspath(__file__)
                log(f"Script path: {script_path}")
                log(f"Python interpreter: {sys.executable}")
                
                # Display an information dialog
                ctypes.windll.user32.MessageBoxW(
                    0,
                    "Telegram Manager installation requires administrator privileges.\n\nPlease confirm elevation of privileges in the window that will open.",
                    "Installation of Telegram Manager",
                    0x40 | 0x1  # MB_ICONINFORMATION | MB_OKCANCEL
                )
                
                # Relancer avec élévation
                result = ctypes.windll.shell32.ShellExecuteW(
                    None, 
                    "runas", 
                    sys.executable, 
                    f'"{script_path}"', 
                    None, 
                    1
                )
                
                if result <= 32:
                    raise Exception(f"Failed to elevate privileges. Error code: {result}")
                
                log("Relaunch with elevation of privileges requested")
                return
                
            except Exception as e:
                error_msg = f"Error elevating privileges: {e}"
                log(error_msg)
                ctypes.windll.user32.MessageBoxW(
                    0,
                    f"{error_msg}\n\nPlease manually launch the installer as an administrator.\n\nLog details: {log_file}",
                    "Installation error",
                    0x10  # MB_ICONERROR
                )
                return
        
        # If we get here, we have administrator privileges
        log("Administrator privileges confirmed")
        
        # Check dependencies
        try:
            log("Checking dependencies...")
            import tkinter as tk
            from tkinter import ttk
            import win32com.client
            log("All dependencies are available")
        except ImportError as e:
            log(f"Missing dependency: {e}")
            ctypes.windll.user32.MessageBoxW(
                0,
                f"A required dependency is missing: {e}\n\nPlease install the dependencies with the command:\npip install pywin32\n\nLog details: {log_file}",
                "Missing dependency",
                0x10  # MB_ICONERROR
            )
            return
        
        # Start the user interface
        try:
            log("Creating user interface...")
            root = tk.Tk()
            # Set the application icon
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, 'app_icon.ico')
            if os.path.exists(icon_path):
                try:
                    # Méthode principale
                    root.iconbitmap(icon_path)
                    root.wm_iconbitmap(icon_path)

                    # Méthode alternative avec ctypes pour forcer l'icône
                    try:
                        import ctypes
                        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TelegramManager.Installer")
                        root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=icon_path))
                    except Exception as e:
                        log(f"Alternative method failed: {e}")

                    log(f"Icon loaded successfully: {icon_path}")
                except Exception as e:
                    log(f"Failed to load icon: {e}")
            else:
                log(f"Icon file not found: {icon_path}")
            
            app = InstallerApp(root)
            log("Starting main loop...")
            root.mainloop()
            log("Installation completed successfully")
            
        except Exception as e:
            error_msg = f"Error starting application: {e}"
            log(error_msg)
            import traceback
            log("Complete traceback:")
            log(traceback.format_exc())
            
            ctypes.windll.user32.MessageBoxW(
                0,
                f"An error occurred while starting the application.\n\nError: {str(e)}\n\nPlease check the log file for more details.\n\nLog file path: {log_file}",
                "Application error",
                0x10  # MB_ICONERROR
            )
    
    except Exception as e:
        # Capture des erreurs inattendues
        error_msg = f"Unexpected error: {e}"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[ERROR] {error_msg}\n")
            import traceback
            f.write("Complete traceback:\n")
            f.write(traceback.format_exc())
        
        print(f"[ERROR] {error_msg}")
        ctypes.windll.user32.MessageBoxW(
            0,
            f"An unexpected error occurred.\n\nError: {str(e)}\n\nPlease check the log file for more details.\n\nLog file path: {log_file}",
            "Critical error",
            0x10  # MB_ICONERROR
        )

if __name__ == "__main__":
    main()
