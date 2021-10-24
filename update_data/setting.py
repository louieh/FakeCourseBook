#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import datetime


class Config(object):
    # base uri
    # BASE_URI = 'https://coursebook.utdallas.edu/{0}/term_{1}'
    # BASE_URI = 'https://coursebook.utdallas.edu/term_{1}/cp_{0}'
    # BASE_URI = 'https://coursebook.utdallas.edu/clips/clip-coursebook.zog'
    BASE_URI = 'https://coursebook.utdallas.edu/clips/clip-cb11-hat.zog'
    BASE_URL_FOR_PREFIX = 'https://coursebook.utdallas.edu/guidedsearch'

    POST_DATA = 'action=search&s%5B%5D=term_{1}&s%5B%5D=cp_{0}'

    # term and prefix
    ALL_TERM_LIST = ['22s', '21f', '21u', '21s', '20F', '20U', '20S', '19F', '19U', '19S', '18F', '18U', '18S', '17F',
                     '17U', '17S', '16F', '16U', '16S', '15F', '15U', '15S', '14F', '14U', '14S', '13F', '13U', '13S',
                     '12F', '12U', '12S', '11F', '11U', '11S', '10F', '10U', '10S']
    CURRENT_TERM_LIST = ['22s', '21f']
    ALL_PREFIX_LIST = ['cs']
    CURRENT_PREFIX_LIST = ['cs']

    # data structure
    For_Speed_struc = ['class_title', 'class_term', 'class_number', 'class_section', 'class_instructor',
                       'class_isFull', 'class_day', 'class_start_time']  # timestamp
    For_Graph_struc = ['class_title', 'class_section', 'class_term', 'class_instructor', 'class_number']

    # header
    FAKE_HEADER = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "PTGSESSID=f53e47ecbd7a0cf4cf7d0daafcbde5e2",
        "DNT": "1",
        "Connection": "keep-alive",
        "Host": "coursebook.utdallas.edu",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    }
    ENCODING = 'utf-8'

    # get time
    TIMEDELTA = 5
    TIMENOW = lambda: (datetime.datetime.utcnow() - datetime.timedelta(hours=Config.TIMEDELTA)).strftime(
        "%Y-%m-%d %H:%M")
    TIMENOW_UTC = lambda: datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    TIMENOW_UTC_NEXT = lambda: (
            datetime.datetime.utcnow() + datetime.timedelta(minutes=Config.UPDATE_INTERVAL)).strftime(
        "%Y-%m-%d %H:%M")

    # switch of updating next time key
    UPDATE_NEXT_TIME_KEY = True

    # update_interval
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 360))


class ProductionConfig(Config):
    # db
    MONGO_HOST = os.getenv('MONGO_HOST', 'mongo')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    COLLECTION_NAME_FOR_SEARCH = 'CourseForSearch'
    COLLECTION_NAME_FOR_GRAPH = 'CourseForGraph'
    COLLECTION_NAME_FOR_SPEED = 'CourseForSpeed'
    DB_NAME = 'Coursebook'
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
    REDIS_KEY_FOR_SEARCH = 'search_data_update_time'
    REDIS_KEY_FOR_SEARCH_NEXT = 'search_data_next_update_time'
    REDIS_KEY_FOR_GRAPH = 'graph_data_update_time'
    REDIS_KEY_FOR_SPEED = 'speed_data_update_time'
    # switch of update object
    UPDATE_FOR_SEARCH = True if os.getenv('UPDATE_FOR_SEARCH', True) in [True, 'True'] else False
    UPDATE_FOR_GRAPH = True if os.getenv('UPDATE_FOR_GRAPH', False) in [True, 'True'] else False
    UPDATE_FOR_SPEED = True if os.getenv('UPDATE_FOR_SPEED', False) in [True, 'True'] else False
    GRADUATE_LEVEL = True if os.getenv('GRADUATE_LEVEL', True) in [True, 'True'] else False
    SKIP = True if os.getenv('SKIP', True) in [True, 'True'] else False


class DevelopmentConfig(Config):
    # db
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    COLLECTION_NAME_FOR_SEARCH = 'CourseForSearch'
    COLLECTION_NAME_FOR_GRAPH = 'CourseForGraph'
    COLLECTION_NAME_FOR_SPEED = 'CourseForSpeed'
    DB_NAME = 'Coursebook'
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    REDIS_KEY_FOR_SEARCH = 'search_data_update_time'
    REDIS_KEY_FOR_SEARCH_NEXT = 'search_data_next_update_time'
    REDIS_KEY_FOR_GRAPH = 'graph_data_update_time'
    REDIS_KEY_FOR_SPEED = 'speed_data_update_time'
    # switch of update object
    UPDATE_FOR_SEARCH = True
    UPDATE_FOR_GRAPH = False
    UPDATE_FOR_SPEED = False
    GRADUATE_LEVEL = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
