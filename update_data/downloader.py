#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __init__ import config as setting
import requests
from log import logger
from concurrent import futures

MAX_WORKERS = 20


class Downloader(object):
    def __init__(self, header=setting.FAKE_HEADER,
                 url=setting.BASE_URI):
        self.header = header
        self.proxy = ''
        self.session = requests.Session()
        self.resps = []
        self.base_uri = url

    def download_tool(self, data):
        if not data:
            return
        try:
            logger.info('download data: {0}'.format(data))
            # resp = self.session.get(url, headers=self.header)
            resp = self.session.post(self.base_uri, headers=self.header, data=data)
        except requests.exceptions.ConnectionError as e:
            logger.error('Unable to download the webpage: {0}'.format(data))
            return
        except Exception as e:
            logger.error('other error: {0}'.format(str(e)))
            return
        if resp.status_code == 200:
            self.resps.append(resp)
        else:
            logger.error('the status_code:{0}'.format(resp.status_code))
            return

    def download(self, datas, **kwargs):
        self.resps = []
        header = kwargs.get('header', {})
        self.header.update(header)
        workers = min(MAX_WORKERS, len(datas))
        with futures.ThreadPoolExecutor(workers) as executor:
            executor.map(self.download_tool, datas)
        return self.resps
