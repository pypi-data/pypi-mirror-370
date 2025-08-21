import requests
from rich.console import Console
console = Console()


class Mixin:
    def ql_request_passive_delegators_for_lookup(self, before: str = None, after: str = None):
        
        query = "query { passiveDelegation  { delegatorCount "
        
        if before == 'first':
            accounts_str  =  f'delegators (first: {self.nodes_request_limit}) '
        
        elif before != 'null':
            accounts_str  =  f'delegators (last: {self.nodes_request_limit}, before: "{before}") '
        elif 'last' in after:
            accounts_str  =  f'delegators ({after}) ' 
        
        elif after != 'null':
            accounts_str  =  f'delegators (first: {self.nodes_request_limit}, after: "{after}") ' 
        else:
            accounts_str = f'delegators (first: {self.nodes_request_limit})'
        query += accounts_str + '{'
        query += self.pageInfo()
        query += """
                    nodes {
                        stakedAmount
                        restakeEarnings
                        accountAddress {
                            asString
                        }
                    }
        """
        query += ' } } }'

        try:
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                return r.json()['data']['passiveDelegation']['delegators']['nodes'], \
                    r.json()['data']['passiveDelegation']['delegators']['pageInfo'], \
                    r.json()['data']['passiveDelegation']['delegatorCount'],                           
            else:
                console.log(r.text)
    
        except Exception as e:
            console.log(query, e)
            return [], [], 0

    def ql_get_passive_pool_info(self):
        query = "query { passiveDelegation {"
        query += """
                    apy_30: apy(period: LAST30_DAYS)
                    apy_7: apy(period: LAST7_DAYS)
                    delegatorCount
                    delegatedStake
                    delegatedStakePercentage
                    commissionRates {
                        finalizationCommission
                        transactionCommission
                        bakingCommission
                    }
                } } """
        try:
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                return r.json()['data']['passiveDelegation']                    
            else:
                console.log(r.text)
        
        except Exception as e:
            console.log(query, e)
            return None

    def ql_passive_delegation_main(self):
        query = """
                query {
        passiveDelegation {
            delegatedStakePercentage
            delegatedStake
            delegatorCount
            commissionRates {
            finalizationCommission
            bakingCommission
            transactionCommission
            }
        }
        }
        
        """
        try:
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                return r.json()['data']['passiveDelegation']
       
        except Exception as e:
            console.log(query, e)