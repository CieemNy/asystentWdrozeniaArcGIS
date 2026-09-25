import sys
import os
import customtkinter as ctk
from ui.home_screen import HomeScreen
from ui.enterprise.arcgis_enterprise import EnterpriseScreen
from ui.pro.arcgis_pro import ArcGISProScreen
from ui.staging import StagingScreen
from ui.components import FooterFrame

# Funkcja pomocnicza do bezpiecznego wczytywania ścieżek zasobów
def get_resource_path(relative_path: str) -> str:
    """Zwraca bezwzględną ścieżkę do pliku (działa w kodzie oraz po skompilowaniu w .exe)"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ArcGIS - Asystent Wdrożenia v2.0")

        # --- USTAWIANIE IKONY OKNA ---
        icon_path = get_resource_path(os.path.join("images", "app_icon.ico"))
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        # Wyśrodkowanie okna na ekranie (szerokość: 950, wysokość: 800)
        self.center_window(950, 800)

        # Inicjalizacja i przypięcie stopki
        self.footer = FooterFrame(self, app_name="ArcGIS Asystent Wdrożenia", version="2.0")
        self.footer.pack(side="bottom", fill="x")

        self.current_screen = None
        self.show_home_screen()

    def center_window(self, width: int, height: int):
        """Oblicza pozycję środka ekranu i ustawia rozdzielczość okna."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")

    def clear_screen(self):
        if self.current_screen is not None:
            self.current_screen.destroy()
            self.current_screen = None

    def show_home_screen(self):
        self.clear_screen()
        self.current_screen = HomeScreen(
            self, 
            on_select_staging=self.show_staging_screen,
            on_select_enterprise=self.show_enterprise_screen,
            on_select_pro=self.show_pro_screen
        )
        self.current_screen.pack(side="top", fill="both", expand=True)

    def show_staging_screen(self):
        self.clear_screen()
        self.current_screen = StagingScreen(self, on_back=self.show_home_screen)
        self.current_screen.pack(side="top", fill="both", expand=True)

    def show_enterprise_screen(self):
        self.clear_screen()
        self.current_screen = EnterpriseScreen(self, on_back=self.show_home_screen)
        self.current_screen.pack(side="top", fill="both", expand=True)

    def show_pro_screen(self):
        self.clear_screen()
        self.current_screen = ArcGISProScreen(self, on_back=self.show_home_screen)
        self.current_screen.pack(side="top", fill="both", expand=True)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()