from pydantic import BaseModel

class ConcordiumBlockInfo(BaseModel):
    blockArriveTime: str
    blockBaker: int = None
    blockHash: str
    blockHeight: int
    blockLastFinalized: str
    blockParent: str
    blockReceiveTime: str
    blockSlot: int
    blockSlotTime: str
    eraBlockHeight: int
    finalized: bool
    genesisIndex: int
    transactionCount: int
    transactionEnergyCost: int
    transactionsSize: int

class ConcordiumBlockSummaryFinalizationDataFinalizer(BaseModel):
    bakerId: int
    signed: bool
    weight: int

class ConcordiumBlockSummaryFinalizationData(BaseModel):
    finalizationBlockPointer: str
    finalizationDelay: int
    finalizationIndex: int
    finalizers: list

class ConcordiumBlockSummary(BaseModel):
    protocolVersion: int
    finalizationData: ConcordiumBlockSummaryFinalizationData = None
    specialEvents: list
    updates: dict
    transactionSummaries: list


class ConcordiumBlock(BaseModel):
    blockInfo: ConcordiumBlockInfo
    blockSummary: ConcordiumBlockSummary