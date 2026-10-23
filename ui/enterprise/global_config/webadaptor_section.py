# global_config/webadaptor_section.py
import customtkinter as ctk
from core import session
from ui.components.form_fields import FormFieldMixin

class WebAdaptorSectionFrame(FormFieldMixin, ctk.CTkFrame):
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
            text="Konfigurator ArcGIS Web Adaptor", 
            font=("Segoe UI", 15, "bold"),
            fg_color="#f8f7f4"
        ).pack(fill="x", anchor="w")

        webadaptor_installer = session.get("webadaptor_installer", "C:\\Installation\\Software\\ArcGISServer\\Setup.exe")
        webdeploy_installer = session.get("webdeploy_installer", "C:\\Installation\\Software\\webdeploy_amd64_pl-PL.msi")
        dotnet_hosting = session.get("dotnet_hosting", "C:\\Installation\\Software\\dotnet-hosting-8.0.0-win.exe")

        self._add_field("Path to WebAdaptor Installer", "Ścieżka do instalki ArcGIS WebAdaptor", webadaptor_installer)
        self._add_checkbox("WA_IsSelfExtracting", "Do wypakowania?", default=False)
        self._add_field("Path to WebAdaptor Dotnet", "Ścieżka do instalki Dotnet", dotnet_hosting)
        self._add_field("Path to WebAdaptor WebDeploy", "Ścieżka do instalki WebDeploy", webdeploy_installer)

        wa_sub = ctk.CTkFrame(self, fg_color="transparent")
        wa_sub.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(
            wa_sub, 
            text="Opcje dla ArcGIS Webadaptor", 
            font=("Segoe UI", 12, "bold"),
            fg_color="#f8f7f4"
        ).pack(anchor="w", fill="x", padx=10)

        self._add_checkbox("WA_AdminAccess", "Odblokować dostęp administracyjny?", default=True, parent_frame=wa_sub)
        self._add_checkbox("WA_OverrideHTTPS", "Nadpisać powiązania HTTPS w IIS?", default=True, parent_frame=wa_sub)

    def get_data(self):
        v = {k: var.get() for k, var in self.vars.items()}
        return {
            "Installer": {
                "Path": v["Path to WebAdaptor Installer"], 
                "IsSelfExtracting": v["WA_IsSelfExtracting"], 
                "DotnetHostingBundlePath": v["Path to WebAdaptor Dotnet"], 
                "WebDeployPath": v["Path to WebAdaptor WebDeploy"]
            }, 
            "AdminAccessEnabled": v["WA_AdminAccess"], 
            "OverrideHTTPSBinding": v["WA_OverrideHTTPS"]
        }