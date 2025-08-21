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
    def convertSuccess(self, message) -> CCD_InvokeInstanceResponse_Success:
        result = {}
        for descriptor in message.DESCRIPTOR.fields:
            key, value = self.get_key_value_from_descriptor(descriptor, message)
            if key == "effects":
                result[key] = self.convertUpdateEvents(value)

            elif type(value) in self.simple_types:
                result[key] = self.convertType(value)

        return CCD_InvokeInstanceResponse_Success(**result)

    def convertFailure(self, message) -> CCD_InvokeInstanceResponse_Failure:
        result = {}
        for descriptor in message.DESCRIPTOR.fields:
            key, value = self.get_key_value_from_descriptor(descriptor, message)
            if type(value) is RejectReason:
                result[key], _ = self.convertRejectReason(value)

            elif type(value) in self.simple_types:
                result[key] = self.convertType(value)

        return CCD_InvokeInstanceResponse_Failure(**result)

    def invoke_instance(
        self: GRPCClient,
        block_hash: str,
        instance_index: int,
        instance_subindex: int,
        entrypoint: str,
        parameter_bytes: bytes,
        net: Enum = NET.MAINNET,
    ) -> CCD_InvokeInstanceResponse:
        result = {}
        blockHashInput = self.generate_block_hash_input_from(block_hash)
        invokeInstanceRequest = self.generate_invoke_instance_request_from(
            instance_index,
            instance_subindex,
            blockHashInput,
            entrypoint,
            parameter_bytes,
        )

        grpc_return_value: InvokeInstanceResponse = self.stub_on_net(
            net, "InvokeInstance", invokeInstanceRequest
        )

        for descriptor in grpc_return_value.DESCRIPTOR.fields:
            key, value = self.get_key_value_from_descriptor(
                descriptor, grpc_return_value
            )

            if type(value) is InvokeInstanceResponse.Success:
                result[key] = self.convertSuccess(value)

            elif type(value) is InvokeInstanceResponse.Failure:
                result[key] = self.convertFailure(value)

        return CCD_InvokeInstanceResponse(**result)
