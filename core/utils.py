import os
import sys
import customtkinter as ctk
from core.session import session

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def build_dsc_patch_config(component_key):
    """
    Zwraca słownik z PatchesDir i PatchInstallOrder dla podanego komponentu.
    Gdy brak patchy, zwraca pusty słownik {}.
    """
    patch_paths = session.get(component_key, [])
    
    if not patch_paths:
        return {}

    patches_dir = os.path.dirname(patch_paths[0])
    patch_order = [os.path.basename(p) for p in patch_paths]

    return {
        "PatchesDir": patches_dir,
        "PatchInstallOrder": patch_order
    }

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