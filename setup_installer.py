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
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10))
        
        # Variables
        self.install_dir = tk.StringVar(value=os.environ['PROGRAMFILES'])
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_start_menu = tk.BooleanVar(value=True)
        self.github_repo = 'https://github.com/Joelab7/TG_MANAGER.git'
        self.github_token = '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'
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
            font=('Segoe UI', 16, 'bold')
        )
        header.pack(pady=(0, 20))
        
        # Frame de contenu
        content = ttk.Frame(main_frame)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Sélection du répertoire d'installation
        dir_frame = ttk.Frame(content)
        dir_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(dir_frame, text="Installation directory:").pack(anchor='w')
        
        dir_entry_frame = ttk.Frame(dir_frame)
        dir_entry_frame.pack(fill=tk.X, pady=5)
        
        self.dir_entry = ttk.Entry(dir_entry_frame, textvariable=self.install_dir, width=50)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(dir_entry_frame, text="Browse...", command=self.browse_directory)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Installation options
        options_frame = ttk.LabelFrame(content, text="Installation options", padding=10)
        options_frame.pack(fill=tk.X, pady=10)
        
        ttk.Checkbutton(
            options_frame, 
            text="Create a Python launcher(TM) on the desktop to launch Telegram Manager(it is recommended)",
            variable=self.create_desktop_shortcut
        ).pack(anchor='w', pady=2)
        
        # Espacement
        ttk.Frame(content, height=20).pack()
        
        # Style pour la barre de progression
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Custom.Horizontal.TProgressbar",
            thickness=20,
            troughcolor='#f0f0f0',
            background='#4CAF50',  # Couleur verte
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
            foreground='#666666',
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
        
        # Style pour le bouton d'installation
        self.style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))
    
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
                self.update_status(f"Installation directory selected: {directory}", 0)
        except Exception as e:
            error_msg = f"Error selecting directory: {e}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def update_status(self, message, progress=None):
        if hasattr(self, 'status_var'):
            self.status_var.set(message)
            
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
            
    def _create_batch_file(self, target_dir, name):
        """Crée un fichier batch pour lancer l'application en arrière-plan."""
        batch_content = f"""@echo off
start "" /B "{sys.executable}" "{os.path.join(target_dir, 'launch.py')}" %*
"""
        batch_path = os.path.join(target_dir, f"{name}.bat")
        with open(batch_path, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        return batch_path

    def create_shortcut(self, target, name, directory):
        """Crée un raccourci Windows qui demande l'élévation des privilèges."""
        try:
            import pythoncom
            from win32com.client import Dispatch
            import ctypes
            import sys
            import os
            
            # Créer le fichier batch
            target_dir = os.path.dirname(target)
            batch_path = self._create_batch_file(target_dir, name)
            
            # Créer le chemin complet du raccourci
            shortcut_path = os.path.join(directory, f"{name}.lnk")
            
            # Initialiser COM
            pythoncom.CoInitialize()
            
            try:
                # Créer le raccourci
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                
                # Configurer le raccourci pour exécuter avec pythonw.exe (sans console)
                setup_src_path = os.path.join(target_dir, "setup", "src")
                pythonw_exe = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
                
                # Vérifier si pythonw.exe existe, sinon utiliser python.exe
                if not os.path.exists(pythonw_exe):
                    pythonw_exe = sys.executable
                    
                # Configurer le raccourci
                shortcut.TargetPath = pythonw_exe
                shortcut.Arguments = f'"{os.path.join(setup_src_path, "main.py")}"'
                shortcut.WorkingDirectory = setup_src_path
                shortcut.WindowStyle = 0  # 0 = Caché
                
                # Chemin de l'icône pour Telegram Manager
                icon_path = os.path.join(target_dir, 'setup', 'src', 'telegram_manager', 'resources', 'icons', 'app_icon')
                
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
                        print(f"[INFO] Successfully loaded icon for {name}")
                        
                        # Nettoyer
                        window.close()
                        if QApplication.instance() is None:
                            app.quit()
                            
                    except Exception as e:
                        print(f"[WARNING] Unable to load icon with QMainWindow: {e}")
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
                    print("[WARNING] Unable to force elevation: {e}")
                
                # Cacher le fichier batch
                try:
                    ctypes.windll.kernel32.SetFileAttributesW(batch_path, 0x02)  # FILE_ATTRIBUTE_HIDDEN
                except:
                    pass
                
                return True
                
            finally:
                # Nettoyer COM
                pythoncom.CoUninitialize()
                
        except Exception as e:
            print(f"[ERROR] Unable to create shortcut {name}: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def download_github_repo(self, url, target_dir):
        """Clone le dépôt GitHub en utilisant git avec authentification par token."""
        print(f"[DEBUG] Starting download_github_repo with target_dir: {target_dir}")
        temp_dir = None
        
        # Vérifier si git est installé
        try:
            subprocess.run(['git', '--version'], check=True, capture_output=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            error_msg = "Git is not installed or not in PATH."
            print(f"{error_msg} Error: {e}")
            messagebox.showerror(
                "Installation Error",
                f"{error_msg}\n\n"
                "Please install Git from https://git-scm.com/download/win\n"
                "and verify that it is added to your PATH."
            )
            return False
        
        try:
            # Vérifier si le répertoire cible existe déjà avec un installateur
            print(f"[DEBUG] Checking target directory: {target_dir}")
            if os.path.exists(target_dir):
                setup_path = os.path.join(target_dir, 'setup_installer.py')
                print(f"[DEBUG] Checking existence of {setup_path}")
                if os.path.exists(setup_path):
                    print("[DEBUG] Installation already present, returning True")
                    return True  # Installation déjà présente
                
                # Ne pas créer de nouveau dossier, utiliser celui spécifié
                # car le répertoire de téléchargement est déjà un emplacement valide
                pass
            
            # Create the target directory if it doesn't exist
            print(f"[DEBUG] Creating target directory: {target_dir}")
            os.makedirs(target_dir, exist_ok=True)
            
            # Verify that the directory is writable
            test_file = os.path.join(target_dir, 'test_write.tmp')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"[DEBUG] Directory {target_dir} is writable")
                
                # Create a subdirectory 'TelegramManager' if it doesn't exist
                if not target_dir.endswith('Telegram Manager'):
                    target_dir = os.path.join(target_dir, 'Telegram Manager')
                    os.makedirs(target_dir, exist_ok=True)
                    print(f"[DEBUG] Using subdirectory: {target_dir}")
                
                # Mettre à jour la variable de classe avec le chemin final
                self.install_dir.set(target_dir)
                print(f"[DEBUG] Installation directory set to: {target_dir}")
            except Exception as e:
                print(f"[ERROR] Unable to write to {target_dir}: {e}")
                return False
            
            # Configurer l'authentification
            env = os.environ.copy()
            env['GIT_TERMINAL_PROMPT'] = '0'  # Désactiver les invites interactives
            
            # Construire l'URL d'authentification avec token
            auth_url = f"https://{self.github_token}@github.com/Joelab7/TG_MANAGER.git"
            
            # Créer un répertoire temporaire pour le clonage
            temp_dir = tempfile.mkdtemp(prefix='tg_manager_', dir=os.environ.get('TEMP'))
            
            try:
                self.update_status("Cloning GitHub repository...", 20)
                
                # Exécuter git clone avec authentification
                process = subprocess.Popen(
                    ['git', 'clone', '--depth', '1', '--single-branch', auth_url, 'repo'],
                    cwd=temp_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                # Attendre la fin du processus avec un timeout
                try:
                    stdout, stderr = process.communicate(timeout=300)  # 5 minutes de timeout
                    
                    if process.returncode != 0:
                        error_msg = f"Cloning failed.\n\nError output:\n{stderr}"
                        print(error_msg)
                        messagebox.showerror("Cloning Error", error_msg)
                        return False
                        
                except subprocess.TimeoutExpired:
                    process.kill()
                    raise Exception("Cloning took too long. Check your internet connection.")
                
                source_dir = os.path.join(temp_dir, 'repo')
                
                # Vérifier que le clonage a réussi
                if not os.path.exists(source_dir):
                    raise Exception("Cloning failed: source directory does not exist")
                
                # Copy the cloned files to the target directory
                print(f"[DEBUG] Copying files from {source_dir} to {target_dir}")
                items_copied = 0
                for item in os.listdir(source_dir):
                    s = os.path.join(source_dir, item)
                    d = os.path.join(target_dir, item)
                    try:
                        if os.path.isdir(s):
                            print(f"[DEBUG] Copying directory: {s} to {d}")
                            shutil.copytree(s, d, dirs_exist_ok=True)
                        else:
                            print(f"[DEBUG] Copying file: {s} to {d}")
                            shutil.copy2(s, d)
                        items_copied += 1
                    except Exception as copy_error:
                        print(f"[ERREUR] Impossible de copier {s} vers {d}: {copy_error}")
                        continue
                
                print(f"[DEBUG] {items_copied} elements copied successfully")
                
                return True
                
            except Exception as e:
                error_msg = f"Cloning failed: {e}"
                print(error_msg)
                messagebox.showerror("Installation Error", error_msg)
                return False
                
            finally:
                # Nettoyer le répertoire temporaire
                if temp_dir and os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    except Exception as e:
                        print(f"Warning: impossible to delete temporary directory {temp_dir}: {e}")
                        
        except Exception as e:
            error_msg = f"Installation Error: {e}"
            print(error_msg)
            messagebox.showerror("Installation Error", error_msg)
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
                print(f"Warning: impossible to use directory {user_dir}: {e}")
        
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
            # Utiliser le répertoire choisi par l'utilisateur
            install_dir = self.install_dir.get()
            print(f"[DEBUG] _run_installation - Installation directory selected: {install_dir}")
            
            # Vérifier que le répertoire est valide
            if not install_dir or not install_dir.strip():
                error_msg = "Please select a valid installation directory"
                print(f"[ERROR] {error_msg}")
                self.root.after(0, self.update_status, error_msg, 0)
                self.root.after(0, messagebox.showerror, "Installation Error", error_msg)
                return
            
            # Vérifier si le répertoire existe
            print(f"[DEBUG] Checking directory: {install_dir}")
            if not os.path.exists(install_dir):
                print(f"[DEBUG] Creating directory: {install_dir}")
                try:
                    os.makedirs(install_dir, exist_ok=True)
                except Exception as e:
                    error_msg = f"Unable to create directory {install_dir}: {e}"
                    print(f"[ERROR] {error_msg}")
                    self.root.after(0, self.update_status, error_msg, 0)
                    self.root.after(0, messagebox.showerror, "Installation Error", error_msg)
                    return
            
            # Vérifier les permissions en écriture
            test_file = os.path.join(install_dir, 'test_write.tmp')
            try:
                print(f"[DEBUG] Testing write permission in {test_file}")
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print("[DEBUG] Write permission test successful")
            except Exception as e:
                error_msg = f"Unable to write to directory {install_dir}: {e}"
                print(f"[ERROR] {error_msg}")
                self.root.after(0, self.update_status, error_msg, 0)
                self.root.after(0, messagebox.showerror, "Installation Error", error_msg)
                return
            
            # Supprimer le dossier temporaire s'il existe
            temp_repo = os.path.join(install_dir, 'repo')
            if os.path.exists(temp_repo):
                print(f"[DEBUG] Deleting temporary directory: {temp_repo}")
                try:
                    shutil.rmtree(temp_repo, ignore_errors=True)
                except Exception as e:
                    print(f"[WARNING] Unable to delete temporary directory {temp_repo}: {e}")
            
            # Télécharger le dépôt GitHub
            status_msg = "Downloading GitHub repository..."
            print(f"[DEBUG] {status_msg}")
            self.root.after(0, self.update_status, status_msg, 30)
            
            # Télécharger le dépôt
            print(f"[DEBUG] Calling download_github_repo with install_dir={install_dir}")
            if not self.download_github_repo(None, install_dir):
                error_msg = "Failed to download GitHub repository"
                print(f"[ERROR] {error_msg}")
                self.root.after(0, self.update_status, error_msg, 0)
                self.root.after(0, messagebox.showerror, "Installation Error", error_msg)
            else:
                print(f"[DEBUG] Download and file copy completed successfully in {install_dir}")
                # Vérifier que les fichiers ont bien été copiés
                required_files = ['setup_installer.py', 'launch.py']
                install_dir = self.install_dir.get()
                
                print(f"[DEBUG] Checking files in {install_dir}")
                missing_files = [f for f in required_files if not os.path.exists(os.path.join(install_dir, f))]
                
                if missing_files:
                    error_msg = f"Missing files in {install_dir}: {', '.join(missing_files)}"
                    print(f"[ERROR] {error_msg}")
                    print(f"[DEBUG] Directory content: {os.listdir(install_dir)}")
                    self.root.after(0, self.update_status, error_msg, 0)
                    self.root.after(0, messagebox.showerror, "Installation Error", error_msg)
                else:
                    # Installation des dépendances
                    self.root.after(0, self.update_status, "Installing dependencies...", 90)
                    print("[DEBUG] Installing dependencies...")
                    requirements_path = os.path.join(install_dir, 'requirements.txt')
                    if os.path.exists(requirements_path):
                        try:
                            print(f"[DEBUG] Running: {sys.executable} -m pip install -r {requirements_path}")
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
                    
                    # Message de succès
                    success_msg = f"Installation completed successfully in {install_dir}"
                    print(f"[SUCCESS] {success_msg}")
                    self.root.after(0, self.update_status, success_msg, 100)
                    
                    # Lancer l'application
                    launch_path = os.path.join(install_dir, 'launch.py')
                    if os.path.exists(launch_path):
                        try:
                            # Créer un raccourci sur le bureau si demandé
                            if self.create_desktop_shortcut.get():
                                try:
                                    # Créer un dossier pour les raccourcis si nécessaire
                                    shortcuts_dir = os.path.join(install_dir, 'Shortcuts')
                                    os.makedirs(shortcuts_dir, exist_ok=True)
                                    
                                    # Forcer l'utilisation du bureau public
                                    public_desktop = os.path.join(os.environ.get('PUBLIC', ''), 'Desktop')
                                    os.makedirs(public_desktop, exist_ok=True)  # Créer le dossier s'il n'existe pas
                                    print(f"[DEBUG] Using public desktop: {public_desktop}")
                                    
                                    # Créer le raccourci
                                    shortcut_created = self.create_shortcut(
                                        os.path.join(install_dir, 'launch.py'),
                                        'Python launcher(TM)',
                                        public_desktop
                                    )
                                    
                                    if shortcut_created:
                                        print("[DEBUG] The Python launcher(TM) has been created on the desktop")
                                        success_msg += "\n- The Python launcher(TM) has been created on the desktop"
                                    else:
                                        raise Exception("Failed to create shortcut(Python launcher(TM))")
                                        
                                except Exception as e:
                                    error_msg = f"[ERROR] Failed to create shortcut(Python launcher(TM)) on the desktop: {e}"
                                    print(error_msg)
                                    success_msg += "\n- Failed to create shortcut(Python launcher(TM)) on the desktop"
                            
                            # Le raccourci du menu Démarrer a été supprimé de cette version
                            
                            # Lancer l'application en arrière-plan
                            setup_src_path = os.path.join(install_dir, 'setup', 'src')
                            main_script = os.path.join(setup_src_path, 'main.py')
                            if os.path.exists(main_script):
                                subprocess.Popen(
                                    [sys.executable, main_script],
                                    cwd=setup_src_path,
                                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP,
                                    close_fds=True
                                )
                                print("[DEBUG] Telegram Manager launched in the background successfully")
                            else:
                                print(f"[ERROR] Main script not found: {main_script}")
                            print("[DEBUG] Telegram Manager launched successfully")
                            
                            success_msg += "\n\nTelegram Manager launched automatically."
                            
                        except Exception as e:
                            error_msg = f"[ERROR] Failed to launch Telegram Manager: {e}"
                            print(error_msg)
                            success_msg += "\n\nTelegram Manager could not be launched automatically. Please launch it manually by running 'launch.py' in the installation directory."
                    
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
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'installer.log')
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("=== Start of installation ===\n")
    
    def log(message):
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[LOG] {message}\n")
        print(f"[LOG] {message}")
    
    try:
        log("Starting installation...")
        
        if not is_admin():
            log("Elevating privileges...")
            try:
                script_path = os.path.abspath(__file__)
                log(f"Script path: {script_path}")
                log(f"Python interpreter: {sys.executable}")
                
                # Afficher une boîte de dialogue d'information
                ctypes.windll.user32.MessageBoxW(
                    0,
                    "Telegram Manager installation requires administrator privileges.\n\nPlease confirm elevation of privileges in the window that will open.",
                    "Telegram Manager Installation",
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
                    raise Exception(f"Privilege elevation failed. Error code: {result}")
                
                log("Privilege elevation requested")
                return
                
            except Exception as e:
                error_msg = f"Privilege elevation failed: {e}"
                log(error_msg)
                ctypes.windll.user32.MessageBoxW(
                    0,
                    f"{error_msg}\n\nPlease manually launch the installer as administrator.\n\nLog details: {log_file}",
                    "Installation error",
                    0x10  # MB_ICONERROR
                )
                return
        
        # Si on arrive ici, on a les droits administrateur
        log("Administrator privileges confirmed")
        
        # Vérifier les dépendances
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
                "Dependency missing",
                0x10  # MB_ICONERROR
            )
            return
        
        # Démarrer l'interface utilisateur
        try:
            log("Starting user interface...")
            root = tk.Tk()
            app = InstallerApp(root)
            log("Starting main loop...")
            root.mainloop()
            log("Installation completed successfully")
            
        except Exception as e:
            error_msg = f"Application startup error: {e}"
            log(error_msg)
            import traceback
            log("Traceback complet:")
            log(traceback.format_exc())
            
            ctypes.windll.user32.MessageBoxW(
                0,
                f"An error occurred during application startup.\n\nError: {str(e)}\n\nPlease check the log file for more details.\n\nLog file path: {log_file}",
                "Application error",
                0x10  # MB_ICONERROR
            )
    
    except Exception as e:
        # Capture des erreurs inattendues
        error_msg = f"Unexpected error: {e}"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[ERROR] {error_msg}\n")
            import traceback
            f.write("Traceback complet:\n")
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
