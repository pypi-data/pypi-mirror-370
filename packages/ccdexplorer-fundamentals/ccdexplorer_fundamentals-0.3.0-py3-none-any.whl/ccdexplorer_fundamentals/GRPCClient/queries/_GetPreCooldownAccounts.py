# ruff: noqa: F403, F405, E402
from __future__ import annotations
from ccdexplorer_fundamentals.GRPCClient.types_pb2 import *
from ccdexplorer_fundamentals.enums import NET
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccdexplorer_fundamentals.GRPCClient import GRPCClient
from ccdexplorer_fundamentals.GRPCClient.queries._SharedConverters import (
    Mixin as _SharedConverters,
)
import os
import sys

sys.path.append(os.path.dirname("ccdexplorer_fundamentals"))
from ccdexplorer_fundamentals.GRPCClient.CCD_Types import *


class Mixin(_SharedConverters):
    def get_pre_cooldown_accounts(
        self: GRPCClient,
        block_hash: str,
        net: Enum = NET.MAINNET,
    ) -> list[CCD_AccountIndex]:
        result = {}
        result = []
        blockHashInput = self.generate_block_hash_input_from(block_hash)

        grpc_return_value: list[CCD_AccountIndex] = self.stub_on_net(
            net, "GetPreCooldownAccounts", blockHashInput
        )

        for account_index in list(grpc_return_value):
            result.append(account_index.value)

        return result
