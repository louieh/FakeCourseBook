#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import spider, db
from __init__ import config as setting
from log import logger
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


def skip():
    logger.info('pass')


executors = {
    'default': ThreadPoolExecutor(1),
    'processpool': ProcessPoolExecutor(1)
}
scheduler = BlockingScheduler()

Spider = spider.Spider(update_method=1)
if len(sys.argv) > 1:
    logger.info("You may not want to add -m or -s")
    if '-m' in sys.argv[1:] or '-M' in sys.argv[1:]:
        logger.info("Main scheduler started...")
        scheduler.add_job(Spider.update_data, 'interval', minutes=setting.UPDATE_INTERVAL)
        Spider.init_next_update_search()
        scheduler.start()
    elif '-s' in sys.argv[1:] or '-S' in sys.argv[1:]:
        logger.info("Skip scheduler started...")
        scheduler.add_job(skip, 'interval', minutes=setting.UPDATE_INTERVAL)
        scheduler.start()
else:
    setting.UPDATE_NEXT_TIME_KEY = False
    Spider.update_data()
    setting.UPDATE_NEXT_TIME_KEY = True
