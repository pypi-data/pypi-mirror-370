import requests
from rich.console import Console
console = Console()


class Mixin:
    def ql_get_rewards_for_account(self, ql_account_id):
        query = "query {"
        query += f'rewardMetricsForAccount (period:LAST30_DAYS, accountId: "{ql_account_id}")'
        query += """
                    {
                    buckets {
                        y_SumRewards
                        x_Time
                        bucketWidth
                    }
                    sumRewardAmount
                    }
                }
        """
        try:
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                return r.json()['data']['rewardMetricsForAccount']
            else:
                console.log(r.text)
        except Exception as e:
            console.log(query, e)
            return None

    def ql_request_account_rewards(self, ql_id: str):
        query = "query {"
        # query += f'LAST_HOUR:    rewardMetricsForAccount(accountId: "{ql_id}" period: LAST_HOUR) {{ sumRewardAmount }}'
        query += f'LAST24_HOURS: rewardMetricsForAccount(accountId: "{ql_id}" period: LAST24_HOURS) {{ sumRewardAmount }}'
        query += f'LAST7_DAYS:   rewardMetricsForAccount(accountId: "{ql_id}" period: LAST7_DAYS) {{ sumRewardAmount }}'
        query += f'LAST30_DAYS:  rewardMetricsForAccount(accountId: "{ql_id}" period: LAST30_DAYS) {{ sumRewardAmount }}'
        # query += f'LAST_YEAR:    rewardMetricsForAccount(accountId: "{ql_id}" period: LAST_YEAR) {{ sumRewardAmount }}'
        
        query += '}' # query
        try:
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                account_rewards = {
                    # 'LAST_HOUR':    r.json()['data']['LAST_HOUR'],
                    'LAST24_HOURS': r.json()['data']['LAST24_HOURS'],
                    'LAST7_DAYS':   r.json()['data']['LAST7_DAYS'],
                    'LAST30_DAYS':  r.json()['data']['LAST30_DAYS'],
                    # 'LAST_YEAR':    r.json()['data']['LAST_YEAR'],

                 }
                return account_rewards
            else:
                return None
       
        except Exception as e:
            console.log(query, e)
            return None

            