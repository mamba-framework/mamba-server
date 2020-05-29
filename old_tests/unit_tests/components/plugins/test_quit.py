import os

from mamba.core.context import Context
from mamba.components.plugins.quit import Plugin
from mamba.components.main.main_qt import MainWindow

from mamba.components.observable_types.empty import Empty
from mamba.components.main.observable_types.run_action import RunAction


class DummyTestClass:
    def __init__(self):
        super(DummyTestClass, self).__init__()
        self.times_called = 0
        self.last_value = None

    def test_function(self, rx_on_set=None):
        self.times_called += 1
        self.last_value = rx_on_set


class TestClass:
    def setup_class(self):
        """ setup_class called once for the class """
        pass

    def teardown_class(self):
        """ teardown_class called once for the class """
        pass

    def setup_method(self):
        """ setup_method called for every method """
        self.context = Context()
        self.context.set(
            'mamba_dir',
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                         'mamba'))

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_component_w_menu_window(self):
        main_window = MainWindow(self.context)
        main_window.initialize()

        # Test help is not in menu bar
        assert not main_window._exists_menu('File')

        self.context.set('main_window', main_window)
        component = Plugin(self.context)
        component.initialize()

        # Test default configuration
        assert component._configuration == {
            'menu': 'File',
            'name': 'Quit',
            'shortcut': 'Ctrl+Q',
            'status_tip': 'Close Mamba Server'
        }

        # Test menu is in menu bar
        assert main_window._exists_menu('File')

        # Test execute closes Main Window
        main_window._show()
        assert main_window._app.isVisible()

        # Execute Quit Widget
        component.run(Empty())

        # Test window is hidden per default
        assert not main_window._app.isVisible()

    def test_component_run_rx_mamba(self):
        dummy_test_class = DummyTestClass()
        main_window = MainWindow(self.context)
        main_window.initialize()

        self.context.set('main_window', main_window)
        component = Plugin(self.context)

        # Subscribe to the 'quit' that shall be published
        self.context.rx['quit'].subscribe(dummy_test_class.test_function)

        # Check it is not activated by another menu
        self.context.rx['run_plugin'].on_next(
            RunAction(menu_title='File_Wrong', action_name='Quit'))

        assert dummy_test_class.times_called == 0
        assert dummy_test_class.last_value is None

        # Check it is not activated by another action
        self.context.rx['run_plugin'].on_next(
            RunAction(menu_title='File', action_name='Quit_Wrong'))

        assert dummy_test_class.times_called == 0
        assert dummy_test_class.last_value is None

        # Check activation emits 'quit'
        self.context.rx['run_plugin'].on_next(
            RunAction(menu_title='File', action_name='Quit'))

        assert dummy_test_class.times_called == 1
        assert isinstance(dummy_test_class.last_value, Empty)

    def test_component_run_rx_py(self):
        dummy_test_class = DummyTestClass()
        main_window = MainWindow(self.context)
        main_window.initialize()

        self.context.set('main_window', main_window)
        component = Plugin(self.context)

        # Subscribe to the 'quit' that shall be published
        self.context.rx['quit'].subscribe(dummy_test_class.test_function)

        # Check it is not activated by another menu
        self.context.rx['run_plugin'].on_next(
            RunAction(menu_title='File_Wrong', action_name='Quit'))

        assert dummy_test_class.times_called == 0
        assert dummy_test_class.last_value is None

        # Check it is not activated by another action
        self.context.rx['run_plugin'].on_next(
            RunAction(menu_title='File', action_name='Quit_Wrong'))

        assert dummy_test_class.times_called == 0
        assert dummy_test_class.last_value is None

        # Check activation emits 'quit'
        self.context.rx['run_plugin'].on_next(
            RunAction(menu_title='File', action_name='Quit'))

        assert dummy_test_class.times_called == 1
        assert isinstance(dummy_test_class.last_value, Empty)