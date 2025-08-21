import requests
from rich.console import Console
console = Console()


class Mixin:
    def ql_get_blockhash(self, block_height):
        query = "query {"
        query += f'search (query: "{block_height}")'
        query += """
                  {
                    blocks (last: 1) {
                    nodes {
                        blockHeight
                        blockHash
                    }
                    }
                }
                
                }
        """
        try:
            r = requests.post(self.graphql_url, json={'query': query})
            if r.status_code == 200:
                if len (r.json()['data']['search']['blocks']['nodes']) > 0:
                    return r.json()['data']['search']['blocks']['nodes'][0]['blockHash']
                else:
                    return None
            else:
                console.log(r.text)
        except Exception as e:
            console.log(query, e)
            return None