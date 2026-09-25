# global_config/main_panel.py
import os
from collections import OrderedDict
import customtkinter as ctk
from PIL import Image

from core import resource_path
from .base_section import BaseSectionFrame
from .portal_section import PortalSectionFrame
from .server_section import ServerSectionFrame
from .datastore_section import DataStoreSectionFrame
from .webadaptor_section import WebAdaptorSectionFrame
from .federation_section import FederationSectionFrame

class GlobalConfigPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="white", border_width=1, border_color="#cbd5e0", **kwargs)
        self.pack(fill="x", padx=15, pady=20)

        self.help_img = self._load_help_image()

        self.base_sec = BaseSectionFrame(self, help_img=self.help_img, on_ha_change=self.on_ha_toggle)
        self.portal_sec = PortalSectionFrame(self, help_img=self.help_img)
        self.server_sec = ServerSectionFrame(self, help_img=self.help_img)
        self.ds_sec = DataStoreSectionFrame(self, help_img=self.help_img)
        self.wa_sec = WebAdaptorSectionFrame(self, help_img=self.help_img)
        self.fed_sec = FederationSectionFrame(self, help_img=self.help_img)

    def _load_help_image(self):
        try:
            # Dodajemy folder "images" do ścieżki zasobu
            img_path = resource_path(os.path.join("images", "tooltip.png"))
            return ctk.CTkImage(light_image=Image.open(img_path), size=(16, 16))
        except Exception as e:
            print(f"Błąd wczytywania ikony: {e}")
            return None

    def on_ha_toggle(self, is_ha_enabled):
        self.refresh_dynamic_layouts()

    def refresh_dynamic_layouts(self):
        is_ha = self.base_sec.is_ha_enabled()
        self.portal_sec.refresh_layout(is_ha)
        self.server_sec.refresh_layout(is_ha)
        self.ds_sec.refresh_layout()

    def update_visibility(self, active_roles):
        self.base_sec.update_visibility(active_roles)

        sections_map = {
            "Portal": self.portal_sec,
            "Server": self.server_sec,
            "DataStore": self.ds_sec,
            "WebAdaptor": self.wa_sec
        }

        for role_name, frame in sections_map.items():
            if role_name in active_roles:
                frame.pack(fill="x", padx=10, pady=5)
            else:
                frame.pack_forget()

        self.refresh_dynamic_layouts()

        if "Portal" in active_roles and "Server" in active_roles:
            self.fed_sec.pack(fill="x", padx=10, pady=5)
            self.fed_sec.toggle_federation()
        else:
            self.fed_sec.pack_forget()

    def get_config_data(self, active_roles):
        data = OrderedDict()
        self.base_sec.populate_data(data, active_roles)

        is_ha = self.base_sec.is_ha_enabled()

        if "Portal" in active_roles:
            data["Portal"] = self.portal_sec.get_data(is_ha_global=is_ha, download_setups=data.get("DownloadSetups", False))

        if "Server" in active_roles:
            data["Server"] = self.server_sec.get_data(is_ha_global=is_ha, download_setups=data.get("DownloadSetups", False))

        if "DataStore" in active_roles:
            data["DataStore"] = self.ds_sec.get_data()

        if "WebAdaptor" in active_roles:
            data["WebAdaptor"] = self.wa_sec.get_data()

        if "Portal" in active_roles and "Server" in active_roles and self.fed_sec.is_federation_enabled():
            data["Federation"] = self.fed_sec.get_data()

        return data