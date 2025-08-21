import requests
from rich.console import Console
console = Console()


class Mixin:
    def ql_request_pool_rewards(self, ql_id: str):
        query = "query {"
        # query += f'LAST_HOUR:    poolRewardMetricsForBakerPool(bakerId: "{ql_id}" period: LAST_HOUR) {{ sumDelegatorsRewardAmount sumBakerRewardAmount sumTotalRewardAmount }}'
        query += f'LAST24_HOURS: poolRewardMetricsForBakerPool(bakerId: "{ql_id}" period: LAST24_HOURS) {{ sumDelegatorsRewardAmount sumBakerRewardAmount sumTotalRewardAmount }}'
        query += f'LAST7_DAYS:   poolRewardMetricsForBakerPool(bakerId: "{ql_id}" period: LAST7_DAYS) {{ sumDelegatorsRewardAmount sumBakerRewardAmount sumTotalRewardAmount }}'
        query += f'LAST30_DAYS:  poolRewardMetricsForBakerPool(bakerId: "{ql_id}" period: LAST30_DAYS) {{ sumDelegatorsRewardAmount sumBakerRewardAmount sumTotalRewardAmount }}'
        # query += f'LAST_YEAR:    poolRewardMetricsForBakerPool(bakerId: "{ql_id}" period: LAST_YEAR) {{ sumDelegatorsRewardAmount sumBakerRewardAmount sumTotalRewardAmount }}'
        
        query += '}' # query
        try:
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                pool_rewards = {
                    # 'LAST_HOUR':    r.json()['data']['LAST_HOUR'],
                    'LAST24_HOURS': r.json()['data']['LAST24_HOURS'],
                    'LAST7_DAYS':   r.json()['data']['LAST7_DAYS'],
                    'LAST30_DAYS':  r.json()['data']['LAST30_DAYS'],
                    # 'LAST_YEAR':    r.json()['data']['LAST_YEAR'],

                 }
                return pool_rewards
            else:
                return None
       
        except Exception as e:
            console.log(query, e)
            return None

            