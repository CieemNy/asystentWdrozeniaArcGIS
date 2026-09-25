import customtkinter as ctk
from core import session
from core.utils import build_dsc_patch_config

class PortalSectionFrame(ctk.CTkFrame):
    def __init__(self, master, help_img=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.help_img = help_img
        self.vars = {}
        self._build_ui()

    def _build_ui(self):
        label_frame = ctk.CTkFrame(
            self, 
            fg_color="#f8f9fa",
        )
        label_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            label_frame, 
            text="Konfigurator Portal For ArcGIS", 
            font=("Segoe UI", 15, "bold"), 
            fg_color="#f8f7f4"
        ).pack(fill="x", anchor="w")

        portal_installer = session.get("portal_installer", "C:\\Installation\\Software\\PortalForArcGIS\\Setup.exe")
        portal_volume = session.get("portal_volume", "C:\\Installation\\Software\\PortalForArcGIS\\volume.exe.001")
        portal_license = session.get("portal_license", "C:\\Installation\\License\\[PortalLicenseFileName]")

        patch_cfg = build_dsc_patch_config("portal_patches")     
        has_patches = bool(patch_cfg)
        default_patch_dir = patch_cfg.get("PatchesDir", "C:\\Installation\\Patches\\Datestore")
        default_patch_list = ", ".join(patch_cfg.get("PatchInstallOrder", [])) if has_patches else "patch1.msp"

        self._add_field("Path to Portal Installer", "Ścieżka do instalki ArcGIS Portal", portal_installer)
        self._add_field("Path to Portal Volume", "Ścieżka do woluminu ArcGIS Portal", portal_volume)
        self._add_checkbox("Portal_IsSelfExtracting", "Do wypakowania?", default=False)
        self._add_field("Path to Portal License", "Ścieżka do licencji", portal_license)
        self._add_field("Portal Install Directory", "Katalog instalacji", "C:\\Program Files\\ArcGIS\\Portal")
        self._add_field("Portal Content Directory", "Katalog zawartości ArcGIS Portalu", "C:\\arcgisportal")
        self.portal_anchor = self._add_field("Portal Content Location", "Lokalizacja zasobów ArcGIS Portalu", "C:\\arcgisportal\\content")

        # Sekcja Patchy
        self.patch_anchor = self._add_checkbox("Portal_DoPatch", "Zainstalować patche?", default=False, command=self.toggle_patches)
        self.patches_container = ctk.CTkFrame(self, fg_color="transparent")
        self._add_field_to_frame(self.patches_container, "Portal Patches Directory", "Katalog patchy ArcGIS Portal", default_patch_dir)
        self._add_field_to_frame(self.patches_container, "Portal Patches List", "Lista patchy ArcGIS Portal", default_patch_list)

        # Sekcja HA
        self.ha_container = ctk.CTkFrame(self, fg_color="transparent")
        self._add_field_to_frame(self.ha_container, "Portal External LB", "Zewnętrzny LB Portalu", "")
        self._add_field_to_frame(self.ha_container, "Portal Internal LB", "Wewnętrzny LB Portalu", "")
        self._add_field_to_frame(self.ha_container, "Portal Internal LB Port", "Wewnętrzny Port LB Portalu", "7443")

        admin_sub = ctk.CTkFrame(self, fg_color="transparent")
        admin_sub.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(
            admin_sub, 
            text="Konto administracyjne Portalu", 
            font=("Segoe UI", 12, "bold"), 
            fg_color="#f8f7f4"
        ).pack(anchor="w", fill="x", padx=10)

        self._add_field_to_frame(admin_sub, "Portal Username", "Imię i Nazwisko", "Imie Nazwisko")
        self._add_field_to_frame(admin_sub, "Portal Admin User", "Nazwa użytkownika", "PortalCreator")
        self._add_field_to_frame(admin_sub, "Portal Admin Password", "Hasło użytkownika", "", is_pass=True)
        self._add_field_to_frame(admin_sub, "Portal Admin Email", "Email", "admin@domain.local")

    def _add_field(self, var_key, label_text, default, is_pass=False):
        return self._add_field_to_frame(self, var_key, label_text, default, is_pass)

    def _add_field_to_frame(self, parent_frame, var_key, label_text, default, is_pass=False):
        row = ctk.CTkFrame(parent_frame, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(row, text=label_text, width=230, anchor="w", text_color="black").pack(side="left")
        v = ctk.StringVar(value=default)
        self.vars[var_key] = v
        ctk.CTkEntry(row, textvariable=v, fg_color="white", text_color="black", show="*" if is_pass else "").pack(side="left", fill="x", expand=True)
        return row

    def _add_checkbox(self, var_key, label_text, default=True, command=None):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(row, text=label_text, width=230, anchor="w", text_color="black").pack(side="left")
        v = ctk.BooleanVar(value=default)
        self.vars[var_key] = v
        cb = ctk.CTkCheckBox(row, text="", variable=v, width=20, command=command)
        cb.pack(side="left")
        return row

    def toggle_patches(self):
        if self.vars["Portal_DoPatch"].get():
            self.patches_container.pack(fill="x", after=self.patch_anchor)
        else:
            self.patches_container.pack_forget()

    def toggle_ha(self, is_ha_enabled):
        if is_ha_enabled:
            self.ha_container.pack(fill="x", after=self.portal_anchor)
        else:
            self.ha_container.pack_forget()

    def refresh_layout(self, is_ha_enabled):
        self.toggle_patches()
        self.toggle_ha(is_ha_enabled)

    def get_data(self, is_ha_global, download_setups=False):
        v = {k: var.get() for k, var in self.vars.items()}
        
        p_inst = {
            "Path": v["Path to Portal Installer"], 
            "IsSelfExtracting": v["Portal_IsSelfExtracting"], 
            "InstallDir": v["Portal Install Directory"], 
            "ContentDir": v["Portal Content Directory"]
        }

        if v.get("Path to Portal Volume") and download_setups:
            p_inst["VolumePaths"] = [p.strip() for p in v["Path to Portal Volume"].split(",") if p.strip()]

        if v["Portal_DoPatch"]:
            p_inst["PatchesDir"] = v["Portal Patches Directory"]
            p_inst["PatchInstallDir"] = [p.strip() for p in v["Portal Patches List"].split(",") if p.strip()]

        pc = {
            "Installer": p_inst, 
            "LicenseFilePath": v["Path to Portal License"], 
            "PortalLicenseUserTypeId": "creatorUT", 
            "PortalAdministrator": {
                "Fullname": v["Portal Username"], 
                "UserName": v["Portal Admin User"], 
                "Password": v["Portal Admin Password"], 
                "Email": v["Portal Admin Email"], 
                "SecurityQuestionIndex": 1, 
                "SecurityAnswer": "123"
            }, 
            "ContentDirectoryLocation": v["Portal Content Location"], 
            "EnableAutomaticAccountCreation": False, 
            "DefaultRoleForUser": "iAAAAAAAAAAAAAAA", 
            "DefaultUserLicenseTypeIdForUser": "viewerUT", 
            "EnableHSTS": True
        }

        if is_ha_global:
            if v.get("Portal External LB"): 
                pc["ExternalLoadBalancer"] = v["Portal External LB"]
            if v.get("Portal Internal LB"): 
                pc["InternalLoadBalancer"] = v["Portal Internal LB"]
            try:
                lb_port = int(v.get("Portal Internal LB Port"))
            except Exception:
                lb_port = 7443
            pc["InternalLoadBalancerPort"] = lb_port

        return pc