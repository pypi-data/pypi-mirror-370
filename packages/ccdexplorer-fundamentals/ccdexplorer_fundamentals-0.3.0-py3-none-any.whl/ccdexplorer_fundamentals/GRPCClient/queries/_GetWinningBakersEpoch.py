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
    def get_winning_bakers_epoch(
        self: GRPCClient,  # type: ignore
        genesis_index: int,
        epoch: int,
        net: Enum = NET.MAINNET,
    ) -> list[CCD_WinningBaker]:
        epoch_request = self.generate_epoch_request_from_genesis(
            genesis_index=genesis_index, epoch=epoch
        )

        grpc_return_value: list[CCD_WinningBaker] | None = self.stub_on_net(
            net, "GetWinningBakersEpoch", epoch_request
        )

        if grpc_return_value is None:
            return []

        result = []
        for winner in list(grpc_return_value):
            result.append(self.convertWinningBaker(winner))

        return result
