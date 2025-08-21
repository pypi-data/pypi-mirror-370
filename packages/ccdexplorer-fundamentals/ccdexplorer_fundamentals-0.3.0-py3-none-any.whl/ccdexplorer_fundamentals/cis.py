from __future__ import annotations

import datetime as dt
import io
from enum import Enum
from typing import Literal, Optional, Any, Union

import base58
import leb128
from pydantic import BaseModel, ConfigDict, Field
from pymongo import ReplaceOne
from pymongo.collection import Collection
from rich.console import Console

from ccdexplorer_fundamentals.enums import NET
from ccdexplorer_fundamentals.GRPCClient import GRPCClient
from ccdexplorer_fundamentals.GRPCClient.CCD_Types import (
    CCD_AccountAddress,
    CCD_ContractAddress,
    CCD_BlockItemSummary,
    microCCD,
)
from ccdexplorer_fundamentals.mongodb import Collections

console = Console()

LEN_ACCOUNT_ADDRESS = 50


class MongoTypeTokenForAddress(BaseModel):
    """
    MongoTypeTokenForAddress is a data model representing a token for an address in a MongoDB database.

    Attributes:
        token_address (str): The address of the token.
        contract (str): The contract associated with the token.
        token_id (str): The unique identifier of the token.
        token_amount (str): The amount of the token.
    """

    model_config = ConfigDict(coerce_numbers_to_str=True)
    token_address: str
    contract: str
    token_id: str
    token_amount: str


class MongoTypeTokenLink(BaseModel):
    """
    MongoTypeTokenLink is a model representing a link between a token and an account in a MongoDB database.

    Attributes:
        id (str): The unique identifier for the token link, mapped to the MongoDB "_id" field.
        account_address (Optional[str]): The address of the account holding the token.
        account_address_canonical (Optional[str]): The canonical form of the account address.
        token_holding (Optional[MongoTypeTokenForAddress]): The token holding details for the account.
    """

    id: str = Field(..., alias="_id")
    account_address: Optional[str] = None
    account_address_canonical: Optional[str] = None
    token_holding: Optional[MongoTypeTokenForAddress] = None


class MongoTypeTokenHolderAddress(BaseModel):
    """
    MongoTypeTokenHolderAddress is a model representing a token holder's address in a MongoDB collection.

    Attributes:
        id (str): The unique identifier for the token holder, mapped from the MongoDB "_id" field.
        account_address_canonical (Optional[str]): The canonical form of the account address. Defaults to None.
        tokens (dict[str, MongoTypeTokenForAddress]): A dictionary mapping token identifiers to their corresponding MongoTypeTokenForAddress objects.
    """

    id: str = Field(..., alias="_id")
    account_address_canonical: Optional[str] = None
    tokens: dict[str, MongoTypeTokenForAddress]


class MongoTypeLoggedEvent(BaseModel):
    """
    MongoTypeLoggedEvent represents a logged event in a MongoDB collection.

    Attributes:
        id (str): The unique identifier for the event, mapped from the MongoDB "_id" field.
        logged_event (str): The name or description of the logged event.
        result (dict): The result or payload of the logged event.
        tag (int): A tag associated with the event.
        event_type (str): The type or category of the event.
        block_height (int): The block height at which the event occurred.
        slot_time (Optional[dt.datetime]): The slot time when the event was logged, if available.
        tx_index (int): The transaction index within the block.
        ordering (int): The ordering of the event.
        tx_hash (str): The transaction hash associated with the event.
        token_address (str): The address of the token involved in the event.
        contract (str): The contract address related to the event.
        date (Optional[str]): The date when the event was logged, if available.
        to_address_canonical (Optional[str]): The canonical form of the recipient address, if available.
        from_address_canonical (Optional[str]): The canonical form of the sender address, if available.
    """

    id: str = Field(..., alias="_id")
    logged_event: str
    result: dict
    tag: int
    event_type: str
    block_height: int
    slot_time: Optional[dt.datetime] = None
    tx_index: int  #####################################################################
    ordering: int
    tx_hash: str
    token_address: str
    contract: str
    date: Optional[str] = None
    to_address_canonical: Optional[str] = None
    from_address_canonical: Optional[str] = None


class MongoTypeTokensTag(BaseModel):
    """
    MongoTypeTokensTag is a Pydantic model representing a token tag in a MongoDB collection.

    Attributes:
        id (str): The unique identifier for the token tag, mapped from the MongoDB "_id" field.
        contracts (list[str]): A list of contract addresses associated with the token tag.
        tag_template (Optional[bool]): Indicates if the tag is a template.
        single_use_contract (Optional[bool]): Indicates if the contract is for single use.
        logo_url (Optional[str]): URL to the logo image of the token.
        decimals (Optional[int]): Number of decimal places for the token.
        exchange_rate (Optional[float]): Exchange rate of the token.
        get_price_from (Optional[str]): Source from which the price of the token is obtained.
        logged_events_count (Optional[int]): Number of logged events associated with the token.
        owner (Optional[str]): Owner of the token.
        module_name (Optional[str]): Name of the module associated with the token.
        token_type (Optional[str]): Type of the token.
        display_name (Optional[str]): Display name of the token.
        tvl_for_token_in_usd (Optional[float]): Total value locked for the token in USD.
        token_tag_id (Optional[str]): Identifier for the token tag.
    """

    id: str = Field(..., alias="_id")
    contracts: list[str]
    tag_template: Optional[bool] = None
    single_use_contract: Optional[bool] = None
    logo_url: Optional[str] = None
    decimals: Optional[int] = None
    exchange_rate: Optional[float] = None
    get_price_from: Optional[str] = None
    logged_events_count: Optional[int] = None
    owner: Optional[str] = None
    module_name: Optional[str] = None
    token_type: Optional[str] = None
    display_name: Optional[str] = None
    tvl_for_token_in_usd: Optional[float] = None
    token_tag_id: Optional[str] = None


class FailedAttempt(BaseModel):
    """
    A model representing a failed attempt to download and parse metadata.

    Attributes:
        attempts (int): The number of attempts made.
        do_not_try_before (datetime): The datetime before which no further attempts should be made.
        last_error (str): The error message from the last attempt.
    """

    attempts: int
    do_not_try_before: dt.datetime
    last_error: str


class MongoTypeTokenAddress(BaseModel):
    """
    MongoTypeTokenAddress represents the structure of a token address document stored in MongoDB.

    Attributes:
        id (str): The unique identifier for the token address, mapped from the MongoDB "_id" field.
        contract (str): The contract address associated with the token.
        token_id (str): The unique identifier for the token.
        token_amount (Optional[str]): The amount of tokens, if available.
        metadata_url (Optional[str]): The URL to the token's metadata, if available.
        last_height_processed (int): The last blockchain height that was processed for this token.
        token_holders (Optional[dict[str, str]]): A dictionary mapping token holder addresses to their respective amounts, if available.
        tag_information (Optional[MongoTypeTokensTag]): Additional tag information related to the token, if available.
        exchange_rate (Optional[float]): The exchange rate of the token, if available.
        domain_name (Optional[str]): The domain name associated with the token, if available.
        token_metadata (Optional[TokenMetaData]): Metadata related to the token, if available.
        failed_attempt (Optional[FailedAttempt]): Information about any failed attempts related to the token, if available.
        hidden (Optional[bool]): A flag indicating whether the token is hidden.
    """

    id: str = Field(..., alias="_id")
    contract: str
    token_id: str
    token_amount: Optional[str] = None
    metadata_url: Optional[str] = None
    last_height_processed: int
    token_holders: Optional[dict[str, str]] = None
    tag_information: Optional[MongoTypeTokensTag] = None
    exchange_rate: Optional[float] = None
    domain_name: Optional[str] = None
    token_metadata: Optional[TokenMetaData] = None
    failed_attempt: Optional[FailedAttempt] = None
    hidden: Optional[bool] = None


class MongoTypeTokenAddressV2(BaseModel):
    """
    MongoTypeTokenAddressV2 represents a MongoDB document model for token addresses.

    Attributes:
        id (str): The unique identifier for the document, mapped to the MongoDB "_id" field.
        contract (str): The contract address associated with the token.
        token_id (str): The unique identifier for the token.
        token_amount (Optional[str]): The amount of the token, if applicable.
        metadata_url (Optional[str]): The URL to the token's metadata.
        last_height_processed (int): The last blockchain height that was processed for this token.
        tag_information (Optional[MongoTypeTokensTag]): Additional tag information related to the token.
        exchange_rate (Optional[float]): The exchange rate of the token.
        token_metadata (Optional[TokenMetaData]): Metadata associated with the token.
        failed_attempt (Optional[FailedAttempt]): Information about any failed attempts related to the token.
        hidden (Optional[bool]): Indicates whether the token is hidden.
    """

    id: str = Field(..., alias="_id")
    contract: str
    token_id: str
    token_amount: Optional[str] = None
    metadata_url: Optional[str] = None
    last_height_processed: int
    tag_information: Optional[MongoTypeTokensTag] = None
    exchange_rate: Optional[float] = None
    # domain_name: Optional[str] = None
    token_metadata: Optional[TokenMetaData] = None
    failed_attempt: Optional[FailedAttempt] = None
    hidden: Optional[bool] = None


class CISProcessEventRequest(BaseModel):
    """
    CISProcessEventRequest represents a request to process an event in the CIS (Contract Initialization System).

    Attributes:
        tx (CCD_BlockItemSummary): The transaction block item summary.
        event_index (int): The index of events from either contract_initialized or contract_update_issued.
        standard (Optional[StandardIdentifiers]): The standard identifier, None for unrecognized events.
        instance_address (str): The address of the instance.
        event (str): The event string.
        event_name (Optional[str]): The name of the event, None for unrecognized events.
        tag (int): The tag associated with the event.
        recognized_event (Optional[Any]): The recognized event, None for unrecognized events.
        effect_type (Optional[str]): The effect type for contract_update_issued, either interrupted or updated.
        effect_index (int): The index of the effect in the list.
    """

    tx: CCD_BlockItemSummary
    event_index: int  # this is the index of events from either contract_initialized of contract_update_issued
    standard: Optional[StandardIdentifiers] = None  # None for unrecognized events
    instance_address: str
    event: str
    event_name: Optional[str] = None  # None for unrecognized events
    tag: int
    recognized_event: Optional[Any] = None  # None for unrecognized events
    effect_type: Optional[str] = (
        None  # for contract_update_issued, these are either interrupted or updated
    )
    effect_index: int = 0  # its index in the list


# CIS


# CIS-2 Metadata classes
class TokenAttribute(BaseModel):
    """
    TokenAttribute is a data model representing an attribute of a token.

    Attributes:
        type (Optional[str]): The type of the token attribute.
        name (Optional[str]): The name of the token attribute.
        value (Optional[str]): The value of the token attribute.

    Config:
        model_config (ConfigDict): Configuration for the model, with coercion of numbers to strings enabled.
    """

    model_config = ConfigDict(coerce_numbers_to_str=True)
    type: Optional[str] = None
    name: Optional[str] = None
    value: Optional[str] = None


class TokenURLJSON(BaseModel):
    """
    TokenURLJSON is a data model representing a JSON object with a URL and a hash.

    Attributes:
        url (Optional[str]): The URL as a string. Defaults to None.
        hash (Optional[str]): The hash value as a string. Defaults to None.
    """

    model_config = ConfigDict(coerce_numbers_to_str=True)
    url: Optional[str] = None
    hash: Optional[str] = None


class TokenMetaData(BaseModel):
    """
    TokenMetaData is a model representing metadata for a token.

    Attributes:
        name (Optional[str]): The name of the token.
        symbol (Optional[str]): The symbol of the token.
        unique (Optional[bool]): Indicates if the token is unique.
        decimals (Optional[int]): The number of decimal places for the token.
        description (Optional[str]): A description of the token.
        thumbnail (Optional[TokenURLJSON]): A URL to the token's thumbnail image.
        display (Optional[TokenURLJSON]): A URL to the token's display image.
        artifact (Optional[TokenURLJSON]): A URL to the token's artifact.
        assets (Optional[list[TokenMetaData]]): A list of associated token metadata.
        attributes (Optional[list[TokenAttribute]]): A list of attributes for the token.
        localization (Optional[dict[str, TokenURLJSON]]): A dictionary for localization with language codes as keys and TokenURLJSON as values.
    """

    model_config = ConfigDict(coerce_numbers_to_str=True)
    name: Optional[str] = None
    symbol: Optional[str] = None
    unique: Optional[bool] = None
    decimals: Optional[int] = None
    description: Optional[str] = None
    thumbnail: Optional[TokenURLJSON] = None
    display: Optional[TokenURLJSON] = None
    artifact: Optional[TokenURLJSON] = None
    assets: Optional[list[TokenMetaData]] = None
    attributes: Optional[list[TokenAttribute]] = None
    localization: Optional[dict[str, TokenURLJSON]] = None


class StandardIdentifiers(Enum):
    """
    Enum class representing standard identifiers for CIS (Common Identifier System).

    Attributes:
        CIS_0 (str): Represents the identifier "CIS-0".
        CIS_1 (str): Represents the identifier "CIS-1".
        CIS_2 (str): Represents the identifier "CIS-2".
        CIS_3 (str): Represents the identifier "CIS-3".
        CIS_4 (str): Represents the identifier "CIS-4".
        CIS_5 (str): Represents the identifier "CIS-5".
        CIS_6 (str): Represents the identifier "CIS-6".
    """

    CIS_0 = "CIS-0"
    CIS_1 = "CIS-1"
    CIS_2 = "CIS-2"
    CIS_3 = "CIS-3"
    CIS_4 = "CIS-4"
    CIS_5 = "CIS-5"
    CIS_6 = "CIS-6"


class LoggedEvents(Enum):
    transfer_event = 255
    mint_event = 254
    burn_event = 253
    operator_event = 252
    metadata_event = 251
    nonce_event = 250
    register_credential_event = 249
    revoke_credential_event = 248
    issuer_metadata_event = 247
    credential_metadata_event = 246
    credential_schemaref_event = 245
    recovation_key_event = 244
    item_created_event = 237
    item_status_changed = 236


class LEEventInfo(BaseModel):
    """
    LEEventInfo is a model representing information about a logged event.

    Attributes:
        contract (Optional[str]): The contract associated with the event.
        standard (Optional[str]): The standard associated with the event.
        logged_event (str): The name or identifier of the logged event.
        effect_index (int): The index of the effect within the event.
        event_index (int): The index of the event.
        event_type (Optional[str]): The type of the event.
        token_address (Optional[str]): The address of the token involved in the event.
    """

    contract: Optional[str] = None
    standard: Optional[str] = None
    logged_event: str
    effect_index: int
    event_index: int
    event_type: Optional[str] = None
    token_address: Optional[str] = None


class LETxInfo(BaseModel):
    """
    LETxInfo is a data model representing transaction information.

    Attributes:
        date (str): The date of the transaction.
        tx_hash (str): The hash of the transaction.
        tx_index (int): The index of the transaction.
        block_height (int): The height of the block containing the transaction.
    """

    date: str
    tx_hash: str
    tx_index: int
    block_height: int


class MongoTypeLoggedEventV2(BaseModel):
    """
    MongoTypeLoggedEventV2 is a Pydantic model representing a logged event in MongoDB.

    Attributes:
        id (str): The unique identifier for the event, aliased as "_id".
        event_info (LEEventInfo): Information about the logged event.
        tx_info (LETxInfo): Transaction information related to the event.
        recognized_event (Optional[Union[
            mintEvent, transferEvent, burnEvent, updateOperatorEvent, tokenMetadataEvent,
            registerCredentialEvent, revokeCredentialEvent, issuerMetadataEvent,
            credentialMetadataEvent, credentialSchemaRefEvent, revocationKeyEvent,
            itemCreatedEvent, itemStatusChangedEvent, nonceEvent, depositCCDEvent,
            depositCIS2TokensEvent, transferCCDEvent, transferCIS2TokensEvent,
            withdrawCCDEvent, withdrawCIS2TokensEvent, fiveStarsRegisterAccessEvent
        ]]): The recognized event type, which can be one of several event types, or None.
        to_address_canonical (Optional[str]): The canonical address to which the event is related, if applicable.
        from_address_canonical (Optional[str]): The canonical address from which the event is related, if applicable.
    """

    id: str = Field(..., alias="_id")
    event_info: LEEventInfo
    tx_info: LETxInfo
    recognized_event: Optional[
        mintEvent
        | transferEvent
        | burnEvent
        | updateOperatorEvent
        | tokenMetadataEvent
        | registerCredentialEvent
        | revokeCredentialEvent
        | issuerMetadataEvent
        | credentialMetadataEvent
        | credentialSchemaRefEvent
        | revocationKeyEvent
        | itemCreatedEvent
        | itemStatusChangedEvent
        | nonceEventCIS3
        | nonceEventCIS5
        | depositCCDEvent
        | depositCIS2TokensEvent
        | transferCCDEvent
        | transferCIS2TokensEvent
        | withdrawCCDEvent
        | withdrawCIS2TokensEvent
        | fiveStarsRegisterAccessEvent
    ] = None
    to_address_canonical: Optional[str] = None
    from_address_canonical: Optional[str] = None


# CIS-2 Logged Event Types


class transferEvent(BaseModel):
    """A transfer event from a CIS-2 compliant smart contract.

    See: [transferEvent](http://proposals.concordium.software/CIS/cis-2.html#transferevent)

    Attributes:
        tag (int): The event tag (255 for transfer events).
        token_id (Optional[str]): The ID of the token being transferred.
        token_amount (Optional[int]): The amount of tokens being transferred.
        from_address (Optional[str]): The address tokens are being transferred from.
        to_address (Optional[str]): The address tokens are being transferred to.
    """

    tag: int
    token_id: Optional[str] = None
    token_amount: Optional[int] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None


class mintEvent(BaseModel):
    """A mint event from a CIS-2 compliant smart contract.

    See: [mintEvent](http://proposals.concordium.software/CIS/cis-2.html#mintevent)

    Attributes:
        tag (int): The event tag (254 for mint events).
        token_id (Optional[str]): The ID of the token being minted.
        token_amount (Optional[int]): The amount of tokens being minted.
        to_address (Optional[str]): The address receiving the minted tokens.
    """

    tag: int
    token_id: Optional[str] = None
    token_amount: Optional[int] = None
    to_address: Optional[str] = None


class burnEvent(BaseModel):
    """A burn event from a CIS-2 compliant smart contract.

    See: [burnEvent](http://proposals.concordium.software/CIS/cis-2.html#burnevent)

    Attributes:
        tag (int): The event tag (253 for burn events).
        token_id (Optional[str]): The ID of the token being burned.
        token_amount (Optional[int]): The amount of tokens being burned.
        from_address (Optional[str]): The address tokens are being burned from.
    """

    tag: int
    token_id: Optional[str] = None
    token_amount: Optional[int] = None
    from_address: Optional[str] = None


class updateOperatorEvent(BaseModel):
    """An operator update event from a CIS-2 compliant smart contract.

    See: [updateOperatorEvent](http://proposals.concordium.software/CIS/cis-2.html#updateoperatorevent)

    Attributes:
        tag (int): The event tag (252 for operator update events).
        operator_update (Optional[str]): The type of update ("Add operator" or "Remove operator").
        owner (Optional[str]): The address of the token owner.
        operator (Optional[str]): The address of the operator being updated.
    """

    tag: int
    operator_update: Optional[str] = None
    owner: Optional[str] = None
    operator: Optional[str] = None


class SchemaRef(BaseModel):
    """
    SchemaRef represents a reference to a schema with an optional checksum.

    Attributes:
        url (str): The URL of the schema.
        checksum (Optional[str]): An optional checksum for the schema.
    """

    url: str
    checksum: Optional[str] = None


class registerCredentialEvent(BaseModel):
    """A register credential event from a CIS-4 compliant smart contract.

    See: [registerCredentialEvent](http://proposals.concordium.software/CIS/cis-4.html#registercredentialevent)

    Attributes:
        tag (int): The event tag (249 for register credential events).
        credential_id (Optional[str]): The unique identifier of the credential.
        schema_ref (Optional[SchemaRef]): The reference to the schema definition.
        credential_type (Optional[str]): The type of the credential being registered.
    """

    tag: int
    credential_id: Optional[str] = None
    schema_ref: Optional[SchemaRef] = None
    credential_type: Optional[str] = None


class revokeCredentialEvent(BaseModel):
    """A revoke credential event from a CIS-4 compliant smart contract.

    See: [revokeCredentialEvent](http://proposals.concordium.software/CIS/cis-4.html#revokecredentialevent)

    Attributes:
        tag (int): The event tag (248 for revoke credential events).
        credential_id (Optional[str]): The unique identifier of the credential being revoked.
        revoker (Optional[str]): The entity revoking the credential (Issuer, Holder, or Other).
        reason (Optional[str]): The reason for revoking the credential.
    """

    tag: int
    credential_id: Optional[str] = None
    revoker: Optional[str] = None
    reason: Optional[str] = None


class issuerMetadataEvent(BaseModel):
    """An issuer metadata event from a CIS-4 compliant smart contract.

    See: [issuerMetadataEvent](http://proposals.concordium.software/CIS/cis-4.html#issuermetadataevent)

    Attributes:
        tag (int): The event tag (247 for issuer metadata events).
        metadata (MetadataUrl): The URL and optional hash of the issuer's metadata.
    """

    tag: int
    metadata: MetadataUrl


class credentialMetadataEvent(BaseModel):
    """A credential metadata event from a CIS-4 compliant smart contract.

    See: [credentialMetadataEvent](http://proposals.concordium.software/CIS/cis-4.html#credentialmetadataevent)

    Attributes:
        tag (int): The event tag (246 for credential metadata events).
        id (str): The credential holder identifier.
        metadata (MetadataUrl): The URL and optional hash of the credential metadata.
    """

    tag: int
    id: str  # credentialHolderId
    metadata: MetadataUrl


class credentialSchemaRefEvent(BaseModel):
    """A credential schema reference event from a CIS-4 compliant smart contract.

    See: [credentialSchemaRefEvent](http://proposals.concordium.software/CIS/cis-4.html#credentialschemarefevent)

    Attributes:
        tag (int): The event tag (245 for credential schema reference events).
        type (Optional[str]): The type of credential this schema is for.
        schema_ref (Optional[str]): The reference to the schema definition.
    """

    tag: int
    type: Optional[str] = None
    schema_ref: Optional[str] = None


class revocationKeyEvent(BaseModel):
    """A revocation key event from a CIS-4 compliant smart contract.

    See: [revocationKeyEvent](http://proposals.concordium.software/CIS/cis-4.html#revocationkeyevent)

    Attributes:
        tag (int): The event tag (244 for revocation key events).
        public_key_ed25519 (Optional[str]): The public key being registered or removed.
        action (Optional[str]): The action being performed ("Register" or "Remove").
    """

    tag: int
    public_key_ed25519: Optional[str] = None
    action: Optional[str] = None


class MetadataUrl(BaseModel):
    """
    MetadataUrl represents a model for storing metadata URL information.

    Attributes:
        url (str): The URL of the metadata.
        checksum (Optional[str]): An optional checksum for the metadata URL.
    """

    url: str
    checksum: Optional[str] = None


class tokenMetadataEvent(BaseModel):
    """A metadata event from a CIS-2 compliant smart contract.

    See: [tokenMetadataEvent](http://proposals.concordium.software/CIS/cis-2.html#tokenmetadataevent)

    Attributes:
        tag (int): The event tag (251 for metadata events).
        token_id (str): The ID of the token whose metadata is being set.
        metadata (MetadataUrl): The URL and optional hash of the token's metadata.
    """

    tag: int
    token_id: str
    metadata: MetadataUrl


class itemCreatedEvent(BaseModel):
    """An item created event from a CIS-6 compliant smart contract.

    See: [itemCreatedEvent](http://proposals.concordium.software/CIS/cis-6.html#itemcreatedevent)

    Attributes:
        tag (int): The event tag (237 for item created events).
        item_id (str): The unique identifier of the item being created.
        metadata (MetadataUrl): The URL and optional hash of the item's metadata.
        initial_status (str | int): The initial status of the created item.
    """

    tag: int
    item_id: str
    metadata: MetadataUrl
    initial_status: str | int


class itemStatusChangedEvent(BaseModel):
    """An item status change event from a CIS-6 compliant smart contract.

    See: [itemStatusChangedEvent](http://proposals.concordium.software/CIS/cis-6.html#itemstatuschangedevent)

    Attributes:
        tag (int): The event tag (236 for item status changed events).
        item_id (str): The unique identifier of the item being updated.
        new_status (str | int): The new status of the item.
        additional_data (str): Additional data associated with the status change.
    """

    tag: int
    item_id: str
    new_status: str | int
    additional_data: str


class nonceEventCIS3(BaseModel):
    """A nonce event from a CIS-3 compliant smart contract.

    See: [nonceEvent](http://proposals.concordium.software/CIS/cis-3.html#nonceevent)

    Attributes:
        tag (int): The event tag (250 for nonce events).
        nonce (Optional[str]): The generated nonce value.
        sponsoree (Optional[str]): The address of the account being sponsored.
    """

    tag: int
    nonce: Optional[str] = None
    sponsoree: Optional[str] = None


class nonceEventCIS5(BaseModel):
    """A nonce event from a CIS-5 compliant smart contract.

    See: [nonceEvent](http://proposals.concordium.software/CIS/cis-5.html#nonceevent)

    Attributes:
        tag (int): The event tag (250 for nonce events).
        nonce (Optional[str]): The generated nonce value.
        sponsoree (Optional[str]): The public key being sponsored.
    """

    tag: int
    nonce: Optional[str] = None
    sponsoree: Optional[str] = None


class depositCCDEvent(BaseModel):
    """A CCD deposit event from a CIS-5 compliant smart contract.

    See: [depositCCDEvent](http://proposals.concordium.software/CIS/cis-5.html#depositccdevent)

    Attributes:
        tag (int): The event tag (249 for deposit CCD events).
        ccd_amount (Optional[microCCD]): The amount of CCD being deposited.
        from_address (Optional[str]): The address from which CCD is being deposited.
        to_public_key_ed25519 (Optional[str]): The public key of the recipient's account.
    """

    tag: int
    ccd_amount: Optional[microCCD] = None
    from_address: Optional[str] = None
    to_public_key_ed25519: Optional[str] = None


class depositCIS2TokensEvent(BaseModel):
    """A CIS-2 token deposit event from a CIS-5 compliant smart contract.

    See: [depositCIS2TokensEvent](http://proposals.concordium.software/CIS/cis-5.html#depositcis2tokenstevent)

    Attributes:
        tag (int): The event tag (248 for deposit CIS2 tokens events).
        token_amount (Optional[int]): The amount of CIS-2 tokens being deposited.
        token_id (Optional[str]): The ID of the token being deposited.
        cis2_token_contract_address (Optional[str]): The contract address of the CIS-2 token.
        from_address (Optional[str]): The address from which tokens are being deposited.
        to_public_key_ed25519 (Optional[str]): The public key of the recipient's account.
    """

    tag: int
    token_amount: Optional[int] = None
    token_id: Optional[str] = None
    cis2_token_contract_address: Optional[str] = None
    from_address: Optional[str] = None
    to_public_key_ed25519: Optional[str] = None


class withdrawCCDEvent(BaseModel):
    """A CCD withdraw event from a CIS-5 compliant smart contract.

    See: [withdrawCCDEvent](http://proposals.concordium.software/CIS/cis-5.html#withdrawccdevent)

    Attributes:
        tag (int): The event tag (247 for withdraw CCD events).
        ccd_amount (Optional[microCCD]): The amount of CCD being withdrawn.
        from_public_key_ed25519 (Optional[str]): The public key from which CCD is being withdrawn.
        to_address (Optional[str]): The address receiving the withdrawn CCD.
    """

    tag: int
    ccd_amount: Optional[microCCD] = None
    from_public_key_ed25519: Optional[str] = None
    to_address: Optional[str] = None


class withdrawCIS2TokensEvent(BaseModel):
    """A CIS-2 token withdraw event from a CIS-5 compliant smart contract.

    See: [withdrawCIS2TokensEvent](http://proposals.concordium.software/CIS/cis-5.html#withdrawcis2tokenstevent)

    Attributes:
        tag (int): The event tag (246 for withdraw CIS2 tokens events).
        token_amount (Optional[int]): The amount of CIS-2 tokens being withdrawn.
        token_id (Optional[str]): The ID of the token being withdrawn.
        cis2_token_contract_address (Optional[str]): The contract address of the CIS-2 token.
        from_public_key_ed25519 (Optional[str]): The public key from which tokens are being withdrawn.
        to_address (Optional[str]): The address receiving the withdrawn tokens.
    """

    tag: int
    token_amount: Optional[int] = None
    token_id: Optional[str] = None
    cis2_token_contract_address: Optional[str] = None
    from_public_key_ed25519: Optional[str] = None
    to_address: Optional[str] = None


class transferCCDEvent(BaseModel):
    """A CCD transfer event from a CIS-5 compliant smart contract.

    See: [transferCCDEvent](http://proposals.concordium.software/CIS/cis-5.html#transferccdevent)

    Attributes:
        tag (int): The event tag (245 for transfer CCD events).
        ccd_amount (Optional[microCCD]): The amount of CCD being transferred.
        from_public_key_ed25519 (Optional[str]): The public key from which CCD is being transferred.
        to_public_key_ed25519 (Optional[str]): The public key to which CCD is being transferred.
    """

    tag: int
    ccd_amount: Optional[microCCD] = None
    from_public_key_ed25519: Optional[str] = None
    to_public_key_ed25519: Optional[str] = None


class transferCIS2TokensEvent(BaseModel):
    """A CIS-2 token transfer event from a CIS-5 compliant smart contract.

    See: [transferCIS2TokensEvent](http://proposals.concordium.software/CIS/cis-5.html#transfercis2tokensevent)

    Attributes:
        tag (int): The event tag (244 for transfer CIS2 tokens events).
        token_amount (Optional[int]): The amount of CIS-2 tokens being transferred.
        token_id (Optional[str]): The ID of the token being transferred.
        cis2_token_contract_address (Optional[str]): The contract address of the CIS-2 token.
        from_public_key_ed25519 (Optional[str]): The public key from which tokens are being transferred.
        to_public_key_ed25519 (Optional[str]): The public key to which tokens are being transferred.
    """

    tag: int
    token_amount: Optional[int] = None
    token_id: Optional[str] = None
    cis2_token_contract_address: Optional[str] = None
    from_public_key_ed25519: Optional[str] = None
    to_public_key_ed25519: Optional[str] = None


class fiveStarsRegisterAccessEvent(BaseModel):
    """A custom event for registering access for 5tars.

    Attributes:
        tag (int): The event tag (0 for 5tars register access events).
        public_key (Optional[str]): The public key being registered.
        timestamp (Optional[int]): Unix timestamp of the registration.
    """

    tag: int
    public_key: Optional[str] = None
    timestamp: Optional[int] = None


class CIS:
    def __init__(
        self,
        grpcclient: GRPCClient = None,
        instance_index=None,
        instance_subindex=None,
        entrypoint=None,
        net: NET.MAINNET = None,
    ):
        self.grpcclient = grpcclient
        self.instance_index = instance_index
        self.instance_subindex = instance_subindex
        self.entrypoint = entrypoint
        self.net = net

    ###############
    def format_address(self, address):
        if type(address) is not (tuple):
            # it's an account address
            if len(address) != LEN_ACCOUNT_ADDRESS:
                return None

        if isinstance(address, tuple):
            address = f"<{address[0]},{address[1]}>"

        return address

    def execute_save(self, collection: Collection, replacement, _id: str):
        repl_dict = replacement.dict()
        if "id" in repl_dict:
            del repl_dict["id"]

        # sort tokens and token_holders
        if "tokens" in repl_dict:
            sorted_tokens = list(repl_dict["tokens"].keys())
            sorted_tokens.sort()
            tokens_sorted = {i: repl_dict["tokens"][i] for i in sorted_tokens}
            repl_dict["tokens"] = tokens_sorted

        if "token_holders" in repl_dict:
            sorted_holders = list(repl_dict["token_holders"].keys())
            sorted_holders.sort()
            token_holders_sorted = {
                i: repl_dict["token_holders"][i] for i in sorted_holders
            }
            repl_dict["token_holders"] = token_holders_sorted

        _ = collection.bulk_write(
            [
                ReplaceOne(
                    {"_id": _id},
                    replacement=repl_dict,
                    upsert=True,
                )
            ]
        )

    def restore_state_for_token_address(
        self,
        db_to_use: dict[Collections, Collection],
        token_address: str,
    ):
        d: dict = db_to_use[Collections.tokens_token_addresses].find_one(
            {"_id": token_address}
        )

        d.update(
            {
                "token_amount": str(int(0)),  # mongo limitation on int size
                "token_holders": {},  # {CCD_AccountAddress, str(token_amount)}
                "last_height_processed": 0,
            }
        )

        d = MongoTypeTokenAddress(**d)
        self.execute_save(
            db_to_use[Collections.tokens_token_addresses], d, token_address
        )

    def copy_token_holders_state_to_address_and_save(
        self,
        db_to_use: dict[Collections, Collection],
        token_address_info: MongoTypeTokenAddress,
        address: str,
    ):
        token_address = token_address_info.id
        d = db_to_use[Collections.tokens_accounts].find_one({"_id": address})
        # if this account doesn't have tokens, create empty dict.
        if not d:
            d = MongoTypeTokenHolderAddress(
                **{
                    "_id": address,
                    "tokens": {},
                }
            )  # keyed on token_address
        else:
            d = MongoTypeTokenHolderAddress(**d)

        token_to_save = MongoTypeTokenForAddress(
            **{
                "token_address": token_address,
                "contract": token_address_info.contract,
                "token_id": token_address_info.token_id,
                "token_amount": str(token_address_info.token_holders.get(address, 0)),
            }
        )

        d.tokens[token_address] = token_to_save

        if token_to_save.token_amount == str(0):
            del d.tokens[token_address]

        self.execute_save(db_to_use[Collections.tokens_accounts], d, address)

    def save_mint(
        self,
        db_to_use: dict[Collections, Collection],
        instance_address: str,
        result: mintEvent,
        height: int,
    ):
        token_address = f"{instance_address}-{result.token_id}"
        d = db_to_use[Collections.tokens_token_addresses].find_one(
            {"_id": token_address}
        )
        if not d:
            d = MongoTypeTokenAddress(
                **{
                    "_id": token_address,
                    "contract": instance_address,
                    "token_id": result.token_id,
                    "token_amount": str(int(0)),  # mongo limitation on int size
                    "token_holders": {},  # {CCD_AccountAddress, str(token_amount)}
                    "last_height_processed": height,
                }
            )
        else:
            d = MongoTypeTokenAddress(**d)

        token_holders: dict[CCD_AccountAddress, str] = d.token_holders  # noqa: F405
        token_holders[result.to_address] = str(
            int(token_holders.get(result.to_address, "0")) + result.token_amount
        )
        d.token_amount = str((int(d.token_amount) + result.token_amount))
        d.token_holders = token_holders

        self.execute_save(
            db_to_use[Collections.tokens_token_addresses], d, token_address
        )
        self.copy_token_holders_state_to_address_and_save(
            db_to_use, d, result.to_address
        )

    def save_metadata(
        self,
        db_to_use: dict[Collections, Collection],
        instance_address: str,
        result: tokenMetadataEvent,
        height: int,
    ):
        token_address = f"{instance_address}-{result.token_id}"
        d = db_to_use[Collections.tokens_token_addresses].find_one(
            {"_id": token_address}
        )
        if not d:
            d = MongoTypeTokenAddress(
                **{
                    "_id": token_address,
                    "contract": instance_address,
                    "token_id": result.token_id,
                    "last_height_processed": height,
                }
            )
        else:
            d = MongoTypeTokenAddress(**d)

        d.metadata_url = result.metadata.url

        self.execute_save(
            db_to_use[Collections.tokens_token_addresses], d, token_address
        )

    def save_operator(
        self,
        db_to_use: dict[Collections, Collection],
        instance_address: str,
        result: tokenMetadataEvent,
        height: int,
    ):
        token_address = f"{instance_address}-{result.token_id}"
        d = db_to_use[Collections.tokens_token_addresses].find_one(
            {"_id": token_address}
        )
        if not d:
            d = MongoTypeTokenAddress(
                **{
                    "_id": token_address,
                    "contract": instance_address,
                    "token_id": result.token_id,
                    "last_height_processed": height,
                }
            )
        else:
            d = MongoTypeTokenAddress(**d)

        d.metadata_url = result.metadata.url

        self.execute_save(
            db_to_use[Collections.tokens_token_addresses], d, token_address
        )

    def save_transfer(
        self,
        db_to_use: dict[Collections, Collection],
        instance_address: str,
        result: transferEvent,
        height: int,
    ):
        token_address = f"{instance_address}-{result.token_id}"
        d = db_to_use[Collections.tokens_token_addresses].find_one(
            {"_id": token_address}
        )
        if not d:
            return None

        d = MongoTypeTokenAddress(**d)

        try:
            token_holders: dict[CCD_AccountAddress, str] = d.token_holders  # noqa: F405
        except:  # noqa: E722
            console.log(
                f"{result.tag}: {token_address} | {d} has no field token_holders?"
            )
            Exception(
                console.log(
                    f"{result.tag}: {token_address} | {d} has no field token_holders?"
                )
            )

        token_holders[result.to_address] = str(
            int(token_holders.get(result.to_address, "0")) + result.token_amount
        )
        try:
            token_holders[result.from_address] = str(
                int(token_holders.get(result.from_address, None)) - result.token_amount
            )
            if int(token_holders[result.from_address]) >= 0:
                d.token_holders = token_holders
                d.last_height_processed = height
                self.execute_save(
                    db_to_use[Collections.tokens_token_addresses], d, token_address
                )

                self.copy_token_holders_state_to_address_and_save(
                    db_to_use, d, result.from_address
                )
                self.copy_token_holders_state_to_address_and_save(
                    db_to_use, d, result.to_address
                )

        except:  # noqa: E722
            if result.token_amount > 0:
                console.log(
                    f"""{result.tag}: {result.from_address} is not listed 
                    as token holder for {token_address}?"""
                )

    def save_burn(
        self,
        db_to_use: dict[Collections, Collection],
        instance_address: str,
        result: burnEvent,
        height: int,
    ):
        token_address = f"{instance_address}-{result.token_id}"

        d = MongoTypeTokenAddress(
            **db_to_use[Collections.tokens_token_addresses].find_one(
                {"_id": token_address}
            )
        )

        token_holders: dict[CCD_AccountAddress, str] = d.token_holders  # noqa: F405
        try:
            token_holders[result.from_address] = str(
                int(token_holders.get(result.from_address, "0")) - result.token_amount
            )
            if token_holders[result.from_address] == str(0):
                del token_holders[result.from_address]

            d.token_amount = str((int(d.token_amount) - result.token_amount))
            d.token_holders = token_holders
            d.last_height_processed = height

            if int(d.token_amount) >= 0:
                self.execute_save(
                    db_to_use[Collections.tokens_token_addresses], d, token_address
                )
                self.copy_token_holders_state_to_address_and_save(
                    db_to_use, d, result.from_address
                )

        except:  # noqa: E722
            console.log(
                f"""{result.tag}: {result.from_address} is not listed as 
                token holder for {token_address}?"""
            )
            # exit

    def formulate_logged_event(
        self,
        slot_time: dt.datetime,
        tag_: int,
        result: Union[
            mintEvent, burnEvent, transferEvent, updateOperatorEvent, tokenMetadataEvent
        ],
        instance_address: str,
        event: str,
        height: int,
        tx_hash: str,
        tx_index: int,
        ordering: int,
        _id_postfix: str,
    ) -> Union[ReplaceOne, None]:
        if tag_ in [255, 254, 253, 252, 251, 250]:
            if tag_ == 252:
                token_address = f"{instance_address}-operator"
            elif tag_ == 250:
                token_address = f"{instance_address}-nonce"
            else:
                token_address = f"{instance_address}-{result.token_id}"
            _id = f"{height}-{token_address}-{event}-{_id_postfix}"
            if result:
                result_dict = result.model_dump()
            else:
                result_dict = {}
            if "token_amount" in result_dict:
                result_dict["token_amount"] = str(result_dict["token_amount"])

            d = {
                "_id": _id,
                "logged_event": event,
                "result": result_dict,
                "tag": tag_,
                "event_type": LoggedEvents(tag_).name,
                "block_height": height,
                "tx_hash": tx_hash,
                "tx_index": tx_index,
                "ordering": ordering,
                "token_address": token_address,
                "contract": instance_address,
                "date": f"{slot_time:%Y-%m-%d}",
            }
            if "to_address" in result_dict:
                d.update({"to_address_canonical": result_dict["to_address"][:29]})
            if "from_address" in result_dict:
                d.update({"from_address_canonical": result_dict["from_address"][:29]})
            return (
                MongoTypeLoggedEvent(**d),
                ReplaceOne(
                    {"_id": _id},
                    replacement=d,
                    upsert=True,
                ),
            )

        else:
            return (None, None)

    # def process_event(
    #     self,
    #     slot_time: dt.datetime,
    #     instance_address: str,
    #     event: str,
    #     height: int,
    #     tx_hash: str,
    #     tx_index: int,
    #     ordering: int,
    #     _id_postfix: str,
    # ):
    #     tag_, result = self.process_log_events(event)
    #     logged_event = None
    #     logged_event_for_queue = None
    #     token_address = None
    #     if result:
    #         # if tag_ in [255, 254, 253, 252, 251, 250]:
    #         if tag_ in [255, 254, 253, 251]:
    #             token_address = f"{instance_address}-{result.token_id}"

    #             (logged_event, logged_event_for_queue) = self.formulate_logged_event(
    #                 slot_time,
    #                 tag_,
    #                 result,
    #                 instance_address,
    #                 event,
    #                 height,
    #                 tx_hash,
    #                 tx_index,
    #                 ordering,
    #                 _id_postfix,
    #             )

    #     return tag_, logged_event, logged_event_for_queue, token_address

    ###############

    def standard_identifier(self, identifier: StandardIdentifiers) -> bytes:
        """
        Converts a standard identifier to its byte representation.

        This method takes a `StandardIdentifiers` object, calculates the length of its ASCII value,
        and returns the byte representation of the identifier prefixed with its length.

        Args:
            identifier (StandardIdentifiers): The standard identifier to be converted.

        Returns:
            (bytes): The byte representation of the standard identifier.

        See Also:
            [CIS-0 Standard Identifier](http://proposals.concordium.software/CIS/cis-0.html#standard-identifer)
        """
        si = io.BytesIO()
        # write the length of ASCII characters for the identifier
        number = len(identifier.value)
        byte_array = number.to_bytes(1, "little")
        si.write(byte_array)
        # write the identifier
        si.write(bytes(identifier.value, encoding="ASCII"))
        # convert to bytes
        return si.getvalue()

    def supports_parameter(self, standard_identifier: StandardIdentifiers) -> bytes:
        sp = io.BytesIO()
        # write the number of standardIdentifiers present
        number = 1
        byte_array = number.to_bytes(2, "little")
        sp.write(byte_array)
        # write the standardIdentifier
        sp.write(self.standard_identifier(standard_identifier))
        # convert to bytes
        return sp.getvalue()

    def support_result(self, bs: io.BytesIO):
        t = int.from_bytes(bs.read(2), byteorder="little")
        if t == 0:
            return t, "Standard is not supported"
        elif t == 1:
            return t, "Standard is supported by this contract"
        elif t == 2:
            contracts = []
            n = int.from_bytes(bs.read(1), byteorder="little")
            for _ in range(n):
                contracts.append(self.contract_address(bs))
                return (
                    t,
                    "Standard is supported by using one of these contract addresses: "
                    + [x for x in contracts],
                )

    def supports_response(self, res: bytes):
        bs = io.BytesIO(bytes.fromhex(res.decode()))
        if bs.getbuffer().nbytes > 0:
            n = int.from_bytes(bs.read(2), byteorder="little")
            responses = []
            for _ in range(n):
                responses.append(self.support_result(bs))
            if len(responses) > 0:
                if responses[0] is not None:
                    return responses[0]
                else:
                    return False, "Lookup Failure"
            else:
                return False, "Lookup Failure"
        else:
            return False, "Lookup Failure"

    def supports_standard(self, standard_identifier: StandardIdentifiers) -> bool:
        parameter_bytes = self.supports_parameter(standard_identifier)

        ii = self.grpcclient.invoke_instance(
            "last_final",
            self.instance_index,
            self.instance_subindex,
            self.entrypoint,
            parameter_bytes,
            self.net,
        )

        res = ii.success.return_value
        support_result, support_result_text = self.supports_response(res)

        return support_result == 1

    def supports_standards(
        self, standard_identifiers: list[StandardIdentifiers]
    ) -> bool:
        support = False
        for si in standard_identifiers:
            parameter_bytes = self.supports_parameter(si)

            ii = self.grpcclient.invoke_instance(
                "last_final",
                self.instance_index,
                self.instance_subindex,
                self.entrypoint,
                parameter_bytes,
                self.net,
            )

            res = ii.success.return_value
            support_result, _ = self.supports_response(res)

            support = support_result == 1
        return support

    # CIS-2
    def balanceOf(self, block_hash: str, tokenID: str, addresses: list[str]):
        """
        Retrieves the balance of a specific token for a list of addresses at a given block hash.

        Args:
            block_hash (str): The hash of the block at which to query the balance.
            tokenID (str): The ID of the token to query.
            addresses (list[str]): A list of addresses to query the balance for.

        Returns:
            (tuple): A tuple containing the balance result and the invocation instance.

        See Also:
            [CIS-2 BalanceOf](http://proposals.concordium.software/CIS/cis-2.html#balanceof)
        """
        parameter_bytes = self.balanceOfParameter(tokenID, addresses)

        ii = self.grpcclient.invoke_instance(
            block_hash,
            self.instance_index,
            self.instance_subindex,
            self.entrypoint,
            parameter_bytes,
            self.net,
        )

        res = ii.success.return_value
        support_result = self.balanceOfResponse(res)

        return support_result, ii

    # CIS-5
    def CCDbalanceOf(self, block_hash: str, public_keys: list[str]):
        """
        Retrieves the CCD balance of the specified public keys at a given block hash.

        Args:
            block_hash (str): The hash of the block at which to query the balance.
            public_keys (list[str]): A list of public keys to query the balance for.

        Returns:
            (tuple): A tuple containing the support result and the invocation instance.

        References:
            - [CIS-5 CCDbalanceOf](http://proposals.concordium.software/CIS/cis-5.html#ccdbalanceof)
        """
        parameter_bytes = self.CCDbalanceOfParameter(public_keys)

        ii = self.grpcclient.invoke_instance(
            block_hash,
            self.instance_index,
            self.instance_subindex,
            self.entrypoint,
            parameter_bytes,
            self.net,
        )

        res = ii.success.return_value
        support_result = self.CCDbalanceOfResponse(res)

        return support_result, ii

    def CIS2balanceOf(
        self,
        block_hash: str,
        cis2_contract: CCD_ContractAddress,
        token_id: str,
        public_keys: list[str],
    ):
        """
        Queries the balance of a specific token for a list of public keys from a CIS-2 contract.

        Args:
            block_hash (str): The hash of the block to query.
            cis2_contract (CCD_ContractAddress): The address of the CIS-2 contract.
            token_id (str): The ID of the token to query.
            public_keys (list[str]): A list of public keys to query the balance for.

        Returns:
            (tuple): A tuple containing the balance result and the invocation instance.

        Reference:
            [CIS-2 BalanceOf](http://proposals.concordium.software/CIS/cis-5.html#cis2balanceof)
        """
        parameter_bytes = self.CIS2balanceOfParameter(
            cis2_contract, token_id, public_keys
        )

        ii = self.grpcclient.invoke_instance(
            block_hash,
            self.instance_index,
            self.instance_subindex,
            self.entrypoint,
            parameter_bytes,
            self.net,
        )

        res = ii.success.return_value
        support_result = self.CIS2balanceOfResponse(res)

        return support_result, ii

    # CIS Components
    def account_address(self, bs: io.BytesIO):
        """
        Reads a 32-byte account address from a BytesIO stream and encodes it in Base58Check format.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the account address.

        Returns:
            (str): The Base58Check encoded account address.

        See Also:
            [CIS-2 Account Address](http://proposals.concordium.software/CIS/cis-2.html#accountaddress)
        """

        addr = bs.read(32)
        return base58.b58encode_check(b"\x01" + addr).decode()

    def contract_address(self, bs: io.BytesIO):
        """
        Extracts and returns the contract address from a given BytesIO stream.

        The contract address is composed of two 8-byte integers read from the stream
        in little-endian byte order.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the contract address data.

        Returns:
            (tuple): A tuple containing two integers representing the contract address.

        For more information, see the [CIS-2 Contract Address Specification](http://proposals.concordium.software/CIS/cis-2.html#contractaddress).
        """

        return int.from_bytes(bs.read(8), byteorder="little"), int.from_bytes(
            bs.read(8), byteorder="little"
        )

    def address(self, bs: io.BytesIO):
        """
        Parses an address from a given BytesIO stream.

        The function reads the first byte to determine the type of address.
        If the byte is 0, it parses an account address.
        If the byte is 1, it parses a contract address.
        Otherwise, it raises an exception for an invalid type.

        Args:
            bs (io.BytesIO): The input byte stream containing the address data.

        Returns:
            (CCD_AccountAddress | CCD_ContractAddress): The parsed address, either an account address or a contract address.

        Raises:
            Exception: If the address type is invalid.
        See Also:
                [CIS-2 Address](http://proposals.concordium.software/CIS/cis-2.html#address)
        """
        t = int.from_bytes(bs.read(1), byteorder="little")
        if t == 0:
            return self.account_address(bs)
        elif t == 1:
            return self.contract_address(bs)
        else:
            raise Exception("invalid type")

    def receiver(self, bs: io.BytesIO):
        """
        Parses a receiver from the given BytesIO stream.

        The function reads the first byte to determine the type of receiver.
        - If the byte is 0, it returns an account address.
        - If the byte is 1, it returns a tuple containing a contract address and a receive hook name.
        - For any other value, it raises an exception indicating an invalid type.

        Args:
            bs (io.BytesIO): The input byte stream to parse.

        Returns:
            (Union[AccountAddress, Tuple[ContractAddress, str]]): The parsed receiver, either an account address or a tuple of contract address and receive hook name.

        Raises:
            Exception: If the type byte is not 0 or 1.

        See Also:
            [CIS-2 Receiver](http://proposals.concordium.software/CIS/cis-2.html#receiver)
        """

        t = int.from_bytes(bs.read(1), byteorder="little")
        if t == 0:
            return self.account_address(bs)
        elif t == 1:
            return self.contract_address(bs), self.receiveHookName(bs)
        else:
            raise Exception("invalid type")

    def url(self, n: int, bs: io.BytesIO):
        data = bs.read(n)
        return data

    def metadataChecksum(self, bs: io.BytesIO):
        t = int.from_bytes(bs.read(1), byteorder="little")
        if t == 0:
            return None
        elif t == 1:
            try:
                return bs.read(32).hex()
            except:  # noqa: E722
                return -1
        else:
            # should not happen
            return -2

    def metadataUrl(self, bs: io.BytesIO):
        """
        Parses a metadata URL from a given BytesIO stream.

        This method reads a URL from the provided BytesIO stream, calculates its checksum,
        and returns a MetadataUrl object containing the URL and its checksum.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the metadata URL.

        Returns:
            (MetadataUrl): An object containing the parsed URL and its checksum.

        References:
            [CIS-2 Metadata URL](http://proposals.concordium.software/CIS/cis-2.html#metadataurl)
        """

        n = int.from_bytes(bs.read(2), byteorder="little")
        url = bs.read(n).decode()
        checksum = self.metadataChecksum(bs)
        return MetadataUrl(**{"url": url, "checksum": checksum})

    def schema_ref(self, bs: io.BytesIO):
        """
        Parses the schema reference from the given BytesIO stream.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the schema reference data.

        Returns:
            (SchemaRef): An instance of SchemaRef containing the URL and checksum.

        See Also:
            [CIS-4 Schema Reference](http://proposals.concordium.software/CIS/cis-4.html#schemaref)
        """
        metadata_url_proxy = self.metadataUrl(bs)
        return SchemaRef(
            **{"url": metadata_url_proxy.url, "checksum": metadata_url_proxy.checksum}
        )

    def receiveHookName(self, bs: io.BytesIO):
        """
        Reads a hook name from a given BytesIO stream.

        This method reads the first 2 bytes to determine the length of the hook name,
        then reads the hook name of that length from the stream and decodes it using UTF-8 encoding.

        Args:
            bs (io.BytesIO): The input stream containing the hook name.

        Returns:
            (str): The decoded hook name.

        Reference:
            [CIS-2 Specification](http://proposals.concordium.software/CIS/cis-2.html#receivehookname)
        """

        n = int.from_bytes(bs.read(2), byteorder="little")
        name = bs.read(n)
        return bytes.decode(name, "UTF-8")

    def additionalData(self, bs: io.BytesIO):
        """
        Reads additional data from a BytesIO stream.

        This method reads a 2-byte little-endian integer from the given BytesIO stream,
        which indicates the length of the subsequent data. It then reads that many bytes
        from the stream and returns them as a hexadecimal string.

        Args:
            bs (io.BytesIO): The BytesIO stream to read from.

        Returns:
            (str): The hexadecimal representation of the read bytes.

        Reference:
            [CIS-2 Additional Data](http://proposals.concordium.software/CIS/cis-2.html#additionaldata)
        """

        n = int.from_bytes(bs.read(2), byteorder="little")
        return bytes.hex(bs.read(n))

    def balanceOfQuery(self, tokenID: str, address: str):
        """
        Queries the balance of a specific token for a given address.

        Args:
            tokenID (str): The ID of the token to query.
            address (str): The address to query the token balance for.

        Returns:
            (bytes): The serialized query data.

        Reference:
            [CIS-2 Standard](http://proposals.concordium.software/CIS/cis-2.html#id3)
        """
        sp = io.BytesIO()

        tokenID = self.generate_tokenID(tokenID)
        address = self.generate_address(address)
        sp.write(tokenID)
        sp.write(address)
        return sp.getvalue()

    def CIS2balanceOfQuery(
        self, cis2_contract: CCD_ContractAddress, tokenID: str, public_key: str
    ):
        sp = io.BytesIO()

        tokenID = self.generate_tokenID(tokenID)
        contract_ = self.generate_contract_address(cis2_contract.to_str())
        public_key_ = self.generate_public_key_ed25519(public_key)

        sp.write(tokenID)
        sp.write(contract_)
        sp.write(public_key_)
        return sp.getvalue()

    def CIS2balanceOfParameter(
        self, cis2_contract: CCD_ContractAddress, token_id: str, public_keys: list[str]
    ) -> bytes:
        sp = io.BytesIO()
        sp.write(int(len(public_keys)).to_bytes(2, "little"))
        for public_key in public_keys:
            sp.write(self.CIS2balanceOfQuery(cis2_contract, token_id, public_key))
        return sp.getvalue()

    def CCDbalanceOfParameter(self, public_keys: list[str]) -> bytes:
        sp = io.BytesIO()
        sp.write(int(len(public_keys)).to_bytes(2, "little"))
        for public_key in public_keys:
            sp.write(self.generate_public_key_ed25519(public_key))
        return sp.getvalue()

    def balanceOfParameter(self, tokenID: str, addresses: list[str]) -> bytes:
        """
        Generates a byte stream representing the balance of a parameter for a given token ID and a list of addresses.

        Args:
            tokenID (str): The token ID for which the balance is being queried.
            addresses (list[str]): A list of addresses to query the balance for.

        Returns:
            (bytes): A byte stream containing the balance information for the given token ID and addresses.

        Reference:
            [CIS-2 Standard](http://proposals.concordium.software/CIS/cis-2.html#id3)
        """

        sp = io.BytesIO()
        sp.write(int(len(addresses)).to_bytes(2, "little"))
        for address in addresses:
            sp.write(self.balanceOfQuery(tokenID, address))
        return sp.getvalue()

    def CIS2balanceOfResponse(self, res: bytes):
        bs = io.BytesIO(bytes.fromhex(res.decode()))
        n = int.from_bytes(bs.read(2), byteorder="little")

        results = []
        for _ in range(n):
            results.append(self.token_amount(bs))

        return results

    def CCDbalanceOfResponse(self, res: bytes):
        bs = io.BytesIO(bytes.fromhex(res.decode()))
        n = int.from_bytes(bs.read(2), byteorder="little")

        results = []
        for _ in range(n):
            results.append(self.ccd_amount(bs))

        return results

    def balanceOfResponse(self, res: bytes):
        """
        Parses the response bytes to extract token balance information.

        The response format is defined in the CIS-2 standard:
        [CIS-2 Response](http://proposals.concordium.software/CIS/cis-2.html#response)

        Args:
            res (bytes): The response bytes to be parsed.

        Returns:
            (list): A list of token amounts extracted from the response.
        """
        bs = io.BytesIO(bytes.fromhex(res.decode()))
        n = int.from_bytes(bs.read(2), byteorder="little")

        results = []
        for _ in range(n):
            results.append(self.token_amount(bs))

        return results

    def generate_public_key_ed25519(self, public_key: str):
        sp = io.BytesIO()
        public_key_in_bytes = bytes.fromhex(public_key)
        sp.write(public_key_in_bytes)
        return sp.getvalue()

    def generate_tokenID(self, tokenID: str):
        sp = io.BytesIO()
        try:
            int(tokenID, 16)
            tokenID_in_bytes = bytes.fromhex(tokenID)
        except ValueError:
            tokenID_in_bytes = str.encode(tokenID)

        sp.write(int(len(tokenID_in_bytes)).to_bytes(1, "little"))
        sp.write(tokenID_in_bytes)
        return sp.getvalue()

    def generate_account_address(self, address: str):
        return bytearray(base58.b58decode_check(address)[1:])

    def generate_contract_address(self, address: str):
        contract_address = CCD_ContractAddress.from_str(address)

        sp = io.BytesIO()
        sp.write(int(contract_address.index).to_bytes(8, "little"))
        sp.write(int(contract_address.subindex).to_bytes(8, "little"))

        return sp.getvalue()

    def generate_address(self, address: str):
        sp = io.BytesIO()

        if len(address) == 50:
            sp.write(int(0).to_bytes(1, "little"))
            sp.write(self.generate_account_address(address))
        else:
            sp.write(int(1).to_bytes(1, "little"))
            sp.write(self.generate_contract_address(address))

        return sp.getvalue()

    def invoke_token_metadataUrl(self, tokenID: str) -> bool:
        parameter_bytes = self.tokenMetadataParameter(tokenID)

        ii = self.grpcclient.invoke_instance(
            "last_final",
            self.instance_index,
            self.instance_subindex,
            self.entrypoint,
            parameter_bytes,
            self.net,
        )

        res = ii.success.return_value
        return self.tokenMetadataResultParameter(res)

    def viewOwnerHistoryRequest(self, tokenID: str):
        return self.generate_tokenID(tokenID)

    def viewOwnerHistoryResponse(self, res: bytes):
        bs = io.BytesIO(bytes.fromhex(res.decode()))
        n = int.from_bytes(bs.read(1), byteorder="little")
        _ = bs.read(3)  # own_str
        results = []
        for _ in range(0, n):
            results.append(self.address(bs))

        return results

    def tokenMetadataParameter(self, tokenID: str):
        sp = io.BytesIO()
        sp.write(int(1).to_bytes(2, "little"))
        sp.write(self.generate_tokenID(tokenID))
        return sp.getvalue()

    def metadata_result(self, bs: bytes):
        n = int(bs[:2].decode("ASCII"))
        bs = io.BytesIO(bs)
        bs.read(2)
        url = self.url(n, bs)
        return url

    def metadata_response(self, bs: bytes):
        # bs: io.BytesIO = io.BytesIO(bs)
        if len(bs) > 0:
            n = int(bs[:2].decode("ASCII"))
            # n = int.from_bytes(bs.read(2), byteorder="big")
            responses = []
            for _ in range(n):
                responses.append(self.metadata_result(bs))
            return responses[0]
        else:
            return False, "Lookup Failure"

    def tokenMetadataResultParameter(self, res: bytes):
        bs = io.BytesIO(bytes.fromhex(res.decode()))
        n = int.from_bytes(bs.read(2), byteorder="little")
        results = []
        for _ in range(0, n):
            results.append(self.metadataUrl(bs))

        return results

    def operator_update(self, bs: io.BytesIO):
        n = int.from_bytes(bs.read(1), byteorder="little")
        if n == 0:
            return "Remove operator"
        elif n == 1:
            return "Add operator"

    def token_id(self, bs: io.BytesIO):
        """
        Extracts and returns the token ID from a given BytesIO stream.

        The token ID is read from the stream in the following manner:
        1. The first byte indicates the length of the token ID.
        2. The subsequent bytes represent the token ID itself.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the token ID data.

        Returns:
            (str): The hexadecimal representation of the token ID.

        Reference:
            [CIS-2 Token ID](http://proposals.concordium.software/CIS/cis-2.html#tokenid)
        """

        n = int.from_bytes(bs.read(1), byteorder="little")
        return bytes.hex(bs.read(n))

    def item_id(self, bs: io.BytesIO):
        """
        Extracts and returns the item ID from a given BytesIO stream.

        The item ID is read according to the CIS-6 specification.
        For more details, refer to the [CIS-6 documentation](http://proposals.concordium.software/CIS/cis-6.html#itemid).

        Args:
            bs (io.BytesIO): A BytesIO stream containing the item ID data.

        Returns:
            (str): The hexadecimal representation of the item ID.
        """
        n = int.from_bytes(bs.read(1), byteorder="little")
        return bytes.hex(bs.read(n))

    def status(self, bs: io.BytesIO):
        """
        Reads a single byte from the given BytesIO stream and returns its integer value.

        Args:
            bs (io.BytesIO): A BytesIO stream to read the byte from.

        Returns:
            (int): The integer value of the read byte.

        See Also:
            [CIS-6 Status](http://proposals.concordium.software/CIS/cis-6.html#status)
        """
        return int.from_bytes(bs.read(1), byteorder="little")

    def nonce(self, bs: io.BytesIO):
        """
        Extracts a nonce from a given BytesIO stream.

        The nonce is an 8-byte integer read from the stream in little-endian byte order.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the nonce.

        Returns:
            (int): The nonce as an integer.

        Reference:
            [CIS-3 Nonce](http://proposals.concordium.software/CIS/cis-3.html#nonce)
        """

        return int.from_bytes(bs.read(8), byteorder="little")

    def timestamp(self, bs: io.BytesIO):
        """
        Extracts a timestamp from a given BytesIO stream.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the timestamp.

        Returns:
            (int): The extracted timestamp as an integer.

        Reference:
            [CIS-3 Timestamp](http://proposals.concordium.software/CIS/cis-3.html#timestamp)
        """

        return int.from_bytes(bs.read(8), byteorder="little")

    def token_amount(self, bs: io.BytesIO):
        """
        Decodes and returns the token amount from a given BytesIO stream.

        This method reads a LEB128 encoded unsigned integer from the provided
        BytesIO stream and returns the decoded value.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the LEB128 encoded token amount.

        Returns:
            (int): The decoded token amount.

        See Also:
            [CIS-2 Token Amount](http://proposals.concordium.software/CIS/cis-2.html#tokenamount)
        """

        return leb128.u.decode_reader(bs)[0]

    def credential_id(self, bs: io.BytesIO):
        """
        Extracts and returns the credential ID from a given BytesIO stream.

        This method reads the first 32 bytes from the provided BytesIO stream
        and returns it as a hexadecimal string.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the credential data.

        Returns:
            (str): The hexadecimal representation of the credential ID.

        Reference:
            [CIS-4 Credential Holder ID](http://proposals.concordium.software/CIS/cis-4.html#credentialholderid)
        """
        return bytes.hex(bs.read(32))

    def credential_type(self, bs: io.BytesIO):
        """
        Parses the credential type from a given BytesIO stream.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the credential type data.

        Returns:
            (str): The hexadecimal representation of the credential type.

        Reference:
            [CIS-4 Credential Type](http://proposals.concordium.software/CIS/cis-4.html#credentialtype)
        """
        n = int.from_bytes(bs.read(1), byteorder="little")
        return bytes.hex(bs.read(n))

    def reason_string(self, bs: io.BytesIO):
        """
        Extracts a reason string from a given BytesIO stream.

        This method reads the first byte to determine the length of the reason string,
        then reads the subsequent bytes to extract the string and returns it in hexadecimal format.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the reason string data.

        Returns:
            (str): The reason string in hexadecimal format.

        Reference:
            [CIS-4 Reason String](http://proposals.concordium.software/CIS/cis-4.html#id9)
        """
        n = int.from_bytes(bs.read(1), byteorder="little")
        return bytes.hex(bs.read(n))

    def revoker(self, bs: io.BytesIO):
        """
        Determines the revoker type from a given byte stream.

        This method reads a single byte from the provided `io.BytesIO` stream and
        interprets it to determine the type of revoker. The mapping is as follows:
        - 0: "Issuer"
        - 1: "Holder"
        - 2: "Other" (with additional credential ID)

        Args:
            bs (io.BytesIO): A byte stream containing the revoker information.

        Returns:
            (str): A string representing the revoker type.

        Reference:
            [CIS-4 Specification](http://proposals.concordium.software/CIS/cis-4.html#id9)
        """
        n = int.from_bytes(bs.read(1), byteorder="little")
        if n == 0:
            return "Issuer"
        elif n == 1:
            return "Holder"
        elif n == 2:
            key_ = self.credential_id(bs)
            return f"Other ({key_})"

    def optional_reason(self, bs: io.BytesIO):
        """
        Parses an optional reason from a given BytesIO stream.

        This method reads the first byte to determine if a reason is present.
        If the byte is 0, it returns None. If the byte is 2, it reads and returns
        the reason string.

        Args:
            bs (io.BytesIO): The input byte stream to read from.

        Returns:
            (Optional[str]): The reason string if present, otherwise None.

        See Also:
            For more details, refer to the CIS-4 specification:
            [CIS-4 Specification](http://proposals.concordium.software/CIS/cis-4.html#id9)
        """
        n = int.from_bytes(bs.read(1), byteorder="little")
        if n == 0:
            return None
        elif n == 2:
            reason_string_ = self.reason_string(bs)
            return reason_string_

    def signature_ed25519(self, bs: io.BytesIO) -> str:
        """
        Generates an Ed25519 signature from the given BytesIO stream.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the data to be signed.

        Returns:
            (str): A hexadecimal string representation of the Ed25519 signature.

        See Also:
            [CIS-3 Signature Ed25519](http://proposals.concordium.software/CIS/cis-3.html#signatureed25519)
        """
        return bytes.hex(bs.read(64))

    def genesis_hash(self, bs: io.BytesIO) -> str:
        """
        Computes the genesis hash from a given BytesIO stream.

        This method reads the first 32 bytes from the provided BytesIO stream
        and returns its hexadecimal representation.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the data to hash.

        Returns:
            (str): The hexadecimal representation of the first 32 bytes of the stream.

        See Also:
            [CIS-5 Chain Context](http://proposals.concordium.software/CIS/cis-5.html#chaincontext)
        """
        return bytes.hex(bs.read(32))

    def chain_context(self, bs: io.BytesIO):
        """
        Parses the chain context from the given BytesIO stream.

        This method extracts the genesis hash, contract index, and contract subindex
        from the provided binary stream.

        Args:
            bs (io.BytesIO): The binary stream containing the chain context data.

        Returns:
            (tuple): A tuple containing the genesis hash, contract index, and contract subindex.

        Reference:
            For more details, see the CIS-5 specification:
            [CIS-5 Chain Context](http://proposals.concordium.software/CIS/cis-5.html#chaincontext)
        """
        genesis_hash_ = self.genesis_hash(bs)
        contract_index_ = self.contract_index(bs)
        contract_subindex_ = self.contract_subindex(bs)
        return genesis_hash_, contract_index_, contract_subindex_

    def revocation_key_action(self, bs: io.BytesIO):
        """
        Processes the revocation key action from the given byte stream.

        Args:
            bs (io.BytesIO): A byte stream containing the revocation key action data.

        Returns:
            (str): A string indicating the action, either "Register" or "Remove".

        Reference:
            For more details, see the CIS-4 proposal documentation:
            [CIS-4 Revocation Key Event](http://proposals.concordium.software/CIS/cis-4.html#revocationkeyevent)
        """
        n = int.from_bytes(bs.read(1), byteorder="little")
        if n == 0:
            return "Register"
        elif n == 1:
            return "Remove"

    def ccd_amount(self, bs: io.BytesIO) -> int:
        """
        Extracts the CCD amount from a given BytesIO stream.

        This method reads 8 bytes from the provided BytesIO stream and converts it
        to an integer using little-endian byte order.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the CCD amount.

        Returns:
            (int): The CCD amount as an integer.

        Reference:
            [CIS-5 CCD Amount](http://proposals.concordium.software/CIS/cis-5.html#ccdamount)
        """
        return int.from_bytes(bs.read(8), byteorder="little")

    def contract_index(self, bs: io.BytesIO) -> str:
        """
        Extracts and returns the contract index from a given BytesIO stream.

        The contract index is read as the first 8 bytes from the stream and
        returned as a hexadecimal string.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the contract data.

        Returns:
            (str): The contract index as a hexadecimal string.

        Reference:
            [CIS-2 Contract Address](http://proposals.concordium.software/CIS/cis-2.html#contractaddress)
        """
        return bytes.hex(bs.read(8))

    def contract_subindex(self, bs: io.BytesIO) -> str:
        """
        Extracts and returns a subindex from a binary stream.

        This method reads the first 8 bytes from the provided binary stream and
        converts them to a hexadecimal string representation.

        Args:
            bs (io.BytesIO): A binary stream from which the subindex is read.

        Returns:
            (str): The hexadecimal string representation of the subindex.

        See Also:
            [CIS-2 Contract Address](http://proposals.concordium.software/CIS/cis-2.html#contractaddress)
        """
        return bytes.hex(bs.read(8))

    def public_key_ed25519(self, bs: io.BytesIO) -> str:
        """
        Extracts and returns the hexadecimal representation of an Ed25519 public key from a given BytesIO stream.

        Args:
            bs (io.BytesIO): A BytesIO stream containing the public key data.

        Returns:
            (str): The hexadecimal string representation of the Ed25519 public key.

        Reference:
            [CIS-4 PublicKeyEd25519](http://proposals.concordium.software/CIS/cis-4.html#publickeyed25519)
        """
        return bytes.hex(bs.read(32))

    # CIS events
    def transferEvent(self, hexParameter: str) -> transferEvent:
        """
        Parses a hexadecimal string representing a transfer event and returns a transferEvent object.

        Args:
            hexParameter (str): A hexadecimal string representing the transfer event data.

        Returns:
            transferEvent: An object containing the parsed transfer event data.

        The transfer event data is parsed according to the CIS-2 standard.
        For more information, see the [CIS-2 Transfer Event documentation](http://proposals.concordium.software/CIS/cis-2.html#transferevent).
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        token_id_ = self.token_id(bs)
        amount_ = self.token_amount(bs)

        from_ = self.address(bs)
        from_ = self.format_address(from_)
        to_ = self.address(bs)
        to_ = self.format_address(to_)

        return transferEvent(
            **{
                "tag": tag_,
                "token_id": token_id_,
                "token_amount": amount_,
                "from_address": from_,
                "to_address": to_,
            }
        )

    def updateOperatorEvent(self, hexParameter: str) -> updateOperatorEvent:
        """
        Parses a hexadecimal parameter string and returns an updateOperatorEvent object.

        Args:
            hexParameter (str): The hexadecimal string representing the event data.

        Returns:
            updateOperatorEvent: An object containing the parsed event data.

        References:
            [CIS-2 Update Operator Event](http://proposals.concordium.software/CIS/cis-2.html#updateoperatorevent)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        update_ = self.operator_update(bs)

        owner_ = self.address(bs)
        owner_ = self.format_address(owner_)
        operator_ = self.address(bs)
        operator_ = self.format_address(operator_)

        return updateOperatorEvent(
            **{
                "tag": tag_,
                "operator_update": update_,
                "owner": owner_,
                "operator": operator_,
            }
        )

    def mintEvent(self, hexParameter: str) -> mintEvent:
        """
        Parses a hexadecimal string to extract and return a mintEvent object.

        Args:
            hexParameter (str): A hexadecimal string representing the event data.

        Returns:
            mintEvent: An object containing the parsed event data.

        The mintEvent object contains the following fields:
            - tag (int): The event tag.
            - token_id (int): The ID of the token.
            - token_amount (int): The amount of tokens.
            - to_address (str): The address to which the tokens are minted.

        For more details, refer to the CIS-2 specification:
        [CIS-2 Mint Event](http://proposals.concordium.software/CIS/cis-2.html#mintevent)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        token_id_ = self.token_id(bs)
        amount_ = self.token_amount(bs)
        to_ = self.address(bs)
        to_ = self.format_address(to_)

        return mintEvent(
            **{
                "tag": tag_,
                "token_id": token_id_,
                "token_amount": amount_,
                "to_address": to_,
            }
        )

    def burnEvent(self, hexParameter: str) -> burnEvent:
        """
        Parses a hexadecimal string to create a burnEvent object.

        Args:
            hexParameter (str): A hexadecimal string representing the burn event data.

        Returns:
            burnEvent: An instance of the burnEvent class containing parsed data.

        References:
            [CIS-2 Burn Event](http://proposals.concordium.software/CIS/cis-2.html#burnevent)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        token_id_ = self.token_id(bs)
        amount_ = self.token_amount(bs)
        from_ = self.address(bs)
        from_ = self.format_address(from_)

        return burnEvent(
            **{
                "tag": tag_,
                "token_id": token_id_,
                "token_amount": amount_,
                "from_address": from_,
            }
        )

    def tokenMetaDataEvent(self, hexParameter: str) -> tokenMetadataEvent:
        """
        Parses a hexadecimal string to extract token metadata event information.

        Args:
            hexParameter (str): A hexadecimal string representing the token metadata event.

        Returns:
            tokenMetadataEvent: An object containing the parsed token metadata event information.

        Reference:
            [CIS-2 Token Metadata Event](http://proposals.concordium.software/CIS/cis-2.html#tokenmetadataevent)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")

        token_id_ = self.token_id(bs)
        metadata_ = self.metadataUrl(bs)

        return tokenMetadataEvent(
            **{
                "tag": tag_,
                "token_id": token_id_,
                "metadata": metadata_,
            }
        )

    def nonceEventCIS3(self, hexParameter: str) -> nonceEventCIS3:
        """
        Parses a hexadecimal string to create a nonceEventCIS3 object.

        Args:
            hexParameter (str): A hexadecimal string representing the nonce event data.

        Returns:
            nonceEvent: An object containing the parsed nonce event data.

        Reference:
            For more details, see the [CIS-3 NonceEvent specification](http://proposals.concordium.software/CIS/cis-3.html#nonceevent).
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))
        tag_ = int.from_bytes(bs.read(1), byteorder="little")

        nonce_ = self.nonce(bs)
        sponsoree_ = self.account_address(bs)

        return nonceEventCIS3(
            **{
                "tag": tag_,
                "nonce": str(
                    nonce_
                ),  # to cover for strangely large nonces being bounced by Mongo.
                "sponsoree": sponsoree_,
            }
        )

    def nonceEventCIS5(self, hexParameter: str) -> nonceEventCIS5:
        """
        Parses a hexadecimal string to create a nonceEventCIS5 object.

        Args:
            hexParameter (str): A hexadecimal string representing the nonce event data.

        Returns:
            nonceEvent: An object containing the parsed nonce event data.

        Reference:
            For more details, see the [CIS-5 NonceEvent specification](http://proposals.concordium.software/CIS/cis-5.html#nonceevent).
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))
        tag_ = int.from_bytes(bs.read(1), byteorder="little")

        nonce_ = self.nonce(bs)
        sponsoree_ = self.public_key_ed25519(bs)

        return nonceEventCIS5(
            **{
                "tag": tag_,
                "nonce": str(
                    nonce_
                ),  # to cover for strangely large nonces being bounced by Mongo.
                "sponsoree": sponsoree_,
            }
        )

    def registerCredentialEvent(self, hexParameter: str) -> registerCredentialEvent:
        """
        Registers a credential event by parsing a hexadecimal parameter.

        Args:
            hexParameter (str): A string representing the hexadecimal parameter to be parsed.

        Returns:
            dict: A dictionary containing the parsed credential event details with keys:
                - "tag" (int): The tag value.
                - "credential_id" (str): The credential ID.
                - "schema_ref" (str): The schema reference.
                - "credential_type" (str): The credential type.

        See Also:
            [CIS-4 Register Credential Event](http://proposals.concordium.software/CIS/cis-4.html#registercredentialevent)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        credential_id_ = self.credential_id(bs)
        schema_ref_ = self.schema_ref(bs)
        credential_type_ = self.credential_type(bs)
        return registerCredentialEvent(
            **{
                "tag": tag_,
                "credential_id": credential_id_,
                "schema_ref": schema_ref_,
                "credential_type": credential_type_,
            }
        )

    def revokeCredentialEvent(self, hexParameter: str) -> revokeCredentialEvent:
        """
        Parses a hexadecimal string representing a revoke credential event and returns a dictionary with the event details.

        Args:
            hexParameter (str): A hexadecimal string representing the revoke credential event.

        Returns:
            dict: A dictionary containing the parsed event details with keys 'tag', 'credential_id', 'revoker', and 'reason'.

        Reference:
            [CIS-4 RevokeCredentialEvent](http://proposals.concordium.software/CIS/cis-4.html#revokecredentialevent)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        credential_id_ = self.credential_id(bs)
        revoker_ = self.revoker(bs)
        reason_ = self.optional_reason(bs)
        return revokeCredentialEvent(
            **{
                "tag": tag_,
                "credential_id": credential_id_,
                "revoker": revoker_,
                "reason": reason_,
            }
        )

    def issuerMetaDataEvent(self, hexParameter: str) -> issuerMetadataEvent:
        """
        Parses the issuer metadata event from a hexadecimal parameter.

        Args:
            hexParameter (str): The hexadecimal string representing the issuer metadata event.

        Returns:
            issuerMetadataEvent: An instance of issuerMetadataEvent containing the parsed metadata.

        Reference:
            For more details, see the CIS-4 specification:
            [CIS-4 Issuer Metadata](http://proposals.concordium.software/CIS/cis-4.html#issuermetadata)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        metadata_ = self.metadataUrl(bs)

        return issuerMetadataEvent(
            **{
                "tag": tag_,
                "metadata": metadata_,
            }
        )

    def credentialMetaDataEvent(self, hexParameter: str) -> credentialMetadataEvent:
        """
        Parses a hexadecimal string to extract credential metadata event information.

        Args:
            hexParameter (str): A hexadecimal string representing the credential metadata event.

        Returns:
            credentialMetadataEvent: An object containing the parsed credential metadata event information.

        See Also:
            [CIS-4 Credential Metadata Event](http://proposals.concordium.software/CIS/cis-4.html#credentialmetadataevent)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        credential_id_ = self.credential_id(bs)
        metadata_ = self.metadataUrl(bs)

        return credentialMetadataEvent(
            **{
                "tag": tag_,
                "id": credential_id_,
                "metadata": metadata_,
            }
        )

    def credentialSchemaRefEvent(self, hexParameter: str) -> credentialSchemaRefEvent:
        """
        Parses a hexadecimal parameter to extract and return a credential schema reference event.

        Args:
            hexParameter (str): A string representing the hexadecimal parameter to be parsed.

        Returns:
            dict: A dictionary containing the parsed event data with keys 'tag', 'type', and 'schema_ref'.

        Reference:
            For more details, see the CIS-4 documentation:
            [CIS-4 Credential Schema Reference Event](http://proposals.concordium.software/CIS/cis-4.html#credentialschemarefevent)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        schema_ref_ = self.schema_ref(bs)
        credential_type_ = self.credential_type(bs)
        return credentialSchemaRefEvent(
            **{
                "tag": tag_,
                "type": credential_type_,
                "schema_ref": schema_ref_,
            }
        )

    def revocationKeyEvent(self, hexParameter: str) -> revocationKeyEvent:
        """
        Parses a hexadecimal parameter to extract and return a revocation key event.

        Args:
            hexParameter (str): A string representing the hexadecimal parameter.

        Returns:
            revocationKeyEvent: An instance of revocationKeyEvent containing the parsed data.

        References:
            For more information, see the [CIS-4 Revocation Key Event](http://proposals.concordium.software/CIS/cis-4.html#revocationkeyevent) documentation.
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        public_key_ = self.public_key_ed25519(bs)
        action = self.revocation_key_action(bs)

        return revocationKeyEvent(
            **{
                "tag": tag_,
                "public_key_ed25519": public_key_,
                "action": action,
            }
        )

    def ItemCreatedEvent(self, hexParameter: str) -> itemCreatedEvent:
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")

        item_id_ = self.item_id(bs)
        metadata_ = self.metadataUrl(bs)
        initial_status_ = self.status(bs)

        return itemCreatedEvent(
            **{
                "tag": tag_,
                "item_id": item_id_,
                "metadata": metadata_,
                "initial_status": initial_status_,
            }
        )

    def ItemStatusChangedEvent(self, hexParameter: str) -> itemStatusChangedEvent:
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")

        item_id_ = self.item_id(bs)
        new_status_ = self.status(bs)
        additional_data_ = self.additionalData(bs)

        return itemStatusChangedEvent(
            **{
                "tag": tag_,
                "item_id": item_id_,
                "new_status": new_status_,
                "additional_data": additional_data_,
            }
        )

    def itemCreatedEvent(self, hexParameter: str) -> itemCreatedEvent:
        """
        Parses a hexadecimal parameter to create an itemCreatedEvent.

        Args:
            hexParameter (str): The hexadecimal string representing the event data.

        Returns:
            itemCreatedEvent: An instance of itemCreatedEvent with parsed data.

        References:
            [CIS-6 Item Created Event](http://proposals.concordium.software/CIS/cis-6.html#itemcreatedevent)
        """

        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")

        item_id_ = self.item_id(bs)
        metadata_ = self.metadataUrl(bs)
        initial_status_ = self.status(bs)

        return itemCreatedEvent(
            **{
                "tag": tag_,
                "item_id": item_id_,
                "metadata": metadata_,
                "initial_status": initial_status_,
            }
        )

    def itemStatusChangedEvent(self, hexParameter: str) -> itemStatusChangedEvent:
        """
        Parses a hexadecimal parameter string and returns an itemStatusChangedEvent object.

        For more details, refer to the [CIS-6 documentation](http://proposals.concordium.software/CIS/cis-6.html#itemstatuschangedevent).

        Args:
            hexParameter (str): The hexadecimal string representing the event data.

        Returns:
            itemStatusChangedEvent: An object containing the parsed event data with the following fields:
                - tag (int): The tag value extracted from the event data.
                - item_id (int): The item ID extracted from the event data.
                - new_status (int): The new status extracted from the event data.
                - additional_data (bytes): Any additional data extracted from the event data.
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")

        item_id_ = self.item_id(bs)
        new_status_ = self.status(bs)
        additional_data_ = self.additionalData(bs)

        return itemStatusChangedEvent(
            **{
                "tag": tag_,
                "item_id": item_id_,
                "new_status": new_status_,
                "additional_data": additional_data_,
            }
        )

    def process_tnt_log_event(
        self, hexParameter: str
    ) -> (
        tuple[Literal[237], itemCreatedEvent]
        | tuple[Literal[237], None]
        | tuple[Literal[236], itemStatusChangedEvent]
        | tuple[Literal[236], None]
        | tuple[int, str]
    ):
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        if tag_ == 237:
            try:
                event = self.ItemCreatedEvent(hexParameter)
                return tag_, event
            except:  # noqa: E722
                return tag_, None
        elif tag_ == 236:
            try:
                event = self.ItemStatusChangedEvent(hexParameter)
                return tag_, event
            except:  # noqa: E722
                return tag_, None
        else:
            return tag_, f"Custom even with tag={tag_}."

    def fiveStarsRegisterAccess(
        self, hexParameter: str
    ) -> fiveStarsRegisterAccessEvent:
        """Process custom register_access event from 5TARS contract."""
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        public_key_ = self.public_key_ed25519(bs)
        timestamp_ = self.timestamp(bs)

        return fiveStarsRegisterAccessEvent(
            **{
                "tag": tag_,
                "public_key": public_key_,
                "timestamp": timestamp_,
            }
        )

    def process_log_events(
        self, hexParameter: str
    ) -> (
        tuple[Literal[255], transferEvent]
        | tuple[Literal[255], None]
        | tuple[Literal[254], mintEvent]
        | tuple[Literal[254], None]
        | tuple[Literal[253], burnEvent]
        | tuple[Literal[253], None]
        | tuple[Literal[252], updateOperatorEvent]
        | tuple[Literal[252], None]
        | tuple[Literal[251], tokenMetadataEvent]
        | tuple[Literal[251], None]
        | tuple[Literal[250], nonceEventCIS3]
        | tuple[Literal[250], None]
        | tuple[Literal[249], registerCredentialEvent]
        | tuple[Literal[249], None]
        | tuple[Literal[248], revokeCredentialEvent]
        | tuple[Literal[248], None]
        | tuple[Literal[247], issuerMetadataEvent]
        | tuple[Literal[247], None]
        | tuple[Literal[246], credentialMetadataEvent]
        | tuple[Literal[246], None]
        | tuple[Literal[245], credentialSchemaRefEvent]
        | tuple[Literal[245], None]
        | tuple[Literal[244], revocationKeyEvent]
        | tuple[Literal[244], None]
        | tuple[int, str]
    ):
        """Function to determine, based on the tag, whcih event to parse."""
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        if tag_ == 255:
            try:
                event = self.transferEvent(hexParameter)
                return tag_, event
            except:  # noqa: E722
                return tag_, None
        elif tag_ == 254:
            try:
                event = self.mintEvent(hexParameter)
                return tag_, event
            except:  # noqa: E722
                return tag_, None
        elif tag_ == 253:
            try:
                event = self.burnEvent(hexParameter)
                return tag_, event
            except:  # noqa: E722
                return tag_, None
        elif tag_ == 252:
            try:
                event = self.updateOperatorEvent(hexParameter)
                return tag_, event
            except:  # noqa: E722
                return tag_, None
        elif tag_ == 251:
            try:
                event = self.tokenMetaDataEvent(hexParameter)
                return tag_, event
            except:  # noqa: E722
                return tag_, None
        elif tag_ == 250:
            try:
                event = self.nonceEventCIS3(hexParameter)
                return tag_, event
            except:  # noqa: E722
                return tag_, None
        elif tag_ == 249:
            try:
                event = self.registerCredentialEvent(hexParameter)
                return tag_, event
            except:  # noqa: E722
                return tag_, None
        elif tag_ == 248:
            try:
                event = self.revokeCredentialEvent(hexParameter)
                return tag_, event
            except:  # noqa: E722
                return tag_, None
        elif tag_ == 247:
            try:
                event = self.issuerMetaDataEvent(hexParameter)
                return tag_, event
            except:  # noqa: E722
                return tag_, None
        elif tag_ == 246:
            try:
                event = self.credentialMetaDataEvent(hexParameter)
                return tag_, event
            except:  # noqa: E722
                return tag_, None
        elif tag_ == 245:
            try:
                event = self.credentialSchemaRefEvent(hexParameter)
                return tag_, event
            except:  # noqa: E722
                return tag_, None
        elif tag_ == 244:
            try:
                event = self.revocationKeyEvent(hexParameter)
                return tag_, event
            except:  # noqa: E722
                return tag_, None
        else:
            return tag_, f"Custom even with tag={tag_}."

    def depositCCDEvent(self, hexParameter: str) -> depositCCDEvent:
        """
        Parses a hexadecimal parameter string and returns a depositCCDEvent object.

        Args:
            hexParameter (str): A string containing the hexadecimal representation of the event data.

        Returns:
            depositCCDEvent: An object containing the parsed event data.

        The function reads the following data from the hexadecimal string:
            - tag: An integer representing the event tag.
            - ccd_amount: The amount of CCD involved in the event.
            - from_address: The address from which the CCD is sent.
            - to_public_key_ed25519: The public key of the recipient.

        For more details, refer to the CIS-5 specification:
        [CIS-5 Deposit CCD Event](http://proposals.concordium.software/CIS/cis-5.html#depositccdevent)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        ccd_amount_ = self.ccd_amount(bs)
        address_ = self.address(bs)
        to_ = self.public_key_ed25519(bs)
        address_ = self.format_address(address_)

        return depositCCDEvent(
            **{
                "tag": tag_,
                "ccd_amount": ccd_amount_,
                "from_address": address_,
                "to_public_key_ed25519": to_,
            }
        )

    def depositCIS2TokensEvent(self, hexParameter: str) -> depositCIS2TokensEvent:
        """
        Parses a hexadecimal string representing a CIS-2 token deposit event and returns a depositCIS2TokensEvent object.

        Args:
            hexParameter (str): A hexadecimal string representing the CIS-2 token deposit event.

        Returns:
            depositCIS2TokensEvent: An object containing the parsed event data.

        The event data includes:
            - tag (int): The event tag.
            - token_amount (int): The amount of tokens deposited.
            - token_id (int): The ID of the token.
            - cis2_token_contract_address (str): The contract address of the CIS-2 token.
            - from_address (str): The address from which the tokens were sent.
            - to_public_key_ed25519 (str): The public key of the recipient.

        For more details, refer to the CIS-5 specification:
        [CIS-5 Specification](http://proposals.concordium.software/CIS/cis-5.html#depositcis2tokensevent)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        token_amount_ = self.token_amount(bs)
        token_id_ = self.token_id(bs)
        cis2_token_contract_address_ = self.contract_address(bs)
        from_ = self.address(bs)
        from_ = self.format_address(from_)
        to_ = self.public_key_ed25519(bs)

        # transform contract_address into string
        cis2_token_contract_address_str = CCD_ContractAddress.from_index(
            cis2_token_contract_address_[0], cis2_token_contract_address_[1]
        ).to_str()

        return depositCIS2TokensEvent(
            **{
                "tag": tag_,
                "token_amount": token_amount_,
                "token_id": token_id_,
                "cis2_token_contract_address": cis2_token_contract_address_str,
                "from_address": from_,
                "to_public_key_ed25519": to_,
            }
        )

    def withdrawCCDEvent(self, hexParameter: str) -> withdrawCCDEvent:
        """
        Parses a hexadecimal string representing a CCD withdrawal event and returns a dictionary with the event details.

        Args:
            hexParameter (str): A hexadecimal string representing the CCD withdrawal event.

        Returns:
            dict: A dictionary containing the parsed event details:
                - tag (int): The event tag.
                - ccd_amount (int): The amount of CCD withdrawn.
                - from_public_key_ed25519 (bytes): The public key of the sender.
                - to_address (str): The formatted address of the recipient.

        Reference:
            [CIS-5 Withdraw CCD Event](http://proposals.concordium.software/CIS/cis-5.html#withdrawccdevent)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        ccd_amount_ = self.ccd_amount(bs)
        from_ = self.public_key_ed25519(bs)
        to_ = self.address(bs)
        to_ = self.format_address(to_)

        return withdrawCCDEvent(
            **{
                "tag": tag_,
                "ccd_amount": ccd_amount_,
                "from_public_key_ed25519": from_,
                "to_address": to_,
            }
        )

    def withdrawCIS2TokensEvent(self, hexParameter: str) -> withdrawCIS2TokensEvent:
        """
        Parses a hexadecimal parameter to extract and return details of a CIS-2 token withdrawal event.

        Args:
            hexParameter (str): A hexadecimal string representing the event data.

        Returns:
            withdrawCIS2TokensEvent: An instance of withdrawCIS2TokensEvent containing the parsed event details.

        Event Details:
            - tag (int): The event tag.
            - token_amount (int): The amount of tokens withdrawn.
            - token_id (int): The ID of the token.
            - cis2_token_contract_address (str): The contract address of the CIS-2 token in string format.
            - from_public_key_ed25519 (bytes): The public key of the sender in Ed25519 format.
            - to_address (str): The address of the recipient.

        Reference:
            For more details, see the CIS-5 specification: [CIS-5 WithdrawCIS2TokensEvent](http://proposals.concordium.software/CIS/cis-5.html#withdrawcis2tokensevent)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        token_amount_ = self.token_amount(bs)
        token_id_ = self.token_id(bs)
        cis2_token_contract_address_ = self.contract_address(bs)
        from_ = self.public_key_ed25519(bs)
        to_ = self.address(bs)
        to_ = self.format_address(to_)

        # transform contract_address into string
        cis2_token_contract_address_str = CCD_ContractAddress.from_index(
            cis2_token_contract_address_[0], cis2_token_contract_address_[1]
        ).to_str()

        return withdrawCIS2TokensEvent(
            **{
                "tag": tag_,
                "token_amount": token_amount_,
                "token_id": token_id_,
                "cis2_token_contract_address": cis2_token_contract_address_str,
                "from_public_key_ed25519": from_,
                "to_address": to_,
            }
        )

    def transferCCDEvent(self, hexParameter: str) -> transferCCDEvent:
        """
        Parses a hexadecimal string representing a CCD transfer event and returns a transferCCDEvent object.

        Args:
            hexParameter (str): A hexadecimal string representing the CCD transfer event.

        Returns:
            transferCCDEvent: An object containing the parsed CCD transfer event data.

        The CCD transfer event data includes:
            - tag (int): The event tag.
            - ccd_amount (int): The amount of CCD transferred.
            - from_public_key_ed25519 (bytes): The sender's public key in ED25519 format.
            - to_public_key_ed25519 (bytes): The recipient's public key in ED25519 format.

        For more details, refer to the CIS-5 specification:
        [CIS-5 Transfer CCD Event](http://proposals.concordium.software/CIS/cis-5.html#transferccdevent)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        ccd_amount_ = self.ccd_amount(bs)
        from_ = self.public_key_ed25519(bs)
        to_ = self.public_key_ed25519(bs)

        return transferCCDEvent(
            **{
                "tag": tag_,
                "ccd_amount": ccd_amount_,
                "from_public_key_ed25519": from_,
                "to_public_key_ed25519": to_,
            }
        )

    def transferCIS2TokensEvent(self, hexParameter: str) -> transferCIS2TokensEvent:
        """
        Parses a hexadecimal string representing a CIS-2 token transfer event and returns a transferCIS2TokensEvent object.

        Args:
            hexParameter (str): A hexadecimal string containing the encoded CIS-2 token transfer event data.

        Returns:
            transferCIS2TokensEvent: An object containing the parsed event data, including:
                - tag (int): The event tag.
                - token_amount (int): The amount of tokens transferred.
                - token_id (int): The ID of the token being transferred.
                - cis2_token_contract_address (str): The contract address of the CIS-2 token as a string.
                - from_public_key_ed25519 (bytes): The public key of the sender in Ed25519 format.
                - to_public_key_ed25519 (bytes): The public key of the recipient in Ed25519 format.

        Reference:
            [CIS-5 Transfer CIS-2 Tokens Event](http://proposals.concordium.software/CIS/cis-5.html#transfercis2tokensevent)
        """
        bs = io.BytesIO(bytes.fromhex(hexParameter))

        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        token_amount_ = self.token_amount(bs)
        token_id_ = self.token_id(bs)
        cis2_token_contract_address_ = self.contract_address(bs)
        from_ = self.public_key_ed25519(bs)
        to_ = self.public_key_ed25519(bs)

        # transform contract_address into string
        cis2_token_contract_address_str = CCD_ContractAddress.from_index(
            cis2_token_contract_address_[0], cis2_token_contract_address_[1]
        ).to_str()

        return transferCIS2TokensEvent(
            **{
                "tag": tag_,
                "token_amount": token_amount_,
                "token_id": token_id_,
                "cis2_token_contract_address": cis2_token_contract_address_str,
                "from_public_key_ed25519": from_,
                "to_public_key_ed25519": to_,
            }
        )

    # Recognize event
    def recognize_event(
        self, event: str, standards: list[StandardIdentifiers], contract_name: str
    ):
        """
        Contracts can support multiple standards. Hence, depending on the tag we try
        to figure our which standard such an event is specified in and try to parse it.
        """
        bs = io.BytesIO(bytes.fromhex(event))
        tag_ = int.from_bytes(bs.read(1), byteorder="little")
        if StandardIdentifiers.CIS_2 in standards:
            if tag_ == 255:
                try:
                    event = self.transferEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-2.transfer_event",
                        StandardIdentifiers.CIS_2,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 254:
                try:
                    event = self.mintEvent(event)
                    return tag_, event, "CIS-2.mint_event", StandardIdentifiers.CIS_2
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 253:
                try:
                    event = self.burnEvent(event)
                    return tag_, event, "CIS-2.burn_event", StandardIdentifiers.CIS_2
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 252:
                try:
                    event = self.updateOperatorEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-2.operator_event",
                        StandardIdentifiers.CIS_2,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 251:
                try:
                    event = self.tokenMetaDataEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-2.metadata_event",
                        StandardIdentifiers.CIS_2,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            else:
                return tag_, None, None, None
        elif StandardIdentifiers.CIS_3 in standards:
            if tag_ == 250:
                try:
                    event = self.nonceEventCIS3(event)
                    return tag_, event, "CIS-3.nonce_event", StandardIdentifiers.CIS_3
                except:  # noqa: E722
                    return tag_, None, None, None
            else:
                return tag_, None, None, None
        elif StandardIdentifiers.CIS_4 in standards:
            if tag_ == 249:
                try:
                    event = self.registerCredentialEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-4.register_credential_event",
                        StandardIdentifiers.CIS_4,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 248:
                try:
                    event = self.revokeCredentialEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-4.revoke_credential_event",
                        StandardIdentifiers.CIS_4,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 247:
                try:
                    event = self.issuerMetaDataEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-4.issuer_metadata_event",
                        StandardIdentifiers.CIS_4,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 246:
                try:
                    event = self.credentialMetaDataEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-4.credential_metadata_event",
                        StandardIdentifiers.CIS_4,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 245:
                try:
                    event = self.credentialSchemaRefEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-4.credential_schemaref_event",
                        StandardIdentifiers.CIS_4,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 244:
                try:
                    event = self.revocationKeyEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-4.recovation_key_event",
                        StandardIdentifiers.CIS_4,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            else:
                return tag_, None, None, None
        elif StandardIdentifiers.CIS_5 in standards:
            if tag_ == 250:
                try:
                    event = self.nonceEventCIS5(event)
                    return tag_, event, "CIS-5.nonce_event", StandardIdentifiers.CIS_5
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 249:
                try:
                    event = self.depositCCDEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-5.deposit_ccd_event",
                        StandardIdentifiers.CIS_5,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 248:
                try:
                    event = self.depositCIS2TokensEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-5.deposit_cis2_tokens_event",
                        StandardIdentifiers.CIS_5,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 247:
                try:
                    event = self.withdrawCCDEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-5.withdraw_ccd_event",
                        StandardIdentifiers.CIS_5,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 246:
                try:
                    event = self.withdrawCIS2TokensEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-5.withdraw_cis2_tokens_event",
                        StandardIdentifiers.CIS_5,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 245:
                try:
                    event = self.transferCCDEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-5.transfer_ccd_event",
                        StandardIdentifiers.CIS_5,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 244:
                try:
                    event = self.transferCIS2TokensEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-5.transfer_cis2_tokens_event",
                        StandardIdentifiers.CIS_5,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            else:
                return tag_, None, None, None
        elif StandardIdentifiers.CIS_6 in standards:
            if tag_ == 237:
                try:
                    event = self.itemCreatedEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-6.item_created_event",
                        StandardIdentifiers.CIS_6,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            elif tag_ == 236:
                try:
                    event = self.itemStatusChangedEvent(event)
                    return (
                        tag_,
                        event,
                        "CIS-6.item_status_changed_event",
                        StandardIdentifiers.CIS_6,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            else:
                return (
                    tag_,
                    None,
                    None,
                    None,
                )
        # no CIS standard support
        else:
            # 5tars custom event
            if (contract_name == "five-stars-transaction") and (tag_ == 0):
                try:
                    event = self.fiveStarsRegisterAccess(event)
                    return (
                        tag_,
                        event,
                        "five_stars_register_access_event",
                        None,
                    )
                except:  # noqa: E722
                    return tag_, None, None, None
            else:
                return tag_, None, None, None
