#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger()

log_path = './log/'

fp = logging.handlers.RotatingFileHandler(log_path + "datainsert.log", mode='a', maxBytes=1 * 1024 * 1024,
                                          backupCount=10)
logger.addHandler(fp)

std = logging.StreamHandler(sys.stderr)
logger.addHandler(std)

formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(filename)s] [%(lineno)d]- %(message)s")
fp.setFormatter(formatter)
std.setFormatter(formatter)

logger.setLevel(logging.NOTSET)
