import customtkinter as ctk
from core.utils import CTKTooltip

class FormFieldMixin:
    """Wspólne funkcje dla pól formularzy."""

    
    def _add_field(self, var_key, label_text, default, is_pass=False):
            return self._add_field_to_frame(self, var_key, label_text, default, is_pass)
    
    def _add_field_to_frame(self, parent_frame, var_key, label_text, default, is_pass=False):
            row = ctk.CTkFrame(parent_frame, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=2)
            ctk.CTkLabel(row, text=label_text, width=230, anchor="w", text_color="black").pack(side="left")
            v = ctk.StringVar(value=default)
            self.vars[var_key] = v
            ctk.CTkEntry(row, textvariable=v, fg_color="white", text_color="black", show="*" if is_pass else "").pack(side="left", fill="x", expand=True)
            return row
    
    def _add_checkbox(self,var_key,label_text,default=True, command=None, help_text=None, parent_frame=None):
        parent = parent_frame if parent_frame is not None else self
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(row, text=label_text, width=230, anchor="w", text_color="black", ).pack(side="left")
        variable = ctk.BooleanVar(value=default)
        self.vars[var_key] = variable
        ctk.CTkCheckBox(row, text="", variable=variable, width=20, command=command, ).pack(side="left")
        if help_text and getattr(self, "help_img", None):
            help_icon = ctk.CTkLabel(row, text="", image=self.help_img, cursor="question_arrow", )
            help_icon.pack(side="left", padx=10)
            CTKTooltip(help_icon, help_text)
        return row
    
    def _toggle_container(self, var_key, container, anchor, after=None):
        if self.vars[var_key].get():
            container.pack(fill="x", after=after if after is not None else anchor)
        else:
            container.pack_forget()

    def _toggle_container_var(self, enabled, container, anchor):
        if enabled:
            container.pack(fill="x", after=anchor)
        else:
            container.pack_forget()