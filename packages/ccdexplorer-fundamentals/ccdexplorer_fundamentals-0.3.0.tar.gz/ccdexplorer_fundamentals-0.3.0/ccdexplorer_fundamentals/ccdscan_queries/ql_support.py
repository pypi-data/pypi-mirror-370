import requests
from rich.console import Console
from ..tooter import Tooter, TooterType, TooterChannel

import time

console = Console()

# from app.classes.Enums import TransactionTypeQL
from ccdexplorer_fundamentals.transaction import TransactionType


class Mixin:
    def emergency_send(self, message):
        self.tooter.relay(
            channel=TooterChannel.NOTIFIER,
            title="CCDScan down?",
            body=f"{message}",
            notifier_type=TooterType.REQUESTS_ERROR,
        )

    def reset_timer(self):
        self.timer = {"queries": 0, "elapsed_time": 0}

    def timed_request(self, query):

        start_counter_ns = time.perf_counter_ns()
        r = requests.post(self.graphql_url, json={"query": query})
        end_counter_ns = time.perf_counter_ns()

        elapsed = end_counter_ns - start_counter_ns
        self.timer.update(
            {
                "queries": self.timer["queries"] + 1,
                "elapsed_time": self.timer["elapsed_time"] + elapsed,
            }
        )

        return r

    def this_a_tx(self, value):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15"
        }
        a = requests.get(
            f"https://dashboard.mainnet.concordium.software/v1/transactionStatus/{value}",
            headers=headers,
            verify=False,
        )
        return a.json() is not None

    def pageInfo(self):
        query = """
            pageInfo {
                hasPreviousPage
                startCursor
                endCursor
                hasNextPage
            }
                """
        return query

    def standard_tx_fields(self):
        query = """
        
            block {
                blockHash
                blockHeight
                blockSlotTime
                finalized
            }
            transactionType {
                __typename
                ...on AccountTransaction{
                    accountTransactionType
                }
                ... on CredentialDeploymentTransaction{
                    credentialDeploymentTransactionType
                }
                ... on UpdateTransaction {
                    updateTransactionType
                }
            }
            id
            transactionHash
            transactionIndex
            senderAccountAddress {
                asString
            }
            ccdCost
            energyCost
            transactionHash
        """
        return query

    def ql_query_tx_events(self):
        # event
        query = """
        result {
            ... on Rejected {
                __typename
                reason {
                __typename
                }
            }
            ... on Success {
                __typename
                events (first: 50) {
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
                """

        return query
