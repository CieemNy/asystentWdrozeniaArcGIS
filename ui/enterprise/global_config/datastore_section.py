import customtkinter as ctk
from core import session
from core.utils import build_dsc_patch_config

class DataStoreSectionFrame(ctk.CTkFrame):
    def __init__(self, master, help_img=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.help_img = help_img
        self.vars = {}
        self._build_ui()

    def _build_ui(self):
        label_frame = ctk.CTkFrame(
            self, 
            fg_color="#f8f9fa",
            border_color="#dee2e6"
        )
        label_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            label_frame, 
            text="Konfigurator ArcGIS Datastore", 
            font=("Segoe UI", 15, "bold"), 
            fg_color="#f8f7f4"
        ).pack(fill="x", anchor="w")

        datastore_installer = session.get("datastore_installer", "C:\\Installation\\Software\\ArcGISDataStore\\Setup.exe")
        patch_cfg = build_dsc_patch_config("datastore_patches")
        
        has_patches = bool(patch_cfg)
        default_patch_dir = patch_cfg.get("PatchesDir", "C:\\Installation\\Patches\\Datestore")
        default_patch_list = ", ".join(patch_cfg.get("PatchInstallOrder", [])) if has_patches else "patch1.msp"

        self._add_field("Path to Datestore Installer", "Ścieżka do instalki ArcGIS Datastore", datastore_installer)
        self._add_checkbox("DS_IsSelfExtracting", "Do rozpakowania?", default=False)
        self.ds_anchor = self._add_field("Datestore Install Directory", "Katalog instalacji", "C:\\Program Files\\ArcGIS\\DataStore")
        self._add_field("Datestore Content Directory", "Katalog zawartości ArcGIS Datastore", "C:\\arcgisdatastore")

        self.datastore_patch_anchor = self._add_checkbox(
            "DS_DoPatch", 
            "Zainstalować patche?", 
            default=False,
            command=self.toggle_patches
        )

        self.patches_container = ctk.CTkFrame(self, fg_color="transparent")
        self._add_field_to_frame(self.patches_container, "Datestore Patches Directory", "Katalog patchy ArcGIS Datastore", default_patch_dir)
        self._add_field_to_frame(self.patches_container, "Datestore Patches List", "Lista patchy ArcGIS Datastore", default_patch_list)

    def _add_field(self, var_key, label_text, default, is_pass=False):
        return self._add_field_to_frame(self, var_key, label_text, default, is_pass)

    def _add_field_to_frame(self, parent_frame, var_key, label_text, default, is_pass=False):
        row = ctk.CTkFrame(parent_frame, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(row, text=label_text, width=220, anchor="w", text_color="black").pack(side="left")
        v = ctk.StringVar(value=default)
        self.vars[var_key] = v
        ctk.CTkEntry(row, textvariable=v, fg_color="white", text_color="black", show="*" if is_pass else "").pack(side="left", fill="x", expand=True)
        return row

    def _add_checkbox(self, var_key, label_text, default=True, command=None):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(row, text=label_text, width=220, anchor="w", text_color="black").pack(side="left")
        v = ctk.BooleanVar(value=default)
        self.vars[var_key] = v
        cb = ctk.CTkCheckBox(row, text="", variable=v, width=20, command=command)
        cb.pack(side="left")
        return row

    def _add_hr(self):
        line = ctk.CTkFrame(self, height=2, fg_color="#e2e8f0", border_width=0)
        line.pack(fill="x", padx=20, pady=15)

    def toggle_patches(self):
        if self.vars["DS_DoPatch"].get():
            self.patches_container.pack(fill="x", after=self.datastore_patch_anchor)
        else:
            self.patches_container.pack_forget()

    def refresh_layout(self):
        self.toggle_patches()

    def get_data(self):
        v = {k: var.get() for k, var in self.vars.items()}
        
        ds_inst = {
            "Path": v["Path to Datestore Installer"], 
            "IsSelfExtracting": v["DS_IsSelfExtracting"], 
            "InstallDir": v["Datestore Install Directory"]
        }

        if v["DS_DoPatch"]:
            ds_inst["PatchesDir"] = v["Datestore Patches Directory"]
            ds_inst["PatchInstallOrder"] = [p.strip() for p in v["Datestore Patches List"].split(",") if p.strip()]

        return {
            "ContentDirectoryLocation": v["Datestore Content Directory"], 
            "EnableFailoverOnPrimaryStop": False, 
            "EnablePointInTimeRecovery": False, 
            "Installer": ds_inst
        }