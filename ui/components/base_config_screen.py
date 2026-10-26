import datetime
import json
from collections import OrderedDict
from tkinter import filedialog, messagebox

import customtkinter as ctk


class BaseConfigScreen(ctk.CTkFrame):
    """Wspólna obsługa ekranów konfiguracji ArcGIS."""

    def __init__(self, master, on_back, title, filename_prefix, add_button_height=45, add_button_pady=20, panel_pady=20, save_pady=30, title_color="#0f172a", **kwargs):
        super().__init__(master, fg_color="#f1f5f9", **kwargs)
        self.on_back = on_back
        self.filename_prefix = filename_prefix
        self.add_button_pady = add_button_pady
        self.panel_pady = panel_pady
        self.save_pady = save_pady
        self.nodes = []

        top_bar = ctk.CTkFrame(self, fg_color="#f8f7f4", height=50, corner_radius=0)
        top_bar.pack(fill="x", side="top")

        ctk.CTkButton(
            top_bar, text="Powrót do menu", width=140,
            fg_color="#0057ff", hover_color="#0046D5",
            font=("Segoe UI", 12, "bold"), command=self.on_back
        ).pack(side="left", padx=15, pady=10)

        ctk.CTkLabel(
            top_bar, text=title, font=("Segoe UI", 14, "bold"), text_color=title_color
        ).pack(side="left", padx=10)

        self.scroll_canvas = ctk.CTkScrollableFrame(self, fg_color="#f8f7f4")
        self.scroll_canvas.pack(fill="both", expand=True)

        self.btn_add_node = ctk.CTkButton(
            self.scroll_canvas, text="Dodaj maszynę", height=add_button_height,
            fg_color="#10b981", hover_color="#059669", command=self.add_node
        )
        self.btn_add_node.pack(pady=self.add_button_pady)

        self.config_panel = self.create_config_panel(self.scroll_canvas)

        self.btn_save = ctk.CTkButton(
            self.scroll_canvas, text="WYGENERUJ JSON", height=50,
            fg_color="#0057ff", hover_color="#0046D5",
            font=("Segoe UI", 14, "bold"), command=self.save_json
        )
        self.btn_save.pack(fill="x", padx=15, pady=self.save_pady)

        self.add_node()

    def create_config_panel(self, parent):
        raise NotImplementedError

    def create_node(self, index):
        raise NotImplementedError

    def get_config_data(self):
        raise NotImplementedError

    def on_nodes_changed(self):
        """Hook dla ekranów, które muszą odświeżyć zależną konfigurację."""

    def add_node(self):
        node = self.create_node(len(self.nodes) + 1)
        self.nodes.append(node)
        self._reorder_content()
        self.on_nodes_changed()

    def remove_node(self, node):
        if len(self.nodes) > 1:
            node.destroy()
            self.nodes.remove(node)
            self.on_nodes_changed()

    def _reorder_content(self):
        self.btn_add_node.pack_forget()
        self.config_panel.pack_forget()
        self.btn_save.pack_forget()

        self.btn_add_node.pack(pady=self.add_button_pady)
        self.config_panel.pack(fill="x", padx=15, pady=self.panel_pady)
        self.btn_save.pack(fill="x", padx=15, pady=self.save_pady)

    def save_json(self):
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H%M")
        path = filedialog.asksaveasfilename(
            initialfile=f"{self.filename_prefix}_{timestamp}.json",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Zapisz konfigurację jako"
        )
        if not path:
            return

        data = OrderedDict([
            ("AllNodes", [node.get_node_data() for node in self.nodes]),
            ("ConfigData", self.get_config_data())
        ])

        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
            messagebox.showinfo("Success", f"Plik JSON został pomyślnie wygenerowany do\n'{path}'")
        except Exception as exc:
            messagebox.showerror("Error", f"Nie udało się zapisać pliku: {exc}")
