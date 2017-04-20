import datetime
import logging
import os
import threading
import time
import pymongo
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.cursor import CursorType, _QUERY_OPTIONS

from common.database.nosql.enums import MongoCollection
from common.database.interfaces import ConfigDAO, MonitorDAO, ActionsDAO

# Initialize PyMongo
mongodb_host = os.getenv('MONGODB_SERVICE_SERVICE_HOST', '127.0.0.1')
mongodb_port = os.getenv('MONGODB_SERVICE_SERVICE_PORT', '27017')
logging.info('Opening Mongo Connection using {}:{}'.format(mongodb_host, mongodb_port))
mongo = MongoClient('mongodb://{}:{}/'.format(mongodb_host, mongodb_port))
DATABASE_NAME = 'Animals'
OPLOG_COLLECTION_NAME = 'oplog.$main'


class ProductDAO(ConfigDAO, MonitorDAO, ActionsDAO):

    METADATA_ID = ObjectId('000000000000000000000000')
    MONGO_DB_ID_PROPERTY_NAME = '_id'

    def __init__(self, product):
        ConfigDAO.__init__(self)
        MonitorDAO.__init__(self)
        ActionsDAO.__init__(self)
        self.product = product
        self.database = mongo[DATABASE_NAME]
        self.configuration_collection = self.database[
            '{}.{}'.format(MongoCollection.Configuration.prefix, self.product)]
        self.monitor_collection = self.database[
            '{}.{}'.format(MongoCollection.Monitoring.prefix, self.product)]
        self.actions_collection = self.database[
            '{}.{}'.format(MongoCollection.Actions.prefix, self.product)]

    def enable_events(self, is_async=True):
        if is_async:
            t = threading.Thread(target=self._listen_to_oplog_changes)
            t.setDaemon(True)
            t.start()
        else:
            self._listen_to_oplog_changes()

    # ConfigDAO Methods
    def get_app_config(self):
        return self._get_current(MongoCollection.Configuration)

    def set_app_config(self, data):
        self._insert_new(data, MongoCollection.Configuration)

    def update_app_config(self, data):
        merged_config = self._merge_documents(data, MongoCollection.Configuration)
        self._insert_new(merged_config, MongoCollection.Configuration)

    def delete_app_config(self):
        pass

    @classmethod
    def get_configured_app_names(cls):
        return ProductDAO._get_configured_app_names(MongoCollection.Configuration)

    # MonitoringDAO Methods
    def get_app_stats(self):
        return self._get_current(MongoCollection.Monitoring)

    def set_app_stats(self, data):
        self._insert_new(data, MongoCollection.Monitoring)

    def update_app_stats(self, data):
        merged_stats = self._merge_documents(data, MongoCollection.Monitoring)
        self._insert_new(merged_stats, MongoCollection.Monitoring)

    def delete_app_stats(self):
        pass

    @classmethod
    def get_stats_app_names(cls):
        return ProductDAO._get_configured_app_names(MongoCollection.Monitoring)

    # ActionsDAO Methods
    def get_app_actions(self):
        return self._get_current(MongoCollection.Actions)

    def set_app_actions(self, actions):
        self._insert_new(actions, MongoCollection.Actions)

    def update_app_actions(self, actions):
        merged_actions = self._merge_documents(actions, MongoCollection.Actions)
        self._insert_new(merged_actions, MongoCollection.Actions)

    @classmethod
    def get_actions_app_names(cls):
        return ProductDAO._get_configured_app_names(MongoCollection.Actions)

    # Private methods
    @staticmethod
    def _get_configured_app_names(collection_enum):
        products = []
        for collection in mongo[DATABASE_NAME].collection_names():
            if collection.startswith(collection_enum.prefix):
                product = collection.replace('{}.'.format(collection_enum.prefix), '')
                products.append(product)
        return products

    def _insert_new(self, new_doc, collection_enum):
        collection = self._get_collection_from_enum(collection_enum)
        new_doc['created'] = str(datetime.datetime.now())
        ins_id = collection.insert_one(new_doc).inserted_id
        if ins_id:
            metadata = self._get_or_create_metadata(collection_enum)
            metadata['latest_id'] = ins_id
            collection.save(metadata)

    def _get_or_create_metadata(self, mongo_collection):
        collection = self._get_collection_from_enum(mongo_collection)
        metadata = collection.find_one(
            {self.MONGO_DB_ID_PROPERTY_NAME: self.METADATA_ID})
        if not metadata:

            if mongo_collection is MongoCollection.Configuration:
                metadata_dict = self._get_configuration_metadata_dict()
            elif mongo_collection is MongoCollection.Monitoring:
                metadata_dict = self._get_monitor_metadata_dict()
            elif mongo_collection is MongoCollection.Actions:
                metadata_dict = self._get_actions_metadata_dict()

            collection.insert_one(metadata_dict)

            metadata = collection.find_one(
                {self.MONGO_DB_ID_PROPERTY_NAME: self.METADATA_ID})
            if metadata:
                logging.info('Metadata Document Inserted Successfully')
            else:
                logging.error('Metadata Failed to Create')

        return metadata

    def _get_configuration_metadata_dict(self):
        return {
            self.MONGO_DB_ID_PROPERTY_NAME: self.METADATA_ID,
            'latest_id': None
        }

    def _get_monitor_metadata_dict(self):
        return {
            self.MONGO_DB_ID_PROPERTY_NAME: self.METADATA_ID,
            'latest_id': None
        }

    def _get_actions_metadata_dict(self):
        return {
            self.MONGO_DB_ID_PROPERTY_NAME: self.METADATA_ID,
            'latest_id': None
        }

    def _get_current(self, collection_enum):

        metadata = self._get_or_create_metadata(collection_enum)
        if not metadata['latest_id']:
            current_config = None
        else:
            collection = self._get_collection_from_enum(collection_enum)
            current_config = collection.find_one(
                {self.MONGO_DB_ID_PROPERTY_NAME: metadata['latest_id']})
            if self.MONGO_DB_ID_PROPERTY_NAME in current_config:
                del current_config[self.MONGO_DB_ID_PROPERTY_NAME]

        return current_config

    def _merge_documents(self, new, collection_enum):

        merged = None
        current = self._get_current(collection_enum)

        if not current:
            merged = new

        if not new:
            merged = current

        if not merged:
            merged = current.copy()
            merged.update(new)

        return merged

    def _get_collection_from_enum(self, collection_enum):
        if collection_enum is MongoCollection.Configuration:
            collection = self.configuration_collection
        elif collection_enum is MongoCollection.Monitoring:
            collection = self.monitor_collection
        elif collection_enum is MongoCollection.Actions:
            collection = self.actions_collection
        else:
            collection = None

        return collection

    def _listen_to_oplog_changes(self):

        # get the latest timestamp in the database
        last_ts = mongo.local[OPLOG_COLLECTION_NAME].find().sort(
            '$natural', pymongo.DESCENDING)[0]['ts']

        while True:
            # prepare the tail query and kick it off
            cursor = mongo.local[OPLOG_COLLECTION_NAME].find({
                'ts': {'$gt': last_ts},
                'ns': {'$in': ['{}.{}.{}'.format(
                    DATABASE_NAME, MongoCollection.Configuration.prefix,
                    self.product), '{}.{}.{}'.format(
                    DATABASE_NAME, MongoCollection.Monitoring.prefix,
                    self.product), '{}.{}.{}'.format(
                    DATABASE_NAME, MongoCollection.Actions.prefix,
                    self.product)]},
                'op': 'i'}, cursor_type=CursorType.TAILABLE_AWAIT)
            cursor.add_option(_QUERY_OPTIONS['oplog_replay'])

            try:
                while cursor.alive:
                    try:
                        # grab a document if available
                        doc = cursor.next()

                        logging.debug(doc)

                        # Raise event only for actual data excluding the metadata document
                        actual_doc = doc['o']
                        inner_doc_id = actual_doc[self.MONGO_DB_ID_PROPERTY_NAME]
                        if inner_doc_id != self.METADATA_ID:
                            if MongoCollection.Configuration.prefix in doc['ns']:
                                self.raise_app_config_change_event(actual_doc)
                            elif MongoCollection.Monitoring.prefix in doc['ns']:
                                self.raise_app_stats_change_event(actual_doc)
                            elif MongoCollection.Actions.prefix in doc['ns']:
                                self.raise_app_action_change_event(actual_doc)

                    except StopIteration:
                        # thrown when the cursor is out of data, so wait
                        # for a period for some more data
                        time.sleep(10)
            finally:
                cursor.close()
