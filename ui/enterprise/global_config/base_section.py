import customtkinter as ctk
from config import VERSIONS, SERVER_ROLE_OPTIONS
from ui.components.form_fields import FormFieldMixin


class BaseSectionFrame(FormFieldMixin, ctk.CTkFrame):
    def __init__(self, master, help_img=None, on_ha_change=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.help_img = help_img
        self.on_ha_change = on_ha_change
        self.vars = {}

        self.pack(fill="x", padx=10, pady=5)
        self._build_ui()

    def _build_ui(self):
        label_frame = ctk.CTkFrame(self, fg_color="#f8f9fa", border_color="#dee2e6", border_width=1, corner_radius=6)
        label_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(label_frame, text="Podstawowa konfiguracja", font=("Segoe UI", 15, "bold"), text_color="#000000", fg_color="#f8f7f4", corner_radius=8).pack(fill="x", anchor="w")

        self.config_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.config_frame.pack(fill="x")

        self._add_dropdown("Version", "Wersja", VERSIONS, "10.9.1", parent_frame=self.config_frame)
        self._add_checkbox("IsHA", "Odblokować architekturę HA?", default=False, command=self._handle_ha_toggle, parent_frame=self.config_frame)

        # Pola warunkowe — tworzone, ale początkowo ukryte
        self.portal_ctx_row = self._add_field("PortalContext", "Kontekst portalu", "portal", parent_frame=self.config_frame, pack=False)
        self.server_ctx_row = self._add_field("ServerContext", "Kontekst serwera", "arcgis", parent_frame=self.config_frame, pack=False)
        self.server_role_row = self._add_dropdown("ServerRole", "Rola serwera", SERVER_ROLE_OPTIONS, "GeneralPurposeServer", parent_frame=self.config_frame, pack=False)

        # Poświadczenia
        self.credentials_section = ctk.CTkFrame(self, fg_color="transparent")
        self.credentials_section.pack(fill="x")

        ctk.CTkLabel(self.credentials_section, text="Poświadczenia", font=("Segoe UI", 15, "bold"), fg_color="#f8f7f4").pack(fill="x", anchor="w", padx=10, pady=(20, 5))

        self.credentials_frame = ctk.CTkFrame(self.credentials_section, fg_color="transparent")
        self.credentials_frame.pack(fill="x")

        self._add_field("Service Account", "Konto techniczne", "DOMAIN\\USER", parent_frame=self.credentials_frame)
        self._add_field("Service Account Password", "Hasło konta technicznego", "", is_pass=True, parent_frame=self.credentials_frame)
        self._add_field("ADService Account", "Konto techniczne AD", "DOMAIN\\USER", parent_frame=self.credentials_frame)
        self._add_field("ADService Account Password", "Hasło konta technicznego AD", "", is_pass=True, parent_frame=self.credentials_frame)

    def _handle_ha_toggle(self):
        if self.on_ha_change:
            self.on_ha_change(self.vars["IsHA"].get())

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