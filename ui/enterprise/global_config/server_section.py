import customtkinter as ctk
from core.utils import CTKTooltip, build_dsc_patch_config
from core import session
from ui.components.form_fields import FormFieldMixin

class ServerSectionFrame(FormFieldMixin, ctk.CTkFrame):
    def __init__(self, master, help_img=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.help_img = help_img
        self.vars = {}
        self._build_ui()

    def _build_ui(self):
        label_frame = ctk.CTkFrame(
            self, 
            fg_color="#f8f9fa"
        )
        label_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            label_frame, 
            text="Konfigurator ArcGIS Server", 
            font=("Segoe UI", 15, "bold"), 
            fg_color="#f8f7f4",
            text_color="#000000"
        ).pack(fill="x", anchor="w")

        server_installer = session.get("server_installer", "C:\\Installation\\Software\\ArcGISServer\\Setup.exe")
        server_volume = session.get("server_volume", "C:\\Installation\\Patches\\Server\\volume.exe.001")
        windotnet_runtime = session.get("windotnet_runtime", "C:\\Installation\\Software\\windowsdesktop-runtime-8.0.8-win-x64.exe")
        server_license = session.get("server_license", "C:\\Installation\\License\\[[ServerLicenseFileName]")
        patch_cfg = build_dsc_patch_config("server_patches")     
        has_patches = bool(patch_cfg)
        default_patch_dir = patch_cfg.get("PatchesDir", "C:\\Installation\\Patches\\Sever")
        default_patch_list = ", ".join(patch_cfg.get("PatchInstallOrder", [])) if has_patches else "patch1.msp"

        self._add_field("Path to Server Installer", "Ścieżka do instalki ArcGIS Server", server_installer)
        self._add_field("Path to Server Volume", "Ścieżka do woluminu ArcGIS Server", server_volume)
        self._add_checkbox("Server_IsSelfExtracting", "Do wypakowania?", default=False)
        self._add_field("Path to Server License", "Ścieżka do licencji ArcGIS Server", server_license)
        self._add_field("Server Install Directory", "Katalog instalacji", "C:\\Program Files\\ArcGIS\\Server", editable=False)
        self._add_field("Server Root Directory", "Główny katalog ArcGIS Servera", "C:\\arcgisserver\\directories", editable=False)
        self._add_field("Server Config Store", "Katalog konfiguracji ArcGIS Server", "C:\\arcgisserver\\config-store", editable=False)
        self.server_anchor = self._add_field("Server Python Directory", "Katalog Python ArcGIS Servera", "C:\\opt\\Python27", editable=False)

        # Sekcja Patchy
        self.server_patch_anchor = self._add_checkbox("Server_DoPatch", "Zainstalować patche?", default=False, command=lambda: self._toggle_container("Server_DoPatch", self.patches_container, self.server_patch_anchor))
        self.patches_container = ctk.CTkFrame(self, fg_color="transparent")
        self._add_field_to_frame(self.patches_container, "Server Patches Directory", "Katalog patchy ArcGIS Server", default_patch_dir)
        self._add_field_to_frame(self.patches_container, "Server Patches List", "Lista patchy ArcGIS Server", default_patch_list)

        # Sekcja HA
        self.ha_container = ctk.CTkFrame(self, fg_color="transparent")
        self._add_field_to_frame(self.ha_container, "Server External LB", "Zewnętrzny LB Servera", "")
        self._add_field_to_frame(self.ha_container, "Server Installer LB", "Wewnętrzny LB Servera", "")
        self._add_field_to_frame(self.ha_container, "Server Installer LB Port", "Wewnętrzny Port LB Servera", "6443")

        adds_sub = ctk.CTkFrame(self, fg_color="transparent")
        adds_sub.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(
            adds_sub, 
            text="Dodatkowe komponenty dla ArcGIS Servera", 
            font=("Segoe UI", 12, "bold"),
            fg_color="#f8f7f4",
            text_color="#000000"
        ).pack(fill="x", anchor="w", padx=10)

        self._add_checkbox("Server_EnableArcMap", "Odblokować ArcMap Runtime?", default=True, help_text="Dostępne jedynie dla wersji 10.9.1. Jeśli instalujesz inną wersję, odznacz tą opcję.", parent_frame=adds_sub)
        self.server_dotnet_anchor = self._add_checkbox("Server_EnableDotnet", "Odblokować Dotnet Support?", default=True, command=lambda: self._toggle_container("Server_EnableDotnet", self.dotnet_container, self.server_dotnet_anchor), parent_frame=adds_sub)

        self.dotnet_container = ctk.CTkFrame(adds_sub, fg_color="transparent")
        self._add_field_to_frame(self.dotnet_container, "Path to Server Dotnet", "Ścieżka do Dotneta", windotnet_runtime)

        admin_sub = ctk.CTkFrame(self, fg_color="transparent")
        admin_sub.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(
            admin_sub, 
            text="Konto administracyjne ArcGIS Servera", 
            font=("Segoe UI", 12, "bold"), 
            fg_color="#f8f7f4",
            text_color="#000000"
        ).pack(fill="x", anchor="w", padx=10)

        self._add_field_to_frame(admin_sub, "Server Admin User", "Nazwa użytkownika", "siteadmin", editable=False)
        self._add_field_to_frame(admin_sub, "Server Admin Password", "Hasło użytkownika", "", is_pass=True)

    def refresh_layout(self, is_ha_enabled):
        self._toggle_container("Server_DoPatch", self.patches_container, self.server_patch_anchor)
        self._toggle_container_var(is_ha_enabled, self.ha_container, self.server_anchor)
        self._toggle_container("Server_EnableDotnet", self.dotnet_container, self.server_dotnet_anchor)

    def get_data(self, is_ha_global, download_setups=False):
        v = {k: var.get() for k, var in self.vars.items()}
        
        s_inst = {
            "Path": v["Path to Server Installer"], 
            "IsSelfExtracting": v["Server_IsSelfExtracting"], 
            "InstallDir": v["Server Install Directory"], 
            "InstallDirPython": v["Server Python Directory"], 
            "EnableArcMapRuntime": v["Server_EnableArcMap"], 
            "EnableDotnetSupport": v["Server_EnableDotnet"]
        }

        if v.get("Path to Server Volume") and download_setups:
            s_inst["VolumePaths"] = [p.strip() for p in v["Path to Server Volume"].split(",") if p.strip()]

        if v["Server_EnableDotnet"]:
            s_inst["DotnetDesktopRuntimePath"] = v["Path to Server Dotnet"]

        if v["Server_DoPatch"]:
            s_inst["PatchesDir"] = v["Server Patches Directory"]
            s_inst["PatchInstallOrder"] = [p.strip() for p in v["Server Patches List"].split(",") if p.strip()]

        root = v["Server Root Directory"].rstrip("\\")
        sc = {
            "LicenseFilePath": v["Path to Server License"], 
            "Installer": s_inst, 
            "ServerDirectoriesRootLocation": root, 
            "ConfigStoreLocation": v["Server Config Store"], 
            "LocalRepositoryPath": "C:\\arcgisserver\\local", 
            "ServerLogsLocation": "C:\\arcgisserver\\logs", 
            "ServerDirectories": [
                {"name": "arcgiscache", "physicalPath": f"{root}\\arcgiscache", "directoryType": "CACHE", "cleanupMode": "NONE", "maxFileAge": 0}, 
                {"name": "arcgisjobs", "physicalPath": f"{root}\\arcgisjobs", "directoryType": "JOBS", "cleanupMode": "TIME_ELAPSED_SINCE_LAST_MODIFIED", "maxFileAge": 360}, 
                {"name": "arcgisoutput", "physicalPath": f"{root}\\arcgisoutput", "directoryType": "OUTPUT", "cleanupMode": "TIME_ELAPSED_SINCE_LAST_MODIFIED", "maxFileAge": 10}, 
                {"name": "arcgissystem", "physicalPath": f"{root}\\arcgissystem", "directoryType": "SYSTEM", "cleanupMode": "NONE", "maxFileAge": 0}
            ], 
            "PrimarySiteAdmin": {
                "UserName": v["Server Admin User"], 
                "Password": v["Server Admin Password"]
            }, 
            "EnableHTTPSOnly": True
        }

        if is_ha_global:
            if v.get("Server External LB"): 
                sc["ExternalLoadBalancer"] = v["Server External LB"]
            if v.get("Server Installer LB"): 
                sc["InternalLoadBalancer"] = v["Server Installer LB"]
            try:
                lb_port = int(v.get("Server Installer LB Port"))
            except Exception:
                lb_port = 6443
            sc["InternalLoadBalancerPort"] = lb_port

        return sc