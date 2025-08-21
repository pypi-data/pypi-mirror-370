import requests
from rich.console import Console
console = Console()


class Mixin:
    def ql_request_delegators_for_lookup(self, baker_id: int, before: str = None, after: str = None):
            
            query = "query {"
            query += f'bakerByBakerId (bakerId: {baker_id}) '
            
            query += '{ state { ... on ActiveBakerState { pool { delegatorCount '
            
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
            query += ' } } } } } }'

            try:
                r = requests.post(self.graphql_url, json={'query': query})
                if r.status_code == 200:
                    if r.json()['data']['bakerByBakerId']['state'] != {}:
                        return r.json()['data']['bakerByBakerId']['state']['pool']['delegators']['nodes'], \
                            r.json()['data']['bakerByBakerId']['state']['pool']['delegators']['pageInfo'], \
                            r.json()['data']['bakerByBakerId']['state']['pool']['delegatorCount'],                           
                    else:
                        return [], [], 0
                else:
                    console.log(r.text)
        
            except Exception as e:
                console.log(query, e)
                return None

    def ql_get_baker_pool_info(self, baker_id:int):
        
        query = "query {"
        query += f'bakerByBakerId (bakerId: {baker_id}) '
        query += """
             { state {
            ... on ActiveBakerState {
                pool {
                    apy_30: apy (period:LAST30_DAYS) {
                        bakerApy
                        delegatorsApy
                        totalApy
                    }
                    apy_7: apy (period:LAST7_DAYS) {
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
        }
        
        """
        try:
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                if r.json()['data']['bakerByBakerId']['state'] != {}:
                    return r.json()['data']['bakerByBakerId']['state']['pool']                    
                else:
                    return {}
            else:
                console.log(r.text)
        
        except Exception as e:
            console.log(query, e)
            return None

    def ql_get_info_by_bakerId(self, value):
        query = "query {"
        query += f'bakerByBakerId (bakerId: {value})'
        query += """
                    {
                        id
                        state {
                            ... on ActiveBakerState {
                                nodeStatus {
                                    nodeName
                                }
                                pool {
                                    __typename
                                }
                            }
                        }
                        account {
                            address {
                                asString
                            }
                        }
                    }
                }
        """
        try:
            # r = self.timed_request(query)
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                return r.json()['data']['bakerByBakerId']
            else:
                return None
        except Exception as e:
            console.log(query, e)
            return None