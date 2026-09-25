# arcgis_enterprise.py
import datetime
import json
from collections import OrderedDict
import customtkinter as ctk
from tkinter import filedialog, messagebox

from ..components import NodeFrame
from .global_config import GlobalConfigPanel

class EnterpriseScreen(ctk.CTkFrame):
    def __init__(self, master, on_back, **kwargs):
        super().__init__(master, fg_color="#f1f5f9", **kwargs)
        self.on_back = on_back

        # --- 1. Górny Pasek Nawigacyjny ---
        top_bar = ctk.CTkFrame(self, fg_color="#f8f7f4", height=50, corner_radius=0)
        top_bar.pack(fill="x", side="top")

        btn_back = ctk.CTkButton(
            top_bar, 
            text="Powrót do menu", 
            width=140, 
            fg_color="#0057ff",
            hover_color="#0046D5",
            font=("Segoe UI", 12, "bold"),
            command=self.on_back
        )
        btn_back.pack(side="left", padx=15, pady=10)

        title_lbl = ctk.CTkLabel(
            top_bar, 
            text="Generator Konfiguracji: ArcGIS Enterprise", 
            font=("Segoe UI", 14, "bold"), 
            text_color="#0f172a"
        )
        title_lbl.pack(side="left", padx=10)

        # --- 2. Kontener Przewijany ---
        self.scroll_canvas = ctk.CTkScrollableFrame(self, fg_color="#f8f7f4")
        self.scroll_canvas.pack(fill="both", expand=True)

        self.nodes = []

        # Przycisk dodawania nowej maszyny
        self.btn_add_node = ctk.CTkButton(
            self.scroll_canvas, 
            text="Dodaj maszynę", 
            height=45,
            fg_color="#10b981",
            hover_color="#059669", 
            command=self.add_node
        )
        self.btn_add_node.pack(pady=20)

        # Panel z opcjami globalnymi
        self.global_panel = GlobalConfigPanel(self.scroll_canvas)

        # Przycisk generowania pliku JSON
        self.btn_save = ctk.CTkButton(
            self.scroll_canvas, 
            text="WYGENERUJ JSON", 
            height=50, 
            fg_color="#0057ff",
            hover_color="#0046D5",
            font=("Segoe UI", 14, "bold"), 
            command=self.save_json
        )
        self.btn_save.pack(fill="x", padx=15, pady=30)

        # Inicjalizacja pierwszej maszyny
        self.add_node()

    def get_all_active_roles(self):
        active = set()
        for n in self.nodes:
            for r, v in n.role_vars.items():
                if v.get(): 
                    active.add(r)
        return active

    def on_role_update(self): 
        self.global_panel.update_visibility(self.get_all_active_roles())

    def add_node(self):
        node = NodeFrame(self.scroll_canvas, len(self.nodes) + 1, self.remove_node, self.on_role_update)
        self.nodes.append(node)
        
        # Przeładowanie kolejności elementów w widoku
        self.btn_add_node.pack_forget()
        self.global_panel.pack_forget()
        self.btn_save.pack_forget()
        
        self.btn_add_node.pack(pady=20)
        self.global_panel.pack(fill="x", padx=15, pady=20)
        self.btn_save.pack(fill="x", padx=15, pady=30)
        
        self.on_role_update()

    def remove_node(self, node):
        if len(self.nodes) > 1: 
            node.destroy()
            self.nodes.remove(node)
            self.on_role_update()

    def save_json(self):
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H%M")
        path = filedialog.asksaveasfilename(
            initialfile=f"ArcGIS_Enterprise_Configuration_{timestamp}.json",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Zapisz konfigurację jako"
        )
        if path:
            data = OrderedDict([
                ("AllNodes", [n.get_node_data() for n in self.nodes]), 
                ("ConfigData", self.global_panel.get_config_data(self.get_all_active_roles()))
            ])
            try:
                with open(path, "w", encoding="utf-8") as f: 
                    json.dump(data, f, indent=4)
                messagebox.showinfo("Success", f"Plik JSON został pomyślnie wygenerowany do\n'{path}'")
            except Exception as e:
                messagebox.showerror("Error", f"Nie udało się zapisać pliku: {e}")