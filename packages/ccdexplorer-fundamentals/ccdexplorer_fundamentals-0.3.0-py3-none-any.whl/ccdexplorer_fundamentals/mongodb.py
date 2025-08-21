# ruff: noqa :E501, F405
import datetime as dt
from enum import Enum
from typing import Dict, Optional, Union

import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel, ConfigDict, Field
from pymongo import MongoClient, ReadPreference
from pymongo.collection import Collection
from rich.console import Console

from ccdexplorer_fundamentals.env import MONGO_URI
from ccdexplorer_fundamentals.GRPCClient.CCD_Types import *  # noqa: F403
from ccdexplorer_fundamentals.mongodb_queries._apy_calculations import (
    Mixin as _apy_calculations,
)
from ccdexplorer_fundamentals.mongodb_queries._baker_distributions import (
    Mixin as _distributions,
)
from ccdexplorer_fundamentals.mongodb_queries._search_transfers import (
    Mixin as _search_transfers,
)
from ccdexplorer_fundamentals.mongodb_queries._store_block import Mixin as _store_block
from ccdexplorer_fundamentals.mongodb_queries._subscriptions import (
    Mixin as _subscriptions,
)
from ccdexplorer_fundamentals.tooter import Tooter, TooterChannel, TooterType

console = Console()


class MongoLabeledAccount(BaseModel):
    """
    MongoLabeledAccount represents a labeled account in a MongoDB collection.

    Attributes:
        id (str): The unique identifier for the account, mapped from the MongoDB "_id" field.
        account_index (Optional[CCD_AccountIndex]): The index of the account, if available.
        label (str): The label associated with the account.
        label_group (str): The group to which the label belongs.
    """

    id: str = Field(..., alias="_id")
    account_index: Optional[CCD_AccountIndex] = None
    label: str
    label_group: str


class AccountStatementEntry(BaseModel):
    """
    AccountStatementEntry represents an entry in an account statement.

    Attributes:
        block_height (int): The height of the block in the blockchain.
        slot_time (dt.datetime): The timestamp of the slot.
        entry_type (str): The type of the entry (e.g., transaction, reward).
        amount (microCCD): The amount involved in the entry.
        balance (microCCD): The balance after the entry.
    """

    block_height: int
    slot_time: dt.datetime
    entry_type: str
    amount: microCCD
    balance: microCCD


class AccountStatementTransferType(BaseModel):
    """
    AccountStatementTransferType represents a transfer type in an account statement.

    Attributes:
        amount (microCCD): The amount of the transfer in microCCD.
        counterparty (str): The counterparty involved in the transfer.
    """

    amount: microCCD
    counterparty: str


class AccountStatementEntryType(BaseModel):
    """
    AccountStatementEntryType represents the structure of an account statement entry.

    Attributes:
        amount_decrypted (Optional[microCCD]): The decrypted amount in the account statement entry.
        amount_encrypted (Optional[microCCD]): The encrypted amount in the account statement entry.
        baker_reward (Optional[microCCD]): The reward received from baking.
        finalization_reward (Optional[microCCD]): The reward received from finalization.
        foundation_reward (Optional[microCCD]): The reward received from the foundation.
        transaction_fee (Optional[microCCD]): The transaction fee associated with the account statement entry.
        transaction_fee_reward (Optional[microCCD]): The reward received from transaction fees.
        transfer_in (Optional[list[AccountStatementTransferType]]): List of incoming transfers.
        transfer_out (Optional[list[AccountStatementTransferType]]): List of outgoing transfers.
    """

    amount_decrypted: Optional[microCCD] = None
    amount_encrypted: Optional[microCCD] = None
    baker_reward: Optional[microCCD] = None
    finalization_reward: Optional[microCCD] = None
    foundation_reward: Optional[microCCD] = None
    transaction_fee: Optional[microCCD] = None
    transaction_fee_reward: Optional[microCCD] = None
    transfer_in: Optional[list[AccountStatementTransferType]] = None
    transfer_out: Optional[list[AccountStatementTransferType]] = None


class MongoImpactedAddress(BaseModel):
    """
    MongoImpactedAddress is a data model representing an impacted address in a MongoDB collection.

    Attributes:
        id (str): The unique identifier for the impacted address, mapped from the MongoDB "_id" field.
        tx_hash (Optional[str]): The transaction hash associated with the impacted address. Rewards do not have a transaction hash.
        impacted_address (str): The impacted address.
        impacted_address_canonical (str): The canonical form of the impacted address.
        effect_type (str): The type of effect on the impacted address.
        balance_movement (Optional[AccountStatementEntryType]): The balance movement associated with the impacted address.
        block_height (int): The block height at which the impact occurred.
        included_in_flow (Optional[bool]): Indicates whether the impacted address is included in the flow.
        date (Optional[str]): The date when the impact occurred.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str = Field(..., alias="_id")
    tx_hash: Optional[str] = None  # Rewards do not have a tx
    impacted_address: str
    impacted_address_canonical: str
    effect_type: str
    balance_movement: Optional[AccountStatementEntryType] = None
    block_height: int
    included_in_flow: Optional[bool] = None
    date: Optional[str] = None


class MongoTokensImpactedAddress(BaseModel):
    """
    MongoTokensImpactedAddress is a Pydantic model representing a MongoDB document for tokens impacted by an address.

    Attributes:
        id (str): The unique identifier for the document, mapped from MongoDB's "_id" field.
        tx_hash (str): The transaction hash associated with the impacted address.
        impacted_address (str): The address that was impacted.
        impacted_address_canonical (str): The canonical form of the impacted address.
        event_type (str): The type of event that impacted the address.
        token_address (Optional[str]): The address of the token, if applicable.
        contract (Optional[str]): The contract associated with the token, if applicable.
        block_height (int): The block height at which the event occurred.
        date (str): The date when the event occurred.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str = Field(..., alias="_id")
    tx_hash: str
    impacted_address: str
    impacted_address_canonical: str
    event_type: str
    token_address: Optional[str] = None
    contract: Optional[str] = None
    block_height: int
    date: str


class MongoTypeBlockPerDay(BaseModel):
    """
    Block Per Day. This type is stored in the collection `blocks_per_day`.

    :Parameters:
    - `_id`: the date of the day that ended
    - `date`: the date of the day that ended
    - `height_for_first_block`: height of the first block in the day
    - `height_for_last_block`: height of the last block in the day
    - `slot_time_for_first_block`: time of the first block in the day
    - `slot_time_for_last_block`: time of the last block in the day
    - `hash_for_first_block`: hash of the first block in the day
    - `hash_for_last_block`: hash of the last block in the day

    """

    id: str = Field(..., alias="_id")
    date: str
    height_for_first_block: int
    height_for_last_block: int
    slot_time_for_first_block: dt.datetime
    slot_time_for_last_block: dt.datetime
    hash_for_first_block: str
    hash_for_last_block: str


class MongoTypeInvolvedAccount(BaseModel):
    """
    Involved Account. This type is stored in the collections `involved_accounts_all` and
    `involved_accounts_transfer`.

    :Parameters:
    - `_id`: the hash of the transaction
    - `sender`: the sender account address
    - `receiver`: the receiver account address, might be null
    - `sender_canonical`: the canonical sender account address
    - `receiver_canonical`: the  canonical receiver account address, might be null
    - `amount`: amount of the transaction, might be null
    - `type`: dict with transaction `type` and `contents`
    - `block_height`: height of the block in which the transaction is executed
    """

    id: str = Field(..., alias="_id")
    sender: str
    receiver: Optional[str] = None
    sender_canonical: str
    receiver_canonical: Optional[str] = None
    amount: Optional[int] = None
    type: dict[str, str]
    block_height: int
    memo: Optional[str] = None


class MongoTypeInvolvedContract(BaseModel):
    """
    Involved Contract. This type is stored in the collection `involved_contracts`.

    :Parameters:
    - `_id`: the hash of the transaction - the `str` representation of the contract.
    - `index`: contract index
    - `subindex`: contract subindex
    - `contract`: the `str` representation of the contract
    - `type`: dict with transaction `type` and `contents`
    - `block_height`: height of the block in which the transaction is executed
    - `source_module`: hash of the source module from which this contract is instanciated.
    """

    id: str = Field(..., alias="_id")
    index: int
    subindex: int
    contract: str
    type: dict[str, str]
    block_height: int
    source_module: str


class ModuleVerification(BaseModel):
    """
    ModuleVerification represents the verification details of a module.

    Attributes:
        verified (Optional[bool]): Indicates if the module is verified. Defaults to False.
        verification_status (str): The status of the verification process.
        verification_timestamp (Optional[dt.datetime]): The timestamp when the verification was performed. Defaults to None.
        explanation (Optional[str]): An optional explanation of the verification status. Defaults to None.
        build_image_used (Optional[str]): The build image used during verification. Defaults to None.
        build_command_used (Optional[str]): The build command used during verification. Defaults to None.
        archive_hash (Optional[str]): The hash of the archive used during verification. Defaults to None.
        link_to_source_code (Optional[str]): A link to the source code of the module. Defaults to None.
        source_code_at_verification_time (Optional[str]): The source code at the time of verification. Defaults to None.
    """

    verified: Optional[bool] = False
    verification_status: str
    verification_timestamp: Optional[dt.datetime] = None
    explanation: Optional[str] = None
    build_image_used: Optional[str] = None
    build_command_used: Optional[str] = None
    archive_hash: Optional[str] = None
    link_to_source_code: Optional[str] = None
    source_code_at_verification_time: Optional[str] = None


class MongoTypeModule(BaseModel):
    """
    MongoTypeModule represents a module stored in the `modules` collection.

    Attributes:
        id (str): The hex string identifier for the module, stored as `_id` in the database.
        module_name (str): The name of the module.
        methods (Optional[list[str]]): A list of method names associated with the module.
        contracts (Optional[list[str]]): A list of contract instances from this module.
        init_date (Optional[dt.datetime]): The initialization date of the module.
        verification (Optional[ModuleVerification]): The verification details of the module.
    """

    id: str = Field(..., alias="_id")
    module_name: Optional[str] = None
    methods: Optional[list[str]] = None
    contracts: Optional[list[str]] = None
    init_date: Optional[dt.datetime] = None
    verification: Optional[ModuleVerification] = None


class MongoTypeInstance(BaseModel):
    """
    Instance. This type is stored in the collection `instances`.

    :Parameters:
    - `_id`: the hex string
    - `module_name`: the name from the module
    - `methods`: list of method names
    - `contracts`: list of contract instances from this module
    """

    id: str = Field(..., alias="_id")
    v0: Optional[CCD_InstanceInfo_V0] = None  # noqa: F405
    v1: Optional[CCD_InstanceInfo_V1] = None  # noqa: F405
    source_module: Optional[str] = None
    module_verification: Optional[ModuleVerification] = None


class MongoTypeReward(BaseModel):
    """
    Module. This type is stored in the collection `payday_rewards`, property `reward`.

    """

    pool_owner: Optional[Union[int, str]] = None
    account_id: Optional[str] = None
    transaction_fees: int
    baker_reward: int
    finalization_reward: int


class MongoTypePoolReward(BaseModel):
    """
    Module. This type is stored in the collection `payday_rewards`.

    :Parameters:
    - `_id`: the hex string

    """

    id: str = Field(..., alias="_id")
    pool_owner: Union[int, str]
    pool_status: dict
    reward: MongoTypeReward
    date: str


class MongoTypeAccountReward(BaseModel):
    """
    Module. This type is stored in the collection `payday_rewards`.

    :Parameters:
    - `_id`: the hex string
    - `module_name`: the name from the module
    - `methods`: list of method names
    - `contracts`: list of contract instances from this module
    """

    id: str = Field(..., alias="_id")
    account_id: str
    staked_amount: int
    account_is_baker: Optional[bool] = None
    baker_id: Optional[int] = None
    reward: MongoTypeReward
    date: str


class Delegator(BaseModel):
    account: str
    stake: int


class MongoTypePayday(BaseModel):
    """
    Payday. This type is stored in collection `paydays`.

    :Parameters:
    - `_id`: hash of the block that contains payday information for
    this payday.
    - `date`: the payday date
    - `height_for_first_block`: height of the first block in the payday
    - `height_for_last_block`: height of the last block in the payday
    - `hash_for_first_block`: hash of the first block in the payday
    - `hash_for_last_block`: hash of the last block in the payday
    - `payday_duration_in_seconds`: duration of the payday in seconds (used for
    APY calculation)
    - `payday_block_slot_time`: time of payday reward block
    - `bakers_with_delegation_information`: bakers with delegators for reward period, retrieved
    from `get_delegators_for_pool_in_reward_period`, using the hash of the last block
    - `baker_account_ids`: mapping from baker_id to account_address
    - `pool_status_for_bakers`: dictionary, keyed on pool_status, value
    is a list of bakers, retrieved using the hash of the first block
    """

    id: str = Field(..., alias="_id")
    date: str
    height_for_first_block: int
    height_for_last_block: int
    hash_for_first_block: str
    hash_for_last_block: str
    payday_duration_in_seconds: float
    payday_block_slot_time: dt.datetime
    bakers_with_delegation_information: dict[str, list[Delegator]]
    baker_account_ids: dict[int, str]
    pool_status_for_bakers: Optional[dict[str, list[int]]] = None


class MongoTypePaydayV2(BaseModel):
    """
    Payday. This type is stored in collection `paydays_v2`.

    :Parameters:
    - `_id`: hash of the block that contains payday information for
    this payday.
    - `date`: the payday date
    - `height_for_first_block`: height of the first block in the payday
    - `height_for_last_block`: height of the last block in the payday
    - `hash_for_first_block`: hash of the first block in the payday
    - `hash_for_last_block`: hash of the last block in the payday
    - `payday_duration_in_seconds`: duration of the payday in seconds (used for
    APY calculation)
    - `payday_block_slot_time`: time of payday reward block
    """

    id: str = Field(..., alias="_id")
    date: str
    height_for_first_block: int
    height_for_last_block: int
    hash_for_first_block: str
    hash_for_last_block: str
    payday_duration_in_seconds: float
    payday_block_slot_time: dt.datetime


class MongoTypePaydayAPYIntermediate(BaseModel):
    """
    Payday APY Intermediate. This type is stored in collection `paydays_apy_intermediate`.

    :Parameters:
    - `_id`: baker_is or account address

    """

    id: str = Field(..., alias="_id")
    daily_apy_dict: dict
    d30_apy_dict: Optional[dict] = None
    d90_apy_dict: Optional[dict] = None
    d180_apy_dict: Optional[dict] = None


class MongoTypePaydaysPerformance(BaseModel):
    """
    Payday Performance. This is a collection that stores daily performance characteristics
    for bakers.


    :Parameters:
    - `_id`: unique id in the form of `date`-`baker_id`
    - `expectation`: the daily expected number of blocks for this baker in this payday.
    Calculated as the lottery power * 8640 (the expected number of blocks in a day)
    - `payday_block_slot_time`: Slot time of the payday block
    - `baker_id`: the baker_id
    - `pool_status`:

    """

    id: str = Field(..., alias="_id")
    pool_status: CCD_PoolInfo  # noqa: F405
    expectation: float
    date: str
    payday_block_slot_time: dt.datetime
    baker_id: str


class Collections(Enum):
    """
    Enum class representing various MongoDB collection names used in the application.

    Attributes:
        all_account_addresses: Collection for all account addresses.
        blocks: Collection for blocks.
        blocks_log: Collection for blocks log.
        transactions: Collection for transactions.
        special_events: Collection for special events.
        instances: Collection for instances.
        modules: Collection for modules.
        paydays: Collection for paydays.
        paydays_performance: Collection for paydays performance.
        paydays_rewards: Collection for paydays rewards.
        paydays_apy_intermediate: Collection for paydays APY intermediate.
        paydays_current_payday: Collection for current payday.
        paydays_helpers: Collection for payday helpers.
        involved_accounts_transfer: Collection for involved accounts transfer.
        nightly_accounts: Collection for nightly accounts.
        blocks_at_end_of_day: Collection for blocks at end of day.
        blocks_per_day: Collection for blocks per day.
        helpers: Collection for helpers.
        memo_transaction_hashes: Collection for memo transaction hashes.
        cns_domains: Collection for CNS domains.
        dashboard_nodes: Collection for dashboard nodes.
        tokens_accounts: Collection for token accounts.
        tokens_links_v2: Collection for token links version 2.
        tokens_links_v3: Collection for token links version 3.
        tokens_token_addresses_v2: Collection for token addresses version 2.
        tokens_tags: Collection for token tags.
        tokens_logged_events: Collection for token logged events.
        tokens_logged_events_v2: Collection for token logged events version 2.
        tokens_token_addresses: Collection for token addresses.
        memos_to_hashes: Collection for memos to hashes.
        credentials_issuers: Collection for credential issuers.
        impacted_addresses: Collection for impacted addresses.
        impacted_addresses_pre_payday: Collection for impacted addresses pre-payday.
        impacted_addresses_all_top_list: Collection for all top list of impacted addresses.
        pre_tokens_overview: Collection for pre-rendered tokens overview.
        pre_addresses_by_contract_count: Collection for pre-rendered addresses by contract count.
        pre_tokens_by_address: Collection for pre-rendered tokens by address.
        statistics: Collection for statistics.
        pre_render: Collection for pre-rendered data.
        cis5_public_keys_contracts: Collection for CIS5 public keys contracts.
        cis5_public_keys_info: Collection for CIS5 public keys info.
        projects: Collection for projects.
        usecases: Collection for use cases.
        tokens_impacted_addresses: Collection for tokens impacted addresses.
        tnt_logged_events: Collection for TNT logged events.
        queue_todo: Collection for queue to-do items.
        tx_types_count: Collection for transaction types count.
    """

    all_account_addresses = "all_account_addresses"
    blocks = "blocks"
    blocks_log = "blocks_log"
    transactions = "transactions"
    special_events = "special_events"
    instances = "instances"
    modules = "modules"
    paydays = "paydays"
    paydays_performance = "paydays_performance"
    paydays_rewards = "paydays_rewards"
    paydays_apy_intermediate = "paydays_apy_intermediate"
    paydays_current_payday = "paydays_current_payday"
    paydays_v2 = "paydays_v2"
    paydays_v2_performance = "paydays_v2_performance"
    paydays_v2_rewards = "paydays_v2_rewards"
    paydays_v2_apy = "paydays_v2_apy"
    paydays_v2_current_payday = "paydays_v2_current_payday"
    paydays_helpers = "paydays_helpers"
    involved_accounts_transfer = "involved_accounts_transfer"
    nightly_accounts = "nightly_accounts"
    blocks_at_end_of_day = "blocks_at_end_of_day"
    blocks_per_day = "blocks_per_day"
    helpers = "helpers"
    memo_transaction_hashes = "memo_transaction_hashes"
    cns_domains = "cns_domains"
    dashboard_nodes = "dashboard_nodes"
    tokens_accounts = "tokens_accounts"
    tokens_links_v2 = "tokens_links_v2"
    tokens_links_v3 = "tokens_links_v3"
    tokens_token_addresses_v2 = "tokens_token_addresses_v2"
    tokens_tags = "tokens_tags"
    tokens_logged_events = "tokens_logged_events"
    tokens_logged_events_v2 = "tokens_logged_events_v2"
    tokens_token_addresses = "tokens_token_addresses"
    memos_to_hashes = "memos_to_hashes"
    credentials_issuers = "credentials_issuers"
    impacted_addresses = "impacted_addresses"
    impacted_addresses_pre_payday = "impacted_addresses_pre_payday"
    impacted_addresses_all_top_list = "impacted_addresses_all_top_list"
    # statistics and pre-renders
    pre_tokens_overview = "pre_tokens_overview"
    pre_addresses_by_contract_count = "pre_addresses_by_contract_count"
    pre_tokens_by_address = "pre_tokens_by_address"
    statistics = "statistics"
    pre_render = "pre_render"
    cis5_public_keys_contracts = "cis5_public_keys_contracts"
    cis5_public_keys_info = "cis5_public_keys_info"
    tx_types_count = "tx_types_count"
    # addresses and contracts per net per usecase
    projects = "projects"
    usecases = "usecases"
    tokens_impacted_addresses = "tokens_impacted_addresses"
    tnt_logged_events = "tnt_logged_events"
    queue_todo = "queue_todo"
    validator_logs = "validator_logs"
    blocks_with_only_chain_txs = "blocks_with_only_chain_txs"


class CollectionsUtilities(Enum):
    """
    Enum class representing various MongoDB collection names used in the application.

    Attributes:
        labeled_accounts (str): Collection name for labeled accounts.
        labeled_accounts_metadata (str): Collection name for labeled accounts metadata.
        exchange_rates (str): Collection name for exchange rates.
        exchange_rates_historical (str): Collection name for historical exchange rates.
        users_v2_prod (str): Collection name for production users (version 2).
        users_v2_dev (str): Collection name for development users (version 2).
        message_log (str): Collection name for message logs.
        preferences_explanations (str): Collection name for preferences explanations.
        release_notes (str): Collection name for release notes.
        token_api_translations (str): Collection name for token API translations.
        projects (str): Collection name for projects (use case management).
        usecases (str): Collection name for use cases (use case management).
        helpers (str): Collection name for helpers (use case management).
        api_api_keys (str): Collection name for API keys.
        api_users (str): Collection name for API users.
    """

    labeled_accounts = "labeled_accounts"
    labeled_accounts_metadata = "labeled_accounts_metadata"
    exchange_rates = "exchange_rates"
    exchange_rates_historical = "exchange_rates_historical"
    users_v2_prod = "users_v2_prod"
    users_v2_dev = "users_v2_dev"
    message_log = "message_log"
    preferences_explanations = "preferences_explanations"
    release_notes = "release_notes"
    token_api_translations = "token_api_translations"
    # use case management
    projects = "projects"
    usecases = "usecases"
    helpers = "helpers"
    # api
    api_api_keys = "api_api_keys"
    # api
    api_users = "api_users"


class MongoDB(
    _search_transfers,
    _subscriptions,
    _distributions,
    _store_block,
    _apy_calculations,
):
    def __init__(self, tooter: Tooter, nearest: bool = False):
        self.tooter: Tooter = tooter
        try:
            if nearest:
                con = MongoClient(MONGO_URI, read_preference=ReadPreference.NEAREST)
            else:
                con = MongoClient(MONGO_URI)
            self.connection: MongoClient = con

            self.mainnet_db = con["concordium_mainnet"]
            self.mainnet: Dict[Collections, Collection] = {}
            for collection in Collections:
                self.mainnet[collection] = self.mainnet_db[collection.value]

            self.testnet_db = con["concordium_testnet"]
            self.testnet: Dict[Collections, Collection] = {}
            for collection in Collections:
                self.testnet[collection] = self.testnet_db[collection.value]

            self.devnet_db = con["concordium_devnet"]
            self.devnet: Dict[Collections, Collection] = {}
            for collection in Collections:
                self.devnet[collection] = self.devnet_db[collection.value]

            self.utilities_db = con["concordium_utilities"]
            self.utilities: Dict[CollectionsUtilities, Collection] = {}
            for collection in CollectionsUtilities:
                self.utilities[collection] = self.utilities_db[collection.value]

            console.log(con.server_info()["version"])
        except Exception as e:
            print(e)
            tooter.send(
                channel=TooterChannel.NOTIFIER,
                message=f"BOT ERROR! Cannot connect to MongoDB, with error: {e}",
                notifier_type=TooterType.MONGODB_ERROR,
            )


class MongoMotor(
    _search_transfers,
    _subscriptions,
    _distributions,
    _store_block,
    _apy_calculations,
):
    def __init__(self, tooter: Tooter, nearest: bool = False):
        self.tooter: Tooter = tooter
        try:
            if nearest:
                con = motor.motor_asyncio.AsyncIOMotorClient(
                    MONGO_URI, read_preference=ReadPreference.NEAREST
                )
            else:
                con = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
            self.connection = con

            self.mainnet_db = con["concordium_mainnet"]
            self.mainnet: Dict[Collections, AsyncIOMotorCollection] = {}  # type: ignore
            for collection in Collections:
                self.mainnet[collection] = self.mainnet_db[collection.value]

            self.testnet_db = con["concordium_testnet"]
            self.testnet: Dict[Collections, AsyncIOMotorCollection] = {}  # type: ignore
            for collection in Collections:
                self.testnet[collection] = self.testnet_db[collection.value]

            self.utilities_db = con["concordium_utilities"]
            self.utilities: Dict[CollectionsUtilities, AsyncIOMotorCollection] = {}  # type: ignore
            for collection in CollectionsUtilities:
                self.utilities[collection] = self.utilities_db[collection.value]
            # console.log(f'Motor: {con.server_info()["version"]}')
        except Exception as e:
            print(e)
            tooter.send(
                channel=TooterChannel.NOTIFIER,
                message=f"BOT ERROR! Cannot connect to Motor MongoDB, with error: {e}",
                notifier_type=TooterType.MONGODB_ERROR,
            )
