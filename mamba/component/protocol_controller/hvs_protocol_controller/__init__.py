import os

from rx import operators as op
from typing import List, Dict

from mamba.core.msg import ServiceRequest, ServiceResponse,\
    ServiceRequest, ParameterInfo, ParameterType
from mamba.component import ComponentBase
from mamba.core.exceptions import ComponentConfigException


class Driver(ComponentBase):
    def __init__(self, context, local_config=None):
        super(Driver, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        # Initialize observers
        self._register_observers()

        # Define custom variables
        self._provider_params: Dict[str, ParameterInfo] = {}
        self._io_result_subs = None

    def _register_observers(self):
        """ Entry point for registering component observers """

        # Register to the tc provided by the socket protocol translator service
        self._context.rx['tc'].pipe(
            op.filter(lambda value: isinstance(value, ServiceRequest))
        ).subscribe(on_next=self._received_tc)

        # Register to the topic provided by the io_controller services
        self._context.rx['io_service_signature'].subscribe(
            on_next=self._io_service_signature)

    def _generate_tm(self, telecommand: ServiceRequest):
        """ Entry point for generating response telemetry

            Args:
                telecommand: The service request received.
        """

        result = ServiceResponse(id=telecommand.id, type=telecommand.type)

        if 'meta' in telecommand.type:
            io_service = self._provider_params[telecommand.id]

            result.value = {
                'signature': io_service.signature,
                'description': io_service.description
            }

        self._context.rx['tm'].on_next(result)

    def _generate_error_tm(self, telecommand: ServiceRequest, message: str):
        """ Entry point for generating error response telemetry

            Args:
                telecommand: The service request received.
                message: The error feedback message.
        """

        self._context.rx['tm'].on_next(
            ServiceResponse(id=telecommand.id, type='error', value=message))

    def _generate_io_service_request(self, telecommand: ServiceRequest):
        """ Entry point for generating a IO Service request to fulfill
            a request

            Args:
                telecommand: The service request received.
        """

        self._io_result_subs = self._context.rx['io_result'].pipe(
            op.filter(lambda value: isinstance(value, ServiceResponse))
        ).subscribe(on_next=self._process_io_result)

        self._context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider=self._provider_params[telecommand.id].provider,
                id=self._provider_params[telecommand.id].id,
                type=telecommand.type,
                args=telecommand.args))

    def _received_tc(self, telecommand: ServiceRequest):
        """ Entry point for processing a new telecommand coming from the
            socket translator.

            Args:
                telecommand: The telecommand coming from the socket translator.
        """
        if telecommand.provider is not None:
            telecommand.id = f'{telecommand.provider}_{telecommand.id}'

        self._log_dev(f'Received TC: {telecommand.id}')

        if (telecommand.id
                not in self._provider_params) and (telecommand.type != 'helo'):
            self._generate_error_tm(telecommand, 'Not recognized command')
            return

        if telecommand.type in ['helo', 'set_meta', 'get_meta']:
            self._generate_tm(telecommand)
        elif telecommand.type in ['set', 'get']:
            self._generate_io_service_request(telecommand)
        else:
            self._generate_error_tm(telecommand, 'Not recognized command type')

    def _process_io_result(self, rx_result: ServiceResponse):
        """ Entry point for processing the IO Service results.

            Args:
                rx_result: The io service response.
        """
        self._io_result_subs.dispose()
        self._context.rx['tm'].on_next(rx_result)

    def _io_service_signature(self, parameters_info: List[ParameterInfo]):
        """ Entry point for processing the service signatures.

            Args:
                signatures: The io service signatures dictionary.
        """
        self._log_info(
            f"Received signatures from {parameters_info[0].provider}: "
            f"{[str(parameter_info) for parameter_info in parameters_info]}")

        for parameter_info in parameters_info:
            if not isinstance(parameter_info.signature, list) or len(
                    parameter_info.signature) != 2 or not isinstance(
                        parameter_info.signature[0], list):
                raise ComponentConfigException(
                    f'Signature of service {parameter_info.provider} -> '
                    f'"{parameter_info.id}" is invalid. Format shall'
                    f' be [[arg_1, arg_2, ...], return_type]')

            hvs_parameter_id = f'{parameter_info.provider}_{parameter_info.id}'

            if hvs_parameter_id in self._provider_params:
                raise ComponentConfigException(
                    f"Received conflicting parameter key: {hvs_parameter_id}")

            self._provider_params[hvs_parameter_id] = parameter_info
