############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" Component for simulating a simple UDP server equipment """

import os
import threading
import socketserver
from typing import Optional

from mamba.core.msg import Empty
from mamba.core.context import Context
from mamba.core.component_base import InstrumentDriver


class SinglePortUdpMock(InstrumentDriver):
    """ Simple UDP Server Mock """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        self._server: Optional[ThreadedUdpServer] = None
        self._server_thread: Optional[threading.Thread] = None

    def _close(self, rx_value: Optional[Empty] = None) -> None:
        """ Entry point for closing the component """
        if self._server is not None:
            self._server.do_run = False
            self._server.shutdown()

        if self._server_thread is not None:
            self._server_thread.join()

    def initialize(self) -> None:
        """ Entry point for component initialization """
        # Compose shared memory data dictionaries
        for key, parameter_info in self._configuration['parameters'].items():
            self._shared_memory[key] = parameter_info.get('initial_value')

        # Create the TM socket server, binding to host and port
        socketserver.UDPServer.allow_reuse_address = True
        self._server = ThreadedUdpServer(
            (self._instrument.address, self._instrument.port),
            ThreadedUdpHandler, self)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self._server_thread = threading.Thread(
            target=self._server.serve_forever)

        # Exit the server thread when the main thread terminates
        self._server_thread.daemon = True
        self._server_thread.start()
        self._log_info(f'Simple UDP Server running in thread: '
                       f'{self._server_thread.name}')


class ThreadedUdpHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for the socket server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        data = str(self.request[0], self.server.encoding)
        socket = self.request[1]

        for cmd in data.split(self.server.eom_r)[:-1]:
            self.server.log_dev(fr' - Received socket TC: {cmd}')
            cmd = cmd.split(" ")
            if len(cmd) >= 2:
                key = cmd[0].lower()

                if key in self.server.telemetries:
                    self.server.telemetries[cmd[0].lower()] = cmd[1]
                else:
                    self.server.telemetries['syst_err'] = '1, Command error'
            elif cmd[0][-1] == '?':
                key = cmd[0][:-1].lower().replace(':', '_')

                if key[0] == '*':
                    key = key[1:]

                if key in self.server.telemetries:
                    socket.sendto(
                        bytes(
                            f'{self.server.telemetries[key]}'
                            f'{self.server.eom_w}', self.server.encoding),
                        self.client_address)

                    if key == 'syst_err':
                        self.server.telemetries['syst_err'] = '0,_No_Error'
                else:
                    socket.sendto(
                        bytes(f'KeyError{self.server.eom_w}',
                              self.server.encoding), self.client_address)

                    self.server.telemetries['syst_err'] = '1,_Command_Error'
            else:
                key = cmd[0].lower()

                if key[0] == '*':
                    key = key[1:]

                if key not in self.server.telemetries:
                    self.server.telemetries['syst_err'] = '1, Command error'

        self.server.log_info('Remote socket connection has been closed')


class ThreadedUdpServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    """ TC server to modify the telemetries """
    def __init__(self, server_address, request_handler_class,
                 parent: SinglePortUdpMock) -> None:
        super().__init__(server_address, request_handler_class)
        self.log_dev = parent._log_dev
        self.log_info = parent._log_info
        self.telemetries = parent._shared_memory
        self.eom_r = parent._instrument.terminator_read
        self.eom_w = parent._instrument.terminator_write
        self.encoding = parent._instrument.encoding

        self.do_run = True
