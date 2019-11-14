#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    TERM_LIST = ['20S', '19F', '19S', '18F', '18U', '18S', '17F', '17U', '17S', '16F', '16U', '16S', '15F', '15U',
                 '15S',
                 '14F', '14U', '14S', '13F', '13U', '13S', '12F', '12U', '12S', '11F', '11U', '11S', '10F',
                 '10U', '10S']
    # TIMEDELTA = 5  # summer time
    TIMEDELTA = 6  # winter time


class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    COLLECTION_NAME_FOR_SEARCH = 'CourseForSearch'
    COLLECTION_NAME_FOR_GRAPH = 'CourseForGraph'
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    REDIS_UPDATE_TIME_KEY = 'data_update_time'
    REDIS_UPDATE_NEXT_TIME_KEY = 'data_update_next_time'

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    pass


class ProductionConfig(Config):
    DEBUG = False
    MONGO_HOST = os.getenv('MONGO_HOST', 'mongo')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    COLLECTION_NAME_FOR_SEARCH = 'CourseForSearch'
    COLLECTION_NAME_FOR_GRAPH = 'CourseForGraph'
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
    REDIS_UPDATE_TIME_KEY = 'data_update_time'
    REDIS_UPDATE_NEXT_TIME_KEY = 'data_update_next_time'

    @staticmethod
    def init_app(app):
        pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
