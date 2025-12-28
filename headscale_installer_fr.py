# headscale_installer_fr.py
# Installeur client Windows Headscale générique
# Configurez les paramètres ci-dessous avant de compiler

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
import urllib.request
import tempfile
import re
import time
import ctypes
import shutil

# ================================================================
# CONFIGURATION - METTEZ À JOUR CES VALEURS
# ================================================================

HEADSCALE_URL = "https://vpn.example.com"  # URL de votre serveur Headscale
AUTH_KEY = "VOTRE_CLE_PREAUTH_ICI"          # Votre clé de pré-authentification
BASE_DOMAIN = "vpn.example.com"             # Votre domaine MagicDNS de base
TAILSCALE_MSI_URL = "https://pkgs.tailscale.com/stable/tailscale-setup-1.92.3-amd64.msi"
VERSION = "1.0.0"

# ================================================================

def is_admin():
    """Vérifie si exécuté avec privilèges admin"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Relance le programme avec privilèges admin"""
    try:
        if sys.argv[0].endswith('.py'):
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
        else:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, "", None, 1
            )
        sys.exit(0)
    except Exception as e:
        messagebox.showerror(
            "Erreur d'élévation des privilèges",
            f"Impossible d'obtenir les droits administrateur.\n\n{str(e)}"
        )
        sys.exit(1)

class VPNInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Installeur VPN Headscale v{VERSION}")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        
        self.installing = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        bg_color = "#f5f5f5"
        primary_color = "#2563eb"
        accent_color = "#1e40af"
        
        self.root.configure(bg=bg_color)
        
        # En-tête
        header_frame = tk.Frame(root, bg=primary_color, height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="🔒 VPN Headscale",
            font=("Segoe UI", 22, "bold"),
            bg=primary_color,
            fg="white"
        )
        title.pack(pady=(15, 5))
        
        subtitle = tk.Label(
            header_frame,
            text="Installeur d'accès sécurisé à distance",
            font=("Segoe UI", 11),
            bg=primary_color,
            fg="#e0e7ff"
        )
        subtitle.pack()
        
        # Cadre principal
        main_frame = tk.Frame(root, bg=bg_color, padx=40, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instruction = tk.Label(
            main_frame,
            text="Remplissez les informations ci-dessous pour installer le VPN :",
            font=("Segoe UI", 9),
            bg=bg_color,
            fg="#374151",
            wraplength=500,
            justify=tk.LEFT
        )
        instruction.pack(anchor=tk.W, pady=(0, 20))
        
        # Nom du client
        tk.Label(
            main_frame,
            text="Nom du client *",
            font=("Segoe UI", 10, "bold"),
            bg=bg_color,
            fg="#1f2937"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.client_entry = ttk.Entry(main_frame, font=("Segoe UI", 11))
        self.client_entry.pack(fill=tk.X, pady=(0, 3), ipady=5)
        self.client_entry.bind("<KeyRelease>", self.update_preview)
        
        tk.Label(
            main_frame,
            text="Exemple : Nom d'Entreprise, Jean Dupont",
            font=("Segoe UI", 8),
            bg=bg_color,
            fg="#6b7280"
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Type d'appareil
        tk.Label(
            main_frame,
            text="Type d'appareil *",
            font=("Segoe UI", 10, "bold"),
            bg=bg_color,
            fg="#1f2937"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.type_entry = ttk.Entry(main_frame, font=("Segoe UI", 11))
        self.type_entry.pack(fill=tk.X, pady=(0, 3), ipady=5)
        self.type_entry.insert(0, "Bureau")
        self.type_entry.bind("<KeyRelease>", self.update_preview)
        
        tk.Label(
            main_frame,
            text="Exemple : Bureau, Portable, Serveur, Caisse",
            font=("Segoe UI", 8),
            bg=bg_color,
            fg="#6b7280"
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Aperçu
        preview_frame = tk.Frame(main_frame, bg="#dbeafe", bd=0, relief=tk.FLAT)
        preview_frame.pack(fill=tk.X, pady=(5, 20))
        
        preview_inner = tk.Frame(preview_frame, bg="#dbeafe")
        preview_inner.pack(padx=15, pady=12)
        
        tk.Label(
            preview_inner,
            text="📌 Identifiant VPN :",
            font=("Segoe UI", 9, "bold"),
            bg="#dbeafe",
            fg="#1e40af"
        ).pack(anchor=tk.W)
        
        self.preview_label = tk.Label(
            preview_inner,
            text="(remplir le nom du client)",
            font=("Courier New", 11, "bold"),
            bg="#dbeafe",
            fg="#1f2937"
        )
        self.preview_label.pack(anchor=tk.W, pady=(3, 0))
        
        # Statut
        self.status_label = tk.Label(
            main_frame,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            fg="#2563eb",
            wraplength=500
        )
        self.status_label.pack(pady=(0, 15))
        
        # Bouton d'installation
        button_frame = tk.Frame(main_frame, bg=bg_color)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.install_button = tk.Button(
            button_frame,
            text="⚡ Installer maintenant",
            font=("Segoe UI", 13, "bold"),
            bg=primary_color,
            fg="white",
            activebackground=accent_color,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.install,
            bd=0,
            highlightthickness=0
        )
        self.install_button.pack(fill=tk.X, ipady=12)
        
        # Pied de page
        footer = tk.Label(
            main_frame,
            text=f"Version {VERSION}",
            font=("Segoe UI", 8),
            bg=bg_color,
            fg="#9ca3af"
        )
        footer.pack(side=tk.BOTTOM, pady=(15, 0))
        
        self.client_entry.focus()
    
    def on_close(self):
        if self.installing:
            if messagebox.askyesno("Installation en cours", "Voulez-vous vraiment annuler ?"):
                self.root.destroy()
        else:
            self.root.destroy()
    
    def clean_accents(self, text):
        replacements = {
            'à': 'a', 'â': 'a', 'á': 'a', 'ä': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'ï': 'i', 'î': 'i', 'í': 'i',
            'ô': 'o', 'ó': 'o', 'ö': 'o',
            'ù': 'u', 'û': 'u', 'ú': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n'
        }
        for accent, replacement in replacements.items():
            text = text.replace(accent, replacement)
        return text
    
    def generate_hostname(self, client, pc_type):
        client_clean = self.clean_accents(client)
        hostname = f"{client_clean}-{pc_type}"
        hostname = hostname.lower()
        hostname = re.sub(r'[^a-z0-9-]', '-', hostname)
        hostname = re.sub(r'-+', '-', hostname)
        hostname = hostname.strip('-')
        return hostname
    
    def update_preview(self, event=None):
        client = self.client_entry.get().strip()
        pc_type = self.type_entry.get().strip()
        
        if client and pc_type:
            hostname = self.generate_hostname(client, pc_type)
            self.preview_label.config(text=f"{hostname}.{BASE_DOMAIN}", fg="#1f2937")
        elif client:
            self.preview_label.config(text=f"{client.lower()}-(type appareil).{BASE_DOMAIN}", fg="#9ca3af")
        else:
            self.preview_label.config(text="(remplir les champs)", fg="#9ca3af")
    
    def download_with_progress(self, url, dest):
        try:
            def reporthook(blocknum, blocksize, totalsize):
                if totalsize > 0:
                    percent = min(100, blocknum * blocksize * 100 / totalsize)
                    self.status_label.config(text=f"⏳ Téléchargement... {int(percent)}%")
                    self.root.update()
            
            urllib.request.urlretrieve(url, dest, reporthook)
            return True
        except Exception as e:
            messagebox.showerror(
                "Erreur de téléchargement",
                f"Impossible de télécharger Tailscale.\n\n{str(e)}"
            )
            return False
    
    def install(self):
        client = self.client_entry.get().strip()
        pc_type = self.type_entry.get().strip()
        log_file = None
        
        if not client:
            messagebox.showwarning("Champ requis", "Veuillez entrer le nom du client.")
            self.client_entry.focus()
            return
        
        if not pc_type:
            messagebox.showwarning("Champ requis", "Veuillez entrer le type d'appareil.")
            self.type_entry.focus()
            return
        
        hostname = self.generate_hostname(client, pc_type)
        
        confirm = messagebox.askyesno(
            "Confirmation d'installation",
            f"Installation VPN pour :\n\n"
            f"📋 Client : {client}\n"
            f"💻 Type : {pc_type}\n"
            f"🔖 Identifiant : {hostname}.{BASE_DOMAIN}\n\n"
            f"Continuer ?"
        )
        
        if not confirm:
            return
        
        self.installing = True
        self.install_button.config(
            state=tk.DISABLED,
            text="⏳ Installation en cours...",
            bg="#9ca3af"
        )
        self.root.update()
        
        try:
            tailscale_exe = r"C:\Program Files\Tailscale\tailscale.exe"
            
            # Si déjà installé, reconfigurer
            if os.path.exists(tailscale_exe):
                self.status_label.config(text="⚙️ Reconfiguration en cours, merci de patienter...")
                self.root.update()
                
                # Tuer l'interface
                try:
                    subprocess.run(['taskkill', '/F', '/IM', 'tailscale-ipn.exe'], 
                                 capture_output=True, timeout=5)
                except:
                    pass
                
                # Déconnexion d'abord
                subprocess.run([tailscale_exe, 'logout'], capture_output=True, timeout=10)
                time.sleep(2)
                
                # Arrêter et démarrer le service
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
                
                subprocess.run(['net', 'stop', 'Tailscale'], 
                             capture_output=True, timeout=10, 
                             startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(2)
                subprocess.run(['net', 'start', 'Tailscale'], 
                             capture_output=True, timeout=10,
                             startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(3)
                
                # Connexion
                subprocess.run([
                    tailscale_exe, 'login',
                    f'--login-server={HEADSCALE_URL}',
                    f'--authkey={AUTH_KEY}',
                    f'--hostname={hostname}',
                    '--accept-routes'
                ], capture_output=True, timeout=30)
                
                # Mode sans surveillance
                subprocess.run([tailscale_exe, 'set', '--unattended'], 
                             capture_output=True, timeout=10)
                
                # Redémarrer pour appliquer
                self.status_label.config(text="🔄 Finalisation de la configuration, merci de patienter...")
                self.root.update()
                
                subprocess.run(['net', 'stop', 'Tailscale'], 
                             capture_output=True, timeout=10,
                             startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(2)
                subprocess.run(['net', 'start', 'Tailscale'], 
                             capture_output=True, timeout=10,
                             startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(5)
                
                # Lancer l'interface
                tailscale_gui = r"C:\Program Files\Tailscale\tailscale-ipn.exe"
                if os.path.exists(tailscale_gui):
                    try:
                        subprocess.Popen([tailscale_gui], 
                                       creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
                    except:
                        pass
                
                messagebox.showinfo(
                    "✅ Configuration réussie",
                    f"VPN configuré !\n\n"
                    f"📋 {client}\n"
                    f"💻 {pc_type}\n"
                    f"🔖 {hostname}.{BASE_DOMAIN}"
                )
                self.root.destroy()
                return
            
            # Télécharger Tailscale MSI
            temp_dir = tempfile.gettempdir()
            msi_path = os.path.join(temp_dir, "tailscale-setup.msi")
            
            self.status_label.config(text="⏳ Téléchargement...")
            self.root.update()
            
            if not self.download_with_progress(TAILSCALE_MSI_URL, msi_path):
                self.installing = False
                self.install_button.config(state=tk.NORMAL, text="⚡ Installer maintenant", bg="#2563eb")
                return
            
            # Installer MSI
            self.status_label.config(text="⚙️ Installation...")
            self.root.update()
            
            log_file = os.path.join(temp_dir, "headscale-install.log")
            with open(log_file, 'w') as log:
                log.write(f"=== Installation VPN Headscale ===\n")
                log.write(f"Client : {client}\n")
                log.write(f"Type : {pc_type}\n")
                log.write(f"Nom d'hôte : {hostname}\n")
                log.write(f"Headscale : {HEADSCALE_URL}\n\n")
                log.write(f"Installation du MSI...\n")
            
            install_cmd = [
                "msiexec",
                "/i",
                msi_path,
                "/quiet",
                "/norestart"
            ]
            
            process = subprocess.Popen(install_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            try:
                stdout, stderr = process.communicate(timeout=180)
                with open(log_file, 'a') as log:
                    log.write(f"Code de retour : {process.returncode}\n")
                    if stdout:
                        log.write(f"STDOUT : {stdout.decode('utf-8', errors='ignore')}\n")
                    if stderr:
                        log.write(f"STDERR : {stderr.decode('utf-8', errors='ignore')}\n")
            except subprocess.TimeoutExpired:
                process.kill()
                raise Exception("Délai d'installation dépassé (>3min)")
            
            if process.returncode not in [0, 3010]:
                raise Exception(f"Échec de l'installation (code {process.returncode})")
            
            # Configuration
            self.status_label.config(text="⚙️ Configuration en cours, merci de patienter...")
            self.root.update()
            time.sleep(5)
            
            with open(log_file, 'a') as log:
                log.write(f"\nArrêt de l'interface Tailscale...\n")
            
            # Tuer l'interface
            for proc in ['tailscale-ipn.exe', 'tailscale.exe']:
                try:
                    subprocess.run(['taskkill', '/F', '/IM', proc], 
                                 capture_output=True, timeout=5)
                except:
                    pass
            
            time.sleep(2)
            
            # Arrêter le service
            with open(log_file, 'a') as log:
                log.write(f"Arrêt du service...\n")
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
            
            try:
                subprocess.run(['net', 'stop', 'Tailscale'], 
                             capture_output=True, timeout=10,
                             startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(2)
            except:
                pass
            
            # Démarrer le service
            with open(log_file, 'a') as log:
                log.write(f"Démarrage du service...\n")
            
            try:
                subprocess.run(['net', 'start', 'Tailscale'], 
                             capture_output=True, timeout=10,
                             startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(5)
            except:
                pass
            
            # Configurer avec tailscale login
            with open(log_file, 'a') as log:
                log.write(f"\nConfiguration avec tailscale login...\n")
                log.write(f"Serveur : {HEADSCALE_URL}\n")
                log.write(f"Nom d'hôte : {hostname}\n")
            
            if not os.path.exists(tailscale_exe):
                raise Exception("tailscale.exe introuvable après l'installation")
            
            config_cmd = [
                tailscale_exe,
                "login",
                f"--login-server={HEADSCALE_URL}",
                f"--authkey={AUTH_KEY}",
                f"--hostname={hostname}",
                "--accept-routes"
            ]
            
            # Masquer la fenêtre CMD
            config_result = subprocess.run(
                config_cmd,
                capture_output=True,
                text=True,
                timeout=30,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            with open(log_file, 'a') as log:
                log.write(f"Code de retour config : {config_result.returncode}\n")
                log.write(f"STDOUT : {config_result.stdout}\n")
                log.write(f"STDERR : {config_result.stderr}\n")
            
            if config_result.returncode != 0:
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                desktop_log = os.path.join(desktop, "headscale-erreur.log")
                try:
                    shutil.copy(log_file, desktop_log)
                except:
                    pass
                raise Exception(f"Échec de la configuration : {config_result.stderr}\nLog : {desktop_log}")
            
            # Activer le mode sans surveillance
            with open(log_file, 'a') as log:
                log.write(f"\nActivation du mode sans surveillance...\n")
            
            try:
                subprocess.run(
                    [tailscale_exe, "set", "--unattended"],
                    capture_output=True,
                    timeout=10
                )
            except:
                pass
            
            # Redémarrer le service pour appliquer la config complète
            self.status_label.config(text="🔄 Finalisation de la configuration, merci de patienter...")
            self.root.update()
            
            with open(log_file, 'a') as log:
                log.write(f"\nRedémarrage du service pour appliquer la config...\n")
            
            try:
                subprocess.run(['net', 'stop', 'Tailscale'], 
                             capture_output=True, timeout=10,
                             startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(2)
                subprocess.run(['net', 'start', 'Tailscale'], 
                             capture_output=True, timeout=10,
                             startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(5)
            except:
                pass
            
            # Vérification finale
            with open(log_file, 'a') as log:
                log.write(f"\nVérification du statut final...\n")
            
            try:
                final_status = subprocess.run(
                    [tailscale_exe, "status"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                with open(log_file, 'a') as log:
                    log.write(f"Statut final :\n{final_status.stdout}\n")
            except:
                pass
            
            # Nettoyage
            try:
                os.remove(msi_path)
                if os.path.exists(log_file):
                    os.remove(log_file)
            except:
                pass
            
            # Lancer l'interface Tailscale
            tailscale_gui = r"C:\Program Files\Tailscale\tailscale-ipn.exe"
            if os.path.exists(tailscale_gui):
                try:
                    subprocess.Popen([tailscale_gui], 
                                   creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
                except:
                    pass
            
            messagebox.showinfo(
                "✅ Installation terminée",
                f"VPN Headscale installé !\n\n"
                f"📋 {client}\n"
                f"💻 {pc_type}\n"
                f"🔖 {hostname}.{BASE_DOMAIN}\n\n"
                f"✅ Démarrage automatique avec Windows."
            )
            
            self.root.destroy()
            
        except subprocess.TimeoutExpired:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if log_file and os.path.exists(log_file):
                shutil.copy(log_file, os.path.join(desktop, "headscale-timeout.log"))
            
            messagebox.showerror(
                "Erreur de délai",
                "Installation trop longue.\nLog sur le Bureau."
            )
            self.installing = False
            self.install_button.config(state=tk.NORMAL, text="⚡ Installer maintenant", bg="#2563eb")
            
        except Exception as e:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if log_file and os.path.exists(log_file):
                shutil.copy(log_file, os.path.join(desktop, "headscale-erreur.log"))
            
            messagebox.showerror(
                "Erreur d'installation",
                f"{str(e)}\n\nLog sur le Bureau."
            )
            self.installing = False
            self.install_button.config(state=tk.NORMAL, text="⚡ Installer maintenant", bg="#2563eb")

def main():
    if not is_admin():
        response = messagebox.askyesno(
            "Droits administrateur requis",
            "L'installation nécessite les droits administrateur.\n\nContinuer ?"
        )
        if response:
            run_as_admin()
        else:
            sys.exit(0)
    
    root = tk.Tk()
    root.update_idletasks()
    width = 600
    height = 550
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    app = VPNInstaller(root)
    root.mainloop()

if __name__ == "__main__":
    main()
