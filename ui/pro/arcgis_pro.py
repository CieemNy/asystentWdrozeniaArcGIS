import socket
import customtkinter as ctk

from ..components.base_config_screen import BaseConfigScreen
from .pro_config.pro_panel import ProConfigPanel


class ProNodeFrame(ctk.CTkFrame):
    """Ramka reprezentująca maszynę docelową pod instalację ArcGIS Pro."""

    def __init__(self, master, index, on_remove, **kwargs):
        super().__init__(master, fg_color="#ffffff", border_width=1, border_color="#cbd5e0", **kwargs)
        self.pack(fill="x", pady=5, padx=15)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            header, text=f"MASZYNA #{index}",
            font=("Segoe UI", 14, "bold"), text_color="black"
        ).pack(side="left")

        ctk.CTkButton(
            header, text="Usuń", width=80,
            fg_color="#dc3545", hover_color="#c82333",
            command=lambda: on_remove(self)
        ).pack(side="right")

        fqdn_frame = ctk.CTkFrame(self, fg_color="transparent")
        fqdn_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(
            fqdn_frame, text="Nazwa maszyny / FQDN",
            width=230, anchor="w", text_color="black"
        ).pack(side="left")

        self.ent_name = ctk.CTkEntry(fqdn_frame, text_color="black", fg_color="white")
        self.ent_name.pack(side="left", fill="x", expand=True)
        self.ent_name.insert(0, socket.getfqdn())

    def get_node_data(self):
        return {"NodeName": self.ent_name.get().strip(), "Role": ["Pro"]}


class ArcGISProScreen(BaseConfigScreen):
    def __init__(self, master, on_back, **kwargs):
        super().__init__(
            master,
            on_back,
            title="Generator Konfiguracji: ArcGIS Pro",
            filename_prefix="ArcGIS_Pro_Configuration",
            add_button_height=40,
            add_button_pady=15,
            panel_pady=15,
            save_pady=25,
            title_color="#000000",
            **kwargs
        )

    @property
    def pro_panel(self):
        return self.config_panel

    def create_config_panel(self, parent):
        return ProConfigPanel(parent)

    def create_node(self, index):
        return ProNodeFrame(self.scroll_canvas, index, self.remove_node)

    def get_config_data(self):
        return self.config_panel.get_config_data()