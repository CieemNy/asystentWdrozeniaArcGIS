from ..components import NodeFrame
from ..components.base_config_screen import BaseConfigScreen
from .global_config import GlobalConfigPanel


class EnterpriseScreen(BaseConfigScreen):
    def __init__(self, master, on_back, **kwargs):
        super().__init__(
            master,
            on_back,
            title="Generator Konfiguracji: ArcGIS Enterprise",
            filename_prefix="ArcGIS_Enterprise_Configuration",
            add_button_height=45,
            add_button_pady=20,
            panel_pady=20,
            save_pady=30,
            title_color="#0f172a",
            **kwargs
        )

    @property
    def global_panel(self):
        return self.config_panel

    def create_config_panel(self, parent):
        return GlobalConfigPanel(parent)

    def create_node(self, index):
        return NodeFrame(self.scroll_canvas, index, self.remove_node, self.on_role_update)

    def get_all_active_roles(self):
        return {
            role
            for node in self.nodes
            for role, variable in node.role_vars.items()
            if variable.get()
        }

    def on_role_update(self):
        if hasattr(self, "config_panel"):
            self.config_panel.update_visibility(self.get_all_active_roles())

    def on_nodes_changed(self):
        self.on_role_update()

    def get_config_data(self):
        return self.config_panel.get_config_data(self.get_all_active_roles())