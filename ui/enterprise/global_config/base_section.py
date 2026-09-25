# global_config/base_section.py
import customtkinter as ctk
from config import VERSIONS, SERVER_ROLE_OPTIONS

class BaseSectionFrame(ctk.CTkFrame):
    def __init__(self, master, help_img=None, on_ha_change=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.help_img = help_img
        self.on_ha_change = on_ha_change
        self.vars = {}

        self.pack(fill="x", padx=10, pady=5)
        self._build_ui()

    def _build_ui(self):
        label_frame = ctk.CTkFrame(
            self, 
            fg_color="#f8f9fa",
            border_color="#dee2e6",
            border_width=1,
            corner_radius=6
        )
        label_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            label_frame, 
            text="Podstawowa konfiguracja", 
            font=("Segoe UI", 15, "bold"), 
            text_color="#000000",
            fg_color="#f8f7f4",
            corner_radius=8
        ).pack(fill="x", anchor="w")

        # Kontener na wszystkie elementy Sekcji 1
        self.config_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.config_frame.pack(fill="x")

        self._add_dropdown(self.config_frame, "Version", "Wersja", VERSIONS, "10.9.1")
        self._add_checkbox(self.config_frame, "IsHA", "Odblokować architekturę HA?", default=False, command=self._handle_ha_toggle)

        # Pola warunkowe umieszczane wewnątrz self.config_frame
        self.portal_ctx_row = self._create_conditional_field(self.config_frame, "PortalContext", "Kontekst portalu", "portal")
        self.server_ctx_row = self._create_conditional_field(self.config_frame, "ServerContext", "Kontekst serwera", "arcgis")
        self.server_role_row = self._create_conditional_dropdown(self.config_frame, "ServerRole", "Rola serwera", SERVER_ROLE_OPTIONS, "GeneralPurposeServer")

        # --- SEKCJA 2: Poświadczenia ---
        self.credentials_section = ctk.CTkFrame(self, fg_color="transparent")
        self.credentials_section.pack(fill="x")

        ctk.CTkLabel(
            self.credentials_section, 
            text="Poświadczenia", 
            font=("Segoe UI", 15, "bold"), 
            fg_color="#f8f7f4"
        ).pack(fill="x", anchor="w", padx=10, pady=(20, 5))

        self.credentials_frame = ctk.CTkFrame(self.credentials_section, fg_color="transparent")
        self.credentials_frame.pack(fill="x")
        
        self._add_field(self.credentials_frame, "Service Account", "Konto techniczne", "DOMAIN\\USER")
        self._add_field(self.credentials_frame, "Service Account Password", "Hasło konta technicznego", "", is_pass=True)
        self._add_field(self.credentials_frame, "ADService Account", "Konto techniczne AD", "DOMAIN\\USER")
        self._add_field(self.credentials_frame, "ADService Account Password", "Hasło konta technicznego AD", "", is_pass=True)

    def _handle_ha_toggle(self):
        if self.on_ha_change:
            self.on_ha_change(self.vars["IsHA"].get())

    def _add_field(self, parent, var_key, label_text, default, is_pass=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(row, text=label_text, width=220, anchor="w", text_color="black").pack(side="left")
        v = ctk.StringVar(value=default)
        self.vars[var_key] = v
        ctk.CTkEntry(row, textvariable=v, fg_color="white", text_color="black", show="*" if is_pass else "").pack(side="left", fill="x", expand=True)
        return row

    def _add_dropdown(self, parent, var_key, label_text, options, default):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(row, text=label_text, width=220, anchor="w", text_color="black").pack(side="left")
        v = ctk.StringVar(value=default)
        self.vars[var_key] = v
        ctk.CTkComboBox(row, values=options, variable=v, fg_color="white", text_color="black", state="readonly").pack(side="left", fill="x", expand=True)
        return row

    def _add_checkbox(self, parent, var_key, label_text, default=False, command=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(row, text=label_text, width=220, anchor="w", text_color="black").pack(side="left")
        v = ctk.BooleanVar(value=default)
        self.vars[var_key] = v
        cb = ctk.CTkCheckBox(row, text="", variable=v, width=20, command=command)
        cb.pack(side="left")
        return row

    def _create_conditional_field(self, parent, var_key, label_text, default):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(row, text=label_text, width=220, anchor="w", text_color="black").pack(side="left")
        v = ctk.StringVar(value=default)
        self.vars[var_key] = v
        ctk.CTkEntry(row, textvariable=v, fg_color="white", text_color="black").pack(side="left", fill="x", expand=True)
        return row

    def _create_conditional_dropdown(self, parent, var_key, label_text, options, default):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(row, text=label_text, width=220, anchor="w", text_color="black").pack(side="left")
        v = ctk.StringVar(value=default)
        self.vars[var_key] = v
        ctk.CTkComboBox(row, values=options, variable=v, fg_color="white", text_color="black", state="readonly").pack(side="left", fill="x", expand=True)
        return row

    def _add_hr(self):
        line = ctk.CTkFrame(self, height=2, fg_color="#e2e8f0", border_width=0)
        line.pack(fill="x", padx=20, pady=15)

    def is_ha_enabled(self):
        return self.vars["IsHA"].get()

    def update_visibility(self, active_roles):
        if active_roles == {"WebAdaptor"}:
            self.credentials_section.pack_forget()
        else:
            self.credentials_section.pack(fill="x")

        if "Portal" in active_roles:
            self.portal_ctx_row.pack(fill="x", padx=20, pady=2)
        else:
            self.portal_ctx_row.pack_forget()

        if "Server" in active_roles:
            self.server_ctx_row.pack(fill="x", padx=20, pady=2)
            self.server_role_row.pack(fill="x", padx=20, pady=2)
        else:
            self.server_ctx_row.pack_forget()
            self.server_role_row.pack_forget()

    def populate_data(self, data, active_roles):
        v = {k: var.get() for k, var in self.vars.items()}
        data["Version"] = v["Version"]
        data["DownloadSetups"] = False

        if active_roles != {"WebAdaptor"}:
            data["Credentials"] = {
                "ServiceAccount": {
                    "UserName": v["Service Account"], 
                    "Password": v["Service Account Password"], 
                    "IsDomainAccount": True, 
                    "IsMSAAccount": False
                },
                "ADServiceUser": {
                    "UserName": v["ADService Account"], 
                    "Password": v["ADService Account Password"]
                }
            }

        if "Portal" in active_roles:
            data["PortalContext"] = v["PortalContext"]
            
        if "Server" in active_roles:
            data["ServerContext"] = v["ServerContext"]
            data["ServerRole"] = v["ServerRole"]