from .ccdscan_queries._accountByAddress                      import Mixin as _accountByAddress
from .ccdscan_queries._accounts                              import Mixin as _accounts
from .ccdscan_queries._bakerByBakerId                        import Mixin as _bakerByBakerId
from .ccdscan_queries._bakers                                import Mixin as _bakers
from .ccdscan_queries._blockByBlockHash                      import Mixin as _blockByBlockHash
from .ccdscan_queries._blocks                                import Mixin as _blocks
from .ccdscan_queries._passiveDelegation                     import Mixin as _passiveDelegation
from .ccdscan_queries._paydayStatus                          import Mixin as _paydayStatus
from .ccdscan_queries._poolRewardMetricsForBakerPool         import Mixin as _poolRewardMetricsForBakerPool
from .ccdscan_queries._poolRewardMetricsForPassiveDelegation import Mixin as _poolRewardMetricsForPassiveDelegation
from .ccdscan_queries._rewardMetricsForAccount               import Mixin as _rewardMetricsForAccount
from .ccdscan_queries._search                                import Mixin as _search
from .ccdscan_queries._transactionByTransactionHash          import Mixin as _transactionByTransactionHash
from .ccdscan_queries._transactionMetrics                    import Mixin as _transactionMetrics
from .ccdscan_queries.ql_support                             import Mixin as ql_support
from .ccdscan_queries.exchange_account_updates               import Mixin as exchange_accounts  

import datetime as dt
# from .ccdscan_queries.enums import NODES_REQUEST_LIMIT
NODES_REQUEST_LIMIT =20
class CCDScan(
    _accountByAddress,
    _accounts,
    _bakerByBakerId,
    _bakers,
    _blockByBlockHash,
    _blocks,
    _passiveDelegation,
    _paydayStatus,
    _poolRewardMetricsForBakerPool,
    _poolRewardMetricsForPassiveDelegation,
    _rewardMetricsForAccount,
    _search,
    _transactionByTransactionHash,
    _transactionMetrics,
    ql_support,
    exchange_accounts,
    ):

    # https://github.com/Concordium/concordium-scan/tree/e95e8b2b191fefcf381ef4b4a1c918dd1f11ae05/frontend/src/queries
    def __init__(self, tooter):
        self.tooter = tooter
        self.nodes_request_limit = NODES_REQUEST_LIMIT
        self.explorer_ccd_request_timestamp             = dt.datetime.utcnow() - dt.timedelta(seconds=10)
        self.explorer_ccd_request_timestamp_delegators  = dt.datetime.utcnow() - dt.timedelta(seconds=10)
        self.graphql_url = 'https://api-ccdscan.mainnet.concordium.software/graphql/'
        self.graphql_url_testnet = 'https://testnet.api.ccdscan.io/graphql'
        