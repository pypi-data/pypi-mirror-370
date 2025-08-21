from pydantic import BaseModel

class ConcordiumReward(BaseModel):
    account: str = None
    poolOwner: int = None
    bakerReward: int
    finalizationReward: int
    transactionFees: int
    tag: str