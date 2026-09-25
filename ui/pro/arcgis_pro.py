# arcgis_pro.py
import datetime
import json
from collections import OrderedDict
import customtkinter as ctk
from tkinter import filedialog, messagebox
from .pro_config import ProConfigPanel
import socket

class ProNodeFrame(ctk.CTkFrame):
    """Lekka ramka reprezentująca maszynę docelową pod instalację ArcGIS Pro."""
    def __init__(self, master, index, on_remove, **kwargs):
        super().__init__(master, fg_color="#ffffff", border_width=1, border_color="#cbd5e0", **kwargs)
        self.pack(fill="x", pady=5, padx=15)

        fqdn = socket.getfqdn()
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(header, text=f"MASZYNA #{index}", font=("Segoe UI", 14, "bold"), text_color="black").pack(side="left")
        ctk.CTkButton(header, text="Usuń", width=80, fg_color="#dc3545", hover_color="#c82333", command=lambda: on_remove(self)).pack(side="right")

        fqdn_f = ctk.CTkFrame(self, fg_color="transparent")
        fqdn_f.pack(fill="x", padx=15, pady=(0, 10))
        ctk.CTkLabel(fqdn_f, text="Nazwa maszyny / FQDN", width=230, anchor="w", text_color="black").pack(side="left")
        self.ent_name = ctk.CTkEntry(fqdn_f, text_color="black", fg_color="white")
        self.ent_name.pack(side="left", fill="x", expand=True)
        self.ent_name.insert(0, fqdn)

    def get_node_data(self):
        return {
            "NodeName": self.ent_name.get().strip(),
            "Role": ["Pro"]
        }


class ArcGISProScreen(ctk.CTkFrame):
    def __init__(self, master, on_back, **kwargs):
        super().__init__(master, fg_color="#f1f5f9", **kwargs)
        self.on_back = on_back

        # --- Górny Pasek Nawigacyjny ---
        top_bar = ctk.CTkFrame(self, fg_color="#f8f7f4", height=50, corner_radius=0)
        top_bar.pack(fill="x", side="top")

        btn_back = ctk.CTkButton(
            top_bar, text="Powrót do menu", width=140, 
            fg_color="#0057ff", hover_color="#0046D5",
            font=("Segoe UI", 12, "bold"), command=self.on_back
        )
        btn_back.pack(side="left", padx=15, pady=10)

        ctk.CTkLabel(
            top_bar, text="Generator Konfiguracji: ArcGIS Pro", 
            font=("Segoe UI", 14, "bold"), text_color="#000000"
        ).pack(side="left", padx=10)

        # --- Obszar Przewijany ---
        self.scroll_canvas = ctk.CTkScrollableFrame(self, fg_color="#f8f7f4")
        self.scroll_canvas.pack(fill="both", expand=True)

        self.nodes = []

        self.btn_add_node = ctk.CTkButton(
            self.scroll_canvas, text="Dodaj maszynę", 
            height=40, fg_color="#10b981", hover_color="#059669", 
            command=self.add_node
        )
        self.btn_add_node.pack(pady=15)

        # Panel z opcjami konfiguracyjnymi ArcGIS Pro
        self.pro_panel = ProConfigPanel(self.scroll_canvas)

        # Przycisk Zapisz
        self.btn_save = ctk.CTkButton(
            self.scroll_canvas, text="WYGENERUJ JSON", 
            height=50, fg_color="#0057ff", hover_color="#0046D5",
            font=("Segoe UI", 14, "bold"), command=self.save_json
        )
        self.btn_save.pack(fill="x", padx=15, pady=25)

        # Inicjalizacja pierwszej maszyny
        self.add_node()

    def add_node(self):
        node = ProNodeFrame(self.scroll_canvas, len(self.nodes) + 1, self.remove_node)
        self.nodes.append(node)

        # Przebudowa widoku w celu zachowania kolejności
        self.btn_add_node.pack_forget()
        self.pro_panel.pack_forget()
        self.btn_save.pack_forget()

        self.btn_add_node.pack(pady=15)
        self.pro_panel.pack(fill="x", padx=15, pady=15)
        self.btn_save.pack(fill="x", padx=15, pady=25)

    def remove_node(self, node):
        if len(self.nodes) > 1:
            node.destroy()
            self.nodes.remove(node)

    def save_json(self):
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H%M")
        path = filedialog.asksaveasfilename(
            initialfile=f"ArcGIS_Pro_Configuration_{timestamp}.json",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Zapisz konfigurację jako"
        )
        if path:
            data = OrderedDict([
                ("AllNodes", [n.get_node_data() for n in self.nodes]),
                ("ConfigData", self.pro_panel.get_config_data())
            ])
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                messagebox.showinfo("Success", f"Plik JSON został pomyślnie wygenerowany do\n'{path}'")
            except Exception as e:
                messagebox.showerror("Error", f"Nie udało się zapisać pliku {e}")