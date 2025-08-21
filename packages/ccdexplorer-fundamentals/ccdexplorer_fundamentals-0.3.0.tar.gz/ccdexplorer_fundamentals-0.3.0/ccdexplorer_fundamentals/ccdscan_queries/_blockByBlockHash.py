import requests
from rich.console import Console
from ccdexplorer_fundamentals.enums import NET

console = Console()

# from app.classes.Enums import TransactionTypeQL
from ccdexplorer_fundamentals.transaction import TransactionType
from ccdexplorer_fundamentals.enums import NET


class Mixin:
    # Finalizers
    def ql_get_finalizers(self, block_hash, net=NET.MAINNET):
        done = False
        after = "null"
        finalizers = []
        if len(block_hash) == 64:
            while not done:
                this_batch, pageInfo = self.ql_get_finalizers_b_f(
                    block_hash, before="null", after=after, net=net
                )
                done = pageInfo.get("hasNextPage", False) == False
                if not done:
                    after = pageInfo["endCursor"]
                finalizers.extend(this_batch)

        return finalizers

    def ql_get_finalizers_b_f(
        self, block_hash, before: str = None, after: str = None, net=NET.MAINNET
    ):
        query = "query {"
        query += f'blockByBlockHash(blockHash: "{block_hash}") {{ specialEvents {{ nodes {{ __typename ... on FinalizationRewardsSpecialEvent {{'

        if before == "first":
            accounts_str = f"finalizationRewards (first: {self.nodes_request_limit}) "

        elif before != "null":
            accounts_str = f'finalizationRewards (last: {self.nodes_request_limit}, before: "{before}") '
        elif "last" in after:
            accounts_str = f"finalizationRewards ({after}) "

        elif after != "null":
            accounts_str = f'finalizationRewards (first: {self.nodes_request_limit}, after: "{after}") '
        else:
            accounts_str = f"finalizationRewards (first: {self.nodes_request_limit})"
        query += accounts_str + "{"
        query += self.pageInfo()
        query += """
                        nodes {
                            accountAddress {
                                asString
                            }
                            amount
                        }
                    } } } } } }
        """
        try:
            url_to_use = (
                self.graphql_url if net == NET.MAINNET else self.graphql_url_testnet
            )
            r = requests.post(url_to_use, json={"query": query})
            if r.status_code == 200:
                finalizers_not_seen = True
                for n in r.json()["data"]["blockByBlockHash"]["specialEvents"]["nodes"]:
                    if n["__typename"] == "FinalizationRewardsSpecialEvent":
                        finalizers_not_seen = False
                        return (
                            n["finalizationRewards"]["nodes"],
                            n["finalizationRewards"]["pageInfo"],
                        )

                if finalizers_not_seen:
                    return [], {"hasNextPage": False, "endCursor": ""}
        except Exception as e:
            console.log(query, e)
            return [], {"hasNextPage": False, "endCursor": ""}

    def ql_request_blockInfo(self, blockHash: str, net=NET.MAINNET):
        query = "query {"
        query += f'blockByBlockHash(blockHash: "{blockHash}")'
        query += """
                    {
                        transactionCount
                        finalized
                        bakerId
                        blockSlotTime
                        blockHeight
                        blockHash
                    } } """
        try:
            url_to_use = (
                self.graphql_url if net == NET.MAINNET else self.graphql_url_testnet
            )
            r = requests.post(url_to_use, json={"query": query})
            if r.status_code == 200:
                return r.json()["data"]["blockByBlockHash"]

        except Exception as e:
            console.log(query, e)
            return None

    def ql_request_blockSummary_transactions(self, blockHash: str):
        query = "query {"
        query += f'blockByBlockHash(blockHash: "{blockHash}")'
        query += """
                    {
                        transactions (first:50){
                            nodes {
                                result {
                                ... on Success {
                                    events {
                                        nodes {
                                        __typename
                                    
        """
        for tr in TransactionType:
            query += tr.value

        query += """
                        }
                    }
                }
                }
                }
                }
            }# blockByBlockHash
        } # query
        """

        try:
            r = requests.post(self.graphql_url, json={"query": query})
            if r.status_code == 200:
                return r.json()["data"]["blockByBlockHash"]["transactions"]["nodes"]

        except Exception as e:
            console.log(query, e)
            return None

    def ql_request_blockSummary_payday(self, blockHash: str, net=NET.MAINNET):
        query = "query {"
        query += f'blockByBlockHash(blockHash: "{blockHash}")'
        query += """
                    {
                        specialEvents (first: 1, includeFilter: PAYDAY_POOL_REWARD) {
                            nodes {
                                __typename
                                }
                        }
                        } }            
        """

        try:
            url_to_use = (
                self.graphql_url if net == NET.MAINNET else self.graphql_url_testnet
            )
            r = requests.post(url_to_use, json={"query": query})
            if r.status_code == 200:
                if r.json()["data"]["blockByBlockHash"]:
                    return (
                        len(
                            r.json()["data"]["blockByBlockHash"]["specialEvents"][
                                "nodes"
                            ]
                        )
                        > 0
                    )
                else:
                    None

        except Exception as e:
            console.log(query, e)
            return None

    def ql_request_block_payday_account_rewards_for_lookup(
        self, lookup_value: str, before: str = None, after: str = None
    ):
        query = "query {"
        query += f'blockByBlockHash (blockHash: "{lookup_value}") {{ '

        if before == "first":
            accounts_str = f"specialEvents (includeFilter: PAYDAY_ACCOUNT_REWARD, first: {self.nodes_request_limit}) "

        elif before != "null":
            accounts_str = f'specialEvents (includeFilter: PAYDAY_ACCOUNT_REWARD, last: {self.nodes_request_limit}, before: "{before}") '
        elif "last" in after:
            accounts_str = (
                f"specialEvents (includeFilter: PAYDAY_ACCOUNT_REWARD, {after}) "
            )

        elif after != "null":
            accounts_str = f'specialEvents (includeFilter: PAYDAY_ACCOUNT_REWARD, first: {self.nodes_request_limit}, after: "{after}") '
        else:
            accounts_str = f"specialEvents (includeFilter: PAYDAY_ACCOUNT_REWARD, first: {self.nodes_request_limit})"
        query += accounts_str + "{"
        query += self.pageInfo()
        query += """
            nodes {
                __typename
                ... on PaydayAccountRewardSpecialEvent {
                transactionFees
                finalizationReward
                bakerReward
                account {
                    asString
                }
                }
            } } } }
        """

        try:
            r = requests.post(self.graphql_url, json={"query": query})
            if r.status_code == 200:
                return (
                    r.json()["data"]["blockByBlockHash"]["specialEvents"]["nodes"],
                    r.json()["data"]["blockByBlockHash"]["specialEvents"]["pageInfo"],
                )

            else:
                console.log(r.text)

        except Exception as e:
            console.log(query, e)
            return None

    def ql_request_block_payday_pool_rewards_for_lookup(
        self, lookup_value: str, before: str = None, after: str = None
    ):
        query = "query {"
        query += f'blockByBlockHash (blockHash: "{lookup_value}") {{ '

        if before == "first":
            accounts_str = f"specialEvents (includeFilter: PAYDAY_POOL_REWARD, first: {self.nodes_request_limit}) "

        elif before != "null":
            accounts_str = f'specialEvents (includeFilter: PAYDAY_POOL_REWARD, last: {self.nodes_request_limit}, before: "{before}") '
        elif "last" in after:
            accounts_str = (
                f"specialEvents (includeFilter: PAYDAY_POOL_REWARD, {after}) "
            )

        elif after != "null":
            accounts_str = f'specialEvents (includeFilter: PAYDAY_POOL_REWARD, first: {self.nodes_request_limit}, after: "{after}") '
        else:
            accounts_str = f"specialEvents (includeFilter: PAYDAY_POOL_REWARD, first: {self.nodes_request_limit})"
        query += accounts_str + "{"
        query += self.pageInfo()
        query += """
            nodes {
                ... on PaydayPoolRewardSpecialEvent {
                    pool {
                        
                        __typename
                        ... on BakerPoolRewardTarget {
                        bakerId
                        }
                    }
                    id
                    transactionFees
                    finalizationReward
                    bakerReward
                    }
            } } } }
        """

        try:
            r = requests.post(self.graphql_url, json={"query": query})
            if r.status_code == 200:
                return (
                    r.json()["data"]["blockByBlockHash"]["specialEvents"]["nodes"],
                    r.json()["data"]["blockByBlockHash"]["specialEvents"]["pageInfo"],
                )

            else:
                console.log(r.text)

        except Exception as e:
            console.log(query, e)
            return None

    def ql_request_blockSummary(self, blockHash: str, net=NET.MAINNET):
        query = "query {"
        query += f'blockByBlockHash(blockHash: "{blockHash}")'
        query += """
                    {
                        
                        specialEvents {
                        nodes {
                            __typename
                            ... on MintSpecialEvent {
                                bakingReward
                                finalizationReward
                                platformDevelopmentCharge
                            }
                            ... on BlockAccrueRewardSpecialEvent {
                                passiveReward
                                transactionFees
                            }
                            ... on BlockRewardsSpecialEvent {
                                transactionFees
                                }
                                ... on BakingRewardsSpecialEvent {
                                bakingRewards {
                                    nodes {
                                    amount
                                    accountAddress {
                                        asString
                                    }
                                    }
                                }
                            }
                            ... on PaydayFoundationRewardSpecialEvent {
                                id
                                foundationAccount {
                                    asString
                                }
                                developmentCharge
                                }
                                ... on PaydayPoolRewardSpecialEvent {
                                pool {
                                    __typename
                                    ... on BakerPoolRewardTarget {
                                    bakerId
                                    }
                                }
                                id
                                transactionFees
                                finalizationReward
                                bakerReward
                                }
                                ... on PaydayAccountRewardSpecialEvent {
                                    transactionFees
                                    finalizationReward
                                    bakerReward
                                    account {
                                        asString
                                    }
                            }
                            ... on FinalizationRewardsSpecialEvent {
                            finalizationRewards {
                                nodes {
                                accountAddress {
                                    asString
                                }
                                amount
                                }
                            }
                            }
                            ... on MintSpecialEvent {
                            platformDevelopmentCharge
                            finalizationReward
                            bakingReward
                            }
                        }
                        }
                        chainParameters {
                        ... on ChainParametersV0 {
                            __typename
                            minimumThresholdForBaking
                            microCcdPerEuro {
                            denominator
                            numerator
                            }
                            euroPerEnergy {
                            denominator
                            numerator
                            }
                            electionDifficulty
                            rewardParameters {
                            mintDistribution {
                                finalizationReward
                                bakingReward
                            }
                            }
                        }
                        ... on ChainParametersV1 {
                            __typename
                            accountCreationLimit
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
                            foundationAccountAddress {
                                asString
                            }
                            leverageBound {
                                denominator
                                numerator
                            }
                            minimumEquityCapital
                            mintPerPayday
                            passiveBakingCommission
                            passiveFinalizationCommission
                            passiveTransactionCommission
                            poolOwnerCooldown
                            capitalBound
                            delegatorCooldown
                            microCcdPerEuro {
                                denominator
                                numerator
                            }
                            euroPerEnergy {
                                denominator
                                numerator
                            }
                            electionDifficulty
                            rewardPeriodLength
                            rewardParameters {
                                mintDistribution {
                                    finalizationReward
                                    bakingReward
                                }
                            }
                        }

                        }
                    }
                    }

        """
        try:
            url_to_use = (
                self.graphql_url if net == NET.MAINNET else self.graphql_url_testnet
            )
            r = requests.post(url_to_use, json={"query": query})
            if r.status_code == 200:
                return r.json()["data"]["blockByBlockHash"]

        except Exception as e:
            console.log(query, e)
            return None

    def ql_request_block_for_release(self, blockHash: str, net=NET.MAINNET):
        query = (
            "query {\n"
            f'blockByBlockHash(blockHash:"{blockHash}") \u007b \n'
            "blockHeight\n"
            "blockHash\n"
            "balanceStatistics {\n"
            "totalAmount\n"
            "totalAmountReleased\n"
            "}\n"
            "}\n"
            "}\n"
        )
        try:
            url_to_use = (
                self.graphql_url if net == NET.MAINNET else self.graphql_url_testnet
            )
            r = requests.post(url_to_use, json={"query": query})
            if r.status_code == 200:
                return r.json()["data"]["blockByBlockHash"]

        except Exception as e:
            console.log(query, e)
            return None


def query_for_block(block_hash):
    query = (
        "query {\n"
        f'blockByBlockHash(blockHash:"{block_hash}") \u007b \n'
        "blockHeight\n"
        "blockHash\n"
        "balanceStatistics {\n"
        "totalAmount\n"
        "totalAmountReleased\n"
        "}\n"
        "}\n"
        "}\n"
    )
    return query
    # # Finalizers
    # def ql_get_finalizers(self, block_hash):
    #     done = False
    #     after = 'null'
    #     finalizers = []
    #     if len(block_hash) == 64:
    #         while not done:
    #             this_batch, pageInfo = self.ql_get_finalizers_b_f(block_hash, before='null', after=after)
    #             done = pageInfo.get('hasNextPage', False) == False
    #             if not done:
    #                 after = pageInfo['endCursor']
    #             finalizers.extend(this_batch)

    #     return finalizers

    # def ql_get_finalizers_b_f(self, block_hash, before: str = None, after: str = None):
    #     query = "query {"
    #     query += f'blockByBlockHash(blockHash: "{block_hash}") {{ specialEvents {{ nodes {{ __typename ... on FinalizationRewardsSpecialEvent {{'

    #     if before == 'first':
    #         accounts_str  =  f'finalizationRewards (first: {self.nodes_request_limit}) '

    #     elif before != 'null':
    #         accounts_str  =  f'finalizationRewards (last: {self.nodes_request_limit}, before: "{before}") '
    #     elif 'last' in after:
    #         accounts_str  =  f'finalizationRewards ({after}) '

    #     elif after != 'null':
    #         accounts_str  =  f'finalizationRewards (first: {self.nodes_request_limit}, after: "{after}") '
    #     else:
    #         accounts_str = f'finalizationRewards (first: {self.nodes_request_limit})'
    #     query += accounts_str + '{'
    #     query += self.pageInfo()
    #     query += """
    #                     nodes {
    #                         accountAddress {
    #                             asString
    #                         }
    #                         amount
    #                     }
    #                 } } } } } }
    #     """
    #     try:
    #         r = requests.post(self.graphql_url, json={'query': query})
    #         if r.status_code == 200:
    #             finalizers_not_seen = True
    #             for n in r.json()['data']['blockByBlockHash']['specialEvents']['nodes']:
    #                 if n['__typename'] == 'FinalizationRewardsSpecialEvent':
    #                     finalizers_not_seen = False
    #                     return n['finalizationRewards']['nodes'], n['finalizationRewards']['pageInfo']

    #             if finalizers_not_seen:
    #                 return [], {'hasNextPage': False, 'endCursor': ''}
    #     except Exception as e:
    #         console.log(query, e)
    #         return [], {'hasNextPage': False, 'endCursor': ''}
