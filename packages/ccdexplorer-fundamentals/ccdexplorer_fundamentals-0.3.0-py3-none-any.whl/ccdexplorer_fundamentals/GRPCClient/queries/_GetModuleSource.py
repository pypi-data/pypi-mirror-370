# ruff: noqa: F403, F405, E402
from __future__ import annotations
from ccdexplorer_fundamentals.GRPCClient.types_pb2 import *
from ccdexplorer_fundamentals.enums import NET
from ccdexplorer_fundamentals.GRPCClient.queries._SharedConverters import (
    Mixin as _SharedConverters,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccdexplorer_fundamentals.GRPCClient import GRPCClient
import os
import sys

sys.path.append(os.path.dirname("ccdexplorer_fundamentals"))
from ccdexplorer_fundamentals.GRPCClient.CCD_Types import *


class Mixin(_SharedConverters):
    def convertMethods(self, message) -> list[CCD_ReceiveName]:
        methods = []
        for method in message:
            for descriptor in method.DESCRIPTOR.fields:
                _, value = self.get_key_value_from_descriptor(descriptor, method)

                methods.append(self.convertType(value))

        return methods

    def convertInstanceInfo_V0(self, message) -> CCD_InstanceInfo_V0:
        result = {}
        for descriptor in message.DESCRIPTOR.fields:
            key, value = self.get_key_value_from_descriptor(descriptor, message)

            if type(value) in self.simple_types:
                result[key] = self.convertType(value)

            elif key == "methods":
                result[key] = self.convertMethods(value)

        return CCD_InstanceInfo_V0(**result)

    def convertInstanceInfo_V1(self, message) -> CCD_InstanceInfo_V1:
        result = {}
        for descriptor in message.DESCRIPTOR.fields:
            key, value = self.get_key_value_from_descriptor(descriptor, message)

            if type(value) in self.simple_types:
                result[key] = self.convertType(value)

            elif key == "methods":
                result[key] = self.convertMethods(value)

        return CCD_InstanceInfo_V1(**result)

    def get_module_source(
        self: GRPCClient,
        module_ref: CCD_ModuleRef,
        block_hash: str,
        net: Enum = NET.MAINNET,
    ) -> CCD_VersionedModuleSource:
        result = {}
        moduleSourceRequest = self.generate_module_source_request_from(
            module_ref, block_hash
        )

        grpc_return_value: VersionedModuleSource = self.stub_on_net(
            net, "GetModuleSource", moduleSourceRequest
        )

        for field, value in grpc_return_value.ListFields():
            key = field.name
            if type(value) in [
                VersionedModuleSource.ModuleSourceV0,
                VersionedModuleSource.ModuleSourceV1,
            ]:
                result[key] = self.convertType(value)

        return CCD_VersionedModuleSource(**result)

    def get_module_source_original_classes(
        self: GRPCClient,
        module_ref: CCD_ModuleRef,
        block_hash: str,
        net: Enum = NET.MAINNET,
    ) -> VersionedModuleSource:
        result = {}
        moduleSourceRequest = self.generate_module_source_request_from(
            module_ref, block_hash
        )

        grpc_return_value: VersionedModuleSource = self.stub_on_net(
            net, "GetModuleSource", moduleSourceRequest
        )

        for field, value in grpc_return_value.ListFields():
            key = field.name
            if type(value) in [
                VersionedModuleSource.ModuleSourceV0,
                VersionedModuleSource.ModuleSourceV1,
            ]:
                result[key] = value

        return VersionedModuleSource(**result)
