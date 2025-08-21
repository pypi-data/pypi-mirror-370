import pymongo
from pymongo import DESCENDING


class Mixin:
    def search_txs_on_list_of_hashes(
        self, list_of_hashses, skip, limit, sort_on="amount", sort_direction=-1
    ):
        """
        This pipeline is built for the collection 'transactions'.
        """
        sort_direction = (
            pymongo.ASCENDING if sort_direction == 1 else pymongo.DESCENDING
        )
        sort_condition = (
            {"$sort": {"amount_ccd": sort_direction}}
            if sort_on == "amount"
            else {"$sort": {"blockHeight": sort_direction}}
        )
        pipeline = [
            {"$match": {"_id": {"$in": list_of_hashses}}},
            {
                "$addFields": {
                    "amount_ccd": {
                        "$first": {
                            "$map": {
                                "input": "$result.events",
                                "as": "events",
                                "in": {
                                    "$trunc": {
                                        "$divide": [
                                            {"$toDouble": "$$events.amount"},
                                            1000000,
                                        ]
                                    }
                                },
                            }
                        }
                    }
                }
            },
            {
                "$facet": {
                    "metadata": [{"$count": "total"}],
                    "data": [{"$skip": int(skip)}, {"$limit": int(limit)}],
                }
            },
            {
                "$project": {
                    "data": 1,
                    "total": {"$arrayElemAt": ["$metadata.total", 0]},
                }
            },
        ]

        return pipeline

    def search_transfers_based_on_indices(
        self,
        transfer_type,
        gte,
        lte,
        start_block,
        end_block,
        # skip, limit,
        list_of_tx_hashes_with_memo_predicate,
        # sort_on='amount', sort_direction=-1,
        filter_on_memo_txs=False,
    ):
        pipeline = []

        if transfer_type == "scheduled":
            pipeline.extend(
                [{"$match": {"contents": {"$in": ["transferWithSchedule"]}}}]
            )

        if filter_on_memo_txs:
            pipeline.extend(
                [{"$match": {"_id": {"$in": list_of_tx_hashes_with_memo_predicate}}}]
            )

        pipeline.extend(
            [
                {"$match": {"amount": {"$gte": gte}}},
                {"$match": {"amount": {"$lte": lte}}},
                {"$match": {"blockHeight": {"$gt": start_block, "$lte": end_block}}},
                # { '$facet':     { 'metadata': [ { '$count': 'total' } ],
                #                 'data': [ { '$skip': int(skip) }, { '$limit': int(limit) } ]
                #                 }
                # }
            ]
        )

        return pipeline

    def search_transfers_based_on_indices_v2(
        self,
        transfer_type,
        gte,
        lte,
        start_block,
        end_block,
        # skip, limit,
        list_of_tx_hashes_with_memo_predicate,
        # sort_on='amount', sort_direction=-1,
        filter_on_memo_txs=False,
    ):
        pipeline = []

        if transfer_type == "transferred_with_schedule":
            pipeline.extend(
                [{"$match": {"contents": {"$in": ["transferred_with_schedule"]}}}]
            )

        if filter_on_memo_txs:
            pipeline.extend(
                [{"$match": {"_id": {"$in": list_of_tx_hashes_with_memo_predicate}}}]
            )

        pipeline.extend(
            [
                {"$set": {"amount_ccd": {"$divide": ["$amount", 1000000]}}},
                {"$match": {"amount_ccd": {"$gte": gte}}},
                {"$match": {"amount_ccd": {"$lte": lte}}},
                {"$match": {"block_height": {"$gt": start_block, "$lte": end_block}}},
            ]
        )

        return pipeline

    def search_transfers_mongo_v2(
        self,
        transfer_type,
        gte,
        lte,
        start_date,
        end_date,
        skip,
        limit,
        list_of_tx_hashes,
        sort_on="amount",
        sort_direction=-1,
        filter_on_tx_hashes=False,
    ):
        """
        This pipeline now includes all transfers, so regular, scheduled and with memo.
        """

        sort_direction = (
            pymongo.ASCENDING if sort_direction == 1 else pymongo.DESCENDING
        )
        sort_condition = (
            {"$sort": {"amount_ccd": sort_direction}}
            if sort_on == "amount"
            else {"$sort": {"block_info.slot_time": sort_direction}}
        )
        type_contents_condition = [transfer_type]
        pipeline = [
            {"$match": {"type.contents": {"$in": type_contents_condition}}},
        ]
        if filter_on_tx_hashes:
            pipeline.extend([{"$match": {"_id": {"$in": list_of_tx_hashes}}}])

        if transfer_type == "transferred_with_schedule":
            pipeline.extend(
                [
                    {
                        "$set": {
                            "amount_ccd": {
                                "$sum": {
                                    "$map": {
                                        "input": "$account_transaction.effects.transferred_with_schedule.amount",
                                        "as": "event",
                                        "in": {"$divide": ["$$event.amount", 1000000]},
                                    }
                                }
                            }
                        }
                    }
                ]
            )
        else:
            # so regular transfer
            pipeline.extend(
                [
                    {
                        "$set": {
                            "amount_ccd": {
                                "$divide": [
                                    "$account_transaction.effects.account_transfer.amount",
                                    1000000,
                                ]
                            }
                        }
                    }
                ]
            )

        pipeline.extend(
            [
                {"$match": {"amount_ccd": {"$gte": gte}}},
                {"$match": {"amount_ccd": {"$lte": lte}}},
                {
                    "$match": {
                        "block_info.slot_time": {"$gte": start_date, "$lt": end_date}
                    }
                },
                sort_condition,
                {
                    "$facet": {
                        "metadata": [{"$count": "total"}],
                        "data": [{"$skip": int(skip)}, {"$limit": int(limit)}],
                    }
                },
                {
                    "$project": {
                        "data": 1,
                        "total": {"$arrayElemAt": ["$metadata.total", 0]},
                    }
                },
            ]
        )

        return pipeline

    def search_scheduled_transfers_mongo_v2(
        self,
        transfer_type,
        gte,
        lte,
        start_date,
        end_date,
        skip,
        limit,
        list_of_tx_hashes,
        sort_on="amount",
        sort_direction=-1,
        filter_on_tx_hashes=False,
    ):
        """
        This pipeline now includes all transfers, so regular, scheduled and with memo.
        """

        sort_direction = (
            pymongo.ASCENDING if sort_direction == 1 else pymongo.DESCENDING
        )
        sort_condition = (
            {"$sort": {"amount_ccd": sort_direction}}
            if sort_on == "amount"
            else {"$sort": {"block_info.slot_time": sort_direction}}
        )
        type_contents_condition = ["transferred_with_schedule"]
        pipeline = [
            {"$match": {"type.contents": {"$in": type_contents_condition}}},
        ]
        if filter_on_tx_hashes:
            pipeline.extend([{"$match": {"_id": {"$in": list_of_tx_hashes}}}])

        pipeline.extend(
            [
                {
                    "$set": {
                        "amount_ccd": {
                            "$sum": {
                                "$map": {
                                    "input": "$account_transaction.effects.transferred_with_schedule.amount",
                                    "as": "event",
                                    "in": {"$divide": ["$$event.amount", 1000000]},
                                }
                            }
                        }
                    }
                },
                {"$match": {"amount_ccd": {"$gte": gte}}},
                {"$match": {"amount_ccd": {"$lte": lte}}},
                {
                    "$match": {
                        "block_info.slot_time": {"$gte": start_date, "$lt": end_date}
                    }
                },
                sort_condition,
                {
                    "$facet": {
                        "metadata": [{"$count": "total"}],
                        "data": [{"$skip": int(skip)}, {"$limit": int(limit)}],
                    }
                },
                {
                    "$project": {
                        "data": 1,
                        "total": {"$arrayElemAt": ["$metadata.total", 0]},
                    }
                },
            ]
        )

        return pipeline

    def search_scheduled_transfers_mongo(
        self,
        transfer_type,
        gte,
        lte,
        start_date,
        end_date,
        skip,
        limit,
        list_of_tx_hashes,
        sort_on="amount",
        sort_direction=-1,
        filter_on_tx_hashes=False,
    ):
        sort_direction = (
            pymongo.ASCENDING if sort_direction == 1 else pymongo.DESCENDING
        )
        sort_condition = (
            {"$sort": {"amount_ccd": sort_direction}}
            if sort_on == "amount"
            else {"$sort": {"blockInfo.blockSlotTime": sort_direction}}
        )
        type_contents_condition = ["transferWithSchedule"]
        pipeline = [
            {"$match": {"type.contents": {"$in": type_contents_condition}}},
        ]
        if filter_on_tx_hashes:
            pipeline.extend([{"$match": {"_id": {"$in": list_of_tx_hashes}}}])

        pipeline.extend(
            [
                {
                    "$set": {
                        "amount_ccd": {
                            "$sum": {
                                "$first": {
                                    "$map": {
                                        "input": "$result.events",
                                        "as": "event",
                                        "in": {
                                            "$map": {
                                                "input": "$$event.amount",
                                                "as": "amount",
                                                "in": {
                                                    "$divide": [
                                                        {
                                                            "$toDouble": {
                                                                "$last": "$$amount"
                                                            }
                                                        },
                                                        1000000,
                                                    ]
                                                },
                                            }
                                        },
                                    }
                                }
                            }
                        }
                    }
                },
                {"$match": {"amount_ccd": {"$gte": gte}}},
                {"$match": {"amount_ccd": {"$lte": lte}}},
                {"$match": {"blockSlotTime": {"$gte": start_date, "$lt": end_date}}},
                sort_condition,
                {
                    "$facet": {
                        "metadata": [{"$count": "total"}],
                        "data": [{"$skip": int(skip)}, {"$limit": int(limit)}],
                    }
                },
                {
                    "$project": {
                        "data": 1,
                        "total": {"$arrayElemAt": ["$metadata.total", 0]},
                    }
                },
            ]
        )

        return pipeline

    def search_transfers_mongo(
        self,
        transfer_type,
        gte,
        lte,
        start_date,
        end_date,
        skip,
        limit,
        list_of_tx_hashes,
        sort_on="amount",
        sort_direction=-1,
        filter_on_tx_hashes=False,
    ):
        sort_direction = (
            pymongo.ASCENDING if sort_direction == 1 else pymongo.DESCENDING
        )
        sort_condition = (
            {"$sort": {"amount_ccd": sort_direction}}
            if sort_on == "amount"
            else {"$sort": {"blockInfo.blockSlotTime": sort_direction}}
        )
        type_contents_condition = ["transfer", "transferWithMemo"]

        pipeline = [
            {"$match": {"type.contents": {"$in": type_contents_condition}}},
        ]

        if filter_on_tx_hashes:
            pipeline.extend([{"$match": {"_id": {"$in": list_of_tx_hashes}}}])

        pipeline.extend(
            [
                {
                    "$addFields": {
                        "amount_ccd": {
                            "$first": {
                                "$map": {
                                    "input": "$result.events",
                                    "as": "events",
                                    "in": {
                                        "$trunc": {
                                            "$divide": [
                                                {"$toDouble": "$$events.amount"},
                                                1000000,
                                            ]
                                        }
                                    },
                                }
                            }
                        }
                    }
                },
                {"$match": {"amount_ccd": {"$gte": gte}}},
                {"$match": {"amount_ccd": {"$lte": lte}}},
                {"$match": {"blockSlotTime": {"$gte": start_date, "$lt": end_date}}},
                sort_condition,
                {
                    "$facet": {
                        "metadata": [{"$count": "total"}],
                        "data": [{"$skip": int(skip)}, {"$limit": int(limit)}],
                    }
                },
                {
                    "$project": {
                        "data": 1,
                        "total": {"$arrayElemAt": ["$metadata.total", 0]},
                    }
                },
            ]
        )

        return pipeline

    def search_txs_hashes_for_account_as_sender(self, account_id):
        pipeline = [{"$match": {"sender": {"$eq": account_id}}}]
        return pipeline

    def search_txs_hashes_for_account_as_receiver(self, account_id):
        pipeline = [{"$match": {"receiver": {"$eq": account_id}}}]
        return pipeline

    def search_txs_hashes_for_account_as_sender_with_params(
        self, account_id, start_block, end_block
    ):
        pipeline = [
            {"$match": {"sender_canonical": {"$eq": account_id[:29]}}},
            {"$match": {"block_height": {"$gt": start_block, "$lte": end_block}}},
        ]
        return pipeline

    def search_txs_hashes_for_account_as_receiver_with_params(
        self, account_id, start_block, end_block
    ):
        pipeline = [
            {"$match": {"receiver_canonical": {"$eq": account_id[:29]}}},
            {"$match": {"block_height": {"$gt": start_block, "$lte": end_block}}},
        ]
        return pipeline

    def search_txs_hashes_for_account_as_sender_with_params_id_only(
        self, account_id, start_block, end_block
    ):
        pipeline = [
            {"$match": {"sender_canonical": {"$eq": account_id[:29]}}},
            {"$match": {"block_height": {"$gt": start_block, "$lte": end_block}}},
            {"$project": {"_id": 1}},
        ]
        return pipeline

    def search_txs_hashes_for_account_as_receiver_with_params_id_only(
        self, account_id, start_block, end_block
    ):
        pipeline = [
            {"$match": {"receiver_canonical": {"$eq": account_id[:29]}}},
            {"$match": {"block_height": {"$gt": start_block, "$lte": end_block}}},
            {"$project": {"_id": 1}},
        ]
        return pipeline

    def search_txs_in_hash_list(self, tx_hashes):
        pipeline = [
            {"$match": {"_id": {"$in": tx_hashes}}},
            {"$sort": {"block_info.slot_time": DESCENDING}},
        ]
        return pipeline

    def search_txs_in_transactions(self, start_block, end_block):
        pipeline = [
            {
                "$match": {
                    "block_info.block_height": {"$gt": start_block, "$lte": end_block}
                }
            },
        ]
        return pipeline

    def heights_with_transactions_after(self, start_block):
        pipeline = [
            {"$match": {"block_height": {"$gt": start_block}}},
            {"$project": {"_id": 0, "blockHeight": 1}},
        ]
        return pipeline

    def search_txs_non_finalized(self):
        pipeline = [
            {"$match": {"block_info.finalized": False}},
        ]
        return pipeline

    ### exchange search
    def search_exchange_txs_as_receiver(
        self, exchanges_canonical: list, start_block: int, end_block: int
    ):
        pipeline = [
            {"$match": {"receiver_canonical": {"$in": exchanges_canonical}}},
            {"$match": {"block_height": {"$gt": start_block, "$lte": end_block}}},
        ]
        return pipeline

    def search_exchange_txs_as_sender(
        self, exchanges_canonical: list, start_block: int, end_block: int
    ):
        pipeline = [
            {"$match": {"sender_canonical": {"$in": exchanges_canonical}}},
            {"$match": {"block_height": {"$gt": start_block, "$lte": end_block}}},
        ]
        return pipeline
