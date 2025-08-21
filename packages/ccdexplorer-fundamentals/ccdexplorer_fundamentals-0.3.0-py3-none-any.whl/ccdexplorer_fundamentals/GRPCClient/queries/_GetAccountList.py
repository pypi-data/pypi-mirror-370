# ruff: noqa: F403, F405, E402
from __future__ import annotations
from ccdexplorer_fundamentals.GRPCClient.types_pb2 import *
from ccdexplorer_fundamentals.GRPCClient.queries._SharedConverters import (
    Mixin as _SharedConverters,
)
from ccdexplorer_fundamentals.GRPCClient.CCD_Types import *
from ccdexplorer_fundamentals.enums import NET
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccdexplorer_fundamentals.GRPCClient import GRPCClient


class Mixin(_SharedConverters):
    def get_account_list(
        self: GRPCClient,
        block_hash: str,
        net: Enum = NET.MAINNET,
    ) -> list[CCD_AccountAddress]:
        result = []
        blockHashInput = self.generate_block_hash_input_from(block_hash)

        grpc_return_value: list[AccountInfo] = self.stub_on_net(
            net, "GetAccountList", blockHashInput
        )

        for account in list(grpc_return_value):
            result.append(self.convertType(account))

        return result
