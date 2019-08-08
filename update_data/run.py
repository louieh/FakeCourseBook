#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import spider
from log import logger

spider = spider.Spider(update_method=1)
spider.update_data()
