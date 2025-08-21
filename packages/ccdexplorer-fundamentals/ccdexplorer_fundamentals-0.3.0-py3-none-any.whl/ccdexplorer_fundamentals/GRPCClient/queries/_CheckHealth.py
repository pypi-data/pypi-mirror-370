from __future__ import annotations
from ccdexplorer_fundamentals.GRPCClient.service_pb2_grpc import QueriesStub
from ccdexplorer_fundamentals.GRPCClient.types_pb2 import *
from ccdexplorer_fundamentals.GRPCClient.health_pb2 import *
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccdexplorer_fundamentals.GRPCClient import GRPCClient
from ccdexplorer_fundamentals.GRPCClient.queries._SharedConverters import (
    Mixin as _SharedConverters,
)
import os
import sys
from rich import print

sys.path.append(os.path.dirname("ccdexplorer_fundamentals"))
from ccdexplorer_fundamentals.GRPCClient.CCD_Types import *


class Mixin(_SharedConverters):
    def check_health(self: GRPCClient):
        result = {}

        self.check_connection(sys._getframe().f_code.co_name)
        grpc_return_value: NodeHealthResponse = self.health.Check(
            request=NodeHealthRequest()
        )

        return grpc_return_value
