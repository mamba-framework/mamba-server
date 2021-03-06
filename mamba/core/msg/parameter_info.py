############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################

from typing import Any
import enum


class ParameterType(enum.IntEnum):
    get = 0
    set = 1
    get_meta = 2
    set_meta = 3
    helo = 4
    error = 5


class ParameterInfo:
    def __init__(self,
                 provider: str,
                 param_id: str,
                 param_type: ParameterType,
                 signature: Any,
                 description: str = '') -> None:
        self.provider = provider
        self.id = param_id
        self.type = param_type
        self.signature = signature
        self.description = description

    def __str__(self):
        return f'[id: {self.id}, type: {self.type}, ' \
               f'signature: {self.signature}]'
