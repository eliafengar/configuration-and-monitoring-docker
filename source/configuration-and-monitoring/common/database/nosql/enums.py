from enum import Enum


class MongoCollection(Enum):
    Configuration = 'configuration',
    Monitoring = 'monitoring',
    Actions = 'actions'

    def __init__(self, prefix):
        self.prefix = prefix

