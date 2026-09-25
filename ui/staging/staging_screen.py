# ui/staging/staging_screen.py
import os
import customtkinter as ctk
from core.scanner import scan_license_files, scan_certificate_files
from core import session, scan_installed_directory, run_interactive_powershell

class StagingScreen(ctk.CTkFrame):
    # Mapowanie czytelnych nazw (dla instalatorów i ewentualnych poprawek)
    FRIENDLY_NAMES = {
        "server": "ArcGIS Server",
        "portal": "Portal for ArcGIS",
        "datastore": "ArcGIS Data Store",
        "webadaptor": "Web Adaptor",
        "webadaptor_server": "Web Adaptor (Server)",
        "webadaptor_portal": "Web Adaptor (Portal)",
        "desktop": "ArcGIS Desktop",
        "pro": "ArcGIS Pro",
        "arcgis_pro": "ArcGIS Pro",
        "server_installer": "Instalator ArcGIS Server",
        "portal_installer": "Instalator Portal for ArcGIS",
        "datastore_installer": "Instalator ArcGIS Data Store",
        "webadaptor_installer": "Instalator Web Adaptor",
        "desktop_installer": "Instalator ArcGIS Desktop",
        "pro_installer": "Instalator ArcGIS Pro",
        "patches": "Poprawki i Patche (.msp)",
        "patch": "Poprawka (.msp)",
    }

    # Klucze, które NIE powinny trafiać do Sekcji 1
    NON_INSTALLER_KEYS = {
        "server_license", "portal_license", 
        "server_certificate", "portal_certificate", 
        "detected_paths", "all_certificates"
    }

    def __init__(self, master, on_back, **kwargs):
        super().__init__(master, fg_color="#f8f7f4", **kwargs)
        self.on_back = on_back

        # --- Górny Pasek ---
        top_bar = ctk.CTkFrame(self, fg_color="#f8f7f4", height=50)
        top_bar.pack(fill="x", side="top")

        ctk.CTkButton(
            top_bar, text="Powrót do menu", width=140, 
            fg_color="#0057ff", hover_color="#0046D5",
            font=("Segoe UI", 12, "bold"), command=self.on_back
        ).pack(side="left", padx=15, pady=10)

        ctk.CTkLabel(
            top_bar, text="PRZYGOTOWANIE ŚRODOWISKA", 
            font=("Segoe UI", 14, "bold"), text_color="#0f172a"
        ).pack(side="left", padx=10)

        # --- Kontener Główny ---
        container = ctk.CTkFrame(self, fg_color="white", corner_radius=8, border_width=1, border_color="#cbd5e0")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            container, text="Przygotowanie zasobów i autowykrywanie ścieżek, licencji oraz certyfikatów", 
            font=("Segoe UI", 16, "bold"), text_color="#0f172a"
        ).pack(anchor="w", padx=20, pady=(20, 5))

        ctk.CTkLabel(
            container, 
            text="Możesz uruchomić skrypt PowerShell odpowiadający za stworzenie struktury i pobrania zasobów instalacyjnych," \
            "\nBądź też samodzielnie stworzyć struktury, przeskanować katalogi z instalatorami, licencjami i certyfikatami.", 
            font=("Segoe UI", 11), text_color="#475569", justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # --- Wiersz: Katalog do przeskanowania ---
        scan_dir_row = ctk.CTkFrame(container, fg_color="transparent")
        scan_dir_row.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(scan_dir_row, text="Katalog docelowy:", width=150, anchor="w", text_color="black", font=("Segoe UI", 12, "bold")).pack(side="left")
        self.ent_target_dir = ctk.CTkEntry(scan_dir_row, fg_color="white", text_color="black")
        self.ent_target_dir.pack(side="left", fill="x", expand=True)
        self.ent_target_dir.insert(0, "C:\\Install_ArcGIS")

        # --- Wiersz: Przyciski Akcji ---
        buttons_row = ctk.CTkFrame(container, fg_color="transparent")
        buttons_row.pack(anchor="center", padx=20, pady=15)

        self.btn_run_ps = ctk.CTkButton(
            buttons_row, text="Uruchom Skrypt PowerShell", 
            width=200, height=40, fg_color="#0057ff", hover_color="#0046D5",
            font=("Segoe UI", 12, "bold"), command=self.start_staging
        )
        self.btn_run_ps.pack(side="left", padx=(0, 10))

        self.btn_create_struct = ctk.CTkButton(
            buttons_row, text="Stwórz strukturę", 
            width=160, height=40, fg_color="#0057ff", hover_color="#0046D5",
            font=("Segoe UI", 12, "bold"), command=self.create_directory_structure
        )
        self.btn_create_struct.pack(side="left", padx=(0, 10))

        self.btn_scan_all = ctk.CTkButton(
            buttons_row, text="Skanuj", 
            width=160, height=40, fg_color="#0057ff", hover_color="#0046D5",
            font=("Segoe UI", 12, "bold"), command=self.scan_all
        )
        self.btn_scan_all.pack(side="left", padx=(0, 10))

        # --- Status ---
        self.lbl_status = ctk.CTkLabel(container, text="Status: Oczekiwanie na akcję", font=("Segoe UI", 14, "bold"), text_color="#64748b")
        self.lbl_status.pack(anchor="w", padx=20, pady=5)

        # --- Podgląd wyników ---
        self.txt_summary = ctk.CTkTextbox(container, height=220, state="disabled", fg_color="#f8f7f4")
        self.txt_summary.pack(fill="both", expand=True, padx=20, pady=(15, 20))
        self.txt_summary._textbox.configure(spacing3=3)
        self.txt_summary._textbox.tag_config("bold_header", font=("Segoe UI", 11, "bold"), foreground="#0f172a")

    # --- AKCJA 1: Tworzenie Struktury Katalogów ---
    def create_directory_structure(self):
        target_dir = self.ent_target_dir.get().strip()
        if not target_dir:
            self.lbl_status.configure(text="Status: Błąd - Wprowadź poprawną ścieżkę katalogu docelowego.", text_color="#dc2626")
            return

        software_dir = os.path.join(target_dir, "Software")
        others_dir = os.path.join(target_dir, "Others")

        try:
            os.makedirs(software_dir, exist_ok=True)
            os.makedirs(others_dir, exist_ok=True)
            
            self.lbl_status.configure(
                text=f"Status: Utworzono strukturę katalogów (Software, Others) w '{target_dir}'", 
                text_color="#16a34a"
            )
        except Exception as e:
            self.lbl_status.configure(text=f"Status: Błąd tworzenia katalogów: {e}", text_color="#dc2626")

    # --- AKCJA 2: Wywołanie PowerShella ---
    def start_staging(self):
        script_path = os.path.abspath("scripts/arcgis_prepare.ps1")
        
        if not os.path.exists(script_path):
            self.lbl_status.configure(text=f"Status: Błąd - Nie odnaleziono skryptu w ścieżce '{script_path}'", text_color="#dc2626")
            return

        self._clear_summary()
        self._set_buttons_state("disabled")
        self.lbl_status.configure(text="Status: Trwa wykonywanie skryptu w oknie PowerShell...", text_color="#ea580c")

        run_interactive_powershell(script_path, self.on_powershell_finished)

    def on_powershell_finished(self, success, message):
        self._set_buttons_state("normal")
        
        if success:
            self.scan_all()
            self.lbl_status.configure(text="Status: Środowisko pobrane i pomyślnie przeskanowane.", text_color="#16a34a")
        else:
            self.lbl_status.configure(text=f"Status: {message}", text_color="#dc2626")

    # --- AKCJA 3: Zunifikowane skanowanie ---
    def scan_all(self):
        self._clear_summary()
        target_dir = self.ent_target_dir.get().strip()

        if not os.path.exists(target_dir):
            self.lbl_status.configure(text=f"Status: Błąd - Podany katalog nie istnieje: '{target_dir}'", text_color="#dc2626")
            return

        self.lbl_status.configure(text=f"Status: Skanowanie zasobów w '{target_dir}'...", text_color="#0284c7")
        
        # 1. Skanowanie instalatorów (Software / katalog główny)
        software_dir = os.path.join(target_dir, "Software")
        scan_dir = software_dir if os.path.exists(software_dir) else target_dir
        
        paths = scan_installed_directory(scan_dir)
        session["detected_paths"] = paths

        # 2. Skanowanie licencji (Others)
        others_dir = os.path.join(target_dir, "Others")
        
        session["server_license"] = ""
        session["portal_license"] = ""
        session["server_certificate"] = ""
        session["portal_certificate"] = ""

        if os.path.exists(others_dir):
            licenses = scan_license_files(others_dir)
            certs = scan_certificate_files(others_dir)
            
            session["server_license"] = licenses.get("server_license", "")
            session["portal_license"] = licenses.get("portal_license", "")
            session["server_certificate"] = certs.get("server_certificate", "")
            session["portal_certificate"] = certs.get("portal_certificate", "")

        # 3. Odświeżenie widoku
        self._display_summary()
        self.lbl_status.configure(text="Status: Skanowanie zasobów zakończone.", text_color="#16a34a")

    # --- Pomocnicze metody ---
    def _clear_summary(self):
        self.txt_summary.configure(state="normal")
        self.txt_summary.delete("1.0", "end")
        self.txt_summary.configure(state="disabled")

    def _set_buttons_state(self, state):
        self.btn_create_struct.configure(state=state)
        self.btn_run_ps.configure(state=state)
        self.btn_scan_all.configure(state=state)

    def _insert_text(self, text, tag=None):
        if tag:
            self.txt_summary._textbox.insert("end", text, tag)
        else:
            self.txt_summary._textbox.insert("end", text)

    def _display_summary(self):
        self.txt_summary.configure(state="normal")
        self.txt_summary.delete("1.0", "end")

        paths = session.get("detected_paths", {}) or {}

        # --- SEKCJA: INSTALATORY I PLIKI ---
        self._insert_text("INSTALATORY I PATCHE\n", "bold_header")

        has_installers = False

        for key, val in paths.items():
            if key in self.NON_INSTALLER_KEYS:
                continue

            has_installers = True
            name = self.FRIENDLY_NAMES.get(key, key.replace("_", " ").title())
            
            if val:
                if isinstance(val, list):
                    self._insert_text(f"   [✓] {name}:\n")
                    for item in val:
                        self._insert_text(f"      └─ {item}\n")
                else:
                    self._insert_text(f"   [✓] {name}:\n      └─ {val}\n")
            else:
                self._insert_text(f"   [✗] {name}: Brak pliku\n")

        if not has_installers:
            self._insert_text("   (Brak plików instalacyjnych)\n")

        self._insert_text("\n")

        # --- SEKCJA 2: LICENCJE I CERTYFIKATY ---
        self._insert_text("LICENCJE I CERTYFIKATY\n", "bold_header")

        licenses_and_certs = [
            ("Licencja Server (.ecp)", session.get("server_license", "")),
            ("Licencja Portal (.json)", session.get("portal_license", "")),
            ("Certyfikat Server", session.get("server_certificate", "")),
            ("Certyfikat Portal", session.get("portal_certificate", "")),
        ]

        for name, val in licenses_and_certs:
            if val:
                self._insert_text(f"   [✓] {name}:\n      └─ {val}\n")
            else:
                self._insert_text(f"   [✗] {name}: Brak pliku\n")

        self.txt_summary.configure(state="disabled")