import customtkinter as ctk

class HomeScreen(ctk.CTkFrame):
    def __init__(self, master, on_select_staging, on_select_enterprise, on_select_pro, **kwargs):
        super().__init__(master, fg_color="#f8f7f4", **kwargs)
        
        # Nagłówek
        title = ctk.CTkLabel(
            self, text="ArcGIS - Asystent Wdrożenia", 
            font=("Segoe UI", 24, "bold"), text_color="#1e293b"
        )
        title.pack(pady=(40, 5))

        subtitle = ctk.CTkLabel(
            self, text="Wybierz moduł, z którego chcesz skorzystać:", 
            font=("Segoe UI", 13), text_color="#64748b"
        )
        subtitle.pack(pady=(0, 10))

        # Kontener na 3 kafelki
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(expand=True)

        # KAFELKA 1: Staging & Prep
        self._create_card(
            parent=cards_frame,
            title="Przygotowanie środowiska",
            description="Automatyczne pobieranie/kopiowanie plików z sieci przez PowerShell i autowykrywanie ścieżek, plików licencji i certyfikatów",
            button_text="Skonfiguruj środowisko",
            command=on_select_staging,
            color="#0057ff",
            hover_color="#0046D5"
        ).pack(side="left", padx=15, pady=10)

        # KAFELKA 2: Enterprise
        self._create_card(
            parent=cards_frame,
            title="ArcGIS Enterprise",
            description="Generowanie schematu JSON dla instalacji ArcGIS Enterprise:\nPortal, Server, DataStore oraz Web Adaptor",
            button_text="Generator Enterprise",
            command=on_select_enterprise,
            color="#0057ff",
            hover_color="#0046D5"
        ).pack(side="left", padx=15, pady=10)

        # KAFELKA 3: Pro
        self._create_card(
            parent=cards_frame,
            title="ArcGIS Pro",
            description="Generowanie schematu JSON dla instalacji ArcGIS Pro, patchy oraz wymaganych komponentów",
            button_text="Generator ArcGIS Pro",
            command=on_select_pro,
            color="#0057ff",
            hover_color="#0046D5"
        ).pack(side="left", padx=15, pady=10)

    def _create_card(self, parent, title, description, button_text, command, color, hover_color=None):
        card = ctk.CTkFrame(parent, fg_color="white", border_width=1, border_color="#cbd5e0", width=260, height=310)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card, text=title, font=("Segoe UI", 15, "bold"), 
            text_color="#0f172a", wraplength=230
        ).pack(pady=(20, 10), padx=10)

        ctk.CTkLabel(
            card, text=description, font=("Segoe UI", 11), 
            text_color="#475569", justify="center", wraplength=230
        ).pack(pady=(0, 15), padx=10, expand=True)

        ctk.CTkButton(
            card, text=button_text, fg_color=color, hover_color=hover_color,
            font=("Segoe UI", 12, "bold"), height=38, command=command
        ).pack(pady=(0, 20), padx=15, fill="x")

        return card