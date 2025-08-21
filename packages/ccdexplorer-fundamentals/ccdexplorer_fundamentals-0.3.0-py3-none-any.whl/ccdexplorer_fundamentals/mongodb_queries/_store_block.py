import pymongo
from pymongo import ReplaceOne
from dateutil.parser import isoparse
from ..transaction import Transaction
from ccdexplorer_fundamentals.block import ConcordiumBlockInfo, ConcordiumBlock
from ccdexplorer_fundamentals.transaction import ClassificationResult
import datetime as dt


class Mixin:
    # def store_block_in_mongodb(self, block: ConcordiumBlock, client, version=1):
    #     if not isinstance(block.blockInfo.blockArriveTime, dt.datetime):
    #         block.blockInfo.blockArriveTime    = isoparse(block.blockInfo.blockArriveTime)
    #     if not isinstance(block.blockInfo.blockReceiveTime, dt.datetime):
    #         block.blockInfo.blockReceiveTime   = isoparse(block.blockInfo.blockReceiveTime)
    #     if not isinstance(block.blockInfo.blockSlotTime, dt.datetime):
    #         block.blockInfo.blockSlotTime      = isoparse(block.blockInfo.blockSlotTime)

    #     summary = block.blockSummary
    #     try:
    #         summary.updates['chainParameters']['microGTUPerEuro']['numerator'] = \
    #         str(summary.updates['chainParameters']['microGTUPerEuro']['numerator'])
    #     except:
    #         pass

    #     for k, v in summary.updates.items():
    #         try:
    #             summary[k] = isoparse(v)
    #         except Exception:
    #             pass

    #     for item in summary.specialEvents:
    #         for k, v in item.items():
    #             try:
    #                 summary[k] = isoparse(v)
    #             except Exception:
    #                 pass

    #     if version > 1:
    #         del summary.updates['keys']

    #     summary_to_store = summary.__dict__
    #     if summary_to_store['finalizationData']:
    #         summary_to_store['finalizationData'] = summary_to_store['finalizationData'].__dict__

    #     _id = block.blockInfo.blockHash
    #     mongo_block = {
    #         '_id': _id,
    #         'blockHeight': block.blockInfo.blockHeight,
    #         'blockInfo': block.blockInfo.__dict__,
    #         'blockSummary': summary_to_store}
    #     try:
    #         query = {"_id": _id }
    #         self.collection_blocks.replace_one( query, mongo_block, upsert=True)
    #     except Exception as e:
    #         pass

    #     transactions = summary.transactionSummaries
    #     for tx in transactions:
    #         _id = tx['hash']
    #         tx['blockInfo'] = block.blockInfo.__dict__
    #         tx['_id'] = _id
    #         try:
    #             query = {"_id": _id }
    #             self.collection_transactions.replace_one(query, tx, upsert=True)
    #         except Exception as e:
    #             pass

    #     # finally, store account_tx_link if needed
    #     self.fill_accounts_involved(transactions, client, version)

    def store_blockInfo_in_mongodb(self, block: ConcordiumBlock, client, version=1):
        if version == 2:
            # if not isinstance(block.blockInfo.blockArriveTime, dt.datetime):
            #     block.blockInfo.blockArriveTime    = isoparse(block.blockInfo.blockArriveTime)
            # if not isinstance(block.blockInfo.blockReceiveTime, dt.datetime):
            #     block.blockInfo.blockReceiveTime   = isoparse(block.blockInfo.blockReceiveTime)
            if not isinstance(block.blockInfo.blockSlotTime, dt.datetime):
                block.blockInfo.blockSlotTime = isoparse(block.blockInfo.blockSlotTime)

        summary = block.blockSummary

        _id = block.blockInfo.blockHash
        tx_hashes = [x["hash"] for x in summary.transactionSummaries]
        mongo_block = block.blockInfo.__dict__
        mongo_block["transactionHashes"] = tx_hashes
        try:
            query = {"_id": _id}
            self.collection_blocks.replace_one(query, mongo_block, upsert=True)
        except Exception as e:
            pass

        transactions = summary.transactionSummaries
        for tx in transactions:
            _id = tx["hash"]
            if version == 2:
                tx["blockHeight"] = block.blockInfo.blockHeight
                tx["blockSlotTime"] = block.blockInfo.blockSlotTime
            tx["_id"] = _id
            try:
                query = {"_id": _id}
                self.collection_transactions.replace_one(query, tx, upsert=True)
            except Exception as e:
                pass

        # finally, generate_indices_based_on_transactions
        self.generate_indices_based_on_transactions(transactions, client, version)

    # def possibly_update_tx_with_new_blockInfo_in_mongodb(self, block: ConcordiumBlock, tx, client, version=1):
    #     if not isinstance(block.blockInfo.blockArriveTime, dt.datetime):
    #         block.blockInfo.blockArriveTime    = isoparse(block.blockInfo.blockArriveTime)
    #     if not isinstance(block.blockInfo.blockReceiveTime, dt.datetime):
    #         block.blockInfo.blockReceiveTime   = isoparse(block.blockInfo.blockReceiveTime)
    #     if not isinstance(block.blockInfo.blockSlotTime, dt.datetime):
    #         block.blockInfo.blockSlotTime      = isoparse(block.blockInfo.blockSlotTime)

    #     summary = block.blockSummary

    #     _id = block.blockInfo.blockHash

    #     transactions = summary.transactionSummaries
    #     for tx in transactions:
    #         _id = tx['hash']
    #         tx['blockInfo'] = block.blockInfo.__dict__
    #         tx['_id'] = _id
    #         try:
    #             query = {"_id": _id }
    #             self.collection_transactions.replace_one(query, tx, upsert=True)
    #         except Exception as e:
    #             pass

    #     # finally, store account_tx_link if needed
    #     self.fill_accounts_involved(transactions, client, version)

    def generate_indices_based_on_transactions(self, transactions, client, version):
        """
        Given a list of transactions, apply rules to determine which index needs to be updated.
        Add this to a to_be_sent_to_mongo list and do insert_many.
        """
        list_accounts_involved_all = []
        list_accounts_involved_transfer = []
        list_contracts_involved = []
        # print (f"Generating indices for {len(transactions):,.0f} transactions...")
        for tx in transactions:
            classificationResult, classified_tx = (
                Transaction(client).init_from_node(tx).classify_transaction_for_bot()
            )

            if version == 1:
                pass
            elif version == 2:
                index_all, index_transfer = self.determine_account_indices(
                    classified_tx, tx, classificationResult, version
                )
                list_accounts_involved_all.append(
                    ReplaceOne({"_id": index_all["_id"]}, index_all, upsert=True)
                )
                if index_transfer:
                    list_accounts_involved_transfer.append(
                        ReplaceOne(
                            {"_id": index_transfer["_id"]}, index_transfer, upsert=True
                        )
                    )

                if classificationResult.contracts_involved:
                    for contract in classificationResult.list_of_contracts_involved:
                        index_contract = self.determine_contract_indices(
                            classified_tx, tx, classificationResult, contract, version
                        )
                        list_contracts_involved.append(
                            ReplaceOne(
                                {"_id": index_contract["_id"]},
                                index_contract,
                                upsert=True,
                            )
                        )

        try:
            if len(list_accounts_involved_all) > 0:
                result = self.collection_involved_accounts_all.bulk_write(
                    list_accounts_involved_all
                )
                print(
                    f"B: {tx['blockHeight']:,.0f} | Match {result.matched_count:,.0f} | Mod {result.modified_count:,.0f} | Upsert {result.upserted_count:2,.0f} in _all."
                )
        except Exception as e:
            print(e)

        try:
            if len(list_accounts_involved_transfer) > 0:
                result = self.collection_involved_accounts_transfer.bulk_write(
                    list_accounts_involved_transfer
                )
                print(
                    f"B: {tx['blockHeight']:,.0f} | Match {result.matched_count:,.0f} | Mod {result.modified_count:,.0f} | Upsert {result.upserted_count:2,.0f} in _transfer."
                )
        except Exception as e:
            print(e)

        try:
            if len(list_contracts_involved) > 0:
                result = self.collection_involved_contracts.bulk_write(
                    list_contracts_involved
                )
                print(
                    f"B: {tx['blockHeight']:,.0f} | Match {result.matched_count:,.0f} | Mod {result.modified_count:,.0f} | Upsert {result.upserted_count:2,.0f} in _contracts."
                )
        except Exception as e:
            print(e)

    # def fill_accounts_involved(self, transactions, client, version=1):
    #     for tx in transactions:
    #     #     tx_already_done = self.collection_accounts_involved_all.find_one({"_id": tx['blockInfo']['blockHash']})

    #     #     if not tx_already_done:
    #         classificationResult, classified_tx = Transaction(client).init_from_node(tx).classify_transaction_for_bot()

    #         if version == 1:
    #             if classificationResult.sender and classificationResult.receiver:
    #                 self.store_account_tx_link(classified_tx, classificationResult, version)

    #         elif version == 2:
    #             self.determine_account_indices(classified_tx, classificationResult, version)

    #             if classificationResult.contracts_involved:
    #                 for contract in classificationResult.list_of_contracts_involved:
    #                     self.store_contract_tx_link_all(classified_tx, classificationResult, contract, version)

    def determine_account_indices(
        self,
        classified_tx: Transaction,
        tx,
        classificationResult: ClassificationResult,
        version=1,
    ):
        _id = classificationResult.txHash
        dct = {
            "_id": _id,
            "sender": classificationResult.sender,
            "receiver": classificationResult.receiver,
            "sender_canonical": (
                classificationResult.sender[:29]
                if classificationResult.sender
                else None
            ),
            "receiver_canonical": (
                classificationResult.receiver[:29]
                if classificationResult.receiver
                else None
            ),
            "amount": classificationResult.amount,
            "type": classificationResult.type,
            "contents": classificationResult.contents,
            "blockHeight": tx["blockHeight"],
        }
        if version > 1:
            memo = None
            if "events" in classified_tx.result:
                for event in classified_tx.result["events"]:
                    if "memo" in event:
                        memo = event["memo"]

            if memo:
                dct.update({"memo": memo})
        if classificationResult.accounts_involved_transfer:
            return dct, dct
        else:
            return dct, None

    def determine_contract_indices(
        self,
        classified_tx: Transaction,
        tx,
        classificationResult: ClassificationResult,
        contract,
        version=1,
    ):
        _id = f"{classificationResult.txHash}-<{contract[0]},{contract[1]}>"
        dct = {
            "_id": _id,
            "index": contract[0],
            "subindex": contract[1],
            "contract": f"<{contract[0]},{contract[1]}>",
            "type": classificationResult.type,
            "contents": classificationResult.contents,
            "blockHeight": tx["blockHeight"],
        }

        return dct

    # def store_account_tx_link(self,
    #     classified_tx: Transaction,
    #     classificationResult: ClassificationResult,
    #     version=1):
    #     _id = classificationResult.txHash
    #     dct = {

    #         "_id":      _id,
    #         "sender":   classificationResult.sender,
    #         "receiver": classificationResult.receiver,
    #         "amount":   classificationResult.amount,
    #         "type":     classificationResult.type,
    #         "contents": classificationResult.contents,
    #         "blockHeight": classified_tx.block['blockHeight']
    #     }
    #     if version > 1:
    #         memo = None
    #         if 'events' in classified_tx.result:
    #             for event in classified_tx.result['events']:
    #                 if 'memo' in event:
    #                     memo = event['memo']

    #         if memo:
    #             dct.update(
    #                 {
    #                     'memo': memo
    #                 }
    #             )
    #     try:
    #         if version == 1:
    #             self.collection_accounts_involved.insert_one(dct)
    #         elif version == 2:
    #             if classificationResult.accounts_involved_transfer:
    #                 query = {"_id": _id }
    #                 self.collection_accounts_involved_transfer.replace_one(query, dct, upsert=True)

    #             if classificationResult.accounts_involved_all:
    #                 query = {"_id": _id }
    #                 self.collection_accounts_involved_all.replace_one(query, dct, upsert=True)
    #     except Exception as e:
    #         print (e)

    # def store_contract_tx_link_all(self,
    #     classified_tx: Transaction,
    #     classificationResult: ClassificationResult,
    #     contract,
    #     version=1):
    #     _id =  f"{classificationResult.txHash}-<{contract[0]},{contract[1]}>"
    #     dct = {

    #         "_id":      _id,
    #         "index":    contract[0],
    #         "subindex": contract[1],
    #         "contract": f"<{contract[0]},{contract[1]}>",
    #         "type":     classificationResult.type,
    #         "contents": classificationResult.contents,
    #         "blockHeight": classified_tx.block['blockHeight']
    #     }

    #     try:
    #         if version == 1:
    #             pass

    #         elif version == 2:
    #             query = {"_id": _id }
    #             self.collection_contracts_involved.replace_one(query, dct, upsert=True)
    #     except Exception as e:
    #         print (e)

    def search_tx_higher_than_block_height(self, block_height_start, block_height_end):
        pipeline = [
            {"$match": {"blockInfo.blockHeight": {"$gt": block_height_start}}},
            {"$match": {"blockInfo.blockHeight": {"$lt": block_height_end}}},
            # {'$project': {
            #     '_id': 1
            #     }
            # }
        ]

        return pipeline
