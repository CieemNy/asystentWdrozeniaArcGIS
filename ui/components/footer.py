# ui/components/footer.py
import customtkinter as ctk

class FooterFrame(ctk.CTkFrame):
    def __init__(self, master, app_name="ArcGIS Configurator", version="1.0.0", **kwargs):
        super().__init__(
            master, 
            fg_color="#f8f7f4", 
            border_color="#dee2e6", 
            border_width=1, 
            corner_radius=0,
            height=32,
            **kwargs
        )
        self.app_name = app_name
        self.version = version
        self._build_ui()

    def _build_ui(self):
        self.lbl_left = ctk.CTkLabel(
            self, 
            text=f"© 2026 {self.app_name} by Damian Banach", 
            font=("Segoe UI", 11), 
            text_color="#64748b"
        )
        self.lbl_left.pack(side="left", padx=15, pady=4)

        self.lbl_status = ctk.CTkLabel(
            self, 
            text="Apator Rector", 
            font=("Segoe UI", 11, "italic"), 
            text_color="#475569"
        )
        self.lbl_status.pack(side="left", expand=True, pady=4)

        self.lbl_version = ctk.CTkLabel(
            self, 
            text=f"v{self.version}", 
            font=("Segoe UI", 11, "bold"), 
            text_color="#64748b"
        )
        self.lbl_version.pack(side="right", padx=15, pady=4)

    def set_status(self, text: str, color: str = "#475569"):
        self.lbl_status.configure(text=text, text_color=color)