#!/usr/bin/env python3
"""
GitHub Repository Manager - Interface Sécurisée
Interface avec configuration sécurisée du token au démarrage.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
import subprocess
import requests
import math
from typing import Optional

class AnimatedLoginWindow:
    """Fenêtre de connexion animée pour saisir les credentials."""
    
    def __init__(self, parent_callback):
        self.parent_callback = parent_callback
        self.token = None
        self.username = None
        
        self.window = tk.Toplevel()
        self.setup_login_window()
        self.create_login_interface()
        
    def setup_login_window(self):
        """Configure la fenêtre de connexion."""
        self.window.title("🔐 Configuration GitHub")
        self.window.geometry("500x600")
        self.window.configure(bg="#0d1117")
        self.window.resizable(False, False)
        self.window.grab_set()  # Modal
        
        # Centrer la fenêtre
        self.window.transient()
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"500x600+{x}+{y}")
        
    def create_login_interface(self):
        """Crée l'interface de connexion."""
        main_frame = tk.Frame(self.window, bg="#0d1117")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Header animé
        self.create_animated_header(main_frame)
        
        # Formulaire de connexion
        self.create_login_form(main_frame)
        
        # Instructions
        self.create_instructions(main_frame)
        
        # Boutons
        self.create_login_buttons(main_frame)
        
        # Animation d'entrée
        self.animate_entrance()
        
        # Focus sur le premier champ
        self.username_entry.focus_set()
        
        # Bind Enter pour valider
        self.window.bind('<Return>', lambda e: self.validate_credentials())
        
        # État initial du bouton
        self.connect_btn.configure(state="normal", bg="#656d76")
        
    def create_animated_header(self, parent):
        """Crée le header avec animations."""
        header_frame = tk.Frame(parent, bg="#0d1117")
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Logo GitHub animé
        self.logo_canvas = tk.Canvas(header_frame, width=80, height=80, 
                                   bg="#0d1117", highlightthickness=0)
        self.logo_canvas.pack()
        
        # Titre
        title = tk.Label(header_frame, text="Configuration GitHub", 
                        bg="#0d1117", fg="#f0f6fc", 
                        font=("Segoe UI", 20, "bold"))
        title.pack(pady=(10, 5))
        
        subtitle = tk.Label(header_frame, text="Connexion sécurisée à votre compte", 
                          bg="#0d1117", fg="#7d8590", 
                          font=("Segoe UI", 11))
        subtitle.pack()
        
        # Animation du logo
        self.animate_github_logo()
        
    def animate_github_logo(self):
        """Anime le logo GitHub."""
        def draw_logo():
            self.logo_canvas.delete("all")
            
            # Cercle principal avec pulsation
            radius = 30 + 5 * math.sin(time.time() * 2)
            
            # Fond du logo
            self.logo_canvas.create_oval(40-radius, 40-radius, 40+radius, 40+radius,
                                       fill="#21262d", outline="#30363d", width=2)
            
            # Icône GitHub stylisée
            self.logo_canvas.create_text(40, 40, text="⚡", fill="#58a6ff", 
                                       font=("Segoe UI", int(radius), "bold"))
            
        draw_logo()
        self.window.after(100, self.animate_github_logo)
        
    def create_login_form(self, parent):
        """Crée le formulaire de connexion."""
        form_frame = tk.Frame(parent, bg="#21262d", relief="flat")
        form_frame.pack(fill=tk.X, pady=(0, 20), ipady=30, ipadx=30)
        
        # Nom d'utilisateur
        tk.Label(form_frame, text="👤 Nom d'utilisateur GitHub", 
                bg="#21262d", fg="#f0f6fc", 
                font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=(0, 8))
        
        self.username_entry = tk.Entry(form_frame, bg="#0d1117", fg="#f0f6fc", 
                                     font=("Segoe UI", 12), relief="flat", 
                                     bd=0, highlightthickness=2, 
                                     highlightcolor="#58a6ff")
        self.username_entry.pack(fill=tk.X, ipady=12, pady=(0, 20))
        
        # Token GitHub
        tk.Label(form_frame, text="🔑 Token GitHub (Personal Access Token)", 
                bg="#21262d", fg="#f0f6fc", 
                font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=(0, 8))
        
        self.token_entry = tk.Entry(form_frame, bg="#0d1117", fg="#f0f6fc", 
                                  font=("Consolas", 11), relief="flat", 
                                  bd=0, show="*", highlightthickness=2, 
                                  highlightcolor="#58a6ff")
        self.token_entry.pack(fill=tk.X, ipady=12, pady=(0, 10))
        
        # Bind pour validation en temps réel
        self.token_entry.bind('<KeyRelease>', self.validate_token_format)
        self.username_entry.bind('<KeyRelease>', self.validate_form)
        
        # Bouton pour afficher/masquer le token
        show_frame = tk.Frame(form_frame, bg="#21262d")
        show_frame.pack(fill=tk.X)
        
        self.show_token = tk.BooleanVar()
        show_check = tk.Checkbutton(show_frame, text="👁️ Afficher le token", 
                                  variable=self.show_token, 
                                  command=self.toggle_token_visibility,
                                  bg="#21262d", fg="#7d8590", 
                                  selectcolor="#21262d", 
                                  font=("Segoe UI", 10))
        show_check.pack(anchor=tk.W)
        
    def toggle_token_visibility(self):
        """Bascule la visibilité du token."""
        if self.show_token.get():
            self.token_entry.configure(show="")
        else:
            self.token_entry.configure(show="*")
            
    def validate_token_format(self, event=None):
        """Valide le format du token en temps réel."""
        token = self.token_entry.get()
        
        if not token:
            self.token_entry.configure(highlightcolor="#58a6ff")
        elif token.startswith('ghp_') and len(token) >= 20:
            self.token_entry.configure(highlightcolor="#238636")  # Vert
        else:
            self.token_entry.configure(highlightcolor="#f85149")  # Rouge
            
        self.validate_form()
        
    def validate_form(self, event=None):
        """Valide le formulaire et active/désactive le bouton."""
        username = self.username_entry.get().strip()
        token = self.token_entry.get().strip()
        
        # Validation username
        if username:
            self.username_entry.configure(highlightcolor="#238636")
        else:
            self.username_entry.configure(highlightcolor="#58a6ff")
        
        # Activer/désactiver le bouton
        if username and token and token.startswith('ghp_') and len(token) >= 20:
            self.connect_btn.configure(state="normal", bg="#238636")
        else:
            self.connect_btn.configure(state="normal", bg="#656d76")  # Grisé
            
    def create_instructions(self, parent):
        """Crée les instructions."""
        info_frame = tk.Frame(parent, bg="#161b22", relief="flat")
        info_frame.pack(fill=tk.X, pady=(0, 20), ipady=20, ipadx=20)
        
        tk.Label(info_frame, text="ℹ️ Comment obtenir votre token:", 
                bg="#161b22", fg="#58a6ff", 
                font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        instructions = [
            "1. Allez sur GitHub.com → Settings → Developer settings",
            "2. Cliquez sur Personal access tokens → Tokens (classic)",
            "3. Generate new token → Generate new token (classic)",
            "4. Cochez la permission 'repo' (obligatoire)",
            "5. Copiez le token qui commence par 'ghp_'"
        ]
        
        for instruction in instructions:
            tk.Label(info_frame, text=instruction, 
                    bg="#161b22", fg="#7d8590", 
                    font=("Segoe UI", 10)).pack(anchor=tk.W, pady=2)
            
    def create_login_buttons(self, parent):
        """Crée les boutons de connexion."""
        button_frame = tk.Frame(parent, bg="#0d1117")
        button_frame.pack(fill=tk.X, pady=30)
        
        # Container pour centrer les boutons
        buttons_container = tk.Frame(button_frame, bg="#0d1117")
        buttons_container.pack(expand=True)
        
        # Bouton de connexion principal
        self.connect_btn = tk.Button(buttons_container, text="🚀 SE CONNECTER", 
                                   command=self.validate_credentials,
                                   bg="#238636", fg="white", 
                                   font=("Segoe UI", 14, "bold"),
                                   relief="flat", bd=0, padx=40, pady=15,
                                   cursor="hand2", width=20)
        self.connect_btn.pack(pady=(0, 15))
        
        # Frame pour les boutons secondaires
        secondary_frame = tk.Frame(buttons_container, bg="#0d1117")
        secondary_frame.pack()
        
        # Bouton d'aide
        help_btn = tk.Button(secondary_frame, text="❓ Aide", 
                           command=self.show_help,
                           bg="#21262d", fg="#f0f6fc", 
                           font=("Segoe UI", 11, "bold"),
                           relief="flat", bd=0, padx=20, pady=10,
                           cursor="hand2")
        help_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton quitter
        quit_btn = tk.Button(secondary_frame, text="❌ Quitter", 
                           command=self.window.quit,
                           bg="#da3633", fg="white", 
                           font=("Segoe UI", 11, "bold"),
                           relief="flat", bd=0, padx=20, pady=10,
                           cursor="hand2")
        quit_btn.pack(side=tk.LEFT)
        
    def animate_entrance(self):
        """Animation d'entrée de la fenêtre."""
        self.window.attributes('-alpha', 0)
        
        def fade_in():
            alpha = self.window.attributes('-alpha')
            if alpha < 1:
                self.window.attributes('-alpha', alpha + 0.1)
                self.window.after(50, fade_in)
                
        fade_in()
        
    def validate_credentials(self):
        """Valide les credentials avec animation."""
        username = self.username_entry.get().strip()
        token = self.token_entry.get().strip()
        
        # Validation des champs
        if not username:
            messagebox.showerror("Champ requis", "Veuillez saisir votre nom d'utilisateur GitHub.")
            self.username_entry.focus_set()
            return
            
        if not token:
            messagebox.showerror("Champ requis", "Veuillez saisir votre token GitHub.")
            self.token_entry.focus_set()
            return
            
        if not token.startswith('ghp_'):
            messagebox.showerror("Format invalide", 
                               "Le token GitHub doit commencer par 'ghp_'\n\n"
                               "Exemple: ghp_1234567890abcdef...")
            self.token_entry.focus_set()
            return
            
        if len(token) < 20:
            messagebox.showerror("Token invalide", 
                               "Le token semble trop court.\n\n"
                               "Vérifiez que vous avez copié le token complet.")
            self.token_entry.focus_set()
            return
            
        # Animation de validation
        self.animate_validation(username, token)
        
    def animate_validation(self, username, token):
        """Anime la validation des credentials."""
        # Désactiver le bouton
        self.connect_btn.configure(state="disabled", text="🔄 Validation...")
        
        def validate():
            try:
                # Test de l'API GitHub
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                response = requests.get("https://api.github.com/user", 
                                      headers=headers, timeout=10)
                
                if response.status_code == 200:
                    user_data = response.json()
                    actual_username = user_data.get('login')
                    
                    # Animation de succès
                    self.window.after(0, lambda: self.success_animation(username, token, actual_username))
                else:
                    self.window.after(0, lambda: self.error_animation("Token invalide ou expiré"))
                    
            except Exception as e:
                self.window.after(0, lambda: self.error_animation(f"Erreur de connexion: {str(e)}"))
                
        threading.Thread(target=validate, daemon=True).start()
        
    def success_animation(self, username, token, actual_username):
        """Animation de succès."""
        self.connect_btn.configure(text="✅ Connexion réussie!", bg="#238636")
        
        # Effet de flash vert
        original_bg = self.window.cget('bg')
        
        def flash():
            colors = ["#0d1117", "#1a472a", "#0d1117"]
            for color in colors:
                self.window.configure(bg=color)
                self.window.update()
                time.sleep(0.2)
                
        threading.Thread(target=flash, daemon=True).start()
        
        # Sauvegarder les credentials et fermer
        self.token = token
        self.username = actual_username  # Utiliser le vrai nom d'utilisateur
        
        self.window.after(1000, self.close_with_success)
        
    def error_animation(self, error_msg):
        """Animation d'erreur."""
        self.connect_btn.configure(state="normal", text="🚀 Se Connecter", bg="#238636")
        
        # Effet de flash rouge
        def flash():
            colors = ["#0d1117", "#4a1a1a", "#0d1117"]
            for color in colors:
                self.window.configure(bg=color)
                self.window.update()
                time.sleep(0.2)
                
        threading.Thread(target=flash, daemon=True).start()
        
        messagebox.showerror("Erreur de connexion", error_msg)
        
    def close_with_success(self):
        """Ferme la fenêtre avec succès."""
        self.window.grab_release()
        self.window.destroy()
        self.parent_callback(self.username, self.token)
        
    def show_help(self):
        """Affiche l'aide."""
        help_text = """
🔗 Liens utiles:

• GitHub Personal Access Tokens:
  https://github.com/settings/tokens

• Documentation GitHub API:
  https://docs.github.com/en/rest

• Guide de création de token:
  https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

⚠️ Sécurité:
• Ne partagez jamais votre token
• Utilisez des permissions minimales
• Renouvelez régulièrement vos tokens
        """
        
        messagebox.showinfo("Aide - Configuration GitHub", help_text)

class GitHubManagerSecureGUI:
    """Interface principale avec authentification sécurisée."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.github_token = None
        self.github_username = None
        
        self.setup_window()
        self.show_login()
        
    def setup_window(self):
        """Configure la fenêtre principale."""
        self.root.title("🚀 GitHub Repository Manager Pro")
        self.root.geometry("800x900")
        self.root.configure(bg="#0d1117")
        self.root.withdraw()  # Masquer jusqu'à la connexion
        
    def show_login(self):
        """Affiche la fenêtre de connexion."""
        login_window = AnimatedLoginWindow(self.on_login_success)
        
    def on_login_success(self, username, token):
        """Callback appelé après connexion réussie."""
        self.github_username = username
        self.github_token = token
        
        # Afficher la fenêtre principale
        self.root.deiconify()
        self.create_main_interface()
        
        # Message de bienvenue
        messagebox.showinfo("Bienvenue!", 
                          f"Connexion réussie!\n\n"
                          f"Utilisateur: {username}\n"
                          f"Vous pouvez maintenant créer vos dépôts en toute sécurité.")\
        
    def create_main_interface(self):
        """Crée l'interface principale."""
        # Canvas avec scrollbar pour l'interface principale
        canvas = tk.Canvas(self.root, bg="#0d1117", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        
        # Frame scrollable
        main_container = tk.Frame(canvas, bg="#0d1117")
        
        # Configuration du scroll
        main_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=main_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas et scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=30, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Header avec info utilisateur
        self.create_user_header(main_container)
        
        # Formulaire de création
        self.create_repo_form(main_container)
        
        # Zone de progression
        self.create_progress_section(main_container)
        
        # Zone de logs
        self.create_log_section(main_container)
        
        # Boutons d'action - IMPORTANT: doit être en dernier
        self.create_action_buttons(main_container)
        
        # S'assurer que tout est visible et configurer la zone de scroll
        main_container.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Centrer le contenu horizontalement
        def center_content(event=None):
            canvas_width = canvas.winfo_width()
            frame_width = main_container.winfo_reqwidth()
            if canvas_width > frame_width:
                x_offset = (canvas_width - frame_width) // 2
                canvas.coords(canvas.find_all()[0], x_offset, 0)
        
        canvas.bind('<Configure>', center_content)
        self.root.after(100, center_content)
        
    def create_user_header(self, parent):
        """Crée le header avec info utilisateur."""
        header_frame = tk.Frame(parent, bg="#21262d", relief="flat")
        header_frame.pack(fill=tk.X, pady=(0, 20), ipady=20, ipadx=20)
        
        # Info utilisateur
        user_frame = tk.Frame(header_frame, bg="#21262d")
        user_frame.pack(fill=tk.X)
        
        tk.Label(user_frame, text="🚀 GitHub Repository Manager Pro", 
                bg="#21262d", fg="#58a6ff", 
                font=("Segoe UI", 18, "bold")).pack(anchor=tk.W)
        
        tk.Label(user_frame, text=f"👤 Connecté en tant que: {self.github_username}", 
                bg="#21262d", fg="#7d8590", 
                font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(5, 0))
        
        # Bouton de déconnexion
        logout_btn = tk.Button(user_frame, text="🚪 Déconnexion", 
                             command=self.logout,
                             bg="#da3633", fg="white", 
                             font=("Segoe UI", 10, "bold"),
                             relief="flat", bd=0, padx=15, pady=5)
        logout_btn.pack(anchor=tk.E, pady=(10, 0))
        
    def create_repo_form(self, parent):
        """Crée le formulaire de création de dépôt."""
        form_frame = tk.Frame(parent, bg="#21262d", relief="flat")
        form_frame.pack(fill=tk.X, pady=(0, 20), ipady=20, ipadx=20)
        
        tk.Label(form_frame, text="📝 Nouveau Dépôt", 
                bg="#21262d", fg="#f0f6fc", 
                font=("Segoe UI", 16, "bold")).pack(anchor=tk.W, pady=(0, 20))
        
        # Nom du dépôt
        tk.Label(form_frame, text="📁 Nom du dépôt:", 
                bg="#21262d", fg="#f0f6fc", 
                font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.repo_name = tk.Entry(form_frame, bg="#0d1117", fg="#f0f6fc", 
                                font=("Segoe UI", 12), relief="flat", 
                                bd=0, highlightthickness=2, 
                                highlightcolor="#58a6ff")
        self.repo_name.pack(fill=tk.X, ipady=10, pady=(0, 15))
        
        # Description
        tk.Label(form_frame, text="📄 Description:", 
                bg="#21262d", fg="#f0f6fc", 
                font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.description = tk.Entry(form_frame, bg="#0d1117", fg="#f0f6fc", 
                                  font=("Segoe UI", 12), relief="flat", 
                                  bd=0, highlightthickness=2, 
                                  highlightcolor="#58a6ff")
        self.description.pack(fill=tk.X, ipady=10, pady=(0, 15))
        
        # Destination
        tk.Label(form_frame, text="📂 Destination:", 
                bg="#21262d", fg="#f0f6fc", 
                font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        dest_frame = tk.Frame(form_frame, bg="#21262d")
        dest_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.destination = tk.Entry(dest_frame, bg="#0d1117", fg="#f0f6fc", 
                                  font=("Segoe UI", 12), relief="flat", 
                                  bd=0, highlightthickness=2, 
                                  highlightcolor="#58a6ff")
        self.destination.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10)
        self.destination.insert(0, os.getcwd())
        
        browse_btn = tk.Button(dest_frame, text="📂", 
                             command=self.browse_destination,
                             bg="#58a6ff", fg="white", 
                             font=("Segoe UI", 12, "bold"),
                             relief="flat", bd=0, padx=15, pady=10)
        browse_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Options
        options_frame = tk.Frame(form_frame, bg="#21262d")
        options_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.is_public = tk.BooleanVar()
        public_check = tk.Checkbutton(options_frame, text="🌐 Dépôt public", 
                                    variable=self.is_public,
                                    bg="#21262d", fg="#f0f6fc", 
                                    selectcolor="#21262d", 
                                    font=("Segoe UI", 11))
        public_check.pack(anchor=tk.W)
        
        self.is_local_push = tk.BooleanVar()
        local_check = tk.Checkbutton(options_frame, text="📤 Pousser un projet local vers GitHub", 
                                   variable=self.is_local_push,
                                   command=self.toggle_local_mode,
                                   bg="#21262d", fg="#f0f6fc", 
                                   selectcolor="#21262d", 
                                   font=("Segoe UI", 11))
        local_check.pack(anchor=tk.W, pady=(5, 0))
        
    def create_progress_section(self, parent):
        """Crée la section de progression."""
        progress_frame = tk.Frame(parent, bg="#21262d", relief="flat")
        progress_frame.pack(fill=tk.X, pady=(0, 20), ipady=20, ipadx=20)
        
        tk.Label(progress_frame, text="📊 Progression", 
                bg="#21262d", fg="#f0f6fc", 
                font=("Segoe UI", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Barre de progression
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', 
                                      length=400, style='TProgressbar')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Statut
        self.status_label = tk.Label(progress_frame, text="⏳ Prêt à commencer", 
                                   bg="#21262d", fg="#7d8590", 
                                   font=("Segoe UI", 11))
        self.status_label.pack(anchor=tk.W)
        
    def create_log_section(self, parent):
        """Crée la section de logs."""
        log_frame = tk.Frame(parent, bg="#21262d", relief="flat")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20), ipady=20, ipadx=20)
        
        tk.Label(log_frame, text="📋 Journal d'activité", 
                bg="#21262d", fg="#f0f6fc", 
                font=("Segoe UI", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Zone de texte avec scrollbar
        text_frame = tk.Frame(log_frame, bg="#21262d")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(text_frame, bg="#0d1117", fg="#f0f6fc", 
                              font=('Consolas', 10), wrap=tk.WORD, height=8,
                              relief="flat", bd=0)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                                command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_action_buttons(self, parent):
        """Crée les boutons d'action."""
        # Cadre pour les boutons avec fond visible
        button_container = tk.Frame(parent, bg="#21262d", relief="flat")
        button_container.pack(fill=tk.X, pady=20, ipady=25, ipadx=20)
        
        # Titre de la section
        tk.Label(button_container, text="⚙️ Actions", 
                bg="#21262d", fg="#f0f6fc", 
                font=("Segoe UI", 14, "bold")).pack(anchor=tk.W, pady=(0, 15))
        
        # Frame pour centrer les boutons
        button_frame = tk.Frame(button_container, bg="#21262d")
        button_frame.pack(expand=True)
        
        # Bouton principal - CREER ET CLONER
        self.create_btn = tk.Button(button_frame, text="🚀 CRÉER ET CLONER LE DÉPÔT", 
                                  command=self.start_creation,
                                  bg="#238636", fg="white", 
                                  font=("Segoe UI", 16, "bold"),
                                  relief="flat", bd=0, padx=40, pady=20,
                                  cursor="hand2", width=25)
        self.create_btn.pack(pady=(0, 15))
        
        # Frame pour les boutons secondaires
        secondary_frame = tk.Frame(button_frame, bg="#21262d")
        secondary_frame.pack()
        
        # Bouton effacer
        clear_btn = tk.Button(secondary_frame, text="🗑️ Effacer le formulaire", 
                            command=self.clear_form,
                            bg="#da3633", fg="white", 
                            font=("Segoe UI", 12, "bold"),
                            relief="flat", bd=0, padx=25, pady=12,
                            cursor="hand2")
        clear_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Bouton test connexion
        test_btn = tk.Button(secondary_frame, text="🔍 Tester la connexion", 
                           command=self.test_connection,
                           bg="#58a6ff", fg="white", 
                           font=("Segoe UI", 12, "bold"),
                           relief="flat", bd=0, padx=25, pady=12,
                           cursor="hand2")
        test_btn.pack(side=tk.LEFT)
        
    def toggle_local_mode(self):
        """Bascule entre mode création et mode push local."""
        if self.is_local_push.get():
            self.create_btn.configure(text="📤 CRÉER ET POUSSER LE DÉPÔT LOCAL")
        else:
            self.create_btn.configure(text="🚀 CRÉER ET CLONER LE DÉPÔT")
    
    def browse_destination(self):
        """Ouvre le sélecteur de dossier."""
        if self.is_local_push.get():
            folder = filedialog.askdirectory(initialdir=self.destination.get(), 
                                           title="Sélectionner le dossier du projet local")
            if folder:
                self.destination.delete(0, tk.END)
                self.destination.insert(0, folder)
                # Informer l'utilisateur si ce n'est pas encore un dépôt Git
                if not os.path.exists(os.path.join(folder, ".git")):
                    self.log_message(f"📁 Dossier sélectionné: {folder} (sera initialisé comme dépôt Git)")
                else:
                    self.log_message(f"📁 Dépôt Git existant sélectionné: {folder}")
        else:
            folder = filedialog.askdirectory(initialdir=self.destination.get())
            if folder:
                self.destination.delete(0, tk.END)
                self.destination.insert(0, folder)
            
    def log_message(self, message):
        """Ajoute un message au log."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\\n")
        self.log_text.see(tk.END)
        
    def start_creation(self):
        """Démarre la création du dépôt."""
        repo_name = self.repo_name.get().strip()
        
        if not repo_name:
            messagebox.showerror("Erreur", "Veuillez saisir un nom de dépôt.")
            return
            
        self.create_btn.configure(state="disabled")
        thread = threading.Thread(target=self.creation_process, daemon=True)
        thread.start()
        
    def creation_process(self):
        """Processus de création du dépôt."""
        try:
            repo_name = self.repo_name.get().strip()
            description = self.description.get().strip()
            destination = self.destination.get().strip()
            is_public = self.is_public.get()
            is_local = self.is_local_push.get()
            
            # Étape 1: Création du dépôt GitHub
            self.root.after(0, lambda: self.status_label.configure(text="🔄 Création du dépôt..."))
            self.root.after(0, lambda: self.progress.configure(value=20))
            self.root.after(0, lambda: self.log_message(f"Création du dépôt '{repo_name}'"))
            
            clone_url = self.create_github_repo(repo_name, not is_public, description)
            
            if not clone_url:
                self.root.after(0, lambda: self.status_label.configure(text="❌ Échec de la création"))
                return
                
            self.root.after(0, lambda: self.progress.configure(value=50))
            
            if is_local:
                # Mode push local
                self.root.after(0, lambda: self.status_label.configure(text="📤 Push du dépôt local..."))
                self.root.after(0, lambda: self.log_message("Début du push du dépôt local"))
                success = self.push_local_repo(destination, clone_url)
            else:
                # Mode clonage normal
                self.root.after(0, lambda: self.status_label.configure(text="📥 Clonage..."))
                self.root.after(0, lambda: self.log_message("Début du clonage"))
                success = self.clone_repository(clone_url, destination)
            
            if success:
                self.root.after(0, lambda: self.progress.configure(value=100))
                self.root.after(0, lambda: self.status_label.configure(text="✅ Terminé!"))
                action = "poussé" if is_local else "cloné"
                self.root.after(0, lambda: self.log_message(f"🎉 Dépôt {action} avec succès!"))
                self.root.after(0, lambda: messagebox.showinfo("Succès", f"Dépôt '{repo_name}' créé et {action}!"))
            else:
                self.root.after(0, lambda: self.status_label.configure(text="⚠️ Partiellement réussi"))
                
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Erreur: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.create_btn.configure(state="normal"))
            
    def create_github_repo(self, repo_name, private, description):
        """Crée un dépôt GitHub."""
        url = "https://api.github.com/user/repos"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "name": repo_name,
            "private": private,
            "description": description
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 201:
                repo_data = response.json()
                self.root.after(0, lambda: self.log_message(f"✅ Dépôt créé: {repo_data['html_url']}"))
                return repo_data["clone_url"]
            else:
                error_msg = response.json().get('message', 'Erreur inconnue')
                self.root.after(0, lambda: self.log_message(f"❌ Erreur: {error_msg}"))
                
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Erreur de connexion: {e}"))
        
        return None
        
    def clone_repository(self, clone_url, destination):
        """Clone le dépôt."""
        try:
            result = subprocess.run(
                ["git", "clone", clone_url],
                cwd=destination,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.root.after(0, lambda: self.log_message("✅ Clonage réussi"))
                return True
            else:
                self.root.after(0, lambda: self.log_message(f"❌ Erreur clonage: {result.stderr}"))
                return False
                
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Erreur clonage: {e}"))
        
        return False
        
    def push_local_repo(self, local_path, remote_url):
        """Pousse un dépôt local vers GitHub (initialise si nécessaire)."""
        try:
            # Vérifier si c'est déjà un dépôt Git, sinon l'initialiser
            if not os.path.exists(os.path.join(local_path, ".git")):
                self.root.after(0, lambda: self.log_message("🌱 Initialisation du dépôt Git..."))
                result = subprocess.run(["git", "init"], cwd=local_path, capture_output=True, timeout=30)
                if result.returncode != 0:
                    self.root.after(0, lambda: self.log_message("❌ Échec de l'initialisation Git"))
                    return False
            
            # Configurer la branche principale
            self.root.after(0, lambda: self.log_message("🌿 Configuration de la branche principale..."))
            subprocess.run(["git", "branch", "-M", "main"], cwd=local_path, capture_output=True, timeout=30)
            
            # Ajouter tous les fichiers
            self.root.after(0, lambda: self.log_message("📁 Ajout des fichiers..."))
            subprocess.run(["git", "add", "."], cwd=local_path, capture_output=True, timeout=30)
            
            # Vérifier s'il y a des changements à commiter
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  cwd=local_path, capture_output=True, text=True, timeout=30)
            
            if result.stdout.strip():
                self.root.after(0, lambda: self.log_message("💾 Commit initial..."))
                commit_result = subprocess.run(["git", "commit", "-m", "Initial commit from GitHub Manager"], 
                                             cwd=local_path, capture_output=True, timeout=30)
                if commit_result.returncode != 0:
                    self.root.after(0, lambda: self.log_message("❌ Échec du commit"))
                    return False
            else:
                # Vérifier s'il y a déjà des commits
                result = subprocess.run(["git", "log", "--oneline"], 
                                      cwd=local_path, capture_output=True, text=True, timeout=30)
                if not result.stdout.strip():
                    self.root.after(0, lambda: self.log_message("⚠️ Aucun fichier à commiter"))
                    return False
            
            # Ajouter le remote origin (supprimer s'il existe déjà)
            self.root.after(0, lambda: self.log_message("🔗 Configuration du remote..."))
            subprocess.run(["git", "remote", "remove", "origin"], 
                         cwd=local_path, capture_output=True, timeout=30)  # Ignore errors
            
            result = subprocess.run(["git", "remote", "add", "origin", remote_url], 
                                  cwd=local_path, capture_output=True, timeout=30)
            if result.returncode != 0:
                self.root.after(0, lambda: self.log_message("❌ Échec de la configuration du remote"))
                return False
            
            # Push vers GitHub
            self.root.after(0, lambda: self.log_message("🚀 Push vers GitHub..."))
            result = subprocess.run(["git", "push", "-u", "origin", "main"], 
                                  cwd=local_path, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.root.after(0, lambda: self.log_message("✅ Push réussi vers GitHub!"))
                return True
            else:
                error_msg = result.stderr.strip() if result.stderr else "Erreur inconnue"
                self.root.after(0, lambda: self.log_message(f"❌ Erreur push: {error_msg}"))
                return False
                
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self.log_message("❌ Timeout lors de l'opération Git"))
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Erreur: {str(e)}"))
        
        return False
        
    def clear_form(self):
        """Efface le formulaire."""
        self.repo_name.delete(0, tk.END)
        self.description.delete(0, tk.END)
        self.is_public.set(False)
        self.is_local_push.set(False)
        self.toggle_local_mode()
        self.progress.configure(value=0)
        self.status_label.configure(text="⏳ Prêt à commencer")
        self.log_text.delete(1.0, tk.END)
        
    def test_connection(self):
        """Teste la connexion GitHub."""
        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                messagebox.showinfo("Test de connexion", 
                                  f"Connexion réussie!\n\n"
                                  f"Utilisateur: {user_data.get('login')}\n"
                                  f"Dépôts publics: {user_data.get('public_repos', 0)}\n"
                                  f"Dépôts privés: {user_data.get('total_private_repos', 0)}")
            else:
                messagebox.showerror("Test de connexion", "Erreur de connexion à l'API GitHub")
                
        except Exception as e:
            messagebox.showerror("Test de connexion", f"Erreur: {str(e)}")
    
    def logout(self):
        """Déconnexion."""
        if messagebox.askyesno("Déconnexion", "Voulez-vous vraiment vous déconnecter?"):
            self.root.quit()
            
    def run(self):
        """Lance l'application."""
        self.root.mainloop()

def main():
    """Point d'entrée principal."""
    app = GitHubManagerSecureGUI()
    app.run()

if __name__ == "__main__":
    main()