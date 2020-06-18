""" Single Port TCP controller base """
from typing import Optional
import os

from mamba.core.component_base import TcpInstrumentDriver
from mamba.core.context import Context


class H8823SpwRawController(TcpInstrumentDriver):
    """ Simple TCP controller base class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)