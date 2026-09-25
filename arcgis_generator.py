import datetime
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
from collections import OrderedDict
import os
from PIL import Image, ImageTk
import sys

# --- KONFIGURACJA UI ---
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

# --- STAŁE I OPCJE ---
ROLES = ["Server", "Portal", "DataStore", "WebAdaptor"]
DS_TYPES = ["Relational", "SpatioTemporal", "TileCache", "GraphStore", "ObjectStore"]
SSL_TARGETS = ["Server", "Portal", "DataStore", "WebAdaptor"]
VERSIONS = ["12.0", "11.5", "11.4", "11.3", "11.2", "11.1", "11.0", "10.9.1", "10.9", "10.8.1"]

SERVER_ROLE_OPTIONS = [
    "GeneralPurposeServer", "GeoAnalytics", "GeoEvent", "ImageHosting", 
    "RasterAnalytics", "NotebookServer", "MissionServer", 
    "KnowledgeServer", "WorkflowManagerServer", "VideoServer"
]

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CTKTooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window:
            return

        # Pobieramy pozycję i dodajemy offset, żeby okno nie "blokowało" myszy
        x = self.widget.winfo_rootx() + 25 
        y = self.widget.winfo_rooty() + 10

        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.attributes("-topmost", True)
        
        # Opcjonalnie: upewnij się, że okno nie przejmuje fokusu
        self.tooltip_window.withdraw()
        
        label = ctk.CTkLabel(self.tooltip_window, text=self.text, 
                             fg_color="#1e293b", text_color="white",
                             corner_radius=6, padx=10, pady=5, font=("Segoe UI", 11))
        label.pack()
        
        self.tooltip_window.deiconify()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class SSLCertificateRow(ctk.CTkFrame):
    def __init__(self, master, on_remove, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#f8f9fa", border_width=1, border_color="#dee2e6")
        self.pack(fill="x", pady=0, padx=0)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(header, text="CERTIFICATE CONFIG", font=("Segoe UI", 12, "bold"), text_color="#000000").pack(side="left")
        ctk.CTkButton(header, text="Delete", width=60, height=22, fg_color="#fee2e2", text_color="#dc2626", 
                      hover_color="#fecaca", command=lambda: on_remove(self)).pack(side="right")

        self.ents = {}
        fields = [("Path to Cert:", "path"), ("Cert Password:", "pass"), ("CName (FQDN):", "cname")]
        for lbl, key in fields:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=lbl, width=120, anchor="w", text_color="black").pack(side="left")
            entry = ctk.CTkEntry(row, height=28, text_color="black", fg_color="white", show="*" if "pass" in key else "")
            entry.pack(side="left", fill="x", expand=True)
            self.ents[key] = entry
        
        self.ents["cname"].insert(0, "domena.local")

        target_f = ctk.CTkFrame(self, fg_color="transparent")
        target_f.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(target_f, text="Target:", text_color="black", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0,10))
        self.target_vars = {t: ctk.BooleanVar() for t in SSL_TARGETS}
        for t in SSL_TARGETS:
            ctk.CTkCheckBox(target_f, text=t, variable=self.target_vars[t], text_color="black", checkbox_width=18).pack(side="left", padx=5)

    def get_data(self):
        p = self.ents["path"].get().strip()
        if not p: return None
        return {
            "Path": p, 
            "Password": self.ents["pass"].get(), 
            "CNameFQDN": self.ents["cname"].get(),
            "Target": [t for t, v in self.target_vars.items() if v.get()]
        }

class NodeFrame(ctk.CTkFrame):
    def __init__(self, master, index, on_remove, on_role_change, **kwargs):
        super().__init__(master, **kwargs)
        self.on_role_change = on_role_change
        self.configure(fg_color="#ffffff", border_width=1, border_color="#cbd5e0")
        self.pack(fill="x", pady=10, padx=15)

        # Nagłówek i Nazwa FQDN
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(header, text=f"MACHINE #{index}", font=("Segoe UI", 16, "bold"), text_color="black").pack(side="left")
        ctk.CTkButton(header, text="DELETE MACHINE", width=120, fg_color="#dc3545", hover_color="#c82333", command=lambda: on_remove(self)).pack(side="right")

        fqdn_f = ctk.CTkFrame(self, fg_color="transparent")
        fqdn_f.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(fqdn_f, text="Node FQDN:", width=120, anchor="w", text_color="black").pack(side="left")
        self.ent_name = ctk.CTkEntry(fqdn_f, text_color="black", fg_color="white")
        self.ent_name.pack(side="left", fill="x", expand=True)
        self.ent_name.insert(0, "domena.local")

        role_f = ctk.CTkFrame(self, fg_color="transparent")
        role_f.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(role_f, text="Role:", width=120, anchor="w", text_color="black").pack(side="left")
        self.role_vars = {r: ctk.BooleanVar() for r in ROLES}
        for r in ROLES:
            ctk.CTkCheckBox(role_f, text=r, variable=self.role_vars[r], command=self.refresh_ui, text_color="black", checkbox_width=20).pack(side="left", padx=10)

        # --- SEKCJA WEBADAPTOR (KOMPAKTOWA) ---
        self.wa_container = ctk.CTkFrame(self, fg_color="#f1f5f9", border_width=1, border_color="#e2e8f0")
        ctk.CTkLabel(self.wa_container, text="WEBADAPTOR CONFIG", font=("Segoe UI", 11, "bold"), text_color="black").pack(padx=10, anchor="w", pady=5)
        
        wa_rows = ctk.CTkFrame(self.wa_container, fg_color="transparent")
        wa_rows.pack(fill="x", padx=10, pady=(0, 5))

        def create_wa_group(master, role_name, default_ctx):
            container = ctk.CTkFrame(master, fg_color="transparent")
            ctk.CTkLabel(container, text=f"{role_name} Context:", font=("Segoe UI", 11, "bold"), text_color="black", width=110, anchor="w").pack(side="left", padx=(0, 5))
            ctx_ent = ctk.CTkEntry(container, width=100, fg_color="white", text_color="black")
            ctx_ent.insert(0, default_ctx)
            ctx_ent.pack(side="left", padx=2)
            admin_var = ctk.BooleanVar(value=False)
            admin_group = ctk.CTkFrame(container, fg_color="transparent")
            admin_group.pack(side="left", padx=10)
            ctk.CTkLabel(admin_group, text="Admin Access", font=("Segoe UI", 11), text_color="black").pack(side="left", padx=(0, 5))
            admin_check = ctk.CTkCheckBox(admin_group, text="", variable=admin_var, checkbox_width=16, width=16)
            admin_check.pack(side="left")
            return container, ctx_ent, admin_var

        self.wa_p_group, self.wa_p_ctx, self.wa_p_admin_var = create_wa_group(wa_rows, "Portal", "portal")
        self.wa_s_group, self.wa_s_ctx, self.wa_s_admin_var = create_wa_group(wa_rows, "Server", "arcgis")

        # DataStore Section
        self.ds_container = ctk.CTkFrame(self, fg_color="#f8fafc", border_width=1, border_color="#e2e8f0")
        ctk.CTkLabel(self.ds_container, text="DATESTORE TYPES:", text_color="black", font=("Segoe UI", 12, "bold")).pack(padx=10, anchor="w", pady=5)
        self.ds_vars = {ds: ctk.BooleanVar(value=(ds=="Relational")) for ds in DS_TYPES}
        for ds in DS_TYPES:
            ctk.CTkCheckBox(self.ds_container, text=ds, variable=self.ds_vars[ds], text_color="black", checkbox_width=18).pack(side="left", padx=10, pady=5)

        # SSL Box
        self.ssl_box = ctk.CTkFrame(self, fg_color="transparent")
        self.ssl_box.pack(fill="x", padx=20, pady=10)
        self.ssl_rows_list = []
        self.add_ssl_btn = ctk.CTkButton(self.ssl_box, text="Add Certificate SSL", width=140, fg_color="#e9ecef", text_color="black", hover_color="#dee2e6", command=self.add_ssl)
        self.add_ssl_btn.pack(pady=5, anchor="w")

    def refresh_ui(self):
        if self.role_vars["WebAdaptor"].get():
            self.wa_container.pack(fill="x", padx=20, pady=5, expand=False)
            self.wa_p_group.pack_forget()
            self.wa_s_group.pack_forget()

            portal_is_role = self.role_vars["Portal"].get()
            server_is_role = self.role_vars["Server"].get()

            if not portal_is_role and not server_is_role:
                self.wa_p_group.pack(fill="x", padx=10, pady=2)
                self.wa_s_group.pack(fill="x", padx=10, pady=2)
            else:
                if portal_is_role: self.wa_p_group.pack(fill="x", padx=10, pady=2)
                if server_is_role: self.wa_s_group.pack(fill="x", padx=10, pady=2)
        else:
            self.wa_container.pack_forget()
        
        if self.role_vars["DataStore"].get(): self.ds_container.pack(fill="x", padx=20, pady=5)
        else: self.ds_container.pack_forget()
        
        self.ssl_box.pack_forget()
        self.ssl_box.pack(fill="x", padx=20, pady=10)
        self.on_role_change()

    def add_ssl(self):
        row = SSLCertificateRow(self.ssl_box, self.remove_ssl)
        self.ssl_rows_list.append(row)
        self.add_ssl_btn.pack_forget(); self.add_ssl_btn.pack(pady=5, anchor="w")

    def remove_ssl(self, row):
        row.destroy(); self.ssl_rows_list.remove(row)

    def get_node_data(self):
        roles = [r for r, v in self.role_vars.items() if v.get()]
        node = {"NodeName": self.ent_name.get(), "Role": roles}
        
        if "DataStore" in roles:
            node["DataStoreTypes"] = [ds for ds, v in self.ds_vars.items() if v.get()]
            
        if "WebAdaptor" in roles:
            wa_list = []
            if self.wa_p_group.winfo_ismapped() and self.wa_p_ctx.get().strip():
                wa_list.append({
                    "Role": "Portal", "Context": self.wa_p_ctx.get().strip(),
                    "AdminAccessEnabled": self.wa_p_admin_var.get()
                })
            if self.wa_s_group.winfo_ismapped() and self.wa_s_ctx.get().strip():
                wa_list.append({
                    "Role": "Server", "Context": self.wa_s_ctx.get().strip(),
                    "AdminAccessEnabled": self.wa_s_admin_var.get()
                })
            if wa_list: node["WebAdaptorConfig"] = wa_list
                
        certs = [r.get_data() for r in self.ssl_rows_list if r.get_data()]
        if certs: node["SslCertificates"] = certs
        return node

class GlobalConfigPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="white", border_width=1, border_color="#cbd5e0")
        self.pack(fill="x", padx=15, pady=20)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Dodajemy "images" do ścieżki, a potem nazwę pliku
        icon_path = resource_path("tooltip.png")
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(script_dir, "tooltip.png")
            
            self.help_img = ctk.CTkImage(
                light_image=Image.open(img_path),
                size=(16, 16)
            )
        except Exception as e:
            print(f"Błąd wczytywania ikony: {e}")
            self.help_img = None # Jeśli nie ma pliku, nie wywali programu

        # 1. Inicjalizacja słowników na samym początku
        self.sections = {}
        self.vars = {}
        self.conditional_rows = {}
        self.containers = {} # Tu przechowujemy ramki dynamiczne (HA, Patche)

        # --- 1. BASE ---
        self._add_hr(self)
        self.sections["Base"] = self._create_section("Basic Configuration & Credentials")
        self._add_hr(self.sections["Base"])
        self._add_dropdown(self.sections["Base"], "Version", VERSIONS, "10.9.1")
        self._add_checkbox_row(self.sections["Base"], "IsHA", "Enable HA Architecture?", default=False, command=self.refresh_dynamic_layouts)
        self.credentials_frame = ctk.CTkFrame(self.sections["Base"], fg_color="transparent")
        self.credentials_frame.pack(fill="x")
        self._add_field(self.credentials_frame, "Service Account", "DOMAIN\\USER")
        self._add_field(self.credentials_frame, "Service Account Password", "", is_pass=True)
        self._add_field(self.credentials_frame, "ADService Account", "DOMAIN\\USER")
        self._add_field(self.credentials_frame, "ADService Account Password", "", is_pass=True)

        self.conditional_rows["PortalContext"] = self._add_conditional_field("Base", "PortalContext", "portal")
        self.conditional_rows["ServerContext"] = self._add_conditional_field("Base", "ServerContext", "arcgis")
        self.conditional_rows["ServerRole"] = self._add_conditional_dropdown("Base", "ServerRole", SERVER_ROLE_OPTIONS, "GeneralPurposeServer")
        self._add_hr(self)
        # --- 2. PORTAL ---
        self.sections["Portal"] = self._create_section("Global: Portal for ArcGIS")
        self._add_hr(self.sections["Portal"])
        self._add_checkbox_row(self.sections["Portal"], "Portal_IsSelfExtracting", "To Unpack?", default=False)
        self._add_field(self.sections["Portal"], "Path to Portal Installer", "C:\\Installation\\Software\\PortalForArcGIS\\Setup.exe")
        self._add_field(self.sections["Portal"], "Path to Portal Volume","")
        self._add_field(self.sections["Portal"], "Path to Portal License", "C:\\Installation\\License\\[PortalLicenseFileName]")
        self._add_field(self.sections["Portal"], "Portal Install Directory", "C:\\Program Files\\ArcGIS\\Portal")
        
        # --- SEKCJA PATCHY ---
        # Przypisujemy wiersz checkboxa jako kotwicę dla pól patchy
        self.portal_patch_anchor = self._add_checkbox_row(
            self.sections["Portal"], 
            "Portal_DoPatch",
            "Install Portal Patches?",
            default=False,
            command=self.refresh_dynamic_layouts # Zalecam używanie głównej funkcji odświeżania
        )
        
        # Kontener Patchy
        self.containers["Portal_Patches"] = ctk.CTkFrame(self.sections["Portal"], fg_color="transparent")
        self._add_field(self.containers["Portal_Patches"], "Portal Patches Directory", "C:\\Installation\\Patches\\Portal")
        self._add_field(self.containers["Portal_Patches"], "Portal Patches List", "Patch1.msp, Patch2.msp")
        
        # Kotwica dla HA (pola HA pojawią się pod ContentDir)
        self._add_field(self.sections["Portal"], "Portal Content Directory", "C:\\arcgisportal")
        self.portal_anchor = self._add_field(self.sections["Portal"], "Portal Content Location", "C:\\arcgisportal\\content")

        # Kontener HA
        self.containers["Portal_HA"] = ctk.CTkFrame(self.sections["Portal"], fg_color="transparent")
        self._add_field(self.containers["Portal_HA"], "Portal External LB", "") 
        self._add_field(self.containers["Portal_HA"], "Portal Internal LB", "") 
        self._add_field(self.containers["Portal_HA"], "Portal Internal LB Port", "7443")

        self._add_hr(self.sections["Portal"])
        # Podsekcja: Portal Admin Konto
        admin_subPortal = self._create_sub_section(self.sections["Portal"], "Portal Administrator Details")
        self._add_field(admin_subPortal, "Portal Username", "Imie Nazwisko")
        self._add_field(admin_subPortal, "Portal Admin User", "PortalCreator")
        self._add_field(admin_subPortal, "Portal Admin Password", "", is_pass=True)
        self._add_field(admin_subPortal, "Portal Admin Email", "admin@domain.local")
        self._add_hr(self.sections["Portal"])

        # --- 3. SERVER ---
        self.sections["Server"] = self._create_section("Global: ArcGIS Server")
        self._add_hr(self.sections["Server"])
        self._add_checkbox_row(self.sections["Server"], "Server_IsSelfExtracting", "To Unpack?", default=False)
        self._add_field(self.sections["Server"], "Path to Server Installer", "C:\\Installation\\Software\\ArcGISServer\\Setup.exe")
        self._add_field(self.sections["Server"], "Path to Server Volume","")
        self._add_field(self.sections["Server"], "Path to Server License", "C:\\Installation\\License\\[ServerLicenseFileName]")
        self._add_field(self.sections["Server"], "Server Install Directory", "C:\\Program Files\\ArcGIS\\Server")
        # Przypisujemy wiersz checkboxa jako kotwicę dla pól patchy
        self.server_patch_anchor = self._add_checkbox_row(
            self.sections["Server"], 
            "Server_DoPatch", 
            "Install Server Patches?", 
            default=False, 
            command=self.refresh_dynamic_layouts # Zalecam używanie głównej funkcji odświeżania
        )
        self.containers["Server_Patches"] = ctk.CTkFrame(self.sections["Server"], fg_color="transparent")
        self._add_field(self.containers["Server_Patches"], "Server Patches Directory", "C:\\Installation\\Patches\\Server")
        self._add_field(self.containers["Server_Patches"], "Server Patches List", "PatchS1.msp")
        self._add_field(self.sections["Server"], "Server Root Directory", "C:\\arcgisserver\\directories")
        self._add_field(self.sections["Server"], "Server Config Store", "C:\\arcgisserver\\config-store")
        
        # KOTWICA SERVERA
        self.server_anchor = self._add_field(self.sections["Server"], "Server Python Directory", "C:\\opt\\Python27")
        
        # Kontenery Servera
        self.containers["Server_HA"] = ctk.CTkFrame(self.sections["Server"], fg_color="transparent")
        self._add_field(self.containers["Server_HA"], "Server External LB", "") 
        self._add_field(self.containers["Server_HA"], "Server Installer LB", "") 
        self._add_field(self.containers["Server_HA"], "Server Installer LB Port", "6443")

        self._add_hr(self.sections["Server"])

        # Podsekcja: Dodatkowe komponenty serwera
        server_AddsComponents = self._create_sub_section(self.sections["Server"], "Additional Server Components")
        self._add_checkbox_row(server_AddsComponents, "Server_EnableArcMap", "Enable ArcMap Runtime?", default=True, help_text="Only available for 10.9.1. If you have another version, uncheck it.")

        self.server_dotnet_anchor = self._add_checkbox_row(
            server_AddsComponents, 
            "Server_EnableDotnet", 
            "Enable Dotnet Support?", 
            default=True, 
            command=self.refresh_dynamic_layouts
        )
        self.containers["Server_Dotnet"] = ctk.CTkFrame(server_AddsComponents, fg_color="transparent")
        self._add_field(self.containers["Server_Dotnet"], "Path to Server Dotnet", "C:\\Installation\\Software\\dotnet-hosting-8.0.0-win.exe")
        
        # Podsekcja: Server Admin Konto
        self._add_hr(self.sections["Server"])
        admin_subServer = self._create_sub_section(self.sections["Server"], "Server Administrator Details")
        self._add_field(admin_subServer, "Server Admin User", "siteadmin")
        self._add_field(admin_subServer, "Server Admin Password", "", is_pass=True)
        self._add_hr(self.sections["Server"])

        # --- 4. DATASTORE ---
        self.sections["DataStore"] = self._create_section("Global: DataStore")
        self._add_hr(self.sections["DataStore"])
        self._add_checkbox_row(self.sections["DataStore"], "DS_IsSelfExtracting", "To Unpack?", default=False)
        self._add_field(self.sections["DataStore"], "Path to Datestore Installer", "C:\\Installation\\Software\\ArcGISDataStore\\Setup.exe")
        
        # KOTWICA DATASTORE
        self.ds_anchor = self._add_field(self.sections["DataStore"], "Datestore Install Directory", "C:\\Program Files\\ArcGIS\\DataStore")
        
        self.datastore_patch_anchor = self._add_checkbox_row(
            self.sections["DataStore"], 
            "DS_DoPatch", 
            "Install Datestore patches?", 
            default=False, 
            command=self.refresh_dynamic_layouts # Zalecam używanie głównej funkcji odświeżania
        )

        self.containers["DS_Patches"] = ctk.CTkFrame(self.sections["DataStore"], fg_color="transparent")
        self._add_field(self.containers["DS_Patches"], "Datestore Patches Directory", "C:\\Installation\\Patches\\Datestore")
        self._add_field(self.containers["DS_Patches"], "Datestore Patches List", "DSPatch.msp")
        self._add_field(self.sections["DataStore"], "Datestore Content Directory", "C:\\arcgisdatastore")
        self._add_hr(self.sections["DataStore"])

        # --- 5. WEBADAPTOR ---
        self.sections["WebAdaptor"] = self._create_section("Global: Web Adaptor (IIS)")
        self._add_hr(self.sections["WebAdaptor"])
        self._add_checkbox_row(self.sections["WebAdaptor"], "WA_IsSelfExtracting", "To Unpack?", default=False)
        self._add_field(self.sections["WebAdaptor"], "Path to WebAdaptor Installer", "C:\\Installation\\Software\\WebAdaptorIIS\\Setup.exe")
        self._add_field(self.sections["WebAdaptor"], "Path to WebAdaptor Dotnet", "C:\\Installation\\Software\\dotnet-hosting-8.0.0-win.exe")
        self._add_field(self.sections["WebAdaptor"], "Path to WebAdaptor WebDeploy", "C:\\Installation\\Software\\webdeploy_amd64_pl-PL.msi")
        
        # --- PODSEKCJA: WEB ADAPTOR SETTINGS ---
        wa_sub = self._create_sub_section(self.sections["WebAdaptor"], "IIS & Web Adaptor Configuration")
        self._add_checkbox_row(wa_sub, "WA_AdminAccess", "Admin Access Enabled (Global)?", default=True)
        self._add_checkbox_row(wa_sub, "WA_OverrideHTTPS", "Override HTTPS Binding?", default=True)
        # self._add_field(wa_sub, "WA_WebSiteId", "1")
        self._add_hr(self.sections["WebAdaptor"])

        # --- 6. FEDERATION ---
        self.sections["Federation"] = self._create_section("Global: Federation")
        self._add_hr(self.sections["Federation"])
        self.fed_anchor = self._add_checkbox_row(
            self.sections["Federation"], 
            "DoFederate", 
            "Federate Portal & Server?", 
            default=False, 
            command=self.toggle_federation # Zalecam używanie głównej funkcji odświeżania
        )
        self._add_hr(self.sections["Federation"])
        self.fed_fields_frame = ctk.CTkFrame(self.sections["Federation"], fg_color="transparent")
        self._add_field(self.fed_fields_frame, "Portal Federation Hostname", "")
        self._add_field(self.fed_fields_frame, "Portal Federation Port", "443")
        self._add_field(self.fed_fields_frame, "Portal Federation Context", "portal")
        ctk.CTkLabel(self.fed_fields_frame, text="Portal Administrator:", font=("Segoe UI", 12, "bold"), text_color="black").pack(anchor="w", padx=20, pady=(10,0))
        self._add_field(self.fed_fields_frame, "Portal Federation Admin UserName", "PortalCreator")
        self._add_field(self.fed_fields_frame, "Portal Federation Admin Password", "", is_pass=True)
        ctk.CTkLabel(self.fed_fields_frame, text="Optional Server parameters:", font=("Segoe UI", 12, "bold"), text_color="black").pack(anchor="w", padx=20, pady=(15,0))
        self._add_field(self.fed_fields_frame, "Server Federation Hostname", "")
        self._add_field(self.fed_fields_frame, "Server Federation Port", "443")
        self._add_field(self.fed_fields_frame, "Server Federation Context", "arcgis")
        self._add_field(self.fed_fields_frame, "Server Federation Admin Hostname", "")
        self._add_field(self.fed_fields_frame, "Server Federation Admin URL Port", "6443")
        self._add_field(self.fed_fields_frame, "Server Federation Admin Context", "arcgis")
        self._add_hr(self.fed_fields_frame)
        author_label = ctk.CTkLabel(
            self, 
            text="by Damian Banach 2026", 
            font=("Segoe UI", 11, "italic"), 
            text_color="gray60" # Delikatny szary kolor, żeby nie rzucał się w oczy bardziej niż opcje
        )
        author_label.pack(side="bottom", pady=10)

    def _create_section(self, title):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame, text=title.upper(), font=("Segoe UI", 14, "bold"), text_color="#2e7d32").pack(anchor="w", padx=10, pady=(0, 10))
        return frame
    
    def _create_sub_section(self, parent_frame, title):
        sub_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        sub_frame.pack(fill="x", padx=10, pady=5)
        
        # Nagłówek podsekcji (mniejszy niż główny)
        ctk.CTkLabel(sub_frame, text=title.upper(), font=("Segoe UI", 12, "bold"), text_color="#2e7d32").pack(anchor="w", padx=10)
        
        return sub_frame

    def _add_field(self, parent_frame, var_key, default, is_pass=False):
        row = ctk.CTkFrame(parent_frame, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(row, text=var_key.replace("_", " ")+":", width=220, anchor="w", text_color="black").pack(side="left")
        v = ctk.StringVar(value=default); self.vars[var_key] = v
        # st = "disabled" if var_key == "Version" else "normal"
        ctk.CTkEntry(row, textvariable=v, fg_color="white", text_color="black", show="*" if is_pass else "", state="normal").pack(side="left", fill="x", expand=True)
        return row
    
    def _add_dropdown(self, parent_frame, var_key, options, default):
        row = ctk.CTkFrame(parent_frame, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(row, text=var_key.replace("_", " ")+":", width=220, anchor="w", text_color="black").pack(side="left")
        v = ctk.StringVar(value=default); self.vars[var_key] = v
        # state="readonly" blokuje wpisywanie tekstu, pozwala tylko wybrać z listy
        ctk.CTkComboBox(row, values=options, variable=v, fg_color="white", text_color="black", state="readonly").pack(side="left", fill="x", expand=True)
        return row

    def _add_conditional_field(self, section_key, var_key, default):
        row = ctk.CTkFrame(self.sections[section_key], fg_color="transparent")
        ctk.CTkLabel(row, text=var_key.replace("_", " ")+":", width=220, anchor="w", text_color="black").pack(side="left")
        v = ctk.StringVar(value=default); self.vars[var_key] = v
        ctk.CTkEntry(row, textvariable=v, fg_color="white", text_color="black").pack(side="left", fill="x", expand=True)
        return row

    def _add_conditional_dropdown(self, section_key, var_key, options, default):
        row = ctk.CTkFrame(self.sections[section_key], fg_color="transparent")
        ctk.CTkLabel(row, text=var_key.replace("_", " ")+":", width=220, anchor="w", text_color="black").pack(side="left")
        v = ctk.StringVar(value=default); self.vars[var_key] = v
        ctk.CTkComboBox(row, values=options, variable=v, fg_color="white", text_color="black", state="readonly").pack(side="left", fill="x", expand=True)
        return row
    
    def _add_checkbox_row(self, parent_frame, var_key, label_text, default=True, command=None, help_text=None):
        row = ctk.CTkFrame(parent_frame, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)
        
        # 1. Etykieta (po lewej)
        lbl = ctk.CTkLabel(row, text=label_text, width=220, anchor="w", text_color="black")
        lbl.pack(side="left")
        
        # 2. Zmienna i Checkbox
        v = ctk.BooleanVar(value=default)
        self.vars[var_key] = v 
        
        cb = ctk.CTkCheckBox(row, text="", variable=v, width=20, command=command)
        cb.pack(side="left") # Checkbox zostaje zaraz za etykietą
        
        # 3. Tooltip (po prawej stronie checkboxa)
        if help_text and self.help_img:
            help_icon = ctk.CTkLabel(
                row, 
                text="", 
                image=self.help_img, 
                cursor="question_arrow"
            )
            help_icon.pack(side="left", padx=10)
            
            # Aktywacja dymka z tekstem
            CTKTooltip(help_icon, help_text)
        
        return row
    
    def _add_hr(self, parent_frame):
        # Tworzymy ramkę o wysokości 2px, która udaje linię separatora
        line = ctk.CTkFrame(parent_frame, height=2, fg_color="#e2e8f0", border_width=0)
        line.pack(fill="x", padx=20, pady=15)

    # --- JEDNA FUNKCJA DO ZARZĄDZANIA UKŁADEM ---
    # To zapobiega błędom "window isn't packed"
    def refresh_dynamic_layouts(self):
        # 1. Reset (ukryj wszystko dynamiczne)
        self.containers["Portal_HA"].pack_forget()
        self.containers["Portal_Patches"].pack_forget()
        self.containers["Server_HA"].pack_forget()
        self.containers["Server_Patches"].pack_forget()
        self.containers["DS_Patches"].pack_forget()
        self.containers["Server_Dotnet"].pack_forget()

        # 2. Portal Logic
        # Zawsze zaczynamy od kotwicy
        target_portal = self.portal_anchor
        
        if self.vars["IsHA"].get():
            self.containers["Portal_HA"].pack(fill="x", after=target_portal)
            target_portal = self.containers["Portal_HA"] # Nowa kotwica to HA
            
        if self.vars["Portal_DoPatch"].get():
            self.containers["Portal_Patches"].pack(fill="x", after=self.portal_patch_anchor)
        
        # 3. Server Logic
        target_server = self.server_anchor
        
        if self.vars["IsHA"].get():
            self.containers["Server_HA"].pack(fill="x", after=target_server)
            target_server = self.containers["Server_HA"]
            
        if self.vars["Server_DoPatch"].get():
            self.containers["Server_Patches"].pack(fill="x", after=self.server_patch_anchor)

        if self.vars["Server_EnableDotnet"].get():
            self.containers["Server_Dotnet"].pack(fill="x", after=self.server_dotnet_anchor)

        # 4. DataStore Logic
        if self.vars["DS_DoPatch"].get():
            self.containers["DS_Patches"].pack(fill="x", after=self.datastore_patch_anchor)

    def toggle_server_dotnet(self):
        self.containers["Server_Dotnet"].pack_forget()
        # Jeśli checkbox jest zaznaczony
        if self.vars["Server_EnableDotnet"].get():
            self.containers["Server_Dotnet"].pack(fill="x", padx=10, pady=2)

    def toggle_federation(self):
        if self.vars["DoFederate"].get():
            self.fed_fields_frame.pack(fill="x", padx=0, pady=5)
        else:
            self.fed_fields_frame.pack_forget()

    # Te funkcje muszą zostać dla kompatybilności, ale przekierowują do nowej logiki
    def toggle_patches(self): self.refresh_dynamic_layouts()
    def toggle_ha(self): self.refresh_dynamic_layouts()

    def update_visibility(self, active_roles):
        if active_roles == {"WebAdaptor"}:
            self.credentials_frame.pack_forget()
        else:
            self.credentials_frame.pack(fill="x", after=self.sections["Base"].winfo_children()[2])

        for role in ["Portal", "Server", "DataStore", "WebAdaptor"]:
            if role in active_roles: self.sections[role].pack(fill="x", padx=10, pady=5)
            else: self.sections[role].pack_forget()

        if "Portal" in active_roles: self.conditional_rows["PortalContext"].pack(fill="x", padx=20, pady=2)
        else: self.conditional_rows["PortalContext"].pack_forget()
        
        if "Server" in active_roles:
            self.conditional_rows["ServerContext"].pack(fill="x", padx=20, pady=2)
            self.conditional_rows["ServerRole"].pack(fill="x", padx=20, pady=2)
            self.toggle_server_dotnet()
        else:
            self.conditional_rows["ServerContext"].pack_forget()
            self.conditional_rows["ServerRole"].pack_forget()
            self.containers["Server_Dotnet"].pack_forget()
            
        self.refresh_dynamic_layouts() # Główna aktualizacja układu

        self.sections["Federation"].pack_forget()
        if "Portal" in active_roles and "Server" in active_roles:
            self.sections["Federation"].pack(fill="x", padx=10, pady=5)
            self.toggle_federation()

    def get_config_data(self, active_roles):
        v = {k: (var.get() if hasattr(var, 'get') else var) for k, var in self.vars.items()}
        data = OrderedDict([("Version", v["Version"]), ("DownloadSetups", False)])
        if active_roles != {"WebAdaptor"}:
            data["Credentials"] = {
                "ServiceAccount": {"UserName": v["Service Account"], "Password": v["Service Account Password"], "IsDomainAccount": True, "IsMSAAccount": False},
                "ADServiceUser": {"UserName": v["ADService Account"], "Password": v["ADService Account Password"]}
            }
        if "Portal" in active_roles: data["PortalContext"] = v["PortalContext"]
        if "Server" in active_roles: data["ServerContext"] = v["ServerContext"]; data["ServerRole"] = v["ServerRole"]

        if "Portal" in active_roles:
            p_inst = {"Path": v["Path to Portal Installer"], "IsSelfExtracting": v["Portal_IsSelfExtracting"], "InstallDir": v["Portal Install Directory"], "ContentDir": v["Portal Content Directory"]}
            
            # VolumePaths (only if DownloadSetups = True and value provided)
            if v.get("Path to Portal Volume") and data.get("DownloadSetups"):
                p_inst["VolumePaths"] = [p.strip() for p in v["Path to Portal Volume"].split(",") if p.strip()]

            if v["Portal_DoPatch"]:
                p_inst["PatchesDir"] = v["Portal Patches Directory"]
                p_inst["PatchInstallDir"] = [p.strip() for p in v["Portal Patches List"].split(",") if p.strip()]
            pc = {"Installer": p_inst, "LicenseFilePath": v["Path to Portal License"], "PortalLicenseUserTypeId": "creatorUT", "PortalAdministrator": {"Fullname": v["Portal Username"], "UserName": v["Portal Admin User"], "Password": v["Portal Admin Password"], "Email": v["Portal Admin Email"], "SecurityQuestionIndex": 1, "SecurityAnswer": "123"}, "ContentDirectoryLocation": v["Portal Content Location"], "EnableAutomaticAccountCreation": True, "DefaultRoleForUser": "iAAAAAAAAAAAAAAA", "DefaultUserLicenseTypeIdForUser": "viewerUT", "EnableHSTS": True}
            
            if v.get("IsHA"):
                if v.get("Portal External LB"): pc["ExternalLoadBalancer"] = v["Portal External LB"]
                if v.get("Portal Internal LB"): pc["InternalLoadBalancer"] = v["Portal Internal LB"]
                try: lb_port = int(v.get("Portal Internal LB Port"))
                except: lb_port = 7443
                pc["InternalLoadBalancerPort"] = lb_port
            data["Portal"] = pc

        if "Server" in active_roles:
            s_inst = {"Path": v["Path to Server Installer"], "IsSelfExtracting": v["Server_IsSelfExtracting"], "InstallDir": v["Server Install Directory"], "InstallDirPython": v["Server Python Directory"], "EnableArcMapRuntime": v["Server_EnableArcMap"], "EnableDotnetSupport": v["Server_EnableDotnet"]}
            # VolumePaths (only if DownloadSetups = True and value provided)
            if v.get("Path to Server Volume") and data.get("DownloadSetups"):
                s_inst["VolumePaths"] = [
                    p.strip() for p in v["Path to Server Volume"].split(",") if p.strip()]
            if v["Server_EnableDotnet"]: s_inst["DotnetDesktopRuntimePath"] = v["Path to Server Dotnet"]
            if v["Server_DoPatch"]:
                s_inst["PatchesDir"] = v["Server Patches Directory"]
                s_inst["PatchInstallOrder"] = [p.strip() for p in v["Server Patches List"].split(",") if p.strip()]
            root = v["Server Root Directory"].rstrip("\\")
            sc = {"LicenseFilePath": v["Path to Server License"], "Installer": s_inst, "ServerDirectoriesRootLocation": root, "ConfigStoreLocation": v["Server Config Store"], "LocalRepositoryPath": "C:\\arcgisserver\\local", "ServerLogsLocation": "C:\\arcgisserver\\logs", "ServerDirectories": [{"name": "arcgiscache", "physicalPath": f"{root}\\arcgiscache", "directoryType": "CACHE", "cleanupMode": "NONE", "maxFileAge": 0}, {"name": "arcgisjobs", "physicalPath": f"{root}\\arcgisjobs", "directoryType": "JOBS", "cleanupMode": "TIME_ELAPSED_SINCE_LAST_MODIFIED", "maxFileAge": 360}, {"name": "arcgisoutput", "physicalPath": f"{root}\\arcgisoutput", "directoryType": "OUTPUT", "cleanupMode": "TIME_ELAPSED_SINCE_LAST_MODIFIED", "maxFileAge": 10}, {"name": "arcgissystem", "physicalPath": f"{root}\\arcgissystem", "directoryType": "SYSTEM", "cleanupMode": "NONE", "maxFileAge": 0}], "PrimarySiteAdmin": {"UserName": v["Server Admin User"], "Password": v["Server Admin Password"]}, "EnableHTTPSOnly": True}
            
            if v.get("IsHA"):
                if v.get("Server External LB"): sc["ExternalLoadBalancer"] = v["Server External LB"]
                if v.get("Server Installer LB"): sc["InternalLoadBalancer"] = v["Server Installer LB"]
                try: lb_port = int(v.get("Server Installer LB Port"))
                except: lb_port = 6443
                sc["InternalLoadBalancerPort"] = lb_port
            data["Server"] = sc
        
        if "DataStore" in active_roles:
            ds_inst = {"Path": v["Path to Datestore Installer"], "IsSelfExtracting": v["DS_IsSelfExtracting"], "InstallDir": v["Datestore Install Directory"]}
            if v["DS_DoPatch"]:
                ds_inst["PatchesDir"] = v["Datestore Patches Directory"]
                ds_inst["PatchInstallOrder"] = [p.strip() for p in v["Datestore Patches List"].split(",") if p.strip()]
            data["DataStore"] = {"ContentDirectoryLocation": v["Datestore Content Directory"], "EnableFailoverOnPrimaryStop": False, "EnablePointInTimeRecovery": False, "Installer": ds_inst}

        if "WebAdaptor" in active_roles:
            data["WebAdaptor"] = {"Installer": {"Path": v["Path to WebAdaptor Installer"], "IsSelfExtracting": v["WA_IsSelfExtracting"], "DotnetHostingBundlePath": v["Path to WebAdaptor Dotnet"], "WebDeployPath": v["Path to WebAdaptor WebDeploy"]}, "AdminAccessEnabled": v["WA_AdminAccess"], "OverrideHTTPSBinding": v["WA_OverrideHTTPS"]}

        if "Portal" in active_roles and "Server" in active_roles and v["DoFederate"]:
            fed = {"PortalHostName": v["Portal Federation Hostname"], "PortalPort": int(v["Portal Federation Port"] or 7443), "PortalContext": v["Portal Federation Context"], "PortalAdministrator": {"UserName": v["Portal Federation Admin UserName"], "Password": v["Portal Federation Admin Password"]}}
            for jk, vk in [("ServerHostName", "Server Federation Hostname"), ("ServerUrlPort", "Server Federation Port"), ("ServerContext", "Server Federation Context"), ("ServerAdminHostName", "Server Federation Admin Hostname"), ("ServerAdminUrlPort", "Server Federation Admin URL Port"), ("ServerAdminContext", "Server Federation Admin Context")]:
                val = v[vk].strip()
                if val: fed[jk] = int(val) if "Port" in jk and val.isdigit() else val
            data["Federation"] = fed
        return data

class ArcGISApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ArcGIS Deployment Generator Tool v1.5")
        self.geometry("820x800")
        self.scroll_canvas = ctk.CTkScrollableFrame(self, fg_color="#f1f5f9")
        self.scroll_canvas.pack(fill="both", expand=True)
        self.nodes = []
        self.btn_add_node = ctk.CTkButton(self.scroll_canvas, text="ADD NEXT NODE MACHINE", height=45, command=self.add_node)
        self.btn_add_node.pack(pady=20)
        self.global_panel = GlobalConfigPanel(self.scroll_canvas)
        self.btn_save = ctk.CTkButton(self.scroll_canvas, text="GENERATE JSON FILE", height=50, fg_color="#2e7d32", font=("Segoe UI", 14, "bold"), command=self.save_json)
        self.btn_save.pack(fill="x", padx=15, pady=30)
        self.add_node()

    def get_all_active_roles(self):
        active = set()
        for n in self.nodes:
            for r, v in n.role_vars.items():
                if v.get(): active.add(r)
        return active

    def on_role_update(self): self.global_panel.update_visibility(self.get_all_active_roles())

    def add_node(self):
        node = NodeFrame(self.scroll_canvas, len(self.nodes)+1, self.remove_node, self.on_role_update)
        self.nodes.append(node)
        self.btn_add_node.pack_forget(); self.global_panel.pack_forget(); self.btn_save.pack_forget()
        self.btn_add_node.pack(pady=20); self.global_panel.pack(fill="x", padx=15, pady=20); self.btn_save.pack(fill="x", padx=15, pady=30)
        self.on_role_update()

    def remove_node(self, node):
        if len(self.nodes) > 1: node.destroy(); self.nodes.remove(node); self.on_role_update()

    def save_json(self):
        # Parametr initialfile ustawia sugerowaną nazwę pliku
        path = filedialog.asksaveasfilename(
            initialfile=f"ArcGIS_Configuration_{(datetime.datetime.now()).strftime("%Y_%m_%d_%H%M")}.json",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Configuration As"
        )
        if path:
            data = OrderedDict([
                ("AllNodes", [n.get_node_data() for n in self.nodes]), 
                ("ConfigData", self.global_panel.get_config_data(self.get_all_active_roles()))
            ])
            try:
                with open(path, "w", encoding="utf-8") as f: 
                    json.dump(data, f, indent=4)
                messagebox.showinfo("Success", f"JSON FILE WAS GENERATED SUCCESSFULLY TO '{path}'")
            except Exception as e:
                messagebox.showerror("Error", f"FAILED TO SAVE FILE TO: {e}")

if __name__ == "__main__":
    ArcGISApp().mainloop()
