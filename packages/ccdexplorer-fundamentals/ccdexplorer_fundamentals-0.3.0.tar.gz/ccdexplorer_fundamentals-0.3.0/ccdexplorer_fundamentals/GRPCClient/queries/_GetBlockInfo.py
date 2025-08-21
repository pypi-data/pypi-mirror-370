# ruff: noqa: F403, F405, E402
from __future__ import annotations
from ccdexplorer_fundamentals.GRPCClient.types_pb2 import *
from ccdexplorer_fundamentals.enums import NET
from enum import Enum
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ccdexplorer_fundamentals.GRPCClient import GRPCClient
from ccdexplorer_fundamentals.GRPCClient.queries._SharedConverters import (
    Mixin as _SharedConverters,
)

import os
import sys

sys.path.append(os.path.dirname("ccdexplorer_fundamentals"))
from ccdexplorer_fundamentals.GRPCClient.CCD_Types import (
    CCD_BlockInfo,
    ProtocolVersions,
)


class Mixin(_SharedConverters):
    def get_block_info(
        self: GRPCClient,
        block_input: Union[str, int],
        net: Enum = NET.MAINNET,
    ) -> CCD_BlockInfo:
        result = {}
        blockHashInput = self.generate_block_hash_input_from(block_input)

        grpc_return_value: BlockInfo = self.stub_on_net(
            net, "GetBlockInfo", blockHashInput
        )

        for descriptor in grpc_return_value.DESCRIPTOR.fields:
            key, value = self.get_key_value_from_descriptor(
                descriptor, grpc_return_value
            )

            if key == "protocol_version":
                result[key] = ProtocolVersions(value).name

            elif type(value) in self.simple_types:
                result[f"{key}"] = self.convertType(value)

        # TODO: fix for BakerId always producing 0
        # even when it's not set (as is the case for genesis blocks)
        if result["era_block_height"] == 0:
            result["baker"] = None
        return CCD_BlockInfo(**result)
