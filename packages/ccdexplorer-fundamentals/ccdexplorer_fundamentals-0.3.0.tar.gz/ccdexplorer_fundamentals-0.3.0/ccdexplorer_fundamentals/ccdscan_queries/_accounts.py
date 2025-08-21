import requests
from rich.console import Console
from enum import Enum
console = Console()

class AccountSort(Enum):
    AGE_ASC                 ='AGE_ASC'
    AGE_DESC                ='AGE_DESC'
    AMOUNT_ASC              ='AMOUNT_ASC'
    AMOUNT_DESC             ='AMOUNT_DESC'
    DELEGATED_STAKE_ASC     ='DELEGATED_STAKE_ASC'
    DELEGATED_STAKE_DESC    ='DELEGATED_STAKE_DESC'
    TRANSACTION_COUNT_ASC   ='TRANSACTION_COUNT_ASC'
    TRANSACTION_COUNT_DESC  ='TRANSACTION_COUNT_DESC'

class Mixin:
    def ql_get_account_metrics(self):
        query = """
                query {
                    accountsMetrics (period: LAST24_HOURS){
                        accountsCreated
                        lastCumulativeAccountsCreated
                    }
                }
        """
        try:
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                return r.json()['data']['accountsMetrics']
                
            else:
                console.log (r.text)
        except Exception as e:
            console.log(query, e)
            return None
    def ql_accounts_response(self, sort: AccountSort):
        query = "query {"
        query += f"accounts(first:10, sort: {sort.value})"
        query += """
                    {
                        nodes {
                            createdAt
                            transactionCount
                            amount
                            address {
                                asString
                            }
                        }
                    }
                }
        """
        try:
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                return r.json()['data']['accounts']['nodes']
       
        except Exception as e:
            console.log(query, e)
            return None

    # def ql_passive_delegation_delegators(self, before: str = None, after: str = None):
        
    #     if before != 'null':
    #         accounts_str  =  f'accounts (last: {self.nodes_request_limit}, before: "{before}") '
    #     elif after != 'null':
    #         accounts_str  =  f'accounts (first: {self.nodes_request_limit}, after: "{after}") ' 
    #     else:
    #         accounts_str = 'accounts'
        
    #     query = ' query { ' 
    #     query += accounts_str
        
    #     query += """
    #             {
    #             nodes {
    #                     amount
    #                     address {
    #                         asString
    #                     }
    #                 }
    #             """
    #     query += self.pageInfo(self)
    #     query += """
    #             }
    #         }

        
    #     """
    #     console.log(query)

    #     try:
    #         r = requests.post(self.graphql_url, json={'query': query})
    #         if r.status_code == 200:
    #             return r.json()['data']['accounts']['nodes'], r.json()['data']['accounts']['pageInfo']
       
    #     except Exception as e:
    #         console.log(query, e)