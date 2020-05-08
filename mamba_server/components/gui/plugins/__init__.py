import os
import json

from PySide2.QtWidgets import QWidget, QAction, QMenu

from mamba_server.exceptions import ComponentConfigException

COMPONENT_CONFIG_FILE = "component.config.json"
SETTINGS_DESCRIPTION_FILE = "settings.json"


class GuiPluginsBase(QWidget):
    def __init__(self, folder, context):
        super(GuiPluginsBase, self).__init__()

        self.configuration = {}

        with open(os.path.join(folder, COMPONENT_CONFIG_FILE)) as f:
            self.configuration = json.load(f)

        self._validate_configuration()
        self._register_menu(context)

    def _validate_configuration(self):
        with open(os.path.join(os.path.dirname(__file__), SETTINGS_DESCRIPTION_FILE)) as f:
            settings_description = json.load(f)

            for key, value in settings_description.items():
                if key not in self.configuration:
                    if value['required']:
                        raise ComponentConfigException(f"Component '{self.configuration['name']}' configuration is missing parameter '{key}'!")
                    else:
                        self.configuration[key] = ""

    def _register_menu(self, context):
        self.action = QAction(self.configuration['name'],
                              self,
                              statusTip=self.configuration['status_tip'],
                              triggered=self.show)

        # Add Menu if it is not already in menu bar
        if self.configuration['menu'] not in [menu.title() for menu in context.get('main_window').menuBar().findChildren(QMenu)]:
            self.menu = context.get('main_window').menuBar().addMenu(self.configuration['menu'])

        self.menu.addAction(self.action)

    def show(self):
        """
        Entry point for showing gui plugin
        """
        raise NotImplementedError
