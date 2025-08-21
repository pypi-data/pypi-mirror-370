# ruff: noqa: F403, F405, E402
from __future__ import annotations
from ccdexplorer_fundamentals.GRPCClient.types_pb2 import *
from ccdexplorer_fundamentals.enums import NET
from enum import Enum
from ccdexplorer_fundamentals.GRPCClient.queries._SharedConverters import (
    Mixin as _SharedConverters,
)
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccdexplorer_fundamentals.GRPCClient import GRPCClient

sys.path.append(os.path.dirname("ccdexplorer_fundamentals"))
from ccdexplorer_fundamentals.GRPCClient.CCD_Types import *


class Mixin(_SharedConverters):
    def get_passive_delegation_info(
        self: GRPCClient,
        block_hash: str,
        net: Enum = NET.MAINNET,
    ) -> CCD_PassiveDelegationInfo:
        prefix = ""
        result = {}
        blockHashInput = self.generate_block_hash_input_from(block_hash)

        grpc_return_value: PassiveDelegationInfo = self.stub_on_net(
            net, "GetPassiveDelegationInfo", blockHashInput
        )

        for descriptor in grpc_return_value.DESCRIPTOR.fields:
            key, value = self.get_key_value_from_descriptor(
                descriptor, grpc_return_value
            )
            key_to_store = f"{prefix}{key}"
            if type(value) in self.simple_types:
                result[key_to_store] = self.convertType(value)

            elif type(value) is CommissionRates:
                result[key] = self.convertCommissionRates(value)

        return CCD_PassiveDelegationInfo(**result)
