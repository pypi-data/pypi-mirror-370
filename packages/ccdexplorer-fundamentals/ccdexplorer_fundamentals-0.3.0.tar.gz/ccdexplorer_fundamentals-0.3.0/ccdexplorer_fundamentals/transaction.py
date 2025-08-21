from enum import Enum
import dateutil
from .cns import CNSDomain, CNSActions

from ccdexplorer_fundamentals.block import ConcordiumBlockInfo
import io
from rich.console import Console

console = Console()


# sender, receiver, txHash, contract, amount, tokenId, self.cns_domain.domain_name, self
class ClassificationResult:
    def __init__(self):
        self.sender = None
        self.receiver = None
        self.txHash = None
        self.contract = None
        self.amount = None
        self.tokenId = None
        self.domain_name = None
        self.type = None
        self.contents = None
        self.accounts_involved_all = False
        self.accounts_involved_transfer = False
        self.contracts_involved = False
        self.list_of_contracts_involved = set()


class DelegationAndStakingResult:
    def __init__(self):
        self.sender = None
        self.bakerId = None
        self.txHash = None
        self.message = ""
        self.request_target = None
        self.perc = None
        self.unstaked = False
        self.unstaked_amount = 0


class TransactionClass(Enum):
    AccountTransaction = "accountTransaction"
    CredentialDeploymentTransaction = "credentialDeploymentTransaction"
    UpdateTransaction = "updateTransaction"


class TransactionType(Enum):
    # https://github.com/Concordium/concordium-scan/blob/e95e8b2b191fefcf381ef4b4a1c918dd1f11ae05/frontend/src/queries/useTransactionQuery.ts
    AccountCreated = """
    ... on AccountCreated {
        accountAddress {
            asString
        }
    }
    """
    AmountAddedByDecryption = """
    ... on AmountAddedByDecryption {
        amount
        accountAddress {
            asString
        }
    }
    """
    BakerAdded = """
    ... on BakerAdded {
        bakerId
        restakeEarnings
        stakedAmount
        electionKey
        signKey
        aggregationKey
        accountAddress {
            asString
        }
    }
    """
    BakerKeysUpdated = """
    ... on BakerKeysUpdated {
        bakerId
        electionKey
        signKey
        aggregationKey
        accountAddress {
            asString
        }
    }
    """
    BakerRemoved = """
    ... on BakerRemoved {
        bakerId
        accountAddress {
            asString
        }
    }
    """
    BakerSetBakingRewardCommission = """
    ... on BakerSetBakingRewardCommission {
        bakerId
        bakingRewardCommission
        accountAddress {
            asString
        }
    }
    """
    BakerSetFinalizationRewardCommission = """
    ... on BakerSetFinalizationRewardCommission {
        bakerId
        finalizationRewardCommission
        accountAddress {
            asString
        }
    }
    """
    BakerSetMetadataURL = """
    ... on BakerSetMetadataURL {
        bakerId
        metadataUrl
        accountAddress {
            asString
        }
    }
    """
    BakerSetOpenStatus = """
    ... on BakerSetOpenStatus {
        bakerId
        openStatus
        accountAddress {
            asString
        }
    }
    """
    BakerSetRestakeEarnings = """
    ... on BakerSetRestakeEarnings {
        bakerId
        restakeEarnings
        accountAddress {
            asString
        }
    }    
    """
    BakerSetTransactionFeeCommission = """
    ... on BakerSetTransactionFeeCommission {
        bakerId
        transactionFeeCommission
        accountAddress {
            asString
        }
    }
    """
    BakerStakeDecreased = """
    ... on BakerStakeDecreased {
        bakerId
        newStakedAmount
        accountAddress {
            asString
        }
    }
    """
    BakerStakeIncreased = """
    ... on BakerStakeIncreased {
        bakerId
        newStakedAmount
        accountAddress {
            asString
        }
    }
    """
    ChainUpdateEnqueued = """
    ... on ChainUpdateEnqueued {
        effectiveImmediately
        __typename
	effectiveTime
	payload {
		__typename
		...on AddAnonymityRevokerChainUpdatePayload {
			name
		}
		...on AddIdentityProviderChainUpdatePayload {
			name
		}
		...on BakerStakeThresholdChainUpdatePayload {
			amount
		}
		...on ElectionDifficultyChainUpdatePayload {
			electionDifficulty
		}
		...on EuroPerEnergyChainUpdatePayload {
			exchangeRate {
				numerator
				denominator
			}
		}
		...on FoundationAccountChainUpdatePayload {
			accountAddress {
				asString
			}
		}
		...on GasRewardsChainUpdatePayload {
			accountCreation
			baker
			chainUpdate
			finalizationProof
		}
		...on MicroCcdPerEuroChainUpdatePayload {
			exchangeRate {
				denominator
				numerator
			}
		}
		...on MintDistributionChainUpdatePayload {
			bakingReward
			finalizationReward
			mintPerSlot
		}
		...on ProtocolChainUpdatePayload {
			message
			specificationUrl
		}
		...on TransactionFeeDistributionChainUpdatePayload {
			baker
			gasAccount
		}
		...on CooldownParametersChainUpdatePayload {
			delegatorCooldown
			poolOwnerCooldown
		}
		...on TimeParametersChainUpdatePayload {
			mintPerPayday
			rewardPeriodLength
		}
		...on MintDistributionV1ChainUpdatePayload {
			bakingReward
			finalizationReward
		}
		...on PoolParametersChainUpdatePayload {
			bakingCommissionRange {
				min
				max
			}
			finalizationCommissionRange {
				min
				max
			}
			transactionCommissionRange {
				min
				max
			}
			passiveBakingCommission
			passiveFinalizationCommission
			passiveTransactionCommission
			minimumEquityCapital
			capitalBound
			leverageBound {
				denominator
				numerator
			}
		}
	}
    }
    """
    ContractInitialized = """
    ... on ContractInitialized {
        amount
        contractAddress {
            __typename
            asString
            index
            subIndex
        }
        HEX:eventsAsHex {
            nodes 
        }
        initName
        moduleRef
    }
    """
    ContractInterrupted = """
    ... on ContractInterrupted {
        contractAddress {
            __typename
            asString
            index
            subIndex
        }
        hex_events:eventsAsHex
    }
    """
    ContractModuleDeployed = """
    ... on ContractModuleDeployed {
        moduleRef
        __typename
    }
    """
    ContractResumed = """
    ... on ContractResumed {
        contractAddress {
            __typename
            asString
            index
            subIndex
        }
        success
    }
    """
    ContractUpdated = """
    ... on ContractUpdated {
        amount
        contractAddress {
            __typename
            asString
            index
            subIndex
        }
        eventsAsHex {
            nodes 
        }
        instigator {
            __typename
            ... on AccountAddress {
                __typename
                asString
            }
            ... on ContractAddress {
                __typename
                asString
                index
                subIndex
            }
        }
        messageAsHex
        receiveName
    }
    """
    CredentialDeployed = """
    ... on CredentialDeployed {
        accountAddress {
            asString
        }
        regId
    }
    """
    CredentialKeysUpdated = """
    ... on CredentialKeysUpdated {
        credId
    }
    """
    CredentialsUpdated = """
    ... on CredentialsUpdated {
        accountAddress {
            asString
        }
        newCredIds
        newThreshold
        removedCredIds
    }
    """
    DataRegistered = """
    ... on DataRegistered {
        dataAsHex
    }
    """
    DelegationAdded = """
    ... on DelegationAdded {
        accountAddress {
            asString
        }
        delegatorId
    }
    """
    DelegationRemoved = """
    ... on DelegationRemoved {
        accountAddress {
            asString
        }
        delegatorId
    }
    """
    DelegationSetDelegationTarget = """
    ... on DelegationSetDelegationTarget {
        accountAddress {
            asString
        }
        delegationTarget {
            __typename
            ... on BakerDelegationTarget {
                bakerId
            }
        }
        delegatorId
    }
    """
    DelegationSetRestakeEarnings = """
    ... on DelegationSetRestakeEarnings {
        accountAddress {
            asString
        }
        delegatorId
        restakeEarnings
    }
    """
    DelegationStakeDecreased = """
    ... on DelegationStakeDecreased {
        accountAddress {
            asString
        }
        delegatorId
        newStakedAmount
    }
    """
    DelegationStakeIncreased = """
    ... on DelegationStakeIncreased {
        accountAddress {
            asString
        }
        delegatorId
        newStakedAmount
    }
    """
    EncryptedAmountsRemoved = """
    ... on EncryptedAmountsRemoved {
        accountAddress {
                asString
            }
        inputAmount
        newEncryptedAmount
        upToIndex
    }
    """
    EncryptedSelfAmountAdded = """
    ... on EncryptedSelfAmountAdded {
        accountAddress {
                asString
            }
        amount
        newEncryptedAmount
    }
    """
    NewEncryptedAmount = """
    ... on NewEncryptedAmount {
        accountAddress {
                asString
            }
        encryptedAmount
        newIndex
    }
    """
    TransferMemo = """
    ... on TransferMemo {
        decoded {
            text
        }
        rawHex
    }
    """
    Transferred = """
    ... on Transferred {
        amount
        from {
            ... on AccountAddress {
            __typename
            asString
            }
            ... on ContractAddress {
            __typename
            index
            subIndex
            }
            __typename
        }
        to {
            ... on AccountAddress {
            __typename
            asString
            }
            ... on ContractAddress {
            __typename
            index
            subIndex
            asString
            }
            __typename
        }
        __typename
        }
    """
    TransferredWithSchedule = """
    ... on TransferredWithSchedule {
        amountsSchedule (first: 50) {
            nodes {
                amount
                timestamp
            }
        }
        fromAccountAddress {
            asString
        }
            
        toAccountAddress {
            asString
        }
        totalAmount
        }
        
    """


class EventOpenStatusFromQLToNode(Enum):
    OPEN_FOR_ALL = "openForAll"
    CLOSED_FOR_NEW = "closedForNew"
    CLOSED_FOR_ALL = "closedForAll"


class TransactionTypeFromQLToNode(Enum):
    AccountTransaction = "accountTransaction"
    CredentialDeploymentTransaction = "credentialDeploymentTransaction"
    UpdateTransaction = "updateTransaction"


class TransactionContentsFromQLToNode(Enum):
    # AccountTransaction
    ADD_BAKER = "addBaker"
    CONFIGURE_BAKER = "configureBaker"
    CONFIGURE_DELEGATION = "configureDelegation"
    DEPLOY_MODULE = "deployModule"
    ENCRYPTED_TRANSFER = "encryptedAmountTransfer"
    ENCRYPTED_TRANSFER_WITH_MEMO = "encryptedAmountTransferWithMemo"
    INITIALIZE_SMART_CONTRACT_INSTANCE = "initContract"
    REGISTER_DATA = "registerData"
    REMOVE_BAKER = "removeBaker"
    SIMPLE_TRANSFER = "transfer"
    SIMPLE_TRANSFER_WITH_MEMO = "transferWithMemo"
    TRANSFER_TO_ENCRYPTED = "transferToEncrypted"
    TRANSFER_TO_PUBLIC = "transferToPublic"
    TRANSFER_WITH_SCHEDULE = "transferWithSchedule"
    TRANSFER_WITH_SCHEDULE_WITH_MEMO = "transferWithScheduleAndMemo"
    UPDATE_BAKER_KEYS = "updateBakerKeys"
    UPDATE_BAKER_RESTAKE_EARNINGS = "updateBakerRestakeEarnings"
    UPDATE_BAKER_STAKE = "updateBakerStake"
    UPDATE_CREDENTIAL_KEYS = "updateCredentialKeys"
    UPDATE_CREDENTIALS = "updateCredentials"
    UPDATE_SMART_CONTRACT_INSTANCE = "update"
    UNKNOWN = "_unknown"

    # CredentialDeploymentTransaction
    NORMAL = "normal"
    INITIAL = "initial"

    # UpdateTransaction
    UPDATE_ADD_ANONYMITY_REVOKER = "updateAddAnonymityRevoker"
    UPDATE_ADD_IDENTITY_PROVIDER = "updateAddIdentityProvider"
    UPDATE_BAKER_STAKE_THRESHOLD = "updateBakerStake"
    UPDATE_COOLDOWN_PARAMETERS = "updateCooldownParameters"
    UPDATE_ELECTION_DIFFICULTY = "updateElectionDifficulty"
    UPDATE_EURO_PER_ENERGY = "updateEuroPerEnergy"
    UPDATE_FOUNDATION_ACCOUNT = "updateFoundationAccount"
    UPDATE_GAS_REWARDS = "updateGASRewards"
    UPDATE_LEVEL1_KEYS = "updateLevel1Keys"
    UPDATE_LEVEL2_KEYS = "updateLevel2Keys"
    UPDATE_MICRO_GTU_PER_EURO = "updateMicroGTUPerEuro"
    UPDATE_MINT_DISTRIBUTION = "updateMintDistribution"
    UPDATE_POOL_PARAMETERS = "updatePoolParameters"
    UPDATE_PROTOCOL = "updateProtocol"
    UPDATE_ROOT_KEYS = "updateRootKeys"
    UPDATE_TIME_PARAMETERS = "updateTimeParameters"
    UPDATE_TRANSACTION_FEE_DISTRIBUTION = "updateTransactionFeeDistribution"


class Reward:
    """ """

    def __init__(self, r):
        self.r = r

    def account_reward(self):
        r = self.r
        self.tag = r["tag"]

        if self.tag == "PaydayAccountReward":
            return r["account"]
        else:
            return None

    def pool_reward(self):
        r = self.r
        self.tag = r["tag"]

        if self.tag == "PaydayPoolReward":
            return r["poolOwner"]
        else:
            return None


class Event:
    def __init__(self, _event):
        self._event = _event
        self.d = {}

    def determineAddress(self, address):
        a = {}

        if address["__typename"] == "AccountAddress":
            a = {"type": "AddressAccount", "address": address["asString"]}
        elif address["__typename"] == "ContractAddress":
            a = {
                "type": "AddressContract",
                "address": {"index": address["index"], "subindex": address["subIndex"]},
            }
        return a

    def decode_memo(self, hex):
        # bs = bytes.fromhex(hex)
        # return bytes.decode(bs[1:], 'UTF-8')
        try:
            bs = io.BytesIO(bytes.fromhex(hex))
            n = int.from_bytes(bs.read(1), byteorder="little")
            value = bs.read(n)
            try:
                memo = bytes.decode(value, "UTF-8")
                return memo
            except UnicodeDecodeError:
                memo = bytes.decode(value[1:], "UTF-8")
                return memo
        except:
            return "Decoding failure..."

    def translate_memo_if_present(self):
        if self._event["tag"] == "TransferMemo":
            self._event["memo"] = self.decode_memo(self._event["memo"])

    def translate_event_from_graphQL(self):
        e = self._event
        etype = e["__typename"]
        self.d["tag"] = etype

        if etype == TransactionType.AccountCreated.name:
            self.d["contents"] = e["accountAddress"]["asString"]

        if etype == TransactionType.AmountAddedByDecryption.name:
            self.d["amount"] = int(e["amount"])
            self.d["account"] = e["accountAddress"]["asString"]

        elif etype == TransactionType.BakerSetOpenStatus.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["bakerId"] = e["bakerId"]
            self.d["openStatus"] = EventOpenStatusFromQLToNode[e["openStatus"]].value

        elif etype == TransactionType.BakerSetBakingRewardCommission.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["bakerId"] = e["bakerId"]
            self.d["bakingRewardCommission"] = e["bakingRewardCommission"]

        elif etype == TransactionType.BakerSetFinalizationRewardCommission.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["bakerId"] = e["bakerId"]
            self.d["finalizationRewardCommission"] = e["finalizationRewardCommission"]

        elif etype == TransactionType.BakerSetTransactionFeeCommission.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["bakerId"] = e["bakerId"]
            self.d["transactionFeeCommission"] = e["transactionFeeCommission"]

        elif etype == TransactionType.BakerSetMetadataURL.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["bakerId"] = e["bakerId"]
            self.d["metadataUrl"] = e["metadataUrl"]

        elif etype == TransactionType.DelegationAdded.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["delegatorId"] = e["delegatorId"]

        elif etype == TransactionType.DelegationSetDelegationTarget.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["delegatorId"] = e["delegatorId"]
            if e["delegationTarget"]["__typename"] == "PassiveDelegationTarget":
                self.d["delegationTarget"] = {"delegateType": "Passive"}
            else:
                self.d["delegationTarget"] = {
                    "delegateType": "Baker",
                    "bakerId": e["delegationTarget"]["bakerId"],
                }

        elif etype == TransactionType.DelegationSetRestakeEarnings.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["delegatorId"] = e["delegatorId"]
            self.d["restakeEarnings"] = e["restakeEarnings"]

        elif etype == TransactionType.DelegationRemoved.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["delegatorId"] = e["delegatorId"]

        elif etype == TransactionType.DelegationStakeDecreased.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["delegatorId"] = e["delegatorId"]
            self.d["newStake"] = e["newStakedAmount"]

        elif etype == TransactionType.DelegationStakeIncreased.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["delegatorId"] = e["delegatorId"]
            self.d["newStake"] = e["newStakedAmount"]

        elif etype == TransactionType.BakerAdded.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["bakerId"] = e["bakerId"]
            self.d["aggregationKey"] = e["aggregationKey"]
            self.d["electionKey"] = e["electionKey"]
            self.d["restakeEarnings"] = e["restakeEarnings"]
            self.d["signKey"] = e["signKey"]
            self.d["stake"] = e["stakedAmount"]

        elif etype == TransactionType.BakerKeysUpdated.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["bakerId"] = e["bakerId"]
            self.d["aggregationKey"] = e["aggregationKey"]
            self.d["electionKey"] = e["electionKey"]
            self.d["signKey"] = e["signKey"]

        elif etype == TransactionType.BakerRemoved.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["bakerId"] = e["bakerId"]

        elif etype == TransactionType.BakerSetRestakeEarnings.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["bakerId"] = e["bakerId"]
            self.d["restakeEarnings"] = e["restakeEarnings"]

        elif etype == TransactionType.BakerStakeDecreased.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["bakerId"] = e["bakerId"]
            self.d["newStake"] = e["newStakedAmount"]

        elif etype == TransactionType.BakerStakeIncreased.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["bakerId"] = e["bakerId"]
            self.d["newStake"] = e["newStakedAmount"]

        elif etype == TransactionType.ChainUpdateEnqueued.name:
            self.d["effectiveTime"] = dateutil.parser.parse(
                e["effectiveTime"]
            ).timestamp()
            if e["payload"]["__typename"] == "BakerStakeThresholdChainUpdatePayload":
                self.d["payload"] = {}
                self.d["payload"]["update"] = {
                    "minimumThresholdForBaking": e["payload"]["amount"]
                }
                self.d["payload"]["updateType"] = "bakerStakeThreshold"

            elif e["payload"]["__typename"] == "ProtocolChainUpdatePayload":
                self.d["payload"] = {}
                self.d["payload"]["update"] = {
                    "specificationUrl": e["payload"]["specificationUrl"],
                    "message": e["payload"]["message"],
                    "specificationHash": e["payload"]["specificationHash"],
                    "specificationAuxiliaryData": e["payload"][
                        "specificationAuxiliaryDataAsHex"
                    ],
                }
                self.d["payload"]["updateType"] = "protocol"
            else:
                self.d["payload"] = e["payload"]

        elif etype == TransactionType.ContractInitialized.name:
            self.d["address"] = {
                "index": e["contractAddress"]["index"],
                "subindex": e["contractAddress"]["subIndex"],
            }
            self.d["amount"] = e["amount"]
            self.d["contractVersion"] = 0  # note: not available in QL
            self.d["initName"] = e["initName"]
            self.d["ref"] = e["moduleRef"]
            self.d["events"] = e["HEX"]["nodes"]

        elif etype == TransactionType.ContractResumed.name:
            self.d["address"] = {
                "index": e["contractAddress"]["index"],
                "subindex": e["contractAddress"]["subIndex"],
            }
            self.d["success"] = e["success"]

        elif etype == TransactionType.ContractInterrupted.name:
            self.d["address"] = {
                "index": e["contractAddress"]["index"],
                "subindex": e["contractAddress"]["subIndex"],
            }
            self.d["events"] = e["hex_events"]

        elif etype == TransactionType.ContractUpdated.name:
            self.d["address"] = {
                "index": e["contractAddress"]["index"],
                "subindex": e["contractAddress"]["subIndex"],
            }
            self.d["amount"] = e["amount"]
            self.d["contractVersion"] = 0  # note: not available in QL
            self.d["instigator"] = self.determineAddress(e["instigator"])
            self.d["message"] = e["messageAsHex"]
            self.d["receiveName"] = e["receiveName"]
            self.d["events"] = e["eventsAsHex"]["nodes"]

        elif etype == TransactionType.ContractModuleDeployed.name:
            self.d["contents"] = e["moduleRef"]

        elif etype == TransactionType.CredentialDeployed.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["regId"] = e["regId"]

        elif etype == TransactionType.CredentialsUpdated.name:
            self.d["account"] = e["accountAddress"]["asString"]
            self.d["newCredIds"] = e["newCredIds"]
            self.d["newThreshold"] = e["newThreshold"]
            self.d["removedCredIds"] = e["removedCredIds"]

        elif etype == TransactionType.DataRegistered.name:
            self.d["data"] = e["dataAsHex"]

        elif etype == TransactionType.EncryptedAmountsRemoved.name:
            pass

        elif etype == TransactionType.NewEncryptedAmount.name:
            pass

        elif etype == TransactionType.TransferMemo.name:
            # note this is actually NOT the same as the node, as the node does NOT decode.
            self.d["memo"] = e["decoded"]["text"]

        elif etype == TransactionType.Transferred.name:
            self.d["amount"] = int(e["amount"])
            self.d["from"] = self.determineAddress(e["from"])
            self.d["to"] = self.determineAddress(e["to"])

        elif etype == TransactionType.TransferredWithSchedule.name:
            self.d["from"] = e["fromAccountAddress"]["asString"]
            self.d["to"] = e["toAccountAddress"]["asString"]
            self.d["amount"] = [
                (dateutil.parser.parse(x["timestamp"]).timestamp() * 1000, x["amount"])
                for x in e["amountsSchedule"]["nodes"]
            ]

        return self.d


class Transaction:
    """
    Canonical Transaction. Transactions from either the node or GraphQL will be morphed to fit this class
    Node language will be the go-to point, so graphQL terms are translated to fit the node.
    """

    def __init__(self, node):
        self.node = node
        self.block: ConcordiumBlockInfo

    def find_memo_and_amount(self):
        self.memo = None
        self.amount = None
        if (self.contents == "transferWithMemo") or (self.contents == "Transferred"):
            if "events" in self.result:
                for event in self.result.get("events", []):
                    if event["tag"] == TransactionType.TransferMemo.name:
                        self.memo = event["memo"]
                    if event["tag"] == TransactionType.Transferred.name:
                        self.amount = event["amount"]

        return self

    def get_domain_from_cache_or_node(self):
        if self.cns_domain.tokenId in self.node.cns_cache_by_token_id:
            self.cns_domain.domain_name = self.node.cns_cache_by_token_id[
                self.cns_domain.tokenId
            ]
            console.log(f"Using cache for {self.cns_domain.domain_name}")
        else:
            self.cns_domain.get_cns_domain_name(self.node, self.cns_domain.tokenId)

            self.node.cns_cache_by_token_id[self.cns_domain.tokenId] = (
                self.cns_domain.domain_name
            )
            self.node.cns_cache_by_name[self.cns_domain.domain_name] = (
                self.cns_domain.tokenId
            )
            self.node.save_cns_cache()
            console.log(f"Saving cache for {self.cns_domain.domain_name}")

    def set_possible_cns_domain(self):
        self.cns_domain = CNSDomain()
        if "events" in self.result:
            for event in self.result.get("events", []):
                if event["tag"] in [
                    TransactionType.ContractInterrupted.name,
                    "Interrupted",
                ]:
                    # console.log(f'{event["tag"]=}')
                    if "events" in event:
                        if len(event["events"]) > 0:
                            the_event = event["events"][0]

                            (
                                tag_,
                                contract_index,
                                contract_subindex,
                                token_id_,
                                seller_,
                                winner_,
                                price_,
                                seller_share,
                                royalty_length_,
                                royalties,
                                owner_,
                                bidder_,
                                amount_,
                            ) = self.cns_domain.finalize(the_event)

                            # tag_, contract_index, contract_subindex, \
                            # token_id_, bidder_, amount_ = self.cns_domain.bidEvent(the_event)

                            self.cns_domain.tokenId = token_id_
                            # self.cns_domain.amount = amount_

                            self.get_domain_from_cache_or_node()
                # console.log(f"{event['tag']=}")
                if event["tag"] in [TransactionType.ContractUpdated.name, "Updated"]:
                    # console.log(f'{event["receiveName"]=}')
                    self.cns_domain.function_calls[event["receiveName"]] = event[
                        "message"
                    ]

                    if event["receiveName"] == "BictoryCnsNft.transfer":
                        self.cns_domain.action = CNSActions.transfer
                        (
                            self.cns_domain.tokenId,
                            self.cns_domain.transfer_to,
                        ) = self.cns_domain.decode_transfer_to_from(event["message"])

                        self.get_domain_from_cache_or_node()

                    if event["receiveName"] == "BictoryCns.register":
                        self.cns_domain.amount = event["amount"]
                        self.cns_domain.action = CNSActions.register
                        (
                            self.cns_domain.domain_name,
                            self.cns_domain.register_address,
                            self.cns_domain.duration_years,
                        ) = self.cns_domain.decode_from_register(event["message"])

                    if event["receiveName"] == "BictoryCns.extend":
                        self.cns_domain.amount = event["amount"]
                        self.cns_domain.action = CNSActions.extend
                        (
                            self.cns_domain.domain_name,
                            self.cns_domain.duration_years,
                        ) = self.cns_domain.decode_from_extend(event["message"])

                    if event["receiveName"] == "BictoryCns.createSubdomain":
                        self.cns_domain.action = CNSActions.createSubdomain
                        self.cns_domain.amount = event["amount"]
                        self.cns_domain.subdomain = (
                            self.cns_domain.decode_subdomain_from(event["message"])
                        )

                    if event["receiveName"] == "BictoryCns.setAddress":
                        self.cns_domain.action = CNSActions.setAddress
                        (
                            self.cns_domain.domain_name,
                            self.cns_domain.set_address,
                        ) = self.cns_domain.decode_set_address_from(event["message"])

                    if event["receiveName"] == "BictoryCns.setData":
                        self.cns_domain.action = CNSActions.setData
                        (
                            self.cns_domain.domain_name,
                            self.cns_domain.set_data_key,
                            self.cns_domain.set_data_value,
                        ) = self.cns_domain.decode_set_data_from(event["message"])

                    if event["receiveName"] == "BictoryNftAuction.bid":
                        self.cns_domain.action = CNSActions.bid

                        if len(event["events"]) > 0:
                            the_event = event["events"][0]

                            (
                                tag_,
                                contract_index,
                                contract_subindex,
                                token_id_,
                                bidder_,
                                amount_,
                            ) = self.cns_domain.bidEvent(the_event)

                            self.cns_domain.tokenId = token_id_
                            self.cns_domain.amount = amount_

                            self.get_domain_from_cache_or_node()

                    if event["receiveName"] == "BictoryNftAuction.finalize":
                        self.cns_domain.action = CNSActions.finalize

                        if len(event["events"]) > 0:
                            the_event = event["events"][0]

                            (
                                tag_,
                                contract_index,
                                contract_subindex,
                                token_id_,
                                seller_,
                                winner_,
                                price_,
                                seller_share,
                                royalty_length_,
                                royalties,
                                owner_,
                                bidder_,
                                amount_,
                            ) = self.cns_domain.finalize(the_event)

                            self.cns_domain.tokenId = token_id_

                            self.get_domain_from_cache_or_node()

                    if event["receiveName"] == "BictoryNftAuction.cancel":
                        self.cns_domain.action = CNSActions.cancel

                        if len(event["events"]) > 0:
                            the_event = event["events"][0]

                            (
                                tag_,
                                contract_index,
                                contract_subindex,
                                token_id_,
                                owner_,
                            ) = self.cns_domain.cancelEvent(the_event)

                            self.cns_domain.tokenId = token_id_

                            self.get_domain_from_cache_or_node()

                    if event["receiveName"] == "BictoryCnsNft.getTokenExpiry":
                        self.cns_domain.action = CNSActions.getTokenExpiry
                        self.cns_domain.tokenId = self.cns_domain.decode_token_id_from(
                            event["message"]
                        )

                        self.get_domain_from_cache_or_node()

    def decode_possible_memo(self):
        _events = []
        if "events" in self.result:
            for event in self.result.get("events", []):
                Event(event).translate_memo_if_present()

    def init_from_node(self, t):
        # note that only blockHash, blockHeight, blockSlotTime, finalized is used
        self.block: ConcordiumBlockInfo = t.get("blockInfo", None)
        if not self.block:
            self.block = {}
            self.block["blockHash"] = t["hash"]
            self.block["blockHeight"] = t["blockHeight"]
            self.block["blockSlotTime"] = t["blockSlotTime"]
        self.cost = t["cost"]
        self.energyCost = t["energyCost"]
        self.hash = t["hash"]
        self.index = t["index"]
        if t["result"]["outcome"] == "success":
            self.result = {
                "events": t["result"]["events"],
                "outcome": t["result"]["outcome"],
            }
        else:
            self.result = {"outcome": t["result"]["outcome"]}
        self.sender = t["sender"]
        self.type = t["type"]["type"]  # accountTransaction
        self.contents = t["type"]["contents"]  # transfer
        self.decode_possible_memo()
        self.set_possible_cns_domain()
        # self.node = None
        # console.log(f"{self.hash=} | {self.cns_domain.domain_name=}")
        return self

    def init_from_mongo_tx(self, t):
        # note that only blockHash, blockHeight, blockSlotTime, finalized is used
        self.block = {}
        self.block["blockHash"] = t["blockHash"]
        self.block["blockHeight"] = t["blockHeight"]
        self.block["blockSlotTime"] = t["blockSlotTime"]
        self.cost = t["cost"]
        self.energyCost = t["energyCost"]
        self.hash = t["hash"]
        self.index = t["index"]
        if t["result"]["outcome"] == "success":
            self.result = {
                "events": t["result"]["events"],
                "outcome": t["result"]["outcome"],
            }
        else:
            self.result = {"outcome": t["result"]["outcome"]}
        self.sender = t["sender"]
        self.type = t["type"]["type"]  # accountTransaction
        self.contents = t["type"]["contents"]  # transfer
        self.decode_possible_memo()
        self.set_possible_cns_domain()
        # self.node = None
        # console.log(f"{self.hash=} | {self.cns_domain.domain_name=}")
        return self

    # Bot classification requirements
    def get_sum_amount_from_scheduled_transfer(self, events):
        sum = 0
        for event in events[0]["amount"]:
            sum += int(event[1])
        return sum

    def classify_transaction_for_bot(self):
        # console.log(f"BOT: {self.hash=} | {self.cns_domain.domain_name=}")
        t = self
        result = ClassificationResult()
        result.domain_name = self.cns_domain.domain_name
        result.accounts_involved_all = True
        result.type = t.type
        result.contents = t.contents
        result.sender = t.sender
        result.txHash = t.hash
        result.receiver = None

        if self.type == "credentialDeploymentTransaction":
            if t.result["outcome"] == "success":
                events = t.result["events"]

                for event in events:
                    if event["tag"] == "AccountCreated":
                        result.sender = event["contents"]

        if self.type == "accountTransaction":
            if t.result["outcome"] == "success":
                events = t.result["events"]

                for event in events:
                    if event["tag"] == "Transferred":
                        result.receiver = event["to"]["address"]
                        result.amount = event["amount"]
                        result.accounts_involved_transfer = True

                    elif event["tag"] == "TransferredWithSchedule":
                        result.receiver = event["to"]
                        result.amount = self.get_sum_amount_from_scheduled_transfer(
                            events
                        )
                        result.accounts_involved_transfer = True

                    elif event["tag"] == "ContractInitialized":
                        result.contract = {
                            "tag": event["tag"],
                            "index": event["address"]["index"],
                            "subindex": event["address"]["subindex"],
                        }

                        result.list_of_contracts_involved.add(
                            (event["address"]["index"], event["address"]["subindex"])
                        )
                        result.contracts_involved = True

                    elif event["tag"] == "Updated":
                        result.contract = {
                            "tag": event["tag"],
                            "index": event["address"]["index"],
                            "subindex": event["address"]["subindex"],
                        }

                        result.list_of_contracts_involved.add(
                            (event["address"]["index"], event["address"]["subindex"])
                        )
                        result.contracts_involved = True

                    elif event["tag"] == "Resumed":
                        result.contract = {
                            "tag": event["tag"],
                            "index": event["address"]["index"],
                            "subindex": event["address"]["subindex"],
                        }

                        result.list_of_contracts_involved.add(
                            (event["address"]["index"], event["address"]["subindex"])
                        )
                        result.contracts_involved = True

                    elif event["tag"] == "Interrupted":
                        result.contract = {
                            "tag": event["tag"],
                            "index": event["address"]["index"],
                            "subindex": event["address"]["subindex"],
                        }

                        result.list_of_contracts_involved.add(
                            (event["address"]["index"], event["address"]["subindex"])
                        )
                        result.contracts_involved = True

        if result.amount:
            result.amount = int(result.amount) / 1_000_000
        return result, self

    def request_delegated_amount_for_account_on_previous_block(
        self, account_id, block_height
    ):
        previous_block_hash = self.node.request_block_hash_at_height(block_height - 1)
        account_info_at_previous_block = self.node.request_accountInfo_at(
            previous_block_hash, account_id
        )
        if "accountDelegation" in account_info_at_previous_block:
            previous_amount = account_info_at_previous_block["accountDelegation"][
                "stakedAmount"
            ]
        else:
            previous_amount = None
        return previous_amount

    def request_staked_amount_for_account_on_previous_block(
        self, account_id, block_height
    ):
        previous_block_hash = self.node.request_block_hash_at_height(block_height - 1)
        account_info_at_previous_block = self.node.request_accountInfo_at(
            previous_block_hash, account_id
        )
        if "accountBaker" in account_info_at_previous_block:
            previous_amount = account_info_at_previous_block["accountBaker"][
                "stakedAmount"
            ]
        else:
            previous_amount = None
        return previous_amount

    def classify_transaction_for_bot_for_delegation_and_staking(self):
        t = self
        result = DelegationAndStakingResult()

        if self.type == "accountTransaction":
            result.sender = t.sender
            result.txHash = t.hash

            if t.result["outcome"] == "success":
                events = t.result["events"]

                for event in events:
                    perc = ""
                    # print (f"event = {event}")
                    if event["tag"] in ["BakerStakeDecreased"]:
                        result.bakerId = event["bakerId"]
                        previous_amount = (
                            self.request_staked_amount_for_account_on_previous_block(
                                result.sender, self.block.blockHeight
                            )
                        )
                        if previous_amount:
                            if int(previous_amount) > 0:
                                result.perc = f" ({(100*(int(previous_amount) - int(event['newStake']))/int(previous_amount)):,.2f}%)"
                                result.unstaked_amount = (
                                    int(previous_amount) - int(event["newStake"])
                                ) / 1_000_000

                    if event["tag"] in [
                        "DelegationStakeIncreased",
                        "DelegationStakeDecreased",
                    ]:
                        previous_amount = (
                            self.request_delegated_amount_for_account_on_previous_block(
                                result.sender, self.block.blockHeight
                            )
                        )
                        if previous_amount:
                            if int(previous_amount) > 0:
                                if int(event["newStake"]) > int(previous_amount):
                                    result.perc = f" ({(100*((int(event['newStake'])/int(previous_amount)) - 1)):,.2f}%)"
                                else:
                                    result.perc = f" ({(100*(int(previous_amount) - int(event['newStake']))/int(previous_amount)):,.2f}%)"

                    if event["tag"] == "DelegationSetDelegationTarget":
                        if event["delegationTarget"]["delegateType"] == "Baker":
                            result.bakerId = event["delegationTarget"]["bakerId"]
                            result.message += (
                                f"Delegation target set to {result.bakerId:,.0f}. "
                            )

                    elif event["tag"] == "DelegationStakeIncreased":
                        if previous_amount:
                            result.message += f"Stake increased{result.perc} to {(int(event['newStake'])/1_000_000):,.0f} CCD."
                        else:
                            result.message += f"Stake set to {(int(event['newStake'])/1_000_000):,.0f} CCD."
                        result.request_target = True

                    elif event["tag"] == "DelegationStakeDecreased":
                        result.message += f"Stake decreased{result.perc} to {(int(event['newStake'])/1_000_000):,.0f} CCD."
                        result.request_target = True

                    elif event["tag"] == "BakerStakeDecreased":
                        result.message += f"Baker stake decreased {result.unstaked_amount:,.0f} CCD{result.perc} to {(int(event['newStake'])/1_000_000):,.0f} CCD."
                        result.request_target = False
                        result.unstaked = True

                    elif event["tag"] == "DelegationRemoved":
                        result.message += f"Delegation removed."
                        result.request_target = True

        return result

    def define_type_and_contents_from_graphQL(self, t):
        _type = t["transactionType"]["__typename"]  # AccountTransaction

        if _type == "AccountTransaction":
            try:
                _contents = t["transactionType"]["accountTransactionType"]
            except:
                _contents = "UNKNOWN"
        elif _type == "CredentialDeploymentTransaction":
            try:
                _contents = t["transactionType"]["credentialDeploymentTransactionType"]
            except:
                _contents = "UNKNOWN"
        elif _type == "UpdateTransaction":
            try:
                _contents = t["transactionType"]["updateTransactionType"]
            except:
                _contents = "UNKNOWN"
        else:
            _contents = "UNKNOWN"

        # now translate to node language
        # console.log(f"{_type=}, {_contents=}")
        self.type = TransactionTypeFromQLToNode[_type].value
        if t["result"]["__typename"] == "Success":
            self.contents = TransactionContentsFromQLToNode[_contents].value
        else:
            self.contents = None

    def translate_result_from_graphQL(self, t):
        if t["result"]["__typename"] == "Success":
            _outcome = "success"
        elif t["result"]["__typename"] == "Rejected":
            _outcome = "reject"
            _rejectReason = t["result"]["reason"]["__typename"]

        _events = []
        if "events" in t["result"]:
            for event in t["result"]["events"]["nodes"]:
                e = Event(event).translate_event_from_graphQL()
                _events.append(e)

        if _outcome == "success":
            return {"events": _events, "outcome": _outcome}
        else:
            return {
                "events": _events,
                "outcome": _outcome,
                "rejectReason": _rejectReason,
            }

    def init_from_graphQL(self, t):
        # try:
        #     t['block']['blockSlotTime'] = dateutil.parser.parse(t['block']['blockSlotTime'])
        # except:
        #     pass
        self.block = t["block"]
        self.cost = t["ccdCost"]
        self.energyCost = t["energyCost"]
        self.hash = t["transactionHash"]
        self.index = t["transactionIndex"]
        self.sender = (
            t["senderAccountAddress"]["asString"]
            if t["senderAccountAddress"] is not None
            else None
        )
        self.define_type_and_contents_from_graphQL(t)
        self.result = self.translate_result_from_graphQL(t)
        self.set_possible_cns_domain()
        self.node = None
        return self
