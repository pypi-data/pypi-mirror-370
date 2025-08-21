# ruff: noqa: F403, F405, E402
from __future__ import annotations
from ccdexplorer_fundamentals.GRPCClient.types_pb2 import *
from ccdexplorer_fundamentals.enums import NET
from ccdexplorer_fundamentals.GRPCClient.queries._SharedConverters import (
    Mixin as _SharedConverters,
)
from typing import TYPE_CHECKING
import sys

if TYPE_CHECKING:
    from ccdexplorer_fundamentals.GRPCClient import GRPCClient
from ccdexplorer_fundamentals.GRPCClient.CCD_Types import *
from rich import print


class Mixin(_SharedConverters):
    def convertFinalizedBlock(self, block) -> CCD_FinalizedBlockInfo:
        result = {}

        for descriptor in block.DESCRIPTOR.fields:
            key, value = self.get_key_value_from_descriptor(descriptor, block)

            if type(value) in self.simple_types:
                result[key] = self.convertType(value)

        return CCD_FinalizedBlockInfo(**result)

    def get_finalized_blocks(
        self: GRPCClient,
        net: Enum = NET.MAINNET,
    ) -> CCD_FinalizedBlockInfo:
        self.check_connection(net, sys._getframe().f_code.co_name)
        if net == NET.MAINNET:
            for block in self.stub_mainnet.GetFinalizedBlocks(request=Empty()):
                return self.convertFinalizedBlock(block)
        else:
            for block in self.stub_testnet.GetFinalizedBlocks(request=Empty()):
                return self.convertFinalizedBlock(block)
