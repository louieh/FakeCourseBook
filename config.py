#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')


class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_HOST = os.getenv('MONGO_HOST', 'mongo')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    COLLECTION_NAME_FOR_SEARCH = 'CourseForSearch'
    COLLECTION_NAME_FOR_GRAPH = 'CourseForGraph'
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
    REDIS_UPDATE_TIME_KEY = 'data_update_time'

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    pass


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
