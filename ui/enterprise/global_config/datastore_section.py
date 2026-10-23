import customtkinter as ctk
from core import session
from core.utils import build_dsc_patch_config
from ui.components.form_fields import FormFieldMixin

class DataStoreSectionFrame(FormFieldMixin, ctk.CTkFrame):
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
            fg_color="#f8f7f4",
            text_color="#000000"
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
        self.datastore_patch_anchor = self._add_checkbox("DS_DoPatch", "Zainstalować patche?", default=False, command=lambda: self._toggle_container("DS_DoPatch", self.patches_container, self.datastore_patch_anchor))
        self.patches_container = ctk.CTkFrame(self, fg_color="transparent")
        self._add_field_to_frame(self.patches_container, "Datestore Patches Directory", "Katalog patchy ArcGIS Datastore", default_patch_dir)
        self._add_field_to_frame(self.patches_container, "Datestore Patches List", "Lista patchy ArcGIS Datastore", default_patch_list)

    def refresh_layout(self):
        self._toggle_container("DS_DoPatch", self.patches_container, self.datastore_patch_anchor)

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