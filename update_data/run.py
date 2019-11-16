#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import spider
from __init__ import config as setting
from log import logger
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


def main():
    Spider = spider.Spider(update_method=1)
    Spider.update_data()


def skip():
    print("pass")


executors = {
    'default': ThreadPoolExecutor(1),
    'processpool': ProcessPoolExecutor(1)
}
scheduler = BlockingScheduler(executors=executors)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        print("You may want to add -m or -s.")
        if '-m' in sys.argv[1:] or '-M' in sys.argv[1:]:
            print("Main scheduler started...")
            scheduler.add_job(main, 'interval', minutes=setting.UPDATE_INTERVAL)
            scheduler.start()
        elif '-s' in sys.argv[1:] or '-S' in sys.argv[1:]:
            print("Skip scheduler started...")
            scheduler.add_job(skip, 'interval', minutes=setting.UPDATE_INTERVAL)
            scheduler.start()
    else:
        setting.UPDATE_NEXT_TIME_KEY = False
        main()
        setting.UPDATE_NEXT_TIME_KEY = True
