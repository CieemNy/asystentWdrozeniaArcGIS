import customtkinter as ctk
from config import ROLES, DS_TYPES, SSL_TARGETS
from core.session import session
import socket

class SSLCertificateRow(ctk.CTkFrame):
    def __init__(self, master, on_remove, default_path="", default_targets=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#f8f7f4", border_width=1, border_color="#dee2e6")
        self.pack(fill="x", pady=0, padx=0)

        fqdn = socket.getfqdn()
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(header, text="Konfiguracja certyfikatu", font=("Segoe UI", 12, "bold"), text_color="#000000").pack(side="left")
        ctk.CTkButton(header, text="Usuń", width=60, height=22, fg_color="#dc3545", hover_color="#c82333", command=lambda: on_remove(self)).pack(side="right")

        self.ents = {}
        fields = [("Ścieżka do certyfikatu", "path"), ("Hasło certyfikatu", "pass"), ("Nazwa maszyny / FQDN", "cname")]
        for lbl, key in fields:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=lbl, width=220, anchor="w", text_color="black").pack(side="left")
            entry = ctk.CTkEntry(row, height=28, text_color="black", fg_color="white", show="*" if "pass" in key else "")
            entry.pack(side="left", fill="x", expand=True)
            self.ents[key] = entry
        
        self.ents["cname"].insert(0, fqdn)

        # Wypełnienie ścieżki z sesji, jeśli została przekazana
        if default_path:
            self.ents["path"].insert(0, default_path)

        target_f = ctk.CTkFrame(self, fg_color="transparent")
        target_f.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(target_f, text="Przeznaczenie", text_color="black", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0,10))
        
        self.target_vars = {t: ctk.BooleanVar() for t in SSL_TARGETS}
        for t in SSL_TARGETS:
            chk = ctk.CTkCheckBox(target_f, text=t, variable=self.target_vars[t], text_color="black", checkbox_width=18)
            chk.pack(side="left", padx=5)
            # Automatyczne zaznaczenie checkboxów Target zgadzających się z rolami maszyny
            if default_targets and t in default_targets:
                self.target_vars[t].set(True)

    def get_data(self):
        p = self.ents["path"].get().strip()
        if not p: return None
        return {
            "Path": p, 
            "Password": self.ents["pass"].get(), 
            "CNameFQDN": self.ents["cname"].get(),
            "Target": [t for t, v in self.target_vars.items() if v.get()]
        }


class NodeFrame(ctk.CTkFrame):
    def __init__(self, master, index, on_remove, on_role_change, **kwargs):
        super().__init__(master, **kwargs)
        self.on_role_change = on_role_change
        self.configure(fg_color="#ffffff", border_width=1, border_color="#cbd5e0")
        self.pack(fill="x", pady=10, padx=15)

        fqdn = socket.getfqdn()
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(header, text=f"Maszyna #{index}", font=("Segoe UI", 16, "bold"), text_color="black").pack(side="left")
        ctk.CTkButton(header, text="Usuń", width=120, fg_color="#dc3545", hover_color="#c82333", command=lambda: on_remove(self)).pack(side="right")

        fqdn_f = ctk.CTkFrame(self, fg_color="transparent")
        fqdn_f.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(fqdn_f, text="Nazwa maszyny / FQDN", width=240, anchor="w", text_color="black").pack(side="left")
        self.ent_name = ctk.CTkEntry(fqdn_f, text_color="black", fg_color="white")
        self.ent_name.pack(side="left", fill="x", expand=True)
        self.ent_name.insert(0, fqdn)

        role_f = ctk.CTkFrame(self, fg_color="transparent")
        role_f.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(role_f, text="Role:", width=120, anchor="w", text_color="black").pack(side="left")
        self.role_vars = {r: ctk.BooleanVar() for r in ROLES}
        for r in ROLES:
            ctk.CTkCheckBox(role_f, text=r, variable=self.role_vars[r], command=self.refresh_ui, text_color="black", checkbox_width=20).pack(side="left", padx=10)

        # --- SEKCJA WEBADAPTOR (KOMPAKTOWA) ---
        self.wa_container = ctk.CTkFrame(self, fg_color="#f8f7f4", border_width=1, border_color="#e2e8f0")
        ctk.CTkLabel(self.wa_container, text="Konfiguracja WebAdaptor", font=("Segoe UI", 11, "bold"), text_color="black").pack(padx=10, anchor="w", pady=5)
        
        wa_rows = ctk.CTkFrame(self.wa_container, fg_color="transparent")
        wa_rows.pack(fill="x", padx=10, pady=(0, 5))

        def create_wa_group(master, role_name, default_ctx):
            container = ctk.CTkFrame(master, fg_color="transparent")
            ctk.CTkLabel(container, text=f"{role_name} Kontekst", font=("Segoe UI", 11, "bold"), text_color="black", width=110, anchor="w").pack(side="left", padx=(0, 5))
            ctx_ent = ctk.CTkEntry(container, width=100, fg_color="white", text_color="black")
            ctx_ent.insert(0, default_ctx)
            ctx_ent.pack(side="left", padx=2)
            admin_var = ctk.BooleanVar(value=False)
            admin_group = ctk.CTkFrame(container, fg_color="transparent")
            admin_group.pack(side="left", padx=10)
            ctk.CTkLabel(admin_group, text="Dostęp administracyjny", font=("Segoe UI", 11), text_color="black").pack(side="left", padx=(0, 5))
            admin_check = ctk.CTkCheckBox(admin_group, text="", variable=admin_var, checkbox_width=16, width=16)
            admin_check.pack(side="left")
            return container, ctx_ent, admin_var

        self.wa_p_group, self.wa_p_ctx, self.wa_p_admin_var = create_wa_group(wa_rows, "Portal", "portal")
        self.wa_s_group, self.wa_s_ctx, self.wa_s_admin_var = create_wa_group(wa_rows, "Server", "arcgis")

        # DataStore Section
        self.ds_container = ctk.CTkFrame(self, fg_color="#f8f7f4", border_width=1, border_color="#e2e8f0")
        ctk.CTkLabel(self.ds_container, text="Typy Datastore:", text_color="black", font=("Segoe UI", 12, "bold")).pack(padx=10, anchor="w", pady=5)
        self.ds_vars = {ds: ctk.BooleanVar(value=(ds=="Relational")) for ds in DS_TYPES}
        for ds in DS_TYPES:
            ctk.CTkCheckBox(self.ds_container, text=ds, variable=self.ds_vars[ds], text_color="black", checkbox_width=18).pack(side="left", padx=10, pady=5)

        # SSL Box
        self.ssl_box = ctk.CTkFrame(self, fg_color="transparent")
        self.ssl_box.pack(fill="x", padx=20, pady=10)
        self.ssl_rows_list = []
        self.add_ssl_btn = ctk.CTkButton(self.ssl_box, text="Dodaj certyfikat", width=140, fg_color="#10b981", hover_color="#059669", command=self.add_ssl)
        self.add_ssl_btn.pack(pady=5, anchor="w")

    def refresh_ui(self):
        if self.role_vars["WebAdaptor"].get():
            self.wa_container.pack(fill="x", padx=20, pady=5, expand=False)
            self.wa_p_group.pack_forget()
            self.wa_s_group.pack_forget()

            portal_is_role = self.role_vars["Portal"].get()
            server_is_role = self.role_vars["Server"].get()

            if not portal_is_role and not server_is_role:
                self.wa_p_group.pack(fill="x", padx=10, pady=2)
                self.wa_s_group.pack(fill="x", padx=10, pady=2)
            else:
                if portal_is_role: self.wa_p_group.pack(fill="x", padx=10, pady=2)
                if server_is_role: self.wa_s_group.pack(fill="x", padx=10, pady=2)
        else:
            self.wa_container.pack_forget()
        
        if self.role_vars["DataStore"].get(): self.ds_container.pack(fill="x", padx=20, pady=5)
        else: self.ds_container.pack_forget()
        
        self.ssl_box.pack_forget()
        self.ssl_box.pack(fill="x", padx=20, pady=10)
        self.on_role_change()

    def add_ssl(self):
        """Dodaje wiersz certyfikatu SSL po kliknięciu przycisku.
        Automatycznie pobiera ścieżkę z sesji i zaznacza w Target wszystkie aktywne role maszyny."""
        cert_path = ""

        if self.role_vars["Server"].get() and session.get("server_certificate"):
            cert_path = session.get("server_certificate")
        elif self.role_vars["Portal"].get() and session.get("portal_certificate"):
            cert_path = session.get("portal_certificate")

        # Zaznacza w sekcji Target wszystkie role aktywne na tej maszynie (np. Server, Portal, DataStore, WebAdaptor)
        default_targets = [role for role, var in self.role_vars.items() if var.get() and role in SSL_TARGETS]

        row = SSLCertificateRow(self.ssl_box, self.remove_ssl, default_path=cert_path, default_targets=default_targets)
        self.ssl_rows_list.append(row)
        self.add_ssl_btn.pack_forget()
        self.add_ssl_btn.pack(pady=5, anchor="w")

    def remove_ssl(self, row):
        row.destroy()
        self.ssl_rows_list.remove(row)

    def get_node_data(self):
        roles = [r for r, v in self.role_vars.items() if v.get()]
        node = {"NodeName": self.ent_name.get(), "Role": roles}
        
        if "DataStore" in roles:
            node["DataStoreTypes"] = [ds for ds, v in self.ds_vars.items() if v.get()]
            
        if "WebAdaptor" in roles:
            wa_list = []
            if self.wa_p_group.winfo_ismapped() and self.wa_p_ctx.get().strip():
                wa_list.append({
                    "Role": "Portal", "Context": self.wa_p_ctx.get().strip(),
                    "AdminAccessEnabled": self.wa_p_admin_var.get()
                })
            if self.wa_s_group.winfo_ismapped() and self.wa_s_ctx.get().strip():
                wa_list.append({
                    "Role": "Server", "Context": self.wa_s_ctx.get().strip(),
                    "AdminAccessEnabled": self.wa_s_admin_var.get()
                })
            if wa_list: node["WebAdaptorConfig"] = wa_list
                
        certs = [r.get_data() for r in self.ssl_rows_list if r.get_data()]
        if certs: node["SslCertificates"] = certs
        return node