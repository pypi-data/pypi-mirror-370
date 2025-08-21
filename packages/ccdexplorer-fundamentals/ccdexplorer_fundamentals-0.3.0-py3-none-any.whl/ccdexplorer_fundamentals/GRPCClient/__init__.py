# ruff: noqa: F403, F405, E402
from __future__ import annotations
import os
import sys

sys.path.append(os.path.dirname("ccdexplorer_fundamentals"))
from ccdexplorer_fundamentals.GRPCClient.service_pb2_grpc import QueriesStub
from ccdexplorer_fundamentals.env import GRPC_MAINNET, GRPC_TESTNET
from ccdexplorer_fundamentals.tooter import Tooter, TooterChannel, TooterType
from ccdexplorer_fundamentals.GRPCClient.types_pb2 import *
import grpc
from ccdexplorer_fundamentals.enums import NET
import sys
import os
from rich.console import Console

console = Console()

HOME_IP = os.environ.get("HOME_IP", "")

from ccdexplorer_fundamentals.GRPCClient.queries._GetPoolInfo import (
    Mixin as _GetPoolInfo,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetPoolDelegatorsRewardPeriod import (
    Mixin as _GetPoolDelegatorsRewardPeriod,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetPassiveDelegatorsRewardPeriod import (
    Mixin as _GetPassiveDelegatorsRewardPeriod,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetAccountList import (
    Mixin as _GetAccountList,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetBakerList import (
    Mixin as _GetBakerList,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetBlocksAtHeight import (
    Mixin as _GetBlocksAtHeight,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetBlocks import (
    Mixin as _GetBlocks,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetFinalizedBlocks import (
    Mixin as _GetFinalizedBlocks,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetInstanceInfo import (
    Mixin as _GetInstanceInfo,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetInstanceList import (
    Mixin as _GetInstanceList,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetAnonymityRevokers import (
    Mixin as _GetAnonymityRevokers,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetIdentityProviders import (
    Mixin as _GetIdentityProviders,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetPoolDelegators import (
    Mixin as _GetPoolDelegators,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetPassiveDelegators import (
    Mixin as _GetPassiveDelegators,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetAccountInfo import (
    Mixin as _GetAccountInfo,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetBlockInfo import (
    Mixin as _GetBlockInfo,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetElectionInfo import (
    Mixin as _GetElectionInfo,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetTokenomicsInfo import (
    Mixin as _GetTokenomicsInfo,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetPassiveDelegationInfo import (
    Mixin as _GetPassiveDelegationInfo,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetBlockTransactionEvents import (
    Mixin as _GetBlockTransactionEvents,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetBlockSpecialEvents import (
    Mixin as _GetBlockSpecialEvents,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetBlockPendingUpdates import (
    Mixin as _GetBlockPendingUpdates,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetModuleSource import (
    Mixin as _GetModuleSource,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetBlockChainParameters import (
    Mixin as _GetBlockChainParameters,
)
from ccdexplorer_fundamentals.GRPCClient.queries._InvokeInstance import (
    Mixin as _InvokeInstance,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetConsensusInfo import (
    Mixin as _GetConsensusInfo,
)

from ccdexplorer_fundamentals.GRPCClient.queries._GetBakerEarliestWinTime import (
    Mixin as _GetBakerEarliestWinTime,
)
from ccdexplorer_fundamentals.GRPCClient.queries._CheckHealth import (
    Mixin as _CheckHealth,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetGetConsensusDetailedStatus import (
    Mixin as _GetGetConsensusDetailedStatus,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetScheduledReleaseAccounts import (
    Mixin as _GetScheduledReleaseAccounts,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetCooldownAccounts import (
    Mixin as _GetCooldownAccounts,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetPreCooldownAccounts import (
    Mixin as _GetPreCooldownAccounts,
)
from ccdexplorer_fundamentals.GRPCClient.queries._GetPrePreCooldownAccounts import (
    Mixin as _GetPrePreCooldownAccounts,
)

from ccdexplorer_fundamentals.GRPCClient.queries._GetTokenInfo import (
    Mixin as _GetTokenInfo,
)

from ccdexplorer_fundamentals.GRPCClient.queries._GetTokenList import (
    Mixin as _GetTokenList,
)

from ccdexplorer_fundamentals.GRPCClient.queries._GetWinningBakersEpoch import (
    Mixin as _GetWinningBakersEpoch,
)

# from ccdexplorer_fundamentals.GRPCClient.queries._SendBlockItem import (
#     Mixin as _SendBlockItem,
# )


class GRPCClient(
    _GetPoolInfo,
    _GetAccountList,
    _GetBakerList,
    _GetInstanceInfo,
    _GetInstanceList,
    _GetBlocks,
    _GetFinalizedBlocks,
    _GetBlocksAtHeight,
    _GetIdentityProviders,
    _GetAnonymityRevokers,
    _GetPassiveDelegationInfo,
    _GetPassiveDelegators,
    _GetPoolDelegators,
    _GetPoolDelegatorsRewardPeriod,
    _GetPassiveDelegatorsRewardPeriod,
    _GetAccountInfo,
    _GetBlockInfo,
    _GetElectionInfo,
    _GetBlockTransactionEvents,
    _GetBlockSpecialEvents,
    _GetBlockPendingUpdates,
    _GetTokenomicsInfo,
    _GetModuleSource,
    _GetBlockChainParameters,
    _InvokeInstance,
    _GetConsensusInfo,
    _GetBakerEarliestWinTime,
    _CheckHealth,
    _GetGetConsensusDetailedStatus,
    _GetScheduledReleaseAccounts,
    _GetCooldownAccounts,
    _GetPreCooldownAccounts,
    _GetPrePreCooldownAccounts,
    _GetTokenInfo,
    _GetTokenList,
    _GetWinningBakersEpoch,
    # _SendBlockItem,
):
    def __init__(self, net: str = "mainnet", devnet: bool = False):
        self.net = NET(net)
        # self.channel_mainnet: grpc.Channel
        # self.channel_testnet: grpc.Channel
        self.stub_mainnet: QueriesStub
        self.stub_testnet: QueriesStub
        # self.stub_to_net: dict[NET:QueriesStub]
        self.host_index = {NET.MAINNET: 0, NET.TESTNET: 0}
        self.hosts = {}
        self.hosts[NET.MAINNET] = GRPC_MAINNET
        if devnet:
            self.hosts[NET.MAINNET] = [
                {
                    "host": "--secure--grpc.devnet-plt-beta.concordium.com",
                    "port": 20000,
                }
            ]

        self.hosts[NET.TESTNET] = GRPC_TESTNET
        if len(GRPC_MAINNET) > 0:
            self.connect()
            self.check_connection(NET.MAINNET)
            self.check_connection(NET.TESTNET)

    def connect(self):
        host = self.hosts[NET.MAINNET][self.host_index[NET.MAINNET]]["host"]
        port = self.hosts[NET.MAINNET][self.host_index[NET.MAINNET]]["port"]

        use_secure = "--secure--" in host
        host = host.replace("--secure--", "")
        address = f"{host}:{port}"

        if use_secure:
            creds = grpc.ssl_channel_credentials()
            options = [
                ("grpc.ssl_target_name_override", "grpc.devnet-plt-beta.concordium.com")
            ]
            self.channel_mainnet = grpc.secure_channel(
                "18.200.162.59:20000", creds, options
            )
        else:
            self.channel_mainnet = grpc.insecure_channel(address)

        try:
            grpc.channel_ready_future(self.channel_mainnet).result(timeout=3)
            console.log(f"GRPCClient for {NET.MAINNET.value} connected on: {address}")
        except grpc.FutureTimeoutError:
            console.log(f"GRPC connection to {address} timed out.")

        host = self.hosts[NET.TESTNET][self.host_index[NET.TESTNET]]["host"]
        port = self.hosts[NET.TESTNET][self.host_index[NET.TESTNET]]["port"]
        self.channel_testnet = grpc.insecure_channel(f"{host}:{port}")
        try:
            grpc.channel_ready_future(self.channel_testnet).result(timeout=1)
            console.log(
                f"GRPCClient for {NET.TESTNET.value} connected on: {host}:{port}"
            )
        except grpc.FutureTimeoutError:
            pass

        self.stub_mainnet = QueriesStub(self.channel_mainnet)
        self.stub_testnet = QueriesStub(self.channel_testnet)

        self.channel = grpc.insecure_channel(
            f"{self.hosts[self.net][self.host_index[self.net]]['host']}:{self.hosts[self.net][self.host_index[self.net]]['port']}"
        )

        self.stub = QueriesStub(self.channel)

    def stub_on_net(self, net, method_name, *args):
        self.check_connection(net)
        stub = self.stub_mainnet if net == NET.MAINNET else self.stub_testnet
        method = getattr(stub, method_name, None)

        if method:
            return method(timeout=30, *args)
        else:
            return None

    def switch_to_net(self, net: str = "mainnet"):
        # only switch when we need to connect to a different net
        if not net:
            net = NET.MAINNET.value

        if net != self.net.value:
            self.net = NET(net)
            self.connect()

    def check_connection(self, net: NET = NET.MAINNET, f=None):
        connected = {NET.MAINNET: False, NET.TESTNET: False}

        while not connected[net]:
            channel_to_check = (
                self.channel_mainnet if net == NET.MAINNET else self.channel_testnet
            )
            try:
                grpc.channel_ready_future(channel_to_check).result(timeout=1)
                connected[net] = True

            except grpc.FutureTimeoutError:
                console.log(
                    f"""GRPCClient for {net.value} Timeout for :
                      {self.hosts[net][self.host_index[net]]['host']}:
                      {self.hosts[net][self.host_index[net]]['port']}"""
                )
                self.host_index[net] += 1
                if self.host_index[net] == len(self.hosts[net]):
                    self.host_index[net] = 0
                self.connect()

    def connection_info(self, caller: str, tooter: Tooter, ADMIN_CHAT_ID: int) -> None:
        message = f"<code>{caller}</code> connection status\n<code>mainnet</code> - {self.hosts[NET.MAINNET][self.host_index[NET.MAINNET]]['host']}:{self.hosts[NET.MAINNET][self.host_index[NET.MAINNET]]['port']}\n<code>testnet</code> - {self.hosts[NET.TESTNET][self.host_index[NET.TESTNET]]['host']}:{self.hosts[NET.TESTNET][self.host_index[NET.TESTNET]]['port']}\n"
        tooter.relay(
            channel=TooterChannel.NOTIFIER,
            title="",
            chat_id=ADMIN_CHAT_ID,
            body=message,
            notifier_type=TooterType.INFO,
        )

    async def aconnection_info(
        self, caller: str, tooter: Tooter, ADMIN_CHAT_ID: int
    ) -> None:
        message = f"<code>{caller}</code> connection status\n<code>mainnet</code> - {self.hosts[NET.MAINNET][self.host_index[NET.MAINNET]]['host']}:{self.hosts[NET.MAINNET][self.host_index[NET.MAINNET]]['port']}\n<code>testnet</code> - {self.hosts[NET.TESTNET][self.host_index[NET.TESTNET]]['host']}:{self.hosts[NET.TESTNET][self.host_index[NET.TESTNET]]['port']}\n"
        tooter.relay(
            channel=TooterChannel.NOTIFIER,
            title="",
            chat_id=ADMIN_CHAT_ID,
            body=message,
            notifier_type=TooterType.INFO,
        )
