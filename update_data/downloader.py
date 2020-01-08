#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __init__ import config as setting
import requests
from log import logger
from concurrent import futures

MAX_WORKERS = 20


class Downloader(object):
    def __init__(self, header=setting.FAKE_HEADER):
        self.header = header
        self.proxy = ''
        self.session = requests.Session()

    def download_tool(self, url):
        if not url:
            return
        try:
            logger.info('download url: {0}'.format(url))
            resp = self.session.get(url, headers=self.header)
        except requests.exceptions.ConnectionError as e:
            logger.error('Unable to download the webpage: {0}'.format(url))
            return
        except Exception as e:
            logger.error('other error: {0}'.format(str(e)))
            return
        if resp.status_code == 200:
            return resp
        else:
            logger.error('the status_code:{0}'.format(resp.status_code))
            return

    def download(self, urls, **kwargs):
        res = []
        header = kwargs.get('header', {})
        self.header.update(header)
        # workers = min(MAX_WORKERS, len(urls))
        # with futures.ThreadPoolExecutor(workers) as executor:
        #     executor.map(self.download_tool, urls)
        for url in urls:
            res.append(self.download_tool(url))
        return res
