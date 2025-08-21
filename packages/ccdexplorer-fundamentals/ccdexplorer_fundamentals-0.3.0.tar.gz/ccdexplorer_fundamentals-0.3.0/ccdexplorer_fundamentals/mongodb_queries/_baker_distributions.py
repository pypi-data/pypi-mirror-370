import pymongo
class Mixin:
    def baker_distribution_for_id(self, bakerId):
        pipeline = [
            {
                '$match': {
                    'blockInfo.blockBaker': bakerId
                }
            }, {
                '$sort': {
                    'blockInfo.blockSlotTime': -1
                }
            }, {
                '$project': {
                    'blockHeight': 1, 
                    '_id': 0
                }
            }
        ]
        
        return pipeline