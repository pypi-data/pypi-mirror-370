import datetime as dt

class Mixin:
    def get_rewards_data_for_accounts(self, date: str):
        pipeline = [
                {
                    "$match":     {
                        "date": {"$eq": date},
                        "reward.tag": {"$eq": "PaydayAccountReward"}
                     }
                    # '$match': { "account_id": account_id }
                }, 
                # { '$sort': {'blockSlotTime': -1} },
                # {'$limit': limit},
                {
                '$addFields': {
                    'sum_rewards': {
                        '$sum': [
                            '$reward.bakerReward', '$reward.finalizationReward', '$reward.transactionFees'
                        ]
                    }
                }
                },   
                # {'$project': {'_id': 0, 'stakedAmount': 1, 'sum_rewards': 1}}

        ]

        return pipeline
    def get_rewards_data_for_account(self, account_id: str):
        pipeline = [
                {
                    # "$match":     {"timestamp": {"$gt": start_date} },
                    '$match': { "account_id": account_id }
                }, 
                # { '$sort': {'blockSlotTime': -1} },
                # {'$limit': limit},
                {
                '$addFields': {
                    'sum_rewards': {
                        '$sum': [
                            '$reward.bakerReward', '$reward.finalizationReward', '$reward.transactionFees'
                        ]
                    }
                }
                },   
                # {'$project': {'_id': 0, 'stakedAmount': 1, 'sum_rewards': 1}}

        ]

        return pipeline

    def get_rewards_data_for_pool(self, pool_id: str):
        try:
            pool_id = int(pool_id)
        except:
            pool_id = 'passiveDelegation'

        pipeline = [
                # {
                #     "$match":     {"date": {"$in": days_in_apy_period} },
                # },
                {
                    '$match': { "poolOwner": pool_id }
                }, 
                { '$sort': {'blockSlotTime': -1} },
                # {'$limit': limit},
                {
                '$addFields': {
                    'baker_ratio': {
                        '$divide': [
                            '$pool_status.currentPaydayStatus.bakerEquityCapital', 
                            '$pool_status.currentPaydayStatus.effectiveStake'

                        ]
                    }
                }
                },   
                {
                '$addFields': {
                    'delegators_ratio': {
                        '$divide': [
                            '$pool_status.currentPaydayStatus.delegatedCapital', 
                            '$pool_status.currentPaydayStatus.effectiveStake'
                            ]
                    }
                }
                },
                {
                '$addFields': {
                    'delegators_baking_reward': {
                        '$multiply': [
                            {
                                '$subtract': [
                                    1, 
                                    '$pool_status.poolInfo.commissionRates.bakingCommission'
                                ]
                            }
                            ,
                            {
                                '$multiply': 
                                [
                                    '$delegators_ratio', 
                                    '$reward.bakerReward'
                                ]
                            }
                        ]
                    }
                }
                },
                {
                '$addFields': {
                    'delegators_transaction_reward': {
                        '$multiply': [
                            {
                                '$subtract': [
                                    1, 
                                    '$pool_status.poolInfo.commissionRates.transactionCommission'
                                ]
                            }
                            ,
                            {
                                '$multiply': 
                                [
                                    '$delegators_ratio', 
                                    '$reward.transactionFees'
                                ]
                            }
                        ]
                    }
                }
                },   
                {
                '$addFields': {
                    'delegators_finalization_reward': {
                        '$multiply': [
                            {
                                '$subtract': [
                                    1, 
                                    '$pool_status.poolInfo.commissionRates.finalizationCommission'
                                ]
                            }
                            ,
                            {
                                '$multiply': 
                                [
                                    '$delegators_ratio', 
                                    '$reward.finalizationReward'
                                ]
                            }
                        ]
                    }
                }
                },
                {
                '$addFields': {
                    'baker_baking_reward': {
                        '$subtract': [
                            '$reward.bakerReward', 
                            '$delegators_baking_reward'
                        ]
                    }
                }
                },
                {
                '$addFields': {
                    'baker_transaction_reward': {
                        '$subtract': [
                            '$reward.transactionFees', 
                            '$delegators_transaction_reward'
                                ]
                            }
                    }
                },   
                {
                '$addFields': {
                    'baker_finalization_reward': {
                        '$subtract': [
                            '$reward.finalizationReward', 
                            '$delegators_finalization_reward'
                                ]
                            }
                    }
                },   
                {
                '$addFields': {
                    'delegator_reward': {
                        '$add': [
                            '$delegators_baking_reward', 
                            '$delegators_transaction_reward',
                            '$delegators_finalization_reward'
                        ]
                    }
                }
                },   
                {
                '$addFields': {
                    'total_reward': {
                        '$sum': [
                            '$reward.bakerReward', '$reward.finalizationReward', '$reward.transactionFees'
                        ]
                    }
                }
                },   
                {
                '$addFields': {
                    'baker_reward': {
                        '$subtract': [
                            '$total_reward', 
                            '$delegator_reward'
                        ]
                    }
                }
                },   
                # {'$project': {'_id': 0, 'bakerEquityCapital': 1, 'delegatedCapital': 1, 'bakerReward_baker': 1}}

        ]

        return pipeline

    def get_rewards_data_for_pools(self, date: str):
        pipeline = [
                {
                    "$match":     {
                        "date": {"$eq": date},
                        "reward.tag": {"$eq": "PaydayPoolReward"}
                     }
                }, 
                {
                '$addFields': {
                    'baker_ratio': {
                        '$divide': [
                            '$pool_status.currentPaydayStatus.bakerEquityCapital', 
                            '$pool_status.currentPaydayStatus.effectiveStake'

                        ]
                    }
                }
                },   
                {
                '$addFields': {
                    'delegators_ratio': {
                        '$divide': [
                            '$pool_status.currentPaydayStatus.delegatedCapital', 
                            '$pool_status.currentPaydayStatus.effectiveStake'
                            ]
                    }
                }
                },
                {
                '$addFields': {
                    'delegators_baking_reward': {
                        '$multiply': [
                            {
                                '$subtract': [
                                    1, 
                                    '$pool_status.poolInfo.commissionRates.bakingCommission'
                                ]
                            }
                            ,
                            {
                                '$multiply': 
                                [
                                    '$delegators_ratio', 
                                    '$reward.bakerReward'
                                ]
                            }
                        ]
                    }
                }
                },
                {
                '$addFields': {
                    'delegators_transaction_reward': {
                        '$multiply': [
                            {
                                '$subtract': [
                                    1, 
                                    '$pool_status.poolInfo.commissionRates.transactionCommission'
                                ]
                            }
                            ,
                            {
                                '$multiply': 
                                [
                                    '$delegators_ratio', 
                                    '$reward.transactionFees'
                                ]
                            }
                        ]
                    }
                }
                },   
                {
                '$addFields': {
                    'delegators_finalization_reward': {
                        '$multiply': [
                            {
                                '$subtract': [
                                    1, 
                                    '$pool_status.poolInfo.commissionRates.finalizationCommission'
                                ]
                            }
                            ,
                            {
                                '$multiply': 
                                [
                                    '$delegators_ratio', 
                                    '$reward.finalizationReward'
                                ]
                            }
                        ]
                    }
                }
                },
                {
                '$addFields': {
                    'baker_baking_reward': {
                        '$subtract': [
                            '$reward.bakerReward', 
                            '$delegators_baking_reward'
                        ]
                    }
                }
                },
                {
                '$addFields': {
                    'baker_transaction_reward': {
                        '$subtract': [
                            '$reward.transactionFees', 
                            '$delegators_transaction_reward'
                                ]
                            }
                    }
                },   
                {
                '$addFields': {
                    'baker_finalization_reward': {
                        '$subtract': [
                            '$reward.finalizationReward', 
                            '$delegators_finalization_reward'
                                ]
                            }
                    }
                },   
                {
                '$addFields': {
                    'delegator_reward': {
                        '$add': [
                            '$delegators_baking_reward', 
                            '$delegators_transaction_reward',
                            '$delegators_finalization_reward'
                        ]
                    }
                }
                },   
                {
                '$addFields': {
                    'total_reward': {
                        '$sum': [
                            '$reward.bakerReward', '$reward.finalizationReward', '$reward.transactionFees'
                        ]
                    }
                }
                },   
                {
                '$addFields': {
                    'baker_reward': {
                        '$subtract': [
                            '$total_reward', 
                            '$delegator_reward'
                        ]
                    }
                }
                }
        ]

        return pipeline
