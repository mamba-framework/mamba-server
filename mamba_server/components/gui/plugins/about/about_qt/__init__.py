""" Plugin to show About message implemented in Qt5 """

import os
import pkgutil

from PySide2.QtWidgets import QMessageBox, QWidget, QApplication

from mamba_server.components.gui.plugins.interface import GuiPluginInterface


class GuiPlugin(GuiPluginInterface):
    """ Plugin to show About message implemented in Qt5 """
    def __init__(self, context):
        super(GuiPlugin, self).__init__(os.path.dirname(__file__), context)

        # Initialize observables
        self._register_observables()

        # Initialize custom variables
        self._version = None
        self._box_message = None
        self._app = None

        self.initialize()  # TBR

    def _register_observables(self):
        self._context.rx.subscribe(
            subject_name='run_plugin',
            on_next=self.run,
            op_filter=lambda rx_dict: rx_dict['menu'] == self._configuration[
                'menu'] and rx_dict['action'] == self._configuration['name'])

    def initialize(self):
        self._app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

        self._version = pkgutil.get_data('mamba_server',
                                         'VERSION').decode('ascii').strip()
        self._box_message = f"Mamba Server v{self._version}"

    def run(self, rx_on_next_value=None):
        QMessageBox.about(QWidget(), self._configuration['message_box_title'],
                          self._box_message)
