import requests
from rich.console import Console
console = Console()


class Mixin:
    def ql_get_active_bakers(self):
        done = False
        after = 'null'
        self.active_bakers_by_baker_id   = {}
        self.active_bakers_by_account_id = {}

        while not done:
            this_batch, pageInfo = self.ql_get_active_bakers_b_f(before='null', after=after)
            done = pageInfo.get('hasNextPage', False) == False
            if not done:
                after = pageInfo['endCursor']
            active_batch = [x for x in this_batch if x['state']['__typename'] == 'ActiveBakerState']
            
            for x in active_batch:
                baker_id = x['bakerId']
                account = x['account']['address']['asString']
                self.active_bakers_by_baker_id[baker_id]    = account
                self.active_bakers_by_account_id[account]   = baker_id
        
    def ql_get_active_bakers_b_f(self, before: str = None, after: str = None):
        query = "query {"

        if before == 'first':
            accounts_str  =  f'bakers (first: {self.nodes_request_limit}) '
        
        elif before != 'null':
            accounts_str  =  f'bakers (last: {self.nodes_request_limit}, before: "{before}") '
        elif 'last' in after:
            accounts_str  =  f'bakers ({after}) ' 
        
        elif after != 'null':
            accounts_str  =  f'bakers (first: {self.nodes_request_limit}, after: "{after}") ' 
        else:
            accounts_str = f'bakers (first: {self.nodes_request_limit})'
        query += accounts_str + '{'
        query += self.pageInfo()
        query += """
                        nodes {
                        state {
                            __typename
                        }
                        bakerId
                        account {
                            address {
                                asString
                            }
                        }
                        }
                    }
                }
        """
        try:
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                return r.json()['data']['bakers']['nodes'], r.json()['data']['bakers']['pageInfo']
                
        except Exception as e:
            console.log(query, e)
            return None

    def ql_get_pools(self):
        done = False
        after = 'null'
        pools = []
       
        while not done:
            this_batch, pageInfo = self.ql_get_pools_b_f(before='null', after=after)
            done = pageInfo.get('hasNextPage', False) == False
            if not done:
                after = pageInfo['endCursor']
            pools.extend(this_batch)
            
        return pools

    def ql_get_pools_b_f(self, before: str = None, after: str = None):
        # LIMIT = self.nodes_request_limit
        LIMIT = 50
        query = "query {"
        
        if before == 'first':
            accounts_str  =  f'bakers (first: {LIMIT}) '
        
        elif before != 'null':
            accounts_str  =  f'bakers (last: {LIMIT}, before: "{before}") '
        elif 'last' in after:
            accounts_str  =  f'bakers ({after}) ' 
        
        elif after != 'null':
            accounts_str  =  f'bakers (first: {LIMIT}, after: "{after}") ' 
        else:
            accounts_str = f'bakers (first: {LIMIT})'
        query += accounts_str + '{'
        query += self.pageInfo()
        query += """
                        nodes {
                            id
                            bakerId
                            state {
                                ... on ActiveBakerState {
                                stakedAmount
                                pool {
                                    apy_30: apy(period: LAST30_DAYS) {
                                        bakerApy
                                        delegatorsApy
                                        totalApy
                                    }
                                    apy_7: apy(period: LAST7_DAYS) {
                                        bakerApy
                                        delegatorsApy
                                        totalApy
                                    }
                                    openStatus
                                    metadataUrl
                                    delegatorCount
                                    delegatedStake
                                    delegatedStakeCap
                                    rankingByTotalStake {
                                        rank
                                        total
                                    }
                                    totalStake
                                    totalStakePercentage
                                    commissionRates {
                                        finalizationCommission
                                        transactionCommission
                                        bakingCommission
                                    }
                                }
                                }
                            }
                            
                        }
                    } } 
        """
        try:
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                    return r.json()['data']['bakers']['nodes'], r.json()['data']['bakers']['pageInfo']

        except Exception as e:
            console.log(query, e)
            return None