#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setting
import redis
from pymongo import MongoClient
from log import logger


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

    def insert_mongo_for_SG(self, data, just_update=False, **kwargs):
        if not data:
            logger.info('insert_mongo: no data')
            return
        if not self.mongo_client:
            self.init_mongo()

        collection_dump, collection, collection_name = (
            self.db.CourseForSearch_dump, self.db.CourseForSearch,
            self.col_name_search) if self.update_for_search else (self.db.CourseForGraph_dump,
                                                                  self.db.CourseForGraph, self.col_name_graph)

        # there are three collection:
        # temp, CourseForSearch, CourseForSearch_dump
        # 1. generate temp
        # 2. delete CourseForSearch_dump
        # 3. rename CourseForSearch to CourseForSearch_dump
        # 4. rename temp to CourseForSearch

        # generate collection temp
        try:
            self.db.temp.insert_many(data)
        except Exception as e:
            logger.error('insert temp collection failed: {0}'.format(str(e)))
            self.db.temp.drop()
            logger.info('drop temp collection')
            return

        # drop the old collection
        try:
            collection_dump.drop()
            logger.info('the collection dump has dropped')
        except Exception as e:
            logger.error('the collection dump drop failed: {0}'.format(str(e)))
            self.db.temp.drop()
            return

        # rename collection to collection_dump
        try:
            collection.rename(collection_name + "dump")
            logger.info('collection has rename to {0}'.format(collection_name + "dump"))
        except Exception as e:
            logger.error('collection rename to {0} failed'.format(collection_name + "dump"))
            collection.drop()
            logger.info('collection has been dropped')

        # rename temp to collection
        try:
            self.db.temp.rename(collection_name)
            logger.info('db.temp has rename to {0}'.format(collection_name))
        except Exception as e:
            logger.error('db.temp rename to {0} error'.format(collection_name))
            self.db.temp.drop()
            return

        self.insert_redis(setting.TIMENOW_UTC())

    def insert_redis(self, data, key_prefix=None, **kwargs):
        if not key_prefix:
            key_prefix = setting.REDIS_UPDATE_TIME_KEY

        if not self.redis_client:
            self.init_redis()
        try:
            self.redis_client.set(key_prefix, data)
            logger.info('set redis key OK.')
        except Exception as e:
            logger.error('insert redis failed: {0}'.format(str(e)))
