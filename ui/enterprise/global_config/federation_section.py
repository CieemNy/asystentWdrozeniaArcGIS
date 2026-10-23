import customtkinter as ctk
from ui.components.form_fields import FormFieldMixin

class FederationSectionFrame(FormFieldMixin, ctk.CTkFrame):
    def __init__(self, master, help_img=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.help_img = help_img
        self.vars = {}
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self, 
            text="Konfigurator Federacji", 
            font=("Segoe UI", 15, "bold"), 
            fg_color="#f8f7f4"
        ).pack(anchor="w", padx=10, fill="x", pady=(0, 10))
        self.fed_anchor = self._add_checkbox("DoFederate", "Sfederować Portal & Server?", default=False, command=lambda: self._toggle_container("DoFederate", self.fed_fields_frame, self.fed_anchor))

        self.fed_fields_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._add_field_to_frame(self.fed_fields_frame, "Portal Federation Hostname", "Hostname Portalu", "")
        self._add_field_to_frame(self.fed_fields_frame, "Portal Federation Port", "Port Portalu", "443")
        self._add_field_to_frame(self.fed_fields_frame, "Portal Federation Context", "Kontekst Portalu", "portal")

        ctk.CTkLabel(
            self.fed_fields_frame, 
            text="Konto administracyjne Portalu", 
            font=("Segoe UI", 12, "bold"), 
            fg_color="#f8f7f4"
        ).pack(anchor="w", padx=20, fill="x", pady=(10, 0))
        self._add_field_to_frame(self.fed_fields_frame, "Portal Federation Admin UserName", "Nazwa użytkownika", "PortalCreator")
        self._add_field_to_frame(self.fed_fields_frame, "Portal Federation Admin Password", "Hasło użytkownika", "", is_pass=True)

        ctk.CTkLabel(
            self.fed_fields_frame, 
            text="Opcjonalne parametry ArcGIS Servera",
            font=("Segoe UI", 12, "bold"), 
            fg_color="#f8f7f4"
        ).pack(anchor="w", padx=20, fill="x", pady=(15, 0))
        self._add_field_to_frame(self.fed_fields_frame, "Server Federation Hostname", "Hostname Servera", "")
        self._add_field_to_frame(self.fed_fields_frame, "Server Federation Port", "Port Servera", "443")
        self._add_field_to_frame(self.fed_fields_frame, "Server Federation Context", "Kontekst Serwera", "arcgis")
        self._add_field_to_frame(self.fed_fields_frame, "Server Federation Admin Hostname", "Hostname Administracyjny", "")
        self._add_field_to_frame(self.fed_fields_frame, "Server Federation Admin URL Port", "Port administracyjny Servera", "6443")
        self._add_field_to_frame(self.fed_fields_frame, "Server Federation Admin Context", "Kontekst administracyjny Servera", "arcgis")

    def toggle_federation(self):
        if self.vars["DoFederate"].get():
            self.fed_fields_frame.pack(fill="x", padx=0, pady=5)
        else:
            self.fed_fields_frame.pack_forget()

    def is_federation_enabled(self):
        return self.vars["DoFederate"].get()

    def get_data(self):
        v = {k: var.get() for k, var in self.vars.items()}
        fed = {
            "PortalHostName": v["Portal Federation Hostname"], 
            "PortalPort": int(v["Portal Federation Port"] or 7443), 
            "PortalContext": v["Portal Federation Context"], 
            "PortalAdministrator": {
                "UserName": v["Portal Federation Admin UserName"], 
                "Password": v["Portal Federation Admin Password"]
            }
        }
        for jk, vk in [
            ("ServerHostName", "Server Federation Hostname"), 
            ("ServerUrlPort", "Server Federation Port"), 
            ("ServerContext", "Server Federation Context"), 
            ("ServerAdminHostName", "Server Federation Admin Hostname"), 
            ("ServerAdminUrlPort", "Server Federation Admin URL Port"), 
            ("ServerAdminContext", "Server Federation Admin Context")
        ]:
            val = v[vk].strip()
            if val:
                fed[jk] = int(val) if "Port" in jk and val.isdigit() else val
        return fed