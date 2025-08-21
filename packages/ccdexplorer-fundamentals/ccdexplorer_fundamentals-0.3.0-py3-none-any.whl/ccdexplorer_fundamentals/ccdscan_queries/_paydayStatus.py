import requests
from rich.console import Console
console = Console()
import sys

import datetime as dt

class Mixin:
    def ql_get_next_payday(self):
            query = """
                    query { paydayStatus { 
                    nextPaydayTime 
                    paydaySummaries (first: 1) {
                        nodes {
                            block {
                            blockSlotTime
                            blockHeight
                            blockHash
                            }
                        }
                        }
                    } }
            """
            try:
                r = requests.post(self.graphql_url, json={'query': query})
                if r.status_code == 200:
                    return r.json()['data']['paydayStatus']['nextPaydayTime'], \
                           r.json()['data']['paydayStatus']['paydaySummaries']['nodes'][0]['block']
                    
                else:
                    console.log(r.text)
            except Exception as e:
                console.log(query, e)
                return None

    def ql_request_paydays(self, before: str = None, after: str = None):
            row_count = (dt.datetime.now() - dt.datetime(2022,6,24,8,0,0)).days + 1
            query = "query {"
            query += f'paydayStatus {{ nextPaydayTime '
            
            if before == 'first':
                accounts_str  =  f'paydaySummaries (first: {self.nodes_request_limit}) '
            
            elif before != 'null':
                accounts_str  =  f'paydaySummaries (last: {self.nodes_request_limit}, before: "{before}") '
            elif 'last' in after:
                accounts_str  =  f'paydaySummaries ({after}) ' 
            
            elif after != 'null':
                accounts_str  =  f'paydaySummaries (first: {self.nodes_request_limit}, after: "{after}") ' 
            else:
                accounts_str = f'paydaySummaries (first: {self.nodes_request_limit})'
            query += accounts_str + '{'
            query += self.pageInfo()
            query += """
                        nodes {
                            block {
                                blockHeight
                                blockSlotTime
                                blockHash
                            }
                        }
            """
            query += ' } } }'

            try:
                r = requests.post(self.graphql_url, json={'query': query})
                if r.status_code == 200:
                    return  r.json()['data']['paydayStatus']['paydaySummaries']['nodes'], \
                            r.json()['data']['paydayStatus']['paydaySummaries']['pageInfo'],\
                            r.json()['data']['paydayStatus']['nextPaydayTime'],\
                            row_count
                        
                else:
                    console.log(r.text)
                    sys.exit(1)
            except Exception as e:
                console.log(query, e)
                sys.exit(1)
                return None

    def ql_get_all_paydays(self):
        done = False
        after = 'null'
        paydays = []
       
        while not done:
            this_batch, pageInfo = self.ql_request_paydays(before='null', after=after)
            done = pageInfo.get('hasNextPage', False) == False
            if not done:
                after = pageInfo['endCursor']
            paydays.extend(this_batch)
            
        return paydays

    # def ql_request_paydays(self, before: str = None, after: str = None):
    #     row_count = (dt.datetime.now() - dt.datetime(2022,6,24,8,0,0)).days + 1
    #     query = "query {"
    #     query += f'paydayStatus {{ nextPaydayTime '
        
    #     if before == 'first':
    #         accounts_str  =  f'paydaySummaries (first: {self.nodes_request_limit}) '
        
    #     elif before != 'null':
    #         accounts_str  =  f'paydaySummaries (last: {self.nodes_request_limit}, before: "{before}") '
    #     elif 'last' in after:
    #         accounts_str  =  f'paydaySummaries ({after}) ' 
        
    #     elif after != 'null':
    #         accounts_str  =  f'paydaySummaries (first: {self.nodes_request_limit}, after: "{after}") ' 
    #     else:
    #         accounts_str = f'paydaySummaries (first: {self.nodes_request_limit})'
    #     query += accounts_str + '{'
    #     query += self.pageInfo()
    #     query += """
    #                 nodes {
    #                     block {
    #                         blockHeight
    #                         blockSlotTime
    #                         blockHash
    #                     }
    #                 }
    #     """
    #     query += ' } } }'

    #     try:
    #         r = requests.post(self.graphql_url, json={'query': query})
    #         if r.status_code == 200:
    #             return  r.json()['data']['paydayStatus']['paydaySummaries']['nodes'], \
    #                     r.json()['data']['paydayStatus']['paydaySummaries']['pageInfo']
                        
                    
    #         else:
    #             print (r.text)

    #     except Exception as e:
    #         print (query, e)
    #         return None