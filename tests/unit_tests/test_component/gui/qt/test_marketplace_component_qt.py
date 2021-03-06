import pytest
import os
import time

from mamba.core.context import Context
from mamba.core.msg import Empty
from mamba.component.gui.qt.marketplace_component_qt import MarketplaceComponent
from mamba.component.gui.qt import MainWindowQt
from mamba.core.testing.utils import CallbackTestClass


class TestClass:
    def setup_method(self):
        self.context = Context()
        self.context.set(
            'mamba_dir',
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                         '..', 'mamba'))

    def teardown_method(self):
        del self.context

    def test_component_wo_context(self):
        with pytest.raises(TypeError) as excinfo:
            MarketplaceComponent()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_component_w_empty_context(self):
        component = MarketplaceComponent(self.context)
        component.initialize()

        assert component._configuration == {
            'menu': '&Marketplace',
            'name': 'Component',
            'shortcut': 'Ctrl+C'
        }

        assert component._app is not None

    def test_views_publication(self):
        dummy_test_class = CallbackTestClass()

        self.context.rx['run_plugin'].subscribe(dummy_test_class.test_func_1)

        component = MarketplaceComponent(self.context)
        component.initialize()

        assert component._configuration == {
            'menu': '&Marketplace',
            'name': 'Component',
            'shortcut': 'Ctrl+C'
        }

        assert component._app is not None

        component.publish_views([{
            "menu_title": "Utils",
            "action_name": "tc_window",
            "data": {
                "pos_x": 0,
                "pos_y": 0,
                "width": 670,
                "height": 296,
                "services": ["digitizer -> connect", "shutdown -> shutdown"]
            }
        }])

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.menu_title == 'Utils'
        assert dummy_test_class.func_1_last_value.action_name == 'tc_window'
        assert dummy_test_class.func_1_last_value.perspective == {
            'height': 296,
            'pos_x': 0,
            'pos_y': 0,
            'services': ['digitizer -> connect', 'shutdown -> shutdown'],
            'width': 670
        }

        component.publish_views([{
            "menu_title": "Utils",
            "action_name": "tc_window",
            "data": {
                "pos_x": 0,
                "pos_y": 0,
                "width": 670,
                "height": 296,
                "services": ["digitizer -> connect", "shutdown -> shutdown"]
            }
        }, {
            "menu_title": "Utils",
            "action_name": "tm_window",
            "data": {
                "pos_x":
                670,
                "pos_y":
                0,
                "width":
                653,
                "height":
                296,
                "services": [
                    "cyclic_telemetry_tcp -> connected",
                    "digitizer -> connected"
                ]
            }
        }])

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 3
        assert dummy_test_class.func_1_last_value.menu_title == 'Utils'
        assert dummy_test_class.func_1_last_value.action_name == 'tm_window'
        assert dummy_test_class.func_1_last_value.perspective == {
            'height':
            296,
            'pos_x':
            670,
            'pos_y':
            0,
            'services':
            ['cyclic_telemetry_tcp -> connected', 'digitizer -> connected'],
            'width':
            653
        }

    def test_component_w_menu_window(self):
        main_window = MainWindowQt(self.context)
        main_window.initialize()

        assert not main_window._exists_menu('&Help')

        component = MarketplaceComponent(self.context)
        component.initialize()

        assert component._configuration == {
            'menu': '&Marketplace',
            'name': 'Component',
            'shortcut': 'Ctrl+C'
        }

        assert component._app is not None

        assert main_window._exists_menu('&Marketplace')
        assert main_window._is_action_in_menu('&Marketplace', 'Component')

        main_window._close(Empty())
        main_window._qt_app.quit()
