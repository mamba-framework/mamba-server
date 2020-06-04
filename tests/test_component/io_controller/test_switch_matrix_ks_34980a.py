import os
import pytest
import copy
import time
from tempfile import NamedTemporaryFile

from rx import operators as op

from mamba.core.testing.utils import compose_service_info, get_config_dict, CallbackTestClass, get_io_service_signature
from mamba.core.context import Context
from mamba.component.io_controller.switch_matrix import SwitchMatrixKs34980a
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import Empty, ServiceRequest, ServiceResponse

component_path = os.path.join('component', 'io_controller', 'switch_matrix',
                              'ks_34980a')


class TestClass:
    def setup_class(self):
        """ setup_class called once for the class """
        self.mamba_path = os.path.join(os.path.dirname(__file__), '..', '..',
                                       '..', 'mamba')

        self.default_component_config = get_config_dict(
            os.path.join(self.mamba_path, component_path, 'config.yml'))

        self.default_service_info = compose_service_info(
            self.default_component_config)

    def teardown_class(self):
        """ teardown_class called once for the class """
        pass

    def setup_method(self):
        """ setup_method called for every method """
        self.context = Context()
        self.context.set(
            'mamba_dir',
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'mamba'))

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_wo_context(self):
        """ Test component behaviour without required context """
        with pytest.raises(TypeError) as excinfo:
            SwitchMatrixKs34980a()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_w_default_context_component_creation(self):
        """ Test component creation behaviour with default context """
        component = SwitchMatrixKs34980a(self.context)

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {}
        assert component._shared_memory_getter == {}
        assert component._shared_memory_setter == {}
        assert component._service_info == {}
        assert component._inst is None
        assert component._simulation_file is None

    def test_w_default_context_component_initialization(self):
        """ Test component initialization behaviour with default context """
        component = SwitchMatrixKs34980a(self.context)
        component.initialize()

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {
            'connected': False,
            'query_raw_result': ''
        }
        assert component._shared_memory_getter == {
            'SWITCH_34980A_QUERY_CONNECTED': 'connected',
            'SWITCH_34980A_TM_QUERY_RAW': 'query_raw_result'
        }
        assert component._shared_memory_setter == {
            'SWITCH_34980A_CONNECT': 'connected',
            'SWITCH_34980A_DISCONNECT': 'connected',
            'SWITCH_34980A_TC_QUERY_RAW': 'query_raw_result'
        }
        assert component._service_info == self.default_service_info
        assert component._inst is None
        assert 'ks_34980a.yml' in component._simulation_file

    def test_visa_sim_local_from_project_folder(self):
        """ Test component creation behaviour with default context """
        temp_file = NamedTemporaryFile(delete=False)

        temp_file_folder = temp_file.name.rsplit('/', 1)[0]
        temp_file_name = temp_file.name.rsplit('/', 1)[1]

        os.chdir(temp_file_folder)

        component = SwitchMatrixKs34980a(
            self.context, local_config={'visa-sim': temp_file_name})
        component.initialize()

        assert temp_file_name in component._simulation_file

        temp_file.close()

    def test_visa_sim_mamba_from_project_folder(self):
        """ Test component creation behaviour with default context """
        os.chdir('/tmp')

        component = SwitchMatrixKs34980a(self.context)
        component.initialize()

        assert 'ks_34980a.yml' in component._simulation_file

    def test_w_custom_context(self):
        """ Test component creation behaviour with default context """
        component = SwitchMatrixKs34980a(
            self.context,
            local_config={
                'name': 'custom_name',
                'visa-sim': None,
                'topics': {
                    'CUSTOM_TOPIC': {
                        'command': 'CUSTOM_SCPI {:}',
                        'description': 'Custom command description',
                        'signature': [['str'], None]
                    }
                }
            })
        component.initialize()

        custom_component_config = copy.deepcopy(self.default_component_config)
        custom_component_config['name'] = 'custom_name'
        custom_component_config['visa-sim'] = None
        custom_component_config['topics'].update({
            'CUSTOM_TOPIC': {
                'command': 'CUSTOM_SCPI {:}',
                'description': 'Custom command description',
                'signature': [['str'], None]
            }
        })

        # Test default configuration load
        assert component._configuration == custom_component_config

        # Test custom variables default values
        assert component._shared_memory == {
            'connected': False,
            'query_raw_result': ''
        }
        assert component._shared_memory_getter == {
            'SWITCH_34980A_QUERY_CONNECTED': 'connected',
            'SWITCH_34980A_TM_QUERY_RAW': 'query_raw_result'
        }
        assert component._shared_memory_setter == {
            'SWITCH_34980A_CONNECT': 'connected',
            'SWITCH_34980A_DISCONNECT': 'connected',
            'SWITCH_34980A_TC_QUERY_RAW': 'query_raw_result'
        }

        custom_service_info = compose_service_info(custom_component_config)
        assert component._service_info == custom_service_info
        assert component._inst is None
        assert component._simulation_file is None

    def test_w_wrong_custom_context(self):
        """ Test component creation behaviour with default context """

        # Test with wrong topics dictionary
        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKs34980a(self.context,
                                 local_config={
                                     'topics': 'wrong'
                                 }).initialize()
        assert "Topics configuration: wrong format" in str(excinfo.value)

        # In case no new topics are given, use the default ones
        component = SwitchMatrixKs34980a(self.context,
                                         local_config={'topics': {}})
        component.initialize()

        assert component._configuration == self.default_component_config

        # Test with missing simulation file
        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKs34980a(self.context,
                                 local_config={
                                     'visa-sim': 'non-existing'
                                 }).initialize()
        assert "Visa-sim file has not been found" in str(excinfo.value)

        # Test case properties do not have a getter, setter or default
        component = SwitchMatrixKs34980a(
            self.context, local_config={'parameters': {
                'new_param': {}
            }})
        component.initialize()

        assert component._shared_memory == {
            'connected': False,
            'query_raw_result': '',
            'new_param': None,
        }

    def test_io_signature_publication(self):
        """ Test component io_signature observable """
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_service_signature'].pipe(
            op.filter(lambda value: isinstance(value, dict))).subscribe(
                dummy_test_class.test_func_1)

        component = SwitchMatrixKs34980a(self.context)
        component.initialize()

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value == get_io_service_signature(
            self.default_component_config, self.default_service_info)

        component = SwitchMatrixKs34980a(
            self.context,
            local_config={
                'name': 'custom_name',
                'visa-sim': None,
                'topics': {
                    'CUSTOM_TOPIC': {
                        'command': 'CUSTOM_SCPI {:}',
                        'description': 'Custom command description',
                        'signature': [['str'], None]
                    }
                }
            })
        component.initialize()

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 2

        custom_component_config = copy.deepcopy(self.default_component_config)
        custom_component_config['name'] = 'custom_name'
        custom_component_config['visa-sim'] = None
        custom_component_config['topics'].update({
            'CUSTOM_TOPIC': {
                'command': 'CUSTOM_SCPI {:}',
                'description': 'Custom command description',
                'signature': [['str'], None]
            }
        })

        custom_service_info = compose_service_info(custom_component_config)

        assert dummy_test_class.func_1_last_value == get_io_service_signature(
            custom_component_config, custom_service_info)

    def test_io_service_request_observer(self):
        """ Test component io_service_request observer """
        component = SwitchMatrixKs34980a(self.context)
        component.initialize()
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # 1 - Test that component only gets activated for implemented services
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='NOT_EXISTING', type='any', args=[]))

        assert dummy_test_class.func_1_times_called == 0
        assert dummy_test_class.func_1_last_value is None

        # 2 - Test generic command before connection to the instrument has been established
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='SWITCH_34980A_QUERY_IDN', type='tc', args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'SWITCH_34980A_QUERY_IDN'
        assert dummy_test_class.func_1_last_value.type == 'error'
        assert dummy_test_class.func_1_last_value.value == 'Not possible to perform command before connection is established'

        # 3 - Test connection to the instrument
        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='SWITCH_34980A_CONNECT', type='tc', args=[]))

        time.sleep(.1)

        assert component._inst is not None
        assert dummy_test_class.func_1_times_called == 2
        assert dummy_test_class.func_1_last_value.id == 'SWITCH_34980A_CONNECT'
        assert dummy_test_class.func_1_last_value.type == 'tc'
        assert dummy_test_class.func_1_last_value.value is None

        # 4 - Test generic command
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='SWITCH_34980A_RST', type='tc', args=[1]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 3
        assert dummy_test_class.func_1_last_value.id == 'SWITCH_34980A_RST'
        assert dummy_test_class.func_1_last_value.type == 'tc'
        assert dummy_test_class.func_1_last_value.value is None

        # 5 - Test generic query
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='SWITCH_34980A_QUERY_IDN', type='tm', args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 4
        assert dummy_test_class.func_1_last_value.id == 'SWITCH_34980A_QUERY_IDN'
        assert dummy_test_class.func_1_last_value.type == 'tm'
        assert dummy_test_class.func_1_last_value.value == 'AGILENT_TECHNOLOGIES,34980A,XXX'

        # 6 - Test shared memory set
        assert component._shared_memory == {
            'connected': 1,
            'query_raw_result': ''
        }

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='SWITCH_34980A_TC_QUERY_RAW',
                           type='tc',
                           args=['*IDN?']))

        time.sleep(.1)

        assert component._shared_memory == {
            'connected':
            1,
            'query_raw_result':
            'AGILENT_TECHNOLOGIES,34980A,XXX'
        }

        assert dummy_test_class.func_1_times_called == 5
        assert dummy_test_class.func_1_last_value.id == 'SWITCH_34980A_TC_QUERY_RAW'
        assert dummy_test_class.func_1_last_value.type == 'tc'
        assert dummy_test_class.func_1_last_value.value is None

        # 7 - Test shared memory get
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='SWITCH_34980A_TM_QUERY_RAW', type='tm',
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 6
        assert dummy_test_class.func_1_last_value.id == 'SWITCH_34980A_TM_QUERY_RAW'
        assert dummy_test_class.func_1_last_value.type == 'tm'
        assert dummy_test_class.func_1_last_value.value == 'AGILENT_TECHNOLOGIES,34980A,XXX'

        # 8 - Test special case of msg command with multiple args
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='SWITCH_34980A_RAW',
                           type='tc',
                           args=['CONF:VOLT:DC', '10,0.003,(@4009)']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 7
        assert dummy_test_class.func_1_last_value.id == 'SWITCH_34980A_RAW'
        assert dummy_test_class.func_1_last_value.type == 'tc'
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='SWITCH_34980A_TC_QUERY_RAW',
                           type='tc',
                           args=['MEAS:VOLT:DC?', '1,0.001,(@4009)']))

        time.sleep(.1)

        assert component._shared_memory == {
            'connected': 1,
            'query_raw_result': '10'
        }

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='SWITCH_34980A_TM_QUERY_RAW', type='tm',
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 9
        assert dummy_test_class.func_1_last_value.id == 'SWITCH_34980A_TM_QUERY_RAW'
        assert dummy_test_class.func_1_last_value.type == 'tm'
        assert dummy_test_class.func_1_last_value.value == '10'

        # 9 - Test disconnection to the instrument
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='SWITCH_34980A_DISCONNECT', type='tc', args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 10
        assert dummy_test_class.func_1_last_value.id == 'SWITCH_34980A_DISCONNECT'
        assert dummy_test_class.func_1_last_value.type == 'tc'
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='SWITCH_34980A_QUERY_CONNECTED',
                           type='tm',
                           args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 11
        assert dummy_test_class.func_1_last_value.id == 'SWITCH_34980A_QUERY_CONNECTED'
        assert dummy_test_class.func_1_last_value.type == 'tm'
        assert dummy_test_class.func_1_last_value.value == 0

    def test_connection_visa_sim_wrong_instrument_address(self):
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # Test simulated normal connection to the instrument
        component = SwitchMatrixKs34980a(
            self.context,
            local_config={'resource-name': 'TCPIP0::4.3.2.1::INSTR'})
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='SWITCH_34980A_CONNECT', type='tc', args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'SWITCH_34980A_CONNECT'
        assert dummy_test_class.func_1_last_value.type == 'tc'
        assert dummy_test_class.func_1_last_value.value is None

    def test_disconnection_w_no_connection(self):
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # Test real connection to missing instrument
        component = SwitchMatrixKs34980a(self.context)
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='SWITCH_34980A_DISCONNECT', type='tc', args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'SWITCH_34980A_DISCONNECT'
        assert dummy_test_class.func_1_last_value.type == 'tc'
        assert dummy_test_class.func_1_last_value.value is None

    def test_service_invalid_signature(self):
        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKs34980a(self.context,
                                 local_config={
                                     'topics': {
                                         'CUSTOM_TOPIC': {
                                             'command':
                                             'SOURce:CUSTOM_SCPI {:}',
                                             'description':
                                             'Custom command description'
                                             'frequency',
                                             'signature': ['String']
                                         }
                                     }
                                 }).initialize()

        assert 'Signature of service "CUSTOM_TOPIC" is invalid. Format shall' \
               ' be [[arg_1, arg_2, ...], return_type]' in str(excinfo.value)

        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKs34980a(self.context,
                                 local_config={
                                     'topics': {
                                         'CUSTOM_TOPIC': {
                                             'command':
                                             'SOURce:CUSTOM_SCPI {:}',
                                             'description':
                                             'Custom command description'
                                             'frequency',
                                             'signature': ['String', str]
                                         }
                                     }
                                 }).initialize()

        assert 'Signature of service "CUSTOM_TOPIC" is invalid. Format shall' \
               ' be [[arg_1, arg_2, ...], return_type]' in str(excinfo.value)

        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKs34980a(self.context,
                                 local_config={
                                     'topics': {
                                         'CUSTOM_TOPIC': {
                                             'command':
                                             'SOURce:CUSTOM_SCPI {:}',
                                             'description':
                                             'Custom command description'
                                             'frequency',
                                             'signature':
                                             'String'
                                         }
                                     }
                                 }).initialize()

        assert 'Signature of service "CUSTOM_TOPIC" is invalid. Format shall' \
               ' be [[arg_1, arg_2, ...], return_type]' in str(excinfo.value)

    def test_connection_cases_normal_fail(self):
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # Test real connection to missing instrument
        component = SwitchMatrixKs34980a(self.context,
                                         local_config={'visa-sim': None})
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(id='SWITCH_34980A_CONNECT', type='tc', args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'SWITCH_34980A_CONNECT'
        assert dummy_test_class.func_1_last_value.type == 'error'
        assert dummy_test_class.func_1_last_value.value == 'Instrument is unreachable'

    def test_quit_observer(self):
        """ Test component quit observer """
        class Test:
            called = False

            def close(self):
                self.called = True

        component = SwitchMatrixKs34980a(self.context)
        component.initialize()

        # Test quit while on load window
        component._inst = Test()

        assert not component._inst.called

        self.context.rx['quit'].on_next(Empty())

        # Test connection to the instrument has been closed
        assert component._inst is None
