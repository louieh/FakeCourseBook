#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __init__ import config as setting
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
                 col_name_speed=setting.COLLECTION_NAME_FOR_SPEED,
                 db_name=setting.DB_NAME,
                 redis_key_for_search=setting.REDIS_KEY_FOR_SEARCH,
                 redis_key_for_graph=setting.REDIS_KEY_FOR_GRAPH,
                 redis_key_for_speed=setting.REDIS_KEY_FOR_SPEED,
                 redis_key_for_search_next=setting.REDIS_KEY_FOR_SEARCH_NEXT,
                 UPDATE_INTERVAL=setting.UPDATE_INTERVAL,
                 ):
        self.mongo_host = mongo_host
        self.redis_host = redis_host
        self.mongo_port = mongo_port
        self.redis_port = redis_port
        self.col_name_search = col_name_search
        self.col_name_graph = col_name_graph
        self.col_name_speed = col_name_speed
        self.db_name = db_name
        self.redis_key_for_search = redis_key_for_search
        self.redis_key_for_search_next = redis_key_for_search_next
        self.redis_key_for_graph = redis_key_for_graph
        self.redis_key_for_speed = redis_key_for_speed
        self.UPDATE_INTERVAL = UPDATE_INTERVAL

    def init_redis(self):
        pool = redis.ConnectionPool(host=self.redis_host, port=self.redis_port, decode_responses=True)
        self.redis_client = redis.Redis(connection_pool=pool)
        try:
            self.redis_client.keys()
            return True
        except:
            logger.error('init redis error.')
            return False

    def init_mongo(self):
        self.mongo_client = MongoClient(self.mongo_host, self.mongo_port)
        self.db = self.mongo_client.get_database(self.db_name)
        try:
            self.db.list_collection_names()
            return True
        except:
            logger.error('init mongo error.')
            return False

    def insert_mongo_for_SG(self, data, **kwargs):
        """
        :param data: dict
        :param kwargs:
        :return:
        """
        if not data:
            logger.info('insert_mongo: no data')
            return
        if not self.mongo_client:
            self.init_mongo()

        # there are three collection:
        # temp, CourseFor***, CourseFor***_dump
        # 1. generate temp
        # 2. delete CourseFor***_dump
        # 3. rename CourseFor*** to CourseFor***_dump
        # 4. rename temp to CourseFor***

        if self.col_name_search in data:
            logger.info('inserting for {0}'.format(self.col_name_search))
            try:
                self.db.temp.insert_many(data.get(self.col_name_search))
            except Exception as e:
                logger.error('insert temp collection failed: {0}'.format(str(e)))
                self.db.temp.drop()
                logger.info('drop temp collection')
                return

            # drop the old dump collection
            if self.col_name_search + '_dump' in self.db.list_collection_names():
                try:
                    self.db.get_collection(self.col_name_search + '_dump').drop()
                    logger.info('the collection dump has dropped')
                except Exception as e:
                    logger.error('the collection dump drop failed: {0}'.format(str(e)))
                    self.db.temp.drop()
                    return
            else:
                logger.info('there is no {0}'.format(self.col_name_search + '_dump'))

            # rename collection to collection_dump
            if self.col_name_search in self.db.list_collection_names():
                try:
                    self.db.get_collection(self.col_name_search).rename(self.col_name_search + "_dump")
                    logger.info('collection has rename to {0}'.format(self.col_name_search + "_dump"))
                except Exception as e:
                    logger.error('collection rename to {0} failed: {1}'.format(self.col_name_search + "_dump", str(e)))
                    self.db.get_collection(self.col_name_search).drop()
                    logger.info('collection has been dropped')
            else:
                logger.info('there is no {0}'.format(self.col_name_search))

            # rename temp to collection
            try:
                self.db.temp.rename(self.col_name_search)
                logger.info('db.temp has rename to {0}'.format(self.col_name_search))
            except Exception as e:
                logger.error('db.temp rename to {0} error: {1}'.format(self.col_name_search, str(e)))
                self.db.temp.drop()
                return
            self.insert_redis(self.redis_key_for_search)

        if self.col_name_graph in data:
            logger.info('inserting for {0}'.format(self.col_name_graph))
            try:
                self.db.temp.insert_many(data.get(self.col_name_graph))
            except Exception as e:
                logger.error('insert temp collection failed: {0}'.format(str(e)))
                self.db.temp.drop()
                logger.info('drop temp collection')
                return

            # drop the old dump collection
            if self.col_name_graph + '_dump' in self.db.list_collection_names():
                try:
                    self.db.get_collection(self.col_name_graph + '_dump').drop()
                    logger.info('the collection dump has dropped')
                except Exception as e:
                    logger.error('the collection dump drop failed: {0}'.format(str(e)))
                    self.db.temp.drop()
                    return
            else:
                logger.info('there is not {0}'.format(self.col_name_graph + '_dump'))

            # rename collection to collection_dump
            if self.col_name_graph in self.db.list_collection_names():
                try:
                    self.db.get_collection(self.col_name_graph).rename(self.col_name_graph + "_dump")
                    logger.info('collection has rename to {0}'.format(self.col_name_graph + "_dump"))
                except Exception as e:
                    logger.error('collection rename to {0} failed: {1}'.format(self.col_name_graph + "_dump", str(e)))
                    self.db.get_collection(self.col_name_graph).drop()
                    logger.info('collection has been dropped')
            else:
                logger.info('there is no {0}'.format(self.col_name_graph))

            # rename temp to collection
            try:
                self.db.temp.rename(self.col_name_graph)
                logger.info('db.temp has rename to {0}'.format(self.col_name_graph))
            except Exception as e:
                logger.error('db.temp rename to {0} error: {1}'.format(self.col_name_graph, str(e)))
                self.db.temp.drop()
                return
            self.insert_redis(self.redis_key_for_graph)

        if self.col_name_speed in data:
            logger.info('inserting for {0}'.format(self.col_name_speed))
            try:
                for each_for_speed in data.get(self.col_name_speed):
                    if len(list(self.db.CourseForSpeed.find({'class_term': each_for_speed.get('class_term'),
                                                             'class_number': each_for_speed.get('class_number')}))):
                        self.db.CourseForSpeed.update({'class_term': each_for_speed.get('class_term'),
                                                       'class_number': each_for_speed.get('class_number')}, {
                                                          "$push": {'update_data': {
                                                              'percentage': each_for_speed.get('class_isFull'),
                                                              'timestamp': each_for_speed.get('timestamp')}}})
                    else:
                        each_for_speed.update({'update_data': [{'percentage': each_for_speed.get('class_isFull'),
                                                                'timestamp': each_for_speed.get('timestamp')}]})
                        each_for_speed.pop('class_isFull')
                        each_for_speed.pop('timestamp')
                        self.db.CourseForSpeed.insert_one(each_for_speed)
                logger.info('update UPDATE_FOR_SPEED ok')
                self.insert_redis(self.redis_key_for_speed)
            except Exception as e:
                logger.error('update UPDATE_FOR_SPEED error: {0}'.format(str(e)))

    def insert_redis(self, key_name=None, **kwargs):
        if not self.redis_client:
            self.init_redis()
        if not key_name:
            logger.info('no key_name')
            return
        if key_name == self.redis_key_for_search:
            try:
                self.redis_client.set(self.redis_key_for_search, setting.TIMENOW_UTC())
                if setting.UPDATE_NEXT_TIME_KEY:
                    self.update_next_time_search()
                else:
                    logger.info('did not update update next time key')
                logger.info('set redis key OK for {0}'.format(self.redis_key_for_search))
            except Exception as e:
                logger.error('insert redis {0} failed: {1}'.format(self.redis_key_for_search, str(e)))
        if key_name == self.redis_key_for_graph:
            try:
                self.redis_client.set(self.redis_key_for_graph, setting.TIMENOW_UTC())
                logger.info('set redis key OK for {0}'.format(self.redis_key_for_graph))
            except Exception as e:
                logger.error('insert redis {0} failed: {0}'.format(self.redis_key_for_graph, str(e)))
        if key_name == self.redis_key_for_speed:
            try:
                self.redis_client.set(self.redis_key_for_speed, setting.TIMENOW_UTC())
                logger.info('set redis key OK for {0}'.format(self.redis_key_for_speed))
            except Exception as e:
                logger.error('insert redis {0} failed: {0}'.format(self.redis_key_for_speed, str(e)))

    def update_next_time_search(self):
        if not self.redis_client:
            self.init_redis()
        self.redis_client.set(self.redis_key_for_search_next, setting.TIMENOW_UTC_NEXT(),
                              ex=(self.UPDATE_INTERVAL + 5) * 60)  # minute
