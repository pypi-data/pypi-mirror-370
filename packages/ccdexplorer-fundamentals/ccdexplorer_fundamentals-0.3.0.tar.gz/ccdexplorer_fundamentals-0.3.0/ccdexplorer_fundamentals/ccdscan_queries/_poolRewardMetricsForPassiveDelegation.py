import requests
from rich.console import Console
console = Console()


class Mixin:
    def ql_request_passive_rewards(self):
        query = "query {"
        # query += f'LAST_HOUR:    poolRewardMetricsForPassiveDelegation(period: LAST_HOUR) {{ sumDelegatorsRewardAmount sumBakerRewardAmount sumTotalRewardAmount }}'
        query += f'LAST24_HOURS: poolRewardMetricsForPassiveDelegation(period: LAST24_HOURS) {{ sumDelegatorsRewardAmount sumBakerRewardAmount sumTotalRewardAmount }}'
        query += f'LAST7_DAYS:   poolRewardMetricsForPassiveDelegation(period: LAST7_DAYS) {{ sumDelegatorsRewardAmount sumBakerRewardAmount sumTotalRewardAmount }}'
        query += f'LAST30_DAYS:  poolRewardMetricsForPassiveDelegation(period: LAST30_DAYS) {{ sumDelegatorsRewardAmount sumBakerRewardAmount sumTotalRewardAmount }}'
        # query += f'LAST_YEAR:    poolRewardMetricsForBakerPool(bakerId: "{ql_id}" period: LAST_YEAR) {{ sumDelegatorsRewardAmount sumBakerRewardAmount sumTotalRewardAmount }}'
        
        query += '}' # query
        try:
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                passive_rewards = {
                    # 'LAST_HOUR':    r.json()['data']['LAST_HOUR'],
                    'LAST24_HOURS': r.json()['data']['LAST24_HOURS'],
                    'LAST7_DAYS':   r.json()['data']['LAST7_DAYS'],
                    'LAST30_DAYS':  r.json()['data']['LAST30_DAYS'],
                    # 'LAST_YEAR':    r.json()['data']['LAST_YEAR'],

                 }
                return passive_rewards
            else:
                return None
       
        except Exception as e:
            console.log(query, e)
            return None
            