#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import datetime

# db
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_UPDATE_TIME_KEY = 'DATA_UPDATE_TIME'

# base uri
BASE_URI = 'https://coursebook.utdallas.edu/{0}/term_{1}'
BASE_URL_FOR_PREFIX = 'https://coursebook.utdallas.edu/guidedsearch'

# term and prefix
ALL_TERM_LIST = ['19F', '19S', '18F', '18U', '18S', '17F', '17U', '17S', '16F', '16U', '16S', '15F', '15U', '15S',
                 '14F', '14U', '14S', '13F', '13U', '13S', '12F', '12U', '12S', '11F', '11U', '11S', '10F',
                 '10U', '10S']
CURRENT_TERM_LIST = ['19F', '19S']
ALL_PREFIX_LIST = ['CS', 'CE', 'EE', 'SE']
CURRENT_PREFIX_LIST = ['CS', 'CE', 'EE', 'SE']

#
JUST_UPDATE = False
INSERT_DIRECTLY = False
UPDATE_FRO_SEARCH = True
GRADUATE_LEVEL = True

# header
FAKE_HEADER = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
    "DNT": "1",
    "Host": "coursebook.utdallas.edu",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
}
ENCODING = 'utf-8'

# get time
TIMEDELTA = 5
TIMENOW = lambda: (datetime.datetime.utcnow() - datetime.timedelta(hours=TIMEDELTA)).strftime("%Y-%m-%d %H:%M")
TIMENOW_UTC = lambda: datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
