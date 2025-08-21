from rich.console import Console
from functools import lru_cache
import datetime as dt
from datetime import timedelta
import functools
console = Console()

import time

def cache(seconds: int, maxsize: int = 128, typed: bool = False):
    def wrapper_cache(func):
        func = functools.lru_cache(maxsize=maxsize, typed=typed)(func)
        func.delta = timedelta(seconds=seconds)
        func.expiration = dt.datetime.utcnow() + func.delta

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            if dt.datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = dt.datetime.utcnow() + func.delta

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache
class Mixin:
    # @cache(seconds=2)
    def ql_get_all_transactions_for_exchange_graphs_for_account(self, before_cursor, account_id):
        done = False
        after = None
        txs = []
        total_retrieved = 0
        while not done:
            this_batch, pageInfo = self.ql_request_transactions_for_lookup_using_edges(account_id, before_cursor=before_cursor, after=after)
            total_retrieved += len(this_batch)
            console.log(f"Retrieved {len(this_batch):,.0f} trades in this batch, totaling {total_retrieved:,.0f}.")
            if before_cursor:
                done = pageInfo.get('hasPreviousPage', False) == False
                if not done:
                    before_cursor = pageInfo['startCursor']
            else:
                    
                done = pageInfo.get('hasNextPage', False) == False
                if not done:
                    after = pageInfo['endCursor']
            txs.extend(this_batch)
            time.sleep(0.01)

        if len(txs) > 0:
            cursor_to_return = pageInfo['startCursor'] if before_cursor else txs[0]['before_cursor']
        else:
            cursor_to_return = before_cursor
        return txs, cursor_to_return

    def ql_get_all_transactions_for_explorer_ccd(self, before_cursor, account_id):
        done = False
        after = None
        cursor_to_return = None
        txs = []
        total_retrieved = 0
        now = dt.datetime.utcnow()
        if (now - self.explorer_ccd_request_timestamp).seconds > 5:
            while not done:
                this_batch, pageInfo = self.ql_request_transactions_for_lookup_using_edges(account_id, before_cursor=before_cursor, after=after)
                total_retrieved += len(this_batch)
                console.log(f"Retrieved {len(this_batch):,.0f} trades in this batch, totaling {total_retrieved:,.0f}.")
                if before_cursor:
                    done = pageInfo.get('hasPreviousPage', False) == False
                    if not done:
                        before_cursor = pageInfo['startCursor']
                else:
                        
                    done = pageInfo.get('hasNextPage', False) == False
                    if not done:
                        after = pageInfo['endCursor']
                txs.extend(this_batch)
                time.sleep(0.01)

            if len(txs) > 0:
                cursor_to_return = pageInfo['startCursor'] if before_cursor else txs[0]['before_cursor']
            else:
                cursor_to_return = before_cursor
            self.explorer_ccd_transactions = txs
            self.explorer_ccd_request_timestamp = now
        else:
            # console.log("Getting explorer.ccd txs from cache.")
            txs = self.explorer_ccd_transactions
        return txs, cursor_to_return

    def ql_get_all_delegators_for_explorer_ccd(self, before_cursor, account_id):
        done = False
        after = None
        cursor_to_return = None
        delegators = []
        total_retrieved = 0
        now = dt.datetime.utcnow()
        if (now - self.explorer_ccd_request_timestamp_delegators).seconds > 5:
            while not done:
                this_batch, pageInfo = self.ql_request_delegators_for_lookup_using_edges(account_id, before_cursor=before_cursor, after=after)
                total_retrieved += len(this_batch)
                console.log(f"Retrieved {len(this_batch):,.0f} delegators in this batch, totaling {total_retrieved:,.0f}.")
                if before_cursor:
                    done = pageInfo.get('hasPreviousPage', False) == False
                    if not done:
                        before_cursor = pageInfo['startCursor']
                else:
                        
                    done = pageInfo.get('hasNextPage', False) == False
                    if not done:
                        after = pageInfo['endCursor']
                delegators.extend(this_batch)
                time.sleep(0.01)

            if len(delegators) > 0:
                cursor_to_return = pageInfo['startCursor'] if before_cursor else delegators[0]['before_cursor']
            else:
                cursor_to_return = before_cursor
            self.explorer_ccd_delegators = delegators
            self.explorer_ccd_request_timestamp_delegators = now
        else:
            # console.log("Getting explorer.ccd txs from cache.")
            delegators = self.explorer_ccd_delegators
        return delegators, cursor_to_return