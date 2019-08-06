#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setting
import redis
from pymongo import MongoClient


class DB(object):
    def __init__(self, mongo_host=setting.MONGO_HOST,
                 mongo_port=setting.MONGO_PORT,
                 redis_host=setting.REDIS_HOST,
                 redis_port=setting.REDIS_PORT,
                 col_name_search=setting.COLLECTION_NAME_FOR_SEARCH,
                 col_name_graph=setting.COLLECTION_NAME_FOR_GRAPH,
                 update_for_search=setting.UPDATE_FRO_SEARCH
                 ):
        self.mongo_host = mongo_host
        self.redis_host = redis_host
        self.mongo_port = mongo_port
        self.redis_port = redis_port
        self.col_name_search = col_name_search
        self.col_name_graph = col_name_graph
        self.update_for_search = update_for_search

    def init_redis(self):
        self.redis_client = redis.StrictRedis(host=self.redis_host, port=self.redis_port, decode_responses=True)
        try:
            self.redis_client.keys()
            return True
        except:
            print('init redis error.')
            return False

    def init_mongo(self):
        self.mongo_client = MongoClient(self.mongo_host, self.mongo_port)
        self.db = self.mongo_client.Coursebook
        try:
            self.db.list_collection_names()
            return True
        except:
            print('init mongo error.')
            return False

    def insert_mongo(self, data, just_update=False, **kwargs):
        if not data:
            print('insert_mongo: no data')
            return
        if not self.mongo_client:
            self.init_mongo()
        collection, collection_name = (self.db.CourseForSearch, self.col_name_search) if self.update_for_search else (
            self.db.CourseForGraph, self.col_name_graph)
        try:
            self.db.temp.insert_many(data)
        except Exception as e:
            print('insert temp collection failed: {0}'.format(str(e)))
            self.db.temp.drop()
            print('drop temp collection')
            return

        try:
            collection.drop()
            print('the old collection has dropped')
        except Exception as e:
            print('the old collection drop failed: {0}'.format(str(e)))
            self.db.temp.drop()
            return

        try:
            self.db.temp.rename(collection_name)
            print('db.temp has rename to {0}'.format(collection_name))
        except Exception as e:
            print('db.temp rename to {0} error'.format(collection_name))
            return

        self.insert_redis(setting.TIMENOW_UTC())

    def insert_redis(self, data, key_prefix=None, **kwargs):
        if not key_prefix:
            key_prefix = setting.REDIS_UPDATE_TIME_KEY

        if not self.redis_client:
            self.init_redis()
        try:
            self.redis_client.set(key_prefix, data)
        except Exception as e:
            print('insert redis failed: {0}'.format(str(e)))
