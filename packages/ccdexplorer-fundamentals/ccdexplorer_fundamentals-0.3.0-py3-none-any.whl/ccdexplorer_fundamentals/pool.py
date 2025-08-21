from pydantic import BaseModel


class BakerStakePendingChange(BaseModel):
    pendingChangeType: str


class CurrentPaydayStatus(BaseModel):
    bakerEquityCapital: str
    blocksBaked: int
    delegatedCapital: str
    effectiveStake: str
    finalizationLive: bool
    lotteryPower: float
    transactionFeesEarned: str


class CommissionRates(BaseModel):
    bakingCommission: float
    finalizationCommission: float
    transactionCommission: float


class PoolInfo(BaseModel):
    commissionRates: CommissionRates
    metadataUrl: str
    openStatus: str


class APY(BaseModel):
    bakerApy: float
    delegatorsApy: float = None
    totalApy: float


class Rank(BaseModel):
    rank: int
    total: int


class ConcordiumPoolFromClient(BaseModel):
    allPoolTotalCapital: str
    bakerAddress: str
    bakerEquityCapital: str
    bakerId: int
    bakerStakePendingChange: BakerStakePendingChange
    currentPaydayStatus: CurrentPaydayStatus
    delegatedCapital: str
    delegatedCapitalCap: str
    poolInfo: PoolInfo
    poolType: str


class ConcordiumPoolFromCCDScan(BaseModel):
    apy_30: APY
    apy_7: APY
    openStatus: str
    metadataUrl: str
    delegatorCount: int
    delegatedStake: int
    delegatedStakeCap: int
    rankingByTotalStake: Rank
    totalStake: int
    totalStakePercentage: float
    commissionRates: CommissionRates


class PeriodReward(BaseModel):
    sumBakerRewardAmount: int
    sumDelegatorsRewardAmount: int
    sumTotalRewardAmount: int


class ConcordiumPoolRewards(BaseModel):
    LAST24_HOURS: PeriodReward
    LAST7_DAYS: PeriodReward
    LAST30_DAYS: PeriodReward


class ConcordiumPool(BaseModel):
    via_client: ConcordiumPoolFromClient = None
    via_ccdscan: ConcordiumPoolFromCCDScan = None
    rewards: ConcordiumPoolRewards = None
