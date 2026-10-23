import customtkinter as ctk
from config import PRO_VERSIONS, PRO_AUTH_TYPES
from core import session
from core.utils import build_dsc_patch_config
from ui.components.form_fields import FormFieldMixin

class ProConfigPanel(FormFieldMixin, ctk.CTkFrame):
    def __init__(self, master, help_img=None, **kwargs):
        super().__init__(master, fg_color="white", border_width=1, border_color="#cbd5e0", **kwargs)
        self.help_img = help_img
        self.vars = {}
        
        self.pack(fill="x", padx=15, pady=20)
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self, 
            text="Konfigurator ArcGIS Pro", 
            font=("Segoe UI", 15, "bold"), 
            fg_color="#f8f7f4",
            text_color="#000000"
        ).pack(anchor="w", fill="x", padx=15, pady=(15, 5))

        pro_installer = session.get("pro_installer", "C:\\Installation\\Software\\ArcGISServer\\Setup.exe")
        windotnet_runtime = session.get("windotnet_runtime", "C:\\Installation\\Software\\windowsdesktop-runtime-8.0.8-win-x64.exe")
        webview2 = session.get("webview2", "C:\\Installation\\Software\\webview.exe")

        patch_cfg = build_dsc_patch_config("pro_patches")     
        has_patches = bool(patch_cfg)
        default_patch_dir = patch_cfg.get("PatchesDir", "C:\\Installation\\Patches\\Pro")
        default_patch_list = ", ".join(patch_cfg.get("PatchInstallOrder", [])) if has_patches else "patch1.msp"

        self._add_dropdown("ProVersion", "Wersja ArcGIS Pro", PRO_VERSIONS, "3.6")

        self._add_field("Path_Installer", "Ścieżka do instalki ArcGIS Pro", pro_installer)
        self._add_checkbox("Pro_IsSelfExtracting", "Do rozpakowania?", default=True)
        self._add_field("Install_Dir", "Katalog instalacji", "C:\\Program Files\\ArcGIS\\Pro")
        self._add_field("Path_Dotnet", "Ścieżka do DotNet Desktop Runtime", windotnet_runtime)
        self._add_field("Path_WebView2", "Ścieżka do Edge WebView2 Runtime", webview2)
        
        self.cb_patch = self._add_checkbox("Pro_DoPatch", "Zainstalować patche?", default=True, command=self.toggle_patches)
        self.patches_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._add_field_to_frame(self.patches_frame, "Patches_Dir", "Katalog patchy ArcGIS PRO", default_patch_dir)
        self._add_field_to_frame(self.patches_frame, "Patches_List", "Lista patchy ArcGIS Pro", default_patch_list)

        # 4. Licencjonowanie
        ctk.CTkLabel(
            self, 
            text="Licencjonowanie & Autoryzacja", 
            font=("Segoe UI", 12, "bold"), 
            fg_color="#f8f7f4",
            text_color="#000000"
        ).pack(anchor="w", fill="x", padx=15, pady=(15, 5))

        self.dd_auth = self._add_dropdown(
            "AuthorizationType", "Typ autoryzacji", 
            PRO_AUTH_TYPES, "CONCURRENT_USE", command=self.toggle_license_host
        )
        self.row_license_host = self._add_field("EsriLicenseHost", "FQDN serwera licencji", "serwer_licencji.com.pl")

        # 5. Ustawienia dodatkowe
        ctk.CTkLabel(
            self, 
            text="Ustawienia aplikacji", 
            font=("Segoe UI", 12, "bold"), 
            fg_color="#f8f7f4",
            text_color="#000000"
        ).pack(anchor="w", fill="x", padx=15, pady=(15, 5))

        self._add_checkbox("EnableEUEI", "Odblokuj EUEI (User Experience)", default=False)
        self._add_checkbox("CheckForUpdatesAtStartup", "Sprawdzaj aktualizacje", default=False)

        # Inicjalne ustawienie widoczności
        self.toggle_patches()
        self.toggle_license_host()

    def toggle_patches(self):
        if self.vars["Pro_DoPatch"].get():
            self.patches_frame.pack(fill="x", after=self.cb_patch)
        else:
            self.patches_frame.pack_forget()

    def toggle_license_host(self, choice=None):
        auth_type = self.vars["AuthorizationType"].get()
        if auth_type in ["CONCURRENT_USE", "SINGLE_USE"]:
            self.row_license_host.pack(fill="x", padx=20, pady=2, after=self.dd_auth)
        else:
            self.row_license_host.pack_forget()
    
    def get_config_data(self):
        """Zwraca słownik ConfigData zgodnie z wymaganą strukturą JSON."""
        v = {k: var.get() for k, var in self.vars.items()}

        installer_data = {
            "Path": v["Path_Installer"],
            "IsSelfExtracting": v["Pro_IsSelfExtracting"],
            "DotnetDesktopRuntimePath": v["Path_Dotnet"],
            "EdgeWebView2RuntimePath": v["Path_WebView2"],
            "InstallDir": v["Install_Dir"]
        }

        if v["Pro_DoPatch"]:
            installer_data["PatchesDir"] = v["Patches_Dir"]
            installer_data["PatchInstallOrder"] = [
                p.strip() for p in v["Patches_List"].split(",") if p.strip()
            ]

        pro_data = {
            "Installer": installer_data,
            "AuthorizationType": v["AuthorizationType"],
            "EnableEUEI": v["EnableEUEI"],
            "CheckForUpdatesAtStartup": v["CheckForUpdatesAtStartup"]
        }

        if v["AuthorizationType"] in ["CONCURRENT_USE", "SINGLE_USE"] and v.get("EsriLicenseHost"):
            pro_data["EsriLicenseHost"] = v["EsriLicenseHost"]

        return {
            "ProVersion": v["ProVersion"],
            "Pro": pro_data
        }