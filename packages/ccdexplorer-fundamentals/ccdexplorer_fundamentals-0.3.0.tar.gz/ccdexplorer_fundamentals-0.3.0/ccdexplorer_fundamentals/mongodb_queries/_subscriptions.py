import datetime as dt


# from ccdexplorer_fundamentals.user import User
class Mixin:
    def get_bot_messages_for_user(
        self, user, environment=None, start_date: dt.datetime = None
    ):
        pipeline = [
            {
                # "$match":     {"timestamp": {"$gt": start_date} },
                "$match": {
                    "timestamp": {"$gt": start_date},
                    "receiver": user.chat_id,
                    "environment": environment,
                }
            },
            {"$count": "count_messages"},
        ]

        return pipeline

    def get_bot_messages_count(self, environment=None):
        pipeline = [
            {
                # "$match":     {"timestamp": {"$gte": start_date} },
                "$match": {"environment": environment}
            },
            {"$count": "count_messages"},
        ]

        return pipeline

    def get_bot_messages_per_type(self, environment=None):
        pipeline = [
            {
                # "$match":     {"timestamp": {"$gte": start_date} },
                "$match": {"environment": environment}
            },
            {"$sortByCount": "$type"},
        ]

        return pipeline
