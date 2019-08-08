#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from logging.handlers import TimedRotatingFileHandler

THIS_DIR = os.path.split(os.path.realpath(__file__))[0]


def get_logger():
    fmt = "%(asctime)s-%(name)s pid=%(process)d %(filename)s " + \
          "%(funcName)s %(lineno)s %(levelname)s %(message)s"

    logging.basicConfig(format=fmt)
    logger = logging.getLogger('update_data')
    logger.setLevel(logging.INFO)

    log_path = os.path.join(THIS_DIR, 'logs')
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    handler = TimedRotatingFileHandler(os.path.join(log_path, 'update_data.log'),
                                       when='D', interval=1, backupCount=30)
    handler.setFormatter(logging.Formatter(fmt))
    handler.suffix = "%Y-%m-%d_%H-%M-%S.log"
    logger.addHandler(handler)
    return logger


logger = get_logger()
