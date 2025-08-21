import requests
from rich.console import Console
console = Console()


class Mixin:
    def get_first_last_block(self):
        query = (
            'query {'
            'blocks(first: 1)'
            '{'
            '    nodes {'
            '    transactionCount'
            '    blockHeight'
            '    blockHash'
            '    balanceStatistics {'
            '    totalAmount'
                '   totalAmountLockedInReleaseSchedules'
            '} }'
            '} }'
        )
        r = requests.post(self.graphql_url, json={'query': query})
        if r.status_code == 200:
            result = r.json()['data']['blocks']['nodes'][0]
            # console.log(result)
            dct = {
                'transactionCount': int(result['transactionCount']), 
                "blockHash": result['blockHash'],
                "blockHeight": int(result['blockHeight']), 
                "totalAmount":result['balanceStatistics']['totalAmount'],
                "totalAmountReleased":result['balanceStatistics']['totalAmountLockedInReleaseSchedules']}
        return dct