# global_config/webadaptor_section.py
import customtkinter as ctk
from core import session

class WebAdaptorSectionFrame(ctk.CTkFrame):
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

        self._add_checkbox_to_frame(wa_sub, "WA_AdminAccess", "Odblokować dostęp administracyjny?", default=True)
        self._add_checkbox_to_frame(wa_sub, "WA_OverrideHTTPS", "Nadpisać powiązania HTTPS w IIS?", default=True)

    def _add_field(self, var_key, label_text, default, is_pass=False):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(row, text=label_text, width=230, anchor="w", text_color="black").pack(side="left")
        v = ctk.StringVar(value=default)
        self.vars[var_key] = v
        ctk.CTkEntry(row, textvariable=v, fg_color="white", text_color="black", show="*" if is_pass else "").pack(side="left", fill="x", expand=True)
        return row

    def _add_checkbox(self, var_key, label_text, default=True, command=None):
        return self._add_checkbox_to_frame(self, var_key, label_text, default, command)

    def _add_checkbox_to_frame(self, parent_frame, var_key, label_text, default=True, command=None):
        row = ctk.CTkFrame(parent_frame, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(row, text=label_text, width=230, anchor="w", text_color="black").pack(side="left")
        v = ctk.BooleanVar(value=default)
        self.vars[var_key] = v
        cb = ctk.CTkCheckBox(row, text="", variable=v, width=20, command=command)
        cb.pack(side="left")
        return row

    def _add_hr(self):
        line = ctk.CTkFrame(self, height=2, fg_color="#e2e8f0", border_width=0)
        line.pack(fill="x", padx=20, pady=15)

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