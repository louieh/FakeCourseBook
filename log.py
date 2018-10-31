#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging

logger = logging.getLogger()

log_path = './log/'

fp = logging.FileHandler(log_path + "datainsert.log", mode='a')
logger.addHandler(fp)

std = logging.StreamHandler(sys.stderr)
logger.addHandler(std)

formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(filename)s] [%(lineno)d]- %(message)s")
fp.setFormatter(formatter)
std.setFormatter(formatter)

logger.setLevel(logging.NOTSET)
