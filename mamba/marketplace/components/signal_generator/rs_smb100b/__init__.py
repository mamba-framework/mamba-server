############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" RF Signal Generator IO Controller"""

from typing import Optional
import os

from mamba.core.context import Context
from mamba.core.component_base import VisaInstrumentDriver


class SignalGeneratorSmb100b(VisaInstrumentDriver):
    """ RF Signal Generator IO Controller class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)
