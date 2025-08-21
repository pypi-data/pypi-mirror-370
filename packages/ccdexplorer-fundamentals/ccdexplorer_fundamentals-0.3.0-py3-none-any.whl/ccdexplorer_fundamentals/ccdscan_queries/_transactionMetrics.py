import requests
from rich.console import Console
console = Console()

from enum import Enum

class TimePeriod(Enum):
    LAST_HOUR='LAST_HOUR'
    LAST24_HOURS='LAST24_HOURS'
    LAST7_DAYS='LAST7_DAYS'
    LAST_30_DAYS='LAST30_DAYS'
    LAST_YEAR='LAST_YEAR'
class Mixin:
    def ql_state(self, timePeriod: TimePeriod):
        query = "query {"
        query += f"transactionMetrics(period: {timePeriod.value})"
        query += """
                 {
                lastCumulativeTransactionCount
                transactionCount
                }
                }
        
        """
        try:
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                return r.json()['data']['transactionMetrics']['transactionCount'], r.json()['data']['transactionMetrics']['lastCumulativeTransactionCount']
       
        except Exception as e:
            console.log(query, e)
            return None