#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import spider
import setting
from log import logger
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


def main():
    Spider = spider.Spider(update_method=1)
    Spider.update_data()


executors = {
    'default': ThreadPoolExecutor(1),
    'processpool': ProcessPoolExecutor(1)
}
scheduler = BlockingScheduler(executors=executors)

if __name__ == "__main__":
    if len(sys.argv) >= 2 and ('-i' in sys.argv[1:] or '-I' in sys.argv[1:]):
        main()
    else:
        print("You may want to add -i or -I")
        print("Scheduler started...")
        scheduler.add_job(main, 'interval', minutes=setting.UPDATE_INTERVAL)
        scheduler.start()
