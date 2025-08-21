import requests
from rich.console import Console
from ccdexplorer_fundamentals.enums import NET

console = Console()


class Mixin:
    def ql_request_tx_from_hash(self, txHash: str, net=NET.MAINNET):
        query = "query {"
        query += f'transactionByTransactionHash(transactionHash: "{txHash}")'
        query += "{"

        query += self.standard_tx_fields()
        query += self.ql_query_tx_events()

        query += "}"
        try:
            url_to_use = (
                self.graphql_url if net == NET.MAINNET else self.graphql_url_testnet
            )

            r = requests.post(url_to_use, json={"query": query})
            if r.status_code == 200:
                return r.json()["data"]["transactionByTransactionHash"]

        except Exception as e:
            console.log(query, e)
            return None
