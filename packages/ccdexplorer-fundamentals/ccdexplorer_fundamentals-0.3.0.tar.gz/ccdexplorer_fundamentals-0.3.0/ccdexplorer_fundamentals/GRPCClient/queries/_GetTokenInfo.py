# ruff: noqa: F403, F405, E402
from __future__ import annotations
from ccdexplorer_fundamentals.GRPCClient.types_pb2 import TokenInfoRequest, TokenInfo
from ccdexplorer_fundamentals.GRPCClient.protocol_level_tokens_pb2 import (
    TokenId,
    TokenState,
    TokenAmount,
)
from google.protobuf import message
from ccdexplorer_fundamentals.GRPCClient.queries._SharedConverters import (
    Mixin as _SharedConverters,
)
import cbor2
import os
import sys
from ccdexplorer_fundamentals.enums import NET
from typing import TYPE_CHECKING


sys.path.append(os.path.dirname("ccdexplorer_fundamentals"))
from ccdexplorer_fundamentals.GRPCClient.CCD_Types import *

sys.path.append(os.path.dirname("ccdexplorer_fundamentals"))
if TYPE_CHECKING:
    from ccdexplorer_fundamentals.GRPCClient import GRPCClient


class Mixin(_SharedConverters):
    def convertTokenState(self, message: message.Message) -> CCD_TokenState:
        keys = {}

        for descriptor in message.DESCRIPTOR.fields:
            key, value = self.get_key_value_from_descriptor(descriptor, message)

            if key == "module_state":
                cbor_decoded = cbor2.loads(value.value)
                if "governanceAccount" in cbor_decoded:
                    cbor_decoded["governanceAccount"] = self.convert_GovernanceAccount(
                        cbor_decoded
                    )
                keys[key] = CCD_ModuleState(**cbor_decoded)

            elif type(value) in self.simple_types:
                keys[key] = self.convertType(value)
            elif type(value) is TokenAmount:
                keys[key] = CCD_TokenAmount(
                    **{"value": str(value.value), "decimals": value.decimals}
                )

        return CCD_TokenState(**keys)

    def get_token_info(
        self: GRPCClient,  # type: ignore
        block_hash: str,
        token_id: str,
        net: Enum = NET.MAINNET,
    ) -> CCD_TokenInfo:
        blockHashInput = self.generate_block_hash_input_from(block_hash)

        token_info_request = TokenInfoRequest(
            block_hash=blockHashInput, token_id=TokenId(value=token_id)
        )

        grpc_return_value: TokenInfo = self.stub_on_net(
            net, "GetTokenInfo", token_info_request
        )  # type: ignore

        result = {}
        for descriptor in grpc_return_value.DESCRIPTOR.fields:
            key, value = self.get_key_value_from_descriptor(
                descriptor, grpc_return_value
            )
            if type(value) in self.simple_types:
                result[key] = self.convertType(value)

            elif isinstance(value, TokenState):
                result[key] = self.convertTokenState(value)

        return CCD_TokenInfo(**result)
