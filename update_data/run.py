#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import spider
from log import logger
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


def main():
    spider = spider.Spider(update_method=1)
    spider.update_data()


executors = {
    'default': ThreadPoolExecutor(1),
    'processpool': ProcessPoolExecutor(1)
}
timer = BlockingScheduler(executors=executors)

if __name__ == "__main__":
    timer.add_job(main, 'interval', hours=6)
    timer.start()
