#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setting
import redis
from pymongo import MongoClient


class DB(object):
    def __init__(self, mongo_host=setting.MONGO_HOST, mongo_port=setting.MONGO_HOST, redis_host=setting.REDIS_HOST,
                 redis_port=setting.REDIS_PORT):
        self.mongo_host = mongo_host
        self.redis_host = redis_host
        self.mongo_port = mongo_port
        self.redis_port = redis_port

    def get_redis(self):
        self.redis_client = redis.StrictRedis(host=self.redis_host, port=self.redis_port, decode_responses=True)
        return self.redis_client

    def get_mongo(self):
        self.mongo_client = MongoClient(self.mongo_host, self.mongo_port)
        return self.mongo_client
